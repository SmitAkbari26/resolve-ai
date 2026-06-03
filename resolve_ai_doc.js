const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, VerticalAlign, PageNumber, LevelFormat, ExternalHyperlink,
  UnderlineType
} = require('docx');
const fs = require('fs');

// ── Color palette ──────────────────────────────────────────────────────────────
const C = {
  brand:      "1A4FC4",   // deep blue
  brandLight: "E8F0FE",   // pale blue fill
  teal:       "0F6E56",
  tealLight:  "E1F5EE",
  amber:      "854F0B",
  amberLight: "FAEEDA",
  coral:      "993C1D",
  coralLight: "FAECE7",
  purple:     "534AB7",
  purpleLight:"EEEDFE",
  green:      "3B6D11",
  greenLight: "EAF3DE",
  red:        "A32D2D",
  redLight:   "FCEBEB",
  gray:       "5F5E5A",
  grayLight:  "F1EFE8",
  white:      "FFFFFF",
  black:      "1A1A1A",
  text:       "2C2C2A",
  muted:      "6B6B68",
  border:     "CCCCCC",
};

// ── Border helpers ─────────────────────────────────────────────────────────────
const border1 = (color) => ({ style: BorderStyle.SINGLE, size: 4, color });
const noBorder = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const allBorders = (color) => ({ top: border1(color), bottom: border1(color), left: border1(color), right: border1(color) });
const allNoBorder = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };

// ── Typography helpers ─────────────────────────────────────────────────────────
const run = (text, opts = {}) => new TextRun({
  text,
  font: "Arial",
  size: opts.size || 22,
  bold: opts.bold || false,
  italics: opts.italic || false,
  color: opts.color || C.text,
  ...opts,
});

const para = (children, opts = {}) => new Paragraph({
  children: Array.isArray(children) ? children : [children],
  spacing: { before: opts.spaceBefore || 0, after: opts.spaceAfter || 120 },
  alignment: opts.align || AlignmentType.LEFT,
  ...opts,
});

const heading1 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_1,
  children: [new TextRun({ text, font: "Arial", size: 36, bold: true, color: C.brand })],
  spacing: { before: 360, after: 160 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: C.brand, space: 4 } },
});

const heading2 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_2,
  children: [new TextRun({ text, font: "Arial", size: 28, bold: true, color: C.black })],
  spacing: { before: 280, after: 100 },
});

const heading3 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_3,
  children: [new TextRun({ text, font: "Arial", size: 24, bold: true, color: C.brand })],
  spacing: { before: 200, after: 80 },
});

const bodyText = (text, opts = {}) => new Paragraph({
  children: [new TextRun({ text, font: "Arial", size: 22, color: C.text, ...opts })],
  spacing: { before: 0, after: 140 },
});

const spacer = (pts = 120) => new Paragraph({
  children: [new TextRun("")],
  spacing: { before: 0, after: pts },
});

// Bullet item
const bullet = (text, opts = {}) => new Paragraph({
  numbering: { reference: "bullets", level: 0 },
  children: [new TextRun({ text, font: "Arial", size: 22, color: C.text, ...opts })],
  spacing: { before: 40, after: 40 },
});

// ── Cell helpers ───────────────────────────────────────────────────────────────
const cell = (children, opts = {}) => new TableCell({
  children: Array.isArray(children) ? children : [children],
  width: { size: opts.width || 2340, type: WidthType.DXA },
  shading: opts.fill ? { fill: opts.fill, type: ShadingType.CLEAR } : undefined,
  borders: opts.borders || allBorders(C.border),
  margins: { top: 100, bottom: 100, left: 140, right: 140 },
  verticalAlign: opts.vAlign || VerticalAlign.CENTER,
  columnSpan: opts.span,
});

// ── STAT CARD TABLE (2x2) ──────────────────────────────────────────────────────
const makeStatTable = (stats) => {
  // stats: [{num, label, color}]
  const makeStatCell = (stat) => new TableCell({
    children: [
      new Paragraph({
        children: [new TextRun({ text: stat.num, font: "Arial", size: 52, bold: true, color: stat.color || C.brand })],
        spacing: { before: 80, after: 40 },
      }),
      new Paragraph({
        children: [new TextRun({ text: stat.label, font: "Arial", size: 18, color: C.muted })],
        spacing: { before: 0, after: 100 },
      }),
    ],
    width: { size: 2340, type: WidthType.DXA },
    shading: { fill: C.grayLight, type: ShadingType.CLEAR },
    borders: allNoBorder,
    margins: { top: 120, bottom: 120, left: 160, right: 160 },
  });

  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [4620, 120, 4620],
    rows: [
      new TableRow({
        children: [
          makeStatCell(stats[0]),
          new TableCell({ children: [spacer()], width: { size: 120, type: WidthType.DXA }, borders: allNoBorder }),
          makeStatCell(stats[1]),
        ],
      }),
      new TableRow({
        children: [
          new TableCell({ children: [spacer(80)], width: { size: 4620, type: WidthType.DXA }, borders: allNoBorder }),
          new TableCell({ children: [spacer()], width: { size: 120, type: WidthType.DXA }, borders: allNoBorder }),
          new TableCell({ children: [spacer(80)], width: { size: 4620, type: WidthType.DXA }, borders: allNoBorder }),
        ],
      }),
      new TableRow({
        children: [
          makeStatCell(stats[2]),
          new TableCell({ children: [spacer()], width: { size: 120, type: WidthType.DXA }, borders: allNoBorder }),
          makeStatCell(stats[3]),
        ],
      }),
    ],
  });
};

