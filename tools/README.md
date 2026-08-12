# Tools — đọc & phân tích `db_fujiwara.sql`

`db_fujiwara.sql` **không phải file SQL text**. Nó là archive nhị phân định dạng
`pg_dump --format=custom` (magic `PGDMP`, archive v1.15, PostgreSQL 16.3, nén gzip).
Mở bằng editor hay chạy `psql -f` đều không được.

Ba script dưới đây đọc thẳng định dạng đó bằng Python thuần — **không cần cài
PostgreSQL, không cần `pg_restore`**.

## Cài đặt

```bash
pip install pandas numpy matplotlib tabulate
```

## 1. Xem nhanh cấu trúc

```bash
cd tools
python pgdump_reader.py ../db_fujiwara.sql              # liệt kê 19 bảng
python pgdump_reader.py ../db_fujiwara.sql His_131      # DDL + 5 dòng đầu
```

## 2. Xuất toàn bộ ra CSV

```bash
python export_to_csv.py ../db_fujiwara.sql -o ../data/csv --tz 7
```

Tuỳ chọn hay dùng:

| Cờ | Ý nghĩa |
|---|---|
| `-t His_131 -t Weather` | chỉ xuất vài bảng |
| `--tz 7` | thêm cột `ts_utc` + `ts_local` giải mã từ .NET ticks (VN = UTC+7) |
| `--no-time-col` | không thêm cột thời gian |
| `--sort-by-time` | sắp xếp theo timestamp (dữ liệu gốc **không** sắp xếp sẵn) |
| `--gzip` | nén đầu ra `.csv.gz` |
| `--limit 10000` | lấy N dòng đầu mỗi bảng để thử nhanh |
| `--list` | chỉ in cấu trúc rồi thoát |

Kết quả: `<outdir>/<Tên_bảng>.csv`, `_schema.json` (schema + kiểu PostgreSQL gốc),
`_manifest.csv` (số dòng/cột/dung lượng).

> **NULL được ghi thành ô trống, không phải 0** — đúng theo yêu cầu FR-04
> trong tài liệu mô tả ("dữ liệu trống phải trả về trạng thái thiếu dữ liệu,
> không được gán bằng 0"). pandas sẽ đọc thành `NaN`.

Toàn bộ 19 bảng ≈ **6,56 triệu dòng / 810 MB CSV / ~70 giây**.

## 3. Phân tích dataset

```bash
python analyze_dataset.py ../data/csv -o ../data/report --tz 7 --plots
```

Sinh ra:

- `analysis_report.md` — báo cáo tổng hợp, đọc file này trước
- `column_profile.csv` — thống kê từng cột: `%null`, `%zero`, `%negative`,
  min/p1/p50/p99/max, mean, std, số giá trị duy nhất, cờ hằng số, vai trò vật lý
- `time_profile.csv` — trục thời gian từng bảng: phạm vi, bước mẫu danh định,
  `%` mẫu đúng bước, độ phủ, số gap, gap lớn nhất, timestamp trùng
- `plots/*_diurnal.png` — profile trung bình theo giờ trong ngày

Báo cáo tự kiểm chứng vật lý:

- **Múi giờ**: bức xạ phải đỉnh lúc 11–13h giờ địa phương, nếu lệch → cảnh báo
- **Ban đêm**: bức xạ trung bình 0–4h phải ≈ 0, nếu > 5 W/m² → cảm biến lệch zero
- **Ngưỡng vật lý**: GHI > 1400 W/m² → cảnh báo
- **Đột biến**: `max > 100 × p99` → giá trị rác cần lọc
- **Tương quan**: Pearson giữa cột bức xạ và cột công suất (PV thường > 0,9)

## Ghi chú kỹ thuật

**`UTCTimestamp_Ticks` là .NET DateTime ticks** — số đơn vị 100 ns kể từ
`0001-01-01 00:00:00`. Công thức:

```python
datetime(1, 1, 1) + timedelta(microseconds=ticks // 10)
```

Đã kiểm chứng: cộng +7h thì bức xạ đỉnh đúng 12h trưa → ticks lưu theo **UTC**.

**Dữ liệu trong dump không sắp xếp theo thời gian.** Cột `ID` cũng không đồng biến
theo `UTCTimestamp_Ticks` (historian rollover). Luôn `sort_values("ts_utc")`
trước khi tính chuỗi thời gian, lag feature hay resample.

**Hai bảng rỗng**: `Annotations` (0 dòng) và `CMB` (0 dòng, 1602 cột).

## Nếu vẫn muốn nạp vào PostgreSQL thật

```bash
createdb MEAS
pg_restore -d MEAS --no-owner --no-privileges db_fujiwara.sql
```
