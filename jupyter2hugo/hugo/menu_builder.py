"""Build Hugo menu configuration from TOC structure."""

from typing import List, Dict, Any


class MenuBuilder:
    """Build Hugo menu configuration."""

    @staticmethod
    def build_menu_config(toc) -> str:
        """
        Build Hugo menu configuration from TOC.

        Args:
            toc: TableOfContents object

        Returns:
            TOML configuration string for Hugo menus
        """
        menu_items = []

        # Add menu items for each part (section)
        for part in toc.parts:
            section_slug = _slugify(part.caption)
            menu_item = {
                'identifier': section_slug,
                'name': part.caption,
                'url': f'/{section_slug}/',
                'weight': part.weight
            }
            menu_items.append(menu_item)

        # Generate TOML
        toml_lines = []
        for item in menu_items:
            toml_lines.append("[[menu.main]]")
            toml_lines.append(f'  identifier = "{item["identifier"]}"')
            toml_lines.append(f'  name = "{item["name"]}"')
            toml_lines.append(f'  url = "{item["url"]}"')
            toml_lines.append(f'  weight = {item["weight"]}')
            toml_lines.append("")

        return "\n".join(toml_lines)

    @staticmethod
    def build_sidebar_data(toc) -> Dict[str, Any]:
        """
        Build sidebar navigation data structure.

        Args:
            toc: TableOfContents object

        Returns:
            Dict with sidebar navigation structure
        """
        sidebar = {
            'root': {
                'title': toc.root.title or "Home",
                'url': '/'
            },
            'sections': []
        }

        for part in toc.parts:
            section = {
                'title': part.caption,
                'weight': part.weight,
                'pages': []
            }

            for chapter in part.chapters:
                page = {
                    'title': chapter.title or chapter.slug.replace('-', ' ').title(),
                    'url': f'/{_slugify(part.caption)}/{chapter.slug}/',
                    'weight': chapter.weight,
                    'subsections': []
                }

                for sub in chapter.sections:
                    subsection = {
                        'title': sub.title or sub.slug.replace('-', ' ').title(),
                        'url': f'/{_slugify(part.caption)}/{sub.slug}/',
                        'weight': sub.weight
                    }
                    page['subsections'].append(subsection)

                section['pages'].append(page)

            sidebar['sections'].append(section)

        return sidebar


def _slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    import re
    slug = text.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    return slug.strip('-')
