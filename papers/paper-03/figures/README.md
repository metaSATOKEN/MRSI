# English Figures for the Third Report

These figures accompany [English manuscript v0.1](../MRSI_Paper3-en-v1.0.md) and redraw the diagrams in author-approved Japanese v0.2. They introduce no new results.

| Figure | Content | Raster | Vector |
| --- | --- | --- | --- |
| 1 | Actual execution paths in ST01/ST02, conditional recheck, and computed-evidence supply schedule | [300-dpi PNG](fig01-support-timing-en-v1.png) | [SVG](fig01-support-timing-en-v1.svg) |
| 2 | Separate formation and confirmation panels in JR01, retaining old ST02 notes in confirmation | [300-dpi PNG](fig02-fixed-input-panels-en-v1.png) | [SVG](fig02-fixed-input-panels-en-v1.svg) |

The manuscript embeds PNGs with relative links. For later PDF production, the SVG files retain vector geometry and outline fonts to avoid font substitution. Captions and discussion are in the manuscript. Keep figure numbers aligned with that text.

## Regeneration

Run [make_figures_en_v1.py](make_figures_en_v1.py) with Python and Matplotlib:

```sh
python3 make_figures_en_v1.py
```

Generation is entirely offline and creates only SVG, PNG, and [layout-check JSON](layout-checks-en-v1.json). Automated checks cover text fitting within boxes and the canvas.

Figure 1 uses a support schedule instead of intersecting dashed arrows. “Recheck” supply applies when that stage is activated; only COUNTER activates it. A separate constructed-counterproposal diagnostic is excluded from the main path. Figure 2 shows two disconnected response panels, not a pipeline carrying new formation outputs into new confirmation calls.
