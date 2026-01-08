"""Rewrite links from Jupyter Book format to Hugo URLs."""

from pathlib import Path
from typing import Dict, List, Tuple, Optional
import re
from urllib.parse import urlparse, unquote


class LinkRewriter:
    """Rewrite internal links for Hugo compatibility."""

    def __init__(self, file_mapping: Dict[str, str], source_dir: Path, content_dir: Path):
        """
        Initialize the link rewriter.

        Args:
            file_mapping: Dict mapping source file paths to Hugo content paths
            source_dir: Root directory of Jupyter Book source
            content_dir: Hugo content directory
        """
        self.file_mapping = file_mapping
        self.source_dir = source_dir
        self.content_dir = content_dir
        self.broken_links = []

    def rewrite_links(self, markdown: str, current_file: Path) -> Tuple[str, List[str]]:
        """
        Rewrite all links in markdown content.

        Args:
            markdown: Markdown content with links
            current_file: Path to the current source file (for resolving relative links)

        Returns:
            Tuple of (rewritten_markdown, list_of_broken_links)
        """
        self.broken_links = []

        # Pattern for markdown links: [text](url)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'

        def replace_link(match):
            link_text = match.group(1)
            link_url = match.group(2)

            # Skip external links, anchors, and mailto links
            if link_url.startswith(('http://', 'https://', 'mailto:', '#')):
                return match.group(0)

            # Skip Hugo shortcodes (already processed)
            if '{{' in link_url and '}}' in link_url:
                return match.group(0)

            # Rewrite internal link
            new_url = self._rewrite_url(link_url, current_file)

            if new_url is None:
                self.broken_links.append(link_url)
                # Keep original link but mark it
                return f'[{link_text}]({link_url} "⚠️ Broken link")'

            return f'[{link_text}]({new_url})'

        markdown = re.sub(link_pattern, replace_link, markdown)

        # Also handle HTML <a> tags
        html_link_pattern = r'<a\s+([^>]*href=")([^"]+)("[^>]*)>'

        def replace_html_link(match):
            prefix = match.group(1)
            link_url = match.group(2)
            suffix = match.group(3)

            # Skip external links
            if link_url.startswith(('http://', 'https://', 'mailto:', '#')):
                return match.group(0)

            # Rewrite internal link
            new_url = self._rewrite_url(link_url, current_file)

            if new_url is None:
                self.broken_links.append(link_url)
                return match.group(0)

            return f'<a {prefix}{new_url}{suffix}>'

        markdown = re.sub(html_link_pattern, replace_html_link, markdown)

        return markdown, self.broken_links

    def _rewrite_url(self, url: str, current_file: Path) -> Optional[str]:
        """
        Rewrite a single URL from Jupyter Book to Hugo format.

        Args:
            url: Original URL
            current_file: Current file path (for resolving relatives)

        Returns:
            Rewritten URL or None if link is broken
        """
        # Parse URL to handle anchors
        parsed = urlparse(url)
        path_part = unquote(parsed.path)
        anchor = parsed.fragment

        # Skip empty paths
        if not path_part:
            if anchor:
                return f'#{anchor}'
            return None

        # Resolve relative path
        if path_part.startswith('/'):
            # Absolute path from source root
            target_path = self.source_dir / path_part.lstrip('/')
        else:
            # Relative path from current file
            current_dir = current_file.parent if current_file.is_file() else current_file
            target_path = (current_dir / path_part).resolve()

        # Normalize path
        try:
            relative_to_source = target_path.relative_to(self.source_dir)
        except ValueError:
            # Path is outside source directory
            return None

        # Remove extension for lookup
        base_path = str(relative_to_source.with_suffix(''))

        # Try to find in mapping with various extensions
        hugo_path = None
        for ext in ['', '.md', '.ipynb']:
            lookup_key = f"{base_path}{ext}"
            if lookup_key in self.file_mapping:
                hugo_path = self.file_mapping[lookup_key]
                break

        if not hugo_path:
            # Try just the filename
            filename = relative_to_source.stem
            for key, value in self.file_mapping.items():
                if Path(key).stem == filename:
                    hugo_path = value
                    break

        if not hugo_path:
            return None

        # Convert to Hugo URL (relative to content root)
        # Hugo URLs are like /section/page/ for pages
        hugo_url = f'/{hugo_path}/'

        # Add anchor if present
        if anchor:
            hugo_url += f'#{anchor}'

        return hugo_url


def build_file_mapping(toc, source_dir: Path, content_dir: Path) -> Dict[str, str]:
    """
    Build a mapping from source file paths to Hugo content paths.

    Args:
        toc: TableOfContents object
        source_dir: Jupyter Book source directory
        content_dir: Hugo content directory

    Returns:
        Dict mapping source paths to Hugo content paths
    """
    mapping = {}

    # Map root file
    if toc.root and toc.root.file:
        # Root becomes _index.md
        mapping[toc.root.file] = "_index"
        mapping[f"{toc.root.file}.md"] = "_index"
        mapping[f"{toc.root.file}.ipynb"] = "_index"

    # Map all other files
    for part in toc.parts:
        # Create section slug from caption
        section_slug = _slugify(part.caption)

        for chapter in part.chapters:
            if chapter.file:
                # Chapter becomes section/chapter-slug
                chapter_slug = Path(chapter.file).stem
                hugo_path = f"{section_slug}/{chapter_slug}"

                mapping[chapter.file] = hugo_path
                mapping[f"{chapter.file}.md"] = hugo_path
                mapping[f"{chapter.file}.ipynb"] = hugo_path

                # Map sections
                for section in chapter.sections:
                    if section.file:
                        section_slug_name = Path(section.file).stem
                        section_hugo_path = f"{section_slug}/{section_slug_name}"

                        mapping[section.file] = section_hugo_path
                        mapping[f"{section.file}.md"] = section_hugo_path
                        mapping[f"{section.file}.ipynb"] = section_hugo_path

    return mapping


def _slugify(text: str) -> str:
    """Convert text to a URL-friendly slug."""
    # Convert to lowercase
    slug = text.lower()

    # Replace spaces and special characters with hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = slug.strip('-')

    return slug
