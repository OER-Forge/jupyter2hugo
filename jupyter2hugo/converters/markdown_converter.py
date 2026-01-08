"""Convert MyST markdown directives to Hugo shortcodes."""

from pathlib import Path
from typing import Tuple, Dict, Any, List
import re


class MarkdownConverter:
    """Converter for MyST markdown to Hugo-compatible markdown."""

    # Supported MyST directive types
    DIRECTIVE_TYPES = {
        'note': 'admonition',
        'warning': 'admonition',
        'tip': 'admonition',
        'caution': 'admonition',
        'attention': 'admonition',
        'danger': 'admonition',
        'error': 'admonition',
        'hint': 'admonition',
        'important': 'admonition',
        'admonition': 'admonition',
        'figure': 'figure',
    }

    def convert(self, markdown_content: str) -> Tuple[str, Dict[str, Any]]:
        """
        Convert MyST markdown to Hugo-compatible markdown.

        Args:
            markdown_content: Source markdown with MyST directives

        Returns:
            Tuple of (converted_markdown, metadata)
        """
        metadata = {
            'has_math': self._has_math(markdown_content),
            'images': self._extract_images(markdown_content),
            'directives_converted': []
        }

        # Convert MyST directives to Hugo shortcodes
        markdown_content = self._convert_directives(markdown_content, metadata)

        # Convert Jupyter Book cross-references
        markdown_content = self._convert_cross_references(markdown_content)

        return markdown_content, metadata

    def _has_math(self, markdown: str) -> bool:
        """Check if markdown contains LaTeX math."""
        return bool(re.search(r'\$.*?\$', markdown))

    def _extract_images(self, markdown: str) -> List[str]:
        """Extract image references from markdown."""
        image_pattern = r'!\[.*?\]\(([^)]+)\)'
        matches = re.findall(image_pattern, markdown)

        images = []
        for match in matches:
            if not match.startswith(('http://', 'https://', 'data:')):
                images.append(match)

        return images

    def _convert_directives(self, markdown: str, metadata: Dict) -> str:
        """Convert MyST directives to Hugo shortcodes."""
        # Pattern for MyST directives:
        # :::{directive_type} [title]
        # :class: additional-class
        # :name: label
        # Content here
        # :::

        # Simpler, more robust pattern
        directive_pattern = r':::(?:\{([a-zA-Z-]+)\}|([a-zA-Z-]+))\s*([^\n]*)\n(.*?)\n:::'

        def replace_directive(match):
            directive_type = match.group(1) or match.group(2)
            title = match.group(3).strip()
            full_content = match.group(4)

            # Parse options and content
            lines = full_content.split('\n')
            options_dict = {}
            content_lines = []

            for line in lines:
                if line.strip().startswith(':') and ':' in line[1:]:
                    # This is an option line
                    parts = line.strip()[1:].split(':', 1)
                    if len(parts) == 2:
                        options_dict[parts[0].strip()] = parts[1].strip()
                else:
                    content_lines.append(line)

            content = '\n'.join(content_lines).strip()

            # Get class from options
            css_class = options_dict.get('class', '')

            # Convert to Hugo shortcode
            if directive_type in self.DIRECTIVE_TYPES:
                shortcode_type = self.DIRECTIVE_TYPES[directive_type]
                metadata['directives_converted'].append(directive_type)

                if shortcode_type == 'figure':
                    # For figure directives, title is the image path
                    image_path = title
                    caption = content.strip()

                    # Normalize image path for Hugo static files
                    if not image_path.startswith(('http://', 'https://', 'data:', '/')):
                        # Local image path - convert to Hugo static URL
                        # Remove ../ and ./ prefixes
                        clean_path = image_path.lstrip('./')
                        while clean_path.startswith('../'):
                            clean_path = clean_path[3:]
                        # If path starts with 'images/', keep it; otherwise add /images/
                        if clean_path.startswith('images/'):
                            image_path = f'/{clean_path}'
                        else:
                            image_path = f'/images/{clean_path}'

                    # Convert to Hugo figure shortcode or markdown image
                    if caption:
                        # Use Hugo figure shortcode with caption
                        params = [f'src="{image_path}"']
                        if caption:
                            # Remove broken link warnings from caption
                            caption = re.sub(r'\s*"⚠️ Broken link"', '', caption)
                            # Escape quotes in caption and clean newlines
                            escaped_caption = caption.replace('"', '&quot;').replace('\n', ' ').strip()
                            params.append(f'caption="{escaped_caption}"')
                        param_str = ' '.join(params)
                        return f'{{{{< figure {param_str} >}}}}'
                    else:
                        # Simple markdown image
                        return f'![{caption}]({image_path})'

                elif shortcode_type == 'admonition':
                    # Build shortcode parameters
                    params = [f'type="{directive_type}"']
                    if title:
                        # Escape quotes in title
                        escaped_title = title.replace('"', '\\"')
                        params.append(f'title="{escaped_title}"')
                    if css_class:
                        params.append(f'class="{css_class}"')

                    param_str = ' '.join(params)
                    return f'{{{{< admonition {param_str} >}}}}\n{content}\n{{{{< /admonition >}}}}'
            else:
                # Unknown directive - convert to HTML div for fallback
                css_classes = f"directive {directive_type}"
                if css_class:
                    css_classes += f" {css_class}"

                html = f'<div class="{css_classes}">'
                if title:
                    html += f'<p class="admonition-title">{title}</p>'
                html += f'\n{content}\n</div>'
                return html

        # Apply the conversion
        markdown = re.sub(directive_pattern, replace_directive, markdown, flags=re.DOTALL | re.MULTILINE)

        # Also handle simpler format: ```{directive_type} title
        simple_directive_pattern = r'```\{([a-zA-Z-]+)\}\s*([^\n]*)\n((?:(?!```).)*)\n```'

        def replace_simple_directive(match):
            directive_type = match.group(1)
            title = match.group(2).strip()
            content = match.group(3).strip()

            if directive_type in self.DIRECTIVE_TYPES:
                metadata['directives_converted'].append(directive_type)
                params = [f'type="{directive_type}"']
                if title:
                    params.append(f'title="{title}"')

                param_str = ' '.join(params)
                return f'{{{{< admonition {param_str} >}}}}\n{content}\n{{{{< /admonition >}}}}'

            # Fallback - treat as code block
            return match.group(0)

        markdown = re.sub(simple_directive_pattern, replace_simple_directive, markdown, flags=re.DOTALL)

        # Handle MyST image directive: ```{image} path
        image_directive_pattern = r'```\{image\}\s*([^\n]+)\n((?:---\n)?(?:.*?\n)?(?:---\n)?)```'

        def replace_image_directive(match):
            image_path = match.group(1).strip()
            options = match.group(2).strip()

            # Parse options
            alt_text = ""
            width = ""
            if options:
                for line in options.split('\n'):
                    if line.startswith('alt:'):
                        alt_text = line.split(':', 1)[1].strip()
                    elif line.startswith('width:'):
                        width = line.split(':', 1)[1].strip()

            # Convert to markdown image or Hugo figure shortcode
            if width or alt_text:
                # Use Hugo figure shortcode for better control
                params = [f'src="{image_path}"']
                if alt_text:
                    params.append(f'alt="{alt_text}"')
                if width:
                    params.append(f'width="{width}"')
                param_str = ' '.join(params)
                return f'{{{{< figure {param_str} >}}}}'
            else:
                # Simple markdown image
                return f'![{alt_text}]({image_path})'

        markdown = re.sub(image_directive_pattern, replace_image_directive, markdown, flags=re.DOTALL)

        return markdown

    def _convert_cross_references(self, markdown: str) -> str:
        """Convert Jupyter Book cross-references to Hugo."""
        # Convert {doc}`path/to/file` to Hugo relref
        markdown = re.sub(
            r'\{doc\}`([^`]+)`',
            lambda m: f'[{{{{< relref "{m.group(1)}" >}}}}]({{{{< relref "{m.group(1)}" >}}}})',
            markdown
        )

        # Convert {ref}`label` to Hugo ref
        markdown = re.sub(
            r'\{ref\}`([^`]+)`',
            lambda m: f'[{{{{< ref "{m.group(1)}" >}}}}]({{{{< ref "{m.group(1)}" >}}}})',
            markdown
        )

        return markdown


def convert_markdown(markdown_path: Path) -> Tuple[str, Dict[str, Any]]:
    """
    Convenience function to convert a markdown file.

    Args:
        markdown_path: Path to .md file

    Returns:
        Tuple of (converted_markdown, metadata)
    """
    with open(markdown_path, 'r', encoding='utf-8') as f:
        content = f.read()

    converter = MarkdownConverter()
    return converter.convert(content)


def convert_markdown_string(markdown_content: str) -> Tuple[str, Dict[str, Any]]:
    """
    Convert a markdown string.

    Args:
        markdown_content: Markdown content with MyST directives

    Returns:
        Tuple of (converted_markdown, metadata)
    """
    converter = MarkdownConverter()
    return converter.convert(markdown_content)
