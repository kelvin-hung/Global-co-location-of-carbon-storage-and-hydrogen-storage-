/* Document S1: Supplemental Information (Cell Press style) — Figures S1-S4, Tables S1-S5 */
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, AlignmentType, PageBreak,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType, VerticalAlign,
} = require("docx");

const D = "/home/claude/ccus_uhs";
const FONT = "Arial";
const RED = "E4262C";

// Auto-subscript chemical formulas (CO2, H2, CH4, NH3, N2O, SO2) in plain text; URLs untouched.
function subRuns(text, base) {
  const out = [];
  for (const part of String(text).split(/(https?:\/\/[^\s)]+)/)) {
    if (/^https?:\/\//.test(part)) { if (part) out.push(new TextRun({ ...base, text: part })); continue; }
    for (const piece of part.split(/(?<![A-Za-z0-9])(CO2|CH4|NH3|N2O|SO2|H2)/)) {
      if (!piece) continue;
      if (/^(CO2|CH4|NH3|N2O|SO2|H2)$/.test(piece)) {
        out.push(new TextRun({ ...base, text: piece.slice(0, -1) }));
        out.push(new TextRun({ ...base, text: piece.slice(-1), subScript: true }));
      } else {
        out.push(new TextRun({ ...base, text: piece }));
      }
    }
  }
  return out;
}

function P(segments, opts = {}) {
  const runs = segments.flatMap(seg =>
    typeof seg === "object" && !Array.isArray(seg)
      ? [new TextRun({ font: FONT, size: 20, ...seg })]
      : subRuns(seg, { font: FONT, size: 20 }));
  return new Paragraph({
    children: runs, spacing: { after: 140, line: 276 },
    alignment: AlignmentType.JUSTIFIED, ...opts,
  });
}

function capPara(label, rest) {
  return new Paragraph({
    spacing: { before: 80, after: 60, line: 252 },
    alignment: AlignmentType.JUSTIFIED,
    children: [
      ...subRuns(label, { bold: true, font: FONT, size: 18 }),
      ...rest.flatMap(seg => typeof seg === "object"
        ? [new TextRun({ font: FONT, size: 18, ...seg })]
        : subRuns(seg, { font: FONT, size: 18 })),
    ],
  });
}

function noteP(text) {
  return new Paragraph({
    spacing: { before: 60, after: 240, line: 240 },
    alignment: AlignmentType.JUSTIFIED,
    children: subRuns(text, { font: FONT, size: 16, color: "555555" }),
  });
}

function img(path) {
  const b = fs.readFileSync(path);
  const w = b.readUInt32BE(16), h = b.readUInt32BE(20);
  const maxW = 620;
  const scale = Math.min(maxW / w, 660 / h);
  return new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { before: 160, after: 40 },
    children: [new ImageRun({
      type: "png", data: b,
      transformation: { width: Math.round(w * scale), height: Math.round(h * scale) },
    })],
  });
}

const THIN = { style: BorderStyle.SINGLE, size: 4, color: "BBBBBB" };
const NONE = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
function cell(text, { bold = false, width, fill, size = 16, align = AlignmentType.LEFT } = {}) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    verticalAlign: VerticalAlign.CENTER,
    shading: fill ? { type: ShadingType.CLEAR, fill } : undefined,
    borders: { top: THIN, bottom: THIN, left: NONE, right: NONE },
    margins: { top: 40, bottom: 40, left: 60, right: 60 },
    children: [new Paragraph({
      alignment: align,
      children: subRuns(String(text), { bold, font: FONT, size }),
    })],
  });
}
function table(widths, header, rows, { size = 16 } = {}) {
  return new Table({
    width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    columnWidths: widths,
    rows: [
      new TableRow({ tableHeader: true, children: header.map((t, i) =>
        cell(t, { bold: true, width: widths[i], fill: "F5F3F0", size })) }),
      ...rows.map(r => new TableRow({ children: r.map((t, i) =>
        cell(t, { width: widths[i], size, align: typeof t === "number" ? AlignmentType.RIGHT : AlignmentType.LEFT })) })),
    ],
  });
}

/* ---------- data ---------- */
const A3 = JSON.parse(fs.readFileSync(`${D}/analysis3.json`, "utf8"));

