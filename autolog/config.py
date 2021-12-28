"""
Parse user config
"""
import os
from configparser import ConfigParser, NoOptionError
from pathlib import Path
from typing import Dict

from dotenv import load_dotenv

from autolog.requests import validate_key


def set_env_vars(vars):
    for k, v in vars.items():
        os.environ[k] = v


def configure(project_root: Path) -> Dict:
    load_dotenv(project_root / ".env")
    config = parse_config(project_root)
    configure_api(config["local"])

    return config


def configure_api(local):
    if (not local) and (not validate_key()):
        if "AUTOLOG_API_KEY" in os.environ:
            print("AUTOLOG_API_KEY invalid. Advanced features disabled.")
            del os.environ["AUTOLOG_API_KEY"]


def parse_config(project_root: Path) -> Dict:
    load_dotenv(project_root / ".env")

    DEFAULT_VARS = {
        "AUTOLOG_PROJECT_NAME": project_root.stem,
        "AUTOLOG_RUN_LOCALLY": "false",
    }

    DEFAULT_CONFIG = {
        "changelog_name": "CHANGELOG.md",
        "local": False,
    }

    config_file = project_root / "pyproject.toml"

    if not config_file.exists():
        set_env_vars(DEFAULT_VARS)
        return DEFAULT_CONFIG

    config = ConfigParser()
    config.read(config_file)

    if not config.has_section("tool.autolog"):
        set_env_vars(DEFAULT_VARS)
        return DEFAULT_CONFIG

    # Environment variables
    try:
        project_name = config.get("tool.autolog", "project").strip("'").strip('"')
    except NoOptionError:
        project_name = DEFAULT_VARS["AUTOLOG_PROJECT_NAME"]

    try:
        local = config.getboolean("tool.autolog", "local")
    except (NoOptionError, ValueError):
        local = False

    if "AUTOLOG_API_KEY" not in os.environ:
        print(
            "Environment variable AUTOLOG_API_KEY not set. Advanced features disabled."
        )

    os.environ["AUTOLOG_PROJECT_NAME"] = project_name
    os.environ["AUTOLOG_RUN_LOCALLY"] = str(local)

    # Config values
    try:
        changelog_name = config.get("tool.autolog", "changelog").strip("'").strip('"')
    except NoOptionError:
        changelog_name = DEFAULT_CONFIG["changelog_name"]

    if not changelog_name.endswith(".md"):
        changelog_name += ".md"

    return {"changelog_name": changelog_name, "local": local}
