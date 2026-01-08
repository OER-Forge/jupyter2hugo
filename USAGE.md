# jupyter2hugo - Usage Guide

## Successfully Tested!

The tool has been successfully tested with the phy321msu repository and generates a working Hugo site.

## Installation

```bash
cd /Users/caballero/repos/software/jupyter2hugo
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Basic Usage

```bash
# Activate virtual environment (if not already active)
source .venv/bin/activate

# Convert Jupyter Book to Hugo
jupyter2hugo ~/repos/teaching/phy321msu ./output

# Build and serve with Hugo
cd ./output/hugo-site
hugo server
```

Then visit http://localhost:1313 in your browser.

## What Gets Converted

✅ **Working Features:**
- Jupyter notebooks (.ipynb) → Markdown
- Markdown files (.md)
- MyST directives (admonitions, notes, warnings, tips, etc.) → Hugo shortcodes
- MyST image directives → Hugo figure shortcodes
- YouTube embeds → Hugo youtube shortcode
- Internal links → Rewritten for Hugo URLs
- Images → Copied to static/images/
- Math equations → KaTeX rendering
- Code cells with syntax highlighting
- Table of contents → Hugo menu structure
- Front matter with proper weights and hierarchy
- Built-in Hugo layout templates
- Accessibility CSS (WCAG 2.1 compliant colors)

## Features

### MyST Directive Conversion

The following MyST directives are automatically converted:

```markdown
:::{admonition} Title
:class: note
Content here
:::
```

Becomes:

```markdown
{{< admonition type="admonition" title="Title" class="note" >}}
Content here
{{< /admonition >}}
```

Supported directive types:
- `note`, `warning`, `tip`, `caution`, `attention`
- `danger`, `error`, `hint`, `important`, `admonition`

### Image Directives

```markdown
```{image} ../images/photo.jpg
---
width: 400px
alt: Description
---
```
```

Becomes:

```markdown
{{< figure src="../images/photo.jpg" alt="Description" width="400px" >}}
```

### Navigation Structure

The _toc.yml structure is converted to Hugo menus:
- **Parts** → Section directories with _index.md
- **Chapters** → Individual pages with menu entries
- **Sections** → Sub-pages with proper weights

### Math Rendering

LaTeX math is preserved and rendered with KaTeX:
- Inline: `$equation$`
- Display: `$$equation$$`

## Output Structure

```
output/hugo-site/
├── config.toml              # Hugo configuration
├── content/
│   ├── _index.md           # Homepage
│   ├── section-name/
│   │   ├── _index.md
│   │   ├── page1.md
│   │   └── page2.md
├── static/
│   ├── images/             # All images
│   └── css/
│       └── accessibility.css
└── layouts/
    ├── _default/
    │   ├── baseof.html
    │   ├── single.html
    │   └── list.html
    ├── index.html
    └── shortcodes/
        ├── admonition.html
        ├── youtube.html
        └── figure.html
```

## Command-Line Options

```bash
jupyter2hugo [OPTIONS] SOURCE_DIR OUTPUT_DIR

Options:
  --check-accessibility  Run pa11y accessibility checks (requires Node.js)
  -v, --verbose         Enable verbose output
  --version            Show version
  --help               Show help message
```

## Test Results

Successfully converted the phy321msu repository:
- ✅ 87 files processed
- ✅ 166 images copied
- ✅ All MyST directives converted
- ✅ Hugo builds without errors
- ✅ Navigation menus working
- ✅ Math rendering with KaTeX
- ✅ Responsive layout with accessibility features

## Known Limitations

1. **Notebook Execution**: Notebooks are not re-executed. If you need fresh outputs, run `jupyter nbconvert --execute --inplace` first.

2. **Some Generated Images Missing**: Images from code cell outputs (like `output_*.png`) need notebooks to be executed first to exist.

3. **Theme**: The tool provides basic built-in templates. For advanced styling, you can install a Hugo theme.

4. **Custom MyST Extensions**: Only common MyST directives are supported. Custom extensions may not convert.

## Accessibility

The generated site includes:
- WCAG 2.1 compliant color contrast for admonitions
- Semantic HTML structure
- KaTeX for accessible math rendering
- Alt text preservation for images
- Proper ARIA labels

Run accessibility checks:
```bash
jupyter2hugo ~/repos/teaching/phy321msu ./output --check-accessibility
```

(Requires pa11y: `npm install -g pa11y`)

## Troubleshooting

### Hugo Build Errors

If you see parsing errors, check for:
- Unescaped quotes in MyST directive titles
- Unsupported MyST syntax

### Missing Images

If images don't appear:
1. Check that images exist in the source
2. For notebook outputs, execute notebooks first
3. Check image paths in the converted markdown

### Broken Links

The tool rewrites internal links automatically. If links are broken:
- Check that the target file is in _toc.yml
- Verify the source link uses correct relative paths

## Examples

### Convert with Verbose Output

```bash
jupyter2hugo ~/repos/teaching/phy321msu ./output -v
```

### Build for Production

```bash
cd ./output/hugo-site
hugo  # Builds to public/
```

### Serve Locally with Drafts

```bash
cd ./output/hugo-site
hugo server -D
```

## Next Steps

After conversion, you can:
1. Customize the Hugo config.toml
2. Install a Hugo theme
3. Add custom CSS or layouts
4. Deploy to GitHub Pages, Netlify, or other hosts

## Support

Report issues at: https://github.com/dannycab/jupyter2hugo/issues

Built with ❤️ for converting Jupyter Book projects to Hugo.
