"""Generate basic Hugo layout templates."""

from pathlib import Path


class TemplateGenerator:
    """Generate minimal Hugo layout templates."""

    @staticmethod
    def generate_baseof() -> str:
        """Generate base template (baseof.html)."""
        return '''<!DOCTYPE html>
<html lang="{{ .Site.LanguageCode }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ block "title" . }}{{ .Title }} | {{ .Site.Title }}{{ end }}</title>
    <meta name="description" content="{{ .Description | default .Site.Params.description }}">
    {{ if .Site.Params.math }}
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
            onload="renderMathInElement(document.body, {delimiters: [{left: '$$', right: '$$', display: true}, {left: '$', right: '$', display: false}]});"></script>
    {{ end }}
    <link rel="stylesheet" href="/css/accessibility.css">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }
        nav {
            background: #f4f4f4;
            padding: 15px;
            margin-bottom: 30px;
            border-radius: 5px;
        }
        nav ul {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        nav ul li {
            display: inline;
            margin-right: 20px;
        }
        nav a {
            color: #0066cc;
            text-decoration: none;
        }
        nav a:hover {
            text-decoration: underline;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #222;
            margin-top: 1.5em;
        }
        h1 {
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }
        code {
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: "SF Mono", Monaco, Consolas, monospace;
        }
        pre {
            background: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }
        pre code {
            background: none;
            padding: 0;
        }
        img {
            max-width: 100%;
            height: auto;
        }
        a {
            color: #0066cc;
        }
        .menu-home {
            font-weight: bold;
            margin-right: 30px;
        }
    </style>
</head>
<body>
    <nav role="navigation" aria-label="Main navigation">
        <ul>
            <li class="menu-home"><a href="/">{{ .Site.Title }}</a></li>
            {{ range .Site.Menus.main }}
            {{ if not .Parent }}
            <li><a href="{{ .URL }}">{{ .Name }}</a></li>
            {{ end }}
            {{ end }}
        </ul>
    </nav>

    <main role="main">
        {{ block "main" . }}{{ end }}
    </main>

    <footer role="contentinfo" style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 0.9em;">
        {{ if .Site.Params.author }}
        <p>{{ .Site.Params.author }}</p>
        {{ end }}
        <p>Built with <a href="https://gohugo.io/">Hugo</a> | Converted with jupyter2hugo</p>
    </footer>
</body>
</html>
'''

    @staticmethod
    def generate_home() -> str:
        """Generate home page template (index.html)."""
        return '''{{ define "title" }}{{ .Site.Title }}{{ end }}
{{ define "main" }}
<article>
    <h1>{{ .Title }}</h1>
    {{ .Content }}
</article>

{{ if .Site.Menus.main }}
<section style="margin-top: 40px;">
    <h2>Sections</h2>
    <ul>
        {{ range .Site.Menus.main }}
        {{ if not .Parent }}
        <li style="margin-bottom: 10px;">
            <a href="{{ .URL }}"><strong>{{ .Name }}</strong></a>
        </li>
        {{ end }}
        {{ end }}
    </ul>
</section>
{{ end }}
{{ end }}
'''

    @staticmethod
    def generate_single() -> str:
        """Generate single page template (single.html)."""
        return '''{{ define "main" }}
<article>
    <header>
        <h1>{{ .Title }}</h1>
        {{ if .Params.description }}
        <p style="font-size: 1.1em; color: #666;">{{ .Params.description }}</p>
        {{ end }}
    </header>

    {{ .Content }}

    {{ if or .PrevInSection .NextInSection }}
    <nav style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #eee;">
        <div style="display: flex; justify-content: space-between;">
            <div>
                {{ with .PrevInSection }}
                <a href="{{ .RelPermalink }}">← {{ .Title }}</a>
                {{ end }}
            </div>
            <div style="text-align: right;">
                {{ with .NextInSection }}
                <a href="{{ .RelPermalink }}">{{ .Title }} →</a>
                {{ end }}
            </div>
        </div>
    </nav>
    {{ end }}
</article>
{{ end }}
'''

    @staticmethod
    def generate_list() -> str:
        """Generate list template (list.html)."""
        return '''{{ define "main" }}
<article>
    <h1>{{ .Title }}</h1>
    {{ .Content }}

    {{ if .Pages }}
    <section style="margin-top: 30px;">
        <h2>Pages in this section:</h2>
        <ul>
            {{ range .Pages.ByWeight }}
            <li style="margin-bottom: 10px;">
                <a href="{{ .RelPermalink }}"><strong>{{ .Title }}</strong></a>
                {{ if .Params.description }}
                <p style="margin: 5px 0 0 0; color: #666;">{{ .Params.description }}</p>
                {{ end }}
            </li>
            {{ end }}
        </ul>
    </section>
    {{ end }}
</article>
{{ end }}
'''

    @staticmethod
    def generate_all(layouts_dir: Path):
        """
        Generate all basic layout templates.

        Args:
            layouts_dir: Hugo layouts directory
        """
        # Create _default directory
        default_dir = layouts_dir / "_default"
        default_dir.mkdir(parents=True, exist_ok=True)

        # Generate baseof (base template)
        (default_dir / "baseof.html").write_text(
            TemplateGenerator.generate_baseof(),
            encoding='utf-8'
        )

        # Generate home template
        (layouts_dir / "index.html").write_text(
            TemplateGenerator.generate_home(),
            encoding='utf-8'
        )

        # Generate single page template
        (default_dir / "single.html").write_text(
            TemplateGenerator.generate_single(),
            encoding='utf-8'
        )

        # Generate list template
        (default_dir / "list.html").write_text(
            TemplateGenerator.generate_list(),
            encoding='utf-8'
        )


def generate_templates(layouts_dir: Path):
    """
    Generate all Hugo layout templates.

    Args:
        layouts_dir: Hugo layouts directory
    """
    TemplateGenerator.generate_all(layouts_dir)
