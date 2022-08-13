import datetime
import hashlib
import logging
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pprint import pprint

import appdirs
import click
import toml
from pydantic import BaseModel, BaseSettings

# Default directories
app_dir_settings = {"appname": "note-template"}
_CONFIG_DIR = appdirs.user_config_dir(**app_dir_settings)
_DATA_DIR = appdirs.user_data_dir(**app_dir_settings)
_CACHE_DIR = appdirs.user_cache_dir(**app_dir_settings)
_STATE_DIR = appdirs.user_state_dir(**app_dir_settings)
_LOG_DIR = appdirs.user_log_dir(**app_dir_settings)
_TEMPLATES_DIR = os.path.join(_STATE_DIR, "default_templates_dir")
_NOTES_DIR = os.path.join(_STATE_DIR, "default_notes_dir")
_CONFIG_FILE_PATH = os.environ.get(
    "NOTE_TEMPLATE_CONFIG_FILE", os.path.join(_CONFIG_DIR, "config.toml")
)

logger = logging.getLogger(__name__)


class Config(BaseSettings):
    debug: bool = False
    verbose: bool = False
    data_dir: str = _DATA_DIR
    config_dir: str = _CONFIG_DIR
    state_dir: str = _STATE_DIR
    cache_dir: str = _CACHE_DIR
    log_dir: str = _LOG_DIR
    templates_dir: str = _TEMPLATES_DIR
    notes_dir: str = _NOTES_DIR
    create_default_directories: bool = True
    dont_save_note_if_no_changes: bool = True
    editor: str = os.environ.get("EDITOR", "vim")

    class Config:
        env_prefix = "NOTE_TEMPLATE_CONFIG_"


def generate_default_config(filename):
    if not os.path.exists(_CONFIG_DIR):
        os.makedirs(_CONFIG_DIR)
    config = Config().dict()
    with open(filename, "w", encoding="utf-8") as file:
        toml.dump(config, file)
    print(os.path.abspath(filename))


def file_name_without_extension(filename: str) -> str:
    result = re.search("^.*(?=\.[^\.]*$)", filename)
    if result:
        return result.group()
    return filename


def get_template_file_path(config, template_name):
    for file in os.scandir(config.templates_dir):
        os.path.isfile(file.path)
        if (
            template_name == file_name_without_extension(file.name)
            or template_name == file.name
        ):
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


def filter_dictionary(dictionary) -> dict:
    result = {}
    for key, val in dictionary.items():
        if val is not None:
            result.update({key: val})
    return result


def read_config_file():
    if os.path.exists(_CONFIG_FILE_PATH):
        data = None
        with open(_CONFIG_FILE_PATH, "r") as file:
            data = toml.load(file)
        return data
    return {}


@click.group()
@click.option("--data-dir", type=str, required=False, help="Data directory.")
@click.option("--config-dir", type=str, required=False, help="Config directory.")
@click.option("--cache-dir", type=str, required=False, help="Cache directory.")
@click.option("--state-dir", type=str, required=False, help="State directory.")
@click.option("--log-dir", type=str, required=False, help="Log directory.")
@click.option("--verbose/--no-verbose", help="Show additional information.")
@click.option("--debug/--no-debug", help="Show debug information.")
@click.option("--templates-dir", type=str, required=False, help="Templates directory.")
@click.option("--notes-dir", type=str, required=False, help="Notes directory.")
@click.option("--editor", type=str, required=False, help="Text editor.")
@click.option("--create-default-directories", type=bool, required=False)
@click.option("--dont-save-note-if-no-changes", type=bool, required=False)
@click.pass_context
def commands(context, **kwargs):
    config_kwargs = read_config_file()
    config_kwargs.update(filter_dictionary(kwargs))
    config = Config(**config_kwargs)
    context.obj = config
    check_directory(config.templates_dir, create=True)
    check_directory(config.notes_dir, create=True)
    if kwargs["debug"]:
        logger.setLevel(level=logging.DEBUG)
        logging.basicConfig(level=logging.DEBUG)
        pprint(context.obj)


@commands.command("new")
@click.argument("template", nargs=-1, required=True)
@click.pass_context
def new_note(context, template):
    config = context.obj
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


@commands.group()
@click.pass_context
def templates(context):
    return


@templates.command("list")
@click.pass_context
def templates_list(context):
    config = context.obj
    for template in os.scandir(config.templates_dir):
        print(file_name_without_extension(template.name))


@templates.command("edit")
@click.argument("template", nargs=-1, type=str)
@click.pass_context
def new_template(context, template):
    config = context.obj
    for template_name in template:
        template_file_path = os.path.join(config.templates_dir, template_name)
        subprocess.call([config.editor, template_file_path])


@templates.command("remove")
@click.argument("template", nargs=-1, type=str)
@click.pass_context
def remove_template(context, template):
    config = context.obj
    for template_name in template:
        file_path = get_template_file_path(config, template_name)
        os.remove(file_path)


@commands.group("config")
@click.pass_context
def config_commands(context):
    return


@config_commands.command("generate")
@click.argument("filename", default=_CONFIG_FILE_PATH)
@click.pass_context
def generate_config(context, filename):
    generate_default_config(filename)


@config_commands.command("show")
@click.pass_context
def show_config(context):
    config_data = read_config_file()
    pprint(config_data)




if __name__ == "__main__":
    commands()
