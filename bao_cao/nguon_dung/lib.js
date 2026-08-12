// lib.js — helper dựng báo cáo Word
const D = require('docx');
const fs = require('fs');
const {
  Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType,
  AlignmentType, ShadingType, BorderStyle, ImageRun, PageBreak, TableOfContents,
  Header, Footer, PageNumber, convertInchesToTwip, VerticalAlign,
} = D;

const CW = 9638;                       // bề rộng vùng in (DXA), A4 lề 2cm
const NAVY = '1F4E79', ORANGE = 'C55A11', GREY = '595959', RED = 'C00000',
      GREEN = '548235', LIGHT = 'F2F6FA', LINE = 'BFBFBF';

const P = (text, o = {}) => new Paragraph({
  spacing: { after: o.after ?? 120, line: o.line ?? 280 },
  alignment: o.align,
  indent: o.indent,
  keepNext: o.keepNext,
  children: Array.isArray(text) ? text : [new TextRun({
    text, size: o.size ?? 21, color: o.color, bold: o.bold, italics: o.italics,
    font: o.font,
  })],
});

const run = (t, o = {}) => new TextRun({
  text: t, size: o.size ?? 21, bold: o.bold, italics: o.italics,
  color: o.color, font: o.font, underline: o.underline ? {} : undefined,
});
const code = (t) => run(t, { font: 'Consolas', size: 18, color: '1F4E79' });

const H = (text, lvl) => new Paragraph({
  heading: [HeadingLevel.HEADING_1, HeadingLevel.HEADING_2, HeadingLevel.HEADING_3][lvl - 1],
  spacing: { before: lvl === 1 ? 320 : 260, after: lvl === 1 ? 180 : 120 },
  keepNext: true,
  children: [new TextRun({
    text, bold: true, color: lvl === 1 ? NAVY : (lvl === 2 ? NAVY : GREY),
    size: lvl === 1 ? 30 : (lvl === 2 ? 24 : 21),
  })],
});

const bullets = (arr, o = {}) => arr.map(t => new Paragraph({
  bullet: { level: o.level ?? 0 },
  spacing: { after: 70, line: 276 },
  children: Array.isArray(t) ? t : [new TextRun({ text: t, size: 21 })],
}));

const numbered = (arr, ref) => arr.map(t => new Paragraph({
  numbering: { reference: ref, level: 0 },
  spacing: { after: 70, line: 276 },
  children: Array.isArray(t) ? t : [new TextRun({ text: t, size: 21 })],
}));

// ---- bảng ----
function cell(content, w, o = {}) {
  const kids = Array.isArray(content) ? content : [new Paragraph({
    spacing: { before: 40, after: 40, line: 240 },
    alignment: o.align,
    children: [new TextRun({
      text: String(content), size: o.size ?? 18, bold: o.bold,
      color: o.color ?? (o.head ? 'FFFFFF' : '000000'),
      font: o.mono ? 'Consolas' : undefined,
    })],
  })];
  return new TableCell({
    width: { size: w, type: WidthType.DXA },
    shading: o.fill ? { type: ShadingType.CLEAR, fill: o.fill, color: 'auto' } : undefined,
    margins: { top: 40, bottom: 40, left: 90, right: 90 },
    verticalAlign: VerticalAlign.CENTER,
    children: kids,
  });
}

/** head: [..], rows: [[..]], widths: [..] (tổng = CW) */
function table(head, rows, widths, o = {}) {
  const aligns = o.align || [];
  const bd = { style: BorderStyle.SINGLE, size: 2, color: LINE };
  return new Table({
    columnWidths: widths,
    width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    borders: { top: bd, bottom: bd, left: bd, right: bd, insideHorizontal: bd, insideVertical: bd },
    rows: [
      new TableRow({
        tableHeader: true,
        children: head.map((h, i) => cell(h, widths[i], {
          head: true, bold: true, fill: NAVY, size: o.headSize ?? 17,
          align: AlignmentType.CENTER,
        })),
      }),
      ...rows.map((r, ri) => new TableRow({
        children: r.map((c, i) => cell(c, widths[i], {
          fill: ri % 2 ? LIGHT : undefined,
          align: aligns[i],
          size: o.size ?? 17,
          mono: (o.mono || []).includes(i),
          bold: (o.boldRows || []).includes(ri),
          color: (o.redRows || []).includes(ri) ? RED : undefined,
        })),
      })),
    ],
  });
}

