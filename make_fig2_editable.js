const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3 x 7.5 in

const BLUE = "0072B2", TEAL = "009E73", ORANGE = "E69F00", INK = "1A1A1A",
      MUT = "666666", SAND = "7A6420", RUST = "B25000";
const F = "Arial";

// ---------------- Slide 1: Panel A as native shapes ----------------
const s = pres.addSlide();
s.addText([{ text: "A  ", options: { bold: true, fontSize: 18 } },
           { text: "Coupling CCUS and UHS through the blue-hydrogen value chain", options: { fontSize: 14 } }],
          { x: 0.4, y: 0.15, w: 12.0, h: 0.4, fontFace: F, color: INK, margin: 0 });

function chainBox(x, w, title, l2, l3, fill, line, boldTitle = true) {
  s.addShape(pres.ShapeType.roundRect, {
    x, y: 1.0, w, h: 1.25, fill: { color: fill }, line: { color: line, width: 1.5 }, rectRadius: 0.08,
  });
  const runs = [{ text: title, options: { bold: boldTitle, fontSize: 12, breakLine: true } }];
  if (l2) runs.push({ text: l2, options: { fontSize: 10, breakLine: true } });
  if (l3) runs.push({ text: l3, options: { fontSize: 10 } });
  s.addText(runs, { x, y: 1.0, w, h: 1.25, align: "center", valign: "middle", fontFace: F, color: INK, margin: 0.02 });
}
chainBox(0.5, 2.0, "Natural gas", "upstream CH₄", "leakage 0.2–8%", "F4F1EC", "8A8A8A");
chainBox(2.95, 2.2, "Reformer", "ATR/SMR with", ">90% CO₂ capture", "EAF2FA", BLUE);
chainBox(5.6, 2.0, "Low-carbon H₂", "0.8–4 kg CO₂e", "per kg H₂", "EAF2FA", BLUE);
chainBox(8.05, 2.2, "Underground H₂ storage (UHS)", "+0.23–0.28 kg CO₂e", "per kg H₂ cycled", "E7F5F0", TEAL);
chainBox(10.7, 2.1, "End use", "power, industry,", "mobility", "F4F1EC", "8A8A8A");

function harrow(x1, x2, y, color, opts = {}) {
  s.addShape(pres.ShapeType.line, {
    x: x1, y, w: x2 - x1, h: 0,
    line: Object.assign({ color, width: 2.25, endArrowType: "triangle" }, opts),
  });
}
harrow(2.52, 2.93, 1.62, "8A8A8A");
harrow(5.17, 5.58, 1.62, BLUE);
// two-way seasonal cycling
harrow(7.62, 8.03, 1.50, TEAL);
s.addShape(pres.ShapeType.line, { x: 7.62, y: 1.76, w: 0.41, h: 0, flipH: true,
  line: { color: TEAL, width: 2.25, endArrowType: "triangle" } });
s.addText("seasonal cycling", { x: 7.35, y: 0.62, w: 1.6, h: 0.3, fontSize: 9, fontFace: F, color: MUT, align: "center", margin: 0 });
harrow(10.27, 10.68, 1.62, TEAL);

// CO2 branch down
s.addShape(pres.ShapeType.line, { x: 4.05, y: 2.27, w: 0, h: 1.15,
  line: { color: BLUE, width: 2.75, endArrowType: "triangle" } });
s.addText("≈ 8–9 kg CO₂ captured per kg H₂", { x: 4.2, y: 2.62, w: 3.0, h: 0.3, fontSize: 10, fontFace: F, color: BLUE, margin: 0 });

// CO2 storage box
s.addShape(pres.ShapeType.roundRect, { x: 2.95, y: 3.45, w: 2.2, h: 1.15,
  fill: { color: "EAF2FA" }, line: { color: BLUE, width: 1.5 }, rectRadius: 0.08 });
s.addText([{ text: "Geological CO₂ storage", options: { bold: true, fontSize: 12, breakLine: true } },
           { text: "permanent", options: { fontSize: 10 } }],
          { x: 2.95, y: 3.45, w: 2.2, h: 1.15, align: "center", valign: "middle", fontFace: F, color: INK, margin: 0.02 });

