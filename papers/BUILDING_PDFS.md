# Build the English PDFs

The four reports and the technical synthesis each have a complete TeX source alongside their Markdown source and figures. The collected edition appends these five PDFs to a cover, a one-page summary, and five pages of master contents. No model calls or scientific recalculations are part of this build.

Use a separate checkout and its root `.venv/bin/python`, following [RUNNING.md](../RUNNING.md). The build was checked with Python 3.13.17, Tectonic 0.17.0, and pypdf 6.10.0. Tectonic supplies the TeX packages and TeX Gyre fonts; its first run may download missing packages. Keep its package cache if you need to rebuild offline.

Install the PDF assembly dependency in that working copy:

```sh
.venv/bin/python -m pip install -r papers/requirements-pdf.txt
```

Run the following commands from the checkout root. `tectonic` must resolve to the installed compiler. Each command writes the standalone PDF next to its TeX source.

```sh
tectonic -X compile --untrusted --outdir papers/paper-01 papers/paper-01/MRSI_Paper1-en-v1.0.tex
tectonic -X compile --untrusted --outdir papers/paper-02 papers/paper-02/MRSI_Paper2-en-v1.0.tex
tectonic -X compile --untrusted --outdir papers/paper-03 papers/paper-03/MRSI_Paper3-en-v1.0.tex
tectonic -X compile --untrusted --outdir papers/paper-04 papers/paper-04/MRSI_Paper4-en-v1.0.tex
tectonic -X compile --untrusted --outdir papers/two-role-failure-design papers/two-role-failure-design/manuscript-en-v0.3-2026-10-13.tex
.venv/bin/python -B papers/build_collected.py --repair-bookmarks
```

The last command checks headings against extracted page text and corrects bookmarks that land on the preceding page at a page break. It preserves the page content streams and stops on an ambiguous match.

Compile the front matter into an external build directory and assemble the collection:

```sh
mkdir -p /tmp/mrsi-pdf-build
tectonic -X compile --untrusted --outdir /tmp/mrsi-pdf-build papers/collected_edition_frontmatter.tex
.venv/bin/python -B papers/build_collected.py --frontmatter /tmp/mrsi-pdf-build/collected_edition_frontmatter.pdf
```

The default result is `papers/mrsi_series_collected_edition.pdf`. Use `--output /path/to/a/new-file.pdf` to choose another destination. The assembly checks 7 front-matter pages and 26, 18, 15, 17, and 30 report pages, respectively: **113 pages total**. It turns master-contents entries into internal PDF links, preserves each report's page content, and adds section bookmarks and report-specific page labels.

The front-matter TeX and [collection map](collection.json) record the current pagination. If you edit a report and change its pagination, update those contents entries together; assembly stops if they disagree with the individual PDFs. The [series summary](collected-edition.md) is also available as Markdown.

The TeX sources are the typesetting sources for this edition. Markdown edits are not imported automatically: update the corresponding TeX when revising the text. Render and visually inspect new PDFs, including tables, figures, code blocks, and section transitions. Scientific results should be checked using the separate [verification procedures](../VERIFICATION.md).

## Evidence links

Relative evidence links in Markdown resolve within the repository. The PDFs use GitHub links pinned to evidence commit `9443de315d283874df0c27e0e99b8c04f400709d`; citations to external papers retain their original targets. This keeps the linked experimental materials stable as the repository develops. PDF generation can change metadata and object ordering, so a rebuild is not guaranteed to be byte-identical to the distributed PDF.
