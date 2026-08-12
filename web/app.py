"""
app.py
Giao dien web don gian de chon thuat toan va huan luyen mo hinh du bao cong suat.

Chay:
    pip install flask
    python web/app.py

Tren may nay: http://127.0.0.1:6001
Trong cung mang LAN: http://<IP-may-chay>:6001

Nguyen tac thiet ke: web nay KHONG tu cai dat lai quy trinh danh gia. No goi thang
sang tools/huan_luyen_mo_hinh.py -- cung goc truot, cung bo loc ban ngay, cung bo
chi so. Neu web va dong lenh danh gia khac nhau thi hai con so se khong so sanh
duoc, va som muon cung co nguoi tin nham mot trong hai.
"""

import json
import queue
import sys
import threading
import time
import traceback
import uuid
from pathlib import Path

import numpy as np
import pandas as pd
from flask import Flask, Response, render_template, request, send_file

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC / "tools"))

import huan_luyen_mo_hinh as H          # noqa: E402
import du_bao_tuong_lai as DB           # noqa: E402

app = Flask(__name__)

THU_MUC_DU_LIEU = GOC / "data" / "dataset"

# Mo ta ngan gon tung thuat toan, de nguoi dung biet minh dang chon gi
GIAI_THICH = {
    "gbm": "Cây tăng cường gradient. Mạnh nhất với dữ liệu dạng bảng, tự bỏ qua biến "
           "yếu nên không bị nhiễu kéo đi, và chạy nhanh. Đây là lựa chọn mặc định.",
    "rung": "Rừng ngẫu nhiên. Ổn định, gần như không phải chỉnh tham số, nhưng trên "
            "bài toán này thường kém cây tăng cường một chút và nặng hơn khi chạy.",
    "cay": "Một cây quyết định duy nhất. Rất dễ đọc và giải thích được từng nhánh, "
           "đổi lại độ chính xác thấp hơn hẳn. Dùng để đối chiếu và để trình bày.",
    "knn": "K láng giềng gần nhất. Bị phạt nặng khi thêm biến yếu do lời nguyền số "
           "chiều — chọn nó để thấy rõ hiệu ứng đó bằng số liệu.",
    "tuyen_tinh": "Hồi quy tuyến tính có chính quy hoá. Đây là mốc đối chiếu tối "
                  "thiểu: một thuật toán phức tạp mà không hơn được nó thì không "
                  "đáng đưa vào vận hành.",
    "mlp": "Mạng neural nhiều lớp. Với dữ liệu dạng bảng và chỉ vài trăm mẫu thực sự "
           "độc lập, nó thường không hơn được cây tăng cường — chạy thử để tự kiểm chứng.",
}


# ---------------------------------------------------------------- du lieu
def liet_ke_bo_du_lieu():
    """Cac tep bo du lieu co the dung de huan luyen."""
    if not THU_MUC_DU_LIEU.exists():
        return []
    ra = []
    for p in sorted(THU_MUC_DU_LIEU.glob("bo_du_lieu_*.parquet")) + \
             sorted(THU_MUC_DU_LIEU.glob("bo_du_lieu_*.csv")):
        if p.suffix == ".csv" and p.with_suffix(".parquet").exists():
            continue                     # da co ban parquet, khong liet ke trung
        ra.append({"ten": p.name, "duong_dan": str(p),
                   "kich_thuoc_mb": round(p.stat().st_size / 1e6, 1)})
    return ra


def nap(duong_dan):
    p = Path(duong_dan)
    d = (pd.read_parquet(p) if p.suffix == ".parquet"
         else pd.read_csv(p, index_col=0, parse_dates=True))
    return d.sort_index()