// Archetype 3 dashed arrow (cushion gas)
s.addShape(pres.ShapeType.line, { x: 5.2, y: 2.35, w: 3.3, h: 1.65, flipV: true,
  line: { color: ORANGE, width: 2.25, dashType: "dash", endArrowType: "triangle" } });
s.addText("≈ +8% working H₂ capacity", { x: 6.2, y: 3.35, w: 2.9, h: 0.3, fontSize: 10, fontFace: F, color: RUST, margin: 0 });

// shared substrate band
s.addShape(pres.ShapeType.roundRect, { x: 0.6, y: 5.15, w: 12.1, h: 1.6,
  fill: { color: "FBF6EC" }, line: { color: "D9C89A", width: 1.5 }, rectRadius: 0.1 });
s.addText("SHARED BASIN RESOURCES", { x: 0.6, y: 5.22, w: 12.1, h: 0.35, align: "center",
  bold: true, fontSize: 12, fontFace: F, color: SAND, margin: 0 });
const shared = ["Pore space and\ncaprock integrity", "Wells and drilling\ncapacity", "Pipelines and\nrights-of-way",
                "Monitoring and\nMMV networks", "Subsurface data", "Regulation and\nsocial licence"];
shared.forEach((t, i) => {
  s.addText(t, { x: 0.75 + i * 2.0, y: 5.62, w: 1.95, h: 0.9, align: "center", valign: "middle",
    fontSize: 9.5, fontFace: F, color: "5C4D1A", margin: 0 });
});
// connectors into substrate
s.addShape(pres.ShapeType.line, { x: 4.05, y: 4.6, w: 0, h: 0.55, line: { color: "C4A94E", width: 1.5 } });
s.addShape(pres.ShapeType.line, { x: 9.15, y: 2.25, w: 0, h: 2.9, line: { color: "C4A94E", width: 1.5 } });

// archetype badges
function badge(x, y, num, color, label, labelW) {
  s.addShape(pres.ShapeType.ellipse, { x, y, w: 0.34, h: 0.34, fill: { color }, line: { color: "FFFFFF", width: 1 } });
  s.addText(num, { x, y, w: 0.34, h: 0.34, align: "center", valign: "middle", bold: true,
    fontSize: 12, fontFace: F, color: "FFFFFF", margin: 0 });
  s.addText(label, { x: x + 0.4, y: y + 0.01, w: labelW, h: 0.32, valign: "middle", bold: true,
    fontSize: 10.5, fontFace: F, color, margin: 0 });
}
badge(0.5, 0.62, "2", BLUE, "Integrated value chain: CO₂ down, H₂ cycling", 4.2);
badge(0.62, 4.68, "1", SAND, "Shared-basin co-location", 2.6);
badge(5.65, 2.95, "3", RUST, "CO₂ cushion gas", 1.7);

s.addNotes("Figure 2A, editable version. All boxes, arrows, badges, and labels are native PowerPoint shapes. Colors: CCUS blue 0072B2, UHS teal 009E73, H2+CCS orange E69F00.");

// ---------------- Slide 2: Panel B as image ----------------
const s2 = pres.addSlide();
s2.addText([{ text: "B  ", options: { bold: true, fontSize: 18 } },
            { text: "Harmonized life-cycle emissions of hydrogen pathways", options: { fontSize: 14 } }],
           { x: 0.4, y: 0.2, w: 12.0, h: 0.4, fontFace: F, color: INK, margin: 0 });
s2.addImage({ path: "/home/claude/ccus_uhs/panelB_ladder.png", x: 0.7, y: 0.9, w: 11.9, h: 5.0 });
s2.addText("Data-driven panel rendered from make_joule_figs.py (draw_ladder in plots.py). Edit values in the script and re-export, or request the underlying numbers from Data S1 (Harmonized_GWP sheet). A fully editable vector of the complete figure is provided as JouleFig2_concept_lca.svg.",
           { x: 0.7, y: 6.35, w: 11.9, h: 0.8, fontSize: 10, fontFace: F, color: MUT, margin: 0 });

pres.writeFile({ fileName: "/home/claude/ccus_uhs/Figure2_editable.pptx" }).then(() => console.log("pptx written"));
