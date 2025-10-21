"""A script that can be called after you installed the package.

This script calls create tests, creates the pre-commit config, and
creates the pyproject.toml file and some other things to set up a project.
This package assumes you are using poetry and pre-commit.
This script is intended to be called once at the beginning of a project.
"""

from collections.abc import Callable
from typing import Any

from winipedia_utils.git.gitignore.gitignore import _add_package_patterns_to_gitignore
from winipedia_utils.git.pre_commit.config import (
    _add_package_hook_to_pre_commit_config,
    _pre_commit_install,
)
from winipedia_utils.git.pre_commit.run_hooks import _run_all_hooks
from winipedia_utils.git.workflows.publish import _add_publish_workflow
from winipedia_utils.logging.logger import get_logger
from winipedia_utils.projects.poetry.config import (
    _add_configurations_to_pyproject_toml,
)
from winipedia_utils.projects.poetry.poetry import (
    _install_dev_dependencies,
)
from winipedia_utils.projects.project import _create_project_root

logger = get_logger(__name__)


SETUP_STEPS = [
    _install_dev_dependencies,
    _add_package_hook_to_pre_commit_config,
    _pre_commit_install,
    _add_package_patterns_to_gitignore,
    _add_publish_workflow,
    _add_configurations_to_pyproject_toml,
    _create_project_root,
    _run_all_hooks,
]


def _get_setup_steps() -> list[Callable[..., Any]]:
    """Get the setup steps."""
    return SETUP_STEPS


def _setup() -> None:
    """Set up the project."""
    for step in _get_setup_steps():
        logger.info("Running setup step: %s", step.__name__)
        step()
    logger.info("Setup complete!")


if __name__ == "__main__":
    _setup()
