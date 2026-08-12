"""
thu_nghiem_bien_dau_vao.py
So sanh cac bo bien dau vao cho mo hinh du bao cong suat nha may dien mat troi.

Muc dich: tra loi cau hoi "them do am, gio, nhiet do khong khi vao co giup gi khong",
bang so lieu chay tren chinh du lieu cua nha may.

Cach chay:
    pip install pandas numpy scikit-learn matplotlib
    python thu_nghiem_bien_dau_vao.py --csv ../data/csv --out ../data/thu_nghiem

Neu chua co thu muc CSV thi chay buoc trich xuat truoc:
    python export_to_csv.py ../db_fujiwara.sql -o ../data/csv --tz 7

Script tu in ket qua ra man hinh va ghi ra file CSV trong thu muc --out.
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------- cau hinh
LAT, LON = 13.8634, 109.2708      # toa do nha may, Bang 5.3
TZ_MERIDIAN = 105.0              # kinh tuyen chuan cua mui GMT+7
CAP_AC = 40.0                    # MW xoay chieu, dung de chuan hoa NMAE
CAP_DC = 50.0                    # MWp mot chieu
HE_SO_NHIET = -0.0035            # /degC, gia tri dien hinh cua tam pin tinh the

COT_BUC_XA = "SOLAR_WS_Rad_1"
COT_CONG_SUAT = "Substation_Level_110kV_Bay131_MEAS_P"

# cac dot cam bien Rad_2 treo gia tri, muc 6.4 cua bao cao khao sat
DOT_RAD2_TREO = [
    ("2025-08-05 17:00", "2025-08-05 23:30"),
    ("2025-11-06 14:00", "2025-11-08 12:00"),
    ("2025-12-26 17:00", "2025-12-26 23:00"),
    ("2025-12-29 10:00", "2026-01-06 11:00"),
    ("2026-02-04 13:00", "2026-02-07 12:00"),
    ("2026-02-15 17:00", "2026-02-15 19:00"),
    ("2026-02-22 11:00", "2026-02-24 13:00"),
    ("2026-03-07 16:00", "2026-03-07 23:30"),
]


# ---------------------------------------------------------------- nap du lieu
def nap_du_lieu(csv_dir: Path, buoc: str = "15min") -> pd.DataFrame:
    """Doc Weather + His_131, gop len luoi thoi gian dong nhat."""
    w_path, p_path = csv_dir / "Weather.csv", csv_dir / "His_131.csv"
    for p in (w_path, p_path):
        if not p.exists():
            sys.exit(
                f"Khong tim thay {p}\n"
                "Chay buoc trich xuat truoc:\n"
                "    python export_to_csv.py ../db_fujiwara.sql -o ../data/csv --tz 7"
            )

    cot_w = ["ts_local", COT_BUC_XA, "SOLAR_WS_Panel_T", "SOLAR_WS_Air_T",
             "SOLAR_WS_Humidity", "SOLAR_WS_Wind_Speed"]
    w = pd.read_csv(w_path, usecols=cot_w, parse_dates=["ts_local"])
    p = pd.read_csv(p_path, usecols=["ts_local", COT_CONG_SUAT], parse_dates=["ts_local"])

    w = w.set_index("ts_local").sort_index().resample(buoc).mean()
    p = p.set_index("ts_local").sort_index().resample(buoc).mean()

    d = w.join(p, how="inner").rename(columns={
        COT_BUC_XA: "G", "SOLAR_WS_Panel_T": "Tp", "SOLAR_WS_Air_T": "Ta",
        "SOLAR_WS_Humidity": "RH", "SOLAR_WS_Wind_Speed": "WS",
        COT_CONG_SUAT: "P",
    })
    return d


def lam_sach(d: pd.DataFrame) -> pd.DataFrame:
    """Ap cac quy tac da chot trong bao cao khao sat."""
    d = d.copy()
    ban_ngay = d["G"] > 20

    # muc 7.6 — gia tri 0 ban ngay la mat tin hieu, khong phai so do
    for c in ("Ta", "RH", "Tp"):
        d.loc[ban_ngay & d[c].eq(0), c] = np.nan

    # muc 7.3 va 7.4 — nguong vat ly
    d.loc[d["Tp"] > 80, "Tp"] = np.nan          # tran so 16 bit -> 6553,5 degC
    d.loc[d["G"] > 1350, "G"] = np.nan          # phan duoi bat thuong cua buc xa
    d.loc[d["RH"] > 100, "RH"] = np.nan
    d.loc[d["WS"] > 60, "WS"] = np.nan

    # muc 6.4 — cac dot cam bien treo gia tri
    for a, b in DOT_RAD2_TREO:
        d.loc[a:b, ["G", "Tp", "Ta", "RH", "WS"]] = np.nan

    return d


def them_hinh_hoc_mat_troi(d: pd.DataFrame) -> pd.DataFrame:
    """Goc cao va goc gio mat troi, tinh tu toa do — khong lay tu du lieu."""
    d = d.copy()
    doy = d.index.dayofyear.values
    b = 2 * np.pi * (doy - 1) / 365
    # phuong trinh thoi gian, cong thuc Spencer, don vi phut
    eot = 229.18 * (0.000075 + 0.001868 * np.cos(b) - 0.032077 * np.sin(b)
                    - 0.014615 * np.cos(2 * b) - 0.040849 * np.sin(2 * b))
    dec = np.radians(23.45) * np.sin(2 * np.pi * (284 + doy) / 365)
    phut = d.index.hour.values * 60 + d.index.minute.values
    gio_mat_troi = phut + (LON - TZ_MERIDIAN) * 4 + eot
    ha = np.radians((gio_mat_troi - 720) / 4)          # goc gio

    lat = np.radians(LAT)
    sin_elev = np.sin(lat) * np.sin(dec) + np.cos(lat) * np.cos(dec) * np.cos(ha)
    d["elev"] = np.degrees(np.arcsin(np.clip(sin_elev, -1, 1)))
    d["ha_deg"] = np.degrees(ha)                        # am = sang, duong = chieu
    # buc xa ngoai khi quyen tren mat ngang — chuan hoa hinh hoc
    d["G_toi_da"] = (1361 * np.clip(sin_elev, 0, None))
    return d


# ---------------------------------------------------------------- kiem tra du lieu
def bao_cao_do_san_co(d: pd.DataFrame) -> pd.DataFrame:
    """Ty le mau dung duoc cua tung cam bien theo thang, chi xet ban ngay.

    Buoc nay quan trong: neu mot cam bien chet o giai doan cuoi chuoi thi moi
    ket qua so sanh deu sai lech, vi tap kiem dinh se bi rong.
    """
    ngay = d[d["G"] > 50]
    g = ngay.groupby(ngay.index.to_period("M"))
    out = pd.DataFrame({
        "so_o_ban_ngay": g.size(),
        "G": g["G"].apply(lambda s: s.notna().mean() * 100),
        "Tp": g["Tp"].apply(lambda s: s.notna().mean() * 100),
        "Ta": g["Ta"].apply(lambda s: s.notna().mean() * 100),
        "RH": g["RH"].apply(lambda s: s.notna().mean() * 100),
        "WS": g["WS"].apply(lambda s: s.notna().mean() * 100),
    }).round(1)
    return out


def chon_thang_kiem_dinh(san_co: pd.DataFrame, nguong: float = 90.0,
                         so_fold: int = 5) -> list:
    """Chi lay lam fold kiem dinh nhung thang ma MOI cam bien deu con song.

    Neu bo qua buoc nay, tap kiem dinh cua cac bo bien co Ta/RH se rong sau khi
    loai NaN, va ket qua se la so sanh giua cac tap mau khac nhau — vo nghia.
    """
    cot = ["G", "Tp", "Ta", "RH", "WS"]
    du_dieu_kien = san_co[(san_co[cot] >= nguong).all(axis=1)
                          & (san_co["so_o_ban_ngay"] > 300)]
    return list(du_dieu_kien.index[-so_fold:])


# ---------------------------------------------------------------- mo hinh
def tao_mo_hinh(loai: str):
    """Tra ve doi tuong co .fit/.predict. Uu tien sklearn neu co."""
    try:
        from sklearn.ensemble import HistGradientBoostingRegressor
        from sklearn.neighbors import KNeighborsRegressor
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        from sklearn.linear_model import LinearRegression
    except ImportError:
        return None

    if loai == "gbm":
        # cay tang cuong: tu bo qua bien yeu, khong bi phat khi them chieu
        return HistGradientBoostingRegressor(
            max_iter=400, learning_rate=0.06, max_depth=6,
            min_samples_leaf=40, l2_regularization=1.0, random_state=0)
    if loai == "knn":
        return make_pipeline(StandardScaler(), KNeighborsRegressor(n_neighbors=40))
    if loai == "tuyen_tinh":
        return make_pipeline(StandardScaler(), LinearRegression())
    raise ValueError(loai)


def danh_gia(d, cols, folds, loai="gbm", cot_dich="P"):
    """Danh gia goc truot. Moi fold: huan luyen tren toan bo qua khu, kiem dinh 1 thang."""
    ket_qua = []
    for f in folds:
        thang = d.index.to_period("M")
        tr, te = d[thang < f], d[thang == f]
        if len(tr) < 3000 or len(te) < 300:
            continue
        m = tao_mo_hinh(loai)
        m.fit(tr[cols].values, tr[cot_dich].values)
        du_bao = m.predict(te[cols].values)
        e = du_bao - te[cot_dich].values
        ban_ngay = (te["G"] > 50).values
        ket_qua.append({
            "fold": str(f),
            "n": len(te),
            "MAE": np.abs(e).mean(),
            "MAE_ban_ngay": np.abs(e[ban_ngay]).mean() if ban_ngay.any() else np.nan,
            "RMSE": float(np.sqrt((e ** 2).mean())),
            "Bias": e.mean(),
            "n_ban_ngay": int(ban_ngay.sum()),
        })
    if not ket_qua:
        return None
    r = pd.DataFrame(ket_qua)
    return {
        "MAE": r["MAE"].mean(),
        "MAE_ban_ngay": r["MAE_ban_ngay"].mean(),
        "RMSE": r["RMSE"].mean(),
        "Bias": r["Bias"].mean(),
        "NMAE_%": r["MAE"].mean() / CAP_AC * 100,
        "so_fold": len(r),
        "n_ban_ngay": int(r["n_ban_ngay"].sum()),
    }


# ---------------------------------------------------------------- cac phep thu
BO_BIEN = [
    (["G"],                                   "Chi buc xa"),
    (["G", "Tp"],                             "+ nhiet do tam pin"),
    (["G", "elev"],                           "+ goc cao mat troi (khong co Tp)"),
    (["G", "Tp", "elev", "ha_deg"],           "+ tam pin + hinh hoc mat troi"),
    (["G", "Tp", "elev", "ha_deg", "WS"],     "++ toc do gio"),
    (["G", "Tp", "elev", "ha_deg", "Ta"],     "++ nhiet do khong khi"),
    (["G", "Tp", "elev", "ha_deg", "RH"],     "++ do am"),
    (["G", "Tp", "elev", "ha_deg", "Ta", "RH", "WS"], "Tat ca bay bien"),
]
MOI_BIEN = ["G", "Tp", "Ta", "RH", "WS", "elev", "ha_deg"]


def thu_nghiem_1(d, folds, loai):
    """FC-01: nhiet do tam pin la so DO DUOC, dung truc tiep lam bien dau vao."""
    print("\n" + "=" * 78)
    print("PHEP THU 1 — Bo bien dau vao, truong hop FC-01 (co nhiet do tam pin do duoc)")
    print("=" * 78)
    print(f"Mo hinh: {loai} | goc truot {len(folds)} fold | thang kiem dinh: "
          f"{', '.join(str(f) for f in folds)}")
    print("Moi bo bien duoc cham tren CUNG MOT tap mau.\n")

    print(f'{"Bo bien dau vao":38} {"MAE":>7} {"MAE ngay":>9} {"RMSE":>7} {"NMAE":>7} {"cai thien":>10}')
    print("-" * 78)
    goc, rows = None, []
    for cols, nhan in BO_BIEN:
        r = danh_gia(d, cols, folds, loai)
        if r is None:
            print(f"{nhan:38}   (khong du du lieu)")
            continue
        if goc is None:
            goc = r["MAE"]
        ct = (goc - r["MAE"]) / goc * 100
        print(f'{nhan:38} {r["MAE"]:7.3f} {r["MAE_ban_ngay"]:9.3f} '
              f'{r["RMSE"]:7.3f} {r["NMAE_%"]:6.2f}% {ct:9.1f}%')
        rows.append({"bo_bien": nhan, "cot": " ".join(cols), **r, "cai_thien_%": ct})
    return pd.DataFrame(rows)


def thu_nghiem_2(d, folds, loai):
    """FC-02: ngay mai KHONG co nhiet do tam pin, phai du bao no truoc.

    Day la diem ma toc do gio va nhiet do khong khi thuc su di vao bai toan.
    """
    print("\n" + "=" * 78)
    print("PHEP THU 2 — Truong hop FC-02: phai du bao nhiet do tam pin trung gian")
    print("=" * 78)

    ngay = d[d["G"] > 50].dropna(subset=["G", "Ta", "WS", "Tp"])
    thang = ngay.index.to_period("M")
    tr, te = ngay[thang < folds[0]], ngay[thang.isin(folds)]
    if len(tr) < 1000 or len(te) < 300:
        print("Khong du du lieu cho phep thu nay.")
        return None

    # mo hinh Faiman: Tp = Ta + G / (U0 + U1 * v)
    tot = None
    for u0 in np.arange(10, 45, 0.5):
        for u1 in np.arange(0, 14, 0.25):
            e = np.abs(tr["Ta"] + tr["G"] / (u0 + u1 * tr["WS"]) - tr["Tp"]).mean()
            if tot is None or e < tot[0]:
                tot = (e, u0, u1)
    _, u0, u1 = tot

    bien_the = {
        "Faiman day du: Ta + G/(U0+U1*v)": te["Ta"] + te["G"] / (u0 + u1 * te["WS"]),
        "Bo toc do gio:  Ta + G/U0":       te["Ta"] + te["G"] / u0,
        "Chi nhiet do khong khi":          te["Ta"],
    }
    print(f"Tham so uoc luong tren tap huan luyen: U0 = {u0:.1f}, U1 = {u1:.2f}\n")
    print(f'{"Cach du bao nhiet do tam pin":36} {"MAE (degC)":>11} {"~ MW tuong duong":>18}')
    print("-" * 78)
    for nhan, pred in bien_the.items():
        mae = np.abs(pred - te["Tp"]).mean()
        mw = mae * abs(HE_SO_NHIET) * CAP_AC
        print(f"{nhan:36} {mae:11.2f} {mw:18.3f}")
    print(f"\nQuy doi: sai 1 degC nhiet do tam pin ~ {abs(HE_SO_NHIET)*100:.2f}% x {CAP_AC:.0f} MW "
          f"= {abs(HE_SO_NHIET)*CAP_AC:.3f} MW")
    print("Day la phan sai so CONG THEM cua FC-02 so voi tran ly tuong o Phep thu 1.")

    # do truc tiep: thay Tp do duoc bang Tp du bao roi cham lai mo hinh cong suat
    d2 = d.copy()
    d2["Tp_du_bao"] = d2["Ta"] + d2["G"] / (u0 + u1 * d2["WS"])
    cols_that = ["G", "Tp", "elev", "ha_deg"]
    cols_uoc = ["G", "Tp_du_bao", "elev", "ha_deg"]
    base = d2.dropna(subset=MOI_BIEN + ["Tp_du_bao", "P"])
    a = danh_gia(base, cols_that, folds, loai)
    b = danh_gia(base, cols_uoc, folds, loai)
    if a and b:
        print(f'\n{"Mo hinh cong suat":36} {"MAE":>8} {"NMAE":>8}')
        print("-" * 78)
        print(f'{"Dung nhiet do tam pin DO DUOC (FC-01)":36} {a["MAE"]:8.3f} {a["NMAE_%"]:7.2f}%')
        print(f'{"Dung nhiet do tam pin DU BAO (FC-02)":36} {b["MAE"]:8.3f} {b["NMAE_%"]:7.2f}%')
        print(f'{"Phan cong them do phai du bao Tp":36} {b["MAE"]-a["MAE"]:8.3f} '
              f'{b["NMAE_%"]-a["NMAE_%"]:7.2f}%')
    return {"U0": u0, "U1": u1}


def thu_nghiem_3(d, folds):
    """Do quan trong cua tung bien bang hoan vi — cham tren mo hinh biet chon loc bien."""
    try:
        from sklearn.inspection import permutation_importance
    except ImportError:
        print("\n(Bo qua Phep thu 3: can scikit-learn)")
        return None
    print("\n" + "=" * 78)
    print("PHEP THU 3 — Do quan trong tung bien bang phep hoan vi")
    print("=" * 78)
    print("Xao tron ngau nhien tung cot roi do sai so tang bao nhieu.")
    print("Tang nhieu = bien quan trong. Gan 0 = mo hinh khong dung den bien do.\n")

    thang = d.index.to_period("M")
    tr, te = d[thang < folds[0]], d[thang.isin(folds)]
    m = tao_mo_hinh("gbm")
    m.fit(tr[MOI_BIEN].values, tr["P"].values)
    r = permutation_importance(m, te[MOI_BIEN].values, te["P"].values,
                               n_repeats=10, random_state=0,
                               scoring="neg_mean_absolute_error")
    out = pd.DataFrame({
        "bien": MOI_BIEN,
        "MAE_tang_MW": r.importances_mean,
        "do_lech_chuan": r.importances_std,
    }).sort_values("MAE_tang_MW", ascending=False)
    print(f'{"Bien":10} {"MAE tang (MW)":>15} {"do lech chuan":>15}')
    print("-" * 78)
    for _, x in out.iterrows():
        print(f'{x["bien"]:10} {x["MAE_tang_MW"]:15.4f} {x["do_lech_chuan"]:15.4f}')
    return out


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", default="../data/csv", help="thu muc chua CSV da trich xuat")
    ap.add_argument("--out", default="../data/thu_nghiem", help="thu muc ghi ket qua")
    ap.add_argument("--buoc", default="15min", help="buoc thoi gian, mac dinh 15min cho FC-02")
    ap.add_argument("--mo-hinh", default="gbm", choices=["gbm", "knn", "tuyen_tinh"])
    ap.add_argument("--so-fold", type=int, default=5)
    a = ap.parse_args()

    csv_dir, out_dir = Path(a.csv), Path(a.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    if tao_mo_hinh("gbm") is None:
        sys.exit("Thieu scikit-learn. Chay:  pip install scikit-learn")

    print("Nap du lieu ...")
    d = nap_du_lieu(csv_dir, a.buoc)
    print(f"  {len(d):,} o thoi gian buoc {a.buoc}")

    d = lam_sach(d)
    d = them_hinh_hoc_mat_troi(d)

    # ---- buoc kiem tra bat buoc truoc khi so sanh bat cu thu gi
    print("\n" + "=" * 78)
    print("BUOC KIEM TRA — do san co cua tung cam bien theo thang (%, chi xet ban ngay)")
    print("=" * 78)
    san_co = bao_cao_do_san_co(d)
    print(san_co.to_string())
    san_co.to_csv(out_dir / "do_san_co_cam_bien.csv")

    folds = chon_thang_kiem_dinh(san_co, so_fold=a.so_fold)
    if len(folds) < 2:
        sys.exit("\nKhong du thang ma moi cam bien deu con song de lam tap kiem dinh.")
    bo_qua = [str(t) for t in san_co.index if t not in folds]
    print(f"\nThang dung lam tap kiem dinh: {', '.join(str(f) for f in folds)}")
    if bo_qua:
        print(f"Thang bi loai (co cam bien khong du du lieu): {', '.join(bo_qua)}")
    print("\nLuu y: neu Ta va RH tut ve 0% o cac thang cuoi thi hai cam bien do da hong.")
    print("Khong duoc lay thang do lam tap kiem dinh, neu khong tap se rong sau khi loc NaN.")

    # ---- tap mau chung: moi bo bien phai duoc cham tren cung mot so dong
    truoc = len(d)
    d = d.dropna(subset=MOI_BIEN + ["P"])
    print(f"\nTap mau chung sau khi loai NaN: {len(d):,} / {truoc:,} o "
          f"({len(d)/truoc*100:.1f}%), trong do {int((d['G']>50).sum()):,} o ban ngay")

    kq1 = thu_nghiem_1(d, folds, a.mo_hinh)
    if kq1 is not None and not kq1.empty:
        kq1.to_csv(out_dir / "so_sanh_bo_bien.csv", index=False)

    thu_nghiem_2(d, folds, a.mo_hinh)

    kq3 = thu_nghiem_3(d, folds)
    if kq3 is not None:
        kq3.to_csv(out_dir / "do_quan_trong_bien.csv", index=False)

    print("\n" + "=" * 78)
    print(f"Da ghi ket qua vao {out_dir.resolve()}")
    print("=" * 78)
    print("""
Cach doc ket qua:
  * Cot "MAE ngay" quan trong hon cot "MAE". MAE toan bo bi pha loang boi ban dem
    khi cong suat gan 0 va mo hinh nao cung doan dung.
  * Bien nao lam MAE ngay giam duoi 0,02 MW thi coi nhu khong dong gop.
  * Neu "Tat ca bay bien" te hon "+ tam pin + hinh hoc mat troi" thi do la dau hieu
    cac bien con lai chi them nhieu. Voi cay tang cuong dieu nay hiem xay ra;
    neu chay bang --mo-hinh knn thi rat de xay ra do phat vi tang so chieu.
  * Phep thu 2 moi la con so dung cho FC-02. Phep thu 1 la tran ly tuong.
""")


if __name__ == "__main__":
    main()
