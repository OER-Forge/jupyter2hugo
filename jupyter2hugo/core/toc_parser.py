"""Parse Jupyter Book _toc.yml files and build content tree."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any
import yaml


@dataclass
class TocEntry:
    """Represents a single entry in the table of contents."""

    file: str
    title: Optional[str] = None
    sections: List['TocEntry'] = field(default_factory=list)
    weight: int = 0
    parent: Optional[str] = None
    level: int = 0  # 0=root, 1=chapter, 2=section, 3=subsection

    @property
    def file_path(self) -> str:
        """Get the file path with extension added if needed."""
        if not self.file:
            return ""
        if not any(self.file.endswith(ext) for ext in ['.md', '.ipynb']):
            # Try to guess the extension - will be resolved during processing
            return self.file
        return self.file

    @property
    def slug(self) -> str:
        """Get the slug for Hugo URLs (filename without extension)."""
        return Path(self.file).stem if self.file else ""

    @property
    def hugo_section(self) -> str:
        """Get the Hugo section (directory) for this entry."""
        if not self.file:
            return ""
        parts = Path(self.file).parts
        if len(parts) > 1:
            return parts[0]
        return ""


@dataclass
class TocPart:
    """Represents a part in the table of contents."""

    caption: str
    chapters: List[TocEntry] = field(default_factory=list)
    weight: int = 0


@dataclass
class TableOfContents:
    """Complete table of contents structure."""

    format: str
    root: TocEntry
    parts: List[TocPart] = field(default_factory=list)

    def get_all_files(self) -> List[TocEntry]:
        """Get a flat list of all file entries in order."""
        files = [self.root] if self.root and self.root.file else []

        for part in self.parts:
            for chapter in part.chapters:
                files.append(chapter)
                files.extend(chapter.sections)

        return files

    def get_file_mapping(self) -> Dict[str, TocEntry]:
        """Get a mapping from file path to TocEntry."""
        mapping = {}
        for entry in self.get_all_files():
            if entry.file:
                # Store without extension for flexible matching
                base = str(Path(entry.file).with_suffix(''))
                mapping[base] = entry
                # Also store with common extensions
                mapping[f"{base}.md"] = entry
                mapping[f"{base}.ipynb"] = entry
        return mapping


class TocParser:
    """Parser for Jupyter Book _toc.yml files."""

    def __init__(self, toc_path: Path):
        """
        Initialize the TOC parser.

        Args:
            toc_path: Path to the _toc.yml file
        """
        self.toc_path = toc_path
        self.toc_dir = toc_path.parent

    def parse(self) -> TableOfContents:
        """
        Parse the _toc.yml file.

        Returns:
            TableOfContents object with parsed structure
        """
        with open(self.toc_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        toc_format = data.get('format', 'jb-book')
        root_file = data.get('root', '')

        # Create root entry
        root = TocEntry(file=root_file, level=0, weight=0)

        # Parse parts
        parts = []
        part_weight = 1

        for part_data in data.get('parts', []):
            part = self._parse_part(part_data, part_weight)
            parts.append(part)
            part_weight += 1

        # Handle simple chapter list (no parts)
        if 'chapters' in data and not parts:
            # Create a single default part
            part = TocPart(caption="Main", chapters=[], weight=1)
            chapter_weight = 1
            for chapter_data in data['chapters']:
                chapter = self._parse_chapter(chapter_data, part.caption, chapter_weight, level=1)
                part.chapters.append(chapter)
                chapter_weight += 1
            parts.append(part)

        return TableOfContents(format=toc_format, root=root, parts=parts)

    def _parse_part(self, part_data: Dict[str, Any], weight: int) -> TocPart:
        """Parse a part section."""
        caption = part_data.get('caption', f'Part {weight}')
        part = TocPart(caption=caption, weight=weight)

        chapter_weight = 1
        for chapter_data in part_data.get('chapters', []):
            chapter = self._parse_chapter(chapter_data, caption, chapter_weight, level=1)
            part.chapters.append(chapter)
            chapter_weight += 1

        return part

    def _parse_chapter(
        self,
        chapter_data: Dict[str, Any],
        parent: str,
        weight: int,
        level: int = 1
    ) -> TocEntry:
        """Parse a chapter or section entry."""
        file_path = chapter_data.get('file', '')
        title = chapter_data.get('title')

        chapter = TocEntry(
            file=file_path,
            title=title,
            weight=weight,
            parent=parent,
            level=level
        )

        # Parse sections recursively
        section_weight = 1
        for section_data in chapter_data.get('sections', []):
            section = self._parse_chapter(
                section_data,
                parent=title or file_path,
                weight=section_weight,
                level=level + 1
            )
            chapter.sections.append(section)
            section_weight += 1

        return chapter

    def resolve_file_path(self, entry: TocEntry) -> Optional[Path]:
        """
        Resolve the actual file path for a TOC entry.

        Args:
            entry: TocEntry to resolve

        Returns:
            Resolved Path or None if not found
        """
        if not entry.file:
            return None

        # Try with different extensions
        for ext in ['', '.md', '.ipynb']:
            candidate = self.toc_dir / f"{entry.file}{ext}"
            if candidate.exists():
                return candidate

        return None


def load_toc(toc_path: Path) -> TableOfContents:
    """
    Convenience function to load and parse a _toc.yml file.

    Args:
        toc_path: Path to _toc.yml

    Returns:
        Parsed TableOfContents
    """
    parser = TocParser(toc_path)
    return parser.parse()
