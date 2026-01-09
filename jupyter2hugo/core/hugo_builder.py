"""Main orchestrator for converting Jupyter Book to Hugo."""

from pathlib import Path
from typing import Optional
import shutil

from ..core.toc_parser import load_toc
from ..core.config_parser import load_config
from ..converters.notebook_converter import convert_notebook
from ..converters.markdown_converter import convert_markdown
from ..converters.link_rewriter import LinkRewriter, build_file_mapping
from ..converters.image_processor import ImageProcessor
from ..hugo.frontmatter import FrontMatterBuilder, add_frontmatter, extract_title_from_markdown, remove_first_heading
from ..hugo.menu_builder import MenuBuilder
from ..hugo.shortcodes import generate_shortcodes
from ..hugo.templates import generate_templates


class HugoBuilder:
    """Build a Hugo site from a Jupyter Book project."""

    def __init__(self, source_dir: Path, output_dir: Path, verbose: bool = False):
        """
        Initialize the Hugo builder.

        Args:
            source_dir: Jupyter Book source directory
            output_dir: Output directory for Hugo site
            verbose: Enable verbose logging
        """
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.verbose = verbose

        # Paths
        self.toc_path = source_dir / "_toc.yml"
        self.config_path = source_dir / "_config.yml"

        # Hugo directories
        self.content_dir = self.output_dir / "content"
        self.static_dir = self.output_dir / "static"
        self.layouts_dir = self.output_dir / "layouts"

        # Loaded data
        self.toc = None
        self.config = None
        self.file_mapping = None
        self.link_rewriter = None
        self.image_processor = None

    def build(self):
        """Execute the full build process."""
        self.log("Starting Jupyter Book to Hugo conversion...")

        # Step 1: Parse configuration
        self.log("Step 1: Parsing configuration files...")
        self._parse_config()

        # Step 2: Initialize Hugo structure
        self.log("Step 2: Initializing Hugo directory structure...")
        self._init_hugo_structure()

        # Step 3: Generate Hugo config
        self.log("Step 3: Generating Hugo configuration...")
        self._generate_hugo_config()

        # Step 4: Generate shortcodes and KaTeX support
        self.log("Step 4: Generating Hugo shortcodes and KaTeX support...")
        generate_shortcodes(self.layouts_dir)
        generate_templates(self.layouts_dir)

        # Step 5: Build file mapping for link rewriting
        self.log("Step 5: Building file mapping...")
        self._build_file_mapping()

        # Step 6: Convert content files
        self.log("Step 6: Converting content files...")
        self._convert_content()

        # Step 7: Copy images
        self.log("Step 7: Processing images...")
        self._copy_images()

        # Step 8: Copy logo if present
        if self.config and self.config.logo:
            self.log("Step 8: Copying logo...")
            self._copy_logo()

        self.log(f"\nConversion complete! Hugo site created at: {self.output_dir}")
        self.log("\nTo build and serve the site:")
        self.log(f"  cd {self.output_dir}")
        self.log("  hugo server")

    def _parse_config(self):
        """Parse TOC and config files."""
        if not self.toc_path.exists():
            raise FileNotFoundError(f"TOC file not found: {self.toc_path}")

        self.toc = load_toc(self.toc_path)
        self.log(f"  Loaded TOC with {len(self.toc.parts)} parts")

        if self.config_path.exists():
            self.config = load_config(self.config_path)
            self.log(f"  Loaded config: {self.config.title}")
        else:
            self.log("  No _config.yml found, using defaults")

    def _init_hugo_structure(self):
        """Create Hugo directory structure and initialize modules."""
        # Create main directories
        self.content_dir.mkdir(parents=True, exist_ok=True)
        self.static_dir.mkdir(parents=True, exist_ok=True)
        self.layouts_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (self.static_dir / "images").mkdir(parents=True, exist_ok=True)
        (self.static_dir / "css").mkdir(parents=True, exist_ok=True)
        (self.layouts_dir / "shortcodes").mkdir(parents=True, exist_ok=True)

        # Initialize Hugo modules
        import subprocess
        try:
            subprocess.run(
                ["hugo", "mod", "init", "example.com/site"],
                cwd=self.output_dir,
                capture_output=True,
                check=True
            )
            self.log("  Initialized Hugo modules")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log("  Warning: Could not initialize Hugo modules (hugo command not found)")

        self.log("  Created Hugo directory structure")

    def _generate_hugo_config(self):
        """Generate Hugo config.toml."""
        title = self.config.title if self.config else "Documentation"
        author = self.config.get_author_string() if self.config else ""
        baseurl = self.config.baseurl if self.config else ""
        language = self.config.language if self.config else "en"

        config_content = f'''baseURL = "{baseurl}"
languageCode = "{language}"
title = "{title}"

# Hugo theme configuration
# Default: PaperMod (modern, accessible theme with ToC and WCAG support)
# To change theme, replace with any Hugo theme module path
[module]
  [[module.imports]]
    path = "github.com/adityatelange/hugo-PaperMod"

[markup]
  [markup.goldmark]
    [markup.goldmark.renderer]
      unsafe = true
  [markup.highlight]
    style = "monokai"
    lineNos = false

[params]
  author = "{author}"
  description = "{self.config.description if self.config and self.config.description else title}"
  math = true

  # PaperMod theme configuration
  ShowToc = true
  TocOpen = false
  ShowBreadCrumbs = true
  ShowPostNavLinks = true

# KaTeX configuration for math rendering
[params.katex]
  enable = true

'''

        # Add menu configuration
        menu_config = MenuBuilder.build_menu_config(self.toc)
        config_content += "\n" + menu_config

        # Write config file
        (self.output_dir / "config.toml").write_text(config_content, encoding='utf-8')
        self.log("  Generated config.toml")

    def _build_file_mapping(self):
        """Build mapping from source files to Hugo URLs."""
        self.file_mapping = build_file_mapping(self.toc, self.source_dir, self.content_dir)
        self.link_rewriter = LinkRewriter(self.file_mapping, self.source_dir, self.content_dir)
        self.image_processor = ImageProcessor(self.source_dir, self.static_dir)
        self.log(f"  Mapped {len(self.file_mapping)} files")

    def _convert_content(self):
        """Convert all content files."""
        # Convert root file
        if self.toc.root and self.toc.root.file:
            self._convert_root_file()

        # Convert each part's chapters and sections
        for part in self.toc.parts:
            self._convert_part(part)

    def _convert_root_file(self):
        """Convert the root index file."""
        root_entry = self.toc.root
        source_file = self._resolve_source_file(root_entry.file)

        if not source_file:
            self.log(f"  Warning: Root file not found: {root_entry.file}")
            return

        self.log(f"  Converting root: {source_file.name}")

        # Convert file
        markdown, metadata = self._convert_file(source_file)

        # Extract title
        title = extract_title_from_markdown(markdown) or self.config.title if self.config else "Home"
        markdown = remove_first_heading(markdown)

        # Generate front matter
        fm = FrontMatterBuilder.from_metadata(
            title=title,
            weight=0,
            metadata=metadata
        )

        # Process images and links
        markdown, _ = self.image_processor.process_images(markdown, source_file)
        markdown, broken_links = self.link_rewriter.rewrite_links(markdown, source_file)

        if broken_links:
            self.log(f"    Warning: {len(broken_links)} broken links")

        # Write to Hugo content
        output_file = self.content_dir / "_index.md"
        output_file.write_text(add_frontmatter(markdown, fm), encoding='utf-8')

    def _convert_part(self, part):
        """Convert all chapters and sections in a part."""
        # Create section directory
        section_slug = self._slugify(part.caption)
        section_dir = self.content_dir / section_slug
        section_dir.mkdir(parents=True, exist_ok=True)

        # Create section index
        self._create_section_index(part, section_dir)

        # Convert chapters
        for chapter in part.chapters:
            self._convert_chapter(chapter, part, section_dir)

    def _create_section_index(self, part, section_dir: Path):
        """Create _index.md for a section."""
        fm = FrontMatterBuilder.for_section_index(part.caption, part.weight)
        content = f"This section contains course materials for {part.caption}.\n"
        (section_dir / "_index.md").write_text(add_frontmatter(content, fm), encoding='utf-8')

    def _convert_chapter(self, chapter, part, section_dir: Path):
        """Convert a chapter file."""
        source_file = self._resolve_source_file(chapter.file)

        if not source_file:
            self.log(f"  Warning: File not found: {chapter.file}")
            return

        self.log(f"  Converting: {source_file.name}")

        # Convert file
        markdown, metadata = self._convert_file(source_file)

        # Extract title
        title = chapter.title or extract_title_from_markdown(markdown) or chapter.slug.replace('-', ' ').title()
        if extract_title_from_markdown(markdown):
            markdown = remove_first_heading(markdown)

        # Generate front matter (no menu parent for individual pages)
        fm = FrontMatterBuilder.from_metadata(
            title=title,
            weight=chapter.weight,
            metadata=metadata,
            part_caption=None  # Don't add pages to menu
        )

        # Process images and links
        markdown, _ = self.image_processor.process_images(markdown, source_file)
        markdown, broken_links = self.link_rewriter.rewrite_links(markdown, source_file)

        # Clean up broken link warnings from shortcodes
        markdown = self._clean_shortcode_warnings(markdown)

        if broken_links and self.verbose:
            self.log(f"    Warning: {len(broken_links)} broken links")

        # Write to Hugo content
        output_file = section_dir / f"{chapter.slug}.md"
        output_file.write_text(add_frontmatter(markdown, fm), encoding='utf-8')

        # Convert sections
        for section in chapter.sections:
            self._convert_section(section, part, section_dir)

    def _convert_section(self, section, part, section_dir: Path):
        """Convert a section file."""
        source_file = self._resolve_source_file(section.file)

        if not source_file:
            self.log(f"  Warning: File not found: {section.file}")
            return

        self.log(f"    Converting section: {source_file.name}")

        # Convert file
        markdown, metadata = self._convert_file(source_file)

        # Extract title
        title = section.title or extract_title_from_markdown(markdown) or section.slug.replace('-', ' ').title()
        if extract_title_from_markdown(markdown):
            markdown = remove_first_heading(markdown)

        # Generate front matter (no menu parent for individual pages)
        fm = FrontMatterBuilder.from_metadata(
            title=title,
            weight=section.weight,
            metadata=metadata,
            part_caption=None  # Don't add pages to menu
        )

        # Process images and links
        markdown, _ = self.image_processor.process_images(markdown, source_file)
        markdown, broken_links = self.link_rewriter.rewrite_links(markdown, source_file)

        # Clean up broken link warnings from shortcodes
        markdown = self._clean_shortcode_warnings(markdown)

        if broken_links and self.verbose:
            self.log(f"      Warning: {len(broken_links)} broken links")

        # Write to Hugo content
        output_file = section_dir / f"{section.slug}.md"
        output_file.write_text(add_frontmatter(markdown, fm), encoding='utf-8')

    def _convert_file(self, file_path: Path):
        """Convert a notebook or markdown file."""
        if file_path.suffix == '.ipynb':
            return convert_notebook(file_path)
        elif file_path.suffix == '.md':
            return convert_markdown(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")

    def _resolve_source_file(self, file_ref: str) -> Optional[Path]:
        """Resolve a file reference to an actual file path."""
        if not file_ref:
            return None

        # Try with different extensions
        for ext in ['', '.md', '.ipynb']:
            candidate = self.source_dir / f"{file_ref}{ext}"
            if candidate.exists():
                return candidate

        return None

    def _copy_images(self):
        """Copy images directory if it exists."""
        images_dir = self.source_dir / "images"
        if images_dir.exists():
            count = self.image_processor.copy_directory(images_dir)
            self.log(f"  Copied {count} images")

    def _copy_logo(self):
        """Copy logo file."""
        from ..core.config_parser import ConfigParser
        parser = ConfigParser(self.config_path)
        logo_path = parser.resolve_logo_path(self.config)

        if logo_path and logo_path.exists():
            dest = self.static_dir / "images" / logo_path.name
            shutil.copy2(logo_path, dest)
            self.log(f"  Copied logo: {logo_path.name}")

    def _clean_shortcode_warnings(self, markdown: str) -> str:
        """Remove broken link warnings from Hugo shortcode parameters."""
        import re
        # Remove "⚠️ Broken link" from shortcode parameters
        markdown = re.sub(r'\s*"⚠️ Broken link"', '', markdown)
        # Also remove from any other warning markers
        markdown = re.sub(r'\s*⚠️[^"]*', '', markdown)
        return markdown

    def _slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug."""
        import re
        slug = text.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[\s_]+', '-', slug)
        return slug.strip('-')

    def log(self, message: str):
        """Log a message if verbose mode is enabled."""
        if self.verbose or True:  # Always log for now
            print(message)
