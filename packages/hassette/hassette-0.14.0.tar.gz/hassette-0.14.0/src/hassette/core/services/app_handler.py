import asyncio
import typing
from collections import defaultdict
from copy import deepcopy
from logging import getLogger
from pathlib import Path
from timeit import default_timer as timer

import anyio
from deepdiff import DeepDiff
from humanize import precisedelta

from hassette.core.resources.app.app import App
from hassette.core.resources.base import Resource
from hassette.core.resources.bus.bus import Bus
from hassette.enums import ResourceStatus
from hassette.events.hassette import HassetteEmptyPayload
from hassette.exceptions import InvalidInheritanceError, UndefinedUserConfigError
from hassette.topics import HASSETTE_EVENT_APP_LOAD_COMPLETED, HASSETTE_EVENT_FILE_WATCHER
from hassette.utils.app_utils import load_app_class

if typing.TYPE_CHECKING:
    from hassette import AppConfig, Hassette
    from hassette.config.app_manifest import AppManifest
    from hassette.events import HassetteFileWatcherEvent

LOGGER = getLogger(__name__)
LOADED_CLASSES: "dict[tuple[str, str], type[App[AppConfig]]]" = {}
ROOT_PATH = "root"
USER_CONFIG_PATH = "user_config"


class _AppHandler(Resource):  # pyright: ignore[reportUnusedClass]
    """Manages the lifecycle of apps in Hassette.

    - Deterministic storage: apps[app_name][index] -> App
    - Tracks per-app failures in failed_apps for observability
    """

    # TODO:
    # need to separate startup of app handler from initialization of apps
    # so that we can start the app handler, then the API, then initialize apps
    # because apps may want to use the API during startup
    # could trigger on websocket connected event, with a once=True handler?

    # TODO: handle stopping/starting individual app instances, instead of all apps of a class/key
    # no need to restart app index 2 if only app index 0 changed, etc.

    # TODO: clean this class up - it likely needs to be split into smaller pieces

    apps_config: dict[str, "AppManifest"]
    """Copy of Hassette's config apps"""

    apps: dict[str, dict[int, App["AppConfig"]]]
    """Running apps"""

    failed_apps: dict[str, list[tuple[int, Exception]]]
    """Apps we could not start/failed to start"""

    only_app: str | None
    """If set, only this app will be started (the one marked as only)"""

    bus: Bus
    """Event bus for inter-service communication."""

    @classmethod
    def create(cls, hassette: "Hassette"):
        inst = cls(hassette, parent=hassette)
        inst.apps_config = {}
        inst.set_apps_configs(hassette.config.apps)
        inst.only_app = None
        inst.apps = defaultdict(dict)
        inst.failed_apps = defaultdict(list)
        inst.bus = inst.add_child(Bus)
        return inst

    @property
    def config_log_level(self):
        """Return the log level from the config for this resource."""
        return self.hassette.config.app_handler_log_level

    def set_apps_configs(self, apps_config: dict[str, "AppManifest"]) -> None:
        """Set the apps configuration.

        Args:
            apps_config (dict[str, AppManifest]): The new apps configuration.
        """
        self.logger.debug("Setting apps configuration")
        self.apps_config = deepcopy(apps_config)
        self.only_app = None  # reset only_app, will be recomputed on next initialize

        self.logger.debug("Found %d apps in configuration: %s", len(self.apps_config), list(self.apps_config.keys()))

    @property
    def active_apps_config(self) -> dict[str, "AppManifest"]:
        """Apps that are enabled."""
        enabled_apps = {k: v for k, v in self.apps_config.items() if v.enabled}
        if self.only_app:
            enabled_apps = {k: v for k, v in enabled_apps.items() if k == self.only_app}
        return enabled_apps

    async def on_initialize(self) -> None:
        """Start handler and initialize configured apps."""
        if self.hassette.config.dev_mode or self.hassette.config.allow_reload_in_prod:
            if self.hassette.config.allow_reload_in_prod:
                self.logger.warning("Allowing app reloads in production mode due to config")
            self.bus.on(topic=HASSETTE_EVENT_FILE_WATCHER, handler=self.handle_change_event)
        else:
            self.logger.warning("Not watching for app changes, dev_mode is disabled")

        await self.hassette.wait_for_ready(self.hassette._websocket)
        self.mark_ready("initialized")

    async def after_initialize(self) -> None:
        self.logger.debug("Scheduling app initialization")
        self.task_bucket.spawn(self.initialize_apps())

    async def on_shutdown(self) -> None:
        """Shutdown all app instances gracefully."""
        self.logger.debug("Stopping '%s' %s", self.class_name, self.role)
        self.mark_not_ready(reason="shutting-down")

        self.bus.remove_all_listeners()

        # Flatten and iterate
        for instances in list(self.apps.values()):
            for inst in list(instances.values()):
                try:
                    with anyio.fail_after(self.hassette.config.app_shutdown_timeout_seconds):
                        await inst.shutdown()

                        # in case the app does not call its own cleanup
                        # which is honestly a better user experience
                        await inst.cleanup()
                    self.logger.debug("App %s shutdown successfully", inst.app_config.instance_name)
                except Exception:
                    self.logger.exception("Failed to shutdown app %s", inst.app_config.instance_name)

        self.apps.clear()
        self.failed_apps.clear()

    def get(self, app_key: str, index: int = 0) -> "App[AppConfig] | None":
        """Get a specific app instance if running."""
        return self.apps.get(app_key, {}).get(index)

    def all(self) -> list["App[AppConfig]"]:
        """All running app instances."""
        return [inst for group in self.apps.values() for inst in group.values()]

    async def initialize_apps(self) -> None:
        """Initialize all configured and enabled apps, called at AppHandler startup."""

        if not self.apps_config:
            self.logger.debug("No apps configured, skipping initialization")
            return

        if not await self.hassette.wait_for_ready(
            [
                self.hassette._websocket,
                self.hassette._api_service,
                self.hassette._bus_service,
                self.hassette._scheduler_service,
            ]
        ):
            self.logger.warning("Dependencies never became ready; skipping app startup")
            return

        try:
            tasks = await self._initialize_apps()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    self.logger.exception("Error during app initialization: %s", result)
            if not self.apps:
                self.logger.warning("No apps were initialized successfully")
            else:
                self.logger.info("Initialized %d apps", sum(len(v) for v in self.apps.values()))

            await self.hassette.send_event(
                HASSETTE_EVENT_APP_LOAD_COMPLETED,
                HassetteEmptyPayload.create_event(topic=HASSETTE_EVENT_APP_LOAD_COMPLETED),
            )
        except Exception as e:
            self.logger.exception("Failed to initialize apps")
            await self.handle_crash(e)
            raise

    async def _set_only_app(self):
        """Determine if any app is marked as only, and set self.only_app accordingly."""

        if not self.hassette.config.dev_mode:
            if not self.hassette.config.allow_only_app_in_prod:
                self.logger.warning("Disallowing use of `only_app` decorator in production mode")
                self.only_app = None
                return
            self.logger.warning("Allowing use of `only_app` decorator in production mode due to config")

        only_apps: list[str] = []
        for app_manifest in self.active_apps_config.values():
            try:
                app_class = load_app_class(app_manifest)
                if app_class._only_app:
                    only_apps.append(app_manifest.app_key)
            except (UndefinedUserConfigError, InvalidInheritanceError):
                self.logger.error(
                    "Failed to load app %s due to bad configuration - check previous logs for details",
                    app_manifest.display_name,
                )
            except Exception:
                self.logger.exception("Failed to load app class for %s", app_manifest.display_name)

        if not only_apps:
            self.only_app = None
            return

        if len(only_apps) > 1:
            keys = ", ".join(app for app in only_apps)
            raise RuntimeError(f"Multiple apps marked as only: {keys}")

        self.only_app = only_apps[0]
        self.logger.warning("App %s is marked as only, skipping all others", self.only_app)

    async def _initialize_apps(self, apps: set[str] | None = None) -> list[asyncio.Task]:
        """Initialize all or a subset of apps by key. If apps is None, initialize all enabled apps."""

        tasks: list[asyncio.Task] = []
        await self._set_only_app()

        apps = apps if apps is not None else set(self.active_apps_config.keys())

        for app_key in apps:
            app_manifest = self.active_apps_config.get(app_key)
            if not app_manifest:
                self.logger.debug("Skipping disabled or unknown app %s", app_key)
                continue
            try:
                self._create_app_instances(app_key, app_manifest)
            except (UndefinedUserConfigError, InvalidInheritanceError):
                self.logger.error(
                    "Failed to load app %s due to bad configuration - check previous logs for details", app_key
                )
                continue
            except Exception:
                self.logger.exception("Failed to load app class for %s", app_key)
                continue

            tasks.append(self.task_bucket.spawn(self._initialize_app_instances(app_key, app_manifest)))

        return tasks

    def _create_app_instances(self, app_key: str, app_manifest: "AppManifest", force_reload: bool = False) -> None:
        """Create app instances from a manifest, validating config.

        Args:
            app_key (str): The key of the app, as found in hassette.toml.
            app_manifest (AppManifest): The manifest containing configuration.
        """
        try:
            app_class = load_app_class(app_manifest, force_reload=force_reload)
        except Exception as e:
            self.logger.exception("Failed to load app class for %s", app_key)
            self.failed_apps[app_key].append((0, e))
            return

        class_name = app_class.__name__
        app_class.app_manifest = app_manifest
        app_configs = app_manifest.app_config

        # toml data can be a dict or a list of dicts, but AppManifest should handle conversion for us
        if not isinstance(app_configs, list):
            raise ValueError(f"App {app_key} config is not a list, found {type(app_configs)}")

        for idx, config in enumerate(app_configs):
            instance_name = config.get("instance_name")
            if not instance_name:
                raise ValueError(f"App {app_key} instance {idx} is missing instance_name")
            try:
                validated = app_class.app_config_cls.model_validate(config)
                app_instance = app_class.create(hassette=self.hassette, app_config=validated, index=idx)
                self.apps[app_key][idx] = app_instance
            except Exception as e:
                self.logger.exception("Failed to validate/init config for %s (%s)", instance_name, class_name)
                self.failed_apps[app_key].append((idx, e))
                continue

    async def _initialize_app_instances(self, app_key: str, app_manifest: "AppManifest") -> None:
        """Initialize all instances of a given app_key.

        Args:
            app_key (str): The key of the app, as found in hassette.toml.
          app_manifest (AppManifest): The manifest containing configuration.
        """

        class_name = app_manifest.class_name
        for idx, inst in self.apps.get(app_key, {}).items():
            try:
                with anyio.fail_after(self.hassette.config.app_startup_timeout_seconds):
                    await inst.initialize()
                    inst.mark_ready(reason="initialized")
                self.logger.debug("App '%s' (%s) initialized successfully", inst.app_config.instance_name, class_name)
            except TimeoutError as e:
                self.logger.exception(
                    "Timed out while starting app '%s' (%s)", inst.app_config.instance_name, class_name
                )
                inst.status = ResourceStatus.STOPPED
                self.failed_apps[app_key].append((idx, e))
            except Exception as e:
                self.logger.exception("Failed to start app '%s' (%s)", inst.app_config.instance_name, class_name)
                inst.status = ResourceStatus.STOPPED
                self.failed_apps[app_key].append((idx, e))

    async def handle_change_event(self, event: "HassetteFileWatcherEvent") -> None:
        """Handle changes detected by the watcher."""
        await self.handle_changes(event.payload.data.changed_file_path)

    async def refresh_config(self) -> tuple[dict[str, "AppManifest"], dict[str, "AppManifest"]]:
        """Reload the configuration and return (original_apps_config, current_apps_config)."""
        original_apps_config = deepcopy(self.active_apps_config)

        # Reinitialize config to pick up changes.
        # https://docs.pydantic.dev/latest/concepts/pydantic_settings/#in-place-reloading
        try:
            self.hassette.config.__init__()
        except Exception as e:
            self.logger.exception("Failed to reload configuration: %s", e)

        self.set_apps_configs(self.hassette.config.apps)
        curr_apps_config = deepcopy(self.active_apps_config)

        return original_apps_config, curr_apps_config

    async def handle_changes(self, changed_file_path: Path | None = None) -> None:
        """Handle changes detected by the watcher."""

        original_apps_config, curr_apps_config = await self.refresh_config()

        # recalculate only_app in case it changed
        await self._set_only_app()

        orphans, new_apps, reimport_apps, reload_apps = self._calculate_app_changes(
            original_apps_config, curr_apps_config, changed_file_path
        )
        self.logger.debug(
            "App changes detected - orphans: %s, new: %s, reimport: %s, reload: %s",
            orphans,
            new_apps,
            reimport_apps,
            reload_apps,
        )
        await self._handle_removed_apps(orphans)
        await self._handle_new_apps(new_apps)
        await self._reload_apps_due_to_file_change(reimport_apps)
        await self._reload_apps_due_to_config(reload_apps)

        await self.hassette.send_event(
            HASSETTE_EVENT_APP_LOAD_COMPLETED,
            HassetteEmptyPayload.create_event(topic=HASSETTE_EVENT_APP_LOAD_COMPLETED),
        )

    def _calculate_app_changes(
        self,
        original_apps_config: dict[str, "AppManifest"],
        curr_apps_config: dict[str, "AppManifest"],
        changed_path: Path | None,
    ) -> tuple[set[str], set[str], set[str], set[str]]:
        """Return 4 sets of app keys: (orphans, new_apps, reimport_apps, reload_apps).

        Args:
            original_apps_config (dict[str, AppManifest]): The original apps configuration.
            curr_apps_config (dict[str, AppManifest]): The current apps configuration.
            changed_path (Path | None): The path of the file that changed, if any.

        Returns:
            tuple[set[str], set[str], set[str], set[str]]: A tuple containing four sets:
                - orphans: Apps that were removed from the configuration.
                - new_apps: Apps that were added to the configuration.
                - reimport_apps: Apps that need to be reimported due to file changes.
                - reload_apps: Apps that need to be reloaded due to configuration changes.
        """

        config_diff = DeepDiff(
            original_apps_config, curr_apps_config, ignore_order=True, include_paths=[ROOT_PATH, USER_CONFIG_PATH]
        )

        original_app_keys = set(original_apps_config.keys())
        curr_app_keys = set(curr_apps_config.keys())
        if self.only_app:
            curr_app_keys = {k for k in curr_app_keys if k == self.only_app}

        orphans = original_app_keys - curr_app_keys
        new_apps = curr_app_keys - original_app_keys

        reimport_apps = {app.app_key for app in curr_apps_config.values() if app.get_full_path() == changed_path}

        reload_apps = {
            app_key
            for app_key in config_diff.affected_root_keys
            if app_key not in new_apps and app_key not in orphans and app_key not in reimport_apps
        }

        return orphans, new_apps, reimport_apps, reload_apps

    async def _handle_removed_apps(self, orphans: set[str]) -> None:
        if not orphans:
            return

        self.logger.debug("Apps removed from config: %s", orphans)

        self.logger.debug("Stopping %d orphaned apps: %s", len(orphans), orphans)
        for app_key in orphans:
            self.logger.debug("Stopping orphaned app %s", app_key)
            try:
                await self.stop_app(app_key)
            except Exception:
                self.logger.exception("Failed to stop orphaned app %s", app_key)

    async def _reload_apps_due_to_file_change(self, apps: set[str]) -> None:
        if not apps:
            return

        self.logger.debug("Apps to reimport due to file change: %s", apps)
        for app_key in apps:
            await self.reload_app(app_key, force_reload=True)

    async def _reload_apps_due_to_config(self, apps: set[str]) -> None:
        if not apps:
            return

        self.logger.debug("Apps to reload due to config changes: %s", apps)
        for app_key in apps:
            await self.reload_app(app_key)

    async def stop_app(self, app_key: str) -> None:
        """Stop and remove all instances for a given app_name."""
        instances = self.apps.pop(app_key, None)
        if not instances:
            self.logger.warning("Cannot stop app %s, not found", app_key)
            return
        self.logger.debug("Stopping %d instances of %s", len(instances), app_key)

        for inst in instances.values():
            try:
                start_time = timer()
                with anyio.fail_after(self.hassette.config.app_shutdown_timeout_seconds):
                    await inst.shutdown()

                end_time = timer()
                friendly_time = precisedelta(end_time - start_time, minimum_unit="milliseconds")
                self.logger.debug("Stopped app '%s' in %s", inst.app_config.instance_name, friendly_time)

            except Exception:
                self.logger.exception(
                    "Failed to stop app '%s' after %s seconds",
                    inst.app_config.instance_name,
                    self.hassette.config.app_shutdown_timeout_seconds,
                )

    async def _handle_new_apps(self, apps: set[str]) -> None:
        """Start any apps that are in config but not currently running."""
        if not apps:
            return

        self.logger.debug("Starting %d new apps: %s", len(apps), list(apps))
        try:
            await self._initialize_apps(apps)
        except Exception:
            self.logger.exception("Failed to start new apps")

    async def reload_app(self, app_key: str, force_reload: bool = False) -> None:
        """Stop and reinitialize a single app by key (based on current config)."""
        self.logger.debug("Reloading app %s", app_key)
        try:
            await self.stop_app(app_key)
            # Initialize only that app from the current config if present and enabled
            manifest = self.active_apps_config.get(app_key)
            if not manifest:
                if manifest := self.apps_config.get(app_key):
                    self.logger.warning("Cannot reload app %s, not enabled", app_key)
                    return
                self.logger.warning("Cannot reload app %s, not found", app_key)
                return

            assert manifest is not None, "Manifest should not be None"

            self._create_app_instances(app_key, manifest, force_reload=force_reload)
            await self._initialize_app_instances(app_key, manifest)
        except Exception:
            self.logger.exception("Failed to reload app %s", app_key)