// ── PAIN CARD (bordered box per pain point) ────────────────────────────────────
const makePainTable = (pains) => {
  const makeRow = (pain) => new TableRow({
    children: [
      new TableCell({
        children: [
          new Paragraph({
            children: [new TextRun({ text: pain.title, font: "Arial", size: 22, bold: true, color: pain.titleColor || C.brand })],
            spacing: { before: 60, after: 30 },
          }),
          new Paragraph({
            children: [new TextRun({ text: pain.desc, font: "Arial", size: 20, color: C.text })],
            spacing: { before: 0, after: 30 },
          }),
          new Paragraph({
            children: [new TextRun({ text: pain.pill, font: "Arial", size: 18, bold: true, color: pain.pillColor || C.brand })],
            spacing: { before: 0, after: 60 },
          }),
        ],
        width: { size: 9360, type: WidthType.DXA },
        shading: { fill: pain.fill || C.brandLight, type: ShadingType.CLEAR },
        borders: { top: border1(pain.accent || C.brand), bottom: noBorder, left: { style: BorderStyle.SINGLE, size: 16, color: pain.accent || C.brand }, right: noBorder },
        margins: { top: 80, bottom: 80, left: 200, right: 160 },
      }),
    ],
  });

  const gapRow = new TableRow({
    children: [new TableCell({ children: [spacer(60)], width: { size: 9360, type: WidthType.DXA }, borders: allNoBorder })],
  });

  const rows = [];
  pains.forEach((p, i) => {
    rows.push(makeRow(p));
    if (i < pains.length - 1) rows.push(gapRow);
  });

  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [9360],
    rows,
  });
};

// ── COMPARISON TABLE ───────────────────────────────────────────────────────────
const makeCompTable = (rows_data) => new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: [4640, 4720],
  rows: [
    new TableRow({
      children: [
        new TableCell({
          children: [new Paragraph({ children: [new TextRun({ text: "Today (status quo)", font: "Arial", size: 22, bold: true, color: C.red })], spacing: { before: 60, after: 60 } })],
          width: { size: 4640, type: WidthType.DXA },
          shading: { fill: C.redLight, type: ShadingType.CLEAR },
          borders: allBorders(C.border),
          margins: { top: 80, bottom: 80, left: 140, right: 140 },
        }),
        new TableCell({
          children: [new Paragraph({ children: [new TextRun({ text: "ResolveAI", font: "Arial", size: 22, bold: true, color: C.teal })], spacing: { before: 60, after: 60 } })],
          width: { size: 4720, type: WidthType.DXA },
          shading: { fill: C.tealLight, type: ShadingType.CLEAR },
          borders: allBorders(C.border),
          margins: { top: 80, bottom: 80, left: 140, right: 140 },
        }),
      ],
    }),
    ...rows_data.map(row => new TableRow({
      children: [
        new TableCell({
          children: [new Paragraph({ children: [new TextRun({ text: row.old, font: "Arial", size: 20, color: C.text })], spacing: { before: 60, after: 60 } })],
          width: { size: 4640, type: WidthType.DXA },
          borders: allBorders(C.border),
          margins: { top: 80, bottom: 80, left: 140, right: 140 },
        }),
        new TableCell({
          children: [new Paragraph({ children: [new TextRun({ text: row.new, font: "Arial", size: 20, color: C.text })], spacing: { before: 60, after: 60 } })],
          width: { size: 4720, type: WidthType.DXA },
          shading: { fill: C.tealLight, type: ShadingType.CLEAR },
          borders: allBorders(C.border),
          margins: { top: 80, bottom: 80, left: 140, right: 140 },
        }),
      ],
    })),
  ],
});

