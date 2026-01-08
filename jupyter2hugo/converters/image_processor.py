"""Process and copy images for Hugo static site."""

from pathlib import Path
from typing import Dict, List, Tuple
import shutil
import re


class ImageProcessor:
    """Handle image copying and path rewriting for Hugo."""

    def __init__(self, source_dir: Path, static_dir: Path, maintain_structure: bool = True):
        """
        Initialize the image processor.

        Args:
            source_dir: Root directory of Jupyter Book source
            static_dir: Hugo static directory for images
            maintain_structure: Whether to maintain directory structure
        """
        self.source_dir = source_dir
        self.static_dir = static_dir / "images"
        self.maintain_structure = maintain_structure
        self.copied_images = {}  # Map source path -> static path

    def process_images(self, markdown: str, current_file: Path) -> Tuple[str, List[str]]:
        """
        Process images in markdown content.

        Args:
            markdown: Markdown content with image references
            current_file: Path to the current source file

        Returns:
            Tuple of (updated_markdown, list_of_copied_images)
        """
        copied = []

        # Pattern for markdown images: ![alt](path)
        image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'

        def replace_image(match):
            alt_text = match.group(1)
            image_path = match.group(2)

            # Skip external URLs and data URIs
            if image_path.startswith(('http://', 'https://', 'data:', '/')):
                if not image_path.startswith('/images/'):
                    return match.group(0)

            # Resolve image path relative to current file
            if current_file.is_file():
                current_dir = current_file.parent
            else:
                current_dir = current_file

            resolved_path = (current_dir / image_path).resolve()

            # Copy image and get new path
            try:
                new_path = self._copy_image(resolved_path)
                copied.append(str(resolved_path))

                # Convert to Hugo static URL
                # Don't add /images/ prefix if path already starts with images/
                if new_path.startswith('images/'):
                    hugo_url = f"/{new_path}"
                else:
                    hugo_url = f"/images/{new_path}"
                return f'![{alt_text}]({hugo_url})'
            except Exception as e:
                # Keep original if copy fails
                print(f"Warning: Failed to copy image {image_path}: {e}")
                return match.group(0)

        markdown = re.sub(image_pattern, replace_image, markdown)

        # Also handle HTML <img> tags
        html_img_pattern = r'<img\s+([^>]*src=")([^"]+)("[^>]*)>'

        def replace_html_image(match):
            prefix = match.group(1)
            image_path = match.group(2)
            suffix = match.group(3)

            # Skip external URLs
            if image_path.startswith(('http://', 'https://', 'data:', '/')):
                if not image_path.startswith('/images/'):
                    return match.group(0)

            # Resolve and copy
            if current_file.is_file():
                current_dir = current_file.parent
            else:
                current_dir = current_file

            resolved_path = (current_dir / image_path).resolve()

            try:
                new_path = self._copy_image(resolved_path)
                copied.append(str(resolved_path))

                # Don't add /images/ prefix if path already starts with images/
                if new_path.startswith('images/'):
                    hugo_url = f"/{new_path}"
                else:
                    hugo_url = f"/images/{new_path}"
                return f'<img {prefix}{hugo_url}{suffix}>'
            except Exception as e:
                print(f"Warning: Failed to copy image {image_path}: {e}")
                return match.group(0)

        markdown = re.sub(html_img_pattern, replace_html_image, markdown)

        return markdown, copied

    def _copy_image(self, source_path: Path) -> str:
        """
        Copy an image to the static directory.

        Args:
            source_path: Source image path

        Returns:
            Relative path in static/images directory
        """
        # Check if already copied
        source_str = str(source_path)
        if source_str in self.copied_images:
            return self.copied_images[source_str]

        if not source_path.exists():
            raise FileNotFoundError(f"Image not found: {source_path}")

        if self.maintain_structure:
            # Maintain directory structure relative to source
            try:
                rel_path = source_path.relative_to(self.source_dir)
            except ValueError:
                # Image is outside source directory, use filename only
                rel_path = Path(source_path.name)

            dest_path = self.static_dir / rel_path
        else:
            # Flatten to images directory
            dest_path = self.static_dir / source_path.name

        # Handle name conflicts
        if dest_path.exists() and dest_path.stat().st_size != source_path.stat().st_size:
            # Add parent directory name to avoid conflicts
            stem = source_path.stem
            suffix = source_path.suffix
            parent_name = source_path.parent.name
            dest_path = self.static_dir / f"{parent_name}_{stem}{suffix}"

        # Create parent directories
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy image
        shutil.copy2(source_path, dest_path)

        # Store relative path for reuse
        relative_dest = dest_path.relative_to(self.static_dir)
        self.copied_images[source_str] = str(relative_dest)

        return str(relative_dest)

    def copy_directory(self, images_dir: Path) -> int:
        """
        Copy an entire images directory.

        Args:
            images_dir: Source images directory

        Returns:
            Number of images copied
        """
        if not images_dir.exists():
            return 0

        # Temporarily change source_dir to images_dir to avoid path duplication
        original_source_dir = self.source_dir
        self.source_dir = images_dir

        count = 0
        for image_file in images_dir.rglob('*'):
            if image_file.is_file() and self._is_image(image_file):
                try:
                    self._copy_image(image_file)
                    count += 1
                except Exception as e:
                    print(f"Warning: Failed to copy {image_file}: {e}")

        # Restore original source_dir
        self.source_dir = original_source_dir

        return count

    def _is_image(self, file_path: Path) -> bool:
        """Check if a file is an image based on extension."""
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp', '.ico'}
        return file_path.suffix.lower() in image_extensions


def process_images_in_markdown(
    markdown: str,
    current_file: Path,
    source_dir: Path,
    static_dir: Path
) -> Tuple[str, List[str]]:
    """
    Convenience function to process images in markdown.

    Args:
        markdown: Markdown content
        current_file: Current file path
        source_dir: Source directory
        static_dir: Hugo static directory

    Returns:
        Tuple of (updated_markdown, list_of_copied_images)
    """
    processor = ImageProcessor(source_dir, static_dir)
    return processor.process_images(markdown, current_file)
