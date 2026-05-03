"""
LocalFileLoader — Agno toolkit for loading local files into a knowledge base.

Supports PDF, Markdown, and plain-text files. Files larger than LARGE_FILE_THRESHOLD
are automatically split into smaller chunks before insertion.

Pass an instance to an Agent's `tools=` list so the agent can trigger loading on
demand, or call `load_directory` / `load_file` directly from startup code.
"""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from agno.tools import Toolkit

if TYPE_CHECKING:
    from agno.knowledge import Knowledge

logger = logging.getLogger(__name__)

SUPPORTED_SUFFIXES = {".pdf", ".md", ".txt", ".rst"}

# Files larger than this will be split before loading
LARGE_FILE_THRESHOLD = 10 * 1024 * 1024  # 10 MB

# Target size for each chunk (aim well under the threshold)
CHUNK_TARGET_BYTES = 4 * 1024 * 1024  # 4 MB


class LocalFileLoader(Toolkit):
    """Toolkit that loads local files into an Agno Knowledge base."""

    def __init__(self, knowledge: "Knowledge", name: str = "local_file_loader") -> None:
        super().__init__(name=name)
        self.knowledge = knowledge
        self.register(self.load_directory)
        self.register(self.load_file)
        self.register(self.list_files)

    # ------------------------------------------------------------------
    # Public helpers (usable directly, not just as agent tools)
    # ------------------------------------------------------------------

    def load_directory(self, directory: str, recursive: bool = True) -> str:
        """Load all supported files from *directory* into the knowledge base.

        Args:
            directory: Absolute or relative path to the directory.
            recursive: When True (default) descend into sub-directories.
        """
        dir_path = Path(directory).expanduser().resolve()
        if not dir_path.is_dir():
            return f"Directory not found: {directory}"

        pattern = "**/*" if recursive else "*"
        loaded, skipped, failed = [], [], []

        for path in sorted(dir_path.glob(pattern)):
            if not path.is_file() or path.suffix.lower() not in SUPPORTED_SUFFIXES:
                continue
            n_loaded, n_skipped, n_failed = self._insert_with_splitting(path)
            if n_loaded:
                loaded.append(path.name)
            elif n_skipped:
                skipped.append(path.name)
            if n_failed:
                failed.append(path.name)

        parts = []
        if loaded:
            parts.append(f"Loaded {len(loaded)} file(s): {', '.join(loaded)}")
        if skipped:
            parts.append(f"Skipped {len(skipped)} already-existing file(s)")
        if failed:
            parts.append(f"Failed {len(failed)} file(s): {', '.join(failed)}")
        return " | ".join(parts) if parts else "No supported files found."

    def load_file(self, file_path: str) -> str:
        """Load a single file into the knowledge base.

        Args:
            file_path: Absolute or relative path to the file.
        """
        path = Path(file_path).expanduser().resolve()
        if not path.is_file():
            return f"File not found: {file_path}"
        if path.suffix.lower() not in SUPPORTED_SUFFIXES:
            return f"Unsupported file type '{path.suffix}'. Supported: {', '.join(SUPPORTED_SUFFIXES)}"

        n_loaded, n_skipped, n_failed = self._insert_with_splitting(path)
        if n_failed:
            return f"Failed to load: {path.name}"
        if n_skipped and not n_loaded:
            return f"Already in knowledge base: {path.name}"
        return f"Loaded {path.name} ({n_loaded} chunk(s))"

    def list_files(self, directory: str, recursive: bool = True) -> str:
        """List supported files in *directory* without loading them.

        Args:
            directory: Absolute or relative path to the directory.
            recursive: When True (default) descend into sub-directories.
        """
        dir_path = Path(directory).expanduser().resolve()
        if not dir_path.is_dir():
            return f"Directory not found: {directory}"

        pattern = "**/*" if recursive else "*"
        lines = []
        for p in sorted(dir_path.glob(pattern)):
            if p.is_file() and p.suffix.lower() in SUPPORTED_SUFFIXES:
                size_mb = p.stat().st_size / (1024 * 1024)
                tag = " [large — will split]" if p.stat().st_size > LARGE_FILE_THRESHOLD else ""
                lines.append(f"{p.relative_to(dir_path)}  ({size_mb:.1f} MB){tag}")
        return "\n".join(lines) if lines else "No supported files found."

    # ------------------------------------------------------------------
    # Splitting logic
    # ------------------------------------------------------------------

    def _insert_with_splitting(self, path: Path) -> tuple[int, int, int]:
        """Insert a file, splitting it first if it exceeds the threshold.

        Returns:
            Tuple of (loaded_chunks, skipped_chunks, failed_chunks).
        """
        if path.stat().st_size <= LARGE_FILE_THRESHOLD:
            result = self._insert(path, name=path.stem)
            loaded = 1 if result == "loaded" else 0
            skipped = 1 if result == "skipped" else 0
            failed = 1 if result == "failed" else 0
            return loaded, skipped, failed

        logger.info("%s is >10 MB — splitting into chunks.", path.name)
        suffix = path.suffix.lower()

        if suffix == ".pdf":
            chunks = self._split_pdf(path)
        else:
            chunks = self._split_text(path)

        loaded = skipped = failed = 0
        for chunk_path, chunk_name in chunks:
            result = self._insert(chunk_path, name=chunk_name)
            if result == "loaded":
                loaded += 1
            elif result == "skipped":
                skipped += 1
            else:
                failed += 1

        return loaded, skipped, failed

    def _split_pdf(self, path: Path) -> list[tuple[Path, str]]:
        """Split a large PDF into page-range chunks using pypdf."""
        try:
            from pypdf import PdfReader, PdfWriter
        except ImportError:
            logger.warning("pypdf not installed — loading %s as-is.", path.name)
            return [(path, path.stem)]

        try:
            reader = PdfReader(str(path))
        except Exception as exc:
            logger.warning("Could not open PDF %s: %s", path.name, exc)
            return []

        total_pages = len(reader.pages)
        if total_pages == 0:
            return []

        # Estimate pages per chunk from average page size
        avg_page_bytes = path.stat().st_size / total_pages
        pages_per_chunk = max(1, int(CHUNK_TARGET_BYTES / avg_page_bytes))

        chunks: list[tuple[Path, str]] = []
        tmp_dir = Path(tempfile.mkdtemp(prefix="agentos_split_"))

        for start in range(0, total_pages, pages_per_chunk):
            end = min(start + pages_per_chunk, total_pages)
            writer = PdfWriter()
            for page_num in range(start, end):
                writer.add_page(reader.pages[page_num])

            chunk_name = f"{path.stem}_p{start + 1}-{end}"
            chunk_path = tmp_dir / f"{chunk_name}.pdf"
            with chunk_path.open("wb") as f:
                writer.write(f)
            chunks.append((chunk_path, chunk_name))
            logger.info("PDF chunk: %s (%d pages)", chunk_name, end - start)

        return chunks

    def _split_text(self, path: Path) -> list[tuple[Path, str]]:
        """Split a large text/markdown file on heading boundaries or byte size."""
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            logger.warning("Could not read %s: %s", path.name, exc)
            return []

        suffix = path.suffix.lower()
        sections = (
            self._split_markdown_by_heading(text)
            if suffix == ".md"
            else self._split_by_size(text)
        )

        tmp_dir = Path(tempfile.mkdtemp(prefix="agentos_split_"))
        chunks: list[tuple[Path, str]] = []

        for idx, section in enumerate(sections, start=1):
            if not section.strip():
                continue
            chunk_name = f"{path.stem}_part{idx}"
            chunk_path = tmp_dir / f"{chunk_name}{path.suffix}"
            chunk_path.write_text(section, encoding="utf-8")
            chunks.append((chunk_path, chunk_name))
            logger.info("Text chunk: %s (%d chars)", chunk_name, len(section))

        return chunks

    def _split_markdown_by_heading(self, text: str) -> list[str]:
        """Split markdown at top-level (#) or second-level (##) headings."""
        import re

        # Split on lines that start a heading (# or ##)
        parts = re.split(r"(?m)^(?=#{1,2} )", text)

        # Merge tiny sections into neighbours until each chunk is ~CHUNK_TARGET_BYTES
        chunks: list[str] = []
        current = ""
        for part in parts:
            if len((current + part).encode()) > CHUNK_TARGET_BYTES and current:
                chunks.append(current)
                current = part
            else:
                current += part
        if current:
            chunks.append(current)
        return chunks

    def _split_by_size(self, text: str) -> list[str]:
        """Split plain text into fixed-size byte chunks, breaking on newlines."""
        chunks: list[str] = []
        encoded = text.encode("utf-8")
        start = 0
        while start < len(encoded):
            end = start + CHUNK_TARGET_BYTES
            if end >= len(encoded):
                chunks.append(encoded[start:].decode("utf-8", errors="replace"))
                break
            # Walk back to the nearest newline to avoid splitting mid-line
            newline = encoded.rfind(b"\n", start, end)
            cut = newline + 1 if newline > start else end
            chunks.append(encoded[start:cut].decode("utf-8", errors="replace"))
            start = cut
        return chunks

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _insert(self, path: Path, name: str | None = None) -> str:
        """Insert a single file path into the knowledge base."""
        try:
            self.knowledge.insert(
                name=name or path.stem,
                path=str(path),
                skip_if_exists=True,
            )
            logger.info("Inserted '%s' into knowledge base.", name or path.stem)
            return "loaded"
        except FileExistsError:
            return "skipped"
        except Exception as exc:
            logger.warning("Failed to insert '%s': %s", name or path.stem, exc)
            return "failed"
