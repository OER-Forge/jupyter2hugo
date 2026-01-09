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

The tool creates a Hugo site in the output path with:

```
output/
├── config.toml              # Hugo configuration with KaTeX
├── content/                 # Converted pages
├── static/images/           # Images from source
└── layouts/
    ├── shortcodes/          # Hugo shortcodes for MyST directives
    └── partials/            # KaTeX partials for math rendering
```

## Building the Hugo Site

The converted site includes a **default theme** (PaperMod - modern and accessible with ToC) and is ready to use:

```bash
cd /path/to/output

# Download theme
hugo mod tidy

# Build and serve
hugo server
```

Visit http://localhost:1313 to view your site.

### Changing the Theme

The site works with **any Hugo theme**. To change the default theme, edit `config.toml`:

```toml
[module]
  [[module.imports]]
    path = "github.com/THEME-AUTHOR/THEME-NAME"
```

**Popular theme options:**

- **Documentation sites:**
  - `github.com/adityatelange/hugo-PaperMod` - Modern, accessible with ToC (default)
  - `github.com/alex-shpak/hugo-book` - Clean documentation theme
  - `github.com/google/docsy` - Google's documentation theme
  - `github.com/McShelby/hugo-theme-relearn` - Feature-rich documentation

- **Academic/Research:**
  - `github.com/wowchemy/wowchemy-hugo-themes` - Academic theme with publications support

- **Blog/General:**
  - `github.com/theNewDynamic/gohugo-theme-ananke` - Simple, clean

- **Browse more:** [themes.gohugo.io](https://themes.gohugo.io/)

After changing the theme:

```bash
hugo mod tidy    # Download new theme
hugo server      # Rebuild and serve
```

## Requirements

- Python 3.8+
- Hugo (for building the site)
- Node.js and npm (optional, for accessibility checking)

## License

MIT License
