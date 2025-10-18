# Copyright (c) 2025-Present API SERVICE S.A.C. (<https://www.apiservicesac.com/>)

import asyncio

from dooservice.core.domain.entities.configuration import DooServiceConfiguration
from dooservice.instance.application.use_cases.install_python_dependencies import (
    InstallPythonDependencies,
)
from dooservice.instance.domain.entities.instance_configuration import (
    InstanceEnvironment,
)
from dooservice.instance.domain.exceptions.instance_exceptions import (
    InstanceAlreadyExistsException,
    InstanceConfigurationException,
    InstanceOperationException,
)
from dooservice.instance.domain.repositories.docker_repository import DockerRepository
from dooservice.instance.domain.repositories.instance_repository import (
    InstanceRepository,
)
from dooservice.instance.domain.services.docker_orchestrator import DockerOrchestrator
from dooservice.instance.domain.services.instance_orchestrator import (
    InstanceOrchestrator,
)
from dooservice.repository.application.use_cases.sync_repositories import (
    SyncRepositoriesUseCase,
)
from dooservice.shared.messaging import MessageInterface


class CreateInstance:
    def __init__(
        self,
        sync_repositories: SyncRepositoriesUseCase,
        instance_repository: InstanceRepository,
        docker_repository: DockerRepository,
        instance_orchestrator: InstanceOrchestrator,
        docker_orchestrator: DockerOrchestrator,
        messenger: MessageInterface,
    ):
        self._sync_repositories = sync_repositories
        self._instance_repository = instance_repository
        self._docker_repository = docker_repository
        self._instance_orchestrator = instance_orchestrator
        self._docker_orchestrator = docker_orchestrator
        self._messenger = messenger
        self._install_dependencies = InstallPythonDependencies(
            instance_repository, docker_repository, messenger
        )

    async def execute(
        self, instance_name: str, config: DooServiceConfiguration
    ) -> None:
        """Create a new instance with repositories, configuration, and containers."""
        try:
            if await self._instance_repository.instance_exists(instance_name):
                raise InstanceAlreadyExistsException(instance_name)

            if instance_name not in config.instances:
                raise InstanceConfigurationException(
                    f"Instance '{instance_name}' not found in configuration",
                    instance_name,
                )

            instance_config = config.instances[instance_name]

            # Calculate total steps
            total_repos = (
                len(instance_config.repositories) if instance_config.repositories else 0
            )
            total_deps = (
                len(instance_config.python_dependencies)
                if instance_config.python_dependencies
                else 0
            )

            # Show steps header
            steps = [
                "Create directories",
                f"Synchronize {total_repos} repositories"
                if total_repos > 1
                else f"Synchronize {total_repos} repository",
                "Create configuration files",
                "Create Docker infrastructure",
            ]

            # Add Python dependencies step if defined
            if total_deps > 0:
                steps.append(
                    f"Install {total_deps} Python dependencies"
                    if total_deps > 1
                    else f"Install {total_deps} Python dependency"
                )

            self._messenger.show_steps_header(
                steps, title=f"Creating instance '{instance_name}'"
            )

            instance_env = self._instance_orchestrator.prepare_instance_environment(
                instance_name, instance_config
            )

            # Step 1: Directories
            self._messenger.update_step_status(1, len(steps), steps[0], "in_progress")
            await self._create_directories(instance_env)
            self._messenger.update_step_status(1, len(steps), steps[0], "completed")

            # Step 2: Repositories
            self._messenger.update_step_status(2, len(steps), steps[1], "in_progress")
            if total_repos > 0:
                for idx, repo_name in enumerate(instance_config.repositories, 1):
                    with self._messenger.spinner_context(
                        f"  └─ Syncing '{repo_name}' ({idx}/{total_repos})"
                    ) as spinner:
                        await self._sync_repositories.execute(instance_name, repo_name)
                        spinner.stop(f"  └─ '{repo_name}' synced", success=True)
            self._messenger.update_step_status(2, len(steps), steps[1], "completed")

            # Step 3: Configuration files
            self._messenger.update_step_status(3, len(steps), steps[2], "in_progress")
            await self._create_configuration_files(instance_env, instance_config)
            self._messenger.update_step_status(3, len(steps), steps[2], "completed")

            # Step 4: Docker infrastructure
            self._messenger.update_step_status(4, len(steps), steps[3], "in_progress")
            await self._create_docker_infrastructure(
                instance_name, instance_env, instance_config
            )
            self._messenger.update_step_status(4, len(steps), steps[3], "completed")

            # Step 5: Python dependencies (if defined)
            if total_deps > 0:
                self._messenger.update_step_status(
                    5, len(steps), steps[4], "in_progress"
                )
                try:
                    # Start web container temporarily to install dependencies
                    await self._start_web_container_for_install(instance_name)

                    # Install dependencies (skip running check, we just started it)
                    await self._install_dependencies.execute(
                        instance_name, instance_config, skip_running_check=True
                    )

                    # Stop web container after installation
                    await self._stop_web_container_after_install(instance_name)

                    self._messenger.update_step_status(
                        5, len(steps), steps[4], "completed"
                    )
                except Exception as e:  # noqa: BLE001
                    self._messenger.warning_with_icon(
                        f"Failed to install Python dependencies: {str(e)}"
                    )
                    self._messenger.update_step_status(
                        5, len(steps), steps[4], "failed"
                    )
                    # Ensure container is stopped even on error
                    try:  # noqa: SIM105
                        await self._stop_web_container_after_install(instance_name)
                    except Exception:  # noqa: BLE001, S110
                        pass

            self._messenger.show_success_animation(
                f"Instance '{instance_name}' is ready!"
            )

        except (InstanceAlreadyExistsException, InstanceConfigurationException) as e:
            self._messenger.error_with_icon(str(e))
            raise
        except Exception as e:  # noqa: BLE001
            self._messenger.show_error_animation(
                f"Failed to create instance '{instance_name}': {str(e)}"
            )
            raise InstanceOperationException(str(e), instance_name) from e

    async def _create_directories(self, instance_env: InstanceEnvironment) -> None:
        """Create necessary directories for the instance."""
        await self._instance_repository.create_instance_directories(
            instance_env.name, str(instance_env.paths.data_dir)
        )

        for path in [
            instance_env.paths.addons_dir,
            instance_env.paths.logs_dir,
            instance_env.paths.filestore_dir,
            instance_env.paths.nginx_conf_dir,
        ]:
            path.mkdir(parents=True, exist_ok=True)

        instance_env.paths.config_file.parent.mkdir(parents=True, exist_ok=True)

    async def _create_configuration_files(
        self, instance_env: InstanceEnvironment, instance_config
    ) -> None:
        """Create Odoo configuration and environment files."""
        odoo_config = self._instance_orchestrator.generate_odoo_config(
            instance_env, instance_config
        )

        with open(instance_env.paths.config_file, "w") as f:  # noqa: ASYNC230
            f.write(odoo_config)

        # Generate nginx config if nginx is enabled
        if (
            instance_config.deployment.docker
            and instance_config.deployment.docker.nginx
        ):
            nginx_config = self._instance_orchestrator.generate_nginx_config(
                instance_env, instance_config
            )
            with open(instance_env.paths.nginx_conf_file, "w") as f:  # noqa: ASYNC230
                f.write(nginx_config)

        env_file = instance_env.paths.data_dir / ".env"
        with open(env_file, "w") as f:  # noqa: ASYNC230
            for key, value in instance_env.env_vars.items():
                f.write(f"{key}={value}\n")

    async def _create_docker_infrastructure(
        self, instance_name: str, instance_env: InstanceEnvironment, instance_config
    ) -> None:
        """Create Docker containers and network."""
        if instance_config.deployment.type.value != "docker":
            return

        await self._docker_repository.create_network(f"net_{instance_name}")

        docker_config = self._docker_orchestrator.build_docker_compose_config(
            instance_env, instance_config
        )

        await self._docker_repository.create_containers(instance_name, docker_config)

    async def _start_web_container_for_install(self, instance_name: str) -> None:
        """Temporarily start web container to install Python dependencies."""
        docker_info = await self._instance_repository.get_docker_info(instance_name)

        if not docker_info or not docker_info.web_container:
            raise InstanceOperationException(
                f"Web container not found for instance '{instance_name}'",
                instance_name,
            )

        # Start only web container (DB not needed for pip install)
        await self._docker_repository.start_containers(docker_info.web_container.name)

        # Give container a moment to fully start (5 seconds for Odoo to initialize)
        await asyncio.sleep(5)

    async def _stop_web_container_after_install(self, instance_name: str) -> None:
        """Stop web container after installing Python dependencies."""
        docker_info = await self._instance_repository.get_docker_info(instance_name)

        if docker_info and docker_info.web_container:
            await self._docker_repository.stop_containers(
                docker_info.web_container.name
            )
