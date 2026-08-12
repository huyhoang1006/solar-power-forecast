"""
tao_bo_du_lieu.py
Dung bo du lieu huan luyen: gop du lieu khi tuong voi bien muc tieu cong suat.

Thuc hien dung cac quy tac da chot trong bao cao khao sat:
  muc 4.3   sap xep theo thoi gian truoc khi lam bat cu viec gi
  muc 10.3  khu trung, ap luoi thoi gian, gop tu min len tho
  muc 10.4  gan co chat luong, khong gan gia tri thieu bang 0
  muc 6.4   loai cac doan cam bien Rad_2 treo gia tri
  muc 7.6   gia tri 0 ban ngay la mat tin hieu
  muc 8.2   chan nhom diem do IEC104 khoi bien dau vao (ro ri du lieu tuong lai)
  FR-05     bo du lieu co phien ban, ma kiem tra noi dung, luu cau hinh da dung

Cach chay:
    pip install pandas numpy pyarrow
    python tao_bo_du_lieu.py --csv ../data/csv --out ../data/dataset --buoc 15min

Diem quan trong ve cach ghep bang:
    Cac bang nguon KHONG co khoa ngoai. Cot ID chi la so thu tu dong rieng cua
    tung bang. Moc thoi gian giua hai bang bat ky khong bao gio trung khop tuyet
    doi -- ghep bang dau bang cho ra 0 dong. Lien ket duy nhat la thoi gian, va
    phai lam tron ve mot luoi chung truoc khi ghep.
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

PHIEN_BAN = "1.0"

# ---------------------------------------------------------------- hang so nha may
LAT, LON = 13.8634, 109.2708
KINH_TUYEN_MUI = 105.0
CAP_AC, CAP_DC = 40.0, 50.0

# ---------------------------------------------------------------- ma chat luong (Bang 10.2)
QC = {
    "OK": 0, "MISSING": 1, "OUT_OF_RANGE": 2, "SPIKE": 3, "STALE": 4,
    "LOW_COVERAGE": 5, "SENSOR_FROZEN": 6, "FEEDER_OUTAGE": 7, "ZERO_IN_DAYLIGHT": 8,
}

# ---------------------------------------------------------------- bang anh xa (Bang 10.1)
ANH_XA = {
    # bien chuan          (bang nguon,  cot nguon,                            min,    max)
    "p_ac_mw":     ("His_131", "Substation_Level_110kV_Bay131_MEAS_P",      -2.0,   45.0),
    "q_ac_mvar":   ("His_131", "Substation_Level_110kV_Bay131_MEAS_Q",     -45.0,   45.0),
    "p_ac_mw_bak": ("His_431", "Substation_Level_22kV_Bay431_MEAS_P",       -2.0,   45.0),
    "ghi_wm2":     ("Weather", "SOLAR_WS_Rad_1",                             0.0, 1350.0),
    "ghi_wm2_alt": ("Weather", "SOLAR_WS_Rad_2",                             0.0, 1350.0),
    "t_panel_c":   ("Weather", "SOLAR_WS_Panel_T",                         -10.0,   90.0),
    "t_air_c":     ("Weather", "SOLAR_WS_Air_T",                           -10.0,   55.0),
    "rh_pct":      ("Weather", "SOLAR_WS_Humidity",                          0.0,  100.0),
    "wind_ms":     ("Weather", "SOLAR_WS_Wind_Speed",                        0.0,   60.0),
}

LO_22KV = {
    "p_471": ("His_471", "Substation_Level_22kV_Bay471_Meas_P"),
    "p_473": ("His_473", "Substation_Level_22kV_Bay473_Meas_P"),
    "p_475": ("His_475", "Substation_Level_22kV_Bay475_Meas_P"),
    "p_477": ("His_477", "Substation_Level_22kV_Bay477_Meas_P"),
}

NGUONG_BUC_XA_NGAY = 50.0     # W/m2, ranh gioi ngay dem cho quy tac ma 8
DO_PHU_TOI_THIEU = 0.80       # FR-03 / ma 5

# Cac bien mà gia tri 0 la SO DO THAT, khong duoc ap quy tac ma 8 cho chung.
#
#   wind_ms      -- lang gio la hien tuong co that. Kiem tren du lieu nha may:
#                   7.557 mau co gio bang 0 luc co nang, buc xa trung binh 346 W/m2
#                   va nhiet do khong khi 20,9 degC deu binh thuong, va chung don vao
#                   khung 6-9 gio sang. Do la lang gio som mai chu khong phai mat
#                   tin hieu. Ap ma 8 cho bien nay la vut bo so do that.
#   q_ac_mvar    -- cong suat phan khang doi dau lien tuc nen di qua 0 la binh thuong.
#   ghi_wm2 va ghi_wm2_alt -- khi buc xa bang 0 thi dieu kien "ban ngay" da sai, quy
#                   tac khong the kich hoat; van liet ke ra day cho ro rang.
#
# Nguoc lai, nhiet do khong khi, nhiet do tam pin va do am bang 0 giua trua tai
# Binh Dinh la khong the, nen chung VAN ap quy tac.
BIEN_CO_THE_BANG_0 = ("wind_ms", "q_ac_mvar", "ghi_wm2", "ghi_wm2_alt")


# ================================================================ doc va chuan hoa
def doc_bang(csv_dir, ten_bang, cot_can, buoc_luoi="60s"):
    """Doc mot bang, loc ban ghi hop le, ap luoi thoi gian chung.

    Bon buoc theo muc 10.3, va mot buoc bo sung tim ra khi ra soat lai du lieu:
    chi giu LogType = 1. Hai gia tri con lai la ban ghi danh dau phien ghi
    (89 ban ghi tren toan bo His_131, thieu cong suat toi 96%).
    """
    p = csv_dir / f"{ten_bang}.csv"
    if not p.exists():
        return None
    cot_doc = ["ts_local", "LogType"] + cot_can
    try:
        d = pd.read_csv(p, usecols=lambda c: c in cot_doc, parse_dates=["ts_local"])
    except ValueError:
        return None
    thieu = [c for c in cot_can if c not in d.columns]
    if thieu:
        print(f"    canh bao: {ten_bang} khong co cot {thieu}")
        cot_can = [c for c in cot_can if c in d.columns]
        if not cot_can:
            return None

    n0 = len(d)
    if "LogType" in d.columns:
        d = d[d["LogType"] == 1]
    d = d.drop(columns=[c for c in ("LogType",) if c in d.columns])

    # buoc 1 -- sap xep (muc 4.3). Bat buoc, du lieu nguon khong theo thu tu thoi gian.
    d = d.sort_values("ts_local")
    # buoc 2 -- khu trung, giu ban ghi nhan sau cung
    d = d.drop_duplicates(subset="ts_local", keep="last")
    # buoc 4 -- ap luoi thoi gian chung. Day la co che ghep bang duy nhat kha thi.
    d["ts"] = d["ts_local"].dt.round(buoc_luoi)
    d = d.groupby("ts")[cot_can].mean()

    print(f"    {ten_bang:11} {n0:8,} -> {len(d):8,} o luoi {buoc_luoi}")
    return d


def gop_nguon(csv_dir, buoc_luoi="60s", kem_lo_22kv=True):
    """Gop moi bang nguon ve mot khung du lieu tren luoi thoi gian chung."""
    print("  Doc va ap luoi thoi gian:")
    can = {}
    for bien, (bang, cot, _, _) in ANH_XA.items():
        can.setdefault(bang, []).append((bien, cot))
    if kem_lo_22kv:
        for bien, (bang, cot) in LO_22KV.items():
            can.setdefault(bang, []).append((bien, cot))

    khung = []
    for bang, cap in can.items():
        d = doc_bang(csv_dir, bang, [c for _, c in cap], buoc_luoi)
        if d is None:
            continue
        d = d.rename(columns={c: b for b, c in cap})
        khung.append(d)
    if not khung:
        sys.exit("Khong doc duoc bang nguon nao.")

    d = pd.concat(khung, axis=1, sort=False)
    d = d.reindex(pd.date_range(d.index.min(), d.index.max(), freq=buoc_luoi))
    d.index.name = "ts"
    return d


# ================================================================ hinh hoc mat troi
def them_hinh_hoc(d):
    """Goc mat troi tinh tu toa do, khong lay tu du lieu do.

    Day la bo dac trung thay cho moi thu dac trung thoi gian thu cong. Khong dung
    co nhi phan truoc/sau mot moc gio co dinh: giua trua mat troi tai nha may troi
    tu 11:27 den 11:57 trong nam nen moc co dinh se gan sai nhan (muc 6.3).
    """
    doy = d.index.dayofyear.values
    b = 2 * np.pi * (doy - 1) / 365.0
    eot = 229.18 * (0.000075 + 0.001868 * np.cos(b) - 0.032077 * np.sin(b)
                    - 0.014615 * np.cos(2 * b) - 0.040849 * np.sin(2 * b))
    dec = np.radians(23.45) * np.sin(2 * np.pi * (284 + doy) / 365.0)
    phut = d.index.hour.values * 60 + d.index.minute.values + d.index.second.values / 60.0
    ha = np.radians((phut + (LON - KINH_TUYEN_MUI) * 4 + eot - 720) / 4.0)

    lat = np.radians(LAT)
    sin_h = np.sin(lat) * np.sin(dec) + np.cos(lat) * np.cos(dec) * np.cos(ha)
    sin_h = np.clip(sin_h, -1, 1)

    d["sol_elev"] = np.degrees(np.arcsin(sin_h))
    # Goc gio de NGUYEN chua goi ve [-180, 180] o buoc nay. Ly do: gop_len lay
    # trung binh cong tren tung o 15 phut, ma trung binh cong cua goc bi goi la
    # sai -- mot o nam vat qua ranh gioi se cho 179 va -179 ra 0 do, tuc dung
    # bang dau hieu cua giua trua mat troi. Viec goi duoc lam mot lan duy nhat
    # o cuoi gop_len, sau khi da lay trung binh xong (ham goi_goc_gio).
    d["sol_ha"] = np.degrees(ha)                       # am = sang, duong = chieu
    cos_z = np.clip(sin_h, 0, None)
    d["sol_azi"] = np.degrees(np.arctan2(
        np.sin(ha), np.cos(ha) * np.sin(lat) - np.tan(dec) * np.cos(lat)))
    # buc xa ngoai khi quyen tren mat ngang -- dung de chuan hoa, khong can hieu chinh
    d["ghi_ngoai_kq"] = 1361.0 * cos_z
    # chi so troi quang: ty so giua buc xa do va buc xa ngoai khi quyen.
    # Ban dem dat bang 0 chu khong phai NaN -- neu de NaN thi moi dong ban dem se bi
    # loai khi huan luyen, va mo hinh FC-01 se khong bao gio nhin thay ban dem.
    with np.errstate(invalid="ignore", divide="ignore"):
        kt = np.where(d["ghi_ngoai_kq"] > 20, d["ghi_wm2"] / d["ghi_ngoai_kq"], 0.0)
    d["kt"] = np.clip(kt, 0, 1.2)
    d.loc[d["ghi_wm2"].isna() & (d["ghi_ngoai_kq"] > 20), "kt"] = np.nan
    return d


def canh_bao_cam_bien_chet(d):
    """Canh bao som neu mot cam bien tat han o giai doan cuoi chuoi.

    Neu bo qua buoc nay, tap kiem dinh se rong sau khi loai NaN va moi so sanh
    giua cac bo bien deu vo nghia. Tren du lieu khao sat, nhiet do khong khi va
    do am tat han tu thang 5/2026.
    """
    ngay = d[d["ghi_wm2"] > NGUONG_BUC_XA_NGAY]
    if len(ngay) == 0:
        return
    g = ngay.groupby(ngay.index.to_period("M"))
    bien = [b for b in ANH_XA if b in d.columns]
    tl = pd.DataFrame({b: g[b].apply(lambda s: s.notna().mean() * 100) for b in bien}).round(1)

    canh_bao = []
    cuoi = tl.tail(3)
    for b in bien:
        if len(cuoi) and cuoi[b].max() < 50 and tl[b].head(3).min() > 80:
            thang_chet = tl.index[tl[b] < 50][0] if (tl[b] < 50).any() else None
            canh_bao.append((b, thang_chet, cuoi[b].mean()))

    if canh_bao:
        print("\n  CANH BAO -- cam bien tat han o giai doan cuoi chuoi:")
        for b, thang, con in canh_bao:
            print(f"    {b:13} chet tu khoang {thang}, ba thang cuoi con {con:.0f}%")
        print("    Khong dua cac bien nay vao mo hinh neu chua co ke hoach thay the,")
        print("    va khong lay ba thang cuoi lam tap kiem dinh cho chung.")
    return tl


# ================================================================ co chat luong
def phat_hien_cam_bien_treo(d, cot, cot_doi_chieu, cua_so=60, bien_do_toi_da=10.0):
    """Ma 6 -- cam bien giu nguyen gia tri khi tram mat tin hieu (muc 6.4).

    Hai dieu kien dong thoi: bien do trong cua so rat nho, va cam bien khac cua
    cung tram khong co du lieu. KHONG dung phep tru hang so: trung vi ban dem cua
    Rad_2 bang 0 nen phep tru se khong lam gi ca.
    """
    if cot not in d.columns:
        return pd.Series(False, index=d.index)
    r = d[cot].rolling(cua_so, center=True, min_periods=cua_so // 2)
    bien_do = r.max() - r.min()
    tram_chet = d[cot_doi_chieu].isna()
    if "t_air_c" in d.columns:
        tram_chet = tram_chet & d["t_air_c"].isna()
    return (bien_do < bien_do_toi_da) & tram_chet & d[cot].notna()


def phat_hien_su_co_lo(d, nguong_ty_le=0.05, so_buoc=3):
    """Ma 7 -- mot lo 22 kV mat trong khi cac lo khac van phat (muc 5.5).

    Phan biet may che voi su co lo. May che lam moi lo giam cung luc theo ty le;
    su co lam mot lo ve 0 con cac lo khac giu nguyen. Neu khong tach hai truong
    hop nay, mo hinh se hoc rang troi nang van co the tut cong suat.
    """
    cot = [c for c in LO_22KV if c in d.columns]
    if len(cot) < 3:
        return pd.Series(False, index=d.index)
    X = d[cot]
    su_co = pd.Series(False, index=d.index)
    for c in cot:
        khac = X[[k for k in cot if k != c]].mean(axis=1)
        bat_thuong = (X[c] < nguong_ty_le * khac) & (khac > 1.0)
        lien_tuc = bat_thuong.rolling(so_buoc, min_periods=so_buoc).sum() >= so_buoc
        su_co |= lien_tuc.fillna(False).astype(bool)
    return su_co


def gan_co_chat_luong(d):
    """Gan ma chat luong cho tung bien. Gia tri bi loai duoc dat NaN, khong dat 0."""
    print("  Gan co chat luong:")
    thong_ke = {}
    ban_ngay = d["ghi_wm2"] > NGUONG_BUC_XA_NGAY

    su_co_lo = phat_hien_su_co_lo(d)
    treo_alt = phat_hien_cam_bien_treo(d, "ghi_wm2_alt", "ghi_wm2")

    for bien, (_, _, vmin, vmax) in ANH_XA.items():
        if bien not in d.columns:
            continue
        q = pd.Series(QC["OK"], index=d.index, dtype="int8")

        # ma 1 -- thieu
        q[d[bien].isna()] = QC["MISSING"]

        # ma 2 -- ngoai nguong vat ly cua bang anh xa
        ngoai = d[bien].notna() & ((d[bien] < vmin) | (d[bien] > vmax))
        q[ngoai] = QC["OUT_OF_RANGE"]

        # ma 8 -- bang dung 0 trong khoang co buc xa (muc 7.6).
        # Chi ap cho cac bien ma 0 giua trua la khong the ve mat vat ly.
        # Xem ghi chu o BIEN_CO_THE_BANG_0 phia tren.
        if bien not in BIEN_CO_THE_BANG_0:
            zero_ngay = ban_ngay & d[bien].eq(0)
            q[zero_ngay] = QC["ZERO_IN_DAYLIGHT"]

        # ma 6 -- cam bien treo gia tri
        if bien == "ghi_wm2_alt":
            q[treo_alt] = QC["SENSOR_FROZEN"]

        # ma 4 -- gia tri khong doi qua lau, xet tren CA CHUOI chu khong chi ban ngay
        if bien in ("ghi_wm2", "t_panel_c", "t_air_c", "rh_pct"):
            khong_doi = d[bien].diff().abs().lt(1e-9)
            chuoi = khong_doi.groupby((~khong_doi).cumsum()).cumsum()
            q[(chuoi > 30) & (q == QC["OK"]) & ban_ngay] = QC["STALE"]

        # ma 3 -- buoc nhay bat thuong
        if bien in ("p_ac_mw", "p_ac_mw_bak"):
            nhay = d[bien].diff().abs() > 0.5 * CAP_AC
            q[nhay.fillna(False) & (q == QC["OK"])] = QC["SPIKE"]

        # ma 7 -- su co lo, chi ap cho bien cong suat
        if bien in ("p_ac_mw", "p_ac_mw_bak"):
            q[su_co_lo & (q == QC["OK"])] = QC["FEEDER_OUTAGE"]

        d[f"qc_{bien}"] = q
        # gia tri khong dung duoc -> NaN. Yeu cau FR-04: khong gan bang 0.
        d.loc[q != QC["OK"], bien] = np.nan
        thong_ke[bien] = q.value_counts().to_dict()

        xau = int((q != QC["OK"]).sum())
        print(f"    {bien:13} loai {xau:7,} / {len(q):,} ban ghi ({xau/len(q)*100:5.2f}%)")

    return d, thong_ke


def goi_goc_gio(d):
    """Goi sol_ha ve dai chuan [-180, 180] do.

    Cong thuc goc gio tinh tu phut trong ngay cong hieu chinh kinh do va phuong
    trinh thoi gian. Tong hieu chinh tai Fujiwara khoang +6,4 do, nen nua dem
    dia phuong roi vao khoang 186 do chu khong phai dung 180 -- do la ly do co
    387 o (1,12%) vuot nguong, tat ca deu o 23 gio va deu la ban dem, khong o
    nao lot vao tap ban ngay dang dung de cham. Vi vay loi nay khong lam thay
    doi bat ky con so nao da bao cao.

    Van phai sua, vi hai ly do: FC-01 dung dac trung tre nen se cham vao vung
    ban dem, va mot bien duoc mo ta la "goc gio" ma tra ve 186 do thi bat ky ai
    doi chieu voi tai lieu thien van cung se coi la sai.
    """
    if "sol_ha" in d.columns:
        d["sol_ha"] = (d["sol_ha"] + 180.0) % 360.0 - 180.0
    return d


# ================================================================ gop len buoc lon
def gop_len(d, buoc_dich="15min", buoc_luoi="60s"):
    """Gop tu do phan giai min len tho. Chi duoc gop theo chieu nay (FR-03).

    Cong suat lay trung binh, san luong lay tich phan hinh thang, buc xa trung binh.
    O nao khong du DO_PHU_TOI_THIEU so mau -> danh dau ma 5 va dat NaN.
    """
    giay_luoi = pd.Timedelta(buoc_luoi).total_seconds()
    n_mong_doi = pd.Timedelta(buoc_dich).total_seconds() / giay_luoi
    g = d.resample(buoc_dich, label="left", closed="left")

    bien_tb = [b for b in ANH_XA if b in d.columns]
    bien_hh = ["sol_elev", "sol_ha", "sol_azi", "ghi_ngoai_kq", "kt"]

    out = g[bien_tb].mean()
    for c in bien_hh:
        if c in d.columns:
            out[c] = g[c].mean()

    # san luong -- yeu cau FC-01..FC-04 phai xuat ca cong suat va san luong
    def tich_phan(s):
        s = s.dropna()
        if len(s) < 2:
            return np.nan
        return float(np.trapezoid(s.values, dx=giay_luoi) / 3600.0)

    out["e_ac_mwh"] = g["p_ac_mw"].apply(tich_phan)
    out["n_mau"] = g["p_ac_mw"].count()
    out["do_phu"] = out["n_mau"] / n_mong_doi

    thieu_phu = out["do_phu"] < DO_PHU_TOI_THIEU
    out["qc_gop"] = np.where(thieu_phu, QC["LOW_COVERAGE"], QC["OK"]).astype("int8")
    out.loc[thieu_phu, ["p_ac_mw", "e_ac_mwh", "ghi_wm2"]] = np.nan

    # Goi goc gio SAU khi da lay trung binh -- xem giai thich trong goi_goc_gio()
    out = goi_goc_gio(out)

    print(f"  Gop {buoc_luoi} -> {buoc_dich}: {len(out):,} o, "
          f"{int(thieu_phu.sum()):,} o thieu do phu ({thieu_phu.mean()*100:.2f}%)")
    return out


# ================================================================ ghi ket qua
def ghi_bo_du_lieu(d, out_dir, tham_so, thong_ke_qc):
    out_dir.mkdir(parents=True, exist_ok=True)
    ten = f"bo_du_lieu_{tham_so['buoc']}"

    duong_parquet = out_dir / f"{ten}.parquet"
    try:
        d.to_parquet(duong_parquet)
        duong_chinh = duong_parquet
    except Exception as e:                       # thieu pyarrow
        print(f"  (khong ghi duoc parquet: {e}; chuyen sang CSV)")
        duong_chinh = out_dir / f"{ten}.csv"
        d.to_csv(duong_chinh)

    duong_csv = out_dir / f"{ten}.csv"
    if duong_chinh != duong_csv:
        d.to_csv(duong_csv)
        da_ghi = [duong_chinh.name, duong_csv.name]
    else:
        da_ghi = [duong_csv.name]

    # FR-05 -- ma kiem tra noi dung, phien ban, cau hinh da dung
    h = hashlib.sha256(pd.util.hash_pandas_object(d, index=True).values.tobytes()).hexdigest()
    sieu_du_lieu = {
        "phien_ban_script": PHIEN_BAN,
        "tao_luc": datetime.now(timezone.utc).isoformat(),
        "ma_kiem_tra_sha256": h,
        "so_dong": int(len(d)),
        "so_cot": int(d.shape[1]),
        "pham_vi_thoi_gian": [str(d.index.min()), str(d.index.max())],
        "mui_gio": "Asia/Ho_Chi_Minh (gio dia phuong nha may)",
        "tham_so": tham_so,
        "nha_may": {"capacity_ac_mw": CAP_AC, "capacity_dc_mw": CAP_DC,
                    "lat": LAT, "lon": LON},
        "anh_xa": {k: {"bang": v[0], "cot": v[1], "min": v[2], "max": v[3]}
                   for k, v in ANH_XA.items()},
        "ma_chat_luong": QC,
        "thong_ke_chat_luong": {k: {str(a): int(b) for a, b in v.items()}
                                for k, v in thong_ke_qc.items()},
        "do_phu_theo_bien": {c: float(d[c].notna().mean())
                             for c in d.columns if not c.startswith("qc_")},
    }
    (out_dir / f"{ten}_sieu_du_lieu.json").write_text(
        json.dumps(sieu_du_lieu, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n  Da ghi:")
    for f in da_ghi + [f"{ten}_sieu_du_lieu.json"]:
        print(f"          {f}")
    print(f"  Ma kiem tra noi dung: {h[:16]}...")
    return duong_chinh


# ================================================================ main
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    goc = Path(__file__).resolve().parent.parent      # thu muc goc du an
    ap.add_argument("--csv", default=str(goc / "data" / "csv"))
    ap.add_argument("--out", default=str(goc / "data" / "dataset"))
    ap.add_argument("--buoc", default="15min", help="do phan giai dich: 15min cho FC-02, 5min cho FC-01")
    ap.add_argument("--luoi", default="60s", help="luoi thoi gian trung gian, mac dinh 60s theo nguon")
    ap.add_argument("--khong-lo-22kv", action="store_true", help="bo qua phat hien su co lo")
    a = ap.parse_args()

    csv_dir, out_dir = Path(a.csv), Path(a.out)
    if not csv_dir.exists():
        sys.exit(f"Khong thay {csv_dir}. Chay truoc:\n"
                 f"    python export_to_csv.py ../db_fujiwara.sql -o ../data/csv --tz 7")

    print("=" * 74)
    print("DUNG BO DU LIEU HUAN LUYEN")
    print("=" * 74)

    d = gop_nguon(csv_dir, a.luoi, not a.khong_lo_22kv)
    print(f"  Khung gop: {len(d):,} o, {d.shape[1]} cot, "
          f"{d.index.min()} -> {d.index.max()}")

    d = them_hinh_hoc(d)
    d, tk = gan_co_chat_luong(d)
    canh_bao_cam_bien_chet(d)
    d = gop_len(d, a.buoc, a.luoi)

    # bo cac o khong co bien muc tieu -- khong the huan luyen tren do
    truoc = len(d)
    d = d[d["p_ac_mw"].notna()]
    print(f"  Bo {truoc - len(d):,} o khong co bien muc tieu -> con {len(d):,} o")

    print("\n  Do phu tung bien sau xu ly:")
    for c in [c for c in d.columns if not c.startswith(("qc_", "n_mau", "do_phu"))]:
        print(f"    {c:15} {d[c].notna().mean()*100:6.2f}%")

    tham_so = {"buoc": a.buoc, "luoi": a.luoi, "nguon": str(csv_dir.resolve()),
               "do_phu_toi_thieu": DO_PHU_TOI_THIEU,
               "nguong_buc_xa_ngay": NGUONG_BUC_XA_NGAY}
    duong = ghi_bo_du_lieu(d, out_dir, tham_so, tk)

    print("\n" + "=" * 74)
    print("Buoc tiep theo:")
    print(f"    python huan_luyen_mo_hinh.py --du-lieu {duong.as_posix()}")
    print("=" * 74)


if __name__ == "__main__":
    main()
