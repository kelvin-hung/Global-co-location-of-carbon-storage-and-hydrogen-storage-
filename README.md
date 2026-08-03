# Global-co-location-of-carbon-storage-and-hydrogen-storage-
this code is used for submission to Joule
# Code and data for: Global co-location of carbon storage and hydrogen storage reveals the coupled subsurface of the net-zero energy system

This archive contains the database, analysis code, and figure code required to reproduce
every quantitative result and figure in the manuscript. It accompanies the manuscript as
part of Data S1 and will be deposited at Zenodo under a DOI upon submission.

## Contents

```
code/
  ccus_style.py          Shared figure style system (fonts, palette, panel labels)
  plots.py               Reusable panel-drawing functions for all composite figures
  analyze.py             Proximity (haversine), build-out timeline, and attrition analyses
                         -> writes analysis.json
  analyze2.py            Fleet-anatomy analyses (sector capacity, storage fate by cohort,
                         project scale, transport modes, UHS media/depth/purity/energy)
                         -> writes analysis2.json
  analyze3.py            Supplemental sensitivity analyses (proximity reference sets,
                         Kaplan-Meier specifications, termination calendar, country
                         detail, study-level LCA dispersion) -> writes analysis3.json
  make_si_figs.py        Figures S1-S4 (Document S1)
  make_si_doc.js         Builds Document S1 (Supplemental Information docx)
  make_fig6.py           Kaplan-Meier estimator (Greenwood CIs) for the power-sector cohort
                         -> writes km.json (also renders a standalone survival figure)
  make_joule_figs.py     Figures 1-3 (state of play; framework + LCA; quantitative + survival)
  make_joule_figs2.py    Figures 4-6 (CCUS anatomy; UHS anatomy; resources + readiness)
  make_fig2_editable.js  Editable PowerPoint version of Figure 2 (native shapes)
  requirements.txt       Python dependencies
data/
  ccus_americas.psv      CCUS project records, Americas (pipe-delimited)
  ccus_emea.psv          CCUS project records, Europe-Middle East-Africa
  ccus_apac.psv          CCUS project records, Asia-Pacific
  uhs.psv                Underground hydrogen storage site records
  blueh2.psv             Hydrogen/ammonia-with-CCS project records
  geo_ccus.psv           Geocodes and basin attribution, CCUS
  geo_uhs_blueh2.psv     Geocodes and basin attribution, UHS and H2+CCS
  lca_h2.psv             LCA evidence records, hydrogen production pathways
  lca_uhs_ccs.psv        LCA evidence records, UHS, CCS chains, coupled systems
  storage_resources.psv  Cited CO2 (Gt) and H2-cavern (TWh/PWh) resource estimates
  survival.psv           Event-history data for the Kaplan-Meier analysis
Data_S1_Global_CCUS_UHS_Coupling_Database.xlsx
                         The consolidated 13-sheet database (README sheet inside
                         documents every sheet and field)
```

## Reproducing the results

Python 3.11. Install dependencies:

```
pip install -r code/requirements.txt
```

Run, from the repository root (scripts assume the data/ directory alongside them;
adjust the `D` path constant at the top of each script if relocating):

```
python code/analyze.py        # proximity, timeline, attrition  -> analysis.json
python code/analyze2.py       # fleet anatomy                   -> analysis2.json
python code/make_fig6.py      # Kaplan-Meier                    -> km.json
python code/analyze3.py       # supplemental sensitivities      -> analysis3.json
python code/make_si_figs.py   # Figures S1-S4
node code/make_si_doc.js      # Document S1 (docx)
python code/make_joule_figs.py    # Figures 1-3 (PNG 400 dpi + PDF + SVG)
python code/make_joule_figs2.py   # Figures 4-6 (PNG 400 dpi + PDF + SVG)
node   code/make_fig2_editable.js # Figure2_editable.pptx (requires pptxgenjs)
```

The world basemap uses the Natural Earth 1:110m dataset bundled with
geopandas < 1.0 (`geopandas.datasets.get_path("naturalearth_lowres")`).

## Methods summary

Distances are great-circle (haversine) values between site-level coordinates.
Life-cycle results are harmonized to kg CO2e per kg H2 (LHV 120 MJ/kg; GWP100
unless noted). UHS working energies are converted at 33.3 GWh per kt H2 (LHV).
The Kaplan-Meier estimator is applied to the power-sector cohort (n = 56) with
cancellations or suspensions as events; operational and developing projects are
right-censored at 2026 and completed pilots at completion year; confidence
intervals use Greenwood's formula. Full procedures are described in the
Experimental Procedures section of the manuscript.

## Provenance and caveats

Every project record carries one source URL; announcement years in survival.psv
carry a per-record confidence flag. The database is a curated, source-attributed
core rather than a census; capacities are nameplate values. Compiled August 2026.

## License

Data: CC BY 4.0. Code: MIT. [Adjust as required at deposit.]
