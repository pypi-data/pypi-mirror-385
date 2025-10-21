import importlib.util
import os
import sys

CONFIG_NAME = "settings.py"

def find_config():
    """Search for settings.py in the user's project."""
    for path in sys.path:
        config_path = os.path.join(path, CONFIG_NAME)

        if os.path.exists(config_path):
            return config_path
    return None

def load_settings():
    """Dynamically import config.py if it exists."""
    settings_path = find_config()
    if not settings_path:
        raise FileNotFoundError("Not found 'settings.py' file. Please start projects first with command 'jknife'.")

    # create a module specification for config.py with naming config
    # importlib.util.spec_from_file_location(module name, import path)
    # type = ModuleSpec
    spec = importlib.util.spec_from_file_location("settings", settings_path)

    # create an empty module class instance from specification.
    # importlib.util.module_from_spec(spec)
    settings = importlib.util.module_from_spec(spec)

    # execute an empty module
    # load and execute config.py from config
    spec.loader.exec_module(settings)

    # Inject settings into `sys.modules` as `jknife.settings`
    sys.modules["jknife.settings"] = settings
    return settings