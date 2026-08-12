"""
pgdump_reader.py
================
Doc file dump PostgreSQL dinh dang *custom* (`pg_dump -Fc`, magic "PGDMP")
bang Python thuan - KHONG can cai PostgreSQL / pg_restore.

Ho tro archive version 1.12 -> 1.16 (PostgreSQL 12 -> 17).
Nen: none / gzip(zlib) san co; lz4 va zstd can pip install lz4 / zstandard.

Dung truc tiep:
    from pgdump_reader import PgDumpArchive
    ar = PgDumpArchive("db_fujiwara.sql")
    ar.print_summary()
    for row in ar.iter_rows("His_131"):
        ...

Chay CLI de xem nhanh cau truc:
    python pgdump_reader.py db_fujiwara.sql
"""

from __future__ import annotations

import io
import re
import sys
import zlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Iterator, Optional

# --------------------------------------------------------------------------
# Hang so cua dinh dang archive
# --------------------------------------------------------------------------

MAGIC = b"PGDMP"

# Thuat toan nen (pg_compress_algorithm)
COMPRESSION_NONE = 0
COMPRESSION_GZIP = 1
COMPRESSION_LZ4 = 2
COMPRESSION_ZSTD = 3
COMPRESSION_NAMES = {0: "none", 1: "gzip", 2: "lz4", 3: "zstd"}

# Loai block du lieu
BLK_DATA = 1
BLK_BLOBS = 3

# .NET DateTime tick: 100 nanosecond ke tu 0001-01-01 00:00:00
_DOTNET_EPOCH = datetime(1, 1, 1)
_TICKS_PER_US = 10


def _mk(maj: int, min_: int, rev: int) -> int:
    return (maj << 16) | (min_ << 8) | rev


K_VERS_1_0 = _mk(1, 0, 0)
K_VERS_1_2 = _mk(1, 2, 0)
K_VERS_1_3 = _mk(1, 3, 0)
K_VERS_1_4 = _mk(1, 4, 0)
K_VERS_1_5 = _mk(1, 5, 0)
K_VERS_1_6 = _mk(1, 6, 0)
K_VERS_1_7 = _mk(1, 7, 0)
K_VERS_1_8 = _mk(1, 8, 0)
K_VERS_1_10 = _mk(1, 10, 0)
K_VERS_1_11 = _mk(1, 11, 0)
K_VERS_1_14 = _mk(1, 14, 0)
K_VERS_1_15 = _mk(1, 15, 0)
K_VERS_MAX = _mk(1, 16, 0)


