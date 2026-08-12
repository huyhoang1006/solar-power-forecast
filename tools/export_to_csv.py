"""
export_to_csv.py
================
Xuat TOAN BO du lieu tu file dump PostgreSQL custom-format ra CSV.
Khong can cai PostgreSQL.

Vi du:
    # xuat tat ca bang
    python export_to_csv.py ../db_fujiwara.sql -o ../data/csv

    # chi vai bang, them cot thoi gian doc tu .NET ticks, gio Viet Nam
    python export_to_csv.py ../db_fujiwara.sql -o ../data/csv \
        -t His_131 -t His_report -t Weather --tz 7

    # sap xep theo thoi gian (can du RAM cho bang lon) va gzip ket qua
    python export_to_csv.py ../db_fujiwara.sql -o ../data/csv --sort-by-time --gzip

Dau ra:
    <outdir>/<Ten_bang>.csv          - moi bang mot file
    <outdir>/_schema.json            - schema day du + kieu PostgreSQL
    <outdir>/_manifest.csv           - so dong / so cot / kich thuoc tung bang

Quy uoc: gia tri NULL ghi thanh o TRONG (khong phai 0). pandas se doc thanh NaN.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pgdump_reader import (  # noqa: E402
    PgDumpArchive,
    COMPRESSION_NAMES,
    ticks_to_datetime,
)

# Ten cot chua .NET DateTime ticks trong cac historian SCADA (Ignition/AVEVA/…)
TICK_COLUMN_CANDIDATES = (
    "UTCTimestamp_Ticks",
    "DateTimeUTCTicks",
    "TimestampTicks",
    "utctimestamp_ticks",
)


def find_tick_column(columns):
    for c in columns:
        if c in TICK_COLUMN_CANDIDATES:
            return c
    for c in columns:
        if "tick" in c.lower():
            return c
    return None


def human(n):
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f}{u}"
        n /= 1024
    return f"{n:.1f}TB"


def export_table(ar, name, outdir, tz_offset, add_time_col, use_gzip,
                 sort_by_time, limit, progress_every):
    t = ar.get_table(name)
    header = list(t.column_names)

    tick_col = find_tick_column(header) if add_time_col else None
    tick_idx = header.index(tick_col) if tick_col else None
    if tick_col:
        header = header + ["ts_utc"] + (["ts_local"] if tz_offset else [])

    ext = ".csv.gz" if use_gzip else ".csv"
    path = os.path.join(outdir, name + ext)
    opener = (lambda p: gzip.open(p, "wt", newline="", encoding="utf-8")) if use_gzip \
        else (lambda p: open(p, "w", newline="", encoding="utf-8"))

    t0 = time.time()
    nrows = 0
    nbad = 0

    def build(row):
        nonlocal nbad
        if tick_idx is None:
            return row
        raw = row[tick_idx]
        try:
            ticks = int(raw)
        except (TypeError, ValueError):
            nbad += 1
            return row + [""] + ([""] if tz_offset else [])
        u = ticks_to_datetime(ticks)
        extra = ["" if u is None else u.isoformat(sep=" ", timespec="milliseconds")]
        if tz_offset:
            l = ticks_to_datetime(ticks, tz_offset)
            extra.append("" if l is None else l.isoformat(sep=" ", timespec="milliseconds"))
        return row + extra

    if sort_by_time and tick_idx is not None:
        rows = []
        for row in ar.iter_rows(name):
            rows.append(row)
            if limit and len(rows) >= limit:
                break
        rows.sort(key=lambda r: int(r[tick_idx]) if _isint(r[tick_idx]) else -1)
        with opener(path) as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(header)
            for row in rows:
                w.writerow(["" if v is None else v for v in build(row)])
                nrows += 1
    else:
        with opener(path) as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(header)
            for row in ar.iter_rows(name):
                w.writerow(["" if v is None else v for v in build(row)])
                nrows += 1
                if progress_every and nrows % progress_every == 0:
                    print(f"    ... {nrows:,} dong", end="\r", flush=True)
                if limit and nrows >= limit:
                    break

    size = os.path.getsize(path)
    dt = time.time() - t0
    print(f"  {name:<24} {nrows:>10,} dong  {len(header):>3} cot  "
          f"{human(size):>9}  {dt:5.1f}s"
          + (f"  [{nbad} ticks loi]" if nbad else ""))
    return {
        "table": name,
        "file": os.path.basename(path),
        "rows": nrows,
        "columns": len(header),
        "bytes": size,
        "tick_column": tick_col,
        "bad_ticks": nbad,
    }


def _isint(v):
    try:
        int(v)
        return True
    except (TypeError, ValueError):
        return False


def main():
    ap = argparse.ArgumentParser(
        description="Xuat pg_dump custom-format ra CSV (khong can PostgreSQL)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("dump", help="duong dan file dump (vd: db_fujiwara.sql)")
    ap.add_argument("-o", "--outdir", default="csv_export", help="thu muc dau ra")
    ap.add_argument("-t", "--table", action="append", default=[],
                    help="chi xuat bang nay (lap lai duoc). Mac dinh: tat ca")
    ap.add_argument("--exclude", action="append", default=[], help="bo qua bang nay")
    ap.add_argument("--tz", type=float, default=0.0,
                    help="chenh lech gio dia phuong so voi UTC (VN = 7)")
    ap.add_argument("--no-time-col", action="store_true",
                    help="khong tu them cot ts_utc/ts_local tu .NET ticks")
    ap.add_argument("--gzip", action="store_true", help="nen dau ra .csv.gz")
    ap.add_argument("--sort-by-time", action="store_true",
                    help="sap xep theo timestamp (nap ca bang vao RAM)")
    ap.add_argument("--limit", type=int, default=0, help="chi lay N dong dau moi bang")
    ap.add_argument("--list", action="store_true", help="chi liet ke cau truc roi thoat")
    args = ap.parse_args()

    ar = PgDumpArchive(args.dump)

    if args.list:
        ar.print_summary()
        return 0

    names = args.table or ar.table_names()
    names = [n for n in names if n not in args.exclude]
    missing = [n for n in names if n not in ar.tables]
    if missing:
        print(f"Khong tim thay bang: {missing}", file=sys.stderr)
        print(f"Bang co san: {', '.join(ar.table_names())}", file=sys.stderr)
        return 2

    os.makedirs(args.outdir, exist_ok=True)

    print(f"Dump      : {args.dump}")
    print(f"Database  : {ar.dbname}  (PostgreSQL {ar.server_version}, nen "
          f"{COMPRESSION_NAMES.get(ar.compression)})")
    print(f"Dau ra    : {os.path.abspath(args.outdir)}")
    print(f"So bang   : {len(names)}\n")

    manifest = []
    for n in names:
        if not ar.tables[n].has_data:
            print(f"  {n:<24} (khong co khoi du lieu - bo qua)")
            continue
        manifest.append(export_table(
            ar, n, args.outdir, args.tz, not args.no_time_col,
            args.gzip, args.sort_by_time, args.limit, 200_000,
        ))

    # schema
    schema = {
        "source_dump": os.path.abspath(args.dump),
        "database": ar.dbname,
        "server_version": ar.server_version,
        "dump_created": str(ar.created),
        "archive_version": ar.version_str,
        "tz_offset_hours": args.tz,
        "tables": {
            n: {
                "namespace": ar.tables[n].namespace,
                "columns": [{"name": c, "pg_type": ty} for c, ty in ar.tables[n].columns],
                "ddl": ar.tables[n].ddl,
            }
            for n in names
        },
    }
    with open(os.path.join(args.outdir, "_schema.json"), "w", encoding="utf-8") as fh:
        json.dump(schema, fh, indent=2, ensure_ascii=False)

    with open(os.path.join(args.outdir, "_manifest.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["table", "file", "rows", "columns",
                                           "bytes", "tick_column", "bad_ticks"])
        w.writeheader()
        w.writerows(manifest)

    total_rows = sum(m["rows"] for m in manifest)
    total_bytes = sum(m["bytes"] for m in manifest)
    print(f"\nXong. {len(manifest)} bang, {total_rows:,} dong, {human(total_bytes)}.")
    print(f"Schema: {os.path.join(args.outdir, '_schema.json')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
