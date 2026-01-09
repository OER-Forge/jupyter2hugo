"""Generate KaTeX partials only - no page templates."""

from pathlib import Path


def generate_templates(layouts_dir: Path):
    """
    Generate only KaTeX partial templates for math rendering.

    Does NOT generate page templates (baseof, single, list, etc.) so that
    Hugo themes work properly. The generated config.toml includes a default theme.

    Args:
        layouts_dir: Hugo layouts directory
    """
    partials_dir = layouts_dir / "partials"
    partials_dir.mkdir(parents=True, exist_ok=True)

    # KaTeX partial for math rendering
    katex = '''{{ if .Site.Params.math }}
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css" crossorigin="anonymous">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js" crossorigin="anonymous"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js" crossorigin="anonymous"
    onload="renderMathInElement(document.body, {delimiters: [{left: '$$', right: '$$', display: true}, {left: '$', right: '$', display: false}, {left: '\\\\(', right: '\\\\)', display: false}, {left: '\\\\[', right: '\\\\]', display: true}], throwOnError: false});"></script>
{{ end }}
'''

    # Write KaTeX partial
    (partials_dir / "katex.html").write_text(katex, encoding='utf-8')

    # Theme-specific injection points for KaTeX
    # hugo-book theme
    book_inject = partials_dir / "docs" / "inject"
    book_inject.mkdir(parents=True, exist_ok=True)
    (book_inject / "head.html").write_text(katex, encoding='utf-8')

    # PaperMod theme (uses extend_head.html with underscore)
    (partials_dir / "extend_head.html").write_text(katex, encoding='utf-8')

    # Generic theme injection points
    (partials_dir / "extend-head.html").write_text(katex, encoding='utf-8')
    (partials_dir / "head-custom.html").write_text(katex, encoding='utf-8')