// Table S1: leading coupling basins (counts as in Figure 3D + jurisdictions)
const basinsS1 = [
  ["US Gulf Coast", 17, 3, 6, "Frio, Miocene sands; Gulf Coast salt domes", "United States"],
  ["North Sea", 15, 1, 5, "Utsira, Bunter, Johansen; Zechstein salt", "Norway, UK, Netherlands, Denmark"],
  ["Alberta (WCSB)", 14, 1, 4, "Basal Cambrian sands; Lotsberg salt", "Canada"],
  ["NW Australia", 9, 0, 0, "Dupuy, Barrow Delta (offshore)", "Australia"],
  ["Ordos", 8, 0, 0, "Ordovician saline; ultra-deep aquifers", "China"],
  ["Williston", 7, 0, 1, "Broom Creek, Deadwood", "United States, Canada"],
  ["Arabian Platform", 7, 0, 3, "Carbonate aquifers; depleted gas", "Saudi Arabia, UAE, Qatar"],
  ["East Irish Sea", 5, 0, 1, "Ormskirk sandstone; Cheshire salt", "United Kingdom"],
];

// Table S2: harmonized GWP ladder (matches Figure 2B)
const ladderS2 = [
  ["Grey SMR (no capture)", "9.2", "11.0", "14.0", "Natural-gas SMR, upstream CH4 included; no CO2 capture"],
  ["Blue H2, as commonly built", "5.0", "6.5", "9.3", "55-90% capture, ~1-2% upstream CH4 leakage"],
  ["Blue H2, best practice", "0.8", "3.0", "4.0", ">90% capture on all stacks, <=1% CH4 leakage, low-carbon utilities"],
  ["Turquoise (methane pyrolysis)", "0.8", "6.0", "9.9", "Highly sensitive to electricity source and carbon-black credit"],
  ["Green electrolysis", "0.5", "2.9", "4.6", "Dedicated renewables, embodied emissions of stacks and plant included"],
  ["UHS cycle adder (this work)", "0.23", "-", "0.28", "Per kg H2 cycled through salt-cavern or porous-media storage; compression duty, cushion-gas share, 0.5-2% losses"],
];

// Table S3: storage resources from psv
const resRows = fs.readFileSync(`${D}/data/storage_resources.psv`, "utf8")
  .trim().split("\n").slice(1).map(l => l.split("|"))
  .map(r => [r[0] === "CO2" ? "CO2" : "H2", r[1], r[2], r[3], r[4], r[6]]);

// Table S4: 36 terminated projects
const svRows = fs.readFileSync(`${D}/data/survival.psv`, "utf8")
  .trim().split("\n").slice(1).map(l => l.split("|"))
  .filter(r => r[3] === "death")
  .sort((a, b) => Number(a[4]) - Number(b[4]) || a[0].localeCompare(b[0]))
  .map(r => [r[0], r[1] === "power" ? "Power" : "Non-power", r[2], r[4],
             String(Math.max(Number(r[4]) - Number(r[2]), 1)), r[5]]);

// Table S5: readiness matrix
const critsS5 = ["Operating CO2 storage", "Operating or proven UHS", "H2+CCS anchor project",
                 "CO2 resource assessed", "H2 storage potential assessed", "Single jurisdiction"];
const MS5 = {
  "US Gulf Coast": [2, 2, 2, 2, 1, 2],
  "Alberta-Williston": [2, 1, 2, 2, 1, 1],
  "NW Europe": [2, 2, 2, 2, 2, 0],
  "Eastern China": [1, 1, 1, 2, 1, 2],
  "Arabian Platform": [2, 0, 2, 1, 0, 2],
  "SE Australia": [1, 1, 0, 2, 0, 2],
  "NW Australia": [1, 0, 0, 2, 0, 2],
  "Sarawak-Malay": [1, 0, 0, 1, 0, 1],
};
const SYM = ["Absent (0)", "Partial (1)", "In place (2)"];

/* ---------- document ---------- */
const kids = [];

