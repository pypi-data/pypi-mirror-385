# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2022-2025 Valory AG
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""Image building."""


import subprocess  # nosec
from pathlib import Path
from typing import Optional, Tuple

from aea.cli.utils.config import get_default_author_from_cli_config
from aea.configurations.data_types import Dependency, PublicId

from autonomy.constants import (
    AUTONOMY_IMAGE_NAME,
    AUTONOMY_IMAGE_VERSION,
    DEFAULT_DOCKER_IMAGE_AUTHOR,
    OAR_IMAGE,
)
from autonomy.data import DATA_DIR
from autonomy.deploy.constants import DOCKERFILES


def generate_dependency_flag_var(dependencies: Tuple[Dependency, ...]) -> str:
    """Generate dependency flag env var"""
    args = []
    for dep in dependencies:
        # Flag for `aea install` command
        args += ["-e"]
        args += dep.get_pip_install_args()
    return " ".join(args)


class ImageProfiles:  # pylint: disable=too-few-public-methods
    """Image build profiles."""

    CLUSTER = "cluster"
    DEVELOPMENT = "dev"
    PRODUCTION = "prod"
    ALL = (CLUSTER, DEVELOPMENT, PRODUCTION)


def build_image(  # pylint: disable=too-many-locals
    agent: PublicId,
    pull: bool = False,
    version: Optional[str] = None,
    image_author: Optional[str] = None,
    extra_dependencies: Optional[Tuple[Dependency, ...]] = None,
    dockerfile: Optional[Path] = None,
    platform: Optional[str] = None,
    push: bool = False,
    builder: Optional[str] = None,
    pre_install_command: Optional[str] = None,
) -> None:
    """Command to build images from for skaffold deployment."""

    tag: str
    path: str

    image_version = version or agent.hash
    path = str(DATA_DIR / DOCKERFILES / "agent")
    if dockerfile is not None:  # pragma: nocover
        path = str(Path(dockerfile).parent)

    tag = OAR_IMAGE.format(
        image_author=image_author or DEFAULT_DOCKER_IMAGE_AUTHOR,
        agent=agent.name,
        version=image_version,
    )

    build_process = subprocess.run(  # nosec # pylint: disable=subprocess-run-check
        [
            "docker",
            "build",
            "--build-arg",
            f"AUTONOMY_IMAGE_NAME={AUTONOMY_IMAGE_NAME}",
            "--build-arg",
            f"AUTONOMY_IMAGE_VERSION={AUTONOMY_IMAGE_VERSION}",
            "--build-arg",
            f"AUTHOR={get_default_author_from_cli_config()}",
            "--build-arg",
            f"AEA_AGENT={str(agent)}",
            "--tag",
            tag,
            "--no-cache",
        ]
        + (
            [
                "--build-arg",
                f"EXTRA_DEPENDENCIES={generate_dependency_flag_var(extra_dependencies)}",
            ]
            if extra_dependencies
            else []
        )
        + (
            ["--build-arg", f"PRE_INSTALL_COMMAND={pre_install_command}"]
            if pre_install_command
            else []
        )
        + (["--platform", platform] if platform else [])
        + (["--push"] if push else [])
        + (["--pull"] if pull else [])
        + (["--builder", builder] if builder else [])
        + [path]
    )

    build_process.check_returncode()


class ImageBuildFailed(Exception):
    """Raise when there's an error while building the agent image."""
