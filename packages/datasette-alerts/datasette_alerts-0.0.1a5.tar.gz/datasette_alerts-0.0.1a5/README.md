# datasette-alerts

[![PyPI](https://img.shields.io/pypi/v/datasette-alerts.svg)](https://pypi.org/project/datasette-alerts/)
[![Changelog](https://img.shields.io/github/v/release/datasette/datasette-alerts?include_prereleases&label=changelog)](https://github.com/datasette/datasette-alerts/releases)
[![Tests](https://github.com/datasette/datasette-alerts/actions/workflows/test.yml/badge.svg)](https://github.com/datasette/datasette-alerts/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/datasette/datasette-alerts/blob/main/LICENSE)

Setup alerts on specfic new records.

## Installation

Install this plugin in the same environment as Datasette.
```bash
datasette install datasette-alerts
```
## Usage

Usage instructions go here.

## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:
```bash
cd datasette-alerts
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
pip install -e '.[test]'
```
To run the tests:
```bash
python -m pytest
```
