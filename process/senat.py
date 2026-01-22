# Copyright (C) 2026 zizanibot
# See LICENSE file for extended copyright information.
# This file is part of UpdateElectedDB project from https://github.com/zizanibot/UpdateElectedDB.
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set

import aiofiles
import yaml

from common.config import OUTPUT_FOLDER, EMAIL_SENAT_FILE
from common.logger import logger
from download.core import read_file
from process.core import Elected


def add_email_adresses(senats_dict: Dict[str, Any]) -> None:
    email_dict: Dict[str, str] = {}

    if not EMAIL_SENAT_FILE:
        logger.warning("Cannot add email addresses for senat")
        return

    with open(EMAIL_SENAT_FILE, "r") as csvfile:
        ref_reader = csv.reader(csvfile, delimiter=",")
        _ = next(ref_reader, None)  # skip header

        for row in ref_reader:
            email_dict[row[0]] = row[1]

    missing_email: Set[str] = senats_dict.keys() - email_dict.keys()
    found_email: Set[str] = senats_dict.keys() & email_dict.keys()

    for id in missing_email:
        logger.warning("NOT IN REFERENCE: %s", senats_dict[id])

    for id in found_email:
        senats_dict[id]["email"] = email_dict[id]


async def process_file_senat_async(senat_file: Path) -> None:
    logger.info("Processing senat file %s", senat_file)

    senats: List[Elected] = []

    for data in await read_file(senat_file):
        senats.append(await Elected.from_senat_json(data))

    senats_dict: Dict[str, Any] = {senat.ref: senat.to_dict() for senat in senats}
    add_email_adresses(senats_dict)

    output: Dict[str, Any] = {
        "metadata": {
            "last_updated": datetime.now().isoformat(),
            "count": len(senats_dict),
        },
        "deputies": senats_dict,
    }

    async with aiofiles.open(
        OUTPUT_FOLDER / "senat.yaml", mode="w+", encoding="utf-8"
    ) as f:
        await f.write(yaml.dump(output))
        await f.flush()

    logger.info("Process senat done")