def tom_tat_du_lieu(d):
    """Thong tin de hien thi trong phan danh sach du lieu huan luyen."""
    ngay = d["sol_elev"] > 0 if "sol_elev" in d.columns else pd.Series(True, index=d.index)
    bien = []
    for c in d.columns:
        if c.startswith("qc_") or c in ("n_mau", "do_phu"):
            continue
        s = d[c]
        bien.append({
            "ten": c,
            "do_phu": round(s.notna().mean() * 100, 1),
            "nho_nhat": None if s.isna().all() else round(float(s.min()), 2),
            "lon_nhat": None if s.isna().all() else round(float(s.max()), 2),
            "trung_binh": None if s.isna().all() else round(float(s.mean()), 2),
            "la_dau_vao": c in H.dac_trung_nha_may(d),
            "la_muc_tieu": c == "p_ac_mw",
        })
    # Danh sach thang, kem so o ban ngay va so thang co truoc de biet thang nao
    # du dieu kien dem ra cham -- thang dau chuoi khong cham duoc vi chua co gi de hoc.
    thang = sorted(set(d.index.to_period("M")))
    ds_thang = []
    for i, t in enumerate(thang):
        m = d.index.to_period("M") == t
        ds_thang.append({
            "ma": str(t),
            "nhan": f"{t.month:02d}/{t.year}",
            "so_o_ngay": int((ngay & m).sum()),
            "cham_duoc": i >= 3,          # can it nhat 3 thang truoc do de hoc
        })

    return {
        "so_o": len(d),
        "so_o_ban_ngay": int(ngay.sum()),
        "thang": ds_thang,
        "lich": lich_ngay_co_du_lieu(d),
        "tu": str(d.index.min()),
        "den": str(d.index.max()),
        "so_thang": d.index.to_period("M").nunique(),
        "bien": bien,
    }


NGUONG_O_NGAY = 20      # o ban ngay toi thieu de mot ngay dang duoc dem ra doi chieu


def lich_ngay_co_du_lieu(d):
    """Cay nam -> thang -> ngay, chi giu nhung ngay THUC SU co du lieu ban ngay.

    Loc bang NGUONG_O_NGAY chu khong liet ke moi ngay trong pham vi: mot ngay chi
    con vai o do mat ket noi SCADA se ve ra duong gan nhu phang, va nguoi xem se
    tuong nha may hong chu khong nghi la du lieu thieu.
    """
    if "sol_elev" not in d.columns or "p_ac_mw" not in d.columns:
        return {}
    n = d[(d["sol_elev"] > 0) & d["p_ac_mw"].notna()]
    lich = {}
    for ng, g in n.groupby(n.index.date):
        if len(g) < NGUONG_O_NGAY:
            continue
        lich.setdefault(str(ng.year), {}) \
            .setdefault(f"{ng.month:02d}", []).append(f"{ng.day:02d}")
    return lich


