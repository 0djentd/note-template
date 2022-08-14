![PyPI](https://img.shields.io/pypi/v/note-template)
![GitHub release (latest SemVer including pre-releases)](https://img.shields.io/github/v/release/0djentd/note-template?include_prereleases)
![GitHub all releases](https://img.shields.io/github/downloads/0djentd/note-template/total)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/note-template)

![GitHub issues](https://img.shields.io/github/issues/0djentd/note-template)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/0djentd/note-template)
![GitHub Repo stars](https://img.shields.io/github/stars/0djentd/note-template?style=social)

[![Python package](https://github.com/0djentd/note-template/actions/workflows/python-package.yml/badge.svg)](https://github.com/0djentd/note-template/actions/workflows/python-package.yml)
[![Pylint](https://github.com/0djentd/note-template/actions/workflows/pylint.yml/badge.svg)](https://github.com/0djentd/note-template/actions/workflows/pylint.yml)

# note-template
## Description
Simple CLI tool to create notes using templates.

## How to use
```
Usage: note-template [OPTIONS] COMMAND [ARGS]...

Options:
  --data-dir TEXT                 Data directory.
  --config-dir TEXT               Config directory.
  --cache-dir TEXT                Cache directory.
  --state-dir TEXT                State directory.
  --log-dir TEXT                  Log directory.
  --verbose / --no-verbose        Show additional information.
  --debug / --no-debug            Show debug information.
  --templates-dir TEXT            Templates directory.
  --notes-dir TEXT                Notes directory.
  --editor TEXT                   Text editor.
  --create-default-directories BOOLEAN
  --dont-save-note-if-no-changes BOOLEAN
  --help                          Show this message and exit.

Commands:
  config
  new
  templates
```
