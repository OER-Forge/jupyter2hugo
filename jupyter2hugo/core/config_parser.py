"""Parse Jupyter Book _config.yml files."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any
import yaml


@dataclass
class JupyterBookConfig:
    """Configuration from Jupyter Book _config.yml."""

    title: str = ""
    author: str = ""
    authors: List[str] = field(default_factory=list)
    logo: Optional[str] = None
    description: Optional[str] = None
    copyright: Optional[str] = None
    license: Optional[str] = None

    # Repository information
    repository_url: Optional[str] = None
    repository_branch: Optional[str] = None

    # Additional metadata
    language: str = "en"
    baseurl: str = ""

    # Raw config for advanced users
    raw_config: Dict[str, Any] = field(default_factory=dict)

    def get_all_authors(self) -> List[str]:
        """Get a list of all authors."""
        if self.authors:
            return self.authors
        if self.author:
            return [self.author]
        return []

    def get_author_string(self) -> str:
        """Get authors as a comma-separated string."""
        authors = self.get_all_authors()
        if not authors:
            return ""
        if len(authors) == 1:
            return authors[0]
        if len(authors) == 2:
            return f"{authors[0]} and {authors[1]}"
        return ", ".join(authors[:-1]) + f", and {authors[-1]}"


class ConfigParser:
    """Parser for Jupyter Book _config.yml files."""

    def __init__(self, config_path: Path):
        """
        Initialize the config parser.

        Args:
            config_path: Path to the _config.yml file
        """
        self.config_path = config_path
        self.config_dir = config_path.parent

    def parse(self) -> JupyterBookConfig:
        """
        Parse the _config.yml file.

        Returns:
            JupyterBookConfig object with parsed configuration
        """
        with open(self.config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}

        # Extract basic metadata
        title = data.get('title', '')
        author = data.get('author', '')
        logo = data.get('logo')
        description = data.get('description')
        copyright_text = data.get('copyright')
        license_info = None

        # Handle license (can be a string or dict)
        license_data = data.get('license', {})
        if isinstance(license_data, str):
            license_info = license_data
        elif isinstance(license_data, dict):
            license_info = license_data.get('code') or license_data.get('text')

        # Handle authors (can be a string, list, or list of dicts)
        authors = []
        if 'authors' in data:
            authors_data = data['authors']
            if isinstance(authors_data, list):
                for author_entry in authors_data:
                    if isinstance(author_entry, str):
                        authors.append(author_entry)
                    elif isinstance(author_entry, dict):
                        name = author_entry.get('name', '')
                        if name:
                            authors.append(name)
            elif isinstance(authors_data, str):
                authors = [authors_data]
        elif author:
            authors = [author] if isinstance(author, str) else author

        # Extract repository information
        repo_url = None
        repo_branch = None
        if 'repository' in data:
            repo_data = data['repository']
            if isinstance(repo_data, dict):
                repo_url = repo_data.get('url')
                repo_branch = repo_data.get('branch', 'main')
            elif isinstance(repo_data, str):
                repo_url = repo_data

        # Language
        language = 'en'
        if 'sphinx' in data and 'language' in data['sphinx']:
            language = data['sphinx']['language']

        # Base URL
        baseurl = data.get('baseurl', '')

        return JupyterBookConfig(
            title=title,
            author=author,
            authors=authors,
            logo=logo,
            description=description,
            copyright=copyright_text,
            license=license_info,
            repository_url=repo_url,
            repository_branch=repo_branch,
            language=language,
            baseurl=baseurl,
            raw_config=data
        )

    def resolve_logo_path(self, config: JupyterBookConfig) -> Optional[Path]:
        """
        Resolve the absolute path to the logo file.

        Args:
            config: Parsed configuration

        Returns:
            Path to logo file or None
        """
        if not config.logo:
            return None

        logo_path = self.config_dir / config.logo
        if logo_path.exists():
            return logo_path

        return None


def load_config(config_path: Path) -> JupyterBookConfig:
    """
    Convenience function to load and parse a _config.yml file.

    Args:
        config_path: Path to _config.yml

    Returns:
        Parsed JupyterBookConfig
    """
    parser = ConfigParser(config_path)
    return parser.parse()
