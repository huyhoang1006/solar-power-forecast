"""
thu_thap_du_bao.py
Bo thu du bao thoi tiet cho nha may Fujiwara, phuc vu phep thu tien cuu.

Y tuong: chot du bao TRUOC, cho thuc te xay ra, roi moi cham diem. Day la cach duy
nhat kiem duoc that. Moi thu cham tren du lieu qua khu deu co the vo tinh ro ri, vi
nguoi cham da biet ket qua.

Thu gi va vi sao:
  * Chi du bao NWP la bat buoc bat song. Cong suat va buc xa do tai nha may lay tu
    SCADA sau van con nguyen, khong mat gi.
  * Moi lan goi luu TOAN BO tam du bao kem THOI DIEM CHUP. Tam du bao cua tung dong
    = thoi diem muc tieu tru thoi diem chup. Khong co thoi diem chup thi ca tep vo
    dung, nen day la truong quan trong nhat.
  * Chi ghi them, khong bao gio de. Moi lan goi la mot lo du lieu moi.
  * Goi nhieu mo hinh song song de sau nay so cheo xem mo hinh nao hop voi Binh Dinh.

Nguon: Open-Meteo, giay phep CC BY 4.0, dung duoc cho muc dich thuong mai neu ghi
nguon. Khong can khoa API.

Cach chay:

    # chay mot lan -- dung cho Task Scheduler cua Windows
    python tools/thu_thap_du_bao.py --mot-lan

    # chay lien tuc, tu goi lai moi 3 gio -- de cua so nay mo
    python tools/thu_thap_du_bao.py --lap --moi 3

    # xem da thu duoc gi
    python tools/thu_thap_du_bao.py --tom-tat

Dat lich tren Windows (chay moi 3 gio, khong can mo cua so):

    schtasks /create /tn "ThuDuBaoFujiwara" /tr ^
      "D:\\pycharm\\PythonProject8\\.venv\\Scripts\\python.exe D:\\pycharm\\PythonProject8\\tools\\thu_thap_du_bao.py --mot-lan" ^
      /sc hourly /mo 3 /st 00:05
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------- cau hinh nha may
LAT, LON = 13.8634, 109.2708          # Bang 5.3 bao cao khao sat
MUI_GIO = "Asia/Ho_Chi_Minh"
TEN_NHA_MAY = "FUJIWARA_BD"

API = "https://api.open-meteo.com/v1/forecast"

# Bon mo hinh phu Viet Nam, goi song song de sau nay so cheo.
# Khong dung "best_match": no tu doi mo hinh nen chuoi khong nhat quan de danh gia.
MO_HINH = {
    "ecmwf_ifs025": "ECMWF IFS 0.25 do",
    "gfs_seamless": "NOAA GFS",
    "icon_seamless": "DWD ICON",
    "ecmwf_aifs025_single": "ECMWF AIFS (AI)",
}

# Cac mo hinh dang thu nghiem -- chay --kiem-tra-mo-hinh de biet cai nao that su
# tra ve buc xa tai toa do nay truoc khi dua vao MO_HINH.
#
# JMA da bi loai: goi thanh cong nhung cot buc xa toan rong. Mo hinh GSM cua Nhat
# khong cung cap bien buc xa cho vung nay. Goi thanh cong ma khong co du lieu la
# tinh huong nguy hiem hon loi mang, vi no khong bao gi ca -- day la ly do co che
# kiem tra ben duoi va canh bao trong mot_lan().
# Ket qua do tai toa do nha may ngay 07/08/2026:
#   JMA, BOM ACCESS, KMA        -- goi duoc nhung khong co cot buc xa
#   UK Met Office 10 km         -- thieu 71%, khong du dung
#   CMA GRAPES                  -- thieu 31%, khong du dung
#   Meteo-France ARPEGE         -- dinh 2327 W/m2, VUOT NGUONG VAT LY
#   GEM Canada                  -- dinh 2557 W/m2, VUOT NGUONG VAT LY
#   ECMWF IFS HRES 9 km         -- HTTP 400, ma mo hinh khong hop le o API mien phi
# Hai mo hinh cuoi cung nguy hiem nhat: chung tra ve du lieu day du, khong thieu o
# nao, nhung gia tri gap gan hai lan gioi han vat ly. Neu khong kiem nguong thi
# chung se lot vao tap huan luyen ma khong ai biet.
MO_HINH_THU = {
    "jma_seamless": "JMA Nhat Ban",
    "ukmo_global_deterministic_10km": "UK Met Office 10 km",
    "meteofrance_arpege_world": "Meteo-France ARPEGE",
    "cma_grapes_global": "CMA GRAPES Trung Quoc",
    "bom_access_global": "BOM ACCESS Uc",
    "gem_global": "GEM Canada",
    "kma_gdps": "KMA Han Quoc",
    "ecmwf_ifs_hres": "ECMWF IFS HRES 9 km",
}

BIEN_GIO = [
    "shortwave_radiation",          # GHI -- bien quan trong nhat
    "direct_radiation",
    "diffuse_radiation",
    "direct_normal_irradiance",
    "temperature_2m",
    "relative_humidity_2m",
    "cloud_cover",
    "cloud_cover_low",
    "cloud_cover_mid",
    "cloud_cover_high",
    "wind_speed_10m",
    "wind_direction_10m",
]

# Nguong vat ly cua buc xa tren mat dat. Hang so mat troi ngoai khi quyen la
# 1361 W/m2; tren mat dat khong the vuot qua no ngoai vai truong hop tang cuong
# do phan xa ria may, va muc 7.4 bao cao khao sat da chot 1350 cho cam bien tai cho.
# Mo hinh nao tra ve cao hon nhieu la sai don vi hoac dang bao gia tri tich luy theo
# buoc thoi gian thanh thong luong tuc thoi -- khong dung duoc.
GIOI_HAN_BUC_XA = 1400.0    # W/m2
TY_LE_THIEU_TOI_DA = 10.0   # %, cao hon thi coi nhu khong dung duoc

SO_NGAY_DU_BAO = 7      # du cho FC-01 den FC-04
SO_LAN_THU_LAI = 3
CHO_GIUA_HAI_LAN = 20   # giay


# ---------------------------------------------------------------- goi API
def goi_api(mo_hinh, nghieng=None, phuong_vi=None):
    """Goi mot mo hinh, tra ve (du_lieu_json, url). Nem loi neu that bai."""
    bien = list(BIEN_GIO)
    if nghieng is not None and phuong_vi is not None:
        bien.append("global_tilted_irradiance")

    tham_so = {
        "latitude": LAT,
        "longitude": LON,
        "hourly": ",".join(bien),
        "forecast_days": SO_NGAY_DU_BAO,
        "timezone": "UTC",          # luu theo gio chuan quoc te, dung quy uoc muc 3.4
        "models": mo_hinh,
    }
    if nghieng is not None and phuong_vi is not None:
        tham_so["tilt"] = nghieng
        tham_so["azimuth"] = phuong_vi

    url = API + "?" + urllib.parse.urlencode(tham_so)
    req = urllib.request.Request(url, headers={"User-Agent": "solar-forecast-fujiwara/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8")), url


def goi_co_thu_lai(mo_hinh, **kw):
    loi_cuoi = None
    for lan in range(1, SO_LAN_THU_LAI + 1):
        try:
            return goi_api(mo_hinh, **kw)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
            loi_cuoi = e
            if lan < SO_LAN_THU_LAI:
                time.sleep(CHO_GIUA_HAI_LAN)
    raise loi_cuoi


# ---------------------------------------------------------------- chuyen doi
def sang_bang(js, mo_hinh, chup_luc):
    """Doi phan hoi JSON thanh bang phang, moi dong la mot thoi diem muc tieu."""
    h = js.get("hourly")
    if not h or "time" in h and not h["time"]:
        return None

    d = pd.DataFrame(h)
    d = d.rename(columns={"time": "ts_utc"})
    d["ts_utc"] = pd.to_datetime(d["ts_utc"], utc=True)

    d.insert(0, "chup_luc_utc", chup_luc)
    d.insert(1, "mo_hinh", mo_hinh)
    d.insert(2, "nha_may", TEN_NHA_MAY)

    # Tam du bao: khoang cach tu luc chup toi thoi diem muc tieu. Day la truong
    # dung de tach du lieu theo tam khi danh gia FC-01 den FC-04.
    d.insert(3, "tam_gio", (d["ts_utc"] - chup_luc).dt.total_seconds() / 3600.0)

    # gio dia phuong nha may, de doi chieu voi SCADA cho de
    d.insert(4, "ts_local", d["ts_utc"].dt.tz_convert(MUI_GIO).dt.tz_localize(None))

    d["do_cao_mo_hinh_m"] = js.get("elevation")
    return d


# ---------------------------------------------------------------- ghi du lieu
def ghi(d, js_tho, mo_hinh, chup_luc, out_dir):
    """Ghi ca ban tho lan ban da chuyen doi. Chi ghi them, khong bao gio de."""
    tho_dir = out_dir / "tho"
    tho_dir.mkdir(parents=True, exist_ok=True)
    dau_thoi_gian = chup_luc.strftime("%Y%m%dT%H%M%SZ")

    # ban tho giu nguyen phan hoi goc -- de neu sau nay phat hien loi chuyen doi thi
    # van dung lai duoc, khong phai thu lai tu dau
    (tho_dir / f"{dau_thoi_gian}_{mo_hinh}.json").write_text(
        json.dumps(js_tho, ensure_ascii=False), encoding="utf-8")

    kho = out_dir / "du_bao_da_thu.csv"
    d.to_csv(kho, mode="a", header=not kho.exists(), index=False, encoding="utf-8")
    return kho


def mot_lan(out_dir, nghieng=None, phuong_vi=None):
    chup_luc = pd.Timestamp.now(tz="UTC").floor("s")
    print(f"[{chup_luc:%Y-%m-%d %H:%M:%S} UTC] bat dau thu")
    ok, that_bai = 0, []

    for mo_hinh, ten in MO_HINH.items():
        try:
            js, _ = goi_co_thu_lai(mo_hinh, nghieng=nghieng, phuong_vi=phuong_vi)
            d = sang_bang(js, mo_hinh, chup_luc)
            if d is None or d.empty:
                that_bai.append((mo_hinh, "phan hoi rong"))
                continue
            kho = ghi(d, js, mo_hinh, chup_luc, out_dir)
            n_ngay = d["ts_utc"].dt.date.nunique()
            bx = d["shortwave_radiation"]
            vuot = (bx > GIOI_HAN_BUC_XA).sum()
            if vuot > 0:
                print(f"  {ten:18} CANH BAO: {vuot} gia tri vuot {GIOI_HAN_BUC_XA:.0f} W/m2, "
                      f"dinh {bx.max():.0f}. Mo hinh nay sai don vi, KHONG dung de huan luyen.")
                that_bai.append((mo_hinh, f"vuot nguong vat ly, dinh {bx.max():.0f}"))
                continue
            if bx.isna().all():
                # Goi thanh cong nhung khong co buc xa. Phai bao ro, neu khong thi
                # den luc cham diem moi phat hien ra thi da mat ca dot thu.
                print(f"  {ten:18} CANH BAO: goi duoc nhung cot buc xa TOAN RONG. "
                      f"Mo hinh nay khong cung cap buc xa tai toa do nay.")
                that_bai.append((mo_hinh, "buc xa toan rong"))
                continue
            ty_le_thieu = bx.isna().mean() * 100
            them = f", thieu {ty_le_thieu:.0f}%" if ty_le_thieu > 1 else ""
            print(f"  {ten:18} {len(d):4d} dong, {n_ngay} ngay, "
                  f"tam {d.tam_gio.min():+.0f}h -> {d.tam_gio.max():+.0f}h, "
                  f"buc xa dinh {bx.max():.0f} W/m2{them}")
            ok += 1
        except Exception as e:                       # noqa: BLE001
            that_bai.append((mo_hinh, str(e)[:120]))

    for mo_hinh, ly_do in that_bai:
        print(f"  {MO_HINH.get(mo_hinh, mo_hinh):18} THAT BAI: {ly_do}")

    if ok == 0:
        print("  Khong thu duoc mo hinh nao. Kiem tra ket noi mang.")
        return False

    nk = out_dir / "nhat_ky.csv"
    pd.DataFrame([{
        "chup_luc_utc": chup_luc, "so_mo_hinh_ok": ok,
        "so_mo_hinh_loi": len(that_bai),
        "chi_tiet_loi": "; ".join(f"{m}:{l}" for m, l in that_bai),
    }]).to_csv(nk, mode="a", header=not nk.exists(), index=False, encoding="utf-8")
    print(f"  -> {ok}/{len(MO_HINH)} mo hinh, da ghi vao {kho.name}")
    return True


# ---------------------------------------------------------------- kiem tra mo hinh
def kiem_tra_mo_hinh():
    """Goi thu tung mo hinh mot lan, bao cao cai nao that su tra ve buc xa.

    Chay truoc khi chot danh sach thu. Mot mo hinh co the goi thanh cong ma cot buc
    xa van rong -- do la truong hop cua JMA tai toa do nay.
    """
    print("=" * 74)
    print("KIEM TRA MO HINH -- goi thu mot lan cho toa do nha may")
    print("=" * 74)
    print(f"Nguong vat ly: buc xa mat dat khong the vuot {GIOI_HAN_BUC_XA:.0f} W/m2")
    print(f"Nguong thieu : khong qua {TY_LE_THIEU_TOI_DA:.0f}%\n")
    print(f"{'Mo hinh':30} {'Ket luan':22} {'Dinh':>8} {'>nguong':>8} {'Thieu':>7}")
    print("-" * 80)
    dung_duoc = []
    for ma, ten in {**MO_HINH, **MO_HINH_THU}.items():
        try:
            js, _ = goi_api(ma)
            bx = pd.Series(js.get("hourly", {}).get("shortwave_radiation", []), dtype="float64")
            if len(bx) == 0 or bx.isna().all():
                print(f"{ten:30} {'khong co buc xa':22} {'—':>8} {'—':>8} {'—':>7}")
                continue

            thieu = bx.isna().mean() * 100
            vuot = (bx > GIOI_HAN_BUC_XA).mean() * 100
            if vuot > 0:
                ket = "VUOT NGUONG VAT LY"
            elif thieu > TY_LE_THIEU_TOI_DA:
                ket = "thieu qua nhieu"
            else:
                ket = "DUNG DUOC"
                dung_duoc.append(ma)
            print(f"{ten:30} {ket:22} {bx.max():>6.0f} W {vuot:>7.1f}% {thieu:>6.0f}%")
        except Exception as e:                       # noqa: BLE001
            print(f"{ten:30} {'loi: ' + str(e)[:16]:22}")
        time.sleep(1)

    print()
    if dung_duoc:
        print("Cac ma dung duoc, dan vao MO_HINH trong script neu muon doi:")
        print("  " + ", ".join(f'"{m}"' for m in dung_duoc))
    print()
    print("Luu y: mot mo hinh tra ve day du du lieu, khong thieu o nao, van co the")
    print("hoan toan sai. Cot '>nguong' bat truong hop do. Luon xet no truoc cot 'Thieu'.")


# ---------------------------------------------------------------- tom tat
def tom_tat(out_dir):
    kho = out_dir / "du_bao_da_thu.csv"
    if not kho.exists():
        print(f"Chua co du lieu tai {kho}")
        return
    d = pd.read_csv(kho, parse_dates=["chup_luc_utc", "ts_utc", "ts_local"])
    print("=" * 74)
    print("DA THU DUOC")
    print("=" * 74)
    print(f"Tep        : {kho}  ({kho.stat().st_size/1e6:.1f} MB)")
    print(f"So dong    : {len(d):,}")
    print(f"So lan chup: {d.chup_luc_utc.nunique()}")
    print(f"Chup dau   : {d.chup_luc_utc.min()}")
    print(f"Chup cuoi  : {d.chup_luc_utc.max()}")
    print(f"Muc tieu   : {d.ts_local.min()} -> {d.ts_local.max()} (gio nha may)")
    print()
    g = d.groupby("mo_hinh").agg(
        so_lan_chup=("chup_luc_utc", "nunique"),
        so_dong=("ts_utc", "size"),
        buc_xa_dinh=("shortwave_radiation", "max"),
        thieu_buc_xa=("shortwave_radiation", lambda s: s.isna().mean() * 100))
    print(g.round(1).to_string())
    print()
    # kiem tra da co du bao ngay toi chua -- dieu kien de cham FC-02
    ngay_toi = d[(d.tam_gio > 12) & (d.tam_gio <= 36)]
    print(f"So dong o tam 12-36 gio (dung cho FC-02): {len(ngay_toi):,}")
    if len(ngay_toi):
        print(f"  phu cac ngay: {sorted(ngay_toi.ts_local.dt.date.unique())}")


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    goc = Path(__file__).resolve().parent.parent
    ap.add_argument("--out", default=str(goc / "data" / "du_bao"))
    ap.add_argument("--mot-lan", action="store_true", help="thu mot lan roi thoat")
    ap.add_argument("--lap", action="store_true", help="chay lien tuc")
    ap.add_argument("--moi", type=float, default=3.0, help="so gio giua hai lan thu")
    ap.add_argument("--tom-tat", action="store_true", help="xem da thu duoc gi")
    ap.add_argument("--kiem-tra-mo-hinh", action="store_true",
                    help="goi thu moi mo hinh, xem cai nao that su co buc xa tai toa do nay")
    ap.add_argument("--nghieng", type=float, default=None,
                    help="goc nghieng dan pin (do). Chua biet -- xem cau 3 Bang 12.7")
    ap.add_argument("--phuong-vi", type=float, default=None,
                    help="goc phuong vi dan pin (0=Nam, -90=Dong, 90=Tay)")
    a = ap.parse_args()

    out_dir = Path(a.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    if a.kiem_tra_mo_hinh:
        kiem_tra_mo_hinh()
        return

    if a.tom_tat:
        tom_tat(out_dir)
        return

    if not a.mot_lan and not a.lap:
        ap.error("Chon --mot-lan, --lap, --tom-tat hoac --kiem-tra-mo-hinh")

    if a.mot_lan:
        sys.exit(0 if mot_lan(out_dir, a.nghieng, a.phuong_vi) else 1)

    print(f"Chay lien tuc, thu moi {a.moi} gio. Nhan Ctrl+C de dung.")
    print(f"Ghi vao: {out_dir.resolve()}\n")
    try:
        while True:
            mot_lan(out_dir, a.nghieng, a.phuong_vi)
            ke_tiep = datetime.now(timezone.utc) + pd.Timedelta(hours=a.moi)
            print(f"  lan sau: {ke_tiep:%H:%M:%S} UTC\n")
            time.sleep(a.moi * 3600)
    except KeyboardInterrupt:
        print("\nDa dung. Du lieu da thu van con nguyen trong " + str(out_dir))


if __name__ == "__main__":
    main()
