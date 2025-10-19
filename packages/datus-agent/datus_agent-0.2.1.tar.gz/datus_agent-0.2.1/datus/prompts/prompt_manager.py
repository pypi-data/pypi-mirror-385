# Copyright 2025-present DatusAI, Inc.
# Licensed under the Apache License, Version 2.0.
# See http://www.apache.org/licenses/LICENSE-2.0 for details.

"""
Simple File-based Template Version Management

Manages prompt templates with simple file-based versioning.
Template files follow the pattern: {template_name}_{version}.j2
No configuration file needed - versions are determined by scanning files.
"""
import re
import shutil
from pathlib import Path
from typing import List, Optional

from jinja2 import Environment, FileSystemLoader, Template

from datus.utils.loggings import get_logger

logger = get_logger(__name__)


class PromptManager:
    """Manages file-based versioned prompt templates with Jinja2 rendering support."""

    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize the prompt manager.

        Args:
            templates_dir: Directory containing template files.
                          Defaults to check ~/.datus/template first, then fallback to 'prompt_templates'.
        """
        self.user_templates_dir = Path.home() / ".datus" / "template"
        if templates_dir is None:
            # Check user templates directory first
            default_templates_dir = Path(__file__).parent / "prompt_templates"

            if self.user_templates_dir.exists():
                templates_dir = self.user_templates_dir
                logger.info(f"Using user template directory: {self.user_templates_dir}")
            else:
                templates_dir = default_templates_dir
                logger.info(f"Using default template directory: {default_templates_dir}")
        else:
            logger.info(f"Using custom template directory: {templates_dir}")
        logger.info(f"Using template directory: {templates_dir}")
        self.templates_dir = Path(templates_dir)
        self.default_templates_dir = Path(__file__).parent / "prompt_templates"
        self._env = Environment(loader=FileSystemLoader(str(self.templates_dir)), trim_blocks=True, lstrip_blocks=True)

    def _get_template_path(self, template_name: str, version: Optional[str] = None) -> Path:
        """
        Get the actual file path for a template and version.

        Args:
            template_name: Name of the template (without version suffix)
            version: Version string or None for latest version

        Returns:
            Actual file_path
        """
        if version is None:
            # Find the latest version
            versions = self.list_template_versions(template_name)
            if not versions:
                raise FileNotFoundError(f"No versions found for template '{template_name}'")
            version = versions[-1]  # Get the latest version

        filename = f"{template_name}_{version}.j2"

        # Check user templates directory first
        user_templates_dir = Path.home() / ".datus" / "template"
        user_file_path = user_templates_dir / filename

        if user_file_path.exists():
            # Update the environment to use user templates directory
            self.templates_dir = user_templates_dir
            self._env = Environment(
                loader=FileSystemLoader(str(self.templates_dir)), trim_blocks=True, lstrip_blocks=True
            )
            logger.debug(f"Loading template from user directory: {user_file_path}")
            return user_file_path

        # Fallback to default templates directory
        default_file_path = self.default_templates_dir / filename
        if default_file_path.exists():
            # Update the environment to use default templates directory
            self.templates_dir = self.default_templates_dir
            self._env = Environment(
                loader=FileSystemLoader(str(self.templates_dir)), trim_blocks=True, lstrip_blocks=True
            )
            logger.debug(f"Loading template from default directory: {default_file_path}")
            return default_file_path

        raise FileNotFoundError(
            f"Prompt Template file '{filename}' not found in user directory ({user_templates_dir})"
            f" or default directory ({self.default_templates_dir})"
        )

    def _get_template_filename(self, template_name: str, version: Optional[str] = None) -> str:
        """
        Get the actual filename for a template and version.

        Args:
            template_name: Name of the template (without version suffix)
            version: Version string or None for latest version

        Returns:
            Actual filename with version
        """
        file_path = self._get_template_path(template_name, version)
        return file_path.name

    def load_template(self, template_name: str, version: Optional[str] = None) -> Template:
        """
        Load a template by name and version.

        Args:
            template_name: Name of the template (without version suffix)
            version: Version string (e.g., '1.0') or None for latest

        Returns:
            Jinja2 Template object
        """
        filename = self._get_template_filename(template_name, version)
        return self._env.get_template(filename)

    def render_template(self, template_name: str, version: Optional[str] = None, **kwargs) -> str:
        """
        Render a template with the given variables.

        Args:
            template_name: Name of the template
            version: Version string (e.g., '1.0') or None for latest
            **kwargs: Variables to pass to the template

        Returns:
            Rendered template string
        """
        template = self.load_template(template_name, version)
        return template.render(**kwargs)

    def get_raw_template(self, template_name: str, version: Optional[str] = None) -> str:
        """
        Get the raw template content without rendering.

        Args:
            template_name: Name of the template
            version: Version string (e.g., '1.0') or None for latest

        Returns:
            Raw template string
        """
        filename = self._get_template_filename(template_name, version)
        template_path = self.templates_dir / filename

        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()

    def list_templates(self) -> List[str]:
        """
        List all available template names (without versions).

        Returns:
            List of template names
        """
        template_names = set()

        # Check user templates directory first
        user_templates_dir = Path.home() / ".datus" / "template"

        if user_templates_dir.exists():
            for file_path in user_templates_dir.glob("*.j2"):
                match = re.match(r"(.+)_(\d+\.\d+)\.j2$", file_path.name)
                if match:
                    template_names.add(match.group(1))

        # Also check default templates directory
        for file_path in self.default_templates_dir.glob("*.j2"):
            match = re.match(r"(.+)_(\d+\.\d+)\.j2$", file_path.name)
            if match:
                template_names.add(match.group(1))

        return sorted(template_names)

    def list_template_versions(self, template_name: str) -> List[str]:
        """
        List all available versions for a specific template.

        Args:
            template_name: Name of the template

        Returns:
            List of version strings sorted by version number
        """
        versions = set()

        # Check user templates directory first
        user_templates_dir = Path.home() / ".datus" / "template"
        pattern = f"{template_name}_*.j2"

        if user_templates_dir.exists():
            for file_path in user_templates_dir.glob(pattern):
                match = re.search(r"_(\d+\.\d+)\.j2$", file_path.name)
                if match:
                    versions.add(match.group(1))

        # Also check default templates directory for versions not in user directory
        for file_path in self.default_templates_dir.glob(pattern):
            match = re.search(r"_(\d+\.\d+)\.j2$", file_path.name)
            if match:
                version = match.group(1)
                # Only add if not already found in user directory
                user_file = user_templates_dir / f"{template_name}_{version}.j2"
                if not user_file.exists():
                    versions.add(version)

        # Sort versions naturally (1.0, 1.1, 2.0, etc.)
        def version_key(v):
            try:
                return tuple(map(int, v.split(".")))
            except BaseException:
                return (0, 0)

        return sorted(versions, key=version_key)

    def get_latest_version(self, template_name: str) -> str:
        """
        Get the latest version for a template.

        Args:
            template_name: Name of the template

        Returns:
            Latest version string
        """
        versions = self.list_template_versions(template_name)
        if not versions:
            raise FileNotFoundError(f"No versions found for template '{template_name}'")
        return versions[-1]

    def create_template_version(self, template_name: str, new_version: str, base_version: Optional[str] = None) -> None:
        """
        Create a new version of a template by copying from an existing version.

        Args:
            template_name: Name of the template
            new_version: New version string (e.g., '1.1')
            base_version: Version to copy from, or None for latest version
        """
        # Get source file
        if base_version is None:
            base_version = self.get_latest_version(template_name)

        source_filename = f"{template_name}_{base_version}.j2"
        source_path = self.templates_dir / source_filename

        if not source_path.exists():
            raise FileNotFoundError(f"Source template '{source_filename}' not found")

        # Create new file
        new_filename = f"{template_name}_{new_version}.j2"
        new_path = self.templates_dir / new_filename

        if new_path.exists():
            raise ValueError(f"Version '{new_version}' already exists for template '{template_name}'")

        # Copy content
        shutil.copy2(source_path, new_path)
        print(f"Created {new_filename} based on {source_filename}")

    def template_exists(self, template_name: str, version: Optional[str] = None) -> bool:
        """
        Check if a template exists.

        Args:
            template_name: Name of the template
            version: Version string or None for any version

        Returns:
            True if template exists
        """
        try:
            self._get_template_filename(template_name, version)
            return True
        except FileNotFoundError:
            return False

    def get_template_info(self, template_name: str) -> dict:
        """
        Get information about a template.

        Args:
            template_name: Name of the template

        Returns:
            Dictionary with template information
        """
        versions = self.list_template_versions(template_name)
        latest_version = versions[-1] if versions else None

        return {
            "name": template_name,
            "available_versions": versions,
            "latest_version": latest_version,
            "total_versions": len(versions),
        }

    def copy_to(self, src_name: str, target_name: str, target_version: str = "1.0") -> str:
        if not self.user_templates_dir.exists():
            self.user_templates_dir.mkdir(parents=True)

        target_path = str(self.user_templates_dir / f"{target_name}_{target_version}.j2")
        src_path = self._get_template_path(src_name)
        shutil.copy2(src_path, target_path)
        return target_path


# Global instance for easy access
prompt_manager = PromptManager()