// ── PILLAR TABLE ───────────────────────────────────────────────────────────────
const makePillarTable = (pillars) => {
  const makeCell = (p) => new TableCell({
    children: [
      new Paragraph({
        children: [new TextRun({ text: p.name, font: "Arial", size: 22, bold: true, color: p.color })],
        spacing: { before: 80, after: 40 },
      }),
      new Paragraph({
        children: [new TextRun({ text: p.desc, font: "Arial", size: 19, color: C.text })],
        spacing: { before: 0, after: 40 },
      }),
      new Paragraph({
        children: [new TextRun({ text: "✓ " + p.tag, font: "Arial", size: 18, bold: true, color: p.color })],
        spacing: { before: 0, after: 80 },
      }),
    ],
    width: { size: 4560, type: WidthType.DXA },
    shading: { fill: p.fill, type: ShadingType.CLEAR },
    borders: { top: border1(p.color), bottom: noBorder, left: noBorder, right: noBorder },
    margins: { top: 100, bottom: 100, left: 140, right: 140 },
  });

  const gap = new TableCell({ children: [spacer()], width: { size: 240, type: WidthType.DXA }, borders: allNoBorder });

  const rows = [];
  for (let i = 0; i < pillars.length; i += 2) {
    const a = pillars[i], b = pillars[i + 1];
    rows.push(new TableRow({ children: [makeCell(a), gap, b ? makeCell(b) : new TableCell({ children: [spacer()], width: { size: 4560, type: WidthType.DXA }, borders: allNoBorder })] }));
    if (i + 2 < pillars.length) {
      rows.push(new TableRow({ children: [new TableCell({ children: [spacer(80)], width: { size: 9360, type: WidthType.DXA }, borders: allNoBorder, columnSpan: 3 })] }));
    }
  }

  return new Table({ width: { size: 9360, type: WidthType.DXA }, columnWidths: [4560, 240, 4560], rows });
};

// ── AGENTIC LOOP TABLE ─────────────────────────────────────────────────────────
const makeLoopTable = (steps) => {
  const cells = steps.map((s, i) => new TableCell({
    children: [
      new Paragraph({
        children: [new TextRun({ text: `${i + 1}`, font: "Arial", size: 32, bold: true, color: C.brand })],
        spacing: { before: 60, after: 20 },
      }),
      new Paragraph({
        children: [new TextRun({ text: s.title, font: "Arial", size: 20, bold: true, color: C.black })],
        spacing: { before: 0, after: 20 },
      }),
      new Paragraph({
        children: [new TextRun({ text: s.desc, font: "Arial", size: 18, color: C.muted })],
        spacing: { before: 0, after: 60 },
      }),
    ],
    width: { size: 1560, type: WidthType.DXA },
    shading: { fill: i % 2 === 0 ? C.brandLight : C.white, type: ShadingType.CLEAR },
    borders: allBorders(C.border),
    margins: { top: 80, bottom: 80, left: 100, right: 100 },
    verticalAlign: VerticalAlign.TOP,
  }));

  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: new Array(6).fill(1560),
    rows: [new TableRow({ children: cells })],
  });
};

// ── NEXT STEPS TABLE ───────────────────────────────────────────────────────────
const makeNextStepsTable = (steps) => new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: [9360],
  rows: steps.map((s, i) => new TableRow({
    children: [new TableCell({
      children: [
        new Paragraph({
          children: [
            new TextRun({ text: `${String.fromCharCode(65 + i)}  `, font: "Arial", size: 22, bold: true, color: C.brand }),
            new TextRun({ text: s.title, font: "Arial", size: 22, bold: true, color: C.black }),
          ],
          spacing: { before: 60, after: 30 },
        }),
        new Paragraph({
          children: [new TextRun({ text: s.desc, font: "Arial", size: 20, color: C.text })],
          spacing: { before: 0, after: 60 },
        }),
      ],
      width: { size: 9360, type: WidthType.DXA },
      shading: { fill: i % 2 === 0 ? C.brandLight : C.grayLight, type: ShadingType.CLEAR },
      borders: { top: noBorder, bottom: noBorder, left: { style: BorderStyle.SINGLE, size: 20, color: C.brand }, right: noBorder },
      margins: { top: 80, bottom: 80, left: 180, right: 140 },
    })],
  })),
});

