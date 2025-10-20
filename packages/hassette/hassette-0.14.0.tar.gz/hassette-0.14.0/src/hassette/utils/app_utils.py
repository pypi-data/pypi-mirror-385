import importlib.machinery
import importlib.util
import sys
import traceback
import typing
from logging import getLogger
from pathlib import Path

from hassette.core import context
from hassette.core.resources.app.app import App, AppSync
from hassette.exceptions import (
    AppPrecheckFailedError,
    CannotOverrideFinalError,
    InvalidInheritanceError,
    UndefinedUserConfigError,
)

if typing.TYPE_CHECKING:
    from hassette import AppConfig, HassetteConfig
    from hassette.config.app_manifest import AppManifest

LOGGER = getLogger(__name__)
LOADED_CLASSES: "dict[tuple[str, str], type[App[AppConfig]]]" = {}


EXCLUDED_PATH_PARTS = ("site-packages", "importlib")


def run_apps_pre_check(config: "HassetteConfig") -> None:
    """Pre-check all apps to ensure they can be loaded correctly.

    This prevents us from spinning up the whole system and then having apps fail to load
    due to import errors, misconfiguration, etc.

    Args:
        config (HassetteConfig): The Hassette configuration containing app manifests.

    Raises:
        AppPrecheckFailedError: If any app fails to load correctly.
    """

    def _root_cause(exc: BaseException) -> BaseException:
        """Prefer __cause__ (explicit raise ... from ...), else __context__."""
        err = exc
        while getattr(err, "__cause__", None) is not None:
            err = err.__cause__  # pyright: ignore[reportOptionalMemberAccess]
        if getattr(err, "__cause__", None) is None and getattr(err, "__context__", None) is not None:
            err = err.__context__  # pyright: ignore[reportOptionalMemberAccess]

        if typing.TYPE_CHECKING:
            assert isinstance(err, BaseException)

        return err

    def _find_user_frame(exc: BaseException, app_dir: Path) -> traceback.FrameSummary | None:
        """
        Pick the most useful traceback frame:
        1) last frame inside the app's directory
        2) last frame not in site-packages/importlib/hassette
        3) final frame of the traceback
        """
        try:
            err = _root_cause(exc)
            tb_list = traceback.extract_tb(err.__traceback__)
            if not tb_list:
                return None

            app_dir_str = app_dir.as_posix()

            # 1) prefer frames inside the app dir
            for fr in reversed(tb_list):
                if fr.filename.replace("\\", "/").startswith(app_dir_str):
                    return fr

            # 2) otherwise prefer frames that aren't obviously noise
            for fr in reversed(tb_list):
                fn = fr.filename
                if "hassette" not in fn and not any(part in fn for part in EXCLUDED_PATH_PARTS):
                    return fr

            # 3) fallback: last frame
            return tb_list[-1]

        except Exception:
            # Ultra-defensive: never let error formatting throw
            LOGGER.error("Error selecting user frame: %s", traceback.format_exc(limit=1))
            return None

    def _log_compact_load_error(app_manifest: "AppManifest", exc: BaseException) -> None:
        fr = _find_user_frame(exc, app_manifest.app_dir)
        if fr:
            msg = "Failed to load app %s: %s '%s' (at %s:%d)"
            LOGGER.error(msg, app_manifest.display_name, type(exc).__name__, str(exc), fr.filename, fr.lineno)
        else:
            LOGGER.error("Failed to load app %s: %s ('%s')", app_manifest.display_name, type(exc).__name__, str(exc))

    ### actual precheck code starts here ###

    had_errors = False

    for app_manifest in config.apps.values():
        if not app_manifest.enabled:
            continue

        try:
            load_app_class(app_manifest)

        except CannotOverrideFinalError as e:
            # Already a great, app-aware message
            LOGGER.error("App %s: %s", app_manifest.display_name, e)
            had_errors = True

        except (UndefinedUserConfigError, InvalidInheritanceError):
            LOGGER.error(
                "Failed to load app %s due to bad configuration — check previous logs for details",
                app_manifest.display_name,
            )
            had_errors = True

        except Exception as e:
            _log_compact_load_error(app_manifest, e)
            had_errors = True

    if had_errors:
        raise AppPrecheckFailedError("At least one app failed to load — see previous logs for details")


