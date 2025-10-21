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

"""Deployment helpers."""
import json
import os
import platform
import shutil
import subprocess  # nosec
import sys
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import click
from aea.configurations.constants import AGENT
from aea.configurations.data_types import PublicId
from aea.helpers.base import cd
from compose.cli import main as docker_compose
from compose.config.errors import ConfigurationError
from compose.project import Project, ProjectError
from docker.errors import NotFound

from autonomy.chain.config import ChainType, ContractConfigs
from autonomy.chain.exceptions import FailedToRetrieveComponentMetadata
from autonomy.chain.service import get_agent_instances, get_service_info
from autonomy.chain.utils import resolve_component_id
from autonomy.cli.helpers.chain import OnChainHelper
from autonomy.cli.helpers.registry import fetch_service_ipfs
from autonomy.configurations.constants import DEFAULT_SERVICE_CONFIG_FILE
from autonomy.configurations.loader import load_service_config
from autonomy.constants import DEFAULT_BUILD_FOLDER
from autonomy.deploy.base import Resources, build_hash_id
from autonomy.deploy.build import generate_deployment
from autonomy.deploy.constants import (
    AGENT_KEYS_DIR,
    AGENT_VARS_CONFIG_FILE,
    BENCHMARKS_DIR,
    DEATTACH_WINDOWS_FLAG,
    INFO,
    LOG_DIR,
    PERSISTENT_DATA_DIR,
    TENDERMINT_FLASK_APP_PATH,
    TENDERMINT_VARS_CONFIG_FILE,
    TM_STATE_DIR,
    VENVS_DIR,
)
from autonomy.deploy.generators.kubernetes.base import KubernetesGenerator
from autonomy.deploy.generators.localhost.utils import check_tendermint_version
from autonomy.deploy.image import build_image


def _build_dirs(build_dir: Path, mkdir: Optional[List[str]] = None) -> None:
    """Build the necessary directories."""

    mkdirs = [(new_dir_name,) for new_dir_name in mkdir] if mkdir else []

    for dir_path in [
        (PERSISTENT_DATA_DIR,),
        (PERSISTENT_DATA_DIR, LOG_DIR),
        (PERSISTENT_DATA_DIR, TM_STATE_DIR),
        (PERSISTENT_DATA_DIR, BENCHMARKS_DIR),
        (PERSISTENT_DATA_DIR, VENVS_DIR),
        (AGENT_KEYS_DIR,),
    ] + mkdirs:
        path = Path(build_dir, *dir_path)
        path.mkdir(exist_ok=True, parents=True)
        # TOFIX: remove this safely
        try:
            os.chown(path, 1000, 1000)
        except PermissionError:  # pragma: no cover
            click.echo(
                f"Updating permissions failed for {path}, please do it manually."
            )
        except AttributeError:  # pragma: no cover
            continue


def _print_log(compose_app: docker_compose.TopLevelCommand) -> None:
    """Print docker container logs."""
    terminal_width, _ = shutil.get_terminal_size()
    for service in compose_app.project.service_names:
        try:
            click.echo("=" * terminal_width)
            click.echo(f"Trying to get logs for {service}")
            click.echo(compose_app.project.client.logs(service))
        except NotFound:
            continue


def _kill_containers(compose_app: docker_compose.TopLevelCommand) -> None:
    """Kill active containers before exiting."""
    for container in compose_app.project.containers(compose_app.project.service_names):
        click.echo(f"Trying to kill {container.name}")
        container.kill()


def _load_compose_project(
    build_dir: Path, options: Optional[Dict[str, str]] = None
) -> Project:
    """Load docker compose project."""
    try:
        return docker_compose.project_from_options(build_dir, options or {})
    except ConfigurationError as e:  # pragma: no cover
        if "Invalid interpolation format" in e.msg:
            raise click.ClickException(
                "Provided docker compose file contains environment placeholders, "
                "please use `--aev` flag if you intend to use environment variables."
            )
        raise


