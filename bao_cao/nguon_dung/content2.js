// content2.js — Chương 7 đến 12 và phụ lục
const L = require('./lib');
const { P, H, run, code, bullets, table, tblTitle, figure, codeBlock, callout,
        pageBreak, fmt, int, RED, ORANGE, GREEN, NAVY, D } = L;
const { AlignmentType } = D;
const C = AlignmentType.CENTER, R = AlignmentType.RIGHT;

module.exports = function (J, FIG) {
  const T = J.time;
  const tab = n => T.find(x => x.table === n);
  const o = [];

  // ======================= 7. CHẤT LƯỢNG =======================
  o.push(H('7. Đánh giá chất lượng dữ liệu', 1));
  o.push(P('Chương này bám theo bảy tiêu chí mà FR-04 quy định. Mỗi mục nêu tiêu chí, kết quả kiểm tra và hướng xử lý.'));

  o.push(H('7.1. Khung tiêu chí', 2));
  o.push(table(
    ['Tiêu chí theo FR-04', 'Kết quả', 'Mục'],
    [
      ['Phát hiện dữ liệu thiếu', 'Đã kiểm — có vấn đề ở 7 bảng', '7.2'],
      ['Phát hiện dữ liệu trùng lặp', 'Đã kiểm — 3 bản ghi, không đáng kể', '4.5'],
      ['Phát hiện sai mốc thời gian', 'Đã kiểm — không phát hiện', '4.4'],
      ['Phát hiện giá trị ngoài phạm vi hợp lệ', 'Đã kiểm — 3 điểm đo vượt ngưỡng vật lý', '7.4'],
      ['Phát hiện bước nhảy bất thường', 'Đã kiểm — 3 điểm đo có giá trị đột biến', '7.3'],
      ['Tính độ phủ dữ liệu', 'Đã tính cho cả 17 bảng', '4.2'],
      ['Phân biệt giá trị trống với giá trị 0', 'Đã chốt quy tắc xử lý', '7.6'],
    ],
    [4400, 3900, 1338], { align: [null, null, C] }));

  o.push(H('7.2. Dữ liệu thiếu', 2));
  o.push(P('Thiếu dữ liệu xảy ra ở hai mức khác nhau, cần xử lý khác nhau.'));
  o.push(P([run('Mức bảng — thiếu cả khoảng thời gian. ', { bold: true }),
    run('Nêu ở mục 4.2. Nghiêm trọng nhất là bảy lộ 431A–437 mất 46–48% số mẫu.')]));
  o.push(P([run('Mức cột — điểm đo không có dữ liệu. ', { bold: true }),
    run('Bảng dưới liệt kê các cột thiếu trên 90% hoặc chỉ có một giá trị duy nhất.')]));

  o.push(tblTitle('Bảng 7.1 — Điểm đo hỏng hoặc treo giá trị'));
  const dead = J.dead.filter(d => d.null > 90 || d.note === 'hằng số');
  o.push(table(
    ['Bảng', 'Điểm đo', 'Tỷ lệ thiếu', 'Ghi chú'],
    dead.slice(0, 26).map(d => [d.table, d.column.length > 44 ? d.column.slice(0, 42) + '…' : d.column,
      fmt(d.null, 1) + '%', d.note || '']),
    [1500, 4700, 1300, 2138], { align: [null, null, R, null], size: 15, headSize: 15 }));
  if (dead.length > 26) o.push(P(`Danh sách đầy đủ ${dead.length} điểm đo nêu tại Phụ lục B.`, { italics: true, size: 18 }));

  o.push(P('Có thể phân thành ba nhóm nguyên nhân:'));
  o.push(...bullets([
    [run('Trạm khí tượng phụ chưa đấu nối. ', { bold: true }), run('Toàn bộ nhóm Data_WS1_* và Data_WS2_* — 16 điểm đo. Nhóm WS2 thiếu 100%, nhóm WS1 thiếu 93,17% và phần còn lại là hằng số. Đây là hai trạm khí tượng dự phòng đã khai báo trong cấu hình SCADA nhưng chưa lắp hoặc chưa thông tín hiệu.')],
    [run('Điểm đo điện áp một số lộ không có tín hiệu. ', { bold: true }), run('Các cột Meas_Ua, Meas_Ub, Meas_Uc của bốn lộ 471, 473, 475, 477 đều thiếu 100%. Bốn ngăn lộ này chỉ đo dòng và công suất, không đo điện áp — hợp lý về mặt thiết kế vì điện áp thanh cái đã đo tại His_TUC41.')],
    [run('Điểm đo báo hằng số. ', { bold: true }), run('Ví dụ IEC104S_AI_P_LOW luôn bằng 0,3 và Substation_Level_110kV_BayT1_T1_MEAS_Tap luôn bằng một giá trị. Cần xác nhận với vận hành xem đây là giá trị thật không đổi hay tín hiệu treo.')],
  ]));

  o.push(H('7.3. Giá trị đột biến', 2));
  o.push(P('Tiêu chí phát hiện: giá trị lớn nhất vượt quá 100 lần phân vị 99 của chính cột đó. Ngưỡng này chọn đủ rộng để không báo nhầm biến động vận hành bình thường.'));
  o.push(tblTitle('Bảng 7.2 — Giá trị đột biến phát hiện được'));
  o.push(table(
    ['Bảng', 'Điểm đo', 'Phân vị 99', 'Lớn nhất', 'Tỷ lệ vượt'],
    J.spike.map(s => [s.table, s.column.length > 40 ? s.column.slice(0, 38) + '…' : s.column,
      fmt(s.p99), int(s.max), int(s.ratio) + ' lần']),
    [1500, 4000, 1300, 1500, 1338], { align: [null, null, R, R, R], size: 16 }));

  o.push(callout('Trường hợp nghiêm trọng nhất', [
    [code('His_431A.Substation_Level_22kV_Bay431A_MEAS_P'), run(' đạt giá trị 4.410.466 MW.')],
    'Để so sánh: tổng công suất lắp đặt điện mặt trời của cả Việt Nam ở mức vài chục nghìn MW. Giá trị này lớn hơn khoảng một trăm lần con số đó, và lớn hơn 718.016 lần phân vị 99 của chính điểm đo ấy (6,14 MW).',
    'Đây gần như chắc chắn là lỗi truyền tin hoặc lỗi biểu diễn số thực, không phải giá trị đo. Nếu đưa vào huấn luyện mà không lọc, một điểm dữ liệu này đủ làm hỏng hoàn toàn quá trình chuẩn hoá và làm mô hình không hội tụ.',
  ], RED));

  o.push(P([run('Hai trường hợp còn lại: '), code('Data_PR'), run(' (hệ số hiệu suất) đạt 54.108 trong khi giá trị hợp lý nằm trong khoảng 0–100; và '),
    code('SOLAR_WS_Panel_T'), run(' đạt 6.553,5 °C. Giá trị 6553,5 đáng chú ý vì bằng đúng 65535 chia 10 — dấu hiệu tràn số nguyên 16 bit không dấu trong quá trình truyền tin.')]));

  o.push(H('7.4. Giá trị bức xạ bất thường ở dải cao', 2));
  o.push(P('Thay vì lấy một ngưỡng chung, ngưỡng lọc ở đây đọc thẳng từ phân bố của chính dữ liệu. Bảng dưới đếm số mẫu vượt từng mức, trên toàn bộ chuỗi.'));
  o.push(tblTitle('Bảng 7.3 — Phân bố phần đuôi của bức xạ'));
  o.push(table(
    ['Mức (W/m²)', 'SOLAR_WS_Rad_1 (503.153 mẫu)', 'SOLAR_WS_Rad_2 (523.950 mẫu)'],
    [['Phân vị 99', '993', '1.029'],
     ['Phân vị 99,9', '1.146', '1.187'],
     ['> 1.100', '1.021 mẫu (0,20%)', '1.833 mẫu (0,35%)'],
     ['> 1.200', '209 mẫu (0,042%)', '418 mẫu (0,080%)'],
     ['> 1.300', '19 mẫu (0,004%)', '69 mẫu (0,013%)'],
     ['> 1.350', '1 mẫu (0,0002%)', '18 mẫu (0,003%)'],
     ['Lớn nhất', '1.401', '1.454']],
    [2200, 3700, 3738], { align: [null, R, R], size: 16 }));
  o.push(P([run('Phần đuôi rơi rất nhanh. Từ phân vị 99,9 (khoảng 1.150 W/m²) trở lên chỉ còn vài trăm mẫu, và trên 1.300 W/m² chỉ còn vài chục mẫu trên nửa triệu. Đây là dấu hiệu của nhiễu đo chứ không phải một chế độ vận hành riêng.')]));
  o.push(callout('Ngưỡng đề nghị', [
    [run('Đặt ngưỡng hợp lệ '), run('0 – 1.350 W/m²', { bold: true }),
     run(' trong bảng ánh xạ ở mục 10.2. Mức này loại đúng phần đuôi bất thường mà chỉ bỏ 0,003% số mẫu.')],
    'Gắn cờ xem xét cho các giá trị trong khoảng 1.150 – 1.350 W/m². Chúng có thể là hiện tượng tăng cường do phản xạ từ rìa mây, có thật nhưng ngắn, cần theo dõi riêng.',
    'Điểm đo SOLAR_WSRT1_Rad_1 ở bảng His_report chạm 1.501 W/m² — cao nhất trong toàn bộ dữ liệu và thiếu tới 29,5% số mẫu, nên không dùng làm biến đầu vào.',
  ], ORANGE));
  o.push(P('Một khả năng cần loại trừ khi rà lại: nếu cảm biến đặt trên mặt phẳng nghiêng chứ không nằm ngang thì giá trị đo được sẽ cao hơn bức xạ trên mặt ngang ở một số thời điểm trong ngày, và ngưỡng 1.350 W/m² đặt theo mặt ngang sẽ hơi chặt. Phép kiểm ở mục 6.3 cho thấy tỷ số công suất trên bức xạ phẳng suốt cả ngày, tức không có dấu hiệu cảm biến lệch hướng đông hay tây; nhưng phép kiểm đó không loại trừ được trường hợp cảm biến nghiêng đúng hướng nam. Vì vậy vẫn nên hỏi để chốt ngưỡng, xem câu 2 ở Bảng 11.2.'));

  o.push(H('7.5. Giá trị âm của công suất', 2));
  o.push(P([run('Biến mục tiêu có 17,98% số mẫu mang giá trị âm, giá trị nhỏ nhất là −0,450 MW. Đây không phải lỗi, nhưng cách hiểu cần chính xác.')]));
  o.push(tblTitle('Bảng 7.4 — Công suất tại Bay131 theo khung giờ'));
  o.push(table(
    ['Khung giờ địa phương', 'Số mẫu', 'Trung bình', 'Trung vị', 'Nhỏ nhất', 'Tỷ lệ âm'],
    [['Ban đêm, 20h–04h', '195.188', '+0,073 MW', '+0,067 MW', '−0,412 MW', '31,9%'],
     ['Ban ngày, 10h–14h', '108.768', '+23,241 MW', '+26,569 MW', '−0,450 MW', '2,0%']],
    [2400, 1400, 1600, 1600, 1500, 1138], { align: [null, R, R, R, R, R], size: 16 }));
  o.push(P('Ba điểm cần đọc đúng từ bảng này:'));
  o.push(...bullets([
    'Ban đêm chiếm khoảng một nửa chuỗi, không phải 18%. Con số 17,98% là tỷ lệ âm trên toàn chuỗi, gộp cả ban đêm lẫn các mẫu tranh tối tranh sáng.',
    'Trung bình công suất ban đêm là số dương, +0,073 MW, chứ không âm. Chỉ 31,9% số mẫu ban đêm mang dấu âm.',
    'Biên độ dao động ban đêm rất nhỏ, trong dải khoảng ±0,1 MW, tương đương ±0,25% công suất định mức. Phần âm là lúc phụ tải tự dùng vượt phần phát dư, phần dương là ngược lại.',
  ]));
  o.push(P([run('Để so sánh, công suất phản kháng tại cùng ngăn lộ có biên độ lớn hơn hẳn: ban đêm chạm −8,384 MVAr, toàn chuỗi chạm −11,492 MVAr, với 44,88% số mẫu mang dấu âm. Đó là dòng từ hoá máy biến áp và bộ nghịch lưu ở chế độ chờ. Hiện tượng này nằm ở cột '),
    code('MEAS_Q'), run(' chứ không phải '), code('MEAS_P'), run(', hai cột tách bạch trong lược đồ.')]));
  o.push(callout('Ảnh hưởng tới chỉ số đánh giá của FR-07', [
    'Không dùng MAPE trên toàn chuỗi. Ban đêm công suất dao động quanh 0 nên mẫu số tiến về 0 và chỉ số bùng nổ vô nghĩa.',
    'Đề nghị: tính MAPE riêng cho khoảng có bức xạ trên 50 W/m², và dùng NMAE chuẩn hoá theo 40 MW xoay chiều cho toàn chuỗi.',
  ], ORANGE));

  o.push(H('7.6. Cách hiểu giá trị 0', 2));
  o.push(P([run('Yêu cầu FR-04 quy định dữ liệu trống phải giữ trạng thái thiếu, không được gán bằng 0. Vấn đề là ở chiều ngược lại: dữ liệu nguồn có sẵn nhiều giá trị 0, cần biết đó là số đo thật hay là cách hệ thống thu thập biểu thị "không có thông tin".')]));
  o.push(tblTitle('Bảng 7.5 — Tỷ lệ giá trị bằng 0 theo điều kiện'));
  o.push(table(
    ['Điểm đo', 'Bằng 0 toàn chuỗi', 'Bằng 0 lúc nắng rõ'],
    [['Substation_Level_22kV_Bay473_Meas_P', '59,84%', '0,65%'],
     ['Substation_Level_22kV_Bay431_MEAS_P', '59,32%', '0,48%'],
     ['Substation_Level_22kV_Bay475_Meas_P', '59,15%', '0,63%'],
     ['Substation_Level_22kV_Bay477_Meas_P', '58,31%', '0,34%'],
     ['Substation_Level_22kV_Bay471_Meas_P', '58,01%', '0,29%'],
     ['SOLAR_WS_Rad_2', '46,60%', '0,00%'],
     ['SOLAR_WS_Rad_1', '46,13%', '0,00%'],
     ['Substation_Level_110kV_Bay131_MEAS_P', '0,97%', '0,00%']],
    [5000, 2400, 2238], { align: [null, R, R], size: 16 }));
  o.push(P([run('Cột thứ ba tính trên 16.410 mẫu trong khung 10–14 giờ có bức xạ trên 400 W/m², tức điều kiện mà '),
    run('không thể có lý do vật lý nào để công suất hay bức xạ bằng 0', { bold: true }),
    run('. Kết quả rất rõ: giá trị 0 gần như chỉ xuất hiện ban đêm.')]));
  o.push(P('Nghĩa là hai loại số 0 khác hẳn nhau đang nằm chung trong dữ liệu. Ban đêm, số 0 là giá trị đo thật — mặt trời lặn thì bức xạ đúng bằng 0, và điểm đo công suất có vùng chết nên làm tròn các giá trị rất nhỏ về 0. Ban ngày trời nắng, số 0 không thể là số đo thật, chỉ có thể là cách biểu thị mất tín hiệu.'));

  o.push(callout('Quy tắc đã chốt', [
    [run('Giá trị 0 xuất hiện trong khoảng có bức xạ được hiểu là '), run('không có thông tin', { bold: true }),
     run(' và đánh dấu trạng thái thiếu dữ liệu. Giá trị 0 ban đêm giữ nguyên vì đó là số đo thật.')],
    'Chi phí: loại khoảng 0,3–0,7% số mẫu ban ngày. Không ảnh hưởng đáng kể tới lượng dữ liệu huấn luyện.',
    'Nếu áp quy tắc cho cả chuỗi mà không phân biệt ngày đêm thì 46% dữ liệu bức xạ bị đánh dấu thiếu, trong khi đó là giá trị đúng. Vì vậy điều kiện về bức xạ là bắt buộc.',
    'Cách cài đặt cụ thể ở mục 10.4, mã chất lượng số 8.',
  ], GREEN));
  o.push(P([run('Biến mục tiêu '), code('Bay131_MEAS_P'), run(' hầu như không bị ảnh hưởng: tỷ lệ bằng 0 toàn chuỗi chỉ 0,97% trên bảng gộp His_report — và chỉ 0,002% trên bảng gốc His_131 — đồng thời bằng 0 tuyệt đối trong khoảng có nắng. Điểm đo này ghi cả các giá trị rất nhỏ ban đêm thay vì làm tròn, nên giữ được nhiều thông tin hơn hẳn các ngăn lộ 22 kV.')]));

  o.push(H('7.7. Tổng hợp mức độ nghiêm trọng', 2));
  o.push(tblTitle('Bảng 7.6 — Tổng hợp vấn đề chất lượng và hướng xử lý'));
  o.push(table(
    ['#', 'Vấn đề', 'Phạm vi', 'Mức độ', 'Hướng xử lý'],
    [
      ['1', 'Dữ liệu không sắp theo thời gian', '17/17 bảng', 'Cao', 'Sắp xếp bắt buộc khi nạp'],
      ['2', 'Giá trị đột biến biên độ lớn', '3 điểm đo', 'Cao', 'Lọc theo ngưỡng vật lý'],
      ['3', 'Giá trị 0 ban ngày là mất tín hiệu', 'Các điểm đo công suất', 'Cao', 'Đánh dấu thiếu, mã 8 (mục 7.6)'],
      ['4', 'Cột Data_PR sai định nghĩa', '1 điểm đo', 'Cao', 'Loại bỏ, tính lại (mục 8.4)'],
      ['5', 'Bức xạ vượt ngưỡng vật lý', '4 điểm đo', 'Trung bình', 'Cắt ngưỡng 1.350 W/m²'],
      ['6', 'Độ phủ thấp nhóm 431A–437', '7 bảng', 'Trung bình', 'Không dùng làm chuỗi liên tục'],
      ['7', 'Rad_2 treo giá trị 329 giờ khi trạm mất tín hiệu', '1 điểm đo', 'Cao', 'Đánh dấu loại các đợt treo, mã 6 (mục 6.4)'],
      ['8', 'Điểm đo treo hằng số', `${dead.length} điểm đo`, 'Thấp', 'Loại khỏi tập biến đầu vào'],
      ['9', 'Mốc thời gian trùng', '3 bản ghi', 'Thấp', 'Khử trùng khi nạp'],
      ['10', 'Nhiệt độ không khí và độ ẩm tắt hẳn từ 05/2026', '2 điểm đo', 'Cao', 'Không dùng làm biến đầu vào (mục 6.6)'],
    ],
    [500, 3100, 1900, 1400, 2738], { align: [C, null, null, C, null], size: 16,
      redRows: [0, 1, 2, 3] }));

  o.push(pageBreak());

  // ======================= 8. GIẢ THIẾT =======================
  o.push(H('8. Kiểm tra các giả thiết ảnh hưởng đến mô hình', 1));

  o.push(H('8.1. Nhà máy có bị cắt giảm công suất không', 2));
  o.push(P('Đây là câu hỏi quyết định tính dùng được của dữ liệu. Nếu nhà máy thường xuyên bị điều độ yêu cầu giảm phát, thì công suất đo được không phản ánh khả năng phát thực tế, và mô hình huấn luyện trên đó sẽ học nhầm quan hệ giữa bức xạ và công suất.'));
  o.push(P('Phép kiểm: chia dữ liệu theo dải bức xạ, xét phân bố công suất trong từng dải. Nếu có cắt giảm, công suất sẽ chạm một trần phẳng và không tăng tiếp khi bức xạ tăng.'));
  o.push(tblTitle('Bảng 8.1 — Công suất theo dải bức xạ, mẫu ban ngày'));
  o.push(table(
    ['Dải bức xạ (W/m²)', 'Số mẫu', 'Công suất trung bình (MW)', 'Độ lệch chuẩn', 'Lớn nhất (MW)'],
    J.curtail.map(c => [c.bin.replace('–', ' – '), int(c.n), fmt(c.mean), fmt(c.std), fmt(c.max)]),
    [2100, 1600, 2400, 1700, 1838], { align: [C, R, R, R, R] }));
  o.push(...figure(FIG + '/h81_scatter.png', 490, 'Hình 8.1 — Quan hệ bức xạ với công suất, mẫu 8–15 giờ địa phương'));

  o.push(callout('Kết luận mục 8.1', [
    'Công suất trung bình tăng đơn điệu theo bức xạ qua toàn bộ các dải, từ 4,15 MW lên 31,65 MW. Không xuất hiện trần phẳng. Giá trị lớn nhất trong từng dải cũng tăng dần và chỉ chạm 39,27 MW ở dải cao nhất, đúng bằng công suất lắp đặt.',
    'Không phát hiện dấu hiệu cắt giảm công suất theo lệnh điều độ trong toàn bộ 370 ngày dữ liệu.',
  ], GREEN));

  o.push(P([run('Một lưu ý về dải 1.000–1.400 W/m²: công suất trung bình ở dải này (29,50 MW) thấp hơn dải 800–1.000 (31,65 MW). Đây không phải cắt giảm mà là hiệu ứng nhiệt độ — bức xạ rất cao đi kèm nhiệt độ tấm pin cao, làm hiệu suất chuyển đổi giảm. Ngoài ra dải này chỉ có 4.402 mẫu, phần lớn là các đợt tăng cường bức xạ ngắn do phản xạ rìa mây, khi đó hệ thống chưa kịp đáp ứng. Đặc trưng nhiệt độ tấm pin cần được đưa vào mô hình để nắm bắt hiệu ứng này.')]));

  o.push(H('8.2. Ý nghĩa của nhóm điểm đo IEC104', 2));
  o.push(P([run('Ba điểm đo có tiền tố '), code('IEC104S_'), run(' liên quan tới kênh truyền tin với điều độ theo giao thức IEC 60870-5-104. Ban đầu chúng có vẻ là lệnh giới hạn công suất, nhưng kiểm tra cho kết quả khác.')]));
  o.push(table(
    ['Điểm đo', 'Trung bình', 'Lớn nhất', 'Giờ đạt đỉnh', 'Diễn giải'],
    [['AO_A0_P_SETPOINT', '7,80', '40,00', '12 giờ', 'Bám theo công suất thực'],
     ['AI_P_HIGH', '8,38', '45,74', '12 giờ', 'Bám theo công suất thực'],
     ['AI_P_LOW', '0,30', '0,30', '—', 'Hằng số, điểm đo treo']],
    [2400, 1500, 1500, 1600, 2638], { align: [null, R, R, C, null] }));
  o.push(P([run('Nếu đây là lệnh giới hạn từ điều độ, giá trị phải có dạng bậc thang và giữ nguyên trong nhiều giờ. Thực tế cả hai điểm đo đều có dạng hình chuông đạt đỉnh đúng 12 giờ, giống hệt đường công suất phát. Kết luận: '),
    run('đây là giá trị đo gửi lên điều độ, không phải lệnh giới hạn', { bold: true }),
    run('. Không dùng làm biến đầu vào cho mô hình, vì chúng chứa chính thông tin cần dự báo — đưa vào sẽ gây rò rỉ dữ liệu tương lai.')]));

  o.push(H('8.3. Tính đầy đủ của chu kỳ mùa', 2));
  o.push(P('Chuỗi dữ liệu dài 370 ngày, tức đúng một chu kỳ mùa. Điều này có hai hệ quả đối với việc đánh giá mô hình theo FR-07.'));
  o.push(...bullets([
    'Mô hình quan sát được mỗi mùa đúng một lần. Không phân biệt được đặc điểm mùa lặp lại hằng năm với đặc điểm riêng của năm 2025–2026.',
    'Không tách được tập kiểm định độc lập theo mùa. Nếu để dành ba tháng cuối làm tập kiểm định thì tập huấn luyện mất hẳn mùa tương ứng.',
  ]));
  o.push(P('Phương án đề xuất cho giai đoạn hiện tại: dùng đánh giá theo kiểu gốc trượt (rolling origin) mà FR-07 đã yêu cầu, thay vì chia cố định. Cách này tận dụng được toàn bộ chuỗi và vẫn bảo đảm mọi lần đánh giá đều thực hiện trên dữ liệu chưa từng dùng để huấn luyện.'));
  o.push(P('Cần ghi nhận rõ trong báo cáo đánh giá mô hình rằng kết quả của giai đoạn này chưa kiểm chứng được tính ổn định qua nhiều năm.'));

  o.push(H('8.4. Cột Data_PR không phải hệ số hiệu suất', 2));
  o.push(P([run('Bảng '), code('His_report'), run(' có cột '), code('Data_PR'),
    run(' do SCADA tự tính. Tên gọi và vị trí gợi ý đây là hệ số hiệu suất (performance ratio) — chỉ số vận hành tiêu chuẩn của nhà máy quang điện. Kiểm tra cho kết quả khác.')]));
  o.push(P('Theo định nghĩa tiêu chuẩn, hệ số hiệu suất là tỷ số giữa sản lượng thực tế và sản lượng lý thuyết tính theo công suất lắp đặt một chiều:'));
  o.push(codeBlock([
    'PR = (P / P_dc_danh_dinh) / (G / 1000)',
    '',
    '# Suy ngược mẫu số mà SCADA đang dùng:',
    'P_dc_scada = P / ( (Data_PR/100) * (G/1000) )',
  ]));
  o.push(tblTitle('Bảng 8.2 — Suy ngược mẫu số SCADA dùng để tính Data_PR'));
  o.push(table(
    ['Phân vị', 'Công suất danh định suy ra'],
    [['p25', '35,81 MW'], ['p50', '38,22 MW'], ['p75', '40,20 MW'], ['p95', '43,55 MW']],
    [3000, 6638], { align: [C, R] }));
  o.push(P([run('Trung vị 38,22 MW cho thấy SCADA chia cho '), run('công suất xoay chiều', { bold: true }),
    run(' chứ không phải 50 MWp một chiều theo thông lệ. Hệ quả:')]));
  o.push(tblTitle('Bảng 8.3 — So sánh giá trị SCADA báo với giá trị đúng'));
  o.push(table(
    ['Chỉ số', 'Trung vị lúc bức xạ trên 700 W/m²'],
    [['Data_PR do SCADA báo', '98,4%'],
     ['Hệ số hiệu suất thật, chia cho 50 MWp', '75,1%'],
     ['Mức thổi phồng', '1,31 lần']],
    [5000, 4638], { align: [null, R], redRows: [0, 2] }));
  o.push(callout('Cảnh báo', [
    'Không có nhà máy quang điện nào đạt hệ số hiệu suất 98%. Mức bình thường của một nhà máy vận hành tốt là 75–82%. Giá trị 75,1% tính lại theo đúng định nghĩa nằm đúng trong dải này.',
    'Nếu con số 98,4% từng được đưa vào báo cáo vận hành gửi chủ đầu tư hoặc dùng để đánh giá hiệu quả đầu tư thì đang sai lệch khoảng 31%.',
    [run('Hai việc phải làm: loại '), code('Data_PR'),
     run(' khỏi tập biến đầu vào của mô hình, và tính lại chỉ số này theo công suất một chiều 50 MWp nếu cần dùng cho mục đích vận hành.')],
  ], RED));
  o.push(P('Cột này cũng chứa giá trị rác lên tới 54.108 như đã nêu ở mục 7.3, nên dù có tính lại vẫn phải lọc trước.'));

  o.push(pageBreak());

  // ======================= 9. KHOẢNG TRỐNG =======================
  o.push(H('9. Khoảng trống dữ liệu', 1));
  o.push(P('Chương này liệt kê những dữ liệu mà mô hình cần nhưng bản lưu hiện tại không có.'));

  o.push(H('9.1. Không có dữ liệu dự báo thời tiết', 2));
  o.push(P('Rà soát toàn bộ 19 bảng và khoảng 300 cột: không có một cột nào chứa dữ liệu dự báo. Tất cả đều là số liệu đo tại thời điểm quá khứ.'));
  o.push(P('Đây là khoảng trống lớn nhất. Bài toán dự báo một ngày tới không thể chỉ dựa vào dữ liệu quá khứ, vì bức xạ ngày mai không suy ra được từ bức xạ hôm nay. Cần nguồn dự báo thời tiết số trị từ bên ngoài.'));
  o.push(P('Yêu cầu tối thiểu đối với nguồn dự báo:'));
  o.push(...bullets([
    'Đại lượng: bức xạ tổng trên mặt phẳng ngang, nhiệt độ không khí, độ che phủ mây. Có thêm bức xạ trên mặt phẳng nghiêng thì tốt hơn.',
    'Độ phân giải thời gian: 15 phút hoặc mịn hơn, để khớp với FC-02.',
    'Tầm dự báo: tối thiểu 48 giờ.',
    'Tần suất phát hành: tối thiểu hai lần một ngày.',
    'Dữ liệu lịch sử của chính nguồn dự báo đó, tối thiểu một năm — điểm này quan trọng nhất và hay bị bỏ sót. Mô hình cần được huấn luyện trên chính sai số của nguồn dự báo, nên phải có bản lưu trữ các bản dự báo trong quá khứ chứ không chỉ dự báo cho tương lai.',
  ]));
  o.push(P('Cần lưu ý rằng nếu bắt đầu thu thập dự báo từ hôm nay thì phải mất một năm mới đủ dữ liệu ghép cặp giữa dự báo và thực tế. Vì vậy nên ưu tiên nhà cung cấp có bán kèm dữ liệu dự báo lịch sử.'));

  o.push(H('9.2. Không có số liệu sản lượng', 2));
  o.push(P('Dữ liệu chỉ có công suất tức thời, đơn vị MW. Không có cột nào chứa sản lượng luỹ kế hay chỉ số công tơ, đơn vị MWh.'));
  o.push(P('Yêu cầu quy định mỗi kết quả dự báo phải xuất ra cả công suất và sản lượng cho từng khoảng thời gian. Với dữ liệu hiện có, sản lượng phải tính bằng tích phân công suất theo thời gian:'));
  o.push(codeBlock([
    '# Sản lượng trong khoảng 15 phút, đơn vị MWh',
    '# Dùng quy tắc hình thang trên chuỗi công suất 60 giây đã sắp xếp',
    '',
    'E = df["P"].resample("15min").apply(',
    '        lambda s: np.trapezoid(s.values, dx=60) / 3600.0',
    '    )',
    '',
    '# Điều kiện áp dụng: khoảng phải đủ số mẫu.',
    '# Nếu thiếu quá 20% số mẫu trong khoảng -> đánh dấu thiếu, KHÔNG ngoại suy.',
  ]));
  o.push(P('Hệ quả: sản lượng tính ra sẽ mang sai số của phép tích phân cộng với sai số do thiếu mẫu. Nên đối chiếu với chỉ số công tơ thương mại ít nhất một lần để xác định độ lệch hệ thống. Việc này cần đơn vị vận hành cung cấp bảng kê sản lượng theo tháng.'));

  o.push(H('9.3. Chỉ có một năm dữ liệu lịch sử', 2));
  o.push(P('Đã phân tích ảnh hưởng ở mục 8.3. Điểm chưa rõ là nguyên nhân. Chuỗi dài 370 ngày có thể do một trong ba lý do sau, và khảo sát trên một bản chụp không phân biệt được:'));
  o.push(...bullets([
    'Historian tại nhà máy có chính sách xoá dữ liệu cũ hơn khoảng một năm.',
    'Bước trích xuất trung gian chỉ lấy phạm vi một năm.',
    'Nhà máy chỉ mới có dữ liệu từ tháng 07/2025.',
  ]));
  o.push(P([run('Phân biệt được ba khả năng này là việc '), run('nên làm sớm', { bold: true }),
    run(' vì hệ quả khác hẳn nhau. Nếu là lý do thứ nhất thì mỗi ngày trôi qua mất vĩnh viễn một ngày dữ liệu cũ nhất, và cần lập lịch trích xuất định kỳ. Nếu là lý do thứ hai thì chỉ cần trích lại với phạm vi rộng hơn là có ngay chuỗi dài hơn. Cách kiểm nêu ở mục 11.1.')]));

  o.push(H('9.4. Thiếu thông số kỹ thuật nhà máy', 2));
  o.push(P('Hai thông số quan trọng nhất đã được đơn vị cung cấp trong quá trình khảo sát và ghi ở Bảng 5.3: toạ độ địa lý và công suất lắp đặt một chiều. Các thông số còn thiếu:'));
  o.push(table(
    ['Thông số', 'Dùng để làm gì', 'Mức cần'],
    [['Góc nghiêng và phương vị dàn pin', 'Quy đổi bức xạ ngang sang bức xạ mặt phẳng nghiêng', 'Cao'],
     ['Kiểu lắp đặt cảm biến bức xạ: ngang hay nghiêng', 'Chốt ngưỡng vật lý ở mục 7.4', 'Cao'],
     ['Loại giá đỡ: cố định hay xoay theo mặt trời', 'Ảnh hưởng lớn tới dạng đường công suất trong ngày', 'Cao'],
     ['Hệ số nhiệt độ của tấm pin', 'Mô hình hoá hiệu ứng nhiệt ở mục 8.1', 'Trung bình'],
     ['Số lượng và công suất bộ nghịch lưu', 'Xác định ngưỡng cắt ngọn chính xác', 'Trung bình'],
     ['Lịch bảo trì và vệ sinh tấm pin', 'Giải thích các bậc thay đổi hiệu suất', 'Trung bình']],
    [3300, 4600, 1738, ], { align: [null, null, C] }));
  o.push(P('Trong số này, góc nghiêng và phương vị dàn pin là thông số cấp thiết nhất, vì không có nó thì không quy đổi được bức xạ do nguồn dự báo cung cấp — vốn tính trên mặt ngang — sang mặt phẳng dàn pin. Kiểu lắp đặt cảm biến bức xạ đã bớt cấp thiết sau phép kiểm ở mục 6.3: hiện tượng buổi chiều sáng hơn buổi sáng đã xác định được là do khí quyển chứ không phải cảm biến lệch hướng. Câu hỏi này giờ chỉ còn phục vụ việc chốt ngưỡng vật lý ở mục 7.4.'));

  o.push(pageBreak());

  // ======================= 10. MÔ HÌNH DỮ LIỆU =======================
  o.push(H('10. Đề xuất mô hình dữ liệu chuẩn hoá', 1));
  o.push(P('Chương này mô tả cấu trúc dữ liệu đích và các quy tắc chuyển đổi, đủ chi tiết để triển khai trực tiếp.'));

  o.push(H('10.1. Lược đồ đích', 2));
  o.push(P('Đề xuất bốn bảng. Tách bạch giữa số liệu đo, trạng thái chất lượng và cấu hình.'));
  o.push(codeBlock([
    '-- Cấu hình nhà máy (FR-01)',
    'CREATE TABLE plant (',
    '    plant_id        text PRIMARY KEY,',
    '    name            text NOT NULL,',
    '    capacity_ac_mw  double precision NOT NULL,',
    '    capacity_dc_mw  double precision,',
    '    latitude        double precision NOT NULL,',
    '    longitude       double precision NOT NULL,',
    '    timezone        text NOT NULL DEFAULT \'Asia/Ho_Chi_Minh\',',
    '    status          text NOT NULL',
    ');',
    '',
    '-- Chuỗi đo đã chuẩn hoá — một dòng cho một điểm đo tại một thời điểm',
    'CREATE TABLE measurement (',
    '    plant_id    text        NOT NULL REFERENCES plant,',
    '    ts          timestamptz NOT NULL,   -- hiển thị theo GMT+7',
    '    variable    text        NOT NULL,   -- p_ac_mw, ghi_wm2, t_panel_c, ...',
    '    source      text        NOT NULL,   -- bảng và cột gốc',
    '    value       double precision,       -- NULL nghĩa là thiếu, KHÔNG dùng 0',
    '    quality     smallint    NOT NULL,   -- xem 10.4',
    '    PRIMARY KEY (plant_id, ts, variable)',
    ');',
    '',
    '-- Bảng ánh xạ từ điểm đo SCADA sang biến chuẩn (FR-03)',
    'CREATE TABLE tag_mapping (',
    '    mapping_version int   NOT NULL,',
    '    source_table    text  NOT NULL,',
    '    source_column   text  NOT NULL,',
    '    variable        text  NOT NULL,',
    '    unit_source     text  NOT NULL,',
    '    unit_target     text  NOT NULL,',
    '    scale           double precision NOT NULL DEFAULT 1.0,',
    '    offset_         double precision NOT NULL DEFAULT 0.0,',
    '    valid_min       double precision,',
    '    valid_max       double precision,',
    '    PRIMARY KEY (mapping_version, source_table, source_column)',
    ');',
    '',
    '-- Điểm kiểm tra tiếp nhận dữ liệu (FR-02) — theo mốc thời gian',
    'CREATE TABLE ingest_checkpoint (',
    '    source_table  text PRIMARY KEY,',
    '    last_ts_ticks bigint      NOT NULL,',
    '    last_run_utc  timestamptz NOT NULL,',
    '    rows_read     bigint      NOT NULL',
    ');',
  ]));

  o.push(H('10.2. Bảng ánh xạ điểm đo', 2));
  o.push(P('Nội dung khởi tạo cho phiên bản ánh xạ số 1, phục vụ FC-02:'));
  o.push(tblTitle('Bảng 10.1 — Ánh xạ điểm đo cho FC-02'));
  o.push(table(
    ['Bảng nguồn', 'Cột nguồn', 'Biến chuẩn', 'Đơn vị', 'Ngưỡng hợp lệ'],
    [
      ['His_131', '…Bay131_MEAS_P', 'p_ac_mw', 'MW', '−2 … 45'],
      ['His_131', '…Bay131_MEAS_Q', 'q_ac_mvar', 'MVAr', '−45 … 45'],
      ['Weather', 'SOLAR_WS_Rad_1', 'ghi_wm2', 'W/m²', '0 … 1.350'],
      ['Weather', 'SOLAR_WS_Rad_2', 'ghi_wm2_alt', 'W/m²', '0 … 1.350'],
      ['Weather', 'SOLAR_WS_Panel_T', 't_panel_c', '°C', '−10 … 90'],
      ['Weather', 'SOLAR_WS_Air_T', 't_air_c', '°C', '−10 … 55'],
      ['Weather', 'SOLAR_WS_Humidity', 'rh_pct', '%', '0 … 100'],
      ['Weather', 'SOLAR_WS_Wind_Speed', 'wind_ms', 'm/s', '0 … 60'],
      ['His_431', '…Bay431_MEAS_P', 'p_ac_mw_backup', 'MW', '−2 … 45'],
    ],
    [1500, 2600, 2100, 1200, 2238], { align: [null, null, null, C, C], size: 16 }));
  o.push(P('Ngưỡng hợp lệ đặt rộng hơn dải quan sát để không loại nhầm giá trị thật, nhưng đủ chặt để bắt được các trường hợp ở mục 7.3 và 7.4. Riêng ngưỡng bức xạ 1.350 W/m² đọc từ phân bố phần đuôi của chính dữ liệu, xem Bảng 7.3.'));
  o.push(P('Bản ghi khởi tạo cho bảng cấu hình nhà máy, dùng số liệu ở Bảng 5.3:'));
  o.push(codeBlock([
    "INSERT INTO plant (plant_id, name, capacity_ac_mw, capacity_dc_mw,",
    "                   latitude, longitude, timezone, status)",
    "VALUES ('FUJIWARA_BD', 'Fujiwara', 40.0, 50.0,",
    "        13.8634, 109.2708, 'Asia/Ho_Chi_Minh', 'ACTIVE');",
  ]));

  o.push(H('10.3. Quy tắc chuẩn hoá thời gian', 2));
  o.push(...bullets([
    [run('Bước 1 — Đọc và sắp xếp. ', { bold: true }), run('Mọi luồng nạp phải sắp xếp theo UTCTimestamp_Ticks trước khi làm bất cứ việc gì khác. Đây là hệ quả trực tiếp của mục 4.3.')],
    [run('Bước 2 — Khử trùng. ', { bold: true }), run('Với các mốc thời gian trùng, giữ bản ghi nhận được sau cùng và ghi nhật ký số bản bị loại. Trên toàn bộ dữ liệu khảo sát chỉ có 3 bản ghi thuộc trường hợp này.')],
    [run('Bước 3 — Quy đổi thời gian. ', { bold: true }), run('Chuyển mốc .NET sang kiểu timestamptz. Lưu theo giờ chuẩn quốc tế, hiển thị theo múi giờ nhà máy là GMT+7 — đúng yêu cầu FR-01.')],
    [run('Bước 4 — Áp lưới thời gian. ', { bold: true }), run('Gán mỗi mẫu vào ô 60 giây gần nhất. Ô nào không có mẫu thì để trống, không nội suy.')],
    [run('Bước 5 — Gộp lên 15 phút cho FC-02. ', { bold: true }), run('Chỉ được gộp từ độ phân giải mịn lên thô, đúng yêu cầu FR-03.')],
  ]));
  o.push(codeBlock([
    '# Quy tắc gộp 60 giây -> 15 phút',
    '# Công suất: lấy trung bình. Sản lượng: tích phân. Bức xạ: trung bình.',
    '',
    'MIN_COVERAGE = 0.80        # tối thiểu 12/15 mẫu trong ô 15 phút',
    '',
    'g = df.resample("15min", label="left", closed="left")',
    'out = pd.DataFrame({',
    '    "p_ac_mw":  g["p_ac_mw"].mean(),',
    '    "e_ac_mwh": g["p_ac_mw"].apply(lambda s: np.trapezoid(s, dx=60) / 3600),',
    '    "ghi_wm2":  g["ghi_wm2"].mean(),',
    '    "n_sample": g["p_ac_mw"].count(),',
    '})',
    '',
    '# Ô không đủ mẫu -> đánh dấu thiếu, KHÔNG gán 0 (yêu cầu FR-04)',
    'bad = out["n_sample"] < 15 * MIN_COVERAGE',
    'out.loc[bad, ["p_ac_mw", "e_ac_mwh", "ghi_wm2"]] = np.nan',
  ]));

  o.push(H('10.4. Quy tắc gắn cờ chất lượng', 2));
  o.push(P('Mỗi giá trị mang một mã chất lượng. Cách này cho phép truy vết lý do loại bản ghi, đúng yêu cầu FR-05.'));
  o.push(tblTitle('Bảng 10.2 — Mã chất lượng'));
  o.push(table(
    ['Mã', 'Tên', 'Điều kiện', 'Dùng để huấn luyện'],
    [
      ['0', 'OK', 'Giá trị nằm trong ngưỡng hợp lệ', 'Có'],
      ['1', 'MISSING', 'Không có mẫu trong ô thời gian', 'Không'],
      ['2', 'OUT_OF_RANGE', 'Ngoài ngưỡng của bảng ánh xạ', 'Không'],
      ['3', 'SPIKE', 'Biến thiên vượt 50% công suất lắp đặt trong một bước', 'Không'],
      ['4', 'STALE', 'Giá trị không đổi quá 30 phút liên tục, xét trên cả chuỗi', 'Không'],
      ['5', 'LOW_COVERAGE', 'Ô gộp có dưới 80% số mẫu', 'Không'],
      ['6', 'SENSOR_FROZEN', 'Cảm biến treo giá trị khi mất tín hiệu (mục 6.4)', 'Không'],
      ['7', 'FEEDER_OUTAGE', 'Có lộ 22 kV mất trong khi các lộ khác vẫn phát', 'Không'],
      ['8', 'ZERO_IN_DAYLIGHT', 'Bằng đúng 0 trong khoảng có bức xạ (mục 7.6)', 'Không'],
    ],
    [600, 1900, 4600, 2538], { align: [C, null, null, C], size: 16 }));

  o.push(P([run('Mã 8 là quy tắc đã chốt ở mục 7.6. Cài đặt:')]));
  o.push(codeBlock([
    '# Giá trị 0 trong khoảng có bức xạ = không có thông tin',
    '# Ban đêm giữ nguyên 0 vì đó là số đo thật',
    '',
    'NGUONG_BUC_XA = 50          # W/m2 — ranh giới ngày/đêm',
    '',
    'ban_ngay = df["ghi_wm2"] > NGUONG_BUC_XA',
    'la_zero  = df[cot].eq(0)',
    '',
    'df.loc[ban_ngay & la_zero, "quality_" + cot] = 8',
    'df.loc[ban_ngay & la_zero, cot]              = np.nan',
    '',
    '# Lưu ý: không áp dụng cho chính cột bức xạ khi nó bằng 0,',
    '# vì khi đó ban_ngay đã bằng False.',
  ]));

  o.push(P([run('Mã 6 áp dụng cho các đợt Rad_2 treo giá trị nêu ở mục 6.4. Dấu hiệu nhận biết gồm hai điều kiện đồng thời: giá trị gần như không đổi trong nhiều giờ, và các cảm biến khác của cùng trạm đều rỗng.')]));
  o.push(codeBlock([
    '# Phat hien doan cam bien treo gia tri (muc 6.4)',
    '# Dieu kien 1: bien do trong cua so 60 phut rat nho',
    '# Dieu kien 2: cam bien khac cua cung tram khong co du lieu',
    '',
    'W = 60                       # cua so 60 mau = 60 phut',
    'BIEN_DO_TOI_DA = 10.0        # W/m2',
    '',
    'bien_do = (df["ghi_wm2_alt"].rolling(W, center=True).max()',
    '           - df["ghi_wm2_alt"].rolling(W, center=True).min())',
    'tram_chet = df["ghi_wm2"].isna() & df["t_air_c"].isna()',
    '',
    'treo = (bien_do < BIEN_DO_TOI_DA) & tram_chet & df["ghi_wm2_alt"].notna()',
    '',
    'df.loc[treo, "quality_ghi_alt"] = 6',
    'df.loc[treo, "ghi_wm2_alt"]     = np.nan',
    '',
    '# Tren du lieu khao sat, quy tac nay bat duoc 14 dot / 329 gio.',
    '# KHONG dung phep tru hang so: trung vi ban dem cua Rad_2 bang 0,',
    '# tru di se khong thay doi gi ma van con nguyen 284 gio gia tri gia.',
  ]));
  o.push(P('Chỉ sau khi đã áp mã 6, Rad_2 mới được phép dùng để bù vào chỗ thiếu của Rad_1. Thứ tự ngược lại sẽ đưa giá trị giả vào đúng những khoảng không có gì để đối chiếu.'));

  o.push(P([run('Mã 7 là cơ chế phát hiện sự cố lộ nêu ở mục 5.5. Điều kiện phát hiện: trong nhóm bốn lộ 471, 473, 475, 477, nếu một lộ có công suất dưới 5% giá trị trung bình của ba lộ còn lại trong ít nhất ba bước liên tiếp, đánh dấu toàn bộ khoảng đó.')]));

  o.push(H('10.5. Quan hệ giữa các bảng nguồn', 2));
  o.push(P('Mục này nêu rõ một điểm mà nếu bỏ qua thì luồng nạp sẽ chạy không lỗi nhưng cho ra bảng rỗng.'));
  o.push(P([run('Các bảng nguồn '), run('không có khoá ngoại nào', { bold: true }),
    run('. Cột ID chạy đúng từ 0 đến n−1 ở mọi bảng, liên tục và không trùng — nó chỉ là số thứ tự dòng riêng của từng bảng, không mang ý nghĩa liên kết. Ghép His_131 với Weather theo ID cho lệch thời gian trung vị 133.034 giây, tức khoảng 1,5 ngày, và không có bản ghi nào lệch dưới 60 giây.')]));
  o.push(P('Mốc thời gian cũng không trùng khớp tuyệt đối giữa bất kỳ hai bảng nào. Mỗi bảng được historian ghi với độ lệch dưới giây riêng:'));
  o.push(tblTitle('Bảng 10.3 — Mức trùng khớp mốc thời gian giữa các bảng'));
  o.push(table(
    ['Cặp bảng', 'Số mốc trùng khít tuyệt đối', 'Tỷ lệ'],
    [['His_131 ∩ Weather', '0 / 521.103', '0,00%'],
     ['His_report ∩ His_131', '0 / 107.307', '0,00%'],
     ['His_report ∩ Weather', '0 / 107.307', '0,00%']],
    [3400, 3200, 3038], { align: [null, R, R], size: 16, redRows: [0, 1, 2] }));
  o.push(P('Nhưng chúng rất gần nhau. Từ mỗi mốc của His_131 tới mốc Weather gần nhất, trung vị 0,32 giây, phân vị 99 là 1,75 giây, và 99,56% tìm được trong vòng 30 giây. Nghĩa là thời gian là liên kết duy nhất, và phải ghép theo dung sai chứ không ghép bằng dấu bằng.'));
  o.push(tblTitle('Bảng 10.4 — Ba cách ghép, thử trên 100.000 bản ghi'));
  o.push(table(
    ['Cách ghép', 'Số bản ghi ghép được'],
    [['Ghép bằng dấu bằng trên mốc thời gian', '0'],
     ['Ghép mốc gần nhất, dung sai 30 giây', '99.970 / 100.000'],
     ['Làm tròn về lưới 60 giây rồi ghép', '99,47% số ô của His_131']],
    [6000, 3638], { align: [null, R], size: 16, redRows: [0] }));
  o.push(callout('Quy tắc bắt buộc', [
    'Không bao giờ ghép hai bảng nguồn bằng dấu bằng trên mốc thời gian, và không bao giờ dùng cột ID để ghép. Câu lệnh JOIN ON a.UTCTimestamp_Ticks = b.UTCTimestamp_Ticks trả về đúng 0 dòng và không sinh thông báo lỗi nào.',
    'Cách đúng là bước 4 ở mục 10.3: làm tròn mọi bảng về lưới 60 giây rồi mới ghép. Đây chính là lý do bước đó bắt buộc chứ không phải để cho gọn.',
    'Chỉ nạp các bản ghi có LogType = 1. Hai giá trị còn lại chiếm 0,017% số bản ghi, thiếu công suất tới 96–98% và cách nhau hàng chục nghìn giây — đó là bản ghi đánh dấu phiên ghi, không phải số đo. Cột NotSync toàn bộ bằng 0, không mang thông tin.',
  ], ORANGE));
  o.push(P([run('Một lưu ý về bảng His_report: nó '), run('không phải nguồn đo độc lập', { bold: true }),
    run('. So với His_131 trong dung sai 30 giây thì 90,49% bản ghi trùng khít tuyệt đối, chênh lệch trung vị 0,00000 MW. Đây là bản lấy mẫu lại của cùng luồng đo, nên không dùng để đối chứng chéo được. Ba lớp đo độc lập ở mục 5.2 là Bay131, Bay431 và nhóm lộ 22 kV, không tính His_report.')]));

  o.push(pageBreak());

  // ======================= 11. KIẾN NGHỊ =======================
  o.push(H('11. Kiến nghị', 1));

  o.push(H('11.1. Việc nên làm sớm', 2));
  o.push(P([run('Kỹ sư của đơn vị truy cập được cơ sở dữ liệu nhà máy bất cứ lúc nào, nên không có rủi ro mất quyền lấy dữ liệu. Hai việc dưới đây vẫn nên làm sớm vì lý do khác.')]));

  o.push(P([run('Việc thứ nhất — xác định chính sách lưu trữ của historian. ', { bold: true }),
    run('Mục 9.3 nêu ba khả năng giải thích vì sao chuỗi chỉ dài 370 ngày. Phân biệt được bằng một câu truy vấn duy nhất trên cơ sở dữ liệu nhà máy:')]));
  o.push(codeBlock([
    '-- Chạy trực tiếp trên CSDL của nhà máy, không phải trên bản trích xuất',
    'SELECT COUNT(*)                                        AS so_dong,',
    '       MIN("UTCTimestamp_Ticks")                       AS ticks_som_nhat,',
    '       MAX("UTCTimestamp_Ticks")                       AS ticks_moi_nhat,',
    '       (MAX("UTCTimestamp_Ticks") - MIN("UTCTimestamp_Ticks"))',
    '           / 10000000.0 / 86400                        AS so_ngay',
    '  FROM "His_131";',
  ]));
  o.push(table(
    ['Kết quả', 'Kết luận', 'Hành động'],
    [['Số ngày lớn hơn 370 đáng kể', 'Bước trích xuất giới hạn phạm vi', 'Trích lại với phạm vi rộng hơn — có ngay chuỗi dài hơn'],
     ['Số ngày xấp xỉ 370 và mốc sớm nhất trôi theo thời gian', 'Historian xoá dữ liệu cũ', 'Lập lịch trích xuất định kỳ'],
     ['Số ngày xấp xỉ 370 và mốc sớm nhất đứng yên', 'Nhà máy chỉ có dữ liệu từ 07/2025', 'Không làm gì thêm — chuỗi sẽ tự dài ra']],
    [2600, 3000, 4038], { size: 16 }));
  o.push(P('Cách phân biệt hai dòng cuối: chạy câu truy vấn hai lần cách nhau vài tuần và so mốc sớm nhất. Nếu mốc sớm nhất tiến lên thì historian đang xoá dần.'));

  o.push(P([run('Việc thứ hai — lập lịch trích xuất định kỳ. ', { bold: true }),
    run('Chỉ bắt buộc nếu kết quả trên rơi vào trường hợp historian xoá dữ liệu cũ. Khi đó khoảng cách giữa hai lần trích phải luôn nhỏ hơn phạm vi lưu trữ, nếu không sẽ thủng vĩnh viễn một đoạn.')]));
  o.push(P('Ngay cả khi không bắt buộc, vẫn nên trích theo tháng thay vì theo năm: một lần lỡ hạn là mất dữ liệu không lấy lại được; phát hiện sự cố thu thập sớm thay vì một năm sau mới biết; và khi FR-02 hoàn thành thì luồng đọc định kỳ đã có sẵn nên chi phí gần như bằng không. Toàn bộ một năm dữ liệu ở dạng cột nén chỉ khoảng 80 MB.'));

  o.push(P([run('Việc thứ ba — thống nhất khoá định danh bản ghi. ', { bold: true }),
    run('Khi vận hành chính thức, dữ liệu SCADA sẽ được đẩy sang theo dòng thời gian. Khoá định danh của một số đo vì vậy là bộ ba '),
    code('(nhà máy, thời điểm, biến)'),
    run(' như lược đồ ở mục 10.1, không dùng bất kỳ định danh nội bộ nào của hệ thống nguồn.')]));
  o.push(P('Điểm kiểm tra mà FR-02 yêu cầu cũng là mốc thời gian của bản ghi mới nhất đã nhận thành công. Cách này giữ đúng ngữ nghĩa dù dữ liệu được đẩy sang hay được đọc chủ động, và cho phép nhận lại một khoảng đã nhận mà không sinh bản ghi trùng.'));
  o.push(codeBlock([
    '-- Nhận dữ liệu: ghi đè theo khoá tự nhiên, an toàn khi nhận lại',
    'INSERT INTO measurement (plant_id, ts, variable, source, value, quality)',
    'VALUES (...)',
    'ON CONFLICT (plant_id, ts, variable) DO UPDATE',
    '   SET value   = EXCLUDED.value,',
    '       quality = EXCLUDED.quality;',
    '',
    '-- Nếu cần đọc chủ động để bù dữ liệu, lùi mốc một khoảng an toàn',
    '-- để bắt các bản ghi đến muộn. 5 phút = 3_000_000_000 tick',
    'SELECT * FROM "His_131"',
    ' WHERE "UTCTimestamp_Ticks" > :last_ticks - 3000000000',
    ' ORDER BY "UTCTimestamp_Ticks";',
  ]));
  o.push(P([run('Lưu ý bổ sung cho FR-02: yêu cầu nêu rõ hệ thống phải đọc an toàn khi SCADA vẫn đang ghi. Nên đặt mức cô lập giao dịch phù hợp, không giữ giao dịch mở lâu, và đọc theo lô theo khoảng thời gian với mỗi lô không quá một giờ dữ liệu. Vì đơn vị có quyền truy cập trực tiếp, điều kiện này kiểm thử được ngay trên hệ thống thật.')]));
  o.push(P([run('Nên lùi mốc đọc một khoảng an toàn để bắt các bản ghi đến muộn, và khử trùng ở phía nhận thay vì tin tuyệt đối vào mốc.')]));

  o.push(H('11.2. Việc đơn vị tự kiểm chứng được', 2));
  o.push(P('Vì kỹ sư truy cập được cơ sở dữ liệu nhà máy, hai câu hỏi sau tự trả lời được mà không cần chờ bên ngoài.'));
  o.push(tblTitle('Bảng 11.1 — Câu hỏi tự kiểm chứng'));
  o.push(table(
    ['#', 'Câu hỏi', 'Cách kiểm', 'Liên quan'],
    [
      ['A', 'Historian lưu trữ được bao lâu?', 'Câu truy vấn ở mục 11.1, chạy hai lần cách nhau vài tuần', '9.3'],
      ['B', 'Đọc dữ liệu khi SCADA đang ghi có an toàn không?', 'Chạy thử truy vấn đọc vào giờ cao điểm, đo thời gian và kiểm tra khoá', '11.1'],
    ],
    [500, 3300, 4000, 1838], { align: [C, null, null, C], size: 16 }));

  o.push(H('11.3. Câu hỏi cần đơn vị vận hành nhà máy trả lời', 2));
  o.push(P('Các câu hỏi dưới đây có đánh số để tiện trả lời từng mục. Thứ tự theo mức độ ảnh hưởng.'));
  o.push(tblTitle('Bảng 11.2 — Danh sách câu hỏi'));
  o.push(table(
    ['#', 'Câu hỏi', 'Vì sao cần', 'Liên quan'],
    [
      ['1', 'Sơ đồ một sợi của phần 22 kV?', 'Xác nhận vì sao hai nhóm lộ đều cộng ra tổng nhà máy', '5.2'],
      ['2', 'Cảm biến bức xạ lắp nằm ngang hay trên mặt phẳng nghiêng? Nếu nghiêng thì góc bao nhiêu?', 'Chốt ngưỡng vật lý. Phần lệch hướng đông–tây đã loại trừ được ở mục 6.3', '7.4'],
      ['3', 'Góc nghiêng, phương vị dàn pin và loại giá đỡ?', 'Quy đổi bức xạ ngang sang mặt phẳng dàn pin', '9.4'],
      ['4', 'Bảy lộ 431A–437 mất 190–200 ngày dữ liệu vì lý do gì?', 'Phân biệt sự cố thu thập với ngừng vận hành', '4.2'],
      ['5', 'Cột Data_PR do ai cấu hình, mẫu số dùng con số nào?', 'Xác nhận phát hiện ở mục 8.4 và sửa tại nguồn', '8.4'],
      ['6', 'Trạm khí tượng WS1 và WS2 có tồn tại vật lý không?', 'Quyết định có chờ dữ liệu hay loại khỏi thiết kế', '7.2'],
      ['7', 'Nhà máy có từng bị điều độ yêu cầu giảm phát trong giai đoạn 07/2025–07/2026?', 'Xác nhận kết luận mục 8.1 bằng nguồn độc lập', '8.1'],
      ['8', 'Bảng kê sản lượng theo tháng theo công tơ thương mại?', 'Hiệu chuẩn phép tích phân sản lượng', '9.2'],
      ['9', 'Lịch bảo trì, vệ sinh tấm pin, thay thế thiết bị?', 'Giải thích các bậc thay đổi hiệu suất trong chuỗi', '9.4'],
      ['10', 'Bảng CMB có kế hoạch thu thập không?', '1.602 điểm đo phía một chiều hiện đang bỏ trống', '3.2'],
      ['11', 'Điểm đo AI_P_LOW luôn bằng 0,3 là giá trị thật hay tín hiệu treo?', 'Loại bỏ hoặc giữ lại điểm đo', '8.2'],
    ],
    [500, 3300, 4000, 1838], { align: [C, null, null, C], size: 15, headSize: 15 }));
  o.push(P('Hai câu hỏi về toạ độ địa lý và công suất lắp đặt đã được trả lời trong quá trình khảo sát, kết quả ghi ở Bảng 5.3.'));

  o.push(H('11.4. Nguồn dữ liệu cần bổ sung', 2));
  o.push(P('Theo mục 9.1, cần một nguồn dự báo thời tiết số trị. Ba hướng, xếp theo mức độ phù hợp với dự án:'));
  o.push(table(
    ['Hướng', 'Ưu điểm', 'Nhược điểm'],
    [
      ['Dịch vụ thương mại chuyên cho điện mặt trời',
       'Có sẵn bức xạ đã hiệu chỉnh theo vệ tinh, có dữ liệu dự báo lịch sử để huấn luyện ngay',
       'Chi phí thuê bao theo năm'],
      ['Mô hình số trị toàn cầu miễn phí',
       'Không mất phí bản quyền',
       'Không có sẵn bức xạ đã hiệu chỉnh, phải tự lưu trữ dự báo trong một năm mới đủ dữ liệu huấn luyện'],
      ['Kết hợp: dùng dịch vụ thương mại cho giai đoạn thử nghiệm, song song tự lưu trữ nguồn miễn phí',
       'Có dữ liệu dùng ngay, đồng thời tích luỹ nguồn dự phòng',
       'Phải xây hai luồng thu thập'],
    ],
    [2900, 3400, 3338], { size: 16 }));
  o.push(P('Điểm cần nhấn mạnh khi đàm phán với nhà cung cấp: yêu cầu bán kèm dữ liệu dự báo lịch sử tối thiểu một năm cho đúng toạ độ nhà máy. Không có phần này thì không huấn luyện được mô hình cho tới khi tự tích luỹ đủ.'));

  o.push(H('11.5. Thứ tự triển khai đề xuất', 2));
  o.push(table(
    ['Giai đoạn', 'Nội dung', 'Điều kiện tiên quyết'],
    [
      ['A', 'Kiểm chứng ba câu hỏi ở Bảng 11.1', 'Không có — làm ngay, mất một buổi'],
      ['B', 'Chốt nhà cung cấp dữ liệu dự báo thời tiết', 'Không có — làm ngay'],
      ['C', 'Xây luồng nạp và chuẩn hoá theo Chương 10', 'Hoàn thành A'],
      ['D', 'Xây bộ kiểm soát chất lượng theo mục 10.4', 'Hoàn thành C'],
      ['E', 'Thu thập dự báo thời tiết', 'Hoàn thành B'],
      ['F', 'Huấn luyện mô hình thử nghiệm cho FC-02', 'Hoàn thành D và E'],
      ['G', 'Đánh giá theo gốc trượt', 'Hoàn thành F'],
    ],
    [1200, 4800, 3638], { align: [C, null, null] }));
  o.push(P('Giai đoạn B là đường găng của cả dự án. Nếu nhà cung cấp bán kèm dữ liệu dự báo lịch sử thì mô hình huấn luyện được ngay sau giai đoạn D. Nếu phải tự tích luỹ thì giai đoạn E kéo dài một năm, không rút ngắn được bằng nhân lực. Vì vậy nên chốt nhà cung cấp trước khi bắt tay vào giai đoạn C.'));
  o.push(P('Giai đoạn A chỉ mất một buổi nhưng gỡ được ba điều chưa chắc chắn còn lại trong báo cáo, nên đặt lên đầu.'));

  o.push(pageBreak());

  // ======================= 12. DAP UNG YEU CAU =======================
  o.push(H('12. Đánh giá khả năng đáp ứng yêu cầu', 1));
  o.push(P('Chương này trả lời câu hỏi trọng tâm của giai đoạn khảo sát: với dữ liệu hiện có, những yêu cầu nào trong tài liệu Mô tả yêu cầu phần mềm Solar Forecast làm được ngay, những yêu cầu nào còn vướng, và vướng ở đâu.'));

  o.push(H('12.1. Thang đánh giá', 2));
  o.push(table(
    ['Mức', 'Ý nghĩa'],
    [['Đáp ứng', 'Dữ liệu khảo sát đã đủ. Còn lại là việc lập trình.'],
     ['Đáp ứng có điều kiện', 'Làm được nhưng phải xử lý trước một vấn đề đã xác định rõ trong báo cáo này.'],
     ['Chưa đủ dữ liệu', 'Không thể làm cho tới khi bổ sung dữ liệu từ bên ngoài phạm vi bản trích xuất.'],
     ['Không phụ thuộc khảo sát', 'Yêu cầu về nền tảng phần mềm, không do dữ liệu quyết định. Khảo sát chỉ nêu ràng buộc nếu có.']],
    [2600, 7038], { size: 17 }));

  o.push(H('12.2. Phần AI làm được đến đâu', 2));
  o.push(P('Trước khi đối chiếu từng yêu cầu, cần tách bạch hai nguồn sai số của một hệ dự báo điện mặt trời. Thứ nhất là sai số của phép ánh xạ từ bức xạ và nhiệt độ sang công suất — phần này thuộc về mô hình học máy. Thứ hai là sai số của bản thân dự báo bức xạ — phần này thuộc về nguồn thời tiết, mô hình không cải thiện được.'));
  o.push(P('Đo được phần thứ nhất ngay trên dữ liệu khảo sát bằng cách cho mô hình biết trước bức xạ thật, tức giả định dự báo thời tiết hoàn hảo. Kết quả dưới đây đo bằng cây tăng cường gradient, đánh giá gốc trượt sáu lần, mỗi lần lấy một tháng làm tập kiểm định và toàn bộ phần trước đó làm tập huấn luyện, trên lưới 15 phút đúng như FC-02 yêu cầu. Số vòng lặp chọn bằng lát cắt theo thời gian trong chính tập huấn luyện, không dùng lát cắt ngẫu nhiên.'));
  o.push(callout('Cửa sổ tính chỉ số — cần chốt vào FR-07', [
    'Mọi chỉ số trong chương này chỉ tính trên phần ban ngày, ranh giới lấy theo góc cao mặt trời trên 0 độ. Ban đêm nhà máy không phát, phần công suất đo được là tự dùng, dao động quanh 0 trong dải ±0,1 MW.',
    [run('Ban đêm chiếm '), run('49,8% số ô nhưng chỉ 0,50% sản lượng cả năm', { bold: true }), run(' — 303 MWh trên 60.395 MWh. Nếu gộp chúng vào mẫu số thì chỉ số đẹp lên khoảng gấp đôi mà không phản ánh năng lực dự báo: mô hình nhà máy cho 2,35% khi tính cả ngày đêm và 4,43% khi chỉ tính ban ngày.')],
    'Vì vậy FR-07 cần quy định rõ cửa sổ tính chỉ số, và nên định nghĩa ranh giới theo góc cao mặt trời tính từ toạ độ chứ không theo bức xạ đo được — để chỉ số không phụ thuộc vào một cảm biến có thể hỏng. Nếu hợp đồng ghi NMAE tính trên toàn chuỗi thì con số sẽ đẹp gấp đôi một cách giả tạo.',
  ], RED));
  o.push(tblTitle('Bảng 12.1 — Sai số khi đã biết trước bức xạ, gốc trượt 6 tháng'));
  o.push(table(
    ['Chỉ số', 'Giá trị', 'Ghi chú'],
    [['MAE', '1,772 MW', 'Trung bình sáu tháng kiểm định'],
     ['RMSE', '2,592 MW', ''],
     ['NMAE theo 40 MW', '4,43%', 'Chỉ số chính theo FR-07'],
     ['WAPE', '10,73%', ''],
     ['MAPE trong khoảng có nắng', '14,53%', 'Không tính được trên toàn chuỗi, xem mục 7.5'],
     ['Bias', '−0,368 MW', 'Lệch âm, xem phần dưới'],
     ['R²', '0,942', ''],
     ['Số mẫu kiểm định', '7.784 ô', 'Sáu tháng, chỉ phần ban ngày']],
    [3000, 2000, 4638], { align: [null, R, null], size: 16 }));
  o.push(P('Sai số bám mùa rất rõ, nên một con số trung bình duy nhất sẽ gây hiểu nhầm:'));
  o.push(tblTitle('Bảng 12.2 — Sai số theo từng tháng kiểm định'));
  o.push(table(
    ['Tháng kiểm định', '02/2026', '03/2026', '04/2026', '05/2026', '06/2026', '07/2026'],
    [['NMAE', '7,77%', '6,46%', '4,03%', '3,54%', '2,89%', '1,91%'],
     ['MAE (MW)', '3,106', '2,583', '1,611', '1,414', '1,157', '0,764'],
     ['Bias (MW)', '−1,771', '−1,753', '−0,045', '+0,456', '+0,756', '+0,148']],
    [2400, 1200, 1200, 1200, 1200, 1200, 1238], { align: [null, R, R, R, R, R, R], size: 16 }));
  o.push(P('Tháng 2 khó gấp bốn lần tháng 7 — mùa nhiều mây ven biển. Khi cam kết chỉ số với chủ đầu tư phải nêu dải theo mùa chứ không nêu một con số trung bình.'));
  o.push(callout('Dòng Bias là bằng chứng cho cảnh báo ở mục 8.3', [
    'Hai tháng đầu năm mô hình lệch âm tới −1,77 MW, tức dự báo thiếu 4,4% công suất định mức một cách hệ thống. Các tháng còn lại lệch dương nhẹ.',
    'Nguyên nhân: chuỗi chỉ dài một chu kỳ mùa, nên khi kiểm định tháng 2 thì tập huấn luyện gần như toàn mùa khô. Mô hình chưa từng thấy mùa nhiều mây và dự báo theo thói quen của mùa nắng.',
    'Đây là điều mục 8.3 đã cảnh báo bằng lý luận, giờ đo được bằng số. Nó sẽ tự hết sau khi có năm dữ liệu thứ hai. Trong giai đoạn này cần ghi rõ trong báo cáo đánh giá rằng kết quả chưa kiểm chứng được tính ổn định qua nhiều năm.',
  ], ORANGE));
  o.push(callout('Con số cần nhớ', [
    [run('Nếu dự báo bức xạ đúng tuyệt đối thì sai số dự báo công suất còn '), run('4,43% công suất xoay chiều', { bold: true }), run(' tính trung bình sáu tháng, dao động từ 1,91% mùa khô tới 7,77% mùa nhiều mây. Đó là trần khả năng của phần học máy trên bộ dữ liệu này.')],
    'Phần khó của bài toán không nằm ở mô hình AI mà nằm ở chất lượng dự báo bức xạ. Mọi sai số vượt quá mức trên đều đến từ nguồn thời tiết chứ không phải từ thuật toán. Đây là căn cứ để không kỳ vọng quá mức vào việc thay đổi kiến trúc mô hình.',
    'Một bảng tra hai chiều đơn thuần cũng đạt gần bằng cây tăng cường. Hàm cần học gần như là hàm trơn một chiều theo bức xạ, nên thuật toán không phải là đòn bẩy ở bài toán này.',
  ], GREEN));

  o.push(H('12.3. Bộ biến đầu vào nào thực sự đóng góp', 2));
  o.push(P('Câu hỏi hay gặp là có nên đưa toàn bộ dữ liệu khí tượng vào mô hình hay không. Đo trực tiếp bằng cách bỏ dần từng nhóm biến, chấm trên cùng một tập mẫu và cùng bộ fold. Cột dùng để so là MAE ban ngày, vì MAE toàn bộ bị pha loãng bởi ban đêm khi công suất gần 0 và mô hình nào cũng đoán đúng.'));
  o.push(tblTitle('Bảng 12.3 — Đóng góp của từng nhóm biến đầu vào'));
  o.push(table(
    ['Bộ biến đầu vào', 'MAE ban ngày (MW)', 'So với chỉ bức xạ'],
    [['Chỉ bức xạ', '2,053', '—'],
     ['+ hình học mặt trời (góc cao, góc giờ)', '1,817', 'tốt hơn 11,5%'],
     ['+ nhiệt độ tấm pin', '1,778', 'tốt hơn 13,4%'],
     ['+ nhiệt độ không khí, độ ẩm, tốc độ gió', '1,933', 'tụt lại, xấu hơn 8,7%']],
    [4200, 2400, 3038], { align: [null, R, null], size: 16, boldRows: [2] }));
  o.push(P('Hai kết luận. Thứ nhất, hình học mặt trời tính từ toạ độ đóng góp nhiều nhất trong các biến bổ sung — và nó không tốn thêm phép đo nào, chỉ cần vĩ độ, kinh độ và thời điểm. Thứ hai, ba biến khí tượng còn lại không chỉ vô dụng mà còn có hại, dù cây tăng cường vốn có khả năng tự bỏ qua biến yếu.'));
  o.push(P('Một giới hạn của phép đo này cần ghi rõ: để bốn dòng chấm trên cùng một tập mẫu thì phải loại các ô thiếu bất kỳ biến nào trong bảy biến, mà nhiệt độ không khí và độ ẩm đã chết từ tháng 5/2026 (mục 6.6). Tập còn lại chỉ 1.994 ô ban ngày. Thứ tự giữa bốn dòng ổn định qua nhiều lần chạy với cấu hình khác nhau, nhưng biên độ chênh lệch thì chưa nên coi là chính xác tới từng phần trăm.',
    { size: 19 }));
  o.push(P('Phép hoán vị cho kết quả trùng khớp. Xáo trộn ngẫu nhiên từng cột rồi đo sai số tăng bao nhiêu: bức xạ +7,159 MW, góc cao mặt trời +0,181, nhiệt độ tấm pin +0,136, góc giờ +0,035, nhiệt độ không khí +0,003, tốc độ gió −0,015, độ ẩm −0,080. Hai giá trị âm nghĩa là xáo trộn cột đó lại làm mô hình tốt lên, tức cột đó chỉ mang nhiễu.'));
  o.push(callout('Bộ biến đề nghị', [
    'Bức xạ, góc cao và góc giờ mặt trời, nhiệt độ tấm pin. Bốn biến, trong đó hai biến tính được từ toạ độ.',
    'Không đưa độ ẩm, tốc độ gió và nhiệt độ không khí vào mô hình công suất. Riêng tốc độ gió và nhiệt độ không khí vẫn cần giữ lại nếu sau này phải dự báo nhiệt độ tấm pin cho FC-02, vì chúng là đầu vào của mô hình nhiệt.',
    'Cảnh báo về phạm vi: kết luận này đúng với một chu kỳ mùa và một cảm biến đặt tại một điểm. Có thêm vài năm dữ liệu, hoặc có nhiệt độ đo tại nhiều vị trí trong cánh đồng pin, thì thứ tự có thể đổi. Nên đo lại định kỳ chứ không coi là chốt vĩnh viễn.',
  ], ORANGE));
  o.push(H('12.4. FC-01 làm được đến mức nào', 2));
  o.push(P('Với FC-01, dữ liệu tại chỗ đã đủ để huấn luyện và đánh giá một mô hình dự báo hoàn chỉnh, không cần nguồn thời tiết ngoài. Mô hình dùng đặc trưng trễ của công suất và bức xạ, chỉ số trời quang, độ biến động mây, cộng hình học mặt trời tại thời điểm cần dự báo — thứ tính trước được từ toạ độ nên không phải rò rỉ dữ liệu tương lai.'));
  o.push(P('Hai mốc đối chiếu bắt buộc phải vượt qua thì mô hình mới có giá trị. Cả ba dòng của mỗi tầm dự báo đều chấm trên đúng cùng một tập mẫu.'));
  o.push(tblTitle('Bảng 12.4 — FC-01 so với mốc đối chiếu, NMAE theo 40 MW'));
  o.push(table(
    ['Tầm dự báo', 'Quán tính thô', 'Quán tính chỉ số trời quang', 'Mô hình'],
    [['15 phút', '4,87%', '5,99%', '3,77%'],
     ['30 phút', '8,21%', '7,12%', '5,53%'],
     ['1 giờ', '14,08%', '8,76%', '7,39%'],
     ['2 giờ', '23,68%', '12,47%', '8,76%'],
     ['4 giờ', '36,75%', '21,12%', '10,29%']],
    [2000, 2400, 2800, 2438], { align: [C, R, R, R], size: 16, boldRows: [4] }));
  o.push(P('Mô hình thắng cả hai mốc ở mọi tầm dự báo, và khoảng cách nới rộng theo tầm. Ở 15 phút mô hình tốt hơn mốc tốt nhất 22,5%; ở 4 giờ tốt hơn 51,3%, tức chưa bằng một nửa sai số. Độ lệch hệ thống của mô hình giữ quanh −0,3 MW ở mọi tầm, trong khi hai mốc đối chiếu lệch tới −4,6 và −6,9 MW ở tầm 4 giờ. Hệ số R² ở tầm 4 giờ: mô hình 0,724, quán tính theo chỉ số trời quang 0,098, quán tính thô âm.'));
  o.push(P('Độ suy giảm theo tầm cũng thoải hơn hẳn hai mốc: từ 3,77% ở 15 phút lên 10,29% ở 4 giờ, tức tầm dài gấp 16 lần mà sai số chỉ tăng 2,7 lần, trong khi quán tính thô tăng 7,5 lần. Nghĩa là hình học mặt trời và chỉ số trời quang gánh phần lớn tín hiệu, phần dành cho việc đoán mây chỉ chiếm phần nhỏ.'));
  o.push(callout('Ý nghĩa cho thứ tự triển khai', [
    [run('FC-01 ở tầm 4 giờ đạt '), run('NMAE 10,29% tính trên phần ban ngày', { bold: true }), run(', hoàn toàn bằng dữ liệu hiện có. Đây không phải phương án tạm bợ trong lúc chờ nguồn thời tiết mà là một chức năng dùng được thật.')],
    'FC-02 ở tầm một ngày thì không có con số nào tương đương tính được từ dữ liệu hiện tại, vì toàn bộ độ chính xác phụ thuộc vào nguồn dự báo thời tiết chưa có. Trần 4,43% ở Bảng 12.1 là giới hạn dưới của nó, không phải giá trị kỳ vọng.',
    'Lưu ý khi so với tài liệu bên ngoài: nhiều nhà cung cấp công bố chỉ số tính trên toàn chuỗi kể cả ban đêm, nên con số của họ nhìn nhỏ hơn khoảng một nửa. Khi so sánh phải hỏi rõ cửa sổ tính.',
  ], GREEN));

  o.push(H('12.5. Bốn chức năng dự báo', 2));
  o.push(tblTitle('Bảng 12.5 — Đối chiếu FC-01 đến FC-04'));
  o.push(table(
    ['Mã', 'Ưu tiên', 'Mức đáp ứng', 'Căn cứ'],
    [['FC-01 — 4 giờ tới, 5/10/15 phút', '2', 'Đáp ứng',
      'Đã huấn luyện và đánh giá xong trên dữ liệu thật: NMAE 10,29% ở tầm 4 giờ, 3,77% ở tầm 15 phút, tính trên phần ban ngày — xem Bảng 12.4. Không cần nguồn thời tiết ngoài. Nguồn 60 giây cho phép xuống tới độ phân giải 5 phút mà vẫn đúng quy tắc chỉ gộp từ mịn lên thô của FR-03.'],
     ['FC-02 — 1 ngày tới, 15 phút', '1', 'Chưa đủ dữ liệu',
      'Bức xạ ngày mai không suy ra được từ bức xạ hôm nay. Bắt buộc có nguồn dự báo thời tiết số trị, và bắt buộc có bản lưu dự báo trong quá khứ của chính nguồn đó để huấn luyện. Chi tiết ở mục 9.1.'],
     ['FC-03 — 2 ngày tới, 30 phút', '3', 'Chưa đủ dữ liệu', 'Cùng điều kiện với FC-02. Sai số tăng theo tầm dự báo của nguồn thời tiết.'],
     ['FC-04 — 7 ngày tới, 30 phút', '4', 'Chưa đủ dữ liệu',
      'Cùng điều kiện với FC-02. Ở tầm bảy ngày, dự báo bức xạ tiệm cận mức khí hậu học, nên cần định nghĩa trước thế nào là đạt để tránh đánh giá theo kỳ vọng sai.']],
    [2400, 900, 1700, 4638], { align: [null, C, C, null], size: 16 }));
  o.push(callout('Nghịch lý thứ tự ưu tiên', [
    'FC-02 được đặt ưu tiên 1 và ghi rõ là trọng tâm giai đoạn này, nhưng lại là chức năng duy nhất bị chặn hoàn toàn bởi một dữ liệu chưa có. FC-01 đặt ưu tiên 2 nhưng làm được ngay hôm nay bằng dữ liệu trong tay.',
    'Đề nghị: giữ nguyên thứ tự ưu tiên nghiệp vụ, nhưng đảo thứ tự thực hiện. Làm FC-01 trước để dựng và kiểm chứng toàn bộ luồng nạp, chuẩn hoá, huấn luyện, đánh giá và phát hành trên dữ liệu thật. Khi nguồn dự báo thời tiết về, FC-02 chỉ còn là việc thay bộ biến đầu vào chứ không phải xây lại từ đầu.',
    'Cách này biến thời gian chờ nguồn thời tiết thành thời gian làm việc thay vì thời gian chết.',
  ], ORANGE));
  o.push(P([run('Hai yêu cầu chung của nhóm FC cũng cần lưu ý. Thứ nhất, mỗi chức năng phải xuất cả công suất và sản lượng: dữ liệu hiện không có cột sản lượng nào nên phải tính bằng tích phân công suất, và cần bảng kê công tơ để hiệu chuẩn — nêu ở mục 9.2. Thứ hai, quy định '),
    run('không được lấy kết quả của một mô hình rồi đổi nhãn hoặc nội suy thành kết quả của chức năng khác', { italics: true }),
    run(' ràng buộc thiết kế: FC-01 ở 5 phút và FC-02 ở 15 phút phải là hai bộ dữ liệu và hai mô hình riêng. Dữ liệu nguồn 60 giây cho phép làm đúng như vậy.')]));

  o.push(H('12.6. Yêu cầu chức năng FR-01 đến FR-11', 2));
  o.push(tblTitle('Bảng 12.6 — Đối chiếu yêu cầu chức năng'));
  o.push(table(
    ['Mã', 'Mức đáp ứng', 'Ghi chú từ kết quả khảo sát'],
    [['FR-01 — Thông tin nhà máy', 'Đáp ứng',
      'Đã có toạ độ, công suất một chiều và xoay chiều, múi giờ, điểm đo mục tiêu. Bắt buộc tách hai trường công suất, xem lưu ý ở mục 5.4.'],
     ['FR-02 — Kết nối dữ liệu', 'Đáp ứng có điều kiện',
      'Nguồn là PostgreSQL 16.3, đúng loại được ưu tiên. Nhưng khảo sát chạy trên bản chụp nên chưa kiểm chứng được việc đọc an toàn khi SCADA đang ghi và việc lưu checkpoint. Cần thử trực tiếp trên hệ thống nhà máy, xem mục 11.1.'],
     ['FR-03 — Mapping và chuẩn hoá', 'Đáp ứng',
      'Quy ước tên điểm đo có cấu trúc rõ nên tách tự động được. Bảng ánh xạ khởi tạo đã có ở mục 10.2. Lưu ý: bảng gộp His_report chỉ có chu kỳ 300 giây nên không dùng được cho FC-01 ở 5 phút; phải lấy từ His_131 và Weather ở 60 giây.'],
     ['FR-04 — Kiểm soát chất lượng', 'Đáp ứng',
      'Cả bảy tiêu chí đã kiểm và có hướng xử lý, tổng hợp ở Bảng 7.6. Bộ mã chất lượng đề xuất ở mục 10.4.'],
     ['FR-05 — Tạo và quản lý bộ dữ liệu', 'Đáp ứng có điều kiện',
      'Điểm khó nhất của cả nhóm FR. Yêu cầu chỉ được dùng dữ liệu tồn tại tại thời điểm phát hành, nhưng bản chụp một thời điểm không cho biết độ trễ thực tế của từng bảng. Phải đo trên hệ thật trước khi chốt thiết kế. Ngoài ra nhóm điểm đo IEC104 chứa chính công suất phát nên phải chặn khỏi tập biến đầu vào, xem mục 8.2.'],
     ['FR-06 — Huấn luyện và tái huấn luyện', 'Không phụ thuộc khảo sát',
      'Ràng buộc duy nhất từ dữ liệu: chuỗi chỉ dài một chu kỳ mùa nên vài lần tái huấn luyện đầu vẫn nằm trong cùng một năm, chưa kiểm chứng được tính ổn định qua nhiều năm. Xem mục 8.3.'],
     ['FR-07 — Đánh giá và so sánh', 'Đáp ứng có điều kiện',
      'Ba ràng buộc đã xác định: không dùng MAPE trên toàn chuỗi vì ban đêm mẫu số tiến về 0; NMAE phải chuẩn hoá theo 40 MW xoay chiều; và bắt buộc dùng gốc trượt vì không tách được tập kiểm định độc lập theo mùa. Xem mục 7.5 và 8.3.'],
     ['FR-08 — Chạy dự báo', 'Không phụ thuộc khảo sát',
      'Ràng buộc từ dữ liệu: sản lượng của từng chu kỳ phải tính bằng tích phân công suất và cần hiệu chuẩn theo công tơ, xem mục 9.2.'],
     ['FR-09 — Lập lịch và quản lý tác vụ', 'Không phụ thuộc khảo sát',
      'Lịch chạy theo múi giờ nhà máy, dữ liệu lưu theo giờ chuẩn quốc tế — hai điều này nhất quán với quy ước ở mục 3.4.'],
     ['FR-10 — Quản lý kết quả', 'Không phụ thuộc khảo sát',
      'Khi ghép dự báo với thực tế để tính lại sai số, phải loại các bản ghi mang cờ chất lượng xấu, nếu không sẽ so dự báo với dữ liệu rác. Bộ cờ ở mục 10.4 đủ dùng cho việc này.'],
     ['FR-11 — Giao diện Web và REST API', 'Không phụ thuộc khảo sát', 'Không có ràng buộc nào phát sinh từ dữ liệu.']],
    [2200, 1900, 5538], { align: [null, C, null], size: 15, headSize: 16 }));
  o.push(P('Về yêu cầu triển khai: chạy được trên Windows và Linux không bị dữ liệu ràng buộc. Riêng yêu cầu chạy trên phần cứng nhúng với mô hình rút gọn thì các kết quả ở mục 12.2 là tin tốt — mô hình tốt nhất chỉ dùng bốn biến đầu vào và một bảng tra hai chiều cũng đạt gần bằng, nhẹ đến mức chạy được trên hầu như mọi phần cứng. Không cần mô hình lớn để đạt kết quả tốt trên bài toán này.'));

  o.push(H('12.7. Những điểm phải làm rõ', 2));
  o.push(P('Danh sách dưới đây xếp theo mức độ chặn tiến độ, không theo thứ tự yêu cầu. Bốn mục đầu phải có câu trả lời trước khi chốt thiết kế.'));
  o.push(tblTitle('Bảng 12.7 — Điểm cần làm rõ, xếp theo mức độ chặn'));
  o.push(table(
    ['#', 'Điểm cần làm rõ', 'Chặn cái gì', 'Hỏi ai'],
    [['1', 'Chọn nguồn dự báo thời tiết nào, và nguồn đó có bán kèm bản lưu dự báo lịch sử tối thiểu một năm không?',
      'FC-02, FC-03, FC-04 — tức toàn bộ phần ưu tiên 1. Là đường găng của dự án.', 'Chủ đầu tư và nhà cung cấp'],
     ['2', 'Độ trễ thực tế của dữ liệu SCADA: một số đo tại thời điểm T thì đến khi nào mới đọc được?',
      'FR-05. Không biết con số này thì không thực thi được quy tắc chống rò rỉ dữ liệu tương lai, và mọi kết quả đánh giá đều đáng ngờ.', 'Kỹ sư vận hành, đo trực tiếp'],
     ['3', 'Góc nghiêng, phương vị dàn pin và loại giá đỡ cố định hay xoay.',
      'Chất lượng quy đổi bức xạ ngang của nguồn dự báo sang mặt phẳng dàn pin. Ảnh hưởng trực tiếp tới sai số FC-02.', 'Đơn vị vận hành'],
     ['4', 'Ngưỡng nào được coi là đạt chất lượng cho từng chức năng dự báo?',
      'FR-07 yêu cầu phân biệt chạy thành công với đạt chất lượng, nhưng tài liệu yêu cầu chưa nêu ngưỡng số nào.', 'Chủ đầu tư'],
     ['5', 'Phạm vi triển khai: một nhà máy hay nhiều, và có bao gồm điện mặt trời mái nhà không?',
      'Mục tiêu dự án có nhắc tới điện mặt trời mái nhà nhưng dữ liệu khảo sát chỉ có một nhà máy quy mô lớn. Hai loại này khác nhau về cấu trúc đo và về cách chuẩn hoá.', 'Chủ đầu tư'],
     ['6', 'Bảng kê sản lượng theo công tơ thương mại.',
      'Hiệu chuẩn phép tích phân sản lượng mà FC-01 đến FC-04 đều bắt buộc phải xuất.', 'Đơn vị vận hành'],
     ['7', 'Cấu hình phần cứng nhúng mục tiêu.',
      'Quyết định mô hình rút gọn tới mức nào. Theo Bảng 12.1 thì ràng buộc này nhẹ hơn tưởng.', 'Chủ đầu tư'],
     ['8', 'Chính sách lưu trữ của historian tại nhà máy.',
      'Quyết định có phải lập lịch trích xuất định kỳ hay không. Cách kiểm nêu ở mục 11.1.', 'Tự kiểm chứng được'],
    ],
    [500, 3200, 3600, 2338], { align: [C, null, null, null], size: 15, headSize: 16 }));

  o.push(H('12.8. Kết luận', 2));
  o.push(callout('Trả lời câu hỏi trọng tâm', [
    [run('Dữ liệu vận hành hiện có đủ chất lượng để xây dựng mô hình dự báo. Biến mục tiêu sạch, độ phủ 98%, quan hệ vật lý với bức xạ rõ ràng, và khi cho biết trước bức xạ thì sai số là '), run('4,43%', { bold: true }), run(' công suất xoay chiều, tính trên phần ban ngày. Phần học máy của bài toán này không khó.')],
    [run('FC-01 không còn là dự đoán trên giấy: đã huấn luyện và đánh giá theo gốc trượt, đạt '), run('NMAE 10,29% ở tầm 4 giờ', { bold: true }), run(' và 3,77% ở tầm 15 phút, thắng cả hai mốc đối chiếu ở mọi tầm với khoảng cách nới rộng theo tầm. Toàn bộ bằng dữ liệu hiện có.')],
    'Chín trong mười một yêu cầu chức năng làm được ngay hoặc chỉ vướng một điểm đã xác định rõ. Không có yêu cầu nào bị chặn bởi chất lượng dữ liệu vận hành.',
    'Điểm chặn duy nhất và cũng là điểm quan trọng nhất: không có dữ liệu dự báo thời tiết. Ba trong bốn chức năng dự báo — trong đó có chức năng ưu tiên 1 — không thực hiện được cho tới khi có nguồn này kèm bản lưu lịch sử. Đây là việc mua sắm và đàm phán, không phải việc kỹ thuật, nên cần khởi động sớm nhất có thể.',
    'Khuyến nghị hành động: chốt nguồn dự báo thời tiết song song với việc đưa FC-01 vào vận hành. FC-01 dùng được toàn bộ dữ liệu hiện có, cho phép kiểm chứng luồng nạp và bộ chỉ số đánh giá trên dữ liệu thật, và khi nguồn thời tiết về thì FC-02 chỉ còn là bước thay bộ biến đầu vào.',
  ], NAVY));

  o.push(pageBreak());

  // ======================= PHỤ LỤC =======================
  o.push(H('Phụ lục A. Danh mục bảng và số cột', 1));
  o.push(table(
    ['Bảng', 'Số cột', 'Số bản ghi', 'Kích thước CSV'],
    J.tables.map(t => [t.name, int(t.ncol), int(t.rows),
      t.bytes ? (t.bytes / 1048576).toFixed(1).replace('.', ',') + ' MB' : '—']),
    [3000, 1800, 2400, 2438], { align: [null, R, R, R] }));

  o.push(H('Phụ lục B. Hồ sơ thống kê chi tiết', 1));
  o.push(P([run('Hồ sơ đầy đủ của toàn bộ điểm đo được lưu ở tệp '), code('column_profile.csv'),
    run('. Mỗi dòng ứng với một cột của một bảng, gồm các trường: tỷ lệ thiếu, tỷ lệ bằng 0, tỷ lệ âm, số giá trị khác nhau, cờ hằng số, giá trị nhỏ nhất, các phân vị 1, 25, 50, 75, 99, giá trị lớn nhất, trung bình, độ lệch chuẩn, và vai trò vật lý được phân loại tự động.')]));
  o.push(P([run('Hồ sơ trục thời gian lưu ở '), code('time_profile.csv'), run(', gồm 17 dòng ứng với 17 bảng có dữ liệu.')]));

  o.push(H('Phụ lục C. Trục thời gian đầy đủ', 1));
  o.push(table(
    ['Bảng', 'Bước mẫu', 'Phân bố khoảng cách giữa các mẫu'],
    T.map(t => [t.table, t.nominal_s + ' s', t.top_int]),
    [1800, 1200, 6638], { align: [null, C, null], size: 15, headSize: 15 }));

  o.push(H('Phụ lục D. Bộ công cụ khảo sát', 1));
  o.push(P('Ba tập lệnh Python được viết riêng cho khảo sát này. Không phụ thuộc vào việc cài đặt PostgreSQL, chạy được trên Windows và Linux.'));
  o.push(table(
    ['Tập lệnh', 'Chức năng'],
    [['pgdump_reader.py', 'Giải mã định dạng lưu trữ nhị phân, đọc lược đồ và khối dữ liệu nén'],
     ['export_to_csv.py', 'Trích xuất toàn bộ bảng ra CSV, quy đổi mốc thời gian, giữ nguyên giá trị trống'],
     ['analyze_dataset.py', 'Lập hồ sơ thống kê, kiểm chứng vật lý, sinh báo cáo và biểu đồ']],
    [2400, 7238]));
  o.push(P('Cách chạy lại toàn bộ khảo sát:'));
  o.push(codeBlock([
    'pip install pandas numpy matplotlib tabulate',
    '',
    'cd tools',
    'python pgdump_reader.py  ../db_fujiwara.sql',
    'python export_to_csv.py  ../db_fujiwara.sql -o ../data/csv --tz 7',
    'python analyze_dataset.py ../data/csv -o ../data/report --tz 7 --plots',
  ]));
  o.push(P('Thời gian chạy tham khảo: bước trích xuất khoảng 70 giây, bước phân tích khoảng 30 giây.'));

  o.push(H('Phụ lục E. Nhật ký kiểm chứng', 1));
  o.push(P('Mỗi kết luận chính trong báo cáo kèm một phép kiểm độc lập. Bảng dưới liệt kê phép kiểm và kết quả.'));
  o.push(table(
    ['Kết luận', 'Phép kiểm', 'Kết quả'],
    [
      ['Buổi chiều sáng hơn buổi sáng',
       'So trọng tâm đỉnh bức xạ với giữa trưa mặt trời tính từ toạ độ',
       'Đỉnh chậm 38 phút; cả Rad_1 và Rad_2 cho cùng con số'],
      ['Quy đổi múi giờ GMT+7 đúng',
       'So mốc giữa ngày đo được với giữa trưa mặt trời tính từ kinh độ',
       'Đo 11:44 — tính 11:43; lệch 1,4 phút'],
      ['Bất đối xứng sáng chiều do khí quyển, không do cảm biến lệch hướng',
       'Xét tỷ số công suất trên bức xạ theo giờ trong ngày',
       'Tỷ số phẳng 75,9–79,2% từ 07 đến 17 giờ, không có xu hướng theo chiều'],
      ['Rad_2 treo giá trị chứ không lệch điểm không',
       'Xét phân bố ban đêm thay vì trung bình; truy ngược các mẫu bất thường',
       '95,6% mẫu ban đêm bằng đúng 0; phần còn lại gom thành 14 đợt / 329 giờ'],
      ['Ba cảm biến bức xạ hỏng đồng pha',
       'Đối chiếu thời điểm thiếu của Rad_1 với trạng thái của Rad_2 và WSRT1',
       '92,8% chỗ thiếu của Rad_1 trùng đợt Rad_2 treo; WSRT1 chỉ phủ 15,0%'],
      ['Offset không phải nguyên nhân làm tương quan Rad_2 thấp',
       'Tính lại hệ số sau khi dịch chuyển hằng số, và sau khi loại các đợt treo',
       'r(Rad_2 − 26,05) = r(Rad_2) = 0,86285; loại đợt treo thì r = 0,958'],
      ['Công suất một chiều 50 MWp',
       'Tính tỷ số công suất phát trên công suất một chiều nhân bức xạ chuẩn hoá',
       'Trung vị 75,2%, phân vị 95 là 85,6% — đúng dải bình thường'],
      ['Nhà máy không bị cắt ngọn',
       'Đếm mẫu sát ngưỡng và tính độ lệch chuẩn của nhóm đỉnh',
       '14/107.307 mẫu vượt 39 MW; độ lệch chuẩn 0,29 MW'],
      ['Thứ tự lưu trữ trùng ranh giới trang đĩa',
       'Đối chiếu chu kỳ đảo lộn với số cột của ba bảng khác nhau',
       '18 cột → 72 dòng; 15 cột → 84 dòng; 69 cột → 25 dòng'],
      ['Bay131 là điểm đấu nối, biến mục tiêu',
       'Đối chiếu ba lớp đo độc lập',
       'Cả ba cho cùng 22,4 MW, tương quan trên 0,998'],
      ['Không có cắt giảm công suất theo lệnh điều độ',
       'Xét phân bố công suất theo dải bức xạ',
       'Công suất tăng đơn điệu, không có trần phẳng'],
      ['Điểm đo IEC104 không phải lệnh giới hạn',
       'Kiểm tra dạng đường theo giờ trong ngày',
       'Có dạng hình chuông đỉnh 12 giờ, giống công suất phát'],
      ['Data_PR dùng mẫu số là công suất xoay chiều',
       'Suy ngược mẫu số từ công thức hệ số hiệu suất',
       'Trung vị 38,22 MW, không phải 50 MWp'],
      ['Bức xạ có phần đuôi bất thường',
       'Đếm số mẫu vượt từng mức trên toàn chuỗi',
       'Trên 1.350 W/m² chỉ còn 1 và 18 mẫu trên nửa triệu'],
      ['Chuỗi sau sắp xếp đủ đều để gộp 15 phút',
       'Tính phân vị 95 và 99 của khoảng cách mẫu',
       'Cả hai xấp xỉ 60 giây'],
    ],
    [2700, 3600, 3338], { size: 15, headSize: 15 }));

  return o;
};
