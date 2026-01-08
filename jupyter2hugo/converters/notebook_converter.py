"""Convert Jupyter notebooks to Hugo-compatible markdown."""

from pathlib import Path
from typing import Tuple, List, Dict, Any
import re
from nbconvert import MarkdownExporter
from nbconvert.preprocessors import Preprocessor
from traitlets import Unicode
import nbformat


class HugoPreprocessor(Preprocessor):
    """Preprocessor to handle Hugo-specific conversions."""

    def preprocess(self, nb, resources):
        """Preprocess the notebook."""
        resources['youtube_embeds'] = []
        return super().preprocess(nb, resources)

    def preprocess_cell(self, cell, resources, index):
        """Preprocess a single cell."""
        if cell.cell_type == 'markdown':
            # Extract YouTube embeds and convert to shortcodes
            cell.source = self._convert_youtube_embeds(cell.source, resources)

            # Handle Jupyter Book specific syntax
            cell.source = self._convert_jb_syntax(cell.source)

        return cell, resources

    def _convert_youtube_embeds(self, source: str, resources: Dict) -> str:
        """Convert YouTube iframes and markdown links to Hugo shortcodes."""
        # Pattern 1: iframe embeds
        iframe_pattern = r'<iframe[^>]*src=["\']https?://(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]+)["\'][^>]*>.*?</iframe>'
        def replace_iframe(match):
            video_id = match.group(1)
            resources['youtube_embeds'].append(video_id)
            return f'{{{{< youtube {video_id} >}}}}'

        source = re.sub(iframe_pattern, replace_iframe, source, flags=re.DOTALL | re.IGNORECASE)

        # Pattern 2: YouTube links that should be embedded
        # [![...](https://img.youtube.com/vi/VIDEO_ID/...)](https://www.youtube.com/watch?v=VIDEO_ID)
        youtube_link_pattern = r'\[!\[([^\]]*)\]\(https?://img\.youtube\.com/vi/([a-zA-Z0-9_-]+)[^\)]*\)\]\(https?://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)\)'
        def replace_youtube_link(match):
            video_id = match.group(2)  # From thumbnail URL
            resources['youtube_embeds'].append(video_id)
            return f'{{{{< youtube {video_id} >}}}}'

        source = re.sub(youtube_link_pattern, replace_youtube_link, source)

        return source

    def _convert_jb_syntax(self, source: str) -> str:
        """Convert Jupyter Book specific syntax."""
        # Convert {doc}`path/to/file` to Hugo relref
        source = re.sub(
            r'\{doc\}`([^`]+)`',
            r'[{{\< relref "\1" >\}}]({{< relref "\1" >}})',
            source
        )

        # Convert {ref}`label` to Hugo ref
        source = re.sub(
            r'\{ref\}`([^`]+)`',
            r'[{{\< ref "\1" >\}}]({{< ref "\1" >}})',
            source
        )

        return source


class NotebookConverter:
    """Converter for Jupyter notebooks to Hugo markdown."""

    def __init__(self):
        """Initialize the converter."""
        self.exporter = MarkdownExporter()
        self.exporter.register_preprocessor(HugoPreprocessor, enabled=True)

    def convert(self, notebook_path: Path) -> Tuple[str, Dict[str, Any]]:
        """
        Convert a Jupyter notebook to markdown.

        Args:
            notebook_path: Path to the .ipynb file

        Returns:
            Tuple of (markdown_content, metadata_dict)
        """
        # Read the notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)

        # Convert to markdown
        (body, resources) = self.exporter.from_notebook_node(nb)

        # Extract metadata
        metadata = {
            'title': self._extract_title(nb, body),
            'youtube_embeds': resources.get('youtube_embeds', []),
            'has_code': self._has_code_cells(nb),
            'has_math': self._has_math(body),
            'images': self._extract_images(body),
        }

        # Post-process markdown
        body = self._post_process_markdown(body)

        # Apply MyST directive conversion
        from .markdown_converter import MarkdownConverter
        converter = MarkdownConverter()
        body_converted, myst_metadata = converter.convert(body)

        # Merge metadata
        if myst_metadata.get('directives_converted'):
            metadata['directives_converted'] = myst_metadata['directives_converted']

        return body_converted, metadata

    def _extract_title(self, nb: nbformat.NotebookNode, markdown: str) -> str:
        """Extract title from notebook."""
        # Try to get from notebook metadata
        if 'title' in nb.metadata:
            return nb.metadata['title']

        # Try to extract from first heading in markdown
        heading_match = re.search(r'^#\s+(.+)$', markdown, re.MULTILINE)
        if heading_match:
            return heading_match.group(1).strip()

        return ""

    def _has_code_cells(self, nb: nbformat.NotebookNode) -> bool:
        """Check if notebook has code cells."""
        return any(cell.cell_type == 'code' for cell in nb.cells)

    def _has_math(self, markdown: str) -> bool:
        """Check if markdown contains LaTeX math."""
        # Check for $...$ or $$...$$ patterns
        return bool(re.search(r'\$.*?\$', markdown))

    def _extract_images(self, markdown: str) -> List[str]:
        """Extract image references from markdown."""
        # Match ![alt](path) pattern
        image_pattern = r'!\[.*?\]\(([^)]+)\)'
        matches = re.findall(image_pattern, markdown)

        # Filter out external URLs, keep local paths
        images = []
        for match in matches:
            if not match.startswith(('http://', 'https://', 'data:')):
                images.append(match)

        return images

    def _post_process_markdown(self, markdown: str) -> str:
        """Post-process markdown for Hugo compatibility."""
        # Remove notebook-specific formatting that doesn't work well in Hugo
        # This is a placeholder for any additional processing needed

        return markdown


def convert_notebook(notebook_path: Path) -> Tuple[str, Dict[str, Any]]:
    """
    Convenience function to convert a notebook.

    Args:
        notebook_path: Path to .ipynb file

    Returns:
        Tuple of (markdown_content, metadata)
    """
    converter = NotebookConverter()
    return converter.convert(notebook_path)
