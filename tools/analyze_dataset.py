"""
analyze_dataset.py
==================
Phan tich / profiling bo du lieu CSV da xuat tu export_to_csv.py.
Tra loi cac cau hoi can thiet truoc khi lam mo hinh du bao:

  1. Dang du lieu   - bao nhieu dong/cot, kieu gi, bang nao la time-series
  2. Truc thoi gian - pham vi, do phan giai thuc te, do phu, khoang trong
  3. Chat luong     - thieu, trung timestamp, gia tri hang so, ngoai khoang
  4. Y nghia vat ly - cot nao la cong suat / buc xa / nhiet do / dien ap
  5. Kiem chung     - buc xa co dinh vao ~12h trua khong (xac nhan mui gio dung)
                    - cong suat ban dem co bang 0 khong
                    - tuong quan buc xa <-> cong suat

Vi du:
    python analyze_dataset.py ../data/csv -o ../data/report --tz 7
    python analyze_dataset.py ../data/csv -o ../data/report --tz 7 --plots

Dau ra:
    <out>/analysis_report.md   - bao cao tong hop (doc truoc)
    <out>/column_profile.csv   - thong ke chi tiet tung cot cua tung bang
    <out>/time_profile.csv     - truc thoi gian tung bang
    <out>/plots/*.png          - bieu do (neu bat --plots)
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import os
import sys
from collections import Counter, defaultdict

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------
# Phan loai y nghia vat ly cua cot theo ten
# --------------------------------------------------------------------------

ROLE_RULES = [
    ("irradiance",  lambda s: "rad" in s or "irr" in s or s.endswith("ghi") or "poa" in s),
    ("energy",      lambda s: any(k in s for k in ("kwh", "mwh", "energy", "wh_", "_wh"))),
    ("active_power", lambda s: s.endswith("_p") or s.endswith("meas_p") or "_p_" in s
                     or s.endswith("_power") or "setpoint" in s or s.endswith("p_high")
                     or s.endswith("p_low")),
    ("reactive_power", lambda s: s.endswith("_q")),
    ("power_factor", lambda s: s.endswith("pf")),
    ("current",     lambda s: s.endswith(("_ia", "_ib", "_ic", "_in")) or "current" in s),
    ("voltage",     lambda s: s.endswith(("_ua", "_ub", "_uc", "_uab", "_ubc", "_uca"))),
    ("frequency",   lambda s: s.endswith("_f")),
    ("temperature", lambda s: "temp" in s or s.endswith(("_t", "panel_t", "air_t", "oiltemp"))),
    ("humidity",    lambda s: "humid" in s),
    ("wind",        lambda s: "wind" in s),
    ("pressure",    lambda s: "pressure" in s),
    ("performance_ratio", lambda s: s.endswith("_pr") or s == "data_pr"),
    ("tap_changer", lambda s: s.endswith("_tap")),
]

META_COLS = {"id", "logtype", "notsync", "rowguid", "sync", "replaced", "hide"}
TIME_COLS = {"ts_utc", "ts_local", "utctimestamp_ticks", "datetimeutcticks", "datetime"}


def classify(col: str) -> str:
    s = col.strip().lower()
    if s in META_COLS:
        return "meta"
    if s in TIME_COLS:
        return "time"
    for role, fn in ROLE_RULES:
        try:
            if fn(s):
                return role
        except Exception:
            pass
    return "other"


# --------------------------------------------------------------------------
# Bo tich luy thong ke theo tung chunk (khong nap ca bang vao RAM)
# --------------------------------------------------------------------------


class ColAcc:
    """Thong ke luy tien cho mot cot so."""

    RES_CAP = 100_000     # kich thuoc mau du tru de tinh percentile

    def __init__(self, name):
        self.name = name
        self.n = 0
        self.n_null = 0
        self.n_zero = 0
        self.n_neg = 0
        self.s = 0.0
        self.ss = 0.0
        self.mn = math.inf
        self.mx = -math.inf
        self.res = []
        self.seen = 0
        self.uniq = set()
        self.uniq_overflow = False
        self.rng = np.random.default_rng(0)

    def update(self, v: pd.Series):
        self.n += len(v)
        nn = v.isna()
        self.n_null += int(nn.sum())
        x = v[~nn].to_numpy(dtype="float64", copy=False)
        if x.size == 0:
            return
        self.n_zero += int((x == 0).sum())
        self.n_neg += int((x < 0).sum())
        self.s += float(x.sum())
        self.ss += float((x * x).sum())
        self.mn = min(self.mn, float(x.min()))
        self.mx = max(self.mx, float(x.max()))
        if not self.uniq_overflow:
            self.uniq.update(x[:50_000].tolist())
            if len(self.uniq) > 5000:
                self.uniq_overflow = True
                self.uniq = set()
        # mau du tru
        for val in (x if x.size <= 5000 else self.rng.choice(x, 5000, replace=False)):
            self.seen += 1
            if len(self.res) < self.RES_CAP:
                self.res.append(val)
            else:
                j = self.rng.integers(0, self.seen)
                if j < self.RES_CAP:
                    self.res[int(j)] = val

    def result(self):
        nv = self.n - self.n_null
        mean = self.s / nv if nv else math.nan
        var = (self.ss / nv - mean * mean) if nv else math.nan
        std = math.sqrt(max(var, 0.0)) if nv else math.nan
        q = {}
        if self.res:
            a = np.array(self.res)
            for p in (1, 25, 50, 75, 99):
                q[f"p{p}"] = float(np.percentile(a, p))
        return {
            "column": self.name,
            "role": classify(self.name),
            "n": self.n,
            "n_null": self.n_null,
            "pct_null": round(100 * self.n_null / self.n, 3) if self.n else None,
            "pct_zero": round(100 * self.n_zero / nv, 3) if nv else None,
            "pct_negative": round(100 * self.n_neg / nv, 3) if nv else None,
            "n_unique_approx": ("> 5000" if self.uniq_overflow else len(self.uniq)),
            "is_constant": (not self.uniq_overflow and len(self.uniq) <= 1),
            "min": None if self.mn == math.inf else round(self.mn, 6),
            "max": None if self.mx == -math.inf else round(self.mx, 6),
            "mean": None if nv == 0 else round(mean, 6),
            "std": None if nv == 0 else round(std, 6),
            **{k: round(v, 6) for k, v in q.items()},
        }


class DiurnalAcc:
    """Trung binh theo gio dia phuong -> kiem tra chu ky ngay/dem."""

    def __init__(self, cols):
        self.sum = {c: np.zeros(24) for c in cols}
        self.cnt = {c: np.zeros(24) for c in cols}

    def update(self, hours: np.ndarray, df: pd.DataFrame):
        for c in self.sum:
            if c not in df.columns:
                continue
            v = df[c].to_numpy(dtype="float64", copy=False)
            m = ~np.isnan(v)
            if not m.any():
                continue
            np.add.at(self.sum[c], hours[m], v[m])
            np.add.at(self.cnt[c], hours[m], 1)

    def profile(self, c):
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.where(self.cnt[c] > 0, self.sum[c] / np.maximum(self.cnt[c], 1), np.nan)


# --------------------------------------------------------------------------
# Phan tich mot bang
# --------------------------------------------------------------------------


def analyze_table(path, table, schema, tz, chunksize, max_rows, corr_cols_cap=8):
    pg_types = {}
    if schema and table in schema.get("tables", {}):
        pg_types = {c["name"]: c["pg_type"] for c in schema["tables"][table]["columns"]}

    header = pd.read_csv(path, nrows=0).columns.tolist()
    numeric_cols = [c for c in header if classify(c) not in ("time",)
                    and c not in ("ts_utc", "ts_local")]
    accs = {c: ColAcc(c) for c in numeric_cols}

    time_col = "ts_utc" if "ts_utc" in header else None
    tick_col = next((c for c in header if "tick" in c.lower()), None)

    # cot dang quan tam de ve profile theo gio
    interest = [c for c in header
                if classify(c) in ("irradiance", "active_power", "temperature",
                                   "reactive_power", "performance_ratio")]
    diurnal = DiurnalAcc(interest[:30])

    ts_all = []
    n_rows = 0
    corr_cols = ([c for c in header if classify(c) == "irradiance"][:3]
                 + [c for c in header if classify(c) == "active_power"][:5])[:corr_cols_cap]
    corr_buf = []

    reader = pd.read_csv(
        path, chunksize=chunksize, low_memory=False,
        parse_dates=[time_col] if time_col else None,
    )
    for chunk in reader:
        n_rows += len(chunk)
        for c in numeric_cols:
            if c in chunk.columns:
                accs[c].update(pd.to_numeric(chunk[c], errors="coerce"))
        if tick_col and tick_col in chunk.columns:
            ts_all.append(pd.to_numeric(chunk[tick_col], errors="coerce").to_numpy())
        if time_col and time_col in chunk.columns:
            h = chunk[time_col]
            if tz:
                h = h + pd.Timedelta(hours=tz)
            hours = h.dt.hour.to_numpy()
            ok = ~pd.isna(hours)
            if ok.any():
                num = chunk[[c for c in diurnal.sum if c in chunk.columns]].apply(
                    pd.to_numeric, errors="coerce")
                diurnal.update(hours[ok].astype(int), num[ok])
        if corr_cols:
            sub = chunk[[c for c in corr_cols if c in chunk.columns]].apply(
                pd.to_numeric, errors="coerce")
            if len(corr_buf) * chunksize < 400_000:
                corr_buf.append(sub)
        if max_rows and n_rows >= max_rows:
            break

    # ---- truc thoi gian ----
    tinfo = {"table": table, "rows": n_rows, "columns": len(header)}
    if ts_all:
        ticks = np.concatenate(ts_all)
        ticks = ticks[~np.isnan(ticks)].astype("int64")
        tinfo["n_valid_ts"] = int(ticks.size)
        if ticks.size:
            srt = np.sort(ticks)
            uniq = np.unique(srt)
            tinfo["n_duplicate_ts"] = int(srt.size - uniq.size)
            tinfo["is_sorted_in_file"] = bool(np.all(np.diff(ticks) >= 0))
            from pgdump_reader import ticks_to_datetime
            t0, t1 = ticks_to_datetime(int(srt[0])), ticks_to_datetime(int(srt[-1]))
            tinfo["ts_min_utc"] = str(t0)
            tinfo["ts_max_utc"] = str(t1)
            span_s = (int(srt[-1]) - int(srt[0])) / 1e7
            tinfo["span_days"] = round(span_s / 86400, 2)
            d = np.diff(uniq) / 1e7          # giay
            if d.size:
                dd = np.round(d).astype("int64")
                top = Counter(dd.tolist()).most_common(6)
                tinfo["median_interval_s"] = float(np.median(d))
                tinfo["top_intervals_s"] = "; ".join(
                    f"{k}s x{v:,} ({100*v/dd.size:.1f}%)" for k, v in top)
                nominal = top[0][0] if top[0][0] > 0 else max(1, int(np.median(d)))
                tinfo["nominal_interval_s"] = nominal
                tinfo["pct_at_nominal"] = round(100 * float((dd == nominal).mean()), 2)
                expected = span_s / nominal + 1
                tinfo["coverage_pct"] = round(100 * uniq.size / expected, 2)
                gaps = d[d > 3 * nominal]
                tinfo["n_gaps_gt_3x"] = int(gaps.size)
                tinfo["total_gap_hours"] = round(float(gaps.sum()) / 3600, 2) if gaps.size else 0.0
                tinfo["max_gap_hours"] = round(float(gaps.max()) / 3600, 2) if gaps.size else 0.0

    # ---- tuong quan ----
    corr = None
    if corr_buf:
        cdf = pd.concat(corr_buf, ignore_index=True)
        if cdf.shape[1] >= 2:
            corr = cdf.corr(numeric_only=True)

    prof = []
    for c in header:
        if c in accs:
            r = accs[c].result()
        else:
            r = {"column": c, "role": classify(c), "n": n_rows}
        r["table"] = table
        r["pg_type"] = pg_types.get(c, "")
        prof.append(r)

    return tinfo, prof, diurnal, interest, corr, header


# --------------------------------------------------------------------------
# Bao cao
# --------------------------------------------------------------------------


def fmt_table(rows, cols, headers=None):
    headers = headers or cols
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join("---" for _ in cols) + "|"]
    for r in rows:
        out.append("| " + " | ".join(
            "" if r.get(c) is None else str(r.get(c)) for c in cols) + " |")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(
        description="Phan tich bo du lieu CSV da xuat tu pg_dump",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("csvdir", help="thu muc chua CSV (dau ra cua export_to_csv.py)")
    ap.add_argument("-o", "--outdir", default="analysis", help="thu muc bao cao")
    ap.add_argument("--tz", type=float, default=0.0, help="lech gio dia phuong (VN = 7)")
    ap.add_argument("--chunksize", type=int, default=300_000)
    ap.add_argument("--max-rows", type=int, default=0, help="0 = doc het")
    ap.add_argument("--plots", action="store_true", help="ve bieu do PNG (can matplotlib)")
    ap.add_argument("-t", "--table", action="append", default=[])
    args = ap.parse_args()

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    schema = None
    sp = os.path.join(args.csvdir, "_schema.json")
    if os.path.exists(sp):
        with open(sp, encoding="utf-8") as fh:
            schema = json.load(fh)

    files = sorted(glob.glob(os.path.join(args.csvdir, "*.csv")))
    files = [f for f in files if not os.path.basename(f).startswith("_")]
    if args.table:
        files = [f for f in files
                 if os.path.splitext(os.path.basename(f))[0] in args.table]
    if not files:
        print(f"Khong tim thay CSV trong {args.csvdir}", file=sys.stderr)
        return 2

    os.makedirs(args.outdir, exist_ok=True)
    plotdir = os.path.join(args.outdir, "plots")
    if args.plots:
        os.makedirs(plotdir, exist_ok=True)

    all_time, all_prof, notes = [], [], []
    diurnals = {}
    corrs = {}

    for f in files:
        table = os.path.splitext(os.path.basename(f))[0]
        print(f"[*] {table} ...", flush=True)
        try:
            tinfo, prof, diurnal, interest, corr, header = analyze_table(
                f, table, schema, args.tz, args.chunksize, args.max_rows)
        except Exception as e:
            print(f"    LOI: {e}", file=sys.stderr)
            continue
        all_time.append(tinfo)
        all_prof.extend(prof)
        diurnals[table] = (diurnal, interest)
        if corr is not None:
            corrs[table] = corr
        print(f"    {tinfo['rows']:,} dong, {tinfo['columns']} cot, "
              f"buoc mau ~{tinfo.get('nominal_interval_s','?')}s, "
              f"do phu {tinfo.get('coverage_pct','?')}%")

    df_time = pd.DataFrame(all_time)
    df_prof = pd.DataFrame(all_prof)
    df_time.to_csv(os.path.join(args.outdir, "time_profile.csv"), index=False)
    front = ["table", "column", "role", "pg_type", "n", "pct_null", "pct_zero",
             "is_constant", "min", "p1", "p50", "p99", "max", "mean", "std",
             "n_unique_approx"]
    cols = [c for c in front if c in df_prof.columns] + \
           [c for c in df_prof.columns if c not in front]
    df_prof[cols].to_csv(os.path.join(args.outdir, "column_profile.csv"), index=False)

    # ---------------- bao cao markdown ----------------
    L = []
    A = L.append
    A("# Bao cao phan tich dataset\n")
    if schema:
        A(f"- Nguon: `{schema.get('source_dump','')}`")
        A(f"- Database: **{schema.get('database','')}** "
          f"(PostgreSQL {schema.get('server_version','')})")
        A(f"- Dump tao luc: {schema.get('dump_created','')}")
    A(f"- Mui gio dia phuong dung trong bao cao: UTC{args.tz:+g}")
    A(f"- So bang phan tich: {len(df_time)}\n")

    A("## 1. Tong quan truc thoi gian\n")
    tc = ["table", "rows", "columns", "ts_min_utc", "ts_max_utc", "span_days",
          "nominal_interval_s", "pct_at_nominal", "coverage_pct",
          "n_duplicate_ts", "n_gaps_gt_3x", "max_gap_hours"]
    tc = [c for c in tc if c in df_time.columns]
    A(fmt_table(df_time.to_dict("records"), tc,
                ["Bang", "Dong", "Cot", "Bat dau (UTC)", "Ket thuc (UTC)", "So ngay",
                 "Buoc mau (s)", "% dung buoc", "Do phu %", "Trung ts",
                 "So gap >3x", "Gap lon nhat (h)"][:len(tc)]))
    A("")

    A("### Phan bo khoang cach giua cac mau\n")
    for r in df_time.to_dict("records"):
        if r.get("top_intervals_s"):
            A(f"- **{r['table']}**: {r['top_intervals_s']}")
    A("")

    A("## 2. Phan loai cot theo y nghia vat ly\n")
    if not df_prof.empty:
        piv = df_prof.pivot_table(index="table", columns="role", values="column",
                                  aggfunc="count", fill_value=0)
        A(piv.to_markdown())
    A("")

    A("## 3. Canh bao chat luong du lieu\n")
    warn = []
    if not df_prof.empty:
        for r in df_prof.to_dict("records"):
            if r.get("role") in ("meta", "time"):
                continue
            c, t = r.get("column"), r.get("table")
            if r.get("is_constant"):
                warn.append(f"`{t}.{c}` — **hang so** (chi 1 gia tri), khong dung lam feature.")
            pz = r.get("pct_zero")
            if pz is not None and pz > 95:
                warn.append(f"`{t}.{c}` — {pz}% gia tri bang 0, nghi ngo tag chet "
                            f"hoac NULL bi ghi thanh 0.")
            pn = r.get("pct_null")
            if pn is not None and pn > 30:
                warn.append(f"`{t}.{c}` — thieu {pn}% du lieu.")
            # gia tri dot bien: max lon hon p99 hang tram lan -> gan nhu chac chan la rac
            p99, mx = r.get("p99"), r.get("max")
            if p99 and mx and p99 > 0 and mx > 100 * p99:
                warn.append(f"`{t}.{c}` — **gia tri dot bien**: max={mx:,.0f} trong khi "
                            f"p99={p99:,.2f} (gap {mx/p99:,.0f} lan). Phai loc truoc khi huan luyen.")
            if r.get("role") == "irradiance":
                if mx is not None and mx > 1400:
                    warn.append(f"`{t}.{c}` — buc xa max = {mx} W/m2, vuot nguong vat ly "
                                f"(GHI cuc dai ~1200-1400 W/m2 ke ca cloud enhancement).")
            if r.get("role") == "active_power" and r.get("pct_negative") not in (None, 0) \
                    and r["pct_negative"] > 5:
                warn.append(f"`{t}.{c}` — {r['pct_negative']}% gia tri am "
                            f"(tieu thu tu luoi hoac sai dau).")
    for r in df_time.to_dict("records"):
        if r.get("n_duplicate_ts"):
            warn.append(f"`{r['table']}` — {r['n_duplicate_ts']:,} timestamp trung lap.")
        if r.get("coverage_pct") is not None and r["coverage_pct"] < 90:
            warn.append(f"`{r['table']}` — do phu chi {r['coverage_pct']}% "
                        f"(mat {r.get('total_gap_hours',0)} gio).")
        if r.get("is_sorted_in_file") is False:
            warn.append(f"`{r['table']}` — du lieu KHONG sap xep theo thoi gian trong file, "
                        f"phai sort truoc khi tinh chuoi thoi gian.")
    if warn:
        for w in dict.fromkeys(warn):
            A(f"- {w}")
    else:
        A("_Khong phat hien van de dang ke._")
    A("")

    A("## 4. Kiem chung chu ky ngay/dem (xac nhan mui gio)\n")
    A(f"Trung binh theo gio dia phuong (UTC{args.tz:+g}). "
      "Buc xa phai dinh quanh 11h-13h; neu lech thi mui gio dang sai.\n")
    for table, (di, interest) in diurnals.items():
        picks = [c for c in interest if classify(c) == "irradiance"][:2] + \
                [c for c in interest if classify(c) == "active_power"][:2]
        if not picks:
            continue
        A(f"**{table}**\n")
        A("| Cot | Vai tro | Gio dinh (local) | Gia tri dinh | TB ban dem (0-4h) |")
        A("|---|---|---|---|---|")
        night_flags = []
        for c in picks:
            p = di.profile(c)
            if np.all(np.isnan(p)):
                continue
            peak = int(np.nanargmax(p))
            with np.errstate(invalid="ignore"):
                seg = p[0:5]
                night = float(np.nanmean(seg)) if not np.all(np.isnan(seg)) else float("nan")
            A(f"| {c} | {classify(c)} | {peak}h | {p[peak]:.2f} | {night:.3f} |")
            role = classify(c)
            if role == "irradiance" and not math.isnan(night) and night > 5:
                night_flags.append(
                    f"`{table}.{c}` ban dem trung binh {night:.1f} W/m2 (dang le ~0) "
                    f"— cam bien bi lech zero (offset), phai hieu chinh.")
            if role == "irradiance" and peak not in (11, 12, 13):
                night_flags.append(
                    f"`{table}.{c}` dinh luc {peak}h thay vi 11-13h — kiem tra lai mui gio.")
        A("")
        for f_ in night_flags:
            A(f"> [!] {f_}")
        if night_flags:
            A("")

    if corrs:
        A("## 5. Tuong quan buc xa <-> cong suat\n")
        A("Tuong quan Pearson. Voi PV, |r| giua buc xa va cong suat AC thuong > 0.9.\n")
        for table, c in corrs.items():
            irr = [x for x in c.columns if classify(x) == "irradiance"]
            pw = [x for x in c.columns if classify(x) == "active_power"]
            if not irr or not pw:
                continue
            A(f"**{table}**\n")
            A(c.loc[irr, pw].round(3).to_markdown())
            A("")

    A("## 6. De xuat buoc tiep theo\n")
    ts_tables = df_time[df_time.get("nominal_interval_s").notna()] \
        if "nominal_interval_s" in df_time.columns else pd.DataFrame()
    if not ts_tables.empty:
        finest = ts_tables.sort_values("nominal_interval_s").iloc[0]
        A(f"- Bang co do phan giai min nhat: **{finest['table']}** "
          f"(~{finest['nominal_interval_s']}s). "
          f"Do phan giai nay quyet dinh chuc nang du bao nao kha thi.")
        A(f"- Tong pham vi thoi gian dai nhat: "
          f"**{df_time.loc[df_time['span_days'].idxmax(),'table']}** "
          f"({df_time['span_days'].max()} ngay). "
          "Duoi ~365 ngay thi mo hinh khong hoc duoc chu ky mua.")
    A("- Cot muc tieu du bao nen la cong suat tai diem dau noi "
      "(bang cua bay 110kV), khong phai tong cac bay 22kV, tru khi da doi chieu.")
    A("- Cac cot co `pct_zero` rat cao can lam ro: la NULL bi ghi thanh 0 hay tag chua dau day. "
      "Theo yeu cau FR-04, du lieu trong PHAI giu trang thai thieu, khong duoc gan 0.")
    A("- Resample len 15 phut (cho FC-02) chi duoc phep tu du lieu min hon; "
      "kiem tra lai cot `nominal_interval_s` o bang 1.")

    report = "\n".join(L)
    rp = os.path.join(args.outdir, "analysis_report.md")
    with open(rp, "w", encoding="utf-8") as fh:
        fh.write(report)

    # ---------------- plots ----------------
    if args.plots:
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
        except ImportError:
            print("Chua co matplotlib: pip install matplotlib", file=sys.stderr)
        else:
            for table, (di, interest) in diurnals.items():
                picks = [c for c in interest][:6]
                picks = [c for c in picks if not np.all(np.isnan(di.profile(c)))]
                if not picks:
                    continue
                fig, ax = plt.subplots(figsize=(9, 4.5))
                for c in picks:
                    ax.plot(range(24), di.profile(c), marker="o", ms=3,
                            label=c[:42])
                ax.set_xlabel(f"Gio dia phuong (UTC{args.tz:+g})")
                ax.set_ylabel("Gia tri trung binh")
                ax.set_title(f"{table} — profile theo gio trong ngay")
                ax.grid(alpha=.3)
                ax.legend(fontsize=7)
                fig.tight_layout()
                fig.savefig(os.path.join(plotdir, f"{table}_diurnal.png"), dpi=110)
                plt.close(fig)
            print(f"Bieu do: {plotdir}")

    print("\n" + "=" * 70)
    print(report[:4000])
    print("=" * 70)
    print(f"\nBao cao day du : {rp}")
    print(f"Profile cot    : {os.path.join(args.outdir,'column_profile.csv')}")
    print(f"Profile thoi gian: {os.path.join(args.outdir,'time_profile.csv')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