// ── COVER PAGE ────────────────────────────────────────────────────────────────
const coverPage = [
  spacer(1440),
  new Paragraph({
    children: [new TextRun({ text: "RESOLVE", font: "Arial", size: 80, bold: true, color: C.brand }),
               new TextRun({ text: "AI", font: "Arial", size: 80, bold: true, color: C.teal })],
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 80 },
  }),
  new Paragraph({
    children: [new TextRun({ text: "Agentic Customer Support Resolution System", font: "Arial", size: 32, color: C.muted })],
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 480 },
  }),
  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [9360],
    rows: [new TableRow({ children: [new TableCell({
      children: [
        new Paragraph({ children: [new TextRun({ text: "A complete market brief, product blueprint, and build roadmap for teams looking to lead the next wave of AI-powered customer support.", font: "Arial", size: 24, color: C.brand, italics: true })], alignment: AlignmentType.CENTER, spacing: { before: 160, after: 160 } }),
      ],
      width: { size: 9360, type: WidthType.DXA },
      shading: { fill: C.brandLight, type: ShadingType.CLEAR },
      borders: { top: border1(C.brand), bottom: border1(C.brand), left: noBorder, right: noBorder },
      margins: { top: 140, bottom: 140, left: 200, right: 200 },
    })] })],
  }),
  spacer(400),
  new Paragraph({
    children: [new TextRun({ text: "May 2026", font: "Arial", size: 20, color: C.muted })],
    alignment: AlignmentType.CENTER,
  }),
  new Paragraph({
    children: [new TextRun({ text: "Confidential", font: "Arial", size: 20, color: C.muted, italics: true })],
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 0 },
  }),
  new Paragraph({ children: [new TextRun({ break: 1 })], pageBreakBefore: true }),
];

