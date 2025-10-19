"""
Project support for the Console.
"""

import argparse
from contextlib import suppress
from pathlib import Path
from typing import Any

from betty.app import App
from betty.assertion import assert_path
from betty.config.file import assert_configuration_file
from betty.console.assertion import assertion_to_argument_type
from betty.console.command import CommandFunction
from betty.error import FileNotFound
from betty.exception import UserFacingException
from betty.locale.localizable import _
from betty.project import Project
from betty.project.config import ProjectConfiguration
from betty.serde.format import FORMAT_REPOSITORY


async def add_project_argument(
    parser: argparse.ArgumentParser, command_function: CommandFunction, app: App
) -> CommandFunction:
    """
    Add an argument to load a :py:class:`betty.project.Project` into a ``project`` keyword argument.
    """
    localizer = await app.localizer
    parser.add_argument(
        "-p",
        "--project",
        dest="project_configuration_file_path",
        help=localizer._(
            "The path to a Betty project directory or configuration file. Defaults to {default} in the current working directory."
        ).format(
            default=f"betty.{'|'.join(extension[1:] for serde_format in FORMAT_REPOSITORY for extension in serde_format.cls.extensions())}"
        ),
        type=assertion_to_argument_type(assert_path(), localizer=localizer),
    )

    async def _command_function_with_project_argument(
        *, project_configuration_file_path: Path | None = None, **kwargs: Any
    ) -> None:
        project = await Project.new(
            app, configuration=await ProjectConfiguration.new(Path())
        )
        await _read_project_configuration(project, project_configuration_file_path)
        return await command_function(project=project, **kwargs)

    return _command_function_with_project_argument


async def _read_project_configuration(
    project: Project, provided_configuration_file_path_str: Path | None
) -> None:
    project_directory_path = Path.cwd()
    if provided_configuration_file_path_str is None:
        try_configuration_file_paths = [
            project_directory_path / f"betty{extension}"
            for extension in FORMAT_REPOSITORY.extensions()
        ]
        for try_configuration_file_path in try_configuration_file_paths:
            with suppress(FileNotFound):
                return await _read_project_configuration_file(
                    project, try_configuration_file_path
                )
        raise UserFacingException(
            _(
                "Could not find any of the following configuration files in {project_directory_path}: {configuration_file_names}."
            ).format(
                configuration_file_names=", ".join(
                    str(try_configuration_file_path.relative_to(project_directory_path))
                    for try_configuration_file_path in try_configuration_file_paths
                ),
                project_directory_path=str(project_directory_path),
            )
        )
    await _read_project_configuration_file(
        project,
        (project_directory_path / provided_configuration_file_path_str)
        .expanduser()
        .resolve(),
    )
    return None


async def _read_project_configuration_file(
    project: Project, configuration_file_path: Path
) -> None:
    user = project.app.user
    assert_configuration = await assert_configuration_file(project.configuration)
    try:
        assert_configuration(configuration_file_path)
    except UserFacingException as error:
        await user.message_debug(error)
        raise
    else:
        project.configuration.configuration_file_path = configuration_file_path
        await user.message_information(
            _("Loaded the configuration from {configuration_file_path}.").format(
                configuration_file_path=str(configuration_file_path)
            ),
        )
