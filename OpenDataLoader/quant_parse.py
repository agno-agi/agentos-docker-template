"""
quant_parse.py — Convert QuantConnect PDFs to markdown and load into knowledge base.

Large PDFs (> SPLIT_PAGE_THRESHOLD pages) are pre-split into NUM_SPLITS equal parts
before being handed to opendataloader, so the JVM never has to process thousands of
pages in a single pass.
"""

import math
import sys
from pathlib import Path

import opendataloader_pdf
from pypdf import PdfReader, PdfWriter

# Repo root is one level up from this file
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.quant_knowledge_agent import load_quant_knowledge

SPLIT_PAGE_THRESHOLD = 300   # PDFs with more pages than this get pre-split
NUM_SPLITS = 3               # Number of equal parts to create

knowledge_dir = Path(__file__).parent.parent / "knowledge" / "QuantConnect"
output_dir = Path(__file__).parent / "output"
split_dir = Path(__file__).parent / "split"
output_dir.mkdir(parents=True, exist_ok=True)
split_dir.mkdir(parents=True, exist_ok=True)


def split_pdf(pdf_path: Path, num_parts: int) -> list[Path]:
    """Split *pdf_path* into *num_parts* equal page-range chunks.

    Returns a list of paths to the generated split files (in split_dir).
    """
    reader = PdfReader(str(pdf_path))
    total = len(reader.pages)
    pages_per_part = math.ceil(total / num_parts)
    parts: list[Path] = []

    for i in range(num_parts):
        start = i * pages_per_part
        end = min(start + pages_per_part, total)
        if start >= total:
            break

        writer = PdfWriter()
        for page_num in range(start, end):
            writer.add_page(reader.pages[page_num])

        part_path = split_dir / f"{pdf_path.stem}_part{i + 1}.pdf"
        with part_path.open("wb") as f:
            writer.write(f)

        print(f"  Split part {i + 1}/{num_parts}: {part_path.name} (pages {start + 1}–{end})")
        parts.append(part_path)

    return parts


# ------------------------------------------------------------------
# Build the file list, pre-splitting large PDFs
# ------------------------------------------------------------------
files_to_convert: list[str] = []

for pdf in sorted(knowledge_dir.glob("*.pdf")):
    try:
        reader = PdfReader(str(pdf))
        page_count = len(reader.pages)
    except Exception as exc:
        print(f"Skipping {pdf.name} — could not read: {exc}")
        continue

    if page_count > SPLIT_PAGE_THRESHOLD:
        print(f"Splitting {pdf.name} ({page_count} pages) into {NUM_SPLITS} parts...")
        parts = split_pdf(pdf, NUM_SPLITS)
        files_to_convert.extend(str(p) for p in parts)
    else:
        print(f"Using {pdf.name} as-is ({page_count} pages)")
        files_to_convert.append(str(pdf))

# ------------------------------------------------------------------
# Convert to markdown
# ------------------------------------------------------------------
print(f"\nConverting {len(files_to_convert)} file(s) to markdown...")
opendataloader_pdf.convert(
    input_path=files_to_convert,
    output_dir=str(output_dir),
    format="markdown",
)

# ------------------------------------------------------------------
# Load into knowledge base
# ------------------------------------------------------------------
print("\nLoading converted files into knowledge base...")
load_quant_knowledge()
print("Done.")
