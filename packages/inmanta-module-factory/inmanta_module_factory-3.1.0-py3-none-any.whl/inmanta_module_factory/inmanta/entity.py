"""
Copyright 2021 Inmanta

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Contact: code@inmanta.com
Author: Inmanta
"""

from collections.abc import Sequence
from textwrap import indent
from typing import Optional

from inmanta_module_factory.helpers import utils
from inmanta_module_factory.helpers.const import INDENT_PREFIX
from inmanta_module_factory.inmanta import attribute, entity_field, entity_relation
from inmanta_module_factory.inmanta.module_element import ModuleElement


class Entity(ModuleElement):
    def __init__(
        self,
        name: str,
        path: list[str],
        fields: Optional[Sequence["entity_field.EntityField"]] = None,
        parents: Optional[Sequence["Entity"]] = None,
        description: Optional[str] = None,
        *,
        force_attribute_doc: bool = True,
        sort_attributes: bool = True,
    ) -> None:
        """
        An entity definition.
        :param name: The name of the entity
        :param path: The place in the module where the entity should be printed out
        :param fields: A list of all the attributes and relations of this entity.
            All the fields provided here will be attached to this entity using their
            method `attach_entity`.
        :param parents: A list of all the entities this one inherit from
        :param description: A description of this entity, to be added in its docstring
        :param force_attribute_doc: Add attribute and relation lines to the entity docstring even if the attribute / relation
            has no description.
        :param sort_attributes: Sort attributes (and relations docs) alphabetically. If false, insert order is kept.
        """
        super().__init__(utils.validate_entity_name(name), path, description)
        # store fields in a dict to maintain insert order
        self.fields: dict["entity_field.EntityField", None] = {
            field: None for field in (fields or [])
        }
        for field in self.fields:
            field.attach_entity(self)
        self.parents = parents or []
        self._force_attribute_doc: bool = force_attribute_doc
        self._sort_attributes: bool = sort_attributes

    def all_fields(self) -> set["entity_field.EntityField"]:
        """
        Return a set of all the fields of the entity, and any of its parent
        """
        parents_fields = set()
        for parent in self.parents:
            parents_fields |= parent.all_fields()

        return self.fields.keys() | parents_fields

    def attach_field(self, field: "entity_field.EntityField") -> None:
        self.fields[field] = None

    @property
    def attributes(self) -> list["attribute.Attribute"]:
        attributes = [
            field for field in self.fields if isinstance(field, attribute.Attribute)
        ]
        return (
            sorted(attributes, key=lambda attr: attr.name)
            if self._sort_attributes
            else attributes
        )

    @property
    def relations(self) -> list["entity_relation.EntityRelation"]:
        relations = [
            field
            for field in self.fields
            if isinstance(field, entity_relation.EntityRelation)
        ]
        return (
            sorted(relations, key=lambda rel: rel.name)
            if self._sort_attributes
            else relations
        )

    def _ordering_key(self) -> str:
        return self.name + ".entity"

    def _get_derived_imports(self) -> set[str]:
        imports = set()

        for parent in self.parents:
            if self.path_string != parent.path_string:
                # Parent is in a different file
                imports.add(parent.path_string)

        for attr in self.attributes:
            if not attr.inmanta_type.path_string:
                # This is a primitive type, it can not be imported
                continue

            if self.path_string != attr.inmanta_type.path_string:
                # Attribute type is defined in another file
                imports.add(attr.inmanta_type.path_string)

        return imports

    def docstring(self) -> str:
        attribute_docs = [
            f":attr {x_attribute.name}: {x_attribute.description or ''}"
            for x_attribute in self.attributes
            if self._force_attribute_doc or x_attribute.description is not None
        ]

        relation_docs = [
            f":rel {relation.name}: {relation.description or ''}"
            for relation in self.relations
            # exclude relations where name is None or the empty string,
            # i.e. one-direction relations on the side where they are not defined
            if relation.name
            and (self._force_attribute_doc or relation.description is not None)
        ]

        result = "\n".join([super().docstring(), *attribute_docs, *relation_docs])
        # make sure to end with a single traling newline
        return result.rstrip("\n") + "\n"

    def _definition(self) -> str:
        inheritance = ""
        if self.parents:
            parents = []
            for parent in self.parents:
                parent_path = parent.name
                if parent.full_path_string == "std::Entity":
                    # This is implicit, not need to specify it
                    continue

                if self.path_string != parent.path_string:
                    # Parent is in a different file
                    parent_path = parent.full_path_string

                parents.append(parent_path)

            if parents:
                inheritance = " extends " + ", ".join(parents)

        return f"entity {self.name}{inheritance}:\n"

    def __str__(self) -> str:
        return (
            self._definition()
            + indent(
                (
                    '"""\n'
                    + self.docstring()
                    + '"""\n'
                    + "".join([str(attribute) for attribute in self.attributes])
                ),
                prefix=INDENT_PREFIX,
            )
            + "end\n"
        )
