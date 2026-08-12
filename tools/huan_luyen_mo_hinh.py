"""
huan_luyen_mo_hinh.py
Huan luyen va danh gia mo hinh du bao cong suat, tren bo du lieu do
tao_bo_du_lieu.py sinh ra.

Hai bai toan tach bach:

  1. MO HINH NHA MAY   P = f(buc xa, hinh hoc mat troi)
     Anh xa buc xa sang cong suat. Chua du bao duoc gi cho tuong lai vi no can
     buc xa cua thoi diem can du bao. Day la cau phan san sang cho FC-02 khi co
     nguon du bao thoi tiet. Sai so cua no la TRAN kha nang cua ca he thong.

  2. MO HINH FC-01     P(t+h) = f(trang thai tai thoi diem t)
     Du bao that, dung duoc ngay hom nay vi khong can nguon thoi tiet ngoai.
     Moi dac trung deu lay tai thoi diem t hoac truoc do; rieng hinh hoc mat troi
     tai t+h duoc phep dung vi tinh truoc duoc tu toa do.

Danh gia theo goc truot dung yeu cau FR-07. Chi so gom MAE, RMSE, NMAE, WAPE,
Bias va MAPE co dieu kien, kem so mau va do phu.

Cach chay:
    pip install pandas numpy scikit-learn matplotlib joblib
    python huan_luyen_mo_hinh.py --du-lieu ../data/dataset/bo_du_lieu_15min.parquet

Dung mo hinh da luu:
    from huan_luyen_mo_hinh import du_bao
    kq = du_bao("../data/mo_hinh/nha_may.joblib", df)
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

CAP_AC = 40.0
NGUONG_SANG = 50.0      # W/m2 -- nguong tinh MAPE, tranh mau so tien ve 0
NGUONG_ELEV_NGAY = 0.0  # do -- ranh gioi ngay dem, tinh tu toa do

# Vi sao mac dinh chi danh gia ban ngay:
#   Ban dem nha may khong phat, phan cong suat do duoc la tu dung, dao dong quanh 0
#   trong dai +-0,1 MW tuc +-0,25% cong suat dinh muc (muc 7.5 bao cao khao sat).
#   Ban dem chiem khoang hai phan ba so o. Neu tinh chung, chung vao mau so va keo
#   chi so xuong khoang mot nua ma khong phan anh nang luc du bao that. Vi du do
#   duoc tren chinh du lieu nay: mo hinh nha may 2,35% khi tinh ca ngay dem, 5,03%
#   khi chi tinh ban ngay.
#   Ranh gioi lay theo goc cao mat troi chu khong theo buc xa do duoc, de chi so
#   khong phu thuoc vao mot cam bien co the hong.


# ================================================================ chi so danh gia
def tinh_chi_so(y, yh, ghi=None):
    """Bo chi so theo FR-07. MAPE chi tinh trong khoang co buc xa.

    Ly do khong tinh MAPE tren toan chuoi: ban dem cong suat dao dong quanh 0 nen
    mau so tien ve 0 va chi so bung no vo nghia (muc 7.5 bao cao khao sat).
    """
    y, yh = np.asarray(y, float), np.asarray(yh, float)
    ok = np.isfinite(y) & np.isfinite(yh)
    y, yh = y[ok], yh[ok]
    if len(y) == 0:
        return None
    e = yh - y
    kq = {
        "n": int(len(y)),
        "MAE": float(np.abs(e).mean()),
        "RMSE": float(np.sqrt((e ** 2).mean())),
        "NMAE_%": float(np.abs(e).mean() / CAP_AC * 100),
        "WAPE_%": float(np.abs(e).sum() / np.abs(y).sum() * 100) if np.abs(y).sum() > 0 else np.nan,
        "Bias": float(e.mean()),
        "R2": float(1 - (e ** 2).sum() / ((y - y.mean()) ** 2).sum()),
    }
    if ghi is not None:
        g = np.asarray(ghi, float)[ok]
        m = (g > NGUONG_SANG) & (np.abs(y) > 0.5)
        if m.sum() > 10:
            ape = np.abs(e[m] / y[m]) * 100
            kq["MAPE_%_co_nang"] = float(ape.mean())
            kq["MAE_ban_ngay"] = float(np.abs(e[m]).mean())
            kq["n_ban_ngay"] = int(m.sum())
    return kq


def bang_chi_so(ten_dong, ket_qua):
    cot = ["n", "MAE", "MAE_ban_ngay", "RMSE", "NMAE_%", "WAPE_%",
           "MAPE_%_co_nang", "Bias", "R2"]
    r = pd.DataFrame(ket_qua, index=ten_dong)
    return r[[c for c in cot if c in r.columns]]


# ================================================================ dac trung
def dac_trung_nha_may(d, bo_nhiet=True):
    """Bien dau vao cho mo hinh nha may.

    Bo bien chot lai sau khi do bang goc truot 6 fold tren chinh du lieu nha may,
    cham tren cung mot tap mau. Con so la MAE ban ngay, don vi MW:

        chi buc xa                  1,841
        + hinh hoc mat troi         1,644   tot hon 10,7%
        + nhiet do tam pin          1,610   tot hon 12,5%   <- chon bo nay
        + khong khi, do am, gio     1,748   tut lai

    Ba bien khi tuong con lai khong duoc dua vao. Chung khong chi vo dung ma con
    lam xau di 8,6% so voi bo tot nhat, du cay tang cuong co kha nang tu bo qua
    bien yeu. Phep hoan vi cho ket qua trung khop: nhiet do khong khi +0,003 MW,
    toc do gio -0,015, do am -0,080 -- hai gia tri am nghia la xao tron cot do lai
    lam mo hinh tot len, tuc cot do chi mang nhieu.
    """
    cols = ["ghi_wm2", "sol_elev", "sol_ha", "ghi_ngoai_kq", "t_panel_c"]
    if bo_nhiet:
        cols.remove("t_panel_c")
    return [c for c in cols if c in d.columns]


def dac_trung_fc01(d, h_buoc):
    """Bien dau vao cho FC-01. Moi dac trung deu lay tai t hoac truoc t.

    Rieng hinh hoc mat troi tai t+h duoc dung vi tinh truoc duoc tu toa do,
    khong phai du lieu tuong lai. Dieu nay khong vi pham FR-05.
    """
    x = pd.DataFrame(index=d.index)

    for lag in (0, 1, 2, 4, 8):
        x[f"p_lag{lag}"] = d["p_ac_mw"].shift(lag)
        x[f"ghi_lag{lag}"] = d["ghi_wm2"].shift(lag)
    for lag in (0, 1, 2, 4):
        x[f"kt_lag{lag}"] = d["kt"].shift(lag)

    x["p_tb4"] = d["p_ac_mw"].rolling(4).mean()
    x["p_do_lech4"] = d["p_ac_mw"].rolling(4).std()
    x["kt_tb8"] = d["kt"].rolling(8).mean()
    x["kt_do_lech8"] = d["kt"].rolling(8).std()      # do bien dong may
    x["p_xu_huong"] = d["p_ac_mw"] - d["p_ac_mw"].shift(4)

    # hinh hoc tai thoi diem can du bao -- biet truoc, khong phai ro ri
    x["elev_dich"] = d["sol_elev"].shift(-h_buoc)
    x["ha_dich"] = d["sol_ha"].shift(-h_buoc)
    x["ngoai_kq_dich"] = d["ghi_ngoai_kq"].shift(-h_buoc)

    # moc doi chieu quan tinh theo chi so troi quang, dua thang vao lam dac trung
    x["quan_tinh_thong_minh"] = d["kt"] * d["ghi_ngoai_kq"].shift(-h_buoc)
    return x


# ================================================================ mo hinh
SO_VONG_LAP_TOI_DA = 500
BUOC_DO = 50            # do sai so tren thang do moi 50 vong lap
BIEN_DO_CHAP_NHAN = 0.02   # chon mo hinh nho nhat nam trong 2% cua tot nhat


# Danh muc thuat toan cho phep chon. Giu chung mot giao thuc danh gia -- goc truot,
# chi ban ngay, cung bo chi so -- de con so giua cac thuat toan so sanh duoc voi nhau.
THUAT_TOAN = {
    "gbm":        "Gradient Boosting",
    "rung":       "Random Forest",
    "cay":        "Decision Tree",
    "knn":        "K-Nearest Neighbors",
    "tuyen_tinh": "Ridge Regression",
    "mlp":        "Neural Network (MLP)",
}


def tao_thuat_toan(ten, so_vong_lap=None, warm=False, seed=0):
    """Tra ve mot bo uoc luong theo ten thuat toan."""
    from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
    from sklearn.tree import DecisionTreeRegressor
    from sklearn.neighbors import KNeighborsRegressor
    from sklearn.linear_model import Ridge
    from sklearn.neural_network import MLPRegressor
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.impute import SimpleImputer

    if ten == "gbm":
        return HistGradientBoostingRegressor(
            max_iter=so_vong_lap or SO_VONG_LAP_TOI_DA, learning_rate=0.05,
            max_depth=None, max_leaf_nodes=31, min_samples_leaf=40,
            l2_regularization=1.0, early_stopping=False, warm_start=warm,
            random_state=seed)
    if ten == "rung":
        return RandomForestRegressor(n_estimators=200, min_samples_leaf=5,
                                     n_jobs=-1, random_state=seed)
    if ten == "cay":
        return DecisionTreeRegressor(min_samples_leaf=40, random_state=seed)
    if ten == "knn":
        return make_pipeline(SimpleImputer(), StandardScaler(),
                             KNeighborsRegressor(n_neighbors=40, n_jobs=-1))
    if ten == "tuyen_tinh":
        return make_pipeline(SimpleImputer(), StandardScaler(), Ridge(alpha=1.0))
    if ten == "mlp":
        return make_pipeline(SimpleImputer(), StandardScaler(),
                             MLPRegressor(hidden_layer_sizes=(64, 32), max_iter=400,
                                          early_stopping=True, random_state=seed))
    raise ValueError(f"Khong biet thuat toan: {ten}")


def tao_mo_hinh(so_vong_lap=SO_VONG_LAP_TOI_DA, warm=False, seed=0):
    """Cay tang cuong gradient theo luoc do histogram.

    KHONG dung early_stopping cua sklearn. Tham so do lay mot phan tap huan luyen
    theo kieu NGAU NHIEN de lam tap dung som, nghia la cac dong dung de dung som
    nam xen ke ve thoi gian trong tap huan luyen. Voi chuoi thoi gian day la ro ri:
    mo hinh duoc chon so vong lap dua tren nhung thoi diem no da nhin thay hang xom
    rat gan. Thay bang chon so vong lap theo lat cat thoi gian, xem chon_so_vong_lap.
    """
    from sklearn.ensemble import HistGradientBoostingRegressor
    return HistGradientBoostingRegressor(
        max_iter=so_vong_lap, learning_rate=0.05, max_depth=None, max_leaf_nodes=31,
        min_samples_leaf=40, l2_regularization=1.0,
        early_stopping=False, warm_start=warm, random_state=seed)


def chon_so_vong_lap(d_tr, cols_X, y_tr, mac_dinh=250):
    """Chon so vong lap bang mot lat cat theo THOI GIAN, khong phai ngau nhien.

    Thang cuoi cung cua tap huan luyen duoc giu lai lam tap do. Mo hinh hoc tang
    dan bang warm_start, do sai so tren thang do sau moi BUOC_DO vong, roi lay so
    vong tot nhat. Sau do goi y nay duoc dung de huan luyen lai tren TOAN BO tap
    huan luyen -- thang do khong bi bo phi.

    Cach nay ton them mot lan huan luyen nhung giu dung nguyen tac cua FR-05:
    chi duoc dung du lieu ton tai truoc thoi diem can du bao.
    """
    thang = d_tr.index.to_period("M")
    cac_thang = sorted(set(thang))
    if len(cac_thang) < 3:
        return mac_dinh

    trong, do = thang < cac_thang[-1], thang == cac_thang[-1]
    Xa, ya = cols_X[trong], y_tr[trong]
    Xb, yb = cols_X[do], y_tr[do]
    ok_a = np.isfinite(ya) & np.isfinite(Xa).all(axis=1)
    ok_b = np.isfinite(yb) & np.isfinite(Xb).all(axis=1)
    if ok_a.sum() < 2000 or ok_b.sum() < 200:
        return mac_dinh

    mo = tao_mo_hinh(so_vong_lap=BUOC_DO, warm=True)
    duong_cong = []
    for n in range(BUOC_DO, SO_VONG_LAP_TOI_DA + 1, BUOC_DO):
        mo.set_params(max_iter=n)
        mo.fit(Xa[ok_a], ya[ok_a])
        duong_cong.append((n, float(np.abs(mo.predict(Xb[ok_b]) - yb[ok_b]).mean())))

    # Lay mo hinh NHO NHAT nam trong BIEN_DO_CHAP_NHAN cua diem tot nhat, chu khong
    # lay diem tot nhat tuyet doi. Ly do: duong cong sai so rat phang o vung day nen
    # diem cuc tieu dich chuyen theo nhieu cua thang do. Quan sat truc tiep khi nang
    # tran tu 500 len 800 vong: thang do doi y chon 650 thay vi 400, va sai so tren
    # thang kiem dinh that xau di tu 0,945 len 0,994 MW. Uu tien mo hinh nho la mot
    # buoc chinh quy hoa, dong thoi hop voi yeu cau chay tren phan cung nhung.
    e_tot = min(e for _, e in duong_cong)
    nguong = e_tot * (1 + BIEN_DO_CHAP_NHAN)
    return min(n for n, e in duong_cong if e <= nguong)


NGUONG_DEM = -2.0        # do -- mat troi duoi duong chan troi


def uoc_luong_nen_dem(d_tr, y_tr, dich_buoc=0):
    """Muc cong suat nen ban dem, uoc luong tu tap huan luyen.

    dich_buoc phai khop voi tam du bao: y_tr la gia tri tai t+h nen phai doi chieu
    voi vi tri mat troi tai t+h.
    """
    if "sol_elev" not in d_tr.columns:
        return None
    elev = d_tr["sol_elev"].shift(-dich_buoc).values
    dem = (elev < NGUONG_DEM) & np.isfinite(y_tr) & np.isfinite(elev)
    return float(np.median(y_tr[dem])) if dem.sum() > 100 else None


def ap_nen_dem(pred, sol_elev, nen_dem):
    """Ban dem thi gan thang muc nen thay vi de mo hinh doan.

    Ly do: ban dem chiem khoang hai phan ba so o, cong suat gan 0 va khong co gi
    de hoc. De mo hinh tu doan thi no ton dung luong vao vung nay va lam xau phan
    ban ngay -- quan sat duoc truc tiep khi them bien vao: MAE ban ngay giam nhung
    MAE toan bo lai tang. Gan bang quy tac lay duoc ca hai dau.
    """
    if nen_dem is None or sol_elev is None:
        return pred
    pred = np.asarray(pred, float).copy()
    pred[np.asarray(sol_elev, float) < NGUONG_DEM] = nen_dem
    return pred


def goc_truot(d, X, y, so_fold=6, toi_thieu_huan_luyen=3000, ap_dem=True,
               dich_buoc=0, chi_ngay=True, ngay_khi_huan_luyen=False,
               thuat_toan="gbm", ghi_log=None, thang_cham=None):
    """Danh gia goc truot: moi fold huan luyen tren toan bo qua khu, kiem dinh 1 thang.

    Bat buoc dung cach nay chu khong chia co dinh: chuoi chi dai mot chu ky mua nen
    de danh ba thang cuoi lam tap kiem dinh thi tap huan luyen mat han mua tuong ung
    (muc 8.3 bao cao khao sat).

    Hai tham so duoi day la HAI QUYET DINH DOC LAP, khong duoc gop lam mot:

    chi_ngay             -- co loai ban dem khoi phep DANH GIA khong. Nen bat.
                            Ban dem chiem 49,8% so o nhung chi 0,50% san luong ca
                            nam, va mo hinh nao cung doan dung, nen no chi lam chi
                            so dep len chu khong do duoc nang luc du bao.

    ngay_khi_huan_luyen  -- co loai ban dem khoi tap HUAN LUYEN khong. Mac dinh
                            KHONG loai. Do la du lieu that, khong ton gi de giu, va
                            cac o luc rang dong hoang hon giup mo hinh hoc phan
                            chuyen tiep. Loai chung di la vut bo mot nua so mau de
                            doi lay mot gia thiet chua kiem chung.

    ghi_log              -- ham nhan tung dong nhat ky, de giao dien hien tien do.
                            De None thi khong ghi gi.

    thang_cham           -- danh sach thang muon dem ra cham, dang "YYYY-MM".
                            De None thi lay so_fold thang cuoi cua chuoi.
                            Thang dau chuoi khong cham duoc vi khong co gi de hoc.
    """
    def log(s=""):
        if ghi_log is not None:
            ghi_log(s)

    thang = d.index.to_period("M")
    cac_thang = sorted(set(thang))
    ket_qua, du_bao_gom = [], []

    # Voi FC-01, muc tieu la P(t+h) nen moi thu dung de PHAN LOAI ket qua phai lay
    # tai t+h chu khong phai tai t: mat troi o dau luc t+h, co nang luc t+h. Neu
    # lay tai t thi quy tac nen dem gan sai -- vi du luc 4 gio sang du bao cho 8 gio
    # sang, mat troi luc t con duoi chan troi nhung luc t+h da len cao.
    elev_dich = (d["sol_elev"].shift(-dich_buoc) if "sol_elev" in d.columns else None)
    ghi_dich = (d["ghi_wm2"].shift(-dich_buoc) if "ghi_wm2" in d.columns else None)

    # Loc ban ngay theo goc cao mat troi tai thoi diem CAN DU BAO
    if elev_dich is not None:
        ban_ngay = (elev_dich > NGUONG_ELEV_NGAY).fillna(False).values
    else:
        ban_ngay = np.ones(len(d), dtype=bool)
    tat_ca = np.ones(len(d), dtype=bool)
    loc_dg = ban_ngay if chi_ngay else tat_ca               # pham vi danh gia
    loc_hl = ban_ngay if ngay_khi_huan_luyen else tat_ca    # pham vi huan luyen

    if thang_cham:
        xin = [pd.Period(t, freq="M") for t in thang_cham]
        thang_cham = [t for t in cac_thang if t in xin]
        bo = [str(t) for t in xin if t not in cac_thang]
    else:
        thang_cham = cac_thang[-so_fold:]
        bo = []
    if not thang_cham:
        if ghi_log:
            ghi_log("Khong co thang nao hop le de cham.")
        return None, None, None

    buoc = pd.Series(d.index).diff().median()
    log("[1/3] CHUAN BI DU LIEU")
    log(f"      Doc {len(d):,} o, buoc {int(buoc.total_seconds()/60)} phut")
    log(f"      Tu {d.index.min()} den {d.index.max()} (gio nha may)")
    if chi_ngay:
        log(f"      Loc ban ngay (goc cao mat troi > {NGUONG_ELEV_NGAY:.0f} do): "
            f"con {int(ban_ngay.sum()):,} o duoc dem ra cham")
    log(f"      Huan luyen tren: {'chi ban ngay' if ngay_khi_huan_luyen else 'ca ngay lan dem'}")
    log(f"      So bien dau vao: {X.shape[1]}")
    log()

    if bo:
        log(f"      Bo qua {', '.join(bo)} -- khong co trong bo du lieu")
    log()
    log(f"[2/3] CHIA DU LIEU -- {len(thang_cham)} luot")
    for i, f in enumerate(thang_cham, 1):
        hoc = [t for t in cac_thang if t < f]
        log(f"      Luot {i}   hoc {hoc[0]} -> {hoc[-1]} ({len(hoc)} thang)   cham {f}")
    log("      Moi luot huan luyen lai tu dau. Thang dem ra cham khong bao gio nam")
    log("      trong phan da hoc -- mo hinh khong nhin thay tuong lai.")
    log()

    log("[3/3] HUAN LUYEN VA CHAM")
    for f in thang_cham:
        m_tr, m_te = (thang < f), (thang == f)
        Xtr, ytr = X[m_tr], y[m_tr]
        Xte, yte = X[m_te], y[m_te]
        ok_tr = np.isfinite(ytr) & np.isfinite(Xtr).all(axis=1) & loc_hl[m_tr]
        ok_te = np.isfinite(yte) & np.isfinite(Xte).all(axis=1) & loc_dg[m_te]
        if ok_tr.sum() < toi_thieu_huan_luyen or ok_te.sum() < 200:
            log(f"      {f}  BO QUA -- chi co {int(ok_tr.sum()):,} mau hoc "
                f"va {int(ok_te.sum()):,} mau cham")
            continue
        t0 = time.time()
        log(f"      {f}  hoc {int(ok_tr.sum()):,} mau ...")

        # Chi cay tang cuong moi can chon so vong lap. Cac thuat toan khac khong co
        # khai niem tuong duong nen bo qua buoc nay.
        if thuat_toan == "gbm":
            n_vong = chon_so_vong_lap(d[m_tr], Xtr, ytr)
            mo = tao_thuat_toan("gbm", so_vong_lap=n_vong)
        else:
            n_vong = None
            mo = tao_thuat_toan(thuat_toan)
        mo.fit(Xtr[ok_tr], ytr[ok_tr])
        pr = mo.predict(Xte[ok_te])

        if ap_dem and elev_dich is not None:
            nen = uoc_luong_nen_dem(d[m_tr], ytr, dich_buoc)
            pr = ap_nen_dem(pr, elev_dich[m_te].values[ok_te], nen)

        ghi = ghi_dich[m_te].values[ok_te] if ghi_dich is not None else None
        cs = tinh_chi_so(yte[ok_te], pr, ghi)
        cs["fold"] = str(f)
        cs["so_vong_lap"] = n_vong if n_vong is not None else 0
        # do phu tinh tren so o CO THE danh gia (tuc ban ngay neu dang loc ban ngay),
        # khong tinh tren toan bo o cua thang, de con so van co nghia la do phu du lieu
        mau_so = max(int(loc_dg[m_te].sum()), 1)
        cs["do_phu"] = float(ok_te.sum() / mau_so)
        if n_vong:
            log(f"              chon {n_vong} vong lap bang lat cat theo thoi gian")
        log(f"              cham tren {int(ok_te.sum()):,} mau cua thang {f}")
        log(f"              MAE {cs['MAE']:.3f} MW    NMAE {cs['NMAE_%']:.2f}%"
            f"    Bias {cs['Bias']:+.3f} MW    ({time.time()-t0:.1f} giay)")
        ket_qua.append(cs)
        du_bao_gom.append(pd.DataFrame(
            {"thuc_te": yte[ok_te], "du_bao": pr},
            index=d.index[m_te][ok_te]))

    if not ket_qua:
        log("      Khong luot nao du du lieu de cham.")
        return None, None, None
    r = pd.DataFrame(ket_qua)
    tb = {c: float(r[c].mean()) for c in r.columns
          if c not in ("fold", "n", "n_ban_ngay", "so_vong_lap")}
    tb["n"] = int(r["n"].sum())
    tb["so_fold"] = len(r)
    log()
    log(f"XONG. Trung binh {len(r)} luot:  NMAE {tb['NMAE_%']:.2f}%"
        f"    MAE {tb['MAE']:.3f} MW    tren {tb['n']:,} mau")
    return tb, r, pd.concat(du_bao_gom)


# ================================================================ moc doi chieu
def moc_doi_chieu(d, h_buoc, chi_muc=None):
    """Hai moc bat buoc phai vuot qua thi mo hinh moi co gia tri.

    QUAN TRONG: tham so chi_muc bat buoc phai la dung tap dong ma mo hinh duoc
    cham. Neu de moc doi chieu tinh tren ca nam con mo hinh chi tinh tren vai
    thang kiem dinh thi hai con so khong so sanh duoc voi nhau -- day la loi de
    mac nhat khi danh gia, va no lam mo hinh trong tot hoac te hon thuc te.
    """
    y = d["p_ac_mw"].shift(-h_buoc)
    he_so = (d["p_ac_mw"] / d["ghi_wm2"].replace(0, np.nan)).median()
    thong_minh = (d["kt"] * d["ghi_ngoai_kq"].shift(-h_buoc) * he_so).clip(-1, CAP_AC)

    if chi_muc is not None:
        chi_muc = d.index.intersection(chi_muc)
        y = y.loc[chi_muc]
        quan_tinh = d["p_ac_mw"].loc[chi_muc]
        thong_minh = thong_minh.loc[chi_muc]
        ghi = d["ghi_wm2"].shift(-h_buoc).loc[chi_muc]
    else:
        quan_tinh, ghi = d["p_ac_mw"], d["ghi_wm2"].shift(-h_buoc)

    return {
        "Quan tinh tho": tinh_chi_so(y, quan_tinh, ghi),
        "Quan tinh chi so troi quang": tinh_chi_so(y, thong_minh, ghi),
    }


# ================================================================ bai toan 1
def chay_mo_hinh_nha_may(d, so_fold, bo_nhiet, out_dir, chi_ngay=True, hl_chi_ngay=False):
    print("\n" + "=" * 74)
    print("BAI TOAN 1 -- MO HINH NHA MAY   P = f(buc xa, hinh hoc mat troi)")
    print("=" * 74)
    cols = dac_trung_nha_may(d, bo_nhiet)
    print(f"Bien dau vao: {', '.join(cols)}")
    print("Luu y: mo hinh nay dung buc xa DO DUOC nen ket qua la tran kha nang,")
    print("       khong phai sai so du bao thuc te.\n")

    X = d[cols].values.astype(float)
    y = d["p_ac_mw"].values.astype(float)
    tb, chi_tiet, dubao = goc_truot(d, X, y, so_fold, chi_ngay=chi_ngay,
                                    ngay_khi_huan_luyen=hl_chi_ngay)
    if tb is None:
        print("Khong du du lieu.")
        return None

    print(bang_chi_so(["Mo hinh nha may"], [tb]).to_string(float_format=lambda v: f"{v:,.3f}"))
    print("\nChi tiet tung fold:")
    cot_ct = ["fold", "n", "so_vong_lap", "MAE", "MAE_ban_ngay", "NMAE_%", "Bias", "do_phu"]
    print(chi_tiet[[c for c in cot_ct if c in chi_tiet.columns]]
          .to_string(index=False, float_format=lambda v: f"{v:,.3f}"))

    # so sanh cac bo bien, tra loi cau hoi them bien co giup gi khong
    print("\nSo sanh bo bien (cung tap mau, cung fold):")
    thu = [(["ghi_wm2"], "chi buc xa"),
           (["ghi_wm2", "sol_elev", "sol_ha", "ghi_ngoai_kq"], "+ hinh hoc mat troi"),
           (["ghi_wm2", "sol_elev", "sol_ha", "ghi_ngoai_kq", "t_panel_c"], "+ nhiet do tam pin"),
           (["ghi_wm2", "sol_elev", "sol_ha", "ghi_ngoai_kq", "t_panel_c",
             "t_air_c", "rh_pct", "wind_ms"], "+ khong khi, do am, gio")]
    co = [c for c in ["ghi_wm2", "sol_elev", "sol_ha", "ghi_ngoai_kq", "t_panel_c",
                      "t_air_c", "rh_pct", "wind_ms"] if c in d.columns]
    d_chung = d.dropna(subset=co + ["p_ac_mw"])
    print(f"  (tap mau chung {len(d_chung):,} / {len(d):,} o -- bat buoc, neu moi bo"
          f" tu loai NaN cua rieng no thi ket qua khong so sanh duoc)")

    thang_chung = sorted(set(d_chung.index.to_period("M")))[-so_fold:]
    thang_chinh = sorted(set(d.index.to_period("M")))[-so_fold:]
    if thang_chung != thang_chinh:
        print(f"  CANH BAO: tap mau chung khong con thang {[str(t) for t in thang_chinh if t not in thang_chung]}")
        print(f"            nen khoi nay cham tren {[str(t) for t in thang_chung]},")
        print(f"            KHONG so sanh truc tiep duoc voi bang chi so o tren.")
        print(f"            Nguyen nhan thuong gap: mot cam bien da tat han (xem canh bao khi tao bo du lieu).")
    else:
        print(f"  (fold kiem dinh: {[str(t) for t in thang_chung]})")

    # kiem tra sau hon: cac thang van con nhung phan BAN NGAY co the da bien mat.
    # Quy tac ma 8 chi bien 0 thanh thieu vao ban ngay, nen khi mot cam bien chet
    # thi cac dong ban dem cua no van song sot va tap mau trong co ve van day.
    m_chung = d_chung.index.to_period("M").isin(thang_chung)
    m_goc = d.index.to_period("M").isin(thang_chung)
    ngay_chung = int((d_chung.loc[m_chung, "ghi_wm2"] > 50).sum())
    ngay_goc = int((d.loc[m_goc, "ghi_wm2"] > 50).sum())
    if ngay_goc > 0 and ngay_chung < 0.3 * ngay_goc:
        print(f"  CANH BAO NANG: tap mau chung chi con {ngay_chung:,}/{ngay_goc:,} o BAN NGAY")
        print(f"                 trong cac thang kiem dinh. Khoi so sanh nay chu yeu")
        print(f"                 dang cham tren ban dem, KHONG dung de ket luan.")

    for cs, nhan in thu:
        cs = [c for c in cs if c in d_chung.columns]
        if len(cs) < len(set(cs)):
            continue
        r, _, _ = goc_truot(d_chung, d_chung[cs].values.astype(float),
                            d_chung["p_ac_mw"].values.astype(float), so_fold,
                            chi_ngay=chi_ngay)
        if r:
            print(f"    {nhan:26} MAE={r['MAE']:.3f}  MAE ngay={r.get('MAE_ban_ngay', np.nan):.3f}"
                  f"  NMAE={r['NMAE_%']:.2f}%  (n={r['n']:,})")

    print("\n  Huan luyen tren ban dem co giup gi khong (ca hai cung cham tren ban ngay):")
    for hl_ngay, nhan in [(False, "huan luyen ca ngay lan dem"),
                          (True, "huan luyen chi ban ngay")]:
        r, _, _ = goc_truot(d, X, y, so_fold, chi_ngay=chi_ngay,
                            ngay_khi_huan_luyen=hl_ngay)
        if r:
            print(f"    {nhan:28} MAE={r['MAE']:.3f}  NMAE={r['NMAE_%']:.2f}%"
                  f"  (n={r['n']:,})")

    luu_mo_hinh(d, cols, "p_ac_mw", out_dir / "nha_may.joblib",
                {"bai_toan": "mo_hinh_nha_may", "tam_du_bao_buoc": 0,
                 "chi_so_goc_truot": tb})
    return {"chi_so": tb, "du_bao": dubao, "bien": cols}


# ================================================================ bai toan 2
def chay_fc01(d, so_fold, buoc_phut, out_dir, chi_ngay=True, hl_chi_ngay=False):
    print("\n" + "=" * 74)
    print("BAI TOAN 2 -- FC-01, du bao 4 gio toi")
    print("=" * 74)
    print("Moi dac trung lay tai thoi diem t hoac truoc do. Hinh hoc mat troi tai t+h")
    print("duoc dung vi tinh truoc tu toa do, khong phai du lieu tuong lai.\n")

    tam_phut = [15, 30, 60, 120, 240]
    dong, ten, tot_nhat = [], [], None
    for tp in tam_phut:
        h = int(round(tp / buoc_phut))
        if h < 1:
            continue
        X = dac_trung_fc01(d, h)
        y = d["p_ac_mw"].shift(-h)
        # Khong ap quy tac nen dem cho FC-01. Da do: no lam xau di o tam ngan
        # (15 phut: 1,98% -> 2,06%) va khong thay doi gi o tam dai. Voi FC-01 mo hinh
        # da co dac trung tre nen tu doan ban dem tot hon la bi gan cung mot muc.
        tb, _, dubao = goc_truot(d, X.values.astype(float), y.values.astype(float),
                                 so_fold, ap_dem=False, dich_buoc=h, chi_ngay=chi_ngay,
                                 ngay_khi_huan_luyen=hl_chi_ngay)
        if tb is None:
            continue
        # moc doi chieu cham tren DUNG tap dong ma mo hinh duoc cham
        mdc = moc_doi_chieu(d, h, chi_muc=dubao.index)
        for nhan, cs in mdc.items():
            if cs:
                dong.append(cs); ten.append(f"{tp:>4} phut | {nhan}")
        dong.append(tb); ten.append(f"{tp:>4} phut | MO HINH")
        if tp == 240:
            tot_nhat = (h, X.columns.tolist(), dubao)

    if not dong:
        print("Khong du du lieu.")
        return None
    b = bang_chi_so(ten, dong)
    print(b.to_string(float_format=lambda v: f"{v:,.3f}"))

    print("\nDoc bang tren: dong MO HINH phai tot hon ca hai dong quan tinh cung tam")
    print("du bao thi mo hinh moi co gia tri. Quan tinh chi so troi quang la moc")
    print("doi chieu that su, khong phai quan tinh tho.")

    if tot_nhat:
        h, cols, dubao = tot_nhat
        X = dac_trung_fc01(d, h)
        dd = d.copy()
        for c in X.columns:
            dd[c] = X[c]
        dd["muc_tieu"] = d["p_ac_mw"].shift(-h)
        luu_mo_hinh(dd.dropna(subset=cols + ["muc_tieu"]), cols, "muc_tieu",
                    out_dir / "fc01_240phut.joblib",
                    {"bai_toan": "fc01", "tam_du_bao_phut": 240, "tam_du_bao_buoc": h})
        return {"bang": b, "du_bao": dubao}
    return {"bang": b, "du_bao": None}


# ================================================================ luu va dung lai
def luu_mo_hinh(d, cols, cot_muc_tieu, duong_dan, sieu_du_lieu):
    """Huan luyen lan cuoi tren TOAN BO du lieu roi luu kem sieu du lieu.

    FR-06: moi lan huan luyen phai luu cau hinh, du lieu, tham so va ket qua.
    Mo hinh luu ra chi duoc ghi nhan, khong tu dong dua vao van hanh -- viec phe
    duyet thuoc ve Administrator dua tren ket qua FR-07.
    """
    import joblib
    ok = d[cols + [cot_muc_tieu]].notna().all(axis=1)
    if ok.sum() < 1000:
        print(f"  (bo qua luu {duong_dan.name}: chi co {ok.sum()} mau day du)")
        return
    X = d.loc[ok, cols].values.astype(float)
    y = d.loc[ok, cot_muc_tieu].values.astype(float)
    n_vong = chon_so_vong_lap(d.loc[ok], X, y)
    mo = tao_mo_hinh(so_vong_lap=n_vong)
    mo.fit(X, y)
    nen_dem = uoc_luong_nen_dem(d.loc[ok], y)
    sieu_du_lieu = {**sieu_du_lieu, "so_vong_lap": int(n_vong),
                    "nen_dem_mw": nen_dem, "nguong_dem_do": NGUONG_DEM}

    duong_dan.parent.mkdir(parents=True, exist_ok=True)
    goi = {
        "mo_hinh": mo,
        "bien_dau_vao": cols,
        "cot_muc_tieu": cot_muc_tieu,
        "capacity_ac_mw": CAP_AC,
        "nen_dem_mw": nen_dem,
        "nguong_dem_do": NGUONG_DEM,
        "sieu_du_lieu": {
            **sieu_du_lieu,
            "huan_luyen_luc": datetime.now(timezone.utc).isoformat(),
            "so_mau_huan_luyen": int(ok.sum()),
            "pham_vi_du_lieu": [str(d.index.min()), str(d.index.max())],
            "trang_thai": "da_ghi_nhan_CHUA_phe_duyet",
        },
    }
    joblib.dump(goi, duong_dan)
    duong_dan.with_suffix(".json").write_text(
        json.dumps(goi["sieu_du_lieu"], indent=2, ensure_ascii=False, default=str),
        encoding="utf-8")
    print(f"\n  Da luu mo hinh: {duong_dan.name}  ({ok.sum():,} mau)")


def du_bao(duong_mo_hinh, df, buoc_phut=15):
    """Ham du bao san dung. Nhan dataframe da co du bien dau vao, tra ve
    cong suat va san luong cua tung chu ky -- dung yeu cau cua FC-01..FC-04.

    Vi du:
        from huan_luyen_mo_hinh import du_bao
        kq = du_bao("../data/mo_hinh/nha_may.joblib", df_moi)
        kq[["p_du_bao_mw", "e_du_bao_mwh"]]
    """
    import joblib
    goi = joblib.load(duong_mo_hinh)
    cols = goi["bien_dau_vao"]
    thieu = [c for c in cols if c not in df.columns]
    if thieu:
        raise ValueError(f"Thieu bien dau vao: {thieu}\nCan day du: {cols}")

    X = df[cols].values.astype(float)
    ok = np.isfinite(X).all(axis=1)
    p = np.full(len(df), np.nan)
    if ok.any():
        p[ok] = goi["mo_hinh"].predict(X[ok])
    p = np.clip(p, -1.0, goi["capacity_ac_mw"])

    # ban dem gan thang muc nen thay vi de mo hinh doan
    if goi.get("nen_dem_mw") is not None and "sol_elev" in df.columns:
        p = ap_nen_dem(p, df["sol_elev"].values, goi["nen_dem_mw"])
        ok = ok | (df["sol_elev"].values < goi.get("nguong_dem_do", NGUONG_DEM))

    out = pd.DataFrame(index=df.index)
    out["p_du_bao_mw"] = p
    # san luong cua chu ky = cong suat trung binh nhan do dai chu ky
    out["e_du_bao_mwh"] = out["p_du_bao_mw"] * (buoc_phut / 60.0)
    out["hop_le"] = ok
    return out


# ================================================================ bieu do
def ve_bieu_do(kq_nha_may, kq_fc01, out_dir):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n(Bo qua bieu do: can matplotlib)")
        return
    out_dir.mkdir(parents=True, exist_ok=True)

    for ten, kq in [("nha_may", kq_nha_may), ("fc01_240phut", kq_fc01)]:
        if not kq or kq.get("du_bao") is None or len(kq["du_bao"]) == 0:
            continue
        dbo = kq["du_bao"].sort_index()
        fig, ax = plt.subplots(2, 1, figsize=(12, 8))

        # mot tuan tieu bieu
        giua = dbo.index[len(dbo) // 2]
        lat = dbo.loc[giua:giua + pd.Timedelta("7D")]
        ax[0].plot(lat.index, lat["thuc_te"], lw=1.1, label="Thuc te")
        ax[0].plot(lat.index, lat["du_bao"], lw=1.1, alpha=0.85, label="Du bao")
        ax[0].set_title(f"{ten} -- du bao so voi thuc te, mot tuan tieu bieu")
        ax[0].set_ylabel("Cong suat (MW)")
        ax[0].legend(); ax[0].grid(alpha=0.3)

        ax[1].scatter(dbo["thuc_te"], dbo["du_bao"], s=2, alpha=0.15)
        lim = [min(dbo.min()), max(dbo.max())]
        ax[1].plot(lim, lim, "r--", lw=1)
        ax[1].set_xlabel("Thuc te (MW)"); ax[1].set_ylabel("Du bao (MW)")
        ax[1].set_title("Phan tan du bao so voi thuc te")
        ax[1].grid(alpha=0.3)

        fig.tight_layout()
        fig.savefig(out_dir / f"{ten}_danh_gia.png", dpi=110)
        plt.close(fig)
        print(f"  Da ve: {ten}_danh_gia.png")


# ================================================================ main
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    goc = Path(__file__).resolve().parent.parent      # thu muc goc du an
    ap.add_argument("--du-lieu", default=str(goc / "data" / "dataset" / "bo_du_lieu_15min.parquet"))
    ap.add_argument("--out", default=str(goc / "data" / "mo_hinh"))
    ap.add_argument("--so-fold", type=int, default=6)
    nhom_nhiet = ap.add_mutually_exclusive_group()
    nhom_nhiet.add_argument("--bo-nhiet", dest="bo_nhiet", action="store_true",
                            help="bo nhiet do tam pin khoi mo hinh nha may (mac dinh)")
    nhom_nhiet.add_argument("--dung-nhiet", dest="bo_nhiet", action="store_false",
                            help="dung nhiet do tam pin lam bien dau vao (chi de thu nghiem)")
    ap.set_defaults(bo_nhiet=True)
    ap.add_argument("--bai-toan", default="ca_hai",
                    choices=["ca_hai", "nha_may", "fc01"])
    ap.add_argument("--ca-ngay-dem", action="store_true",
                    help="DANH GIA ca ban dem (mac dinh chi ban ngay)")
    ap.add_argument("--huan-luyen-chi-ngay", action="store_true",
                    help="loai ban dem khoi tap HUAN LUYEN (mac dinh giu lai)")
    a = ap.parse_args()

    try:
        import sklearn  # noqa: F401
    except ImportError:
        sys.exit("Thieu scikit-learn. Chay:  pip install scikit-learn joblib matplotlib")

    p = Path(a.du_lieu)
    if not p.exists():
        sys.exit(f"Khong thay {p}. Chay truoc:\n"
                 f"    python tao_bo_du_lieu.py --csv ../data/csv --out ../data/dataset")
    d = pd.read_parquet(p) if p.suffix == ".parquet" else pd.read_csv(p, index_col=0, parse_dates=True)
    d = d.sort_index()

    buoc_phut = int(round(pd.Series(d.index).diff().median().total_seconds() / 60))
    print("=" * 74)
    print("HUAN LUYEN VA DANH GIA MO HINH")
    print("=" * 74)
    print(f"Bo du lieu : {p.name}")
    print(f"So o       : {len(d):,}  buoc {buoc_phut} phut")
    print(f"Pham vi    : {d.index.min()} -> {d.index.max()}")
    print(f"Do phu bien muc tieu: {d['p_ac_mw'].notna().mean()*100:.2f}%")
    print(f"Danh gia   : goc truot {a.so_fold} fold (FR-07)")
    if a.ca_ngay_dem:
        print("Pham vi    : CA NGAY LAN DEM -- chi so se dep hon thuc te vi ban dem")
        print("             chiem hai phan ba so o va mo hinh nao cung doan dung")
    else:
        print("Pham vi    : CHI BAN NGAY (goc cao mat troi > 0 do)")
        print("             Ban dem nha may khong phat, phan do duoc la tu dung nen")
        print("             khong dua vao chi so. Dung --ca-ngay-dem de tinh ca hai.")
    print(f"Huan luyen : {'chi ban ngay' if a.huan_luyen_chi_ngay else 'giu ca ban dem'}"
          f" -- day la quyet dinh KHAC voi pham vi danh gia")

    out_dir = Path(a.out)
    kq1 = kq2 = None
    if a.bai_toan in ("ca_hai", "nha_may"):
        kq1 = chay_mo_hinh_nha_may(d, a.so_fold, a.bo_nhiet, out_dir,
                                   not a.ca_ngay_dem, a.huan_luyen_chi_ngay)
    if a.bai_toan in ("ca_hai", "fc01"):
        kq2 = chay_fc01(d, a.so_fold, buoc_phut, out_dir,
                        not a.ca_ngay_dem, a.huan_luyen_chi_ngay)

    print("\n" + "=" * 74)
    print("BIEU DO")
    print("=" * 74)
    ve_bieu_do(kq1, kq2, out_dir)

    tong_hop = {"tao_luc": datetime.now(timezone.utc).isoformat(),
                "bo_du_lieu": str(p.resolve()), "so_fold": a.so_fold}
    if kq1:
        tong_hop["mo_hinh_nha_may"] = kq1["chi_so"]
    if kq2 and "bang" in kq2:
        tong_hop["fc01"] = json.loads(kq2["bang"].to_json(orient="index"))
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "bao_cao_danh_gia.json").write_text(
        json.dumps(tong_hop, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    print("\n" + "=" * 74)
    print(f"Da ghi ket qua vao {out_dir.resolve()}")
    print("=" * 74)
    print("""
Luu y khi doc ket qua:

  * Mo hinh nha may dung buc xa DO DUOC. Con so cua no la tran kha nang cua ca he
    thong, khong phai sai so du bao. Sai so du bao that cua FC-02 se lon hon, va
    phan chenh lech do chat luong nguon du bao thoi tiet quyet dinh.

  * FC-01 phai vuot duoc dong "Quan tinh chi so troi quang" cung tam du bao. Neu
    khong vuot thi mo hinh chua co gia tri gi so voi mot cong thuc ba dong.

  * Mo hinh luu ra dang trang thai da_ghi_nhan_CHUA_phe_duyet, dung yeu cau FR-06:
    huan luyen thanh cong khong dong nghia voi duoc dua vao van hanh.
""")


if __name__ == "__main__":
    main()
