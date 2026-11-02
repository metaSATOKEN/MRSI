# English Figures for the Second Report

These figures accompany [English manuscript v0.1](../MRSI_Paper2-en-v1.0.md) and render the two diagrams in the finalized [Japanese manuscript v0.4](../MRSI_Paper2-ja-v1.0.md). Captions are in the manuscript, at Sections 3.3 and 4.1. Each diagram can be used independently during subsequent typesetting.

| Figure | Subject | Vector file | Raster file | PNG dimensions |
| --- | --- | --- | --- | --- |
| 1 | Update control and subsequent use | [SVG](fig01-update-control-en-v1.svg) | [PNG](fig01-update-control-en-v1.png) | 4,350 × 3,030 pixels, 300 dpi |
| 2 | Saved-note continuity and diagnostic branches | [SVG](fig02-study-connections-en-v1.svg) | [PNG](fig02-study-connections-en-v1.png) | 4,350 × 2,850 pixels, 300 dpi |

Prefer SVG for scalable placement. SVG text is outlined to preserve font appearance on another machine. PNG is a fallback; its nominal canvas size is 14.5 × 10.1 inches for Figure 1 and 14.5 × 9.5 inches for Figure 2. Use a full-width placement and check the final text size after scaling. The Markdown manuscript embeds the PNG files for broad preview compatibility. No PDF files are included.

## Content boundaries

Figure 1 shows accepted updates. Customer information remains model-written, while the designated own/shared observation fields receive row-selection and copying control. The first-cycle readout requests only shared values; the later diagnostic and second-cycle readouts also request customer information. The figure describes processing responsibilities and does not assert that all model-written fields are correct.

Figure 2 shows the second cycle continuing from the first cycle's actual saved notes. The selective-use diagnostic manipulates copies of those notes; its manipulated inputs do not feed the second cycle. The customer-update diagnostic uses separate new initial states. The diagrams introduce no new results or independent samples.

## Regeneration

Source: [make_figures_en_v1.py](make_figures_en_v1.py). Requires Python and Matplotlib; uses the Agg renderer and DejaVu Sans. From this directory:

```sh
python3 make_figures_en_v1.py
```

The script writes only the two SVG/PNG pairs and [layout-checks-en-v1.json](layout-checks-en-v1.json), which checks that box text fits its allocated bounds. It performs no network calls or model inference. Both rendered PNGs were also visually inspected for clipping, arrow direction, branch relationships, and agreement with the captions. The SVG files were checked for valid XML and self-contained graphics.
