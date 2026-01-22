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
from download.core import read_json, read_csv
from process.core import Elected


async def add_email_adresses(senats_dict: Dict[str, Elected]) -> None:
    email_dict: Dict[str, str] = {}

    if not EMAIL_SENAT_FILE:
        logger.warning("Cannot add email addresses for senat")
        return

    email_reader: csv.DictReader = await read_csv(EMAIL_SENAT_FILE)
    for row in email_reader:
        email_dict[row["senmat"]] = row["senema"]

    missing_email: Set[str] = senats_dict.keys() - email_dict.keys()
    found_email: Set[str] = senats_dict.keys() & email_dict.keys()

    for id in missing_email:
        logger.warning("MISSING EMAIL FOR: %s", senats_dict[id])

    for id in found_email:
        senats_dict[id].email = email_dict[id]


async def process_file_senat_async(senat_file: Path) -> None:
    logger.info("Processing senat file %s", senat_file)

    senats: List[Elected] = []

    for data in await read_json(senat_file):
        senats.append(await Elected.from_senat_json(data))

    senats_dict: Dict[str, Elected] = {senat.ref: senat for senat in senats}
    await add_email_adresses(senats_dict)

    output: Dict[str, Any] = {
        "metadata": {
            "last_updated": datetime.now().isoformat(),
            "count": len(senats_dict),
        },
        "members": {k: v.to_dict() for k, v in senats_dict.items()},
    }

    async with aiofiles.open(
        OUTPUT_FOLDER / "senat.yaml", mode="w+", encoding="utf-8"
    ) as f:
        await f.write(yaml.dump(output))
        await f.flush()

    logger.info("Process senat done")
