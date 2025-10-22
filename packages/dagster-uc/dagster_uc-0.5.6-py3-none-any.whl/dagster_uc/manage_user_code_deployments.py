#!/usr/bin/env python3
# ruff: noqa: D103
from __future__ import annotations

import contextlib
import json
import logging
import os
import pprint
import time
from dataclasses import asdict
from typing import Annotated, cast

import kr8s
import typer
from kr8s.objects import (
    Pod,
)

from dagster_uc.config import UserCodeDeploymentsConfig, load_config
from dagster_uc.log import logger
from dagster_uc.uc_handler import DagsterUserCodeHandler
from dagster_uc.utils import (
    BuildTool,
    build_and_push,
    gen_tag,
    is_command_available,
)

app = typer.Typer(invoke_without_command=True)
deployment_app = typer.Typer(
    name="deployment",
    help="Contains various subcommands for managing user code deployments",
    no_args_is_help=True,
)
app.add_typer(deployment_app)
deployment_delete_app = typer.Typer(
    name="delete",
    help="Delete one or more user code deployments",
)
deployment_app.add_typer(deployment_delete_app)
deployment_check_app = typer.Typer(
    name="check",
    help="Check status of the user code deployment",
)
deployment_app.add_typer(deployment_check_app)

handler: DagsterUserCodeHandler
config: UserCodeDeploymentsConfig


@app.command("show-config", help="Outputs the configuration that is currently in use")
def show_config():
    """Pretty print the config object"""
    pprint.pprint(config, indent=4)


