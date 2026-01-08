"""Generate Hugo front matter for pages."""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime
import yaml


@dataclass
class FrontMatter:
    """Hugo front matter for a page."""

    title: str
    weight: int = 0
    draft: bool = False
    date: Optional[str] = None
    description: Optional[str] = None

    # Menu configuration
    menu_parent: Optional[str] = None
    menu_name: Optional[str] = None
    menu_weight: Optional[int] = None

    # Content flags
    math: bool = False
    highlight: bool = False

    # Additional metadata
    tags: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    authors: List[str] = field(default_factory=list)

    # Custom parameters
    params: Dict[str, Any] = field(default_factory=dict)

    def to_yaml(self) -> str:
        """Convert front matter to YAML string."""
        data = {
            'title': self.title,
            'weight': self.weight,
        }

        if self.draft:
            data['draft'] = True

        if self.date:
            data['date'] = self.date
        else:
            # Use current date if not specified
            data['date'] = datetime.now().strftime('%Y-%m-%d')

        if self.description:
            data['description'] = self.description

        # Add menu configuration if present
        if self.menu_parent:
            menu_config = {}
            if self.menu_name:
                menu_config['name'] = self.menu_name
            else:
                menu_config['name'] = self.title

            menu_config['parent'] = self.menu_parent

            if self.menu_weight is not None:
                menu_config['weight'] = self.menu_weight
            else:
                menu_config['weight'] = self.weight

            data['menu'] = {'main': menu_config}

        # Add content flags
        if self.math:
            data['math'] = True

        if self.highlight:
            data['highlight'] = True

        # Add tags and categories
        if self.tags:
            data['tags'] = self.tags

        if self.categories:
            data['categories'] = self.categories

        if self.authors:
            data['authors'] = self.authors

        # Add custom parameters
        if self.params:
            data['params'] = self.params

        # Convert to YAML with proper formatting
        yaml_str = yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)

        return f"---\n{yaml_str}---\n\n"


class FrontMatterBuilder:
    """Build front matter from various sources."""

    @staticmethod
    def from_toc_entry(entry, part_caption: Optional[str] = None) -> FrontMatter:
        """
        Create front matter from a TOC entry.

        Args:
            entry: TocEntry object
            part_caption: Caption of the part (for menu parent)

        Returns:
            FrontMatter object
        """
        # Determine title
        title = entry.title if entry.title else entry.slug.replace('-', ' ').title()

        # Create front matter
        fm = FrontMatter(
            title=title,
            weight=entry.weight,
            menu_parent=part_caption,
            menu_weight=entry.weight,
        )

        return fm

    @staticmethod
    def from_metadata(
        title: str,
        weight: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
        part_caption: Optional[str] = None
    ) -> FrontMatter:
        """
        Create front matter from metadata dict.

        Args:
            title: Page title
            weight: Page weight for ordering
            metadata: Additional metadata
            part_caption: Part caption for menu parent

        Returns:
            FrontMatter object
        """
        fm = FrontMatter(
            title=title,
            weight=weight,
            menu_parent=part_caption,
            menu_weight=weight,
        )

        if not metadata:
            return fm

        # Set flags from metadata
        fm.math = metadata.get('has_math', False)
        fm.highlight = metadata.get('has_code', False)

        # Set other fields if present
        if 'description' in metadata:
            fm.description = metadata['description']

        if 'tags' in metadata:
            fm.tags = metadata['tags']

        if 'categories' in metadata:
            fm.categories = metadata['categories']

        if 'authors' in metadata:
            fm.authors = metadata['authors']

        if 'date' in metadata:
            fm.date = metadata['date']

        return fm

    @staticmethod
    def for_section_index(part_caption: str, weight: int = 0) -> FrontMatter:
        """
        Create front matter for a section index page (_index.md).

        Args:
            part_caption: Caption/title for the section
            weight: Weight for ordering

        Returns:
            FrontMatter object
        """
        return FrontMatter(
            title=part_caption,
            weight=weight,
            menu_parent=None,  # Section indexes don't have parents
            menu_name=part_caption,
            menu_weight=weight,
        )


def add_frontmatter(content: str, frontmatter: FrontMatter) -> str:
    """
    Add front matter to markdown content.

    Args:
        content: Markdown content
        frontmatter: FrontMatter object

    Returns:
        Content with front matter prepended
    """
    fm_yaml = frontmatter.to_yaml()
    return fm_yaml + content


def extract_title_from_markdown(markdown: str) -> Optional[str]:
    """
    Extract title from markdown content (first # heading).

    Args:
        markdown: Markdown content

    Returns:
        Title string or None
    """
    import re
    match = re.search(r'^#\s+(.+)$', markdown, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None


def remove_first_heading(markdown: str) -> str:
    """
    Remove the first # heading from markdown (since it's in front matter).

    Args:
        markdown: Markdown content

    Returns:
        Markdown without first heading
    """
    import re
    # Remove first top-level heading
    markdown = re.sub(r'^#\s+.+$\n?', '', markdown, count=1, flags=re.MULTILINE)
    return markdown.lstrip()
