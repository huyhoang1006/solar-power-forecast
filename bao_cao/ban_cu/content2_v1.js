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
  o.push(P('Một khả năng cần loại trừ khi rà lại: nếu cảm biến đặt trên mặt phẳng nghiêng chứ không nằm ngang thì giá trị đo được sẽ cao hơn bức xạ trên mặt ngang ở một số thời điểm trong ngày. Điều này cũng liên quan tới hiện tượng nêu ở mục 6.3, và cùng được giải đáp bằng một câu hỏi với đơn vị vận hành.'));

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
  o.push(P([run('Biến mục tiêu '), code('Bay131_MEAS_P'), run(' hầu như không bị ảnh hưởng: tỷ lệ bằng 0 toàn chuỗi chỉ 0,97% và bằng 0 tuyệt đối trong khoảng có nắng. Điểm đo này ghi cả các giá trị rất nhỏ ban đêm thay vì làm tròn, nên giữ được nhiều thông tin hơn hẳn các ngăn lộ 22 kV.')]));

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
      ['7', 'Lệch điểm không cảm biến Rad_2', '1 điểm đo', 'Trung bình', 'Trừ độ lệch ban đêm'],
      ['8', 'Điểm đo treo hằng số', `${dead.length} điểm đo`, 'Thấp', 'Loại khỏi tập biến đầu vào'],
      ['9', 'Mốc thời gian trùng', '3 bản ghi', 'Thấp', 'Khử trùng khi nạp'],
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
    '        lambda s: np.trapz(s.values, dx=60) / 3600.0',
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
  o.push(P('Trong số này, kiểu lắp đặt cảm biến bức xạ là câu hỏi cấp thiết nhất vì nó liên quan tới hai phát hiện đã nêu: hiện tượng buổi chiều sáng hơn buổi sáng ở mục 6.3, và phần đuôi bất thường của bức xạ ở mục 7.4.'));

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
    '    "e_ac_mwh": g["p_ac_mw"].apply(lambda s: np.trapz(s, dx=60) / 3600),',
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
      ['4', 'STALE', 'Giá trị không đổi quá 30 phút liên tục trong khoảng có bức xạ', 'Không'],
      ['5', 'LOW_COVERAGE', 'Ô gộp có dưới 80% số mẫu', 'Không'],
      ['6', 'SENSOR_OFFSET', 'Đã hiệu chỉnh lệch điểm không', 'Có'],
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

  o.push(P([run('Mã 6 áp dụng cho việc hiệu chỉnh lệch điểm không của Rad_2 nêu ở mục 6.4. Cách hiệu chỉnh:')]));
  o.push(codeBlock([
    '# Ước lượng độ lệch điểm không từ dữ liệu ban đêm',
    '# Ban đêm lấy theo quan sát ở mục 6.3: trước 05:30 hoặc sau 18:00',
    '',
    'gio     = df.index.hour + df.index.minute / 60',
    'night   = df[(gio < 5.5) | (gio > 18.0)]',
    'offset  = night["ghi_wm2_alt"].median()      # ~26 W/m2 với Rad_2',
    '',
    'df["ghi_wm2_alt_corr"] = (df["ghi_wm2_alt"] - offset).clip(lower=0)',
    'df.loc[df["ghi_wm2_alt"].notna(), "quality_ghi_alt"] = 6',
    '',
    '# Độ lệch nên tính lại theo từng tháng — cảm biến trôi theo thời gian',
  ]));

  o.push(P([run('Mã 7 là cơ chế phát hiện sự cố lộ nêu ở mục 5.5. Điều kiện phát hiện: trong nhóm bốn lộ 471, 473, 475, 477, nếu một lộ có công suất dưới 5% giá trị trung bình của ba lộ còn lại trong ít nhất ba bước liên tiếp, đánh dấu toàn bộ khoảng đó.')]));

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
      ['2', 'Cảm biến bức xạ lắp nằm ngang hay trên mặt phẳng nghiêng? Nếu nghiêng thì góc bao nhiêu?', 'Chốt ngưỡng vật lý và quy đổi bức xạ', '7.4'],
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
       'So trọng tâm đỉnh bức xạ với trung điểm mọc–lặn, 331 ngày',
       'Đỉnh chậm 36 phút; trung điểm ổn định, lệch chuẩn 12,3 phút'],
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