# ---------------------------------------------------------------- huan luyen
def chay_huan_luyen(duong_dan, thuat_toan, so_fold, bo_nhiet=True, ghi_log=None,
                    thang_cham=None):
    d = nap(duong_dan)
    cols = H.dac_trung_nha_may(d, bo_nhiet)
    thieu = [c for c in cols if c not in d.columns]
    if thieu:
        raise ValueError(f"Bo du lieu thieu bien: {thieu}")

    X = d[cols].values.astype(float)
    y = d["p_ac_mw"].values.astype(float)

    nhat_ky = []

    def log(s=""):
        nhat_ky.append(s)
        if ghi_log is not None:
            ghi_log(s)

    log(f"Bo du lieu  : {Path(duong_dan).name}")
    log(f"Thuat toan  : {H.THUAT_TOAN[thuat_toan]}")
    log(f"Bien dau vao: {', '.join(cols)}")
    log()

    bat_dau = time.time()
    tb, chi_tiet, dubao = H.goc_truot(d, X, y, so_fold=so_fold, chi_ngay=True,
                                      thuat_toan=thuat_toan, ghi_log=log,
                                      thang_cham=thang_cham)
    giay = time.time() - bat_dau
    if tb is None:
        raise ValueError("Khong du du lieu de danh gia. Thu giam so thang dem ra cham.")

    fold = chi_tiet.to_dict("records") if chi_tiet is not None else []
    for f in fold:
        for k, v in f.items():
            if isinstance(v, float):
                f[k] = round(v, 3)

    # Cham xong moi khop lai tren TOAN BO du lieu va luu ra tep. Thu tu nay co chu y:
    # nguoi dung nhin thay con so goc truot TRUOC khi mo hinh duoc ghi nhan, nen viec
    # bam nut la mot quyet dinh co can cu chu khong phai bam mu.
    #
    # Day la CHO DUY NHAT trong ca he thong sinh ra mo hinh. Muc du bao chi nap tep
    # nay ra dung, khong bao gio tu huan luyen.
    mo_hinh = None
    try:
        log()
        log("Khop lai tren toan bo du lieu va luu mo hinh")
        mo_hinh = DB.huan_luyen_va_luu(d, cols, thuat_toan, bo_nhiet, ghi_log=log)
    except Exception as e:                           # noqa: BLE001
        log(f"  Khong luu duoc mo hinh: {e}")

    return {
        "thuat_toan": thuat_toan,
        "ten_thuat_toan": H.THUAT_TOAN[thuat_toan],
        "bien_dau_vao": cols,
        "so_fold": tb.get("so_fold"),
        "giay": round(giay, 1),
        "chi_so": {k: (round(v, 4) if isinstance(v, float) else v)
                   for k, v in tb.items()},
        "fold": fold,
        "mo_hinh_da_luu": mo_hinh,
        "theo_ngay": gom_theo_ngay(dubao, d),
        "nhat_ky": "\n".join(nhat_ky),
    }


def gom_theo_ngay(dubao, d):
    """Gom du bao va thuc te theo tung ngay, de nguoi dung xem chi tiet mot ngay.

    Day la cong cu XEM chu khong phai cong cu CHAM. Mot ngay chi co khoang 50 o ban
    ngay nen chi so tren mot ngay dao dong rat manh -- do tren thang 5/2026 thi ngay
    tot nhat 2,43% con ngay te nhat 7,46%, chenh ba lan. Vi vay giao dien luon hien
    chi so ca thang ben canh, de khong ai nham mot ngay dep thanh ket qua cua mo hinh.
    """
    if dubao is None or len(dubao) == 0:
        return {}
    r = dubao.sort_index().copy()
    r["lech"] = r["du_bao"] - r["thuc_te"]
    if "ghi_wm2" in d.columns:
        r["buc_xa"] = d["ghi_wm2"].reindex(r.index)

    ra = {}
    for ngay, g in r.groupby(r.index.date):
        mae = float(g["lech"].abs().mean())
        ra[str(ngay)] = {
            "nmae": round(mae / H.CAP_AC * 100, 2),
            "mae": round(mae, 3),
            "so_o": int(len(g)),
            "e_that": round(float(g["thuc_te"].sum()) * 0.25, 2),   # o 15 phut -> MWh
            "e_du_bao": round(float(g["du_bao"].sum()) * 0.25, 2),
            "dinh_that": round(float(g["thuc_te"].max()), 2),
            "dinh_du_bao": round(float(g["du_bao"].max()), 2),
            "gio_dinh_that": g["thuc_te"].idxmax().strftime("%H:%M"),
            "gio_dinh_du_bao": g["du_bao"].idxmax().strftime("%H:%M"),
            "diem": [[t.strftime("%H:%M"), round(float(a), 3), round(float(b), 3),
                      (None if "buc_xa" not in g or pd.isna(c) else round(float(c)))]
                     for t, a, b, c in zip(
                         g.index, g["thuc_te"], g["du_bao"],
                         g["buc_xa"] if "buc_xa" in g else [np.nan] * len(g))],
        }
    return ra