// ── DOCUMENT SECTIONS ─────────────────────────────────────────────────────────
const sections_content = [

  // 1. MARKET MOMENT
  heading1("1. The Market Moment"),
  bodyText("The customer support industry is in the middle of its most significant structural shift in two decades. Scripted chatbots and deflection bots are giving way to autonomous agents that can reason, act, and resolve — end to end. This is the market ResolveAI is built for."),
  spacer(100),
  makeStatTable([
    { num: "56%", label: "of support interactions will use agentic AI by mid-2026 (Cisco, 2025)", color: C.brand },
    { num: "68%", label: "predicted agentic AI coverage of all customer support by 2028", color: C.teal },
    { num: "60%", label: "drop in ticket volume achievable with AI-driven resolution", color: C.amber },
    { num: "23%", label: "of orgs currently scaling agentic AI — early movers have a clear advantage (McKinsey)", color: C.coral },
  ]),
  spacer(200),
  bodyText("Despite strong momentum, only 19% of companies have invested heavily in agentic AI while 42% are making cautious, incremental bets. The market is still finding its footing — which is precisely the window for a focused, opinionated product like ResolveAI."),

  spacer(120),

  // 2. THE PROBLEM SPACE
  heading1("2. The Problem Space"),
  bodyText("Six recurring failures define how customer support breaks down today. ResolveAI is designed to address all of them."),
  spacer(80),
  makePainTable([
    { title: "Slow resolution", desc: "The average email response time is 12+ hours. 60% of customers consider even a 1-minute hold unacceptable. Speed is not a nice-to-have — it directly predicts customer retention.", pill: "Critical gap", titleColor: C.red, pillColor: C.red, fill: C.redLight, accent: C.red },
    { title: "Agent burnout from repetitive tickets", desc: "Human agents spend the majority of their time on low-complexity, high-volume queries. Teams routinely handle 15–25% more tickets than necessary because AI tools fail to resolve — they only deflect.", pill: "Cost driver", titleColor: C.amber, pillColor: C.amber, fill: C.amberLight, accent: C.amber },
    { title: "Fragmented tooling loses context", desc: "Separate ticketing, knowledge management, and AI tools create constant context switching. Each tool switch bleeds resolution time and frustrates both agents and customers.", pill: "Efficiency loss", titleColor: C.amber, pillColor: C.amber, fill: C.amberLight, accent: C.amber },
    { title: "Low first-contact resolution rate", desc: "The industry average FCR sits at 70%. Top performers reach 85%. The gap represents a massive opportunity — every unresolved ticket is a second contact, a frustrated customer, and an avoidable cost.", pill: "Opportunity", titleColor: C.teal, pillColor: C.teal, fill: C.tealLight, accent: C.teal },
    { title: "Hallucination erodes customer trust", desc: "AI hallucination rates run 15–27% in live deployments. Bots invent refund policies, fabricate timelines, and give incorrect instructions — silently damaging brand trust with every wrong answer.", pill: "Critical gap", titleColor: C.red, pillColor: C.red, fill: C.redLight, accent: C.red },
    { title: "Context is lost on escalation", desc: "When bots hand off to humans, customers repeat their entire problem from scratch. This is the single most cited source of customer frustration with AI support systems and the most solvable engineering challenge.", pill: "Critical gap", titleColor: C.red, pillColor: C.red, fill: C.redLight, accent: C.red },
  ]),

  spacer(160),

  // 3. WHAT RESOLVEAI CHANGES
  heading1("3. What ResolveAI Changes"),
  bodyText("The core insight: deflection is not resolution. Most AI support tools celebrate deflection rates as the headline metric — but a bot that sends customers into a doom loop has not helped anyone. ResolveAI makes resolution quality the north star."),
  spacer(100),
  makeCompTable([
    { old: "Bot deflects → dead-end loop → customer gives up or re-opens ticket", new: "Agent understands intent → acts autonomously → resolves end-to-end with full context retained" },
    { old: "Human escalation loses all context — customer must repeat their entire problem", new: "Handoff carries full conversation history, sentiment score, and recommended next action" },
    { old: "Deflection rate is the headline metric — CSAT silently degrades over months", new: "CSAT-protected deflection is the only metric shown to leadership — quality gates quantity" },
    { old: "AI answers from training data — hallucinates 15–27% of the time in live deployments", new: "Every response grounded in verified knowledge base and policy — hallucination rate approaches zero" },
    { old: "Separate ticketing, knowledge base, and AI tools — constant context switching", new: "Unified agent layer connects to existing CRMs and tools via APIs — no rip and replace" },
  ]),

  spacer(160),

  // 4. CORE PILLARS
  heading1("4. Core Product Pillars"),
  bodyText("ResolveAI is built on six foundational capabilities. Each addresses a specific failure mode in today's support AI landscape."),
  spacer(100),
  makePillarTable([
    { name: "Intent understanding", desc: "Go beyond keyword matching. Understand what the customer actually wants, including emotional state, urgency signals, and underlying intent behind ambiguous phrasing.", tag: "92% intent accuracy is achievable", color: C.brand, fill: C.brandLight },
    { name: "Autonomous action", desc: "Do not just answer — act. Trigger refunds, reset passwords, update orders, create tickets, and close cases without waiting for human approval on routine actions.", tag: "End-to-end resolution", color: C.teal, fill: C.tealLight },
    { name: "Knowledge grounding", desc: "Ground every response in verified policy and knowledge base content. No response leaves the system without a source attribution — eliminating hallucinations at the architecture level.", tag: "Eliminates 15–27% hallucination rate", color: C.amber, fill: C.amberLight },
    { name: "Smart escalation", desc: "Know exactly when human judgment is required. Pass the full context bundle — conversation history, sentiment score, and a recommended next action — to the receiving agent.", tag: "Zero context loss on handoff", color: C.purple, fill: C.purpleLight },
    { name: "Resolution analytics", desc: "Track CSAT-protected deflection, not raw deflection. Surface recurring themes that reveal unresolved root causes and feed directly into knowledge base improvements.", tag: "Proves real ROI to leadership", color: C.coral, fill: C.coralLight },
    { name: "CRM & tool integration", desc: "Connect to Zendesk, Salesforce, Intercom, Freshdesk, and custom stacks via bidirectional APIs. Augment what support teams already use — do not require a rip and replace.", tag: "Works within existing infrastructure", color: C.green, fill: C.greenLight },
  ]),

  spacer(160),

  // 5. AGENTIC LOOP
  heading1("5. The ResolveAI Agentic Loop"),
  bodyText("Every support interaction passes through a structured reasoning loop. The agent does not guess — it plans, retrieves, acts, verifies, and learns."),
  spacer(100),
  makeLoopTable([
    { title: "Receive", desc: "Inbound ticket or live message from any channel" },
    { title: "Classify", desc: "Intent, urgency, complexity & sentiment scored" },
    { title: "Retrieve", desc: "Policy, account data & history pulled in real time" },
    { title: "Plan", desc: "Respond, act, escalate, or request clarification" },
    { title: "Verify", desc: "Output checked against policy before sending" },
    { title: "Learn", desc: "Outcome logged, knowledge gaps surfaced & fixed" },
  ]),
  spacer(120),
  bodyText("The verify step is what separates ResolveAI from most agentic systems. Before any response or action is executed, a lightweight policy check confirms the output is within bounds — catching hallucinations and out-of-policy actions before they reach the customer."),

  spacer(160),

  // 6. KEY METRICS
  heading1("6. Key Metrics to Track"),
  bodyText("ResolveAI surfaces the metrics that actually matter — not vanity numbers. Here is what to instrument from day one."),
  spacer(80),
  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [3000, 2880, 3480],
    rows: [
      new TableRow({
        children: [
          new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "Metric", font: "Arial", size: 20, bold: true, color: C.white })], spacing: { before: 60, after: 60 } })], width: { size: 3000, type: WidthType.DXA }, shading: { fill: C.brand, type: ShadingType.CLEAR }, borders: allBorders(C.brand), margins: { top: 80, bottom: 80, left: 140, right: 140 } }),
          new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "Industry benchmark", font: "Arial", size: 20, bold: true, color: C.white })], spacing: { before: 60, after: 60 } })], width: { size: 2880, type: WidthType.DXA }, shading: { fill: C.brand, type: ShadingType.CLEAR }, borders: allBorders(C.brand), margins: { top: 80, bottom: 80, left: 140, right: 140 } }),
          new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "ResolveAI target", font: "Arial", size: 20, bold: true, color: C.white })], spacing: { before: 60, after: 60 } })], width: { size: 3480, type: WidthType.DXA }, shading: { fill: C.brand, type: ShadingType.CLEAR }, borders: allBorders(C.brand), margins: { top: 80, bottom: 80, left: 140, right: 140 } }),
        ],
      }),
      ...[
        ["CSAT-protected deflection rate", "25–45% (AI adopters)", "50%+ without CSAT regression"],
        ["First-contact resolution (FCR)", "70% avg / 85% top performers", "80% autonomous FCR"],
        ["Average handle time reduction", "44% faster with AI", "45–60% reduction"],
        ["AI intent recognition accuracy", "92% (simple tasks)", "95%+ across all intents"],
        ["Hallucination rate", "15–27% live deployments", "<2% via knowledge grounding"],
        ["Escalation context completeness", "Not measured by most teams", "100% full context on handoff"],
        ["Repeat contact within 7 days", "Leading CSAT degradation signal", "Monitored weekly as health metric"],
      ].map((row, i) => new TableRow({
        children: row.map((text, j) => new TableCell({
          children: [new Paragraph({ children: [new TextRun({ text, font: "Arial", size: 19, color: j === 2 ? C.teal : C.text, bold: j === 2 })], spacing: { before: 60, after: 60 } })],
          width: { size: [3000, 2880, 3480][j], type: WidthType.DXA },
          shading: { fill: i % 2 === 0 ? C.grayLight : C.white, type: ShadingType.CLEAR },
          borders: allBorders(C.border),
          margins: { top: 80, bottom: 80, left: 140, right: 140 },
        })),
      })),
    ],
  }),

  spacer(160),

  // 7. COMPETITOR LANDSCAPE
  heading1("7. Competitor Landscape & Differentiation"),
  bodyText("The agentic support space is crowded with overlapping tools. ResolveAI's differentiation lies in combining resolution quality, knowledge grounding, and context-preserving escalation in a single opinionated product."),
  spacer(80),
  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2200, 3680, 3480],
    rows: [
      new TableRow({
        children: [
          new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "Competitor type", font: "Arial", size: 20, bold: true, color: C.white })], spacing: { before: 60, after: 60 } })], width: { size: 2200, type: WidthType.DXA }, shading: { fill: C.gray, type: ShadingType.CLEAR }, borders: allBorders(C.border), margins: { top: 80, bottom: 80, left: 140, right: 140 } }),
          new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "Weakness", font: "Arial", size: 20, bold: true, color: C.white })], spacing: { before: 60, after: 60 } })], width: { size: 3680, type: WidthType.DXA }, shading: { fill: C.gray, type: ShadingType.CLEAR }, borders: allBorders(C.border), margins: { top: 80, bottom: 80, left: 140, right: 140 } }),
          new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "ResolveAI edge", font: "Arial", size: 20, bold: true, color: C.white })], spacing: { before: 60, after: 60 } })], width: { size: 3480, type: WidthType.DXA }, shading: { fill: C.gray, type: ShadingType.CLEAR }, borders: allBorders(C.border), margins: { top: 80, bottom: 80, left: 140, right: 140 } }),
        ],
      }),
      ...[
        ["Deflection bots (Intercom, Drift)", "Deflect without resolving. High escalation rates. No autonomous action layer.", "End-to-end resolution, not just deflection theatre"],
        ["Generic LLM wrappers", "Hallucinate policy. No knowledge grounding. Not enterprise-safe.", "Grounded, verified responses with policy check layer"],
        ["CRM bolt-ons (Salesforce Einstein, Zendesk AI)", "Locked into single ecosystem. Limited reasoning depth.", "Ecosystem-agnostic. Integrates into any stack."],
        ["Enterprise contact center AI (Genesys, NICE)", "Expensive, slow to deploy, poor out-of-box AI quality.", "Faster time to value. Modern LLM core. API-first."],
      ].map((row, i) => new TableRow({
        children: row.map((text, j) => new TableCell({
          children: [new Paragraph({ children: [new TextRun({ text, font: "Arial", size: 19, color: j === 2 ? C.teal : C.text, bold: j === 2 })], spacing: { before: 60, after: 60 } })],
          width: { size: [2200, 3680, 3480][j], type: WidthType.DXA },
          shading: { fill: i % 2 === 0 ? C.grayLight : C.white, type: ShadingType.CLEAR },
          borders: allBorders(C.border),
          margins: { top: 80, bottom: 80, left: 140, right: 140 },
        })),
      })),
    ],
  }),

  spacer(160),

  // 8. MVP SCOPE
  heading1("8. Suggested MVP Scope"),
  bodyText("Start focused. The MVP should prove end-to-end resolution quality on a narrow set of high-volume, low-complexity ticket types — then expand from that foundation."),
  spacer(80),
  heading3("Phase 1 — Prove resolution quality (months 1–3)"),
  bullet("Connect to one CRM or inbox (Zendesk or Intercom recommended as first integration)"),
  bullet("Ingest knowledge base documents and product FAQs as the grounding corpus"),
  bullet("Handle the top 20–30 ticket types by volume: password resets, order status, billing queries, account changes"),
  bullet("Build the knowledge-grounded response layer with policy verification before send"),
  bullet("Instrument CSAT-protected deflection as the primary dashboard metric from day one"),
  spacer(60),
  heading3("Phase 2 — Add autonomous actions (months 4–6)"),
  bullet("Connect to backend APIs: order management, billing, account systems"),
  bullet("Enable the agent to execute actions (refunds, resets, updates) without human approval on pre-approved action types"),
  bullet("Build the escalation bundle: full context handoff with sentiment score and recommended action"),
  bullet("Launch smart escalation routing based on complexity classification"),
  spacer(60),
  heading3("Phase 3 — Scale and learn (months 7–12)"),
  bullet("Add omnichannel support: email, chat, WhatsApp, in-app"),
  bullet("Build the analytics layer: resolution pattern detection, knowledge gap surfacing"),
  bullet("Enable multi-language support using LLM translation layer"),
  bullet("Introduce proactive support: detect issues before customers raise tickets"),

  spacer(160),

  // 9. MONETIZATION
  heading1("9. Monetization Model"),
  bodyText("The strongest monetization model aligns pricing with the value ResolveAI delivers — resolution, not seat licenses."),
  spacer(80),
  makePillarTable([
    { name: "Resolution-based pricing", desc: "Charge per successful resolution (ticket closed with positive CSAT, no repeat contact within 7 days). Directly aligns revenue with value delivered. Easiest to justify to buyers.", tag: "Recommended primary model", color: C.brand, fill: C.brandLight },
    { name: "Conversation volume tiers", desc: "Monthly subscription tiered by conversation volume. Predictable for the customer, predictable for ResolveAI. Common in the market and easiest to compare-shop.", tag: "Low friction for procurement", color: C.teal, fill: C.tealLight },
    { name: "Platform fee + usage", desc: "Base platform fee for access plus per-resolution or per-conversation charges. Captures base revenue while scaling with customer growth.", tag: "Best for enterprise accounts", color: C.purple, fill: C.purpleLight },
    { name: "ROI-share model", desc: "Advanced: charge a percentage of the measurable savings generated (reduced headcount requirement, lower cost-per-ticket). High upside but requires rigorous measurement infrastructure.", tag: "Future growth model", color: C.amber, fill: C.amberLight },
  ]),

  spacer(160),

  // 10. SUGGESTED TECH STACK
  heading1("10. Suggested Tech Stack"),
  bodyText("ResolveAI should be built API-first, LLM-agnostic, and CRM-agnostic. The architecture choices that matter most are the ones that preserve flexibility as the product grows."),
  spacer(80),
  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2400, 2400, 4560],
    rows: [
      new TableRow({
        children: [
          new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "Layer", font: "Arial", size: 20, bold: true, color: C.white })], spacing: { before: 60, after: 60 } })], width: { size: 2400, type: WidthType.DXA }, shading: { fill: C.brand, type: ShadingType.CLEAR }, borders: allBorders(C.brand), margins: { top: 80, bottom: 80, left: 140, right: 140 } }),
          new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "Recommended choices", font: "Arial", size: 20, bold: true, color: C.white })], spacing: { before: 60, after: 60 } })], width: { size: 2400, type: WidthType.DXA }, shading: { fill: C.brand, type: ShadingType.CLEAR }, borders: allBorders(C.brand), margins: { top: 80, bottom: 80, left: 140, right: 140 } }),
          new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "Why", font: "Arial", size: 20, bold: true, color: C.white })], spacing: { before: 60, after: 60 } })], width: { size: 4560, type: WidthType.DXA }, shading: { fill: C.brand, type: ShadingType.CLEAR }, borders: allBorders(C.brand), margins: { top: 80, bottom: 80, left: 140, right: 140 } }),
        ],
      }),
      ...[
        ["LLM core", "Claude API (Anthropic)", "Best-in-class reasoning, instruction following, and safety guardrails. Extended context window handles long support threads."],
        ["Knowledge retrieval", "RAG with vector DB (Pinecone, Weaviate, or pgvector)", "Grounds responses in verified documents. Eliminates hallucinations on policy and product questions."],
        ["Agent orchestration", "LangGraph or custom state machine", "Manages the receive → classify → retrieve → plan → verify → learn loop reliably."],
        ["CRM integration", "REST APIs + Webhooks", "Zendesk, Salesforce, Intercom all expose robust APIs. Build a connector abstraction layer from day one."],
        ["Backend", "Python (FastAPI) or Node.js", "Fast to iterate, extensive AI library support, easy to hire for."],
        ["Analytics", "ClickHouse or BigQuery", "Column-store for fast aggregation of resolution metrics and CSAT patterns at scale."],
        ["Auth & multi-tenancy", "Auth0 or Clerk", "Enterprise SSO from day one. Multi-tenant isolation is critical for B2B SaaS trust."],
      ].map((row, i) => new TableRow({
        children: row.map((text, j) => new TableCell({
          children: [new Paragraph({ children: [new TextRun({ text, font: "Arial", size: 19, color: C.text })], spacing: { before: 60, after: 60 } })],
          width: { size: [2400, 2400, 4560][j], type: WidthType.DXA },
          shading: { fill: i % 2 === 0 ? C.grayLight : C.white, type: ShadingType.CLEAR },
          borders: allBorders(C.border),
          margins: { top: 80, bottom: 80, left: 140, right: 140 },
        })),
      })),
    ],
  }),

  spacer(160),

  // 11. NEXT STEPS
  heading1("11. Your Next Steps"),
  bodyText("Four concrete directions to move from understanding to building. Each maps to one of the key open questions for ResolveAI."),
  spacer(80),
  makeNextStepsTable([
    { title: "Define your beachhead market", desc: "Pick one vertical (e-commerce, SaaS, fintech) and one support channel (email or live chat) for the MVP. Depth beats breadth in the early stage — a product that resolves 95% of order status queries for e-commerce wins more than one that handles 60% of queries across all industries." },
    { title: "Map your grounding corpus", desc: "Identify what knowledge base content the agent will reason from. FAQ documents, policy PDFs, historical ticket resolutions, and product documentation are the raw material. The quality of this corpus is the primary determinant of resolution accuracy." },
    { title: "Choose your first CRM integration", desc: "Zendesk and Intercom are the best starting points — large customer bases, well-documented APIs, and strong communities. Build a clean abstraction layer from the start so adding Salesforce, Freshdesk, or a custom system is additive, not a rewrite." },
    { title: "Instrument CSAT-protected deflection on day one", desc: "Before launching any AI responses, define your measurement framework. CSAT-protected deflection (deflection rate gated by flat or improving CSAT) is the metric that separates genuine resolution from deflection theatre. Build the dashboard before the product — it will guide every product decision." },
  ]),

  spacer(200),

  // CLOSING
  new Paragraph({
    children: [new TextRun({ text: "ResolveAI is a high-conviction product idea at exactly the right moment. The market is accelerating, the tooling is mature, and the problem is deeply unsolved. The teams that build resolution-first agentic support today will define the standard that everyone else benchmarks against in 2027.", font: "Arial", size: 22, color: C.muted, italics: true })],
    spacing: { before: 0, after: 0 },
    border: { left: { style: BorderStyle.SINGLE, size: 20, color: C.brand, space: 10 } },
    indent: { left: 360 },
  }),
  spacer(80),
];

