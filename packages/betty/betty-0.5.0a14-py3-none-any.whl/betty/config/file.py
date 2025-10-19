"""
Configuration file management.
"""

from __future__ import annotations

from contextlib import chdir
from typing import TYPE_CHECKING, TypeVar

import aiofiles
from aiofiles.os import makedirs

from betty.assertion import AssertionChain, assert_file_path
from betty.config import Configuration
from betty.exception import UserFacingExceptionGroup
from betty.factory import new
from betty.locale.localizable import Plain
from betty.serde.format import FORMAT_REPOSITORY, format_for

if TYPE_CHECKING:
    from pathlib import Path

_ConfigurationT = TypeVar("_ConfigurationT", bound=Configuration)


async def assert_configuration_file(
    configuration: _ConfigurationT,
) -> AssertionChain[Path, _ConfigurationT]:
    """
    Assert that configuration can be loaded from a file.
    """
    available_formats = {
        available_format: await new(available_format.cls)
        for available_format in FORMAT_REPOSITORY
    }

    def _assert(configuration_file_path: Path) -> _ConfigurationT:
        with (
            UserFacingExceptionGroup().assert_valid() as errors,
            # Change the working directory to allow relative paths to be resolved
            # against the configuration file's directory path.
            chdir(configuration_file_path.parent),
        ):
            with open(configuration_file_path) as f:
                read_configuration = f.read()
            with errors.catch(Plain(f"in {str(configuration_file_path.resolve())}")):
                configuration_file_format = available_formats[
                    format_for(list(available_formats), configuration_file_path.suffix)
                ]
                configuration.load(configuration_file_format.load(read_configuration))
            return configuration

    return assert_file_path() | _assert


async def write_configuration_file(
    configuration: Configuration, configuration_file_path: Path
) -> None:
    """
    Write configuration to a file.
    """
    serde_format_type = format_for(
        list(FORMAT_REPOSITORY), configuration_file_path.suffix
    )
    serde_format = await new(serde_format_type.cls)
    dump = serde_format.dump(configuration.dump())
    await makedirs(configuration_file_path.parent, exist_ok=True)
    async with aiofiles.open(configuration_file_path, mode="w") as f:
        await f.write(dump)