// Title block
kids.push(new Paragraph({
  spacing: { before: 200, after: 60 },
  children: [new TextRun({ text: "Supplemental information", bold: true, font: FONT, size: 34 })],
}));
kids.push(new Paragraph({
  spacing: { after: 60 },
  children: [new TextRun({
    text: "Coupling carbon capture and underground hydrogen storage: a global project-level assessment of the blue-hydrogen value chain",
    bold: true, font: FONT, size: 24 })],
}));
kids.push(P([{ text: "Document S1. Figures S1–S4 and Tables S1–S5", italics: true }]));
kids.push(P(["This document provides sensitivity and robustness analyses supporting the main-text claims, together with the full evidence tables underlying Figures 1, 2, 3, and 6. All analyses derive from the project-level database released as Data S1 and are reproducible with the archived code."]));

// ---- Figure S1
kids.push(new Paragraph({ children: [new PageBreak()] }));
kids.push(img(`${D}/JouleFigS1_proximity_sensitivity.png`));
kids.push(capPara("Figure S1. Proximity between UHS sites and CCUS projects under alternative reference sets, related to Figure 3.", [
  " (A) Cumulative distributions of great-circle distance from each of the 39 UHS sites to the nearest CCUS project, computed against three reference sets: all 206 geocoded active CCUS projects (baseline, teal), the 93 operational projects only (blue), and the 121 active projects with dedicated geological storage, excluding EOR and utilization-only projects (orange). (B) Summary statistics for each reference set. The headline co-location result weakens but does not disappear under the strictest definitions: the median distance rises from 139 km (baseline) to 221 km (dedicated storage) and 335 km (operational only), while the share of UHS sites within 200 km of a CCUS project remains 31–62% across all three definitions.",
]));
kids.push(noteP("Distances are great-circle values between site-level coordinates and support basin-scale statements only; they are not pipeline routings."));

// ---- Figure S2
kids.push(img(`${D}/JouleFigS2_survival_robustness.png`));
kids.push(capPara("Figure S2. Robustness of the power-sector survival analysis, related to Figure 3.", [
  " (A) Kaplan–Meier survival under three specifications: the baseline (56 power-sector CCS projects, 22 terminal events), a stricter definition counting only outright cancellations as events with the six suspended projects treated as censored (16 events), and a specification excluding the nine records with low-confidence dating (47 projects, 19 events). Ten-year survival spans 0.52–0.65 across specifications; the baseline estimate of 0.52 is therefore conservative but not fragile. (B) Calendar of all 36 recorded terminations across sectors. Terminations cluster in two waves: the 2010s wave of first-generation power projects and a second wave of 13 terminations in 2024–2025 driven by policy reversals and offtake uncertainty.",
]));

// ---- Figure S3
kids.push(new Paragraph({ children: [new PageBreak()] }));
kids.push(img(`${D}/JouleFigS3_country_detail.png`));
kids.push(capPara("Figure S3. Status-resolved national CCUS portfolios, related to Figure 1.", [
  " (A) Full status breakdown of the 15 largest national CCUS portfolios in the database (242 projects worldwide). (B) Active capture capacity by country. The comparison separates depth from maturity: the United States leads on both counts (54 projects, 81.3 Mt CO2 per year active capacity), while Norway carries the largest capacity concentrated in the fewest projects (41.0 Mt across 10) and Japan's large project count (11) corresponds to only 0.3 Mt of active capacity, reflecting a pilot-dominated portfolio.",
]));

// ---- Figure S4
kids.push(img(`${D}/JouleFigS4_lca_spread.png`));
kids.push(capPara("Figure S4. Study-level dispersion behind the harmonized emission ranges, related to Figure 2.", [
  " (A) The 26 individual GWP100 estimates for hydrogen production pathways retained after unit harmonization (kg CO2e per kg H2, lower heating value), plotted at publication year; vertical bars span each study's reported range and points mark central estimates. (B) Full range and median of central estimates by pathway family. Blue-hydrogen estimates (n=10) span 0.1–9.5 kg CO2e per kg H2 across capture-rate and leakage assumptions, and the harmonized best-practice range used in the main text (1–4, shaded band in A) sits within the envelope of every post-2020 blue-hydrogen study. One green-hydrogen study extends to 41.4 kg CO2e per kg H2 for grid-connected electrolysis in fossil-heavy grids, underscoring that electricity origin, not electrolysis itself, dominates that pathway's footprint.",
]));