# ---------------------------------------------------------------- chay nen
# Moi lan bam Huan luyen tao mot cong viec chay o luong rieng. Cac dong nhat ky
# duoc day vao hang doi, va trinh duyet doc hang doi do qua Server-Sent Events nen
# thay tien do ngay lap tuc thay vi cho toan bo qua trinh ket thuc.
CONG_VIEC = {}
KHOA = threading.Lock()


def don_cong_viec_cu(gio=2):
    """Xoa cong viec da xong qua lau, tranh phinh bo nho."""
    han = time.time() - gio * 3600
    with KHOA:
        for ma in [m for m, c in CONG_VIEC.items() if c["xong"] and c["luc"] < han]:
            CONG_VIEC.pop(ma, None)


@app.post("/bat-dau")
def bat_dau():
    don_cong_viec_cu()
    ct = request.get_json(force=True)
    ma = uuid.uuid4().hex[:12]
    cv = {"hang": queue.Queue(), "ket_qua": None, "loi": None,
          "xong": False, "luc": time.time()}
    with KHOA:
        CONG_VIEC[ma] = cv

    def chay():
        try:
            cv["ket_qua"] = chay_huan_luyen(
                ct["duong_dan"], ct["thuat_toan"], int(ct["so_fold"]),
                bool(ct.get("bo_nhiet", True)), ghi_log=cv["hang"].put,
                thang_cham=ct.get("thang_cham") or None)
        except Exception as e:                       # noqa: BLE001
            cv["loi"] = f"{e}\n\n{traceback.format_exc(limit=3)}"
        finally:
            cv["xong"] = True
            cv["hang"].put(None)          # dau hieu ket thuc

    threading.Thread(target=chay, daemon=True).start()
    return {"ma": ma}


@app.post("/du-bao-tuong-lai")
def du_bao_tuong_lai():
    """Du bao ngay mai va hai ngay ke tiep, lay buc xa tu Open-Meteo.

    Dung chung co che chay nen va SSE voi /bat-dau, nen giao dien khong phai biet
    hai loai cong viec nay khac nhau.
    """
    don_cong_viec_cu()
    ct = request.get_json(force=True)
    ma = uuid.uuid4().hex[:12]
    cv = {"hang": queue.Queue(), "ket_qua": None, "loi": None,
          "xong": False, "luc": time.time()}
    with KHOA:
        CONG_VIEC[ma] = cv

    def chay():
        try:
            kq = DB.du_bao_tuong_lai(ct["duong_dan"], int(ct.get("so_ngay", 3)),
                                     ct.get("thuat_toan", "gbm"),
                                     bool(ct.get("gom_hom_nay")),
                                     ghi_log=cv["hang"].put)
            kq["loai_cong_viec"] = "du_bao"
            cv["ket_qua"] = kq
        except Exception as e:                       # noqa: BLE001
            cv["loi"] = f"{e}\n\n{traceback.format_exc(limit=3)}"
        finally:
            cv["xong"] = True
            cv["hang"].put(None)

    threading.Thread(target=chay, daemon=True).start()
    return {"ma": ma}


@app.get("/xuat-excel/<ma>")
def xuat_excel_route(ma):
    """Xuat ket qua du bao cua mot cong viec ra Excel.

    Xuat tu KET QUA DA LUU cua cong viec chu khong chay lai du bao: neu chay lai thi
    tep Excel se lay du bao NWP moi hon va khong con khop voi bang dang hien tren man
    hinh, ma nguoi bam nut hoan toan khong biet dieu do.
    """
    cv = CONG_VIEC.get(ma)
    if cv is None or not cv.get("ket_qua"):
        return "Khong con ket qua nay. Chay lai du bao roi bam xuat.", 404

    kq = cv["ket_qua"]
    thu_muc = GOC / "data" / "du_bao"
    ten = f"du_bao_{kq['ngay'][0]['ngay']}_{ma}.xlsx"
    try:
        import xuat_excel
        duong = xuat_excel.xuat_excel(kq, thu_muc / ten)
    except ImportError as e:
        # Phai bat quanh CA LOI GOI chu khong chi quanh "import xuat_excel". Tep
        # xuat_excel.py import openpyxl BEN TRONG ham, nen dong import module van
        # chay tron va loi no muon hon mot bac -- luoi dat sai cho thi khong bat duoc.
        return (f"Thieu thu vien de ghi Excel ({e}).\n\n"
                f"Chay lenh sau roi thu lai:\n"
                f"    {sys.executable} -m pip install openpyxl"), 500
    return send_file(duong, as_attachment=True, download_name=ten)


