"""Generate Hugo shortcode templates."""

from pathlib import Path


class ShortcodeGenerator:
    """Generate Hugo shortcode HTML templates."""

    @staticmethod
    def generate_admonition() -> str:
        """Generate admonition shortcode template."""
        return '''{{/* Admonition shortcode for notes, warnings, tips, etc. */}}
{{- $type := .Get "type" | default "note" -}}
{{- $title := .Get "title" -}}
{{- $class := .Get "class" | default "" -}}

<div class="admonition admonition-{{ $type }} {{ $class }}" role="note" aria-label="{{ $type | title }}">
  {{- if $title -}}
  <p class="admonition-title">{{ $title }}</p>
  {{- else -}}
  <p class="admonition-title">{{ $type | title }}</p>
  {{- end -}}
  <div class="admonition-content">
    {{ .Inner | markdownify }}
  </div>
</div>
'''

    @staticmethod
    def generate_youtube() -> str:
        """Generate YouTube embed shortcode template."""
        return '''{{/* YouTube embed shortcode with accessibility */}}
{{- $id := .Get 0 -}}
{{- $title := .Get "title" | default "YouTube video player" -}}

<div class="youtube-embed" style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">
  <iframe
    src="https://www.youtube-nocookie.com/embed/{{ $id }}"
    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
    frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    allowfullscreen
    title="{{ $title }}"
    loading="lazy">
  </iframe>
</div>
'''

    @staticmethod
    def generate_figure() -> str:
        """Generate figure shortcode template."""
        return '''{{/* Figure shortcode with caption and alt text */}}
{{- $src := .Get "src" -}}
{{- $alt := .Get "alt" | default "" -}}
{{- $caption := .Get "caption" | default "" -}}
{{- $width := .Get "width" | default "" -}}
{{- $class := .Get "class" | default "" -}}

<figure class="figure {{ $class }}" role="figure"{{- if $caption }} aria-label="{{ $caption }}"{{- end }}>
  <img src="{{ $src }}" alt="{{ if $alt }}{{ $alt }}{{ else }}{{ $caption }}{{ end }}"{{- if $width }} width="{{ $width }}"{{- end }} loading="lazy">
  {{- if $caption -}}
  <figcaption class="figure-caption">{{ $caption | markdownify }}</figcaption>
  {{- end -}}
</figure>
'''

    @staticmethod
    def generate_all(output_dir: Path):
        """
        Generate all shortcode templates.

        Args:
            output_dir: Directory to write shortcodes (layouts/shortcodes/)
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate admonition shortcode
        (output_dir / "admonition.html").write_text(
            ShortcodeGenerator.generate_admonition(),
            encoding='utf-8'
        )

        # Generate YouTube shortcode
        (output_dir / "youtube.html").write_text(
            ShortcodeGenerator.generate_youtube(),
            encoding='utf-8'
        )

        # Generate figure shortcode
        (output_dir / "figure.html").write_text(
            ShortcodeGenerator.generate_figure(),
            encoding='utf-8'
        )

    @staticmethod
    def generate_accessibility_css() -> str:
        """Generate accessibility CSS for admonitions and content."""
        return '''/* Accessibility styles for jupyter2hugo */

/* Admonition styles */
.admonition {
  margin: 1.5rem 0;
  padding: 1rem;
  border-left: 4px solid;
  border-radius: 4px;
  background-color: #f8f9fa;
}

.admonition-title {
  font-weight: bold;
  margin-top: 0;
  margin-bottom: 0.5rem;
}

.admonition-content {
  margin: 0;
}

/* Type-specific colors (WCAG AA compliant) */
.admonition-note {
  border-color: #0066cc;
  background-color: #e6f2ff;
}

.admonition-tip, .admonition-hint {
  border-color: #00a854;
  background-color: #e6f7f0;
}

.admonition-warning, .admonition-caution {
  border-color: #fa8c16;
  background-color: #fff7e6;
}

.admonition-danger, .admonition-error {
  border-color: #cf1322;
  background-color: #fff1f0;
}

.admonition-important, .admonition-attention {
  border-color: #722ed1;
  background-color: #f9f0ff;
}

/* YouTube embed responsive */
.youtube-embed {
  margin: 1.5rem 0;
}

/* Figure styles */
.figure {
  margin: 1.5rem auto;
  text-align: center;
}

.figure img {
  max-width: 100%;
  height: auto;
}

.figure-caption {
  margin-top: 0.5rem;
  font-size: 0.9em;
  color: #666;
  font-style: italic;
}

/* Code block improvements */
pre {
  overflow-x: auto;
  padding: 1rem;
  border-radius: 4px;
}

/* Math equation spacing */
.math {
  overflow-x: auto;
  overflow-y: hidden;
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .admonition {
    background-color: #1f1f1f;
    color: #e0e0e0;
  }

  .admonition-note {
    background-color: #002b4d;
  }

  .admonition-tip, .admonition-hint {
    background-color: #003d26;
  }

  .admonition-warning, .admonition-caution {
    background-color: #4d2800;
  }

  .admonition-danger, .admonition-error {
    background-color: #4d0a0f;
  }

  .admonition-important, .admonition-attention {
    background-color: #2b1652;
  }

  .figure-caption {
    color: #b0b0b0;
  }
}
'''


def generate_shortcodes(layouts_dir: Path):
    """
    Generate all shortcode templates and CSS.

    Args:
        layouts_dir: Hugo layouts directory
    """
    shortcodes_dir = layouts_dir / "shortcodes"
    ShortcodeGenerator.generate_all(shortcodes_dir)

    # Also generate CSS
    static_css_dir = layouts_dir.parent / "static" / "css"
    static_css_dir.mkdir(parents=True, exist_ok=True)
    (static_css_dir / "accessibility.css").write_text(
        ShortcodeGenerator.generate_accessibility_css(),
        encoding='utf-8'
    )