def ticks_to_datetime(ticks: int, tz_offset_hours: float = 0.0) -> Optional[datetime]:
    """Doi .NET DateTime ticks -> datetime. tz_offset_hours=7 cho gio Viet Nam."""
    if ticks is None:
        return None
    try:
        dt = _DOTNET_EPOCH + timedelta(microseconds=ticks // _TICKS_PER_US)
    except (OverflowError, ValueError):
        return None
    if tz_offset_hours:
        dt = dt + timedelta(hours=tz_offset_hours)
    return dt


# --------------------------------------------------------------------------
# Giai nen theo kieu streaming
# --------------------------------------------------------------------------


class _Decompressor:
    """Bao boc cac thuat toan nen ve cung 1 interface feed()/flush()."""

    def __init__(self, algorithm: int):
        self.algorithm = algorithm
        if algorithm == COMPRESSION_NONE:
            self._d = None
        elif algorithm == COMPRESSION_GZIP:
            self._d = zlib.decompressobj()
        elif algorithm == COMPRESSION_LZ4:
            try:
                import lz4.frame  # type: ignore
            except ImportError:
                raise RuntimeError(
                    "Dump duoc nen bang lz4. Chay: pip install lz4"
                )
            self._d = lz4.frame.LZ4FrameDecompressor()
        elif algorithm == COMPRESSION_ZSTD:
            try:
                import zstandard  # type: ignore
            except ImportError:
                raise RuntimeError(
                    "Dump duoc nen bang zstd. Chay: pip install zstandard"
                )
            self._d = zstandard.ZstdDecompressor().decompressobj()
        else:
            raise RuntimeError(f"Thuat toan nen khong ho tro: {algorithm}")

    def feed(self, data: bytes) -> bytes:
        if self._d is None:
            return data
        return self._d.decompress(data)

    def flush(self) -> bytes:
        if self._d is None:
            return b""
        try:
            return self._d.flush()
        except Exception:
            return b""


# --------------------------------------------------------------------------
# COPY text format
# --------------------------------------------------------------------------

_ESCAPES = {
    "b": "\b",
    "f": "\f",
    "n": "\n",
    "r": "\r",
    "t": "\t",
    "v": "\v",
    "\\": "\\",
}


def unescape_copy_field(s: str) -> Optional[str]:
    """Giai ma 1 truong trong COPY ... TO stdin (text format). Tra None neu NULL."""
    if s == "\\N":
        return None
    if "\\" not in s:
        return s
    out = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c != "\\":
            out.append(c)
            i += 1
            continue
        i += 1
        if i >= n:
            out.append("\\")
            break
        e = s[i]
        if e in _ESCAPES:
            out.append(_ESCAPES[e])
            i += 1
        elif e == "x":  # \xHH
            j = i + 1
            hexs = ""
            while j < n and len(hexs) < 2 and s[j] in "0123456789abcdefABCDEF":
                hexs += s[j]
                j += 1
            if hexs:
                out.append(chr(int(hexs, 16)))
                i = j
            else:
                out.append("x")
                i += 1
        elif e in "01234567":  # \ddd octal
            j = i
            octs = ""
            while j < n and len(octs) < 3 and s[j] in "01234567":
                octs += s[j]
                j += 1
            out.append(chr(int(octs, 8)))
            i = j
        else:
            out.append(e)
            i += 1
    return "".join(out)


# --------------------------------------------------------------------------
# TOC entry
# --------------------------------------------------------------------------


@dataclass
class TocEntry:
    dump_id: int = 0
    had_dumper: int = 0
    tableoid: str = ""
    oid: str = ""
    tag: str = ""
    desc: str = ""
    section: int = 0
    defn: str = ""
    drop_stmt: str = ""
    copy_stmt: str = ""
    namespace: str = ""
    tablespace: str = ""
    tableam: str = ""
    owner: str = ""
    deps: list = field(default_factory=list)
    data_state: int = 0
    data_pos: int = 0

    @property
    def qualified(self) -> str:
        return f"{self.namespace}.{self.tag}" if self.namespace else self.tag


@dataclass
class TableInfo:
    """Mot bang co du lieu: gom DDL (tu entry TABLE) va vi tri data (tu TABLE DATA)."""

    name: str
    namespace: str
    columns: list          # [(ten_cot, kieu_pg), ...] theo dung thu tu trong file data
    ddl: str
    data_entry: Optional[TocEntry]

    @property
    def column_names(self) -> list:
        return [c[0] for c in self.columns]

    @property
    def column_types(self) -> dict:
        return {c[0]: c[1] for c in self.columns}

    @property
    def has_data(self) -> bool:
        return self.data_entry is not None


# --------------------------------------------------------------------------
# Parse DDL
# --------------------------------------------------------------------------

_CREATE_RE = re.compile(
    r"CREATE\s+(?:UNLOGGED\s+)?TABLE\s+[^(]*\((?P<body>.*)\)\s*(?:PARTITION\s+BY[^;]*)?;",
    re.S | re.I,
)


def _split_top_level(body: str) -> list:
    out, depth, cur = [], 0, []
    for ch in body:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    if cur:
        out.append("".join(cur))
    return out


_TABLE_CONSTRAINTS = (
    "primary", "unique", "foreign", "check", "constraint", "exclude", "like",
)


def parse_create_table(ddl: str) -> list:
    """Tra ve [(ten_cot, kieu_du_lieu), ...] tu cau lenh CREATE TABLE."""
    m = _CREATE_RE.search(ddl)
    if not m:
        return []
    cols = []
    for part in _split_top_level(m.group("body")):
        part = part.strip()
        if not part:
            continue
        low = part.lower()
        if low.split(" ")[0].strip('"') in _TABLE_CONSTRAINTS:
            continue
        if part.startswith('"'):
            end = part.index('"', 1)
            name = part[1:end]
            rest = part[end + 1:].strip()
        else:
            sp = part.split(None, 1)
            name = sp[0]
            rest = sp[1] if len(sp) > 1 else ""
        # cat bo cac modifier phia sau kieu du lieu
        typ = re.split(
            r"\s+(?:NOT\s+NULL|NULL|DEFAULT|GENERATED|COLLATE|CONSTRAINT|PRIMARY|UNIQUE|REFERENCES|CHECK)\b",
            rest,
            maxsplit=1,
            flags=re.I,
        )[0].strip().rstrip(",")
        cols.append((name, typ))
    return cols


_COPY_RE = re.compile(r"COPY\s+\S+\s*\((?P<cols>.*?)\)\s+FROM\s+stdin", re.S | re.I)


def parse_copy_columns(copy_stmt: str) -> list:
    """Lay thu tu cot tu cau COPY - day moi la thu tu THUC TE trong khoi data."""
    if not copy_stmt:
        return []
    m = _COPY_RE.search(copy_stmt)
    if not m:
        return []
    out = []
    for c in m.group("cols").split(","):
        c = c.strip()
        if c.startswith('"') and c.endswith('"'):
            c = c[1:-1].replace('""', '"')
        if c:
            out.append(c)
    return out


# --------------------------------------------------------------------------
# Archive
# --------------------------------------------------------------------------


class PgDumpArchive:
    """Doc file pg_dump custom-format."""

    def __init__(self, path: str):
        self.path = path
        self._f = open(path, "rb")
        self.version = 0
        self.int_size = 4
        self.off_size = 8
        self.fmt = 1
        self.compression = COMPRESSION_GZIP
        self.created: Optional[datetime] = None
        self.dbname = ""
        self.server_version = ""
        self.pgdump_version = ""
        self.toc: list = []
        self.data_start = 0
        self._read_header()
        self._read_toc()
        self._tables = self._build_tables()

    # ---------------- primitives ----------------

    def _byte(self) -> int:
        b = self._f.read(1)
        if not b:
            raise EOFError("Het file khi doc byte")
        return b[0]

    def _int(self) -> int:
        sign = self._byte() if self.version > K_VERS_1_0 else 0
        raw = self._f.read(self.int_size)
        if len(raw) < self.int_size:
            raise EOFError("Het file khi doc int")
        res = 0
        for i in range(self.int_size):
            res |= raw[i] << (8 * i)
        return -res if sign else res

    def _str(self) -> Optional[str]:
        n = self._int()
        if n < 0:
            return None
        raw = self._f.read(n)
        return raw.decode("utf-8", "replace")

    def _offset(self):
        if self.version < K_VERS_1_7:
            return 2, self._int()
        flag = self._byte()
        raw = self._f.read(self.off_size)
        o = 0
        for i in range(self.off_size):
            o |= raw[i] << (8 * i)
        return flag, o

    # ---------------- header / toc ----------------

    def _read_header(self):
        if self._f.read(5) != MAGIC:
            raise ValueError(
                f"{self.path} khong phai pg_dump custom format (thieu magic PGDMP).\n"
                "Neu day la file .sql dang text thi nap thang bang psql, khong dung script nay."
            )
        vmaj, vmin = self._byte(), self._byte()
        vrev = self._byte() if (vmaj > 1 or (vmaj == 1 and vmin > 0)) else 0
        self.version = _mk(vmaj, vmin, vrev)
        self.version_str = f"{vmaj}.{vmin}.{vrev}"
        if self.version > K_VERS_MAX:
            print(
                f"[canh bao] archive version {self.version_str} moi hon muc da kiem thu (1.16). "
                "Neu parse loi, hay dung pg_restore.",
                file=sys.stderr,
            )
        self.int_size = self._byte()
        self.off_size = self._byte() if self.version >= K_VERS_1_7 else 4
        self.fmt = self._byte()
        if self.fmt != 1:
            raise ValueError(
                f"Chi ho tro custom format (1), file nay format={self.fmt}"
            )

        if self.version >= K_VERS_1_15:
            self.compression = self._byte()
        elif self.version >= K_VERS_1_2:
            lvl = self._byte() if self.version < K_VERS_1_4 else self._int()
            self.compression = COMPRESSION_GZIP if lvl != 0 else COMPRESSION_NONE
        else:
            self.compression = COMPRESSION_GZIP

        if self.version >= K_VERS_1_4:
            sec, mi, hr, mday, mon, year, _isdst = (self._int() for _ in range(7))
            try:
                self.created = datetime(1900 + year, mon + 1, mday, hr, mi, sec)
            except ValueError:
                self.created = None
            self.dbname = self._str() or ""
        if self.version >= K_VERS_1_10:
            self.server_version = self._str() or ""
            self.pgdump_version = self._str() or ""

    def _read_toc(self):
        n = self._int()
        for _ in range(n):
            e = TocEntry()
            e.dump_id = self._int()
            e.had_dumper = self._int()
            if self.version >= K_VERS_1_8:
                e.tableoid = self._str() or ""
            e.oid = self._str() or ""
            e.tag = self._str() or ""
            e.desc = self._str() or ""
            if self.version >= K_VERS_1_11:
                e.section = self._int()
            e.defn = self._str() or ""
            e.drop_stmt = self._str() or ""
            if self.version >= K_VERS_1_3:
                e.copy_stmt = self._str() or ""
            if self.version >= K_VERS_1_6:
                e.namespace = self._str() or ""
            if self.version >= K_VERS_1_10:
                e.tablespace = self._str() or ""
            if self.version >= K_VERS_1_14:
                e.tableam = self._str() or ""
            e.owner = self._str() or ""
            # pg_dump luon ghi chuoi "false" (truong withOids cu) - phai doc bo
            self._str()
            if self.version >= K_VERS_1_5:
                while True:
                    t = self._str()
                    if t is None:
                        break
                    try:
                        e.deps.append(int(t))
                    except ValueError:
                        pass
            e.data_state, e.data_pos = self._offset()
            self.toc.append(e)
        self.data_start = self._f.tell()

    def _build_tables(self) -> dict:
        data_by_id = {}
        for e in self.toc:
            if e.desc == "TABLE DATA":
                data_by_id[(e.namespace, e.tag)] = e

        tables = {}
        for e in self.toc:
            if e.desc != "TABLE":
                continue
            ddl_cols = parse_create_table(e.defn)
            data_e = data_by_id.get((e.namespace, e.tag))
            # thu tu cot THUC TE lay tu cau COPY
            copy_cols = parse_copy_columns(data_e.copy_stmt) if data_e else []
            typemap = dict(ddl_cols)
            if copy_cols:
                cols = [(c, typemap.get(c, "unknown")) for c in copy_cols]
            else:
                cols = ddl_cols
            tables[e.tag] = TableInfo(
                name=e.tag,
                namespace=e.namespace,
                columns=cols,
                ddl=e.defn,
                data_entry=data_e,
            )
        return tables

    # ---------------- public API ----------------

    @property
    def tables(self) -> dict:
        return self._tables

    def table_names(self) -> list:
        return list(self._tables.keys())

    def get_table(self, name: str) -> TableInfo:
        if name not in self._tables:
            raise KeyError(f"Khong co bang '{name}'. Co: {', '.join(self._tables)}")
        return self._tables[name]

    def iter_raw_lines(self, name: str) -> Iterator[str]:
        """Sinh tung dong text tho cua khoi COPY (chua tach cot)."""
        t = self.get_table(name)
        if not t.has_data:
            return
        e = t.data_entry
        if e.data_state != 2 or e.data_pos <= 0:
            raise RuntimeError(
                f"Bang {name} khong co offset du lieu (data_state={e.data_state}). "
                "Dump co the duoc tao qua pipe/stdout."
            )
        f = open(self.path, "rb")
        try:
            f.seek(e.data_pos)
            blk_type = f.read(1)[0]
            _dump_id = self._read_int_from(f)
            if blk_type != BLK_DATA:
                return
            dec = _Decompressor(self.compression)
            buf = b""
            while True:
                ln = self._read_int_from(f)
                if ln == 0:
                    break
                raw = f.read(ln)
                if len(raw) < ln:
                    raise EOFError(f"Doc thieu du lieu bang {name}")
                buf += dec.feed(raw)
                if b"\n" in buf:
                    *lines, buf = buf.split(b"\n")
                    for l in lines:
                        yield l.decode("utf-8", "replace")
            buf += dec.flush()
            for l in buf.split(b"\n"):
                if l:
                    yield l.decode("utf-8", "replace")
        finally:
            f.close()

    def _read_int_from(self, f) -> int:
        sign = f.read(1)
        if not sign:
            raise EOFError
        raw = f.read(self.int_size)
        res = 0
        for i in range(self.int_size):
            res |= raw[i] << (8 * i)
        return -res if sign[0] else res

    def iter_rows(self, name: str, decode: bool = True) -> Iterator[list]:
        """Sinh tung dong da tach cot. NULL -> None."""
        ncol = len(self.get_table(name).columns)
        for line in self.iter_raw_lines(name):
            if line == "\\." or line == "":
                continue
            fields = line.split("\t")
            if decode:
                fields = [unescape_copy_field(x) for x in fields]
            else:
                fields = [None if x == "\\N" else x for x in fields]
            if ncol and len(fields) != ncol:
                # dong hong -> bo qua nhung van dem duoc o tang tren
                if len(fields) < ncol:
                    fields += [None] * (ncol - len(fields))
                else:
                    fields = fields[:ncol]
            yield fields

    def count_rows(self, name: str) -> int:
        return sum(1 for _ in self.iter_raw_lines(name))

    # ---------------- summary ----------------

    def print_summary(self, file=sys.stdout):
        p = lambda *a: print(*a, file=file)
        p(f"File            : {self.path}")
        p(f"Archive version : {self.version_str}   (int={self.int_size}B, off={self.off_size}B)")
        p(f"Nen             : {COMPRESSION_NAMES.get(self.compression, self.compression)}")
        p(f"Database        : {self.dbname}")
        p(f"Server / pg_dump: {self.server_version} / {self.pgdump_version}")
        p(f"Tao luc         : {self.created}")
        p(f"So TOC entry    : {len(self.toc)}")
        p("")
        p(f"{'BANG':<24} {'#COT':>5}  {'DATA':>6}  DAI DIEN COT")
        p("-" * 100)
        for name, t in self._tables.items():
            sample = ", ".join(t.column_names[:4])
            p(f"{name:<24} {len(t.columns):>5}  {'co' if t.has_data else '-':>6}  {sample[:60]}")


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        print("Cach dung: python pgdump_reader.py <file_dump> [ten_bang]")
        return 1
    ar = PgDumpArchive(argv[1])
    if len(argv) >= 3:
        name = argv[2]
        t = ar.get_table(name)
        print(t.ddl)
        print("\n--- 5 dong dau ---")
        for i, row in enumerate(ar.iter_rows(name)):
            print(dict(zip(t.column_names, row)))
            if i >= 4:
                break
    else:
        ar.print_summary()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
