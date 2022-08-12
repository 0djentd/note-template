import logging
import os

from dataclasses import dataclass
from pprint import pprint

import click
import appdirs


# Default directories
app_dir_settings = {"appname": "note-template"}
_CONFIG_DIR = appdirs.user_config_dir(**app_dir_settings)
_DATA_DIR = appdirs.user_data_dir(**app_dir_settings)
_CACHE_DIR = appdirs.user_cache_dir(**app_dir_settings)
_STATE_DIR = appdirs.user_state_dir(**app_dir_settings)
_LOG_DIR = appdirs.user_log_dir(**app_dir_settings)
_TEMPLATES_DIR = os.path.join(_STATE_DIR, "default_templates_dir")
_NOTES_DIR = os.path.join(_STATE_DIR, "default_notes_dir")

# Environment variables
_PREFIX = "NOTE_TEMPLATE"
_CONFIG_DIR = os.environ.get(_PREFIX + "_CONFIG_DIR", _CONFIG_DIR)
_DATA_DIR = os.environ.get(_PREFIX + "_DATA_DIR", _DATA_DIR)
_CACHE_DIR = os.environ.get(_PREFIX + "_CACHE_DIR", _CACHE_DIR)
_STATE_DIR = os.environ.get(_PREFIX + "_STATE_DIR", _STATE_DIR)
_LOG_DIR = os.environ.get(_PREFIX + "_LOG_DIR", _LOG_DIR)
_EDITOR = os.environ.get(_PREFIX + "_EDITOR", "vim")
_EDITOR = os.environ.get("EDITOR", _EDITOR)
_TEMPLATES_DIR = os.environ.get(_PREFIX + "_TEMPLATES_DIR", _TEMPLATES_DIR)
_NOTES_DIR = os.environ.get(_PREFIX + "_NOTES_DIR", _NOTES_DIR)

logger = logging.getLogger(__name__)


@dataclass
class Config:
    debug: bool
    verbose: bool
    data_dir: str
    config_dir: str
    state_dir: str
    log_dir: str
    templates_dir: str
    notes_dir: str


@click.group()
@click.argument("template", nargs=-1, required=True)
@click.option("--data-dir", type=str, default=_DATA_DIR,
              help="Data directory.")
@click.option("--config-dir", type=str, default=_CONFIG_DIR,
              help="Config directory.")
@click.option("--cache-dir", type=str, default=_CACHE_DIR,
              help="Cache directory.")
@click.option("--state-dir", type=str, default=_STATE_DIR,
              help="State directory.")
@click.option("--log-dir", type=str, default=_LOG_DIR,
              help="Log directory.")
@click.option("--verbose/--no-verbose",
              help="Show additional information.")
@click.option("--debug/--no-debug",
              help="Show debug information.")
@click.option("--templates-dir", type=str, default=_TEMPLATES_DIR,
              help="Templates directory.")
@click.option("--notes-dir", type=str, default=_NOTES_DIR,
              help="Notes directory.")
@click.pass_context
def commands(context, **kwargs):
    context.obj = Config(**kwargs)
    if kwargs["debug"]:
        logger.setLevel(level=logging.DEBUG)
        logging.basicConfig(level=logging.DEBUG)
        pprint(context.obj)


if __name__ == "__main__":
    commands()
