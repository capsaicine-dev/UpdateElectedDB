# Copyright (C) 2026 zizanibot
# See LICENSE file for extended copyright information.
# This file is part of UpdateElectedDB project from https://github.com/zizanibot/UpdateElectedDB.

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


class MissingEnvException(Exception):
    """Exception raised when an environment variable is missing."""


def __load_env(name: str, default: str) -> str:
    """Loads an environment variable either from the environment or from a default generating function."""
    value = os.getenv(name)
    return value if value else default


def __load_env_or_none(name: str) -> Optional[str]:
    """Loads an environment variable from the environment or return None."""
    value = os.getenv(name)
    return value


def __load_env_required(name: str) -> str:
    """Loads a required environment variable."""
    value = os.getenv(name)
    if not value:
        raise MissingEnvException(f"The environment variable {name} is required")
    return value


# Updates
UPDATE_URL_DOWNLOAD_DEPUTES = __load_env(
    "UPDATE_URL_DOWNLOAD_DEPUTES",
    "https://data.assemblee-nationale.fr/static/openData/repository/17/amo/deputes_actifs_mandats_actifs_organes/"
    "AMO10_deputes_actifs_mandats_actifs_organes.json.zip",
)  # URL to update deputes
UPDATE_URL_DOWNLOAD_SENAT = __load_env(
    "UPDATE_URL_DOWNLOAD_SENAT",
    "https://www.senat.fr/api-senat/senateurs.json",
)  # URL to update senat
UPDATE_URL_DOWNLOAD_EUROPARL = __load_env(
    "UPDATE_URL_DOWNLOAD_EUROPARL",
    "https://data.europarl.europa.eu/distribution/meps_10_70_fr.csv",
)  # URL to update senat

UPDATE_PROGRESS_SECOND = int(
    __load_env("UPDATE_DOWNLOAD_PROGRESS_SECOND", "2")
)  # Download progress update in second, if 0 is disabled

OUTPUT_FOLDER = Path(__load_env_required("OUTPUT_FOLDER"))  # Path to "data" folder
EMAIL_SENAT_FILE = (
    Path(email_path)
    if (email_path := __load_env_or_none("EMAIL_SENAT_FILE")) is not None
    else None
)  # Path to the email file

# Logs
LOG_PATH = __load_env("LOG_PATH", "interpelmail_update.log")  # Path to the log file
LOG_LEVEL = __load_env("LOG_LEVEL", "INFO").upper()  # Logging level (INFO, DEBUG...)
