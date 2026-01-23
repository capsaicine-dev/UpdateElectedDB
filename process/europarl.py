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
from download.core import read_csv
from process.core import Elected


async def process_file_europarl_async(europarl_file: Path) -> None:
    logger.info("Processing europarl file %s", europarl_file)

    europarldeps: List[Elected] = []

    for data in await read_csv(europarl_file):
        europarldeps.append(await Elected.from_europarl_csv(data))

    europarldeps_dict: Dict[str, Any] = {
        europarldep.ref: europarldep.to_dict() for europarldep in europarldeps
    }

    output: Dict[str, Any] = {
        "metadata": {
            "last_updated": datetime.now().isoformat(),
            "count": len(europarldeps_dict),
        },
        "members": europarldeps_dict,
    }

    async with aiofiles.open(
        OUTPUT_FOLDER / "europarl.yaml", mode="w+", encoding="utf-8"
    ) as f:
        await f.write(yaml.dump(output))
        await f.flush()

    logger.info("Process europarl done")
