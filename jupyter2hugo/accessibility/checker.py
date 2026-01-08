"""Accessibility checking with pa11y integration."""

from pathlib import Path
from typing import Optional, Dict, Any
import subprocess
import json


class AccessibilityChecker:
    """Check WCAG 2.1 compliance using pa11y."""

    def __init__(self, standard: str = 'WCAG2AA'):
        """
        Initialize the accessibility checker.

        Args:
            standard: WCAG standard to check (WCAG2A, WCAG2AA, WCAG2AAA)
        """
        self.standard = standard

    def check_url(self, url: str) -> Dict[str, Any]:
        """
        Run pa11y on a URL.

        Args:
            url: URL to check

        Returns:
            Dict with results
        """
        try:
            result = subprocess.run(
                ['pa11y', '--reporter', 'json', '--standard', self.standard, url],
                capture_output=True,
                text=True,
                check=False
            )

            if result.stdout:
                issues = json.loads(result.stdout)
                return {
                    'url': url,
                    'issues': issues,
                    'count': len(issues),
                    'passed': len(issues) == 0
                }
            else:
                return {
                    'url': url,
                    'error': result.stderr,
                    'passed': False
                }

        except FileNotFoundError:
            raise ImportError("pa11y not found. Install with: npm install -g pa11y")
        except Exception as e:
            return {
                'url': url,
                'error': str(e),
                'passed': False
            }

    def check_html_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Run pa11y on an HTML file.

        Args:
            file_path: Path to HTML file

        Returns:
            Dict with results
        """
        file_url = f"file://{file_path.absolute()}"
        return self.check_url(file_url)

    def generate_report(self, results: list) -> str:
        """
        Generate a human-readable report from pa11y results.

        Args:
            results: List of check results

        Returns:
            Formatted report string
        """
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("Accessibility Report (WCAG 2.1)")
        report_lines.append("=" * 60)
        report_lines.append("")

        total_issues = 0
        passed_count = 0

        for result in results:
            url = result.get('url', 'Unknown')
            passed = result.get('passed', False)
            count = result.get('count', 0)

            total_issues += count

            if passed:
                report_lines.append(f"✓ {url} - PASSED")
                passed_count += 1
            else:
                report_lines.append(f"✗ {url} - {count} issue(s)")

                if 'issues' in result:
                    for issue in result['issues'][:5]:  # Show first 5 issues
                        report_lines.append(f"  - {issue.get('type', 'error')}: {issue.get('message', '')}")
                        report_lines.append(f"    Code: {issue.get('code', '')}")

                    if count > 5:
                        report_lines.append(f"  ... and {count - 5} more issue(s)")

            report_lines.append("")

        report_lines.append("=" * 60)
        report_lines.append(f"Summary: {passed_count}/{len(results)} pages passed")
        report_lines.append(f"Total issues: {total_issues}")
        report_lines.append("=" * 60)

        return "\n".join(report_lines)


def run_accessibility_check(hugo_site_dir: Path, build_first: bool = True) -> bool:
    """
    Run accessibility check on a Hugo site.

    Args:
        hugo_site_dir: Path to Hugo site directory
        build_first: Whether to build the site first

    Returns:
        True if all checks passed
    """
    if build_first:
        # Build the Hugo site
        result = subprocess.run(
            ['hugo', '--destination', 'public'],
            cwd=hugo_site_dir,
            capture_output=True
        )

        if result.returncode != 0:
            print(f"Hugo build failed: {result.stderr.decode()}")
            return False

    # Find HTML files in public directory
    public_dir = hugo_site_dir / 'public'
    if not public_dir.exists():
        print(f"Public directory not found: {public_dir}")
        return False

    html_files = list(public_dir.rglob('*.html'))

    if not html_files:
        print("No HTML files found to check")
        return False

    # Run pa11y on each file
    checker = AccessibilityChecker()
    results = []

    for html_file in html_files[:10]:  # Check first 10 files
        print(f"Checking: {html_file.relative_to(public_dir)}")
        result = checker.check_html_file(html_file)
        results.append(result)

    # Generate and print report
    report = checker.generate_report(results)
    print(report)

    # Save report to file
    report_file = hugo_site_dir / 'accessibility-report.txt'
    report_file.write_text(report, encoding='utf-8')
    print(f"\nReport saved to: {report_file}")

    # Return True if all checks passed
    return all(r.get('passed', False) for r in results)
