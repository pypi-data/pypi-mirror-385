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

import subprocess
import sys
from pathlib import Path

from conftest import edit_install
from pytest_inmanta.plugin import Project

from inmanta_module_factory.builder import InmantaModuleBuilder
from inmanta_module_factory.inmanta.attribute import Attribute
from inmanta_module_factory.inmanta.entity import Entity
from inmanta_module_factory.inmanta.entity_relation import EntityRelation
from inmanta_module_factory.inmanta.implement import Implement
from inmanta_module_factory.inmanta.implementation import Implementation
from inmanta_module_factory.inmanta.index import Index
from inmanta_module_factory.inmanta.module import Module
from inmanta_module_factory.inmanta.plugin import Plugin, PluginArgument
from inmanta_module_factory.inmanta.types import InmantaListType, InmantaStringType
from inmanta_module_factory.stats.stats import ModuleFileStats, ModuleStats


def test_empty_module(project: Project, tmp_path: Path) -> None:
    """
    This simple test creates an empty module and validates that it is a valid inmanta module.
    We need the project fixture for its venv "inheritance" capabilities.  This insure than when
    installing the generated module (and any of its dependencies) in the venv, it won't affect
    all the other test cases.
    """
    module = Module(name="test_test")
    module_builder = InmantaModuleBuilder(module, allow_watermark=True)

    m = module_builder.generate_module(tmp_path)

    edit_install(m.path)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests",
        ],
        cwd=m.path,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    assert result.returncode == 0, result.stderr

    module_builder.upgrade_existing_module(m)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests",
        ],
        cwd=m.path,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    assert result.returncode == 0, result.stderr


def test_basic_module(project: Project) -> None:
    """
    This simple test creates a more complex module, with entities, implementations, index, etc.
    It then validates that the modules can be compiled and that its entities can be used.
    """
    module = Module(name="test")
    module_builder = InmantaModuleBuilder(module, allow_watermark=True)

    entity = Entity(
        "Test",
        path=[module.name],
        fields=[
            Attribute(
                name="test",
                inmanta_type=InmantaListType(InmantaStringType),
                default="[]",
                description="This is a test list attribute",
            ),
        ],
        description="This is a test entity",
    )

    index_attribute = Attribute(
        name="test1",
        inmanta_type=InmantaStringType,
        description="This is a test attribute",
        entity=entity,
    )

    implementation = Implementation(
        name="test",
        path=[module.name],
        entity=entity,
        content=f"std::print(self.{index_attribute.name})",
        description="This is a test implementation",
    )

    implement = Implement(
        path=[module.name],
        implementation=implementation,
        entity=entity,
    )

    index = Index(
        path=[module.name],
        entity=entity,
        fields=[index_attribute],
        description="This is a test index",
    )

    relation = EntityRelation(
        name="tests",
        path=[module.name],
        entity=entity,
        cardinality=(0, None),
        peer=EntityRelation(
            name="",
            path=[module.name],
            entity=entity,
            cardinality=(0, 0),
        ),
    )

    module_builder.add_module_element(entity)
    module_builder.add_module_element(implementation)
    module_builder.add_module_element(implement)
    module_builder.add_module_element(index)
    module_builder.add_module_element(relation)

    assert module_builder.generate_module_stats() == ModuleStats(
        entity_count=1,
        entity_relation_count=1,
        index_count=1,
        implement_count=1,
        implementation_count=1,
        type_def_count=0,
        module_init_stats=ModuleFileStats(
            entity_count=1,
            entity_relation_count=1,
            index_count=1,
            implement_count=1,
            implementation_count=1,
            type_def_count=0,
        ),
        sub_modules_stats={},
    )

    module_path = Path(project._test_project_dir) / "modules"
    m = module_builder.generate_module(module_path)

    edit_install(f"{str(module_path)}/test")

    project.compile(
        """
            import test

            test::Test(
                test1="a",
                tests=test::Test(test1="b"),
            )
            a = test::Test[test1="a"]
        """,
        no_dedent=False,
    )

    assert "a" in (project.get_stdout() or "")
    assert "b" in (project.get_stdout() or "")

    module_builder.upgrade_existing_module(m)

    project.compile(
        """
            import test

            test::Test(
                test1="a",
                tests=test::Test(test1="b"),
            )
            a = test::Test[test1="a"]
        """,
        no_dedent=False,
    )


def test_plugin(project: Project) -> None:
    """
    This simple test creates a more complex module, with entities, implementations, index, etc.
    It then validates that the modules can be compiled and that its entities can be used.
    """
    module = Module(name="test")
    module_builder = InmantaModuleBuilder(module, allow_watermark=True)

    plugin = Plugin(
        name="hello",
        arguments=[
            PluginArgument(
                name="world",
                inmanta_type=InmantaStringType,
            ),
        ],
        return_type=PluginArgument(
            name="",
            inmanta_type=InmantaStringType,
        ),
        content="""return f"hello {world}" """,
    )

    module_builder.add_plugin(plugin)

    module_path = Path(project._test_project_dir) / "modules"
    m = module_builder.generate_module(module_path)

    edit_install(f"{str(module_path)}/test")

    # Add a dummy file on the side of the plugins file to be sure the full dir is
    # not removed in the middle of the tests as it causes strange OSError during
    # next compile.
    dummy_file = (
        module_path
        / module_builder._module.name
        / "inmanta_plugins"
        / module_builder._module.name
        / ".dummy-file"
    )
    dummy_file.touch()

    project.compile(
        """
            import test

            std::print(test::hello("universe"))
        """,
        no_dedent=False,
    )

    assert "hello universe" in (project.get_stdout() or "")

    module_builder.upgrade_existing_module(m)

    project.compile(
        """
            import test

            std::print(test::hello("universe"))
        """,
        no_dedent=False,
    )

    assert "hello universe" in (project.get_stdout() or "")
