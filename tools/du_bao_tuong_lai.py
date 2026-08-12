"""
du_bao_tuong_lai.py
Du bao cong suat nha may Fujiwara cho NGAY MAI va hai ngay ke tiep.

Khac biet co ban so voi phan danh gia trong huan_luyen_mo_hinh.py:

    Danh gia qua khu   : buc xa DO DUOC -> cong suat.  Do la tran cua mo hinh.
    Du bao ngay mai    : buc xa DU BAO   -> cong suat.  Do la thuc te van hanh.

Hai con so nay khong so sanh duoc voi nhau. NMAE 4,43% do bang goc truot la sai so
cua rieng khau doi buc xa sang cong suat, voi buc xa dung. Khi thay buc xa do bang
buc xa NWP thi sai so cua NWP cong them vao, va no lon hon nhieu lan phan con lai.
Vi vay moi dau ra cua tep nay deu ghi kem canh bao do; khong duoc dat con so 4,43%
canh bang du bao ngay mai.

Vi sao BO nhiet do tam pin (dung nhu nhan xet cua nguoi dung, va do duoc bang so):

    Loi cua viec CO nhiet do tam pin   : +0,136 MW (phep hoan vi tren du lieu qua khu)
    Sai so khi PHAI uoc luong nhiet do : 2,31 degC MAE tren tap kiem dinh sach
                                         -> ~0,32 MW tuong duong cong suat

  Cai gia cao gap hon hai lan cai loi, nen dua nhiet do tam pin vao chi lam xau di.
  Chua ke cam bien nhiet do khong khi tai nha may da hong tu 03/2026 (do phu tut
  con 6% roi 1%, phan con lai bao 0 degC giua trua), nen neu bat buoc phai co Ta
  thi tap huan luyen se mat nam thang gan nhat.

  Bo dac trung dung o day: ghi_wm2, sol_elev, sol_ha, ghi_ngoai_kq -- ba trong bon
  bien tinh tu toa do va dong ho, khong can cam bien nao. Chi mot bien duy nhat
  phai di xin NWP.

Cach chay:

    python tools/du_bao_tuong_lai.py                 # 3 ngay toi, ghi ra data/du_bao
    python tools/du_bao_tuong_lai.py --so-ngay 5
    python tools/du_bao_tuong_lai.py --mo-hinh ecmwf_ifs025

Nguon buc xa: Open-Meteo (CC BY 4.0). Cung nguon voi tools/thu_thap_du_bao.py.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

GOC = Path(__file__).resolve().parent
sys.path.insert(0, str(GOC))

import huan_luyen_mo_hinh as H          # noqa: E402
import tao_bo_du_lieu as T              # noqa: E402
import thu_thap_du_bao as TT            # noqa: E402

BUOC = "15min"
BUOC_PHUT = 15

# Chi nhan cac mo hinh da qua kiem tra trong thu_thap_du_bao.MO_HINH. Cac mo hinh
# bi loai (ARPEGE 2327 W/m2, GEM 2557 W/m2, JMA khong co cot buc xa...) khong duoc
# xuat hien o day. Xem chu thich MO_HINH_THU trong tep do.
MO_HINH_MAC_DINH = list(TT.MO_HINH)

KT_TOI_DA = 1.2         # chi so troi quang khong the vuot qua nhieu hon the
NGUONG_EXT = 20.0       # W/m2 -- duoi muc nay coi nhu dem, khong tinh kt


# ================================================================ 1. lay NWP
def lay_nwp(so_ngay=3, ma_mo_hinh=None, ghi_log=print):
    """Goi Open-Meteo, tra ve (bang_theo_mo_hinh, danh_sach_bi_loai).

    Moi bang co chi muc la GIO DIA PHUONG nha may (naive), cot shortwave_radiation.
    """
    ma_mo_hinh = ma_mo_hinh or MO_HINH_MAC_DINH
    ban_goc = TT.SO_NGAY_DU_BAO
    TT.SO_NGAY_DU_BAO = max(so_ngay + 1, 2)      # xin du de con cat bo hom nay
    bang, loai = {}, []
    try:
        for ma in ma_mo_hinh:
            ten = TT.MO_HINH.get(ma, ma)
            try:
                js, _ = TT.goi_co_thu_lai(ma)
            except Exception as e:                # noqa: BLE001
                loai.append({"ma": ma, "ten": ten, "ly_do": f"khong goi duoc: {e}"})
                ghi_log(f"  {ten:24} KHONG GOI DUOC ({e})")
                continue

            h = js.get("hourly") or {}
            if not h.get("time") or "shortwave_radiation" not in h:
                loai.append({"ma": ma, "ten": ten, "ly_do": "khong co cot buc xa"})
                ghi_log(f"  {ten:24} KHONG CO COT BUC XA")
                continue

            d = pd.DataFrame(h).rename(columns={"time": "ts"})
            d["ts"] = pd.to_datetime(d["ts"], utc=True)
            d = d.set_index(d["ts"].dt.tz_convert(TT.MUI_GIO).dt.tz_localize(None))
            g = pd.to_numeric(d["shortwave_radiation"], errors="coerce")

            # Hai phep kiem BAT BUOC, theo dung thu tu nay. Kiem nguong vat ly TRUOC
            # kiem do thieu: ARPEGE va GEM tra ve du lieu 100% day du nhung dinh gap
            # gan hai lan gioi han vat ly. Neu kiem do thieu truoc thi chung "dat".
            if g.max() > TT.GIOI_HAN_BUC_XA:
                loai.append({"ma": ma, "ten": ten,
                             "ly_do": f"dinh {g.max():.0f} W/m2, vuot nguong vat ly "
                                      f"{TT.GIOI_HAN_BUC_XA:.0f}"})
                ghi_log(f"  {ten:24} LOAI -- dinh {g.max():.0f} W/m2 vuot nguong vat ly")
                continue
            thieu = g.isna().mean() * 100
            if thieu > TT.TY_LE_THIEU_TOI_DA:
                loai.append({"ma": ma, "ten": ten, "ly_do": f"thieu {thieu:.0f}%"})
                ghi_log(f"  {ten:24} LOAI -- thieu {thieu:.0f}% so o")
                continue

            bang[ma] = pd.DataFrame({"ghi": g.values}, index=d.index)
            ghi_log(f"  {ten:24} OK   {len(g):4d} gio, dinh {g.max():6.0f} W/m2")
    finally:
        TT.SO_NGAY_DU_BAO = ban_goc
    return bang, loai


# ================================================================ 2. gio -> 15 phut
def _hinh_hoc(chi_muc):
    """Goc mat troi va buc xa ngoai khi quyen tai cac moc thoi gian dia phuong."""
    k = pd.DataFrame(index=chi_muc)
    k["ghi_wm2"] = np.nan                # them_hinh_hoc can cot nay de tinh kt
    k = T.them_hinh_hoc(k)
    k = T.goi_goc_gio(k)
    return k[["sol_elev", "sol_ha", "sol_azi", "ghi_ngoai_kq"]]


def gio_sang_15p(nwp, chi_muc):
    """Noi suy buc xa gio -> 15 phut QUA CHI SO TROI QUANG, khong noi suy buc xa tho.

    Ly do: buc xa doi rat nhanh quanh binh minh va hoang hon, con chi so troi quang
    kt = buc xa / buc xa ngoai khi quyen thi doi cham vi no chi phan anh do may.
    Noi suy thang buc xa se lam tu ba duong cong hinh chuong, con noi suy kt roi
    nhan lai voi buc xa ngoai khi quyen thi giu dung dang hinh hoc cua ngay.

    Cach nay con mien nhiem voi mot mo ho phien toai: mot gia tri gio cua Open-Meteo
    la TRUNG BINH cua ca gio chu khong phai gia tri tuc thoi, nen no lech nua gio so
    voi nhan thoi gian. kt gan nhu khong doi trong nua gio, buc xa thi doi nhieu.
    """
    hh = _hinh_hoc(chi_muc)
    ext = hh["ghi_ngoai_kq"]

    # trung binh buc xa ngoai khi quyen tren dung khoang [T, T+1h) cua tung dong NWP
    ext_gio = ext.resample("1h").mean().reindex(nwp.index)
    kt_gio = np.where(ext_gio > NGUONG_EXT, nwp["ghi"] / ext_gio.replace(0, np.nan), np.nan)
    kt_gio = pd.Series(np.clip(kt_gio, 0, KT_TOI_DA), index=nwp.index)

    # gan kt vao GIUA khoang roi noi suy theo thoi gian -- dung ban chat "trung binh gio"
    giua = pd.Series(kt_gio.values, index=nwp.index + pd.Timedelta(minutes=30))
    kt = (giua.reindex(giua.index.union(chi_muc)).interpolate("time")
              .reindex(chi_muc).ffill().bfill())

    ra = hh.copy()
    ra["kt"] = kt.clip(0, KT_TOI_DA)
    ra["ghi_wm2"] = np.where(ext > NGUONG_EXT, ra["kt"] * ext, 0.0)
    return ra


# ================================================================ 3. huan luyen
def huan_luyen(d, cols, thuat_toan="gbm", ghi_log=print):
    """Huan luyen tren TOAN BO lich su san co. Khong chia fold o day.

    VI SAO KHONG DUNG LAI MO HINH CUA MUC 1:

    Goc truot khong sinh ra mot mo hinh, no sinh ra MOT MO HINH CHO MOI LUOT, va moi
    luot co tinh khong duoc nhin thang dem ra cham. Luot cuoi cung -- luot "moi" nhat
    -- la luot bi bit mat truoc thang gan day nhat. Dem bat ky mo hinh nao trong so do
    di du bao ngay mai la tu nem di du lieu moi nhat, chinh la phan gan ngay mai nhat.

    Muc 1 do CACH LAM chu khong lam ra san pham. Do xong thi khop lai tren toan bo du
    lieu -- day la quy trinh chuan cua kiem dinh cheo, khong phai loi tat.

    Thuat toan thi VAN lay theo lua chon o muc 1: neu nguoi dung do bang Random Forest
    roi bam Du bao ma may lang le chay Gradient Boosting thi con so o hai muc khong con
    lien quan gi den nhau nua.

    So vong lap van chon bang lat cat theo thoi gian (thang cuoi cua tap huan luyen)
    de khong ro ri, dung nguyen tac cua FR-05.
    """
    ok = d[cols + ["p_ac_mw"]].notna().all(axis=1) & (d["sol_elev"] > H.NGUONG_ELEV_NGAY)
    if ok.sum() < 2000:
        raise ValueError(f"Chi co {int(ok.sum())} mau ban ngay day du -- khong du de hoc.")

    dt = d.loc[ok]
    X = dt[cols].values.astype(float)
    y = dt["p_ac_mw"].values.astype(float)
    ghi_log(f"  Thuat toan          : {H.THUAT_TOAN[thuat_toan]} (lay theo lua chon o muc 1)")
    ghi_log(f"  Mau ban ngay day du : {int(ok.sum()):,}")
    ghi_log(f"  Pham vi huan luyen  : {dt.index.min():%d/%m/%Y} -> {dt.index.max():%d/%m/%Y}")

    if thuat_toan == "gbm":
        # chon_so_vong_lap chi ap dung cho cay tang cuong: no dua vao warm_start de
        # hoc tang dan roi do tren thang cuoi. Cac thuat toan khac khong co khai niem
        # "so vong lap" tuong duong nen bo qua, dung tham so mac dinh cua chung.
        n_vong = H.chon_so_vong_lap(dt, X, y)
        ghi_log(f"  So vong lap tu chon : {n_vong}")
        mo = H.tao_mo_hinh(so_vong_lap=n_vong)
    else:
        n_vong = None
        mo = H.tao_thuat_toan(thuat_toan)
    mo.fit(X, y)

    # muc cong suat nen ban dem lay tu chinh du lieu nha may (tu dung, thuong am)
    nen_dem = H.uoc_luong_nen_dem(d, d["p_ac_mw"].values.astype(float))
    ghi_log(f"  Nen cong suat ban dem: {nen_dem:.3f} MW" if nen_dem is not None
            else "  Nen cong suat ban dem: khong uoc luong duoc")
    return mo, nen_dem, int(ok.sum()), n_vong


# ---------------------------------------------------------------- luu / dung lai
THU_MUC_MO_HINH = GOC.parent / "data" / "mo_hinh"


def _van_tay(d, cols, thuat_toan):
    """Van tay cua BOI CANH huan luyen: du lieu nao, bien nao, thuat toan nao.

    Chi can mot trong ba thu do doi la mo hinh cu khong con dung nua. Van tay lay
    theo NOI DUNG chu khong theo ngay sua tep: chay lai tao_bo_du_lieu.py ma khong
    doi gi thi van tay giu nguyen, khong bat huan luyen lai vo ich.
    """
    import hashlib
    ok = d[cols + ["p_ac_mw"]].notna().all(axis=1) & (d["sol_elev"] > H.NGUONG_ELEV_NGAY)
    dt = d.loc[ok, cols + ["p_ac_mw"]]
    ruot = pd.util.hash_pandas_object(dt, index=True).values.tobytes()
    m = hashlib.sha256(ruot)
    m.update(("|".join(cols) + "|" + thuat_toan).encode())
    return m.hexdigest()


def duong_mo_hinh(thuat_toan, bo_nhiet=True):
    """Moi (thuat toan, bo bien) co tep rieng, khong ghi de len nhau.

    Neu dung chung mot ten tep thi mot lan huan luyen thu bang Random Forest se xoa
    mat mo hinh Gradient Boosting dang chay du bao, va khong ai biet cho toi luc so
    lieu doi.
    """
    return THU_MUC_MO_HINH / \
        f"nha_may_{thuat_toan}_{'khong_nhiet' if bo_nhiet else 'co_nhiet'}.joblib"


def huan_luyen_va_luu(d, cols, thuat_toan, bo_nhiet=True, ghi_log=print,
                      ten_mo_hinh=None):
    """Huan luyen tren toan bo lich su roi luu ra tep. CHI goi tu nut Huan luyen.

    Huan luyen phai la mot hanh dong co chu dinh cua nguoi dung, khong bao gio la he
    qua phu cua viec du lieu thay doi. Mot he thong tu huan luyen lai khi thay du
    lieu moi se:
      - doi mo hinh dang chay ma khong ai quyet dinh, pha cua phe duyet cua FR-06;
      - lam phep cham vo nghia, vi mo hinh bi cham khac mo hinh da du bao;
      - va hong am tham neu du lieu moi bi loi -- dung kieu Rad_2 treo o 922 W/m2.
    """
    import joblib
    mo, nen_dem, n_mau, n_vong = huan_luyen(d, cols, thuat_toan, ghi_log)
    vt = _van_tay(d, cols, thuat_toan)
    s = {
        "ten_mo_hinh": ten_mo_hinh,
        "thuat_toan": thuat_toan,
        "ten_thuat_toan": H.THUAT_TOAN[thuat_toan],
        "bien_dau_vao": cols,
        "bo_nhiet": bool(bo_nhiet),
        "so_mau": n_mau,
        "so_vong_lap": n_vong,
        "nen_dem_mw": nen_dem,
        "pham_vi": [str(d.index.min()), str(d.index.max())],
        "huan_luyen_luc": datetime.now(timezone.utc).isoformat(),
        "trang_thai": "da_ghi_nhan_CHUA_phe_duyet",     # FR-06
    }
    THU_MUC_MO_HINH.mkdir(parents=True, exist_ok=True)
    if ten_mo_hinh:
        import uuid
        duong = THU_MUC_MO_HINH / f"model_{uuid.uuid4().hex[:12]}.joblib"
    else:
        duong = duong_mo_hinh(thuat_toan, bo_nhiet)
    joblib.dump({"mo_hinh": mo, "nen_dem_mw": nen_dem, "van_tay": vt,
                 "sieu_du_lieu": s}, duong)
    duong.with_suffix(".json").write_text(
        json.dumps({**s, "van_tay": vt}, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8")
    ghi_log(f"  Da luu mo hinh: {duong.name}  (van tay {vt[:16]})")
    return {**s, "van_tay": vt, "tep": duong.name}


def nap_mo_hinh(thuat_toan, ghi_log=print):
    """Nap mo hinh da luu. KHONG bao gio tu huan luyen -- neu chua co thi bao loi.

    Bao loi to hon la lang le huan luyen: nguoi dung bam Du bao la de xem ket qua
    cua mo hinh HO da duyet, khong phai cua mot mo hinh vua sinh ra sau lung ho.
    """
    # Kiem tep TRUOC khi import joblib: neu thieu ca hai thi thong bao huu ich phai
    # thang, chu khong de ModuleNotFoundError che mat.
    duong = duong_mo_hinh(thuat_toan, bo_nhiet=True)
    if not duong.exists():
        khac = duong_mo_hinh(thuat_toan, bo_nhiet=False)
        if khac.exists():
            raise ValueError(
                f"Mo hinh '{H.THUAT_TOAN[thuat_toan]}' da luu co dung nhiet do tam pin, "
                f"ma ngay mai khong co bien nay.\n"
                f"O muc 1 dat 'Nhiet do tam pin' = 'Bo ra' roi bam Huan luyen lai.")
        co = sorted(p.name for p in THU_MUC_MO_HINH.glob("nha_may_*_khong_nhiet.joblib")) \
            if THU_MUC_MO_HINH.exists() else []
        raise ValueError(
            f"Chua co mo hinh nao cho '{H.THUAT_TOAN[thuat_toan]}'.\n"
            f"O muc 1: chon thuat toan nay, dat 'Nhiet do tam pin' = 'Bo ra', "
            f"roi bam Huan luyen.\n"
            + (f"Mo hinh dang co: {', '.join(co)}" if co else "Chua co mo hinh nao ca."))

    import joblib
    goi = joblib.load(duong)
    s = goi["sieu_du_lieu"]
    ghi_log(f"  Mo hinh         : {duong.name}")
    ghi_log(f"  Huan luyen luc  : {s['huan_luyen_luc'][:19].replace('T', ' ')} UTC")
    ghi_log(f"  Hoc tu          : {s['so_mau']:,} o ban ngay, "
            f"{s['pham_vi'][0][:10]} -> {s['pham_vi'][1][:10]}")
    ghi_log(f"  Van tay du lieu : {goi['van_tay'][:16]}")
    return goi


def nap_mo_hinh_theo_id(model_id, ghi_log=print):
    """Nap dung model trong catalog, khong suy dien tu ma thuat toan."""
    ten = Path(str(model_id)).stem
    duong = (THU_MUC_MO_HINH / f"{ten}.joblib").resolve()
    if duong.parent != THU_MUC_MO_HINH.resolve() or not duong.is_file():
        raise ValueError("Khong tim thay model da chon.")
    import joblib
    goi = joblib.load(duong)
    s = goi.get("sieu_du_lieu", {})
    ghi_log(f"  Mo hinh         : {duong.name}")
    ghi_log(f"  Huan luyen luc  : {str(s.get('huan_luyen_luc', ''))[:19].replace('T', ' ')} UTC")
    ghi_log(f"  Hoc tu          : {int(s.get('so_mau', 0)):,} o ban ngay, "
            f"{str((s.get('pham_vi') or ['', ''])[0])[:10]} -> "
            f"{str((s.get('pham_vi') or ['', ''])[1])[:10]}")
    ghi_log(f"  Van tay du lieu : {str(goi.get('van_tay', ''))[:16]}")
    return goi, duong.name


# ================================================================ 4. du bao
def du_bao_tuong_lai(duong_du_lieu, so_ngay=3, thuat_toan="gbm", gom_hom_nay=False,
                     ma_mo_hinh=None, ghi_log=print, model_id=None):
    """Du bao bang mo hinh DA LUU. Ham nay khong bao gio huan luyen."""
    d = pd.read_parquet(duong_du_lieu) if str(duong_du_lieu).endswith(".parquet") \
        else pd.read_csv(duong_du_lieu, index_col=0, parse_dates=True)
    d = d.sort_index()
    ghi_log("BUOC 1/4 -- Nap mo hinh da huan luyen")
    if model_id:
        goi, tep_model = nap_mo_hinh_theo_id(model_id, ghi_log)
        thuat_toan = goi.get("sieu_du_lieu", {}).get("thuat_toan", thuat_toan)
    else:
        # Giu tuong thich cho cac script CLI cu; giao dien web bat buoc model_id.
        if thuat_toan not in H.THUAT_TOAN:
            raise ValueError(f"Khong biet thuat toan: {thuat_toan}")
        goi = nap_mo_hinh(thuat_toan, ghi_log)
        tep_model = duong_mo_hinh(thuat_toan).name
    mo, nen_dem = goi["mo_hinh"], goi["nen_dem_mw"]
    sdl = {**goi["sieu_du_lieu"], "van_tay": goi["van_tay"],
           "tep": tep_model}
    cols = sdl["bien_dau_vao"]
    n_mau, n_vong = sdl["so_mau"], sdl.get("so_vong_lap")
    thieu = [c for c in cols if c not in d.columns]
    if thieu:
        raise ValueError(f"Bo du lieu hien tai thieu bien mo hinh can: {thieu}")
    ghi_log(f"  Bien dau vao    : {', '.join(cols)}")

    # So van tay CHI de bao, khong de kich hoat. Quyet dinh huan luyen lai la cua
    # nguoi dung o muc 1, khong phai cua may.
    # Chi so lai dung pham vi model da hoc. Du lieu moi sau moc ket thuc la binh
    # thuong, khong co nghia noi dung tap huan luyen cu da bi thay doi.
    d_kiem_tra = d
    pham_vi = sdl.get("pham_vi") or []
    if len(pham_vi) == 2:
        bat_dau, ket_thuc = pd.Timestamp(pham_vi[0]), pd.Timestamp(pham_vi[1])
        d_kiem_tra = d[(d.index >= bat_dau) & (d.index <= ket_thuc)]
    vt_nay = _van_tay(d_kiem_tra, cols, thuat_toan)
    sdl["du_lieu_da_doi"] = vt_nay != goi["van_tay"]
    if sdl["du_lieu_da_doi"]:
        ghi_log("  LUU Y: bo du lieu hien tai da khac voi luc huan luyen mo hinh nay.")
        ghi_log("  Mo hinh VAN duoc dung nguyen nhu da luu. Muon cap nhat thi bam")
        ghi_log("  Huan luyen o muc 1 -- may khong tu quyet dinh viec do.")

    ghi_log("")
    ghi_log("BUOC 2/4 -- Lay du bao thoi tiet")
    bang, loai = lay_nwp(so_ngay, ma_mo_hinh, ghi_log)
    if not bang:
        raise ValueError("Khong mo hinh thoi tiet nao dung duoc. Kiem tra ket noi mang.")

    # khung 15 phut: bat dau tu 00:00 hom nay hoac ngay mai, tuy lua chon
    hom_nay = pd.Timestamp(datetime.now().date())
    tu = hom_nay if gom_hom_nay else hom_nay + pd.Timedelta(days=1)
    den = tu + pd.Timedelta(days=so_ngay) - pd.Timedelta(minutes=BUOC_PHUT)
    chi_muc = pd.date_range(tu, den, freq=BUOC)
    if gom_hom_nay:
        ghi_log(f"  Gom ca hom nay ({hom_nay:%d/%m}) -- luu y phan gio DA TROI QUA cua")
        ghi_log("  hom nay khong con la du bao that: Open-Meteo tra ve gia tri da duoc")
        ghi_log("  hieu chinh theo quan trac, nen no chinh xac hon du bao thuc su.")

    ghi_log("")
    ghi_log("BUOC 3/4 -- Doi buc xa gio sang buoc 15 phut qua chi so troi quang")
    khung = {}
    for ma, nw in bang.items():
        nw = nw[(nw.index >= tu - pd.Timedelta(hours=2)) &
                (nw.index <= den + pd.Timedelta(hours=2))]
        if nw["ghi"].notna().sum() < 12:
            loai.append({"ma": ma, "ten": TT.MO_HINH.get(ma, ma),
                         "ly_do": "khong phu het khoang can du bao"})
            continue
        khung[ma] = gio_sang_15p(nw, chi_muc)
    if not khung:
        raise ValueError("Khong mo hinh nao phu het khoang thoi gian can du bao.")

    # Hop nhat bang TRUNG VI chu khong phai trung binh cong. Trung vi khong bi mot mo
    # hinh chay sai keo di -- dung bai hoc ARPEGE/GEM: mot nguon hong co the lech ca
    # nghin W/m2, trung binh cong se cong hong do vao ket qua chung.
    ghi_gop = pd.concat([k["ghi_wm2"].rename(ma) for ma, k in khung.items()], axis=1)
    ghi_log(f"  Hop nhat {ghi_gop.shape[1]} mo hinh bang trung vi")
    if ghi_gop.shape[1] >= 2:
        tan = float((ghi_gop.max(axis=1) - ghi_gop.min(axis=1))[ghi_gop.median(axis=1) > 50].mean())
        ghi_log(f"  Do tan giua cac mo hinh (ban ngay): {tan:.0f} W/m2 trung binh")

    hh = _hinh_hoc(chi_muc)
    nen = hh.copy()
    nen["ghi_wm2"] = ghi_gop.median(axis=1)
    # Chi so troi quang cua ban hop nhat. Phai tinh lai o day vi _hinh_hoc chi tra ve
    # goc mat troi, con kt cua tung mo hinh nam trong khung rieng cua no.
    # Tinh lai chu khong lay trung vi cua cac kt: tai mot moc thoi gian, buc xa ngoai
    # khi quyen la chung cho moi mo hinh, nen median(kt_i * ext) = ext * median(kt_i).
    # Hai cach cho ket qua y het, cach nay it duong ong hon.
    nen["kt"] = np.clip(
        np.where(nen["ghi_ngoai_kq"] > NGUONG_EXT,
                 nen["ghi_wm2"] / nen["ghi_ngoai_kq"].replace(0, np.nan), 0.0),
        0, KT_TOI_DA)

    ghi_log("")
    ghi_log("BUOC 4/4 -- Chay mo hinh")
    ket = {}
    for ten, k in [("__gop__", nen)] + [(ma, khung[ma]) for ma in khung]:
        X = k[cols].values.astype(float)
        p = np.clip(mo.predict(X), -1.0, H.CAP_AC)
        p = H.ap_nen_dem(p, k["sol_elev"].values, nen_dem)
        ket[ten] = pd.Series(p, index=chi_muc)

    ra = _dong_goi(ket, nen, ghi_gop, d, cols, loai, khung, sdl, ghi_log)
    ra.update({"so_mau_huan_luyen": n_mau, "so_vong_lap": n_vong,
               "thuat_toan": thuat_toan, "ten_thuat_toan": H.THUAT_TOAN[thuat_toan],
               "bien_dau_vao": cols, "nen_dem_mw": nen_dem,
               "mo_hinh": sdl,          # de thu Hai cham diem con truy nguoc duoc
               "pham_vi_huan_luyen": [str(d.index.min()), str(d.index.max())],
               "chup_luc": datetime.now(timezone.utc).isoformat()})
    return ra


def _dong_goi(ket, nen, ghi_gop, d, cols, loai, khung, sdl, ghi_log):
    """Bo ket qua thanh cau truc de hien len web, kem cac phep kiem tinh tinh."""
    p = ket["__gop__"]
    canh_bao = []

    # --- kiem tra tinh tinh, chay TRUOC khi dua so ra man hinh -------------
    if p.max() > H.CAP_AC + 1e-6:
        canh_bao.append(f"Dinh du bao {p.max():.2f} MW vuot cong suat dat 40 MW.")
    dem = nen["sol_elev"] < H.NGUONG_DEM
    if float(p[dem].abs().max() if dem.any() else 0) > 3.0:
        canh_bao.append("Cong suat ban dem bat thuong -- kiem tra lai quy tac nen dem.")
    if sdl.get("du_lieu_da_doi"):
        canh_bao.append(
            "Bo du lieu da thay doi ke tu khi mo hinh nay duoc huan luyen. Du bao van "
            "dung mo hinh cu -- neu muon cap nhat thi bam Huan luyen o muc 1.")
    lech = _lech_binh_minh(nen)
    if abs(lech) >= 30:
        canh_bao.append(f"Buc xa NWP lech {lech:+.0f} phut so voi hinh hoc mat troi "
                        f"-- co the sai quy uoc nhan thoi gian cua Open-Meteo.")
    ghi_log(f"  Lech tam ngay giua buc xa NWP va hinh hoc mat troi: {lech:+.0f} phut")

    # --- moc doi chieu: cung thang nay trong lich su -----------------------
    thang = pd.Timestamp(nen.index[0]).month
    ls = d[(d.index.month == thang) & d["p_ac_mw"].notna()]
    e_ls = (ls["p_ac_mw"].groupby(ls.index.date).sum() * BUOC_PHUT / 60.0)
    e_ls = e_ls[e_ls > 0]
    moc = None
    if len(e_ls) >= 5:
        moc = {"thang": int(thang), "so_ngay": int(len(e_ls)),
               "tb": round(float(e_ls.mean()), 1),
               "p10": round(float(e_ls.quantile(.1)), 1),
               "p90": round(float(e_ls.quantile(.9)), 1)}
        ghi_log(f"  Doi chieu lich su thang {thang:02d}: san luong ngay trung binh "
                f"{moc['tb']} MWh (khoang {moc['p10']}-{moc['p90']})")

    bay_gio = pd.Timestamp.now()
    ngay = []
    for ng, g in p.groupby(p.index.date):
        gg = nen.loc[g.index]
        e = float(g.clip(lower=0).sum()) * BUOC_PHUT / 60.0
        # Voi ngay hom nay, con so dung duoc trong van hanh la phan CON LAI tu bay
        # gio den het ngay, khong phai ca ngay -- phan da troi qua thi khong con
        # quyet dinh duoc gi nua.
        la_hom_nay = ng == bay_gio.date()
        con_lai = g[g.index >= bay_gio]
        e_con_lai = (round(float(con_lai.clip(lower=0).sum()) * BUOC_PHUT / 60.0, 1)
                     if la_hom_nay else None)
        muc = {ma: round(float(s.loc[g.index].clip(lower=0).sum()) * BUOC_PHUT / 60.0, 1)
               for ma, s in ket.items() if ma != "__gop__"}
        canh_ngay = None
        if moc and (e < moc["p10"] * .5 or e > moc["p90"] * 1.5):
            canh_ngay = "Ngoai xa dai lich su cua thang nay -- xem lai truoc khi dung."
        ngay.append({
            "ngay": str(ng),
            "nhan": pd.Timestamp(ng).strftime("%d/%m/%Y"),
            "thu": _thu(pd.Timestamp(ng)),
            "la_hom_nay": bool(la_hom_nay),
            "e_con_lai": e_con_lai,
            "gio_con_lai": (bay_gio.strftime("%H:%M") if la_hom_nay else None),
            "e_mwh": round(e, 1),
            "dinh_mw": round(float(g.max()), 2),
            "gio_dinh": g.idxmax().strftime("%H:%M"),
            "he_so_tai": round(e / (H.CAP_AC * 24) * 100, 1),
            "gio_nang": int((gg["ghi_wm2"] > 50).sum()) * BUOC_PHUT // 60,
            "kt_tb": _lam_tron(gg.loc[gg["ghi_ngoai_kq"] > 100, "kt"].mean(), 3),
            "e_theo_mo_hinh": muc,
            "tan_mwh": (round(max(muc.values()) - min(muc.values()), 1)
                        if len(muc) >= 2 else None),
            "canh_bao": canh_ngay,
            # phan tu thu 5: 1 = moc nay da troi qua, 0 = con o phia truoc
            "diem": [[t.strftime("%H:%M"), round(float(a), 3),
                      round(float(b)), round(float(c), 3), int(t < bay_gio)]
                     for t, a, b, c in zip(g.index, g.values,
                                           gg["ghi_wm2"].values, gg["kt"].values)],
        })

    return {"ngay": ngay, "moc_lich_su": moc, "canh_bao": canh_bao,
            "mo_hinh_dung": [{"ma": m, "ten": TT.MO_HINH.get(m, m)} for m in khung],
            "mo_hinh_loai": loai, "lech_phut": round(lech, 0)}


def _lam_tron(v, n):
    """Lam tron an toan: NaN thi tra None de JSON con hop le va giao dien hien '—'.

    float('nan') di qua json.dumps se thanh NaN -- khong phai JSON hop le, va
    JSON.parse cua trinh duyet se nem loi lam mat toan bo ket qua chu khong chi
    mot o. Bat o day re hon nhieu so voi bat o dau kia.
    """
    return None if v is None or not np.isfinite(v) else round(float(v), n)


def _thu(ts):
    return ["Thu hai", "Thu ba", "Thu tu", "Thu nam", "Thu sau",
            "Thu bay", "Chu nhat"][ts.weekday()]


def _lech_binh_minh(nen):
    """Do do lech tam giua duong buc xa NWP va duong hinh hoc mat troi, tinh bang phut.

    Neu Open-Meteo hieu nhan thoi gian khac voi gia dinh trong gio_sang_15p thi ca
    duong buc xa se truot sang trai hoac phai nua gio. Phep do nay bat duoc dieu do
    ma khong can du lieu that: so tam khoi luong cua buc xa du bao voi tam khoi luong
    cua buc xa ngoai khi quyen, tren cung mot ngay.
    """
    ra = []
    for _, g in nen.groupby(nen.index.date):
        w1, w2 = g["ghi_wm2"], g["ghi_ngoai_kq"]
        if w1.sum() < 1e-6 or w2.sum() < 1e-6:
            continue
        ph = (g.index.hour * 60 + g.index.minute).astype(float)
        ra.append(float((ph * w1).sum() / w1.sum() - (ph * w2).sum() / w2.sum()))
    return float(np.mean(ra)) if ra else 0.0


# ================================================================ CLI
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    goc = GOC.parent
    ap.add_argument("--du-lieu", default=str(goc / "data" / "dataset" / "bo_du_lieu_15min.parquet"))
    ap.add_argument("--so-ngay", type=int, default=3)
    ap.add_argument("--thuat-toan", default="gbm", choices=list(H.THUAT_TOAN))
    ap.add_argument("--model-id", default=None,
                    help="ID model trong data/mo_hinh, vi du model_03d4f2514b73")
    ap.add_argument("--gom-hom-nay", action="store_true",
                    help="tinh ca hom nay, khong chi tu ngay mai")
    ap.add_argument("--mo-hinh", nargs="*", default=None)
    ap.add_argument("--out", default=str(goc / "data" / "du_bao"))
    a = ap.parse_args()

    duong = Path(a.du_lieu)
    if not duong.exists():
        duong = duong.with_suffix(".csv")
    kq = du_bao_tuong_lai(duong, a.so_ngay, a.thuat_toan, a.gom_hom_nay,
                          a.mo_hinh, model_id=a.model_id)

    print("\n" + "=" * 74)
    print(f'{"Ngay":14}{"San luong":>12}{"Dinh":>10}{"Luc":>8}{"He so tai":>11}{"kt tb":>8}')
    print("-" * 74)
    for n in kq["ngay"]:
        print(f'{n["thu"]+" "+n["ngay"][8:]+"/"+n["ngay"][5:7]:14}'
              f'{n["e_mwh"]:>9.1f} MWh{n["dinh_mw"]:>8.2f} MW{n["gio_dinh"]:>8}'
              f'{n["he_so_tai"]:>10.1f}%{n["kt_tb"]:>8.3f}')
    for c in kq["canh_bao"]:
        print("\n  CANH BAO: " + c)

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    dau = f"du_bao_{datetime.now():%Y%m%dT%H%M%S}"
    ten = out / f"{dau}.json"
    ten.write_text(json.dumps(kq, indent=2, ensure_ascii=False, default=str),
                   encoding="utf-8")
    print(f"\n  Da ghi: {ten}")
    try:
        import xuat_excel
        print(f"  Da ghi: {xuat_excel.xuat_excel(kq, out / f'{dau}.xlsx')}")
    except ImportError as e:
        # bat quanh ca loi goi: openpyxl duoc import ben trong ham cua xuat_excel
        print(f"  (khong xuat duoc Excel: {e})")
        print(f"   Chay: {sys.executable} -m pip install openpyxl")
    print("\n  LUU Y: day la du bao dua tren buc xa NWP, khong phai buc xa do duoc.")
    print("  Con so NMAE 4,43% cua phan danh gia qua khu KHONG ap dung cho ket qua nay.")


if __name__ == "__main__":
    main()