const caption = (t) => new Paragraph({
  spacing: { before: 60, after: 220 },
  alignment: AlignmentType.CENTER,
  children: [new TextRun({ text: t, size: 17, italics: true, color: GREY })],
});

const tblTitle = (t) => new Paragraph({
  spacing: { before: 180, after: 90 },
  keepNext: true,
  children: [new TextRun({ text: t, size: 18, bold: true, color: NAVY })],
});

function figure(path, w, cap) {
  const buf = fs.readFileSync(path);
  const dim = pngSize(buf);
  const h = Math.round(w * dim.h / dim.w);
  return [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 140, after: 0 },
      children: [new ImageRun({ data: buf, type: 'png', transformation: { width: w, height: h } })],
    }),
    caption(cap),
  ];
}
function pngSize(b) { return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) }; }

// khối mã / trích dẫn
const codeBlock = (lines) => new Table({
  columnWidths: [CW],
  width: { size: CW, type: WidthType.DXA },
  borders: {
    top: { style: BorderStyle.SINGLE, size: 2, color: LINE },
    bottom: { style: BorderStyle.SINGLE, size: 2, color: LINE },
    left: { style: BorderStyle.SINGLE, size: 12, color: NAVY },
    right: { style: BorderStyle.SINGLE, size: 2, color: LINE },
    insideHorizontal: { style: BorderStyle.NONE }, insideVertical: { style: BorderStyle.NONE },
  },
  rows: [new TableRow({
    cantSplit: true,
    children: [new TableCell({
      width: { size: CW, type: WidthType.DXA },
      shading: { type: ShadingType.CLEAR, fill: 'F7F7F7', color: 'auto' },
      margins: { top: 110, bottom: 110, left: 160, right: 120 },
      children: lines.map(l => new Paragraph({
        spacing: { after: 0, line: 250 },
        children: [new TextRun({ text: l, font: 'Consolas', size: 17 })],
      })),
    })],
  })],
});

// hộp ghi chú nổi bật
const callout = (title, lines, color = ORANGE) => new Table({
  columnWidths: [CW],
  width: { size: CW, type: WidthType.DXA },
  borders: {
    top: { style: BorderStyle.SINGLE, size: 2, color: color },
    bottom: { style: BorderStyle.SINGLE, size: 2, color: color },
    left: { style: BorderStyle.SINGLE, size: 18, color: color },
    right: { style: BorderStyle.SINGLE, size: 2, color: color },
    insideHorizontal: { style: BorderStyle.NONE }, insideVertical: { style: BorderStyle.NONE },
  },
  rows: [new TableRow({
    cantSplit: true,
    children: [new TableCell({
      width: { size: CW, type: WidthType.DXA },
      shading: { type: ShadingType.CLEAR, fill: 'FDF6F0', color: 'auto' },
      margins: { top: 120, bottom: 120, left: 180, right: 140 },
      children: [
        new Paragraph({
          spacing: { after: 70 },
          children: [new TextRun({ text: title, bold: true, size: 20, color: color })],
        }),
        ...lines.map(l => new Paragraph({
          spacing: { after: 60, line: 270 },
          children: Array.isArray(l) ? l : [new TextRun({ text: l, size: 20 })],
        })),
      ],
    })],
  })],
});

const pageBreak = () => new Paragraph({ children: [new PageBreak()] });
const spacer = (n = 1) => Array.from({ length: n }, () => new Paragraph({ spacing: { after: 120 }, children: [] }));
const hr = () => new Paragraph({
  spacing: { before: 100, after: 160 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: LINE } },
  children: [],
});

const fmt = (n, d = 2) => (n === null || n === undefined || Number.isNaN(n))
  ? '—' : Number(n).toFixed(d).replace('.', ',');
const int = (n) => (n === null || n === undefined) ? '—'
  : Math.round(n).toLocaleString('vi-VN');

module.exports = {
  D, CW, NAVY, ORANGE, GREY, RED, GREEN, LIGHT,
  P, H, run, code, bullets, numbered, table, cell, caption, tblTitle,
  figure, codeBlock, callout, pageBreak, spacer, hr, fmt, int,
};
