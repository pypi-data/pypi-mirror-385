from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

from yaml import safe_load

from suite_py.lib import logger, metrics
from suite_py.lib.handler.changelog_handler import ChangelogHandler
from suite_py.lib.handler.git_handler import GitHandler
from suite_py.lib.handler.github_handler import GithubHandler
from suite_py.lib.handler.version_handler import VersionHandler


class Bump:
    """
    Bumps the local project version.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, project, config, tokens):
        self._changelog_handler = ChangelogHandler()
        _github = GithubHandler(tokens)
        self._repo = _github.get_repo(project)
        _git = GitHandler(project, config)
        self._version = VersionHandler(_repo=self._repo, _git=_git, _github=_github)

    @metrics.command("bump")
    def run(self, project: Optional[str] = None, version: Optional[str] = None) -> None:

        configurations = read_bump_configs_from_yaml(Path(".versions.yml"))
        version_config = (
            configurations[project] if project else configurations["base_project"]
        )

        current_version = self._find_current_version(version_config)

        logger.info(  # pylint: disable=logging-fstring-interpolation
            f"The current version is {current_version}"
        )
        selected_version = version or self._version.select_new_version(
            current_version, allow_prerelease=True, allow_custom_version=True
        )
        self._replace_version_in_project_files(
            current_version, cast(str, selected_version), version_config
        )

        if self._changelog_handler.changelog_exists():
            self._changelog_handler.bump_changelog(
                self._repo.html_url, current_version, selected_version
            )

        logger.info(f"Successfully bumped to version {selected_version}")

    @staticmethod
    def _find_current_version(config: BumpVersionConfig) -> str:
        versions = []
        for file_config in config.files:
            pattern = re.compile(
                file_config.pattern.format(
                    version=r"([0-9]+\.[0-9]+\.[0-9]+(?:-\w+\.[0-9]+)?)"
                ),
                flags=re.MULTILINE,
            )
            matches = pattern.findall(file_config.path.read_text(encoding="utf-8"))
            if len(matches) == 0:
                logger.error(
                    f'Cannot find "{file_config.pattern}" in file {str(file_config.path.absolute())}'
                )
                sys.exit(-1)
            versions += matches

        if len(set(versions)) != 1:
            logger.error(
                "Some of the versions inside the configured project files do not match."
            )
            sys.exit(-1)

        return versions[0]

    def _replace_version_in_project_files(
        self, current_version: str, target_version: str, config: BumpVersionConfig
    ) -> None:
        """
        Replaces current_version with target_version everywhere
        """
        for file_config in config.files:
            search = file_config.pattern.format(
                version=rf"(?P<version>{current_version})"
            )
            self._replace_in_file(file_config.path, search, target_version)

    @staticmethod
    def _replace_in_file(filepath: Path, search: str, target_version: str) -> None:
        """
        Replaces the named group `version` of `search` regex with `target_version` inside `filepath`.
        """
        text = filepath.read_text(encoding="utf-8")

        matched = re.search(search, text, re.MULTILINE)
        if matched is None:
            logger.error(f"No version matched in the provided file: {filepath}")
            sys.exit(-1)

        matched_from, matched_to = matched.span("version")
        final_text = text[:matched_from] + target_version + text[matched_to:]

        filepath.write_text(final_text, encoding="utf-8")


def read_bump_configs_from_yaml(filepath: Path) -> Dict[str, BumpVersionConfig]:
    with open(filepath, "r", encoding="utf-8") as yaml_file:
        content = safe_load(yaml_file)
    configs = {}
    if "files" in content:
        configs["base_project"] = BumpVersionConfig.from_dict(content)
    if "projects" in content:
        for name, subconfig in content["projects"].items():
            configs[name] = BumpVersionConfig.from_dict(subconfig)
    return configs


@dataclass
class BumpVersionConfig:
    """
    Represents the YAML configuration file for the Bump command.
    """

    files: List[VersionFileConfig]
    """
    The list of files in which the version should be bumped.
    """

    @classmethod
    def from_dict(cls, values: Dict[str, Any]) -> BumpVersionConfig:
        return cls(
            files=[
                VersionFileConfig(
                    path=Path(file_config["path"]), pattern=file_config["pattern"]
                )
                for file_config in values["files"]
            ]
        )


@dataclass
class VersionFileConfig:
    """
    Configuration for a single file in which the version should be bumped.
    """

    path: Path
    """
    Path to the file, relative from the project root.
    """
    pattern: str
    """
    The pattern used to lookup and replace the version.
    """
