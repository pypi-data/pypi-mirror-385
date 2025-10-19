"""Provide Betty's data model API."""

from __future__ import annotations

from reprlib import recursive_repr
from typing import TYPE_CHECKING, Any, ClassVar, Self, TypeAlias, TypeVar, final
from uuid import uuid4

from typing_extensions import override

from betty.json.linked_data import (
    JsonLdObject,
    LinkedDataDumpableJsonLdObject,
)
from betty.json.schema import Array, JsonSchemaReference, Null, OneOf, String
from betty.locale.localizable import Localizable, _
from betty.locale.localizer import DEFAULT_LOCALIZER
from betty.mutability import Mutable
from betty.plugin import (
    ClassedPlugin,
    ClassedPluginDefinition,
    ClassedPluginTypeDefinition,
    CountableUserFacingPluginDefinition,
)
from betty.repr import repr_instance
from betty.string import kebab_case_to_lower_camel_case
from betty.user import UserFacing

if TYPE_CHECKING:
    import builtins

    from betty.project import Project
    from betty.serde.dump import Dump, DumpMapping


class NonPersistentId(str):
    """
    A randomly generated ID that is not persistent.

    Entities must have IDs for identification. However, not all entities can be provided with an ID that exists in the
    original data set (such as a third-party family tree loaded into Betty).

    Non-persistent IDs are helpful in case there is no external ID that can be used. However, as they do not persist
    when reloading an ancestry, they *MUST NOT* be in contexts where persistent identifiers are expected, such as in
    URLs.
    """

    __slots__ = ()

    def __new__(cls, entity_id: str | None = None):  # noqa D102
        return super().__new__(cls, entity_id or str(uuid4()))


class Entity(LinkedDataDumpableJsonLdObject, Mutable, ClassedPlugin):
    """
    An entity is a uniquely identifiable data container.

    Read more about :doc:`/development/plugin/entity-type`.

    To test your own subclasses, use :py:class:`betty.test_utils.model.EntityTestBase`.
    """

    plugin: ClassVar[EntityDefinition]

    def __init__(
        self,
        id: str | None = None,  # noqa A002
        *args: Any,
        **kwargs: Any,
    ):
        self._id = NonPersistentId() if id is None else id
        super().__init__(*args, **kwargs)

    @override
    def __hash__(self) -> int:
        return hash(self.ancestry_id)

    @override  # type: ignore[callable-functiontype]
    @recursive_repr()
    def __repr__(self) -> str:
        return repr_instance(self, id=self._id)

    @property
    def id(self) -> str:
        """
        The entity ID.

        This MUST be unique per entity type, per ancestry.
        """
        return self._id

    @property
    def ancestry_id(self) -> tuple[builtins.type[Self], str]:
        """
        The ancestry ID.

        This MUST be unique per ancestry.
        """
        return type(self), self.id

    @property
    def label(self) -> Localizable:
        """
        The entity's human-readable label.
        """
        return _("{entity_type} {entity_id}").format(
            entity_type=self.plugin.label, entity_id=self.id
        )

    @override
    async def dump_linked_data(self, project: Project) -> DumpMapping[Dump]:
        dump = await super().dump_linked_data(project)

        if persistent_id(self) and isinstance(self, UserFacing):
            url_generator = await project.url_generator
            dump["@id"] = url_generator.generate(
                f"betty-static:///{self.plugin.id}/{self.id}/index.json",
                absolute=True,
            )
        dump["id"] = self.id

        return dump

    @override
    @classmethod
    async def linked_data_schema(cls, project: Project) -> JsonLdObject:
        schema = await super().linked_data_schema(project)
        schema._def_name = f"{kebab_case_to_lower_camel_case(cls.plugin.id)}Entity"
        schema.title = cls.plugin.label.localize(DEFAULT_LOCALIZER)
        schema.add_property("$schema", JsonSchemaReference())
        schema.add_property("id", String(title="Entity ID"), False)

        return schema


@final
class EntityDefinition(
    CountableUserFacingPluginDefinition, ClassedPluginDefinition[Entity]
):
    """
    An entity definition.
    """

    type: ClassVar[ClassedPluginTypeDefinition] = ClassedPluginTypeDefinition(
        id="entity",
        label=_("Entity"),
        cls=Entity,
    )


AncestryEntityId: TypeAlias = tuple[type[Entity], str]


def persistent_id(entity_or_id: Entity | str) -> bool:
    """
    Test if an entity ID is persistent.

    See :py:class:`betty.model.NonPersistentId`.
    """
    return not isinstance(
        entity_or_id if isinstance(entity_or_id, str) else entity_or_id.id,
        NonPersistentId,
    )


_EntityT = TypeVar("_EntityT", bound=Entity)


class ToZeroOrOneSchema(OneOf):
    """
    A schema for a to-zero-or-one entity association.
    """

    def __init__(self, *, title: str | None = None, description: str | None = None):
        super().__init__(
            String(
                title=title or "Optional associate entity",
                description=description
                or "An optional reference to an associate entity's JSON resource",
                format=String.Format.URI,
            ),
            Null(),
        )


class ToOneSchema(String):
    """
    A schema for a to-one entity association.
    """

    def __init__(self, *, title: str | None = None, description: str | None = None):
        super().__init__(
            title=title or "Associate entity",
            description=description
            or "A reference to an associate entity's JSON resource",
            format=String.Format.URI,
        )


class ToManySchema(Array):
    """
    A schema for a to-many entity association.
    """

    def __init__(self, *, title: str | None = None, description: str | None = None):
        super().__init__(
            ToOneSchema(),
            title=title or "Associate entities",
            description=description
            or "References to associate entities' JSON resources",
        )