@app.get("/xuat-model/<ma>")
def xuat_model_route(ma):
    """Tai goi model do chinh cong viec huan luyen nay tao ra."""
    cv = CONG_VIEC.get(ma)
    kq = cv.get("ket_qua") if cv else None
    thong_tin = kq.get("mo_hinh_da_luu") if kq else None
    if not thong_tin or not thong_tin.get("tep"):
        return "Khong con model cua lan huan luyen nay. Huan luyen lai roi bam xuat.", 404

    # Chi cho tai mot ten tep nam truc tiep trong thu muc model.
    ten = Path(thong_tin["tep"]).name
    duong = (DB.THU_MUC_MO_HINH / ten).resolve()
    thu_muc = DB.THU_MUC_MO_HINH.resolve()
    if duong.parent != thu_muc or not duong.is_file():
        return "Tep model khong con ton tai tren may chu.", 404
    return send_file(duong, as_attachment=True, download_name=ten,
                     mimetype="application/octet-stream")


@app.get("/xuat-model-hien-tai/<thuat_toan>")
def xuat_model_hien_tai_route(thuat_toan):
    """Tai model khong nhiet hien dang duoc he thong dung cho thuat toan da chon."""
    if thuat_toan not in H.THUAT_TOAN:
        return "Khong biet thuat toan nay.", 404
    duong = DB.duong_mo_hinh(thuat_toan, bo_nhiet=True).resolve()
    if duong.parent != DB.THU_MUC_MO_HINH.resolve() or not duong.is_file():
        return "Chua co model hien tai cho thuat toan nay. Hay huan luyen truoc.", 404
    return send_file(duong, as_attachment=True, download_name=duong.name,
                     mimetype="application/octet-stream")


@app.get("/huong-dan-deploy-model")
def huong_dan_deploy_model_route():
    return send_file(GOC / "HUONG_DAN_DEPLOY_MODEL.md", mimetype="text/markdown")


@app.get("/tai-huong-dan-deploy-model")
def tai_huong_dan_deploy_model_route():
    return send_file(GOC / "HUONG_DAN_DEPLOY_MODEL.md", as_attachment=True,
                     download_name="HUONG_DAN_DEPLOY_MODEL.md",
                     mimetype="text/markdown")