@app.callback(invoke_without_command=True, no_args_is_help=True)
def default(
    ctx: typer.Context,
    environment: str = typer.Option("dev", "--environment", "-e", help="The environment"),
    config_file_path: str = typer.Option(
        None,
        "--config-file",
        "-c",
        help="Path to the config file.",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Output DEBUG logging"),
) -> None:
    """This function executes before any other nested cli command is called and loads the configuration object."""
    global logger
    global config
    global handler

    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    config = load_config(environment, config_file_path)

    if ctx.invoked_subcommand == "init-config":
        pass
    else:
        if verbose:
            config.verbose = True
        logger.debug(f"Switching kubernetes context to {config.environment}...")
        kr8s_api = kr8s.api(context=f"{config.kubernetes_context}", namespace=config.namespace)

        handler = DagsterUserCodeHandler(config, kr8s_api)
        handler.maybe_create_user_deployments_configmap()
        logger.debug(f"Done: Switched kubernetes context to {config.environment}")


def build_push_container(
    deployment_name: str,
    branch_name: str,
    image_prefix: str | None,
    config: UserCodeDeploymentsConfig,
    use_sudo: bool,
    tag: str,
) -> None:
    """Builds a docker image for a user-code deployment of the current branch and uploads it to the image registry"""
    handler.update_dagster_workspace_yaml()
    build_and_push(
        config.repository_root,
        config.container_registry,
        image_name=deployment_name
        if not image_prefix
        else os.path.join(image_prefix, deployment_name),
        dockerfile=config.dockerfile,
        use_sudo=use_sudo,
        tag=tag,
        branch_name=branch_name,
        use_az_login=config.use_az_login,
        build_envs=config.docker_env_vars if config.docker_env_vars is not None else [],
        build_format=config.build_format,
    )


@app.command(
    name="init-config",
    help="Create a config for dagster deployment",
    no_args_is_help=True,
)
def init_config(
    file: Annotated[
        str,
        typer.Option(
            "--file",
            "-f",
            help="File and path where to save the config example.",
        ),
    ],
):
    """Initiates a config template"""

    def optional_prompt(text: str) -> str | None:
        var = typer.prompt(text, default="")
        if var:
            return var
        else:
            return None

    initialized_config = UserCodeDeploymentsConfig(
        environment=typer.prompt("""What environment is this config for [dev, acc, prod etc.]"""),
        container_registry=typer.prompt("Container registry address"),
        container_registry_chart_path=optional_prompt(
            "Relative helm chart path of the previously provided container registry",
        ),
        dockerfile=typer.prompt("Path of dockerfile", default="./Dockerfile"),
        image_prefix=typer.prompt("Prefix for container image to use"),
        namespace=typer.prompt("Namespace of kubernetes deployment"),
        node=typer.prompt("Kubernetes node for user-code pod"),
        code_path=typer.prompt("Path of the Definitions python file inside docker image"),
        docker_root=typer.prompt("Path of docker scope", default="."),
        repository_root=typer.prompt("Path of project scope", default="."),
        dagster_version=typer.prompt(
            "Version of dagster in project (should mirror dagster depoyment!)",
        ),
        docker_env_vars=[],
        user_code_deployment_env_secrets=[],
        user_code_deployment_env=[],
        cicd=typer.confirm(
            "Whether it's executed in CICD. If set to True, then the deployment_name is created from the env",
        ),
        requests=json.loads(
            typer.prompt(
                "Request for the user pod in k8s in json formatted string",
                default=json.dumps({"cpu": "1", "memory": "1Gi"}),
            ),
        ),
        limits=json.loads(
            typer.prompt(
                "Limits for the user pod in k8s in json formatted string",
                default=json.dumps({"cpu": "2", "memory": "2Gi"}),
            ),
        ),
        image_pull_secrets=[],
        kubernetes_context=typer.prompt("Kubernetes context of the cluster to use for api calls"),
        dagster_gui_url=optional_prompt("URL of dagster UI"),
        use_latest_chart_version=typer.confirm(
            "Whether to use latest chart version, if disabled will always use the config dagster version",
        ),
        use_az_login=typer.confirm(
            "Whether to use az cli to login to container registry with podman, and helm if oci charts are used.",
        ),
        use_project_name=typer.confirm(
            "Whether to use the pyproject.toml project-name as deployment name prefix.",
        ),
        user_code_deployments_configmap_name=typer.prompt(
            "Configmap name to use for user_code_deployments",
            default="dagster-user-deployments-values-yaml",
        ),
        dagster_workspace_yaml_configmap_name=typer.prompt(
            "Configmap name of the dagster_workspace_yaml",
            default="dagster-workspace-yaml",
        ),
    )
    with open(file, "w") as fp:
        import yaml

        config_dict = asdict(initialized_config)
        complete_dict = {config_dict["environment"]: config_dict}
        yaml.dump(complete_dict, fp, default_flow_style=False)
    typer.echo(f"Template configuration file generated as '{file}'.")


@deployment_app.command(
    name="list",
    help="List user code deployments that are currently active",
)
def deployment_list():
    """Outputs a list of currently active deployments"""
    typer.echo(
        "\033[1mActive user code deployments\033[0m\n"
        + "\n".join(
            ["* " + d["name"] for d in handler.list_deployments()],
        ),
    )


@deployment_app.command(
    name="revive",
    help="Redeploy an old user code deployment using the latest existing image from the container registry",
)
def deployment_revive(
    name: Annotated[
        str,
        typer.Option("--name", "-n", help="The name of the deployment to revive."),
    ],
    tag: Annotated[str, typer.Option("--tag", "-t", help="The tag of the deployment to revive.")],
):
    # In case the UI name separator of the deployment is passed
    name = name.replace(":", "--")

    if not handler._check_deployment_exists(
        name,
    ):
        handler.add_user_deployment_to_configmap(
            handler.gen_new_deployment_yaml(
                name,
                image_prefix=handler.config.image_prefix,
                tag=tag,
            ),
        )
        handler.deploy_to_k8s()
        logger.info(f"Deployed {name}")
    else:
        raise Exception(f'Deployment "{name}" already exists')


@deployment_delete_app.callback(invoke_without_command=True)
def deployment_delete(
    delete_all: Annotated[
        bool,
        typer.Option(
            "--all",
            "-a",
            help="If this is provided, all deployments will be deleted including CI/CD provided deployments.",
        ),
    ] = False,
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="The name of the deployment to delete. If none is provided, the deployment corresponding to the currently checked out git branch will be deleted.",
        ),
    ] = None,
    branch: Annotated[
        str | None,
        typer.Option(
            "--branch",
            "-b",
            help="Can be the branch name as-is, this will be converted to a dagster-uc compatible deployment name.",
        ),
    ] = None,
) -> None:
    if delete_all:
        handler.remove_all_deployments()
        handler.deploy_to_k8s(reload_dagster=True)
        typer.echo("\033[1mDeleted all deployments\033[0m")
    else:
        if name is not None:
            # In case the UI name separator of the deployment is passed
            name = name.replace(":", "--")
        elif branch is not None:
            name = handler.get_deployment_name(
                use_project_name=config.use_project_name,
                branch=branch,
            ).full_name
        else:
            name = handler.get_deployment_name(
                use_project_name=config.use_project_name,
            ).full_name

        handler.remove_user_deployment_from_configmap(name)
        handler.deploy_to_k8s(reload_dagster=True)
        typer.echo(f"Deleted deployment \033[1m{name}\033[0m")


