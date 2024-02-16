import os.path

from dynaconf import Dynaconf, LazySettings

WORKDIR = os.path.dirname(os.path.abspath(__file__))

settings: LazySettings = Dynaconf(
    settings_files=[
        os.path.join(WORKDIR, "settings.toml"),
        os.path.join(WORKDIR, ".secrets.toml"),
    ],
    environments=True,
    ENVVAR_PREFIX_FOR_DYNACONF=False,
)
""" `settings_files` = Load these files in the order."""