// ---- Table S1
kids.push(new Paragraph({ children: [new PageBreak()] }));
kids.push(capPara("Table S1. The eight leading coupling basins, related to Figures 1 and 3.", [
  " Project counts are active projects in this database (cancelled and suspended projects excluded).",
]));
kids.push(table(
  [1750, 950, 800, 950, 3050, 2200],
  ["Basin", "Active CCUS", "UHS sites", "H2+CCS", "Key storage plays", "Jurisdictions"],
  basinsS1,
));
kids.push(noteP("Basin attribution follows the geological basin of the storage site where disclosed, otherwise the project location. UHS counts include operating and pilot-stage sites within the basin outline."));

// ---- Table S2
kids.push(capPara("Table S2. Harmonized life-cycle emission intensities used in the main text, related to Figure 2.", [
  " Units are kg CO2e per kg H2 (GWP100, lower heating value 120 MJ per kg). Ranges harmonize the study-level estimates of Figure S4 to common system boundaries.",
]));
kids.push(table(
  [2500, 800, 950, 800, 4650],
  ["Pathway", "Low", "Central", "High", "Key assumptions"],
  ladderS2,
));
kids.push(noteP("The UHS cycle adder is incurred once per kilogram of hydrogen cycled through geological storage and equals 2-10% of the best-practice blue-hydrogen footprint."));

// ---- Table S3
kids.push(new Paragraph({ children: [new PageBreak()] }));
kids.push(capPara("Table S3. Assessed geological storage resources for CO2 and hydrogen, related to Figure 6.", [
  " Estimates are reported as published; bases differ (SRMS-classified, theoretical, or mapped capacity) and the table therefore supports order-of-magnitude comparisons only.",
]));
kids.push(table(
  [700, 1900, 1700, 950, 2450, 2000],
  ["Gas", "Region", "Estimate", "Unit", "Basis", "Source"],
  resRows,
  { size: 14 },
));

// ---- Table S4
kids.push(new Paragraph({ children: [new PageBreak()] }));
kids.push(capPara("Table S4. Event history of the 36 terminated projects in the survival dataset, related to Figure 3.", [
  " Entry is the year of public announcement; exit is the year cancellation or indefinite suspension became public. Duration is in years and is floored at 1. Confidence grades the documentary basis of the two dates (high: primary announcement located; medium: secondary reporting; low: inferred from database status changes).",
]));
kids.push(table(
  [3700, 1200, 1250, 1250, 1150, 1150],
  ["Project", "Sector", "Announced", "Terminated", "Duration", "Confidence"],
  svRows,
  { size: 14 },
));

// ---- Table S5
kids.push(new Paragraph({ children: [new PageBreak()] }));
kids.push(capPara("Table S5. Scoring rubric and scores for the basin readiness matrix, related to Figure 6.", [
  " Each criterion is scored 2 (in place), 1 (partial or proposed), or 0 (absent), assessed against the project database as of mid-2026. Criteria: operating CO2 storage (any operational injection at scale in the basin); operating or proven UHS (hydrogen or equivalent salt-cavern storage demonstrated); H2+CCS anchor project (an active blue-hydrogen or ammonia project in the basin); CO2 resource assessed (published basin-scale storage assessment); H2 storage potential assessed (published basin-scale UHS capacity estimate); single jurisdiction (basin lies within one regulatory regime).",
]));
kids.push(table(
  [1900, 1300, 1300, 1300, 1300, 1300, 1300],
  ["Basin", ...critsS5.map(c => c.replace(" project", "").replace(" assessed", " assess."))],
  Object.entries(MS5).map(([b, row]) => [b, ...row.map(v => SYM[v])]),
  { size: 13 },
));
kids.push(noteP("Alberta-Williston scores 1 on jurisdiction because the coupled system spans Alberta/Saskatchewan and North Dakota; NW Europe scores 0 because the North Sea coupling system spans five regulatory regimes. Scores are assessments by the authors from the sources in Data S1 and are intended as a transparent, reproducible screening, not a ranking of investment quality."));

const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: 20 } } } },
  sections: [{
    properties: { page: { margin: { top: 1140, bottom: 1140, left: 1250, right: 1250 } } },
    children: kids,
  }],
});

Packer.toBuffer(doc).then(b => {
  fs.writeFileSync(`${D}/Document_S1_Supplemental_Information.docx`, b);
  console.log("Document S1 written");
});