@deployment_check_app.callback(invoke_without_command=True)
def check_deployment(
    name: Annotated[
        str,
        typer.Option(
            "--name",
            "-n",
            help="The name of the deployment to check. If not provided, checks deployment corresponding to the current branch.",
        ),
    ] = "",
    timeout: Annotated[
        int,
        typer.Option(
            "--timeout",
            "-t",
            help="The timeout duration in seconds to keep following the logs of user code pod.",
        ),
    ] = 60,
) -> None:
    """This function executes before any other nested cli command is called and loads the configuration object."""
    if not name:
        name = handler.get_deployment_name(use_project_name=config.use_project_name).full_name
    else:
        # In case the UI name separator of the deployment is passed
        name = name.replace(":", "--")
    if not handler._check_deployment_exists(name):
        logger.warning(
            f"Deployment with name '{name}' does not seem to exist in environment '{config.environment}'. Attempting to proceed with status check anyways.",
        )
    typer.echo(f"\033[1mStatus for deployment {name}\033[0m")
    for pod in handler.api.get(
        Pod,
        label_selector=f"deployment={name}",
        namespace=config.namespace,
    ):
        pod = cast(Pod, pod)
        with contextlib.suppress(Exception):
            for line in pod.logs(pretty=True, follow=True, timeout=timeout):  # type: ignore
                typer.echo(line)
                if "started dagster code server" in line.lower():
                    break