def run_deployment(
    build_dir: Path,
    no_recreate: bool = False,
    remove_orphans: bool = False,
    detach: bool = False,
    project_name: Optional[str] = None,
) -> None:
    """Run deployment."""
    try:
        options = {"--project-name": project_name} if project_name else {}
        project = _load_compose_project(build_dir=build_dir, options=options)
        commands = docker_compose.TopLevelCommand(project=project)
        commands.up(
            {
                "--detach": True,
                "--no-color": False,
                "--quiet-pull": False,
                "--no-deps": False,
                "--force-recreate": not no_recreate,
                "--always-recreate-deps": False,
                "--no-recreate": no_recreate,
                "--no-build": False,
                "--no-start": False,
                "--build": True,
                "--abort-on-container-exit": False,
                "--attach-dependencies": False,
                "--timeout": None,
                "--renew-anon-volumes": False,
                "--remove-orphans": remove_orphans,
                "--exit-code-from": None,
                "--scale": [],
                "--no-log-prefix": False,
                "SERVICE": None,
            }
        )
        if detach:
            click.echo("The service is running...")
            return
        click.echo("The service is running, press CTRL + C to stop...")
        while True:
            time.sleep(1)
    except NotFound as e:  # pragma: no cover
        raise click.ClickException(e.explanation)
    except ProjectError as e:  # pragma: no cover
        click.echo("Error occured bringing up the project")
        _print_log(compose_app=commands)
        _kill_containers(compose_app=commands)
        raise click.ClickException(e)
    except KeyboardInterrupt:  # pragma: no cover
        stop_deployment(build_dir=build_dir)


def _get_deattached_creation_flags() -> int:
    """Get Popen creation flag based on the platform."""
    return DEATTACH_WINDOWS_FLAG if platform.system() == "Windows" else 0


def _start_localhost_agent(working_dir: Path, detach: bool) -> None:
    """Start localhost agent process."""
    env = json.loads((working_dir / AGENT_VARS_CONFIG_FILE).read_text())
    process_fn: Callable = subprocess.Popen if detach else subprocess.run  # type: ignore[assignment]
    process = process_fn(  # pylint: disable=subprocess-run-check # nosec
        args=[sys.executable, "-m", "aea.cli", "run"],
        cwd=working_dir / AGENT,
        env={**os.environ, **env},
        creationflags=_get_deattached_creation_flags(),  # Detach process from the main process
    )
    (working_dir / "agent.pid").write_text(
        data=str(process.pid),
    )


def _start_localhost_tendermint(working_dir: Path) -> subprocess.Popen:
    """Start localhost tendermint process."""
    check_tendermint_version()
    env = json.loads((working_dir / TENDERMINT_VARS_CONFIG_FILE).read_text())
    flask_app_path = Path(__file__).parents[3] / TENDERMINT_FLASK_APP_PATH
    process = subprocess.Popen(  # pylint: disable=consider-using-with # nosec
        args=[
            "flask",
            "run",
            "--host",
            "localhost",
            "--port",
            "8080",
        ],
        cwd=working_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env={**os.environ, **env, "FLASK_APP": f"{flask_app_path}:create_server"},
        creationflags=_get_deattached_creation_flags(),  # Detach process from the main process
    )
    (working_dir / "tendermint.pid").write_text(
        data=str(process.pid),
    )
    return process


def run_host_deployment(build_dir: Path, detach: bool = False) -> None:
    """Run host deployment."""
    tm_process = _start_localhost_tendermint(build_dir)
    try:
        _start_localhost_agent(build_dir, detach)
    except Exception as e:  # pylint: disable=broad-except
        click.echo(e)
        tm_process.terminate()
    finally:
        if not detach:
            tm_process.terminate()


def stop_deployment(build_dir: Path, project_name: Optional[str] = None) -> None:
    """Stop running deployment."""
    try:
        options = {"--project-name": project_name} if project_name else {}
        project = _load_compose_project(build_dir=build_dir, options=options)
        commands = docker_compose.TopLevelCommand(project=project)
        click.echo("\nDon't cancel while stopping services...")
        commands.down({"--volumes": False, "--remove-orphans": True, "--rmi": None})
        _kill_containers(compose_app=commands)
    except NotFound as e:  # pragma: no cover
        raise click.ClickException(e.explanation)


