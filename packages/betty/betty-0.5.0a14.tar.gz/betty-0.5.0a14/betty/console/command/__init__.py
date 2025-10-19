"""
Provide the Command Line Interface.
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, ClassVar, ParamSpec, TypeAlias, TypeVar, final

from betty.locale.localizable import _
from betty.plugin import (
    ClassedPluginDefinition,
    ClassedPluginTypeDefinition,
    UserFacingPluginDefinition,
)

if TYPE_CHECKING:
    import argparse

_T = TypeVar("_T")
_P = ParamSpec("_P")


CommandFunction: TypeAlias = Callable[..., Awaitable[None]]


class Command:
    """
    A console command plugin.

    Read more about :doc:`/development/plugin/command`.
    """

    plugin: ClassVar[CommandDefinition]

    @abstractmethod
    async def configure(self, parser: argparse.ArgumentParser) -> CommandFunction:
        """
        Configure the command.

        :return: The command function, which is an async callable that returns ``None`` and takes all parser arguments
            as keyword arguments.
        """


@final
class CommandDefinition(UserFacingPluginDefinition, ClassedPluginDefinition[Command]):
    """
    A console command definition.

    Read more about :doc:`/development/plugin/command`.
    """

    type: ClassVar[ClassedPluginTypeDefinition] = ClassedPluginTypeDefinition(
        id="command",
        label=_("Command"),
        cls=Command,
    )