// ── ASSEMBLE DOCUMENT ─────────────────────────────────────────────────────────
const doc = new Document({
  styles: {
    default: {
      document: { run: { font: "Arial", size: 22, color: C.text } },
    },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "Arial", color: C.brand },
        paragraph: { spacing: { before: 360, after: 160 }, outlineLevel: 0 },
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial", color: C.black },
        paragraph: { spacing: { before: 280, after: 100 }, outlineLevel: 1 },
      },
      {
        id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: "Arial", color: C.brand },
        paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 2 },
      },
    ],
  },
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } },
        }],
      },
    ],
  },
  sections: [
    {
      properties: {
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
        },
      },
      headers: {
        default: new Header({
          children: [
            new Paragraph({
              children: [
                new TextRun({ text: "ResolveAI", font: "Arial", size: 18, bold: true, color: C.brand }),
                new TextRun({ text: "  |  Agentic Customer Support Resolution System", font: "Arial", size: 18, color: C.muted }),
              ],
              border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: C.border, space: 4 } },
              spacing: { after: 0 },
            }),
          ],
        }),
      },
      footers: {
        default: new Footer({
          children: [
            new Paragraph({
              children: [
                new TextRun({ text: "Confidential  |  May 2026  |  Page ", font: "Arial", size: 18, color: C.muted }),
                new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 18, color: C.muted }),
              ],
              border: { top: { style: BorderStyle.SINGLE, size: 4, color: C.border, space: 4 } },
              alignment: AlignmentType.RIGHT,
              spacing: { before: 0 },
            }),
          ],
        }),
      },
      children: [...coverPage, ...sections_content],
    },
  ],
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("outputs/ResolveAI_Blueprint.docx", buffer);
  console.log("Done — ResolveAI_Blueprint.docx written");
});