def build_deployment(  # pylint: disable=too-many-locals
    keys_file: Path,
    build_dir: Path,
    deployment_type: str,
    dev_mode: bool,
    number_of_agents: Optional[int] = None,
    packages_dir: Optional[Path] = None,
    open_aea_dir: Optional[Path] = None,
    agent_instances: Optional[List[str]] = None,
    multisig_address: Optional[str] = None,
    consensus_threshold: Optional[int] = None,
    log_level: str = INFO,
    apply_environment_variables: bool = False,
    image_version: Optional[str] = None,
    use_hardhat: bool = False,
    use_acn: bool = False,
    use_tm_testnet_setup: bool = False,
    image_author: Optional[str] = None,
    resources: Optional[Resources] = None,
    service_hash_id: Optional[str] = None,
    service_offset: int = 0,
    mkdir: Optional[List[str]] = None,
) -> None:
    """Build deployment."""

    if build_dir.is_dir():  # pragma: no cover
        raise click.ClickException(f"Build already exists @ {build_dir}")

    if not (Path.cwd() / DEFAULT_SERVICE_CONFIG_FILE).exists():
        raise FileNotFoundError(
            f"No service configuration found at {Path.cwd()}"
        )  # pragma: no cover

    click.echo(f"Building deployment @ {build_dir}")
    build_dir.mkdir()
    if service_hash_id is None:
        service_hash_id = build_hash_id()
    _build_dirs(build_dir, mkdir)

    report = generate_deployment(
        service_hash_id=service_hash_id,
        service_offset=service_offset,
        service_path=Path.cwd(),
        type_of_deployment=deployment_type,
        keys_file=keys_file,
        number_of_agents=number_of_agents,
        build_dir=build_dir,
        dev_mode=dev_mode,
        packages_dir=packages_dir,
        open_aea_dir=open_aea_dir,
        agent_instances=agent_instances,
        multisig_address=multisig_address,
        consensus_threshold=consensus_threshold,
        log_level=log_level,
        apply_environment_variables=apply_environment_variables,
        image_version=image_version,
        use_hardhat=use_hardhat,
        use_acn=use_acn,
        use_tm_testnet_setup=use_tm_testnet_setup,
        image_author=image_author,
        resources=resources,
    )

    click.echo(report)


def _resolve_on_chain_token_id(
    token_id: int,
    chain_type: ChainType,
) -> Tuple[Dict[str, str], List[str], str, int]:
    """Resolve service metadata from tokenID"""

    ledger_api, _ = OnChainHelper.get_ledger_and_crypto_objects(chain_type=chain_type)
    contract_address = ContractConfigs.service_registry.contracts[chain_type]

    click.echo(f"Fetching service metadata using chain type {chain_type.value}")

    try:
        metadata = resolve_component_id(
            ledger_api=ledger_api,
            contract_address=contract_address,
            token_id=token_id,
            is_service=True,
        )
        info = get_agent_instances(
            ledger_api=ledger_api, chain_type=chain_type, token_id=token_id
        )
        agent_instances = info["agentInstances"]
        (
            _,
            multisig_address,
            _,
            consensus_threshold,
            *_,
        ) = get_service_info(
            ledger_api=ledger_api, chain_type=chain_type, token_id=token_id
        )
    except FailedToRetrieveComponentMetadata as e:
        raise click.ClickException(str(e)) from e
    except Exception as e:
        raise click.ClickException(
            f"Cannot find the service registry deployment; Service contract address {contract_address}; Error: {e}"
        ) from e

    return metadata, agent_instances, multisig_address, consensus_threshold


def build_and_deploy_from_token(  # pylint: disable=too-many-locals
    token_id: int,
    keys_file: Path,
    chain_type: ChainType,
    skip_image: bool,
    n: Optional[int],
    deployment_type: str,
    aev: bool = False,
    no_deploy: bool = False,
    detach: bool = False,
    resources: Optional[Resources] = None,
) -> None:
    """Build and run deployment from tokenID."""

    click.echo(f"Building service deployment using token ID: {token_id}")
    (
        service_metadata,
        agent_instances,
        multisig_address,
        consensus_threshold,
    ) = _resolve_on_chain_token_id(
        token_id=token_id,
        chain_type=chain_type,
    )

    click.echo("Service name: " + service_metadata["name"])
    *_, service_hash = service_metadata["code_uri"].split("//")
    public_id = PublicId(author="valory", name="service", package_hash=service_hash)
    service_path = fetch_service_ipfs(public_id)
    build_dir = service_path / DEFAULT_BUILD_FOLDER.format(build_hash_id())

    with cd(service_path):
        build_deployment(
            keys_file=keys_file,
            build_dir=build_dir,
            deployment_type=deployment_type,
            dev_mode=False,
            number_of_agents=n,
            agent_instances=agent_instances,
            multisig_address=multisig_address,
            consensus_threshold=consensus_threshold,
            apply_environment_variables=aev,
            resources=resources,
        )
        if not skip_image:
            click.echo("Building required images.")
            service = load_service_config(service_path, substitute_env_vars=aev)
            build_image(agent=service.agent)

    click.echo("Service build successful.")
    if no_deploy or deployment_type == KubernetesGenerator.deployment_type:
        return

    click.echo("Running deployment")
    run_deployment(build_dir, detach=detach)
