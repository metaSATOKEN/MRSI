#!/usr/bin/env python3
"""Repair PDF navigation or assemble the MRSI collection; no experiment runs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import unicodedata

from pypdf import PdfReader, PdfWriter
from pypdf.generic import ArrayObject, DictionaryObject, Fit, NameObject

PAPERS = Path(__file__).resolve().parent
LINK_PREFIX = "https://github.com/metaSATOKEN/MRSI#collected-page-"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def normalized(text):
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", text).lower())


def add_outline(writer, reader, entries, offset=0, parent=None, texts=None):
    """Preserve hierarchy; optionally resolve headings misplaced at page breaks."""
    previous = None
    corrected = []
    for entry in entries:
        if isinstance(entry, list):
            require(previous is not None, "Outline child has no parent")
            corrected.extend(add_outline(writer, reader, entry, offset, previous, texts))
            continue
        page = reader.get_destination_page_number(entry)
        require(page is not None and 0 <= page < len(reader.pages), "Invalid bookmark")
        if texts is not None and normalized(entry.title) not in texts[page]:
            matches = [i for i, text in enumerate(texts) if normalized(entry.title) in text]
            require(len(matches) == 1 and abs(matches[0] - page) <= 1,
                    f"Review bookmark manually: {entry.title!r}, matches={matches}")
            corrected.append({"title": entry.title, "from": page + 1, "to": matches[0] + 1})
            page = matches[0]
        previous = writer.add_outline_item(entry.title, offset + page, parent=parent,
                                           fit=Fit.fit(), is_open=False)
    return corrected


def repair_bookmarks(path):
    reader = PdfReader(path)
    texts = [normalized(page.extract_text()) for page in reader.pages]
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    writer.root_object.pop(NameObject("/Outlines"), None)
    changes = add_outline(writer, reader, reader.outline, texts=texts)
    if changes:
        temporary = path.with_suffix(".navigation-tmp.pdf")
        writer.write(temporary)
        checked = PdfReader(temporary)
        require(len(checked.pages) == len(reader.pages), "Page count changed during repair")
        for old, new in zip(reader.pages, checked.pages):
            require(old.get_contents().get_data() == new.get_contents().get_data(),
                    "Page content changed during navigation repair")
        temporary.replace(path)
    writer.close()
    return changes


def assemble(frontmatter, output, layout):
    front = PdfReader(frontmatter)
    require(len(front.pages) == layout["front_pages"], "Front-matter pagination changed")
    writer = PdfWriter()
    writer.append(front, import_outline=False)
    writer.add_outline_item("Cover", 0)
    writer.add_outline_item("Series summary", 1)
    contents = writer.add_outline_item("Master contents", 2)
    readers = []
    for index, part in enumerate(layout["parts"]):
        source = PAPERS / part["folder"] / (part["name"] + ".pdf")
        reader = PdfReader(source)
        offset = len(writer.pages)
        require(offset == part["start"] and len(reader.pages) == part["pages"],
                f"Update front matter and collection.json for {source.name}")
        writer.add_outline_item(part["label"], 2 + index, parent=contents)
        writer.append(reader, import_outline=False)
        parent = writer.add_outline_item(part["label"] + " — " + part["title"], offset,
                                         bold=True, is_open=False)
        add_outline(writer, reader, reader.outline, offset, parent)
        readers.append((reader, offset))
        actual = {entry.title: reader.get_destination_page_number(entry) + 1
                  for entry in reader.outline if not isinstance(entry, list)}
        for entry in part["entries"]:
            title = "Abstract" if entry["title"] == "Title and abstract" else entry["title"]
            require(actual.get(title) == entry["local_page"], f"Stale contents entry: {title}")
    require(len(writer.pages) == layout["total_pages"], "Unexpected combined page count")
    expected_targets = {entry["global_page"] - 1
                        for part in layout["parts"] for entry in part["entries"]}
    linked_targets = set()
    link_count = 0
    for page in writer.pages[:layout["front_pages"]]:
        for ref in page.get("/Annots", []):
            annotation = ref.get_object()
            uri = annotation.get("/A", {}).get("/URI", "")
            if not str(uri).startswith(LINK_PREFIX):
                continue
            destination = int(str(uri)[len(LINK_PREFIX):]) - 1
            require(destination in expected_targets, f"Unknown contents destination: {uri}")
            annotation[NameObject("/A")] = DictionaryObject({
                NameObject("/S"): NameObject("/GoTo"),
                NameObject("/D"): ArrayObject([
                    writer.pages[destination].indirect_reference, NameObject("/Fit")]),
            })
            linked_targets.add(destination)
            link_count += 1
    require(linked_targets == expected_targets, "Some contents destinations have no link")
    writer.set_page_label(0, layout["front_pages"] - 1, style="/r", start=1)
    for index, part in enumerate(layout["parts"], 1):
        prefix = f"P{index}-" if index <= 4 else "S-"
        writer.set_page_label(part["start"], part["start"] + part["pages"] - 1,
                              style="/D", prefix=prefix, start=1)
    writer.add_metadata({
        "/Title": "LLM Memory, Records, and Continued Use — MRSI Collected Edition v1.4",
        "/Author": "Kentaro Sato",
        "/Subject": "Content, Provenance, Updates, and Authorization",
        "/Keywords": "MRSI; collected edition v1.4; LLM memory; multi-role systems",
    })
    output.parent.mkdir(parents=True, exist_ok=True)
    writer.write(output)
    combined = PdfReader(output)
    require(len(combined.pages) == layout["total_pages"], "Written page count changed")
    for reader, offset in readers:
        for i, page in enumerate(reader.pages):
            require(page.get_contents().get_data() == combined.pages[offset + i].get_contents().get_data(),
                    f"Page content changed at combined page {offset + i + 1}")
            require(page.extract_text() == combined.pages[offset + i].extract_text(),
                    f"Extracted text changed at combined page {offset + i + 1}")
    for page in combined.pages:
        for ref in page.get("/Annots", []):
            action = ref.get_object().get("/A", {})
            require(not str(action.get("/URI", "")).startswith(LINK_PREFIX), "Unresolved TOC link")
            require(action.get("/S") != "/Launch", "Unexpected executable action")
    writer.close()
    return {"pages": len(combined.pages), "contents_links": link_count,
            "individual_pages_unchanged": sum(len(r.pages) for r, _ in readers)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repair-bookmarks", action="store_true",
                        help="Repair individual PDF bookmarks in this working copy, then exit")
    parser.add_argument("--frontmatter", type=Path, help="Compiled seven-page front matter")
    parser.add_argument("--output", type=Path, default=PAPERS / "mrsi_series_collected_edition.pdf")
    args = parser.parse_args()
    layout = json.loads((PAPERS / "collection.json").read_text())
    if args.repair_bookmarks:
        result = {p["name"]: repair_bookmarks(PAPERS / p["folder"] / (p["name"] + ".pdf"))
                  for p in layout["parts"]}
    else:
        if args.frontmatter is None:
            parser.error("--frontmatter is required")
        result = assemble(args.frontmatter, args.output, layout)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