def load_app_class(app_manifest: "AppManifest", force_reload: bool = False) -> "type[App[AppConfig]]":
    """Import the app's class with a canonical package/module identity so isinstance works.

    Args:
        app_manifest (AppManifest): The app manifest containing configuration.

    Returns:
        type[App]: The app class.
    """
    module_path = app_manifest.get_full_path()
    class_name = app_manifest.class_name

    # cache keyed by (absolute file path, class name)
    cache_key = (str(module_path), class_name)

    if force_reload and cache_key in LOADED_CLASSES:
        LOGGER.info("Forcing reload of app class %s from %s", class_name, module_path)
        del LOADED_CLASSES[cache_key]

    if cache_key in LOADED_CLASSES:
        return LOADED_CLASSES[cache_key]

    if not module_path or not class_name:
        raise ValueError(f"App {app_manifest.display_name} is missing filename or class_name")

    config = context.HASSETTE_CONFIG.get(None)
    if not config:
        raise RuntimeError("HassetteConfig is not available in context")
    pkg_name = config.app_dir.name
    _ensure_on_sys_path(app_manifest.app_dir)
    _ensure_on_sys_path(app_manifest.app_dir.parent)

    # 1) Ensure 'apps' is a namespace package pointing at app_config.app_dir
    _ensure_namespace_package(app_manifest.app_dir, pkg_name)

    # 2) Compute canonical module name from relative path under app_dir
    mod_name = _module_name_for(app_manifest.app_dir, module_path, pkg_name)

    # 3) Import or reload the module by canonical name
    if mod_name in sys.modules:  # noqa: SIM108
        module = importlib.reload(sys.modules[mod_name])
    else:
        module = importlib.import_module(mod_name)

    try:
        app_class = getattr(module, class_name)
    except AttributeError:
        raise AttributeError(f"Class {class_name} not found in module {mod_name} ({module_path})") from None

    if not issubclass(app_class, App | AppSync):
        raise TypeError(f"Class {class_name} is not a subclass of App or AppSync")

    if app_class._import_exception:
        raise app_class._import_exception  # surface subclass init errors

    LOADED_CLASSES[cache_key] = app_class
    return app_class


def _ensure_namespace_package(root: Path, pkg_name: str) -> None:
    """Ensure a namespace package rooted at `root` is importable as `pkg_name`.

    Args:
      root (Path): Directory to treat as the root of the namespace package.
      pkg_name (str): The package name to use (e.g. 'apps')

    Returns:
      None

    - Creates/updates sys.modules[pkg_name] as a namespace package.
    - Adds `root` to submodule_search_locations so 'pkg_name.*' resolves under this directory.
    """

    root = root.resolve()
    if pkg_name in sys.modules and hasattr(sys.modules[pkg_name], "__path__"):
        ns_pkg = sys.modules[pkg_name]
        # extend search locations if necessary
        if str(root) not in ns_pkg.__path__:
            ns_pkg.__path__.append(str(root))
        return

    # Synthesize a namespace package
    spec = importlib.machinery.ModuleSpec(pkg_name, loader=None, is_package=True)
    ns_pkg = importlib.util.module_from_spec(spec)
    ns_pkg.__path__ = [str(root)]
    sys.modules[pkg_name] = ns_pkg


def _module_name_for(app_dir: Path, full_path: Path, pkg_name: str) -> str:
    """
    Map a file within app_dir to a stable module name under the 'apps' package.

    Args:
      app_dir (Path): The root directory containing apps (e.g. /path/to/apps)
      full_path (Path): The full path to the app module file (e.g. /path/to/apps/my_app.py)
      pkg_name (str): The package name to use (e.g. 'apps')

    Returns:
      str: The dotted module name (e.g. 'apps.my_app')

    Examples:
      app_dir=/path/to/apps
        /path/to/apps/my_app.py         -> apps.my_app
        /path/to/apps/notifications/email_digest.py -> apps.notifications.email_digest
    """
    app_dir = app_dir.resolve()
    full_path = full_path.resolve()
    rel = full_path.relative_to(app_dir).with_suffix("")  # drop .py
    parts = list(rel.parts)
    return ".".join([pkg_name, *parts])


def _ensure_on_sys_path(p: Path) -> None:
    """Ensure the given path is on sys.path for module resolution.

    Args:
      p (Path): Directory to add to sys.path

    Note:
      - Will not add root directories (with <=1 parts) for safety.
    """

    p = p.resolve()
    if len(p.parts) <= 1:
        LOGGER.warning("Refusing to add root directory %s to sys.path", p)
        return

    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
