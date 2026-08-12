// build.js — dựng file Word
const fs = require('fs');
const D = require('docx');
const L = require('./lib');
const {
  Document, Packer, Paragraph, TextRun, AlignmentType, HeadingLevel, TableOfContents,
  Header, Footer, PageNumber, BorderStyle, LevelFormat, convertInchesToTwip,
} = D;
const { P, H, run, code, table, pageBreak, NAVY, GREY, ORANGE, CW } = L;

const FIG = process.argv[2] || './fig';
const OUT = process.argv[3] || './BaoCao.docx';
const J = JSON.parse(fs.readFileSync(process.argv[4] || './facts.json', 'utf8'));

// ---------------- trang bìa ----------------
const T = (t, o = {}) => new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { after: o.after ?? 160 },
  children: [new TextRun({
    text: t, size: o.size ?? 24, bold: o.bold, color: o.color, italics: o.italics,
    allCaps: o.caps,
  })],
});

const cover = [
  ...Array.from({ length: 3 }, () => new Paragraph({ spacing: { after: 200 }, children: [] })),
  T('DỰ ÁN PHẦN MỀM SOLAR FORECAST', { size: 22, color: GREY, bold: true }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 200, after: 100 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: NAVY } },
    children: [],
  }),
  T('BÁO CÁO KHẢO SÁT', { size: 52, bold: true, color: NAVY, after: 60 }),
  T('VÀ ĐÁNH GIÁ DỮ LIỆU', { size: 52, bold: true, color: NAVY, after: 100 }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 60, after: 300 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: NAVY } },
    children: [],
  }),
  T('Giai đoạn 1 — Khảo sát nguồn dữ liệu vận hành', { size: 26, italics: true, color: GREY, after: 500 }),
  ...Array.from({ length: 2 }, () => new Paragraph({ spacing: { after: 200 }, children: [] })),
];

const coverTable = table(
  ['Hạng mục', 'Nội dung'],
  [
    ['Đối tượng khảo sát', 'db_fujiwara.sql — cơ sở dữ liệu MEAS'],
    ['Nguồn', 'Hệ thống historian của nhà máy'],
    ['Thời điểm chụp dữ liệu', '17/07/2026'],
    ['Phạm vi dữ liệu', '12/07/2025 – 17/07/2026 (370 ngày)'],
    ['Khối lượng', '6.564.535 bản ghi / 19 bảng'],
    ['Loại tài liệu', 'Tài liệu kỹ thuật nội bộ'],
    ['Phiên bản', '1.0'],
  ],
  [3200, 6438]);

const coverEnd = [
  new Paragraph({ spacing: { after: 400 }, children: [] }),
  T('Tài liệu lưu hành nội bộ nhóm kỹ thuật', { size: 19, italics: true, color: GREY }),
  pageBreak(),
];

// ---------------- mục lục ----------------
const toc = [
  new Paragraph({
    spacing: { after: 240 },
    children: [new TextRun({ text: 'MỤC LỤC', bold: true, size: 32, color: NAVY })],
  }),
  new Paragraph({
    spacing: { after: 200 },
    children: [new TextRun({
      text: 'Nếu mục lục hiển thị trống, bấm vào vùng mục lục rồi nhấn F9 để cập nhật.',
      size: 17, italics: true, color: GREY,
    })],
  }),
  new TableOfContents('Mục lục', {
    hyperlink: true,
    headingStyleRange: '1-3',
    stylesWithLevels: [],
  }),
  pageBreak(),
];

// ---------------- nội dung ----------------
const body = [
  ...require('./content1')(J, FIG),
  ...require('./content2')(J, FIG),
];

const doc = new Document({
  features: { updateFields: true },
  creator: 'Nhóm kỹ thuật — Dự án Solar Forecast',
  title: 'Báo cáo khảo sát và đánh giá dữ liệu',
  description: 'Giai đoạn 1 — khảo sát nguồn dữ liệu vận hành nhà máy điện mặt trời',
  styles: {
    default: {
      document: { run: { font: 'Calibri', size: 21 } },
      heading1: { run: { font: 'Calibri', size: 30, bold: true, color: NAVY } },
      heading2: { run: { font: 'Calibri', size: 24, bold: true, color: NAVY } },
      heading3: { run: { font: 'Calibri', size: 21, bold: true, color: GREY } },
    },
    paragraphStyles: [
      { id: 'Normal', name: 'Normal', run: { font: 'Calibri', size: 21 },
        paragraph: { spacing: { line: 288, after: 120 } } },
    ],
  },
  numbering: {
    config: [{
      reference: 'ql',
      levels: [{
        level: 0, format: LevelFormat.DECIMAL, text: '%1.',
        alignment: AlignmentType.START,
        style: { paragraph: { indent: { left: 520, hanging: 300 } } },
      }],
    }],
  },
  sections: [
    {
      properties: {
        page: {
          size: { width: 11906, height: 16838 },
          margin: { top: 1134, right: 1134, bottom: 1134, left: 1134 },
        },
      },
      children: [...cover, coverTable, ...coverEnd, ...toc, ...body],
      headers: {
        default: new Header({
          children: [new Paragraph({
            alignment: AlignmentType.RIGHT,
            spacing: { after: 40 },
            border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: 'D9D9D9' } },
            children: [new TextRun({
              text: 'Báo cáo khảo sát và đánh giá dữ liệu — Dự án Solar Forecast',
              size: 16, color: GREY, italics: true,
            })],
          })],
        }),
      },
      footers: {
        default: new Footer({
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { before: 60 },
            children: [
              new TextRun({ text: 'Trang ', size: 16, color: GREY }),
              new TextRun({ children: [PageNumber.CURRENT], size: 16, color: GREY }),
              new TextRun({ text: ' / ', size: 16, color: GREY }),
              new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 16, color: GREY }),
            ],
          })],
        }),
      },
    },
  ],
});

Packer.toBuffer(doc).then(b => {
  fs.writeFileSync(OUT, b);
  console.log('OK ->', OUT, (b.length / 1024).toFixed(0) + ' KB');
});
