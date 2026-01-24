# Copyright (C) 2026 zizanibot
# See LICENSE file for extended copyright information.
# This file is part of UpdateElectedDB project from https://github.com/zizanibot/UpdateElectedDB.
from __future__ import annotations

import os
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import aiofiles
import yaml
import asyncpg

from common.config import OUTPUT_FOLDER, POSTGRES_OPTIONS
from common.logger import logger
from process.core import Elected


async def export_from_sql_file(senat_sql_file: Path) -> List[Any]:
    env = os.environ.copy()
    env["PGPASSWORD"] = POSTGRES_OPTIONS.password

    logger.info("Creating database %s", POSTGRES_OPTIONS.database)
    conn = await asyncpg.connect(
        database="postgres",
        user=POSTGRES_OPTIONS.user,
        password=POSTGRES_OPTIONS.password,
        host=POSTGRES_OPTIONS.host,
    )

    await conn.execute(f"DROP DATABASE IF EXISTS {POSTGRES_OPTIONS.database}")
    await conn.execute(f"CREATE DATABASE {POSTGRES_OPTIONS.database}")
    await conn.close()

    logger.info("Loading %s", senat_sql_file)
    conn = await asyncpg.connect(
        database=POSTGRES_OPTIONS.database,
        user=POSTGRES_OPTIONS.user,
        password=POSTGRES_OPTIONS.password,
        host=POSTGRES_OPTIONS.host,
    )

    try:
        process = await asyncio.create_subprocess_exec(
            "psql",
            "-U",
            "postgres",
            "-d",
            POSTGRES_OPTIONS.database,
            "-h",
            POSTGRES_OPTIONS.host,
            "-f",
            str(senat_sql_file),
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise Exception(f"psql failed: {stderr.decode()}")

        logger.info("%s correcly loaded", senat_sql_file)

        rows = await conn.fetch(
            """select 
	sen.senmat, 
	sen.quacod, 
	sen.sennomuse, 
	sen.senprenomuse, 
	dpt.dptcod,
	dpt.dptlib,
	grppol.grppolcod,
	grppol.grppollilcou, 
	sen.senema 
from sen 
join grppol on grppol.grppolcod = sen.sengrppolcodcou
join dpt on dpt.dptnum = sen.sencirnumcou
where etasencod = 'ACTIF'"""
        )

        logger.info(f"Found {len(rows)} rows")

    finally:
        await conn.close()

    logger.info("Cleaning up database %s", POSTGRES_OPTIONS.database)
    conn = await asyncpg.connect(
        database="postgres",
        user=POSTGRES_OPTIONS.user,
        password=POSTGRES_OPTIONS.password,
        host=POSTGRES_OPTIONS.host,
    )

    await conn.execute(f"DROP DATABASE IF EXISTS {POSTGRES_OPTIONS.database}")
    await conn.close()

    return rows


async def process_file_senat_async(senat_file: Path) -> None:
    logger.info("Processing senat file %s", senat_file)

    senats: List[Elected] = []

    for data in await export_from_sql_file(senat_file):
        senats.append(await Elected.from_senat(data))

    senats_dict: Dict[str, Any] = {senat.ref: senat.to_dict() for senat in senats}

    output: Dict[str, Any] = {
        "metadata": {
            "last_updated": datetime.now().isoformat(),
            "count": len(senats_dict),
        },
        "members": senats_dict,
    }

    async with aiofiles.open(
        OUTPUT_FOLDER / "senat.yaml", mode="w+", encoding="utf-8"
    ) as f:
        await f.write(yaml.dump(output))
        await f.flush()

    logger.info("Process senat done")
