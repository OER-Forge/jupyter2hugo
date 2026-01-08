# jupyter2hugo

Convert Jupyter Book projects to Hugo static sites with proper navigation, internal links, and WCAG 2.1 compliance.

## Features

- **Complete conversion** from Jupyter Book (`_toc.yml`) to Hugo static sites
- **Theme-agnostic output** - works with any Hugo theme
- **Navigation preservation** - parts, chapters, and sections from TOC
- **Internal link rewriting** - converts relative paths to Hugo URLs
- **Math support** - KaTeX rendering for LaTeX equations
- **YouTube embeds** - converts to Hugo shortcodes
- **Image handling** - preserves directory structure
- **Code cells** - preserves outputs and syntax highlighting
- **MyST directives** - converts to Hugo shortcodes (admonitions, notes, warnings)
- **Accessibility** - optional WCAG 2.1 compliance checking

## Installation

```bash
cd jupyter2hugo
pip install -e .
```

## Usage

Basic conversion:

```bash
jupyter2hugo /path/to/jupyterbook/project /path/to/output
```

With accessibility checking (requires Node.js and pa11y):

```bash
jupyter2hugo /path/to/jupyterbook/project /path/to/output --check-accessibility
```

## Output Structure

The tool creates a `hugo-site/` directory in the output path with:

```
hugo-site/
├── config.toml              # Hugo configuration with KaTeX
├── content/                 # Converted pages
├── static/images/           # Images from source
└── layouts/shortcodes/      # Hugo shortcodes for directives
```

## Building the Hugo Site

After conversion, build and serve the Hugo site:

```bash
cd /path/to/output/hugo-site
hugo server
```

Visit http://localhost:1313 to view the site.

## Requirements

- Python 3.8+
- Hugo (for building the site)
- Node.js and npm (optional, for accessibility checking)

## License

MIT License