@app.post("/ngay-qua-khu")
def ngay_qua_khu():
    """Tra ve chuoi bức xa va cong suat DO DUOC cua mot ngay, de dat canh du bao.

    Tra rieng tung ngay theo yeu cau chu khong nhet ca nam vao ket qua du bao: bo
    du lieu co hon 380 ngay, moi ngay 96 o -- goi hon 36 nghin diem qua trinh duyet
    de nguoi dung xem mot ngay la lang phi vo ich.
    """
    ct = request.get_json(force=True)
    try:
        d = nap(ct["duong_dan"])
        ngay = pd.Timestamp(ct["ngay"]).date()
    except Exception as e:                           # noqa: BLE001
        return {"loi": f"Khong doc duoc: {e}"}, 400

    g = d[d.index.date == ngay]
    if len(g) == 0:
        return {"loi": f"Khong co du lieu ngay {ngay}"}, 404

    p, ghi = g["p_ac_mw"], g.get("ghi_wm2")
    sang = g["sol_elev"] > 0
    kt = g["kt"] if "kt" in g.columns else None
    return {
        "ngay": str(ngay),
        "thu": DB._thu(pd.Timestamp(ngay)),
        "so_o_ngay": int(sang.sum()),
        "so_o_thieu": int((sang & p.isna()).sum()),
        "e_mwh": _lam_tron(p.clip(lower=0).sum() * 0.25, 1),
        "dinh_mw": _lam_tron(p.max(), 2),
        "gio_dinh": (p.idxmax().strftime("%H:%M") if p.notna().any() else None),
        "ghi_dinh": _lam_tron(ghi.max() if ghi is not None else None, 0),
        "kt_tb": _lam_tron(kt[sang].mean() if kt is not None else None, 3),
        "diem": [[t.strftime("%H:%M"),
                  _lam_tron(a, 3),
                  _lam_tron(b, 0)]
                 for t, a, b in zip(g.index, p,
                                    ghi if ghi is not None else [np.nan] * len(g))],
    }


def _lam_tron(v, n):
    """NaN -> None. json.dumps cua Flask se de NaN nguyen, ma NaN khong phai JSON
    hop le nen JSON.parse ben trinh duyet se nem loi va mat ca phan hoi."""
    if v is None:
        return None
    try:
        v = float(v)
    except (TypeError, ValueError):
        return None
    return None if not np.isfinite(v) else round(v, n)


@app.get("/tien-do/<ma>")
def tien_do(ma):
    cv = CONG_VIEC.get(ma)
    if cv is None:
        return "Khong thay cong viec", 404

    def phat():
        while True:
            try:
                dong = cv["hang"].get(timeout=20)
            except queue.Empty:
                yield ": nhip\n\n"       # giu ket noi song
                continue
            if dong is None:
                break
            yield "data: " + json.dumps({"dong": dong}, ensure_ascii=False) + "\n\n"
        yield "data: " + json.dumps(
            {"xong": True, "ket_qua": cv["ket_qua"], "loi": cv["loi"]},
            ensure_ascii=False, default=str) + "\n\n"

    return Response(phat(), mimetype="text/event-stream", headers={
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",        # tat dem neu chay sau nginx
        "Connection": "keep-alive",
    })


# ---------------------------------------------------------------- route
@app.route("/", methods=["GET"])
def trang_chu():
    ds = liet_ke_bo_du_lieu()
    loi, tom_tat = None, None
    mo_hinh_hien_co = {
        ma: DB.duong_mo_hinh(ma, bo_nhiet=True).is_file()
        for ma in H.THUAT_TOAN
    }

    chon = {
        "duong_dan": request.args.get("duong_dan") or (ds[0]["duong_dan"] if ds else ""),
        "thuat_toan": "gbm",
        "so_fold": 3,
        "bo_nhiet": True,
    }

    if chon["duong_dan"]:
        try:
            tom_tat = tom_tat_du_lieu(nap(chon["duong_dan"]))
        except Exception as e:                       # noqa: BLE001
            loi = f"Khong doc duoc bo du lieu: {e}"

    return render_template("index.html", ds=ds, chon=chon, tom_tat=tom_tat,
                           thuat_toan=H.THUAT_TOAN, giai_thich=GIAI_THICH, loi=loi,
                           mo_hinh_hien_co=mo_hinh_hien_co)


if __name__ == "__main__":
    if not liet_ke_bo_du_lieu():
        print("Chua co bo du lieu nao trong", THU_MUC_DU_LIEU)
        print("Chay truoc:  python tools/tao_bo_du_lieu.py")
    print("Tren may nay: http://127.0.0.1:6001")
    print("Trong LAN:    http://<IP-may-chay>:6001")
    # threaded=True bat buoc: mot luong chay huan luyen, mot luong phuc vu SSE
    app.run(host="0.0.0.0", port=6001, debug=True, threaded=True)