@deployment_app.command(
    name="deploy",
    help="Deploys the currently checked out git branch as a user code deployment",
)
def deployment_deploy(
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="If this is provided, a full redeploy will always be done, rather than just rebooting user code pods if they already exist in order to trigger a new image pull",
        ),
    ] = False,
    skip_build: bool = typer.Option(
        False,
        "--skip-build",
        "-b",
        help="Image build and push will be skipped",
    ),
    deployment_name_suffix: str = typer.Option(
        "",
        "--deployment-name-suffix",
        "-s",
        help="Suffix to append to the default deployment name (which is based on the git branch name) - useful for doing parallel deployments from the same branch.",
    ),
    deployment_name: str = typer.Option(
        "",
        "--deployment-name",
        "-n",
        help="Overrides the name of the deployment, including any --deployment-name-suffix value",
    ),
    reset_lock: bool = typer.Option(
        False,
        "--reset-lock",
        "-r",
        help="Reset the deployment semaphore of any ongoing other deployments.",
    ),
    use_sudo: Annotated[
        bool,
        typer.Option(
            "--use-sudo",
            "-u",
            help="If this is provided, buildah or docker will be called with sudo",
        ),
    ] = False,
    ignore_check: Annotated[
        bool,
        typer.Option(
            "--ignore-check",
            help="If this is provided, ignore the check for if podman is installed. This is used for some CI/CD environments that require podman to always be in sudo mode",
        ),
    ] = False,
):
    handler._ensure_dagster_version_match()

    count = 0
    while not handler.acquire_semaphore(reset_lock):
        logger.error(
            f"Attempt {count}: Another deployment is in progress. Trying again in 10 seconds. You can force a reset of the deployment lock by using 'dagster-uc deployment deploy --reset-lock'",
        )
        count += 1
        time.sleep(10)

    try:
        logger.debug("Determining build tool...")
        if not ignore_check and not is_command_available(BuildTool.podman.value):
            raise Exception("Podman installation is required to run dagster-uc.")

        logger.debug("Using 'podman' to build image.")
        if deployment_name:
            (deployment_name, branch_name) = (deployment_name, deployment_name)
        else:
            dagster_deployment = handler.get_deployment_name(
                deployment_name_suffix,
                use_project_name=config.use_project_name,
            )
            (deployment_name, branch_name) = (
                dagster_deployment.full_name,
                dagster_deployment.branch_name,
            )

        logger.debug("Determining tag...")
        new_tag = gen_tag(
            deployment_name
            if not config.image_prefix
            else os.path.join(config.image_prefix, deployment_name),
            config.container_registry,
            config.dagster_version,
            config.use_az_login,
            use_sudo=use_sudo,
        )

        typer.echo(f"Deploying deployment \033[1m'{deployment_name}:{new_tag}'\033[0m")

        full_redeploy_done = False
        if not skip_build:
            build_push_container(
                deployment_name,
                branch_name=branch_name,
                image_prefix=handler.config.image_prefix,
                config=config,
                use_sudo=use_sudo,
                tag=new_tag,
            )

        if not handler._check_deployment_exists(deployment_name):
            logger.info(
                f"Deployment with name '{deployment_name}' does not exist yet in '{config.environment}'. Adding deployment to configmap",
            )
            handler.add_user_deployment_to_configmap(
                handler.gen_new_deployment_yaml(
                    deployment_name,
                    image_prefix=handler.config.image_prefix,
                    tag=new_tag,
                ),
            )
            handler.deploy_to_k8s()
        else:
            logger.info(
                f"Deployment with name '{deployment_name}' exists in '{config.environment}'. Updating deployment in configmap",
            )
            # TODO(ion): make this into a single operation (replace)
            handler.remove_user_deployment_from_configmap(deployment_name)
            handler.add_user_deployment_to_configmap(
                handler.gen_new_deployment_yaml(
                    deployment_name,
                    image_prefix=handler.config.image_prefix,
                    tag=new_tag,
                ),
            )
            if config.cicd or force:
                handler.deploy_to_k8s()
            elif not handler.check_if_code_pod_exists(label=deployment_name):
                logger.info(
                    "Code deployment present in configmap but pod not found, triggering full deploy...",
                )
                handler.deploy_to_k8s()  # Something went wrong - redeploy yamls and reload webserver
            else:
                logger.info(
                    "Code deployment present in configmap and pod found...",
                )
                handler.deploy_to_k8s(reload_dagster=False)
    finally:
        handler.release_semaphore()
    if config.dagster_gui_url:
        typer.echo(
            f"Your assets: {config.dagster_gui_url.rstrip('/')}/locations/{deployment_name.replace('--', ':')}/assets\033[0m",
        )
    time.sleep(5)
    timeout = 40 if not full_redeploy_done else 240

    while True:
        code_pods = list(
            handler.api.get(
                Pod,
                label_selector=f"deployment={deployment_name}",
                namespace=config.namespace,
            ),
        )
        if len(code_pods) == 0:
            time.sleep(2)
            continue
        else:
            break

    with contextlib.suppress(Exception):
        for code_pod in code_pods:
            code_pod.wait("condition=Ready", timeout=timeout)  # type: ignore
    check_deployment(deployment_name)


if __name__ == "__main__":
    app()
