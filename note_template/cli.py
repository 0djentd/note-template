import logging
import os
import shutil
import re
import datetime
import sys
import subprocess
import hashlib

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
    cache_dir: str
    log_dir: str
    templates_dir: str
    notes_dir: str
    create_default_directories: bool
    dont_save_note_if_no_changes: bool
    editor: str


def file_name_without_extension(filename: str) -> str:
    result = re.search("^.*(?=\.[^\.]*$)", filename)
    if result:
        return result.group()
    return filename


def get_template_file_path(config, template_name):
    for file in os.scandir(config.templates_dir):
        os.path.isfile(file.path)
        if template_name == file_name_without_extension(file.name)\
                or template_name == file.name:
            return file.path
    filename = os.path.join(config.templates_dir, template_name)
    raise FileNotFoundError(filename)


def check_directory(directory: str, create: bool) -> None:
    if os.path.exists(directory):
        if os.path.isdir(directory):
            return
    if create:
        os.makedirs(directory)
    else:
        raise FileNotFoundError(directory)


def file_hash(file_path) -> str:
    hashfunc = hashlib.sha512()
    with open(file_path, "rb") as file:
        hashfunc.update(file.read())
    return hashfunc.hexdigest()


@click.command()
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
@click.option("--editor", type=str, default=_EDITOR,
              help="Text editor.")
@click.option("--create-default-directories", default=True)
@click.option("--dont-save-note-if-no-changes", default=True)
@click.pass_context
def commands(context, template, **kwargs):
    config = Config(**kwargs)
    context.obj = config
    check_directory(config.templates_dir, create=True)
    check_directory(config.notes_dir, create=True)
    if kwargs["debug"]:
        logger.setLevel(level=logging.DEBUG)
        logging.basicConfig(level=logging.DEBUG)
        pprint(context.obj)
    for note_template in template:
        template_file_path = get_template_file_path(config, note_template)
        note_type_dir = os.path.join(config.notes_dir, note_template)
        check_directory(note_type_dir, create=True)
        note_file_name = str(datetime.datetime.now().isoformat())
        note_file_path = os.path.join(note_type_dir, note_file_name)
        shutil.copyfile(template_file_path, note_file_path)
        old_file_hash = file_hash(note_file_path)
        subprocess.call([config.editor, note_file_path])
        if config.dont_save_note_if_no_changes:
            new_file_hash = file_hash(note_file_path)
            if new_file_hash == old_file_hash:
                logging.info("File not modified, removing.")
                os.remove(note_file_path)


if __name__ == "__main__":
    commands()
