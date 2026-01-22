# Copyright (C) 2026 zizanibot
# See LICENSE file for extended copyright information.
# This file is part of UpdateElectedDB project from https://github.com/zizanibot/UpdateElectedDB.
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import aiofiles
import yaml

from common.config import OUTPUT_FOLDER
from common.logger import logger
from download.core import read_files_from_directory
from process.core import Elected


async def process_file_deputy_async(acteur_folder: Path, organe_folder: Path) -> None:
    logger.info("Processing deputies files in %s", acteur_folder)

    deputies: List[Elected] = []

    async for data in read_files_from_directory(acteur_folder):
        deputies.append(await Elected.from_deputy_json(data, organe_folder))

    deputies_dict: Dict[str, Any] = {
        deputy.circonscription_code: deputy.to_dict() for deputy in deputies
    }

    output: Dict[str, Any] = {
        "metadata": {
            "last_updated": datetime.now().isoformat(),
            "count": len(deputies_dict),
        },
        "deputies": deputies_dict,
    }

    async with aiofiles.open(
        OUTPUT_FOLDER / "deputies.yaml", mode="w+", encoding="utf-8"
    ) as f:
        await f.write(yaml.dump(output))
        await f.flush()

    logger.info("Process deputies done")
