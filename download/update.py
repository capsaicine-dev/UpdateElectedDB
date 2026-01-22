# Copyright (C) 2026 zizanibot
# See LICENSE file for extended copyright information.
# This file is part of UpdateElectedDB project from https://github.com/zizanibot/UpdateElectedDB.
from __future__ import annotations

import asyncio
from pathlib import Path
import tempfile

from common.config import (
    UPDATE_URL_DOWNLOAD_DEPUTES,
    UPDATE_URL_DOWNLOAD_SENAT,
    UPDATE_URL_DOWNLOAD_EUROPARL,
)
from download.core import download_file_async, unzip_file_async
from common.logger import logger
from process.depute import process_file_deputy_async
from process.senat import process_file_senat_async
from process.europarl import process_file_europarl_async


def show_error_on_exception(msg: str, exception: Exception) -> None:
    """Standard log output when an exception occur"""
    logger.error("Update failed : %s", msg)
    logger.error("Error : %s", str(exception))


async def update_deputes(download_temp: Path, zip_temp: Path) -> None:
    """
    Update the data folder with fresh data from UPDATE_URL_DOWNLOAD_DEPUTES.
    """
    logger.info("=== Update starting for deputes ===")
    # Download File to zip download folder
    zip_file_deputes: Path = download_temp / "data_deputes.zip"
    try:
        await download_file_async(UPDATE_URL_DOWNLOAD_DEPUTES, zip_file_deputes)
    except Exception as e:
        show_error_on_exception("download failed", e)
        raise e

    await asyncio.sleep(0.1)

    # Unzip File to zip temp folder
    zip_temp_deputes: Path = zip_temp / "deputes"
    try:
        await unzip_file_async(zip_file_deputes, zip_temp_deputes)
    except Exception as e:
        show_error_on_exception("unzipping failed", e)
        raise e

    temp_acteur: Path = zip_temp_deputes / "json" / "acteur"
    temp_organe: Path = zip_temp_deputes / "json" / "organe"
    try:
        await process_file_deputy_async(temp_acteur, temp_organe)
    except Exception as e:
        show_error_on_exception("process failed", e)
        raise e

    logger.info("=== Update success for deputes ===")


async def update_senat(download_temp: Path) -> None:
    """
    Update the data folder with fresh data from UPDATE_URL_DOWNLOAD_SENAT.
    """
    logger.info("=== Update starting for senat ===")
    # Download File to zip download folder
    file_senat: Path = download_temp / "data_senat.json"
    try:
        await download_file_async(UPDATE_URL_DOWNLOAD_SENAT, file_senat)
    except Exception as e:
        show_error_on_exception("download failed", e)
        raise e

    await asyncio.sleep(0.1)

    try:
        await process_file_senat_async(file_senat)
    except Exception as e:
        show_error_on_exception("process failed", e)
        raise e

    logger.info("=== Update success for senat ===")


async def update_europarl(download_temp: Path) -> None:
    """
    Update the data folder with fresh data from UPDATE_URL_DOWNLOAD_EUROPARL.
    """
    logger.info("=== Update starting for europarl ===")
    # Download File to zip download folder
    file_europarl: Path = download_temp / "data_europarl.csv"
    try:
        await download_file_async(UPDATE_URL_DOWNLOAD_EUROPARL, file_europarl)
    except Exception as e:
        show_error_on_exception("download failed", e)
        raise e

    await asyncio.sleep(0.1)

    try:
        await process_file_europarl_async(file_europarl)
    except Exception as e:
        show_error_on_exception("process failed", e)
        raise e

    logger.info("=== Update success for europarl ===")


async def update_async() -> None:
    """
    Update the data folder with fresh data from
    UPDATE_URL_DOWNLOAD_deputes.
    """

    logger.info("=== Update starting ===")

    with (
        tempfile.TemporaryDirectory() as download_temp,
        tempfile.TemporaryDirectory() as zip_temp,
    ):
        download_path: Path = Path(download_temp)
        zip_path: Path = Path(zip_temp)
        try:
            await update_deputes(download_path, zip_path)
        except Exception as e:
            logger.error("=== Update deputes failed ===")
            raise e
        try:
            await update_senat(download_path)
        except Exception as e:
            logger.error("=== Update senat failed ===")
            raise e
        try:
            await update_europarl(download_path)
        except Exception as e:
            logger.error("=== Update europarl failed ===")
            raise e

    logger.info("=== Update success ===")


async def update() -> None:
    """Async version of update ot make it compatible with asyncio"""
    try:
        await update_async()
    except Exception:
        logger.error("=== Update failed ===")
