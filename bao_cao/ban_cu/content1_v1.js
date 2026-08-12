// content1.js — Chương 1 đến 6
const L = require('./lib');
const { P, H, run, code, bullets, table, tblTitle, figure, codeBlock, callout,
        pageBreak, hr, fmt, int, CW, RED, ORANGE, GREEN, NAVY, D } = L;
const { AlignmentType } = D;
const C = AlignmentType.CENTER, R = AlignmentType.RIGHT;

// đổi chuỗi thời gian sang giờ Việt Nam (+7)
const vn = (s, keepMs) => {
  const d = new Date(s.replace(' ', 'T') + 'Z');
  d.setUTCHours(d.getUTCHours() + 7);
  const t = d.toISOString().replace('T', ' ');
  return keepMs ? t.slice(0, 23) : t.slice(0, 19);
};
const vnDate = s => vn(s).slice(0, 10).split('-').reverse().join('/');

module.exports = function (J, FIG) {
  const T = J.time;
  const tab = n => T.find(x => x.table === n);
  const h131 = tab('His_131'), hw = tab('Weather'), hr5 = tab('His_report');
  const o = [];

  // ======================= 1. TÓM TẮT =======================
  o.push(H('1. Tóm tắt kết quả khảo sát', 1));

  o.push(P([run('Báo cáo này trình bày kết quả khảo sát tệp dữ liệu '),
    code('db_fujiwara.sql'), run(' do chủ đầu tư cung cấp, nhằm xác định dữ liệu hiện có đáp ứng được đến đâu cho việc xây dựng mô hình dự báo công suất phát của nhà máy điện mặt trời. Toàn bộ kết luận trong báo cáo đều dẫn từ số liệu tính trực tiếp trên tệp, kèm phép kiểm chứng nêu ở Phụ lục E.')]));

  o.push(H('1.1. Kết luận chính', 2));
  o.push(callout('Dữ liệu đủ điều kiện để xây dựng mô hình dự báo 1 ngày tới (FC-02).', [
    'Chuỗi công suất tại điểm đấu nối liên tục 370 ngày, độ phân giải 60 giây, độ phủ 98,0%. Sau khi sắp xếp lại theo thời gian, trục thời gian đều đặn với chỉ 23 khoảng gián đoạn trên 10 phút trong cả năm.',
    [run('Tương quan giữa bức xạ đo tại nhà máy và công suất phát đạt '), run('r = 0,960', { bold: true }), run(' — tín hiệu vật lý rõ ràng, đủ để mô hình học được quan hệ đầu vào–đầu ra.')],
    'Không phát hiện dấu hiệu cắt giảm công suất theo lệnh điều độ, nên công suất đo được phản ánh đúng khả năng phát thực tế của nhà máy.',
  ], GREEN));

  o.push(P(' ', { after: 60 }));
  o.push(callout('Bốn vấn đề phải xử lý trước khi đưa dữ liệu vào huấn luyện.', [
    [run('1. Dữ liệu không sắp xếp theo thời gian. ', { bold: true }), run('Riêng bảng His_131 có 5.108 điểm mà timestamp của dòng sau nhỏ hơn dòng trước. Mọi luồng nạp phải sắp xếp trước khi xử lý. Chi tiết ở mục 4.3.')],
    [run('2. Tồn tại giá trị rác biên độ lớn. ', { bold: true }), run('Lớn nhất là 4.410.466 MW ở một lộ 22 kV, trong khi phân vị 99 của chính cột đó chỉ là 6,14 MW.')],
    [run('3. Giá trị 0 ban ngày là mất tín hiệu, không phải số đo. ', { bold: true }), run('Các ngăn lộ 22 kV có 58–60% số mẫu bằng 0 toàn chuỗi nhưng chỉ 0,3–0,7% khi trời nắng rõ. Quy tắc xử lý đã chốt ở mục 7.6.')],
    [run('4. Cột Data_PR không phải hệ số hiệu suất thật. ', { bold: true }), run('SCADA báo 98,4% trong khi giá trị đúng theo định nghĩa là 75,1%. Không được dùng làm biến đầu vào hay chỉ số vận hành. Chi tiết ở mục 8.4.')],
  ], ORANGE));

  o.push(H('1.2. Số liệu tổng quan', 2));
  o.push(table(
    ['Hạng mục', 'Giá trị'],
    [
      ['Tên cơ sở dữ liệu', 'MEAS (PostgreSQL 16.3)'],
      ['Thời điểm tạo bản sao lưu', '17/07/2026 (giờ Việt Nam)'],
      ['Kích thước tệp', '152.426.713 byte (145 MB)'],
      ['Số bảng', '19 (trong đó 2 bảng rỗng)'],
      ['Tổng số bản ghi', int(J.meta.total_rows)],
      ['Phạm vi thời gian', '12/07/2025 → 17/07/2026'],
      ['Độ dài chuỗi', '370 ngày'],
      ['Độ phân giải gốc', '60 giây (16 bảng) / 300 giây (1 bảng)'],
      ['Toạ độ nhà máy', '13,8634° N — 109,2708° E'],
      ['Công suất lắp đặt một chiều', '50 MWp'],
      ['Công suất định mức xoay chiều', '≈ 40 MW'],
      ['Công suất lớn nhất quan sát', '39,27 MW'],
    ],
    [3400, 6238], { align: [null, null] }));

  o.push(H('1.3. Việc cần làm', 2));
  o.push(table(
    ['#', 'Việc', 'Mức độ', 'Nêu tại'],
    [
      ['1', 'Xác định nguồn dữ liệu dự báo thời tiết', 'Bắt buộc', '9.1'],
      ['2', 'Dùng bộ ba (nhà máy, thời điểm, biến) làm khoá bản ghi', 'Bắt buộc', '11.1'],
      ['3', 'Xây bộ lọc giá trị đột biến và ngưỡng vật lý', 'Bắt buộc', '10.4'],
      ['4', 'Đánh dấu thiếu cho giá trị 0 xuất hiện ban ngày', 'Bắt buộc', '7.6'],
      ['5', 'Loại cột Data_PR, tính lại theo đúng định nghĩa', 'Bắt buộc', '8.4'],
      ['6', 'Xác nhận chính sách lưu trữ của historian tại nhà máy', 'Nên làm sớm', '11.1'],
      ['7', 'Hiệu chỉnh lệch điểm không của cảm biến bức xạ Rad_2', 'Nên làm', '7.6'],
      ['8', 'Đối chiếu sơ đồ một sợi để xác nhận cấu trúc đo', 'Nên làm', '11.2'],
    ],
    [500, 5300, 1738, 2100], { align: [C, null, C, C] }));

  o.push(pageBreak());

  // ======================= 2. PHƯƠNG PHÁP =======================
  o.push(H('2. Mục tiêu, phạm vi và phương pháp', 1));

  o.push(H('2.1. Câu hỏi cần trả lời', 2));
  o.push(P('Khảo sát được thực hiện để trả lời sáu câu hỏi sau, theo đúng thứ tự này:'));
  o.push(...bullets([
    'Dữ liệu gồm những gì, cấu trúc ra sao, đọc bằng cách nào.',
    'Trục thời gian có liên tục và đều đặn không, độ phân giải thực tế là bao nhiêu.',
    'Cột nào là biến mục tiêu của bài toán dự báo.',
    'Dữ liệu khí tượng có đủ và đáng tin không.',
    'Chất lượng dữ liệu ở mức nào, phải xử lý những gì.',
    'Còn thiếu dữ liệu gì so với nhu cầu của mô hình.',
  ]));

  o.push(H('2.2. Nguồn dữ liệu và đường đi của dữ liệu', 2));
  o.push(P([run('Tệp khảo sát tên '), code('db_fujiwara.sql'),
    run('. Phần mở rộng gợi ý đây là tệp lệnh SQL dạng văn bản, nhưng kiểm tra byte đầu tệp cho thấy không phải như vậy — chi tiết ở mục 3.1. Nội dung là cơ sở dữ liệu '),
    code('MEAS'), run(' của hệ thống historian tại nhà máy, chụp tại thời điểm 17/07/2026.')]));
  o.push(P('Đường đi của dữ liệu, cần ghi rõ vì ảnh hưởng đến cách diễn giải một số đặc tính:'));
  o.push(table(
    ['Bước', 'Nội dung'],
    [['1', 'Cơ sở dữ liệu historian đang vận hành tại nhà máy Fujiwara'],
     ['2', 'Kỹ sư của đơn vị truy cập và trích xuất dữ liệu để thử nghiệm'],
     ['3', 'Bản trích xuất được đóng gói thành tệp db_fujiwara.sql'],
     ['4', 'Khảo sát trong báo cáo này thực hiện trên tệp ở bước 3']],
    [900, 8738], { align: [C, null] }));
  o.push(P([run('Vì có bước trung gian, một số đặc tính quan sát được có thể do bước trích xuất tạo ra chứ không phản ánh cơ sở dữ liệu gốc. Báo cáo nêu rõ ở từng chỗ khi điều này có khả năng xảy ra, cụ thể là mục 4.3 về thứ tự lưu trữ.')]));
  o.push(P([run('Điểm thuận lợi: kỹ sư của đơn vị '), run('truy cập được cơ sở dữ liệu nhà máy bất cứ lúc nào', { bold: true }),
    run('. Nhờ vậy nhiều câu hỏi còn treo trong báo cáo có thể tự kiểm chứng mà không phải chờ bên ngoài trả lời.')]));

  o.push(H('2.3. Quy trình khảo sát', 2));
  o.push(P('Khảo sát tiến hành theo ba bước tách bạch, mỗi bước sinh ra kết quả trung gian kiểm tra được:'));
  o.push(table(
    ['Bước', 'Nội dung', 'Công cụ', 'Kết quả'],
    [
      ['1', 'Giải mã định dạng lưu trữ, đọc lược đồ và khối dữ liệu', 'pgdump_reader.py', 'Danh mục bảng, DDL, số bản ghi'],
      ['2', 'Trích xuất toàn bộ dữ liệu ra dạng bảng phẳng', 'export_to_csv.py', '19 tệp CSV, lược đồ JSON'],
      ['3', 'Lập hồ sơ thống kê và kiểm chứng vật lý', 'analyze_dataset.py', 'Hồ sơ cột, hồ sơ thời gian, biểu đồ'],
    ],
    [640, 3600, 2200, 3198], { align: [C, null, null, null] }));

  o.push(P([run('Bộ công cụ được viết riêng cho khảo sát này bằng Python thuần, không phụ thuộc vào việc cài đặt PostgreSQL. Lý do và cách chạy lại nêu ở Phụ lục D. Thời gian chạy toàn bộ ba bước trên máy thông thường khoảng 100 giây.')]));

  o.push(H('2.4. Nguyên tắc áp dụng', 2));
  o.push(...bullets([
    [run('Mọi kết luận phải kiểm chứng được. ', { bold: true }), run('Không suy đoán từ tên cột. Ví dụ, cột Data_PR có tên gợi ý là hệ số hiệu suất nhưng kiểm tra bằng số liệu cho thấy không phải (mục 8.4).')],
    [run('Giá trị trống giữ nguyên trạng thái trống. ', { bold: true }), run('Trong toàn bộ quá trình trích xuất, giá trị NULL được ghi thành ô rỗng, không thay bằng 0. Đây là yêu cầu bắt buộc của FR-04.')],
    [run('Không sửa dữ liệu nguồn. ', { bold: true }), run('Tệp gốc chỉ được mở ở chế độ chỉ đọc.')],
  ]));

  o.push(H('2.5. Giới hạn của khảo sát', 2));
  o.push(P('Những điểm sau nằm ngoài phạm vi khảo sát và cần được bổ sung trước khi kết luận cuối cùng:'));
  o.push(...bullets([
    'Chỉ khảo sát một bản chụp tại một thời điểm, và bản chụp đó đi qua một bước trích xuất trung gian (mục 2.2). Không quan sát được hành vi ghi dữ liệu theo thời gian thực của historian.',
    'Không có tài liệu mô tả danh mục điểm đo của hệ thống SCADA. Ý nghĩa của từng thẻ đo được suy ra từ tên và từ đặc tính thống kê.',
    'Không có sơ đồ một sợi của nhà máy. Sơ đồ đo lường ở Hình 5.1 là kết quả suy luận từ dữ liệu, cần đối chiếu lại.',
    'Không có sổ nhật ký vận hành, nên chưa phân biệt được khoảng thiếu dữ liệu do sự cố thu thập với khoảng ngừng phát theo kế hoạch.',
    'Chưa biết chính sách lưu trữ của historian tại nhà máy. Chuỗi dài 370 ngày có thể là toàn bộ dữ liệu hiện có, cũng có thể chỉ là phạm vi mà bước trích xuất lấy ra.',
    'Chưa có góc nghiêng, phương vị dàn pin và số bộ nghịch lưu.',
  ]));

  o.push(pageBreak());

  // ======================= 3. MÔ TẢ NGUỒN =======================
  o.push(H('3. Mô tả kỹ thuật nguồn dữ liệu', 1));

  o.push(H('3.1. Định dạng thực tế của tệp', 2));
  o.push(P([run('Năm byte đầu tệp là '), code('PGDMP'), run('. Đây là chuỗi nhận dạng của định dạng lưu trữ nhị phân do công cụ '),
    code('pg_dump --format=custom'), run(' sinh ra, không phải tệp lệnh SQL dạng văn bản. Hệ quả thực tế:')]));
  o.push(...bullets([
    'Mở bằng trình soạn thảo văn bản chỉ thấy phần khai báo lược đồ; toàn bộ dữ liệu nằm trong các khối đã nén.',
    [run('Không nạp được bằng '), code('psql -f'), run('. Phải dùng '), code('pg_restore'), run(' hoặc công cụ đọc riêng.')],
  ]));
  o.push(P('Thông số phần đầu tệp đọc được:'));
  o.push(table(
    ['Trường', 'Giá trị', 'Ý nghĩa'],
    [
      ['Chuỗi nhận dạng', 'PGDMP', 'Bản lưu định dạng riêng của PostgreSQL'],
      ['Phiên bản định dạng', '1.15.0', 'Tương ứng PostgreSQL 16'],
      ['Kích thước số nguyên / con trỏ', '4 byte / 8 byte', 'Bản lưu tạo trên hệ 64 bit'],
      ['Thuật toán nén', 'gzip', 'Từng khối dữ liệu nén độc lập'],
      ['Phiên bản máy chủ', '16.3', 'Máy chủ nguồn'],
      ['Tên cơ sở dữ liệu', 'MEAS', 'Viết tắt của Measurement'],
      ['Thời điểm tạo', '17/07/2026', 'Thời điểm chụp dữ liệu'],
    ],
    [2600, 2600, 4438]));

  o.push(callout('Ảnh hưởng đến thiết kế FR-02', [
    'Yêu cầu FR-02 quy định hệ thống phải kết nối được với cơ sở dữ liệu lịch sử của SCADA. Bản lưu này chỉ là ảnh chụp một thời điểm, không phải kênh kết nối. Khi triển khai thật, phần mềm sẽ kết nối trực tiếp tới máy chủ PostgreSQL 16 của nhà máy chứ không đọc tệp lưu. Bản lưu chỉ dùng cho giai đoạn khảo sát và huấn luyện ban đầu.',
  ], NAVY));

  o.push(H('3.2. Danh mục bảng', 2));
  o.push(P('Cơ sở dữ liệu gồm 19 bảng. Phân theo chức năng:'));
  o.push(tblTitle('Bảng 3.1 — Danh mục bảng và vai trò'));
  o.push(table(
    ['Bảng', 'Số cột', 'Số bản ghi', 'Vai trò'],
    [
      ['His_131', '18', int(h131.rows), 'Đo tại ngăn lộ 110 kV — điểm đấu nối lưới'],
      ['His_431', '18', int(tab('His_431').rows), 'Đo tại ngăn lộ tổng 22 kV'],
      ['His_431A', '9', int(tab('His_431A').rows), 'Lộ 22 kV số 1'],
      ['His_432 … His_437', '9', '247.714 – 256.360', 'Lộ 22 kV số 2 đến số 7'],
      ['His_471, 473, 475, 477', '15', '519.127 – 519.225', 'Bốn lộ 22 kV, đo đầy đủ hơn'],
      ['His_T1', '9', int(tab('His_T1').rows), 'Máy biến áp T1 — nhiệt độ, nấc phân áp'],
      ['His_TUC41', '8', int(tab('His_TUC41').rows), 'Đo điện áp và tần số thanh cái 22 kV'],
      ['His_report', '69', int(hr5.rows), 'Bảng gộp: điện + khí tượng, chu kỳ 5 phút'],
      ['Weather', '32', int(hw.rows), 'Trạm khí tượng, chu kỳ 1 phút'],
      ['Annotations', '26', '0', 'Ghi chú người vận hành — rỗng'],
      ['CMB', '1602', '0', 'Hộp gom dây một chiều — rỗng'],
    ],
    [1900, 900, 1500, 5338], { align: [null, C, R, null], redRows: [9, 10] }));

  o.push(P([run('Hai bảng '), code('Annotations'), run(' và '), code('CMB'),
    run(' tồn tại về cấu trúc nhưng không chứa bản ghi nào. Đáng chú ý là '), code('CMB'),
    run(' có 1.602 cột, mỗi cột ứng với một điểm đo tại hộp gom dây phía một chiều — nhiệt độ và dòng điện của 20 hộp gom thuộc 7 khối. Nếu bảng này được thu thập, nó sẽ cho phép phát hiện suy giảm hiệu suất ở mức chuỗi tấm pin. Hiện tại thì không.')]));

  o.push(H('3.3. Cấu trúc chung của bảng historian', 2));
  o.push(P('Mười bảy bảng có dữ liệu đều theo cùng một khuôn. Bốn cột đầu giống nhau, các cột sau là điểm đo:'));
  o.push(codeBlock([
    'CREATE TABLE public."His_131" (',
    '    "ID"                  bigint    NOT NULL,   -- định danh nội bộ, không dùng',
    '    "UTCTimestamp_Ticks"  bigint    NOT NULL,   -- mốc thời gian .NET',
    '    "LogType"             smallint,             -- loại bản ghi',
    '    "NotSync"             smallint  NOT NULL,   -- cờ chưa đồng bộ',
    '    "Substation_Level_110kV_Bay131_MEAS_P"   real,  -- công suất tác dụng',
    '    "Substation_Level_110kV_Bay131_MEAS_Q"   real,  -- công suất phản kháng',
    '    "Substation_Level_110kV_Bay131_MEAS_PF"  real,  -- hệ số công suất',
    '    "Substation_Level_110kV_Bay131_MEAS_Ia"  real,  -- dòng điện pha A',
    '    ...',
    ');',
  ]));
  o.push(P([run('Quy ước đặt tên điểm đo có cấu trúc rõ ràng: '),
    code('<Cấp>_<Cấp điện áp>_<Ngăn lộ>_<Nhóm>_<Đại lượng>'),
    run('. Quy ước này ổn định trên toàn bộ dữ liệu, nên có thể tách tự động thành các trường có nghĩa khi xây bảng ánh xạ ở mục 10.2.')]));
  o.push(P([run('Mọi điểm đo đều có kiểu '), code('real'),
    run(' — số thực dấu chấm động 4 byte, độ chính xác khoảng 6 chữ số. Đủ cho đại lượng đo lường, nhưng cần lưu ý khi cộng dồn nhiều giá trị: sai số tích luỹ có thể thấy được. Khi chuẩn hoá nên chuyển sang '),
    code('double precision'), run('.')]));

  o.push(H('3.4. Quy ước thời gian', 2));
  o.push(P([run('Cột '), code('UTCTimestamp_Ticks'), run(' là số nguyên 64 bit với giá trị điển hình khoảng 6,39 × 10'),
    run('17', { size: 14 }), run('. Đây là mốc thời gian theo quy ước .NET: số đơn vị 100 nano giây tính từ 00:00:00 ngày 01/01/0001.')]));
  o.push(P([run('Nhà máy đặt tại Việt Nam nên múi giờ là '), run('GMT+7', { bold: true }),
    run('. Giá trị lưu trong cột là giờ chuẩn quốc tế, cộng 7 giờ để ra giờ Việt Nam. Công thức chuyển đổi:')]));
  o.push(codeBlock([
    'from datetime import datetime, timedelta',
    '',
    'def ticks_to_gio_vn(ticks: int) -> datetime:',
    '    return datetime(1, 1, 1) + timedelta(microseconds=ticks // 10, hours=7)',
    '',
    '# 639198520288920000  ->  17/07/2026 09:27:08.892  giờ Việt Nam',
  ]));
  o.push(P([run('Toàn bộ thời điểm nêu trong báo cáo này đều đã quy đổi sang '),
    run('giờ Việt Nam', { bold: true }),
    run('. Riêng lược đồ dữ liệu đích ở mục 10.1 vẫn lưu theo giờ chuẩn quốc tế và hiển thị theo múi giờ nhà máy, đúng yêu cầu FR-01.')]));

  o.push(pageBreak());

  // ======================= 4. TRỤC THỜI GIAN =======================
  o.push(H('4. Khảo sát trục thời gian', 1));

  o.push(H('4.1. Phạm vi và độ phân giải', 2));
  o.push(P('Bảng dưới tổng hợp trục thời gian của cả 17 bảng có dữ liệu. Cột "bước mẫu" là khoảng cách xuất hiện nhiều nhất giữa hai mẫu liên tiếp; cột "đúng bước" là tỷ lệ số mẫu cách nhau đúng bằng bước đó.'));
  o.push(tblTitle('Bảng 4.1 — Trục thời gian theo bảng (giờ Việt Nam)'));
  o.push(table(
    ['Bảng', 'Bản ghi', 'Bắt đầu', 'Kết thúc', 'Số ngày', 'Bước mẫu', 'Đúng bước', 'Độ phủ'],
    T.map(t => [t.table, int(t.rows), vnDate(t.t0),
      vnDate(t.t1), fmt(t.span_days, 1),
      t.nominal_s + ' s', fmt(t.pct_nominal, 1) + '%', fmt(t.coverage, 1) + '%']),
    [1450, 1120, 1080, 1080, 900, 1000, 1150, 1858],
    { align: [null, R, C, C, R, C, R, R], size: 15, headSize: 15,
      redRows: T.map((t, i) => t.coverage < 60 ? i : -1).filter(i => i >= 0) }));

  o.push(P([run('Mười sáu bảng ghi ở chu kỳ 60 giây. Riêng '), code('His_report'),
    run(' ghi ở chu kỳ 300 giây. Đây là bảng gộp sẵn, do một tác vụ định kỳ của SCADA sinh ra chứ không phải luồng thu thập trực tiếp.')]));
  o.push(P([run('Độ phủ của '), code('His_report'), run(' hiện 101,2%, vượt trên 100%. Nguyên nhân là công thức tính lấy bước mẫu phổ biến nhất làm mẫu số, trong khi bảng này có một phần nhỏ số mẫu ghi dày hơn 300 giây. Không phải lỗi dữ liệu.')]));
  o.push(...figure(FIG + '/h44_hist.png', 480, 'Hình 4.1 — Phân bố khoảng cách giữa hai mẫu liên tiếp, bảng His_131'));

  o.push(H('4.2. Độ phủ và khoảng gián đoạn', 2));
  o.push(P('Độ phủ chia làm hai nhóm rõ rệt. Nhóm thứ nhất gồm chín bảng đạt trên 95%. Nhóm thứ hai gồm bảy lộ 22 kV từ 431A đến 437, chỉ đạt 46–48%.'));
  o.push(...figure(FIG + '/h42_cov.png', 470, 'Hình 4.2 — Độ phủ dữ liệu theo bảng'));

  o.push(tblTitle('Bảng 4.2 — Khoảng gián đoạn dữ liệu'));
  o.push(table(
    ['Bảng', 'Số khoảng gián đoạn', 'Tổng thời gian mất (giờ)', 'Khoảng dài nhất (giờ)'],
    T.filter(t => t.n_gap > 0).sort((a, b) => b.gap_h - a.gap_h).slice(0, 10)
      .map(t => [t.table, int(t.n_gap), fmt(t.gap_h, 1), fmt(t.maxgap_h, 1)]),
    [2400, 2400, 2500, 2338], { align: [null, R, R, R],
      redRows: [0, 1, 2, 3, 4, 5, 6] }));

  o.push(P('Bảy lộ 431A–437 mỗi lộ mất từ 4.500 đến 4.900 giờ, tức khoảng 190–200 ngày trên tổng số 370 ngày. Khoảng gián đoạn dài nhất lên tới 262 giờ liên tục, tương đương gần 11 ngày. Mức mất mát này khiến nhóm bảng đó không dùng được làm chuỗi liên tục, chỉ dùng được cho mục đích đối chiếu rời rạc.'));
  o.push(P([run('Ngược lại, bảng biến mục tiêu '), code('His_131'),
    run(' chỉ mất tổng cộng 182,2 giờ trên 370 ngày, tương đương 2,0%, phân bố trong 70 khoảng. Đây là mức chấp nhận được cho bài toán dự báo.')]));
  o.push(...figure(FIG + '/h43_heat.png', 470, 'Hình 4.3 — Bản đồ sẵn có dữ liệu theo ngày và giờ, ba bảng đại diện'));
  o.push(P('Trên bản đồ này, mỗi cột là một ngày, mỗi hàng là một giờ trong ngày, màu càng đỏ thì càng thiếu mẫu. Điểm cần chú ý: các vệt thiếu ở His_131 và Weather chạy theo cột, tức là mất cả ngày chứ không mất theo giờ nhất định. Điều này cho thấy nguyên nhân là gián đoạn thu thập chứ không phải quy luật vận hành.'));

  o.push(H('4.3. Thứ tự lưu trữ', 2));
  o.push(P('Đây là phát hiện có ảnh hưởng lớn nhất tới việc xử lý dữ liệu. Trong tệp gốc, thứ tự các bản ghi không theo thời gian.'));
  o.push(tblTitle('Bảng 4.3 — Mức độ đảo lộn thứ tự thời gian'));
  o.push(table(
    ['Bảng', 'Số cột', 'Số điểm timestamp giảm', 'Chu kỳ lặp (số dòng)', 'Số lần lặp'],
    [['His_131', '18', int(h131.n_back), int(h131.block), int(h131.block_n)],
     ['His_431', '18', int(tab('His_431').n_back), int(tab('His_431').block), int(tab('His_431').block_n)],
     ['Weather', '32', int(hw.n_back), int(hw.block), int(hw.block_n)],
     ['His_471', '15', int(tab('His_471').n_back), int(tab('His_471').block), int(tab('His_471').block_n)],
     ['His_report', '69', int(hr5.n_back), int(hr5.block), int(hr5.block_n)]],
    [1900, 1200, 2400, 2300, 1838], { align: [null, C, R, C, R] }));

  o.push(P('Các điểm đảo lộn không rải ngẫu nhiên mà lặp theo chu kỳ cố định. Chu kỳ này phụ thuộc vào số cột của bảng: bảng 18 cột lặp mỗi 72 dòng, bảng 15 cột lặp mỗi 84 dòng, bảng 69 cột lặp mỗi 25 dòng. Quy luật rất rõ — số dòng trong một chu kỳ tỷ lệ nghịch với độ rộng bản ghi.'));
  o.push(P([run('Giải thích phần cơ chế: PostgreSQL lưu dữ liệu theo trang 8.192 byte. Một bản ghi 18 cột kiểu '),
    code('real'), run(' cộng phần đầu chiếm khoảng 110 byte, nên mỗi trang chứa khoảng 72 bản ghi. Thứ tự các bản ghi trong bản lưu chính là thứ tự vật lý trên đĩa, và ranh giới các đoạn đảo lộn trùng khớp với ranh giới trang. Vì sao các trang lại chứa dữ liệu thuộc những vùng thời gian cách xa nhau thì chưa xác định được — có thể do cách ghi của historian, cũng có thể phát sinh ở bước trích xuất trung gian.')]));
  o.push(P([run('Điểm này không cần làm rõ để triển khai: dù nguyên nhân là gì, '),
    run('mọi luồng nạp đều phải sắp xếp theo thời gian trước khi xử lý', { bold: true }),
    run('. Quy tắc đó an toàn trong cả hai trường hợp.')]));

  o.push(H('4.4. Kết quả sau khi sắp xếp', 2));
  o.push(...figure(FIG + '/h41_sort.png', 500, 'Hình 4.4 — Trục thời gian bảng His_131 trước và sau khi sắp xếp'));
  o.push(P([run('Sau khi sắp xếp theo '), code('UTCTimestamp_Ticks'), run(', trục thời gian trở nên đều đặn:')]));
  o.push(table(
    ['Chỉ số', 'Giá trị'],
    [['Số điểm timestamp giảm còn lại', '0'],
     ['Bước mẫu, phân vị 50', fmt(J.after_sort.p50, 3) + ' giây'],
     ['Bước mẫu, phân vị 95', fmt(J.after_sort.p95, 3) + ' giây'],
     ['Bước mẫu, phân vị 99', fmt(J.after_sort.p99, 3) + ' giây'],
     ['Số khoảng gián đoạn trên 10 phút', int(J.after_sort.gap10m) + ' trên 370 ngày'],
     ['Mẫu đầu tiên', vn(J.after_sort.t0, true)],
     ['Mẫu cuối cùng', vn(J.after_sort.t1, true)]],
    [4600, 5038], { align: [null, R] }));
  o.push(P('Phân vị 95 và 99 đều xấp xỉ 60 giây, nghĩa là hầu như không có mẫu nào lệch bước đáng kể. Chuỗi này đủ điều kiện để lấy trung bình lên độ phân giải 15 phút phục vụ FC-02.'));

  o.push(H('4.5. Mốc thời gian trùng lặp', 2));
  o.push(P([run('Chỉ phát hiện 3 bản ghi trùng mốc thời gian, đều ở bảng '), code('His_TUC41'),
    run(' — bảng đo điện áp thanh cái, không dùng cho mô hình. Mười sáu bảng còn lại không có mốc trùng nào. Tỷ lệ trùng trên toàn bộ 6,56 triệu bản ghi là 0,00005%, không cần xử lý đặc biệt ngoài một bước khử trùng phòng ngừa.')]));

  o.push(pageBreak());

  // ======================= 5. CẤU TRÚC ĐIỆN =======================
  o.push(H('5. Cấu trúc đo lường và biến mục tiêu', 1));

  o.push(H('5.1. Sơ đồ suy ra từ dữ liệu', 2));
  o.push(P('Không có sơ đồ một sợi kèm theo. Cấu trúc dưới đây suy ra từ tên ngăn lộ, cấp điện áp trong tên điểm đo, và quan hệ định lượng giữa các phép đo.'));
  o.push(...figure(FIG + '/h51_topo.png', 500, 'Hình 5.1 — Sơ đồ đo lường suy ra từ dữ liệu'));

  o.push(H('5.2. Đối chiếu ba lớp đo độc lập', 2));
  o.push(P([run('So sánh được thực hiện trên '), run(int(J.n_day_samples), { bold: true }),
    run(' mẫu ban ngày (9–14 giờ địa phương), sau khi đồng bộ các bảng về lưới thời gian 1 phút. Đơn vị MW.')]));
  o.push(tblTitle('Bảng 5.1 — Đối chiếu các lớp đo công suất'));
  o.push(table(
    ['Vị trí đo', 'Số mẫu', 'Trung bình', 'Lớn nhất', 'Hệ số tương quan với Bay131', 'Sai lệch trung bình'],
    J.topology.map(t => [t.label, int(t.n), fmt(t.mean), fmt(t.max),
      t.r === 1 ? '—' : fmt(t.r, 4), t.bias === 0 ? '—' : (t.bias > 0 ? '+' : '') + fmt(t.bias, 3)]),
    [2600, 1200, 1300, 1200, 1900, 1438], { align: [null, R, R, R, C, R], size: 16 }));

  o.push(P('Ba cách đo hoàn toàn độc lập về mặt thiết bị đều cho cùng một con số quanh 22,4 MW, với hệ số tương quan trên 0,998. Đây là bằng chứng mạnh rằng dữ liệu công suất nhất quán và không có lỗi hệ thống về thang đo hay đơn vị.'));
  o.push(P('Điểm chưa giải thích được: cả hai nhóm lộ 22 kV đều cộng lại bằng tổng công suất nhà máy. Nếu chúng là các lộ song song thuộc cùng một thanh cái thì tổng của mỗi nhóm phải bằng một nửa. Khả năng cao là hai nhóm đo ở hai lớp khác nhau của cùng một dòng công suất. Cần đối chiếu sơ đồ một sợi để xác nhận — nêu ở mục 11.2.'));

  o.push(tblTitle('Bảng 5.2 — Công suất từng lộ 22 kV, ban ngày'));
  o.push(table(
    ['Lộ', 'Trung bình (MW)', 'Lớn nhất (MW)', 'Nhóm', 'Độ phủ'],
    J.feeders.map(f => {
      const t = tab('His_' + f.bay);
      return [f.bay, fmt(f.mean), fmt(f.max), f.bay.startsWith('4') && +f.bay.replace('A', '') < 470 ? 'Nhóm A' : 'Nhóm B',
        t ? fmt(t.coverage, 1) + '%' : '—'];
    }),
    [1500, 2200, 2200, 1800, 1938], { align: [C, R, R, C, R] }));
  o.push(P([run('Giá trị lớn nhất 100,00 MW của lộ 431A trong bảng trên là kết quả đã cắt ngưỡng. Giá trị thô là 4.410.466 MW — xem mục 7.3.')]));

  o.push(H('5.3. Lựa chọn biến mục tiêu', 2));
  o.push(callout('Biến mục tiêu của bài toán dự báo', [
    [code('His_131.Substation_Level_110kV_Bay131_MEAS_P')],
    'Đây là công suất tác dụng đo tại ngăn lộ 110 kV, tức điểm đấu nối với lưới truyền tải.',
  ], GREEN));
  o.push(P('Bốn lý do chọn cột này:'));
  o.push(...bullets([
    'Đây là công suất thực sự giao lên lưới, đã trừ tổn thất máy biến áp và tự dùng. Đúng đại lượng mà bên mua điện quan tâm.',
    'Là một phép đo duy nhất, không phải tổng của nhiều phép đo, nên không tích luỹ sai số và không phụ thuộc vào việc mọi lộ đều có dữ liệu.',
    'Độ phủ 98,0%, thuộc nhóm cao nhất trong toàn bộ dữ liệu.',
    'Tỷ lệ giá trị bằng 0 chỉ 0,002%, nghĩa là điểm đo ghi cả giá trị nhỏ ban đêm thay vì làm tròn về 0 — giữ được thông tin.',
  ]));
  o.push(P([run('Cột dự phòng khi biến mục tiêu thiếu dữ liệu: '), code('His_431.Substation_Level_22kV_Bay431_MEAS_P'),
    run('. Hệ số tương quan 0,9998 và sai lệch trung bình chỉ +0,105 MW. Có thể dùng để bù vào 70 khoảng gián đoạn của His_131, sau khi hiệu chỉnh độ lệch cố định.')]));

  o.push(H('5.4. Công suất lắp đặt và vị trí nhà máy', 2));
  o.push(P('Hai nhóm thông số này không nằm trong dữ liệu, được đơn vị cung cấp bổ sung trong quá trình khảo sát. Cả hai đều đã kiểm chứng lại bằng dữ liệu.'));
  o.push(tblTitle('Bảng 5.3 — Thông số nhà máy'));
  o.push(table(
    ['Thông số', 'Giá trị', 'Nguồn'],
    [['Công suất lắp đặt một chiều', '50 MWp', 'Đơn vị cung cấp'],
     ['Công suất định mức xoay chiều', '≈ 40 MW', 'Suy từ dữ liệu'],
     ['Tỷ lệ vượt cỡ một chiều / xoay chiều', '1,25', 'Tính toán'],
     ['Vĩ độ', '13,8634° N', 'Đơn vị cung cấp'],
     ['Kinh độ', '109,2708° E', 'Đơn vị cung cấp'],
     ['Công suất lớn nhất quan sát tại Bay131', '39,2614 MW', 'Dữ liệu'],
     ['Giá trị lớn nhất của điểm đặt công suất', '40,00 MW', 'Dữ liệu']],
    [4200, 2400, 3038], { align: [null, R, C] }));

  o.push(P([run('Kiểm chứng con số 50 MWp: tính tỷ số giữa công suất phát và tích của công suất một chiều với bức xạ chuẩn hoá, trên các mẫu có bức xạ trên 700 W/m².')]));
  o.push(tblTitle('Bảng 5.4 — Hiệu suất hệ thống nếu lấy 50 MWp làm mẫu số'));
  o.push(table(
    ['Phân vị', 'P / (50 MWp × G/1000)'],
    [['p25', '70,4%'], ['p50', '75,2%'], ['p75', '79,1%'], ['p95', '85,6%']],
    [3000, 6638], { align: [C, R] }));
  o.push(P('Dải 70–86% là mức bình thường của nhà máy quang điện sau khi tính tổn thất nhiệt độ, bám bẩn, lệch chuỗi, dây một chiều, bộ nghịch lưu, máy biến áp và tự dùng. Con số 50 MWp nhất quán với dữ liệu.'));

  o.push(P([run('Nhà máy '), run('không bị cắt ngọn', { bold: true }),
    run(' dù tỷ lệ vượt cỡ 1,25. Bằng chứng:')]));
  o.push(...bullets([
    'Chỉ 14 mẫu vượt 39 MW trong tổng số 107.307 mẫu của bảng His_report.',
    'Giá trị lớn nhất là 39,2614 MW, không chạm giới hạn cấu hình 40 MW.',
    'Trong nhóm mẫu trên 38 MW, độ lệch chuẩn là 0,29 MW. Nếu bị cắt ngọn thì con số này phải xấp xỉ 0 vì công suất sẽ nằm phẳng ở đúng ngưỡng.',
  ]));
  o.push(P('Giải thích: chuỗi tổn thất khoảng 22% vừa đúng hấp thụ hết phần vượt cỡ 25%. Phép tính 50 × 0,785 = 39,3 MW khớp với giá trị lớn nhất quan sát được.'));

  o.push(callout('Lưu ý cho FR-01 và FR-07', [
    [run('FR-01 phải lưu hai trường riêng biệt: '), code('capacity_dc_mw'), run(' = 50 và '),
     code('capacity_ac_mw'), run(' ≈ 40. Ở Việt Nam nhà máy thường được gọi theo MWp một chiều, còn hợp đồng mua bán điện và điểm đấu nối tính theo MW xoay chiều. Gộp một trường chắc chắn sẽ có lúc hiểu nhầm.')],
    'FR-07 tính chỉ số NMAE phải chuẩn hoá theo công suất xoay chiều. Lấy nhầm sang một chiều làm sai số nhìn nhỏ hơn thực tế khoảng 20% và không so sánh được với nhà máy khác.',
  ], NAVY));

  o.push(H('5.5. Vai trò của các bảng lộ 22 kV', 2));
  o.push(P('Mười một bảng lộ 22 kV không đóng góp thông tin mới cho việc dự báo, vì tổng của chúng chính là biến mục tiêu. Tuy nhiên chúng giải được một bài toán mà bảng biến mục tiêu không giải được.'));
  o.push(P('Khi công suất nhà máy giảm đột ngột, có hai nguyên nhân khác hẳn nhau: mây che, hoặc một lộ bị sự cố. Nhìn riêng Bay131 thì hai trường hợp giống nhau. Nếu đưa cả hai vào huấn luyện mà không phân biệt, mô hình sẽ học rằng "trời nắng vẫn có thể tụt công suất" — tức là học nhiễu, và sai số sẽ tăng vĩnh viễn.'));
  o.push(P('Có dữ liệu từng lộ thì phân biệt được: mây che làm tất cả các lộ giảm cùng lúc theo tỷ lệ; sự cố làm một lộ về 0 trong khi các lộ khác giữ nguyên. Đây chính là nội dung mà FR-04 yêu cầu về phát hiện bước nhảy bất thường, và FR-05 yêu cầu về ghi lý do loại bản ghi.'));
  o.push(P('Nếu dùng cho mục đích này, nên chọn nhóm 471–477 với độ phủ 95,8%, không dùng nhóm 431A–437 với độ phủ 46–48%.'));

  o.push(pageBreak());

  // ======================= 6. KHÍ TƯỢNG =======================
  o.push(H('6. Dữ liệu khí tượng', 1));

  o.push(H('6.1. Danh mục cảm biến', 2));
  o.push(P([run('Dữ liệu khí tượng nằm ở hai bảng: '), code('Weather'), run(' chu kỳ 60 giây và '),
    code('His_report'), run(' chu kỳ 300 giây. Hai bảng chứa cùng bộ điểm đo, '), code('His_report'),
    run(' là bản lấy mẫu thưa hơn kèm thêm các đại lượng điện.')]));
  o.push(tblTitle('Bảng 6.1 — Cảm biến khí tượng và chất lượng'));
  o.push(table(
    ['Điểm đo', 'Đại lượng', 'Thiếu', 'Nhận xét'],
    [
      ['SOLAR_WS_Rad_1', 'Bức xạ (W/m²)', '4,00%', 'Tốt nhất. Điểm không sạch, dùng làm biến đầu vào chính'],
      ['SOLAR_WS_Rad_2', 'Bức xạ (W/m²)', '0,03%', 'Đầy đủ nhất nhưng lệch điểm không, xem 6.4'],
      ['SOLAR_WSRT1_Rad_1', 'Bức xạ (W/m²)', '29,52%', 'Thiếu nhiều, chỉ dùng đối chứng'],
      ['SOLAR_WS_Panel_T', 'Nhiệt độ tấm pin (°C)', '0,03%', 'Có giá trị đột biến 6.553 °C, xem 7.3'],
      ['SOLAR_WS_Air_T', 'Nhiệt độ không khí (°C)', '0,03%', 'Bình thường'],
      ['SOLAR_WS_Humidity', 'Độ ẩm (%)', '0,03%', 'Bình thường'],
      ['SOLAR_WS_Wind_Speed', 'Tốc độ gió (m/s)', '0,03%', 'Bình thường'],
      ['SOLAR_WS_Wind_direction', 'Hướng gió (°)', '0,03%', 'Bình thường'],
      ['SOLAR_WS_Air_Pressure', 'Áp suất', '0,03%', 'Toàn bộ bằng 0, điểm đo chưa đấu'],
      ['Data_WS1_* (8 điểm)', 'Trạm khí tượng 2', '93,17%', 'Hỏng — giá trị còn lại là hằng số'],
      ['Data_WS2_* (8 điểm)', 'Trạm khí tượng 3', '100,00%', 'Hỏng hoàn toàn — không có dữ liệu'],
    ],
    [2500, 2100, 900, 4138], { align: [null, null, R, null], size: 16,
      redRows: [8, 9, 10] }));

  o.push(H('6.2. Thống kê bức xạ', 2));
  o.push(tblTitle('Bảng 6.2 — Thống kê các điểm đo bức xạ (bảng Weather và His_report)'));
  o.push(table(
    ['Bảng', 'Điểm đo', 'Thiếu', 'Bằng 0', 'Trung vị', 'Phân vị 99', 'Lớn nhất', 'Trung bình'],
    J.irr.filter(x => !Number.isNaN(x.max) && x.max !== null).map(x => [
      x.table, x.column.replace('SOLAR_', '').replace('Data_', ''),
      fmt(x.null, 2) + '%', Number.isNaN(x.zero) ? '—' : fmt(x.zero, 1) + '%',
      fmt(x.p50, 1), fmt(x.p99, 1), fmt(x.max, 1), fmt(x.mean, 1)]),
    [1400, 1500, 900, 900, 1100, 1200, 1200, 1438], { align: [null, null, R, R, R, R, R, R], size: 15, headSize: 15 }));
  o.push(P('Tỷ lệ bằng 0 khoảng 47–49% là hợp lý: đó là phần ban đêm của chuỗi. Hai dòng cuối bảng — Data_WS1_Rad_1 và Rad_2 — có trung vị bằng đúng phân vị 99 bằng đúng giá trị lớn nhất, tức là toàn bộ dữ liệu chỉ có một giá trị duy nhất. Đây là dấu hiệu điểm đo bị treo, không phải dữ liệu thật.'));

  o.push(H('6.3. Chu kỳ ngày và bất đối xứng sáng chiều', 2));
  o.push(P('Đường trung bình theo giờ của bức xạ và công suất có dạng hình chuông đúng như mong đợi, đạt đỉnh quanh giữa trưa.'));
  o.push(...figure(FIG + '/h61_diurnal.png', 490, 'Hình 6.1 — Trung bình theo giờ trong ngày, giờ Việt Nam'));
  o.push(tblTitle('Bảng 6.3 — Giá trị đỉnh và nền đêm'));
  o.push(table(
    ['Đại lượng', 'Giờ đạt đỉnh', 'Giá trị đỉnh', 'Trung bình 0–4 giờ'],
    [['Bức xạ Rad_1', '12 giờ', '703,6 W/m²', '0,011 W/m²'],
     ['Bức xạ Rad_2', '12 giờ', '732,1 W/m²', '26,05 W/m²'],
     ['Công suất Bay131', '12 giờ', '24,76 MW', '0,071 MW']],
    [2800, 2000, 2400, 2438], { align: [null, C, R, R] }));

  o.push(P('Xem kỹ hơn ở độ phân giải 5 phút thì phát hiện một đặc điểm đáng chú ý. Lấy mốc bức xạ vượt 20 W/m² làm ranh giới ngày, thống kê trên 331 ngày có đủ dữ liệu:'));
  o.push(tblTitle('Bảng 6.4 — Các mốc thời gian quan sát trong ngày'));
  o.push(table(
    ['Mốc', 'Thời điểm (giờ Việt Nam)', 'Cách xác định'],
    [['Bắt đầu có bức xạ', '05:59', 'Trung vị của lần đầu vượt 20 W/m² trong ngày'],
     ['Hết bức xạ', '17:27', 'Trung vị của lần cuối vượt 20 W/m² trong ngày'],
     ['Giữa ngày', '11:44', 'Trung điểm giữa hai mốc trên'],
     ['Trọng tâm phần đỉnh bức xạ', '12:20', 'Trọng tâm của phần đường vượt 90% giá trị đỉnh'],
     ['Điểm cao nhất của đường bức xạ', '12:50', 'Trực tiếp từ đường trung bình 5 phút']],
    [2700, 2200, 4738], { align: [null, C, null], size: 16 }));
  o.push(P([run('Điểm giữa ngày rất ổn định, độ lệch chuẩn chỉ 12,3 phút qua cả năm. Nhưng đỉnh bức xạ lại '),
    run('chậm hơn giữa ngày khoảng 36 phút', { bold: true }),
    run('. Nói cách khác, buổi chiều tại nhà máy này sáng hơn buổi sáng một cách hệ thống, không phải ngẫu nhiên.')]));
  o.push(P('Hai nguyên nhân khả dĩ: mây thấp ven biển vào buổi sáng, hoặc cảm biến bức xạ đặt trên mặt phẳng nghiêng lệch về hướng tây. Cần xác nhận kiểu lắp đặt cảm biến với đơn vị vận hành để biết chính xác.'));
  o.push(callout('Ảnh hưởng tới mô hình', [
    'Nếu chỉ dùng đặc trưng "số phút kể từ đầu ngày" hoặc các đặc trưng đối xứng quanh 12 giờ, mô hình sẽ lệch có hệ thống — thiếu vào buổi chiều, thừa vào buổi sáng.',
    'Cách xử lý đơn giản nhất: thêm một đặc trưng nhị phân phân biệt trước và sau 11:44, để mô hình tự học phần chênh lệch giữa hai nửa ngày.',
  ], ORANGE));

  o.push(H('6.4. Lệch điểm không của cảm biến Rad_2', 2));
  o.push(P([run('Bảng 6.3 cho thấy một bất thường: ban đêm, từ 0 đến 4 giờ, cảm biến Rad_2 vẫn báo trung bình '),
    run('26,05 W/m²', { bold: true }), run(' trong khi Rad_1 báo 0,011 W/m². Không có nguồn bức xạ nào lúc nửa đêm, nên đây là độ lệch điểm không của cảm biến.')]));
  o.push(P('Hệ quả nếu bỏ qua: mô hình sẽ học một hệ số chặn sai, và sai số này sẽ xuất hiện ở mọi dự báo, kể cả ban ngày. Cách xử lý đề xuất ở mục 10.4.'));
  o.push(P([run('Lưu ý ngược lại: mặc dù lệch điểm không, Rad_2 lại có tỷ lệ thiếu dữ liệu thấp nhất (0,03% so với 4,00% của Rad_1). Phương án tốt nhất là dùng Rad_1 làm chính và dùng Rad_2 đã hiệu chỉnh để bù vào chỗ thiếu.')]));

  o.push(H('6.5. Tương quan với công suất', 2));
  o.push(P('Bảng dưới là hệ số tương quan Pearson giữa từng đại lượng khí tượng và công suất tại Bay131, tính trên bảng His_report.'));
  o.push(tblTitle('Bảng 6.5 — Tương quan với công suất Bay131'));
  o.push(table(
    ['Đại lượng', 'Hệ số tương quan', 'Nhận xét'],
    [
      ['SOLAR_WS_Rad_1', fmt(J.corr.SOLAR_WS_Rad_1, 3), 'Biến đầu vào mạnh nhất'],
      ['SOLAR_WSRT1_Rad_1', fmt(J.corr.SOLAR_WSRT1_Rad_1, 3), 'Mạnh nhưng thiếu 29,5% dữ liệu'],
      ['SOLAR_WS_Rad_2', fmt(J.corr.SOLAR_WS_Rad_2, 3), 'Thấp hơn do lệch điểm không'],
      ['SOLAR_WS_Panel_T', fmt(J.corr.SOLAR_WS_Panel_T, 3), 'Tương quan gián tiếp qua bức xạ'],
      ['SOLAR_WS_Wind_Speed', fmt(J.corr.SOLAR_WS_Wind_Speed, 3), 'Yếu, có thể có ích cho làm mát tấm pin'],
      ['SOLAR_WS_Humidity', fmt(J.corr.SOLAR_WS_Humidity, 3), 'Yếu và ngược chiều, hợp lý'],
      ['SOLAR_WS_Air_T', fmt(J.corr.SOLAR_WS_Air_T, 3), 'Gần như không tương quan tuyến tính'],
    ],
    [3000, 2000, 4638], { align: [null, R, null] }));
  o.push(P([run('Hệ số 0,960 giữa Rad_1 và công suất là mức tốt cho dữ liệu vận hành thực tế. Phần chưa giải thích được chủ yếu đến từ ba nguồn: hiệu ứng nhiệt độ làm giảm hiệu suất tấm pin ở bức xạ cao, độ trễ nhiệt của hệ thống, và sự khác biệt giữa bức xạ đo tại một điểm với bức xạ trung bình trên toàn bộ cánh đồng pin.')]));
  o.push(P('Điểm đáng chú ý: nhiệt độ không khí gần như không tương quan tuyến tính (0,03) trong khi nhiệt độ tấm pin tương quan 0,55. Điều này đúng với vật lý — nhiệt độ tấm pin tăng theo bức xạ nên bám theo công suất, còn nhiệt độ không khí thì không.'));

  return o;
};
