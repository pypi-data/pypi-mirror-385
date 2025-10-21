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

import logging
import shutil
from collections import defaultdict
from pathlib import Path
from textwrap import dedent
from typing import Any, Literal, Optional

from cookiecutter.main import cookiecutter  # type: ignore

import inmanta.module
from inmanta_module_factory.helpers import const, utils
from inmanta_module_factory.inmanta.module import Module
from inmanta_module_factory.inmanta.module_element import (
    DummyModuleElement,
    ModuleElement,
)
from inmanta_module_factory.inmanta.plugin import Plugin
from inmanta_module_factory.stats.stats import ModuleFileStats, ModuleStats

LOGGER = logging.getLogger(__name__)


class InmantaModuleBuilder:
    def __init__(
        self,
        module: Module,
        *,
        generation: Literal["v1", "v2"] = "v2",
        allow_watermark: bool = False,
    ) -> None:
        self._module = module
        self._model_files: dict[str, list[ModuleElement]] = defaultdict(list)
        self._plugins: list[Plugin] = list()
        self.generation = generation
        self.allow_watermark = allow_watermark

    def add_module_element(self, module_element: ModuleElement) -> None:
        if not module_element.path[0] == self._module.name:
            raise RuntimeError(
                "The module elements should have a path starting with the module name.  "
                f"Got '{module_element.path[0]}', expected '{self._module.name}'"
            )

        self._model_files[module_element.path_string].append(module_element)

    def add_plugin(self, plugin: Plugin) -> None:
        self._plugins.append(plugin)

    def generate_path_tree(self) -> dict[str, Any]:
        """
        Convert the list of paths into a dict tree, which represents the generated file structure.
        Each key in the dict represents a sub-folder, the _init.cf files are not represented.
        """
        tree: dict[str, Any] = dict()
        for raw_path in self._model_files.keys():
            path = raw_path.split("::")
            tree_ref = tree
            for elem in path:
                if elem not in tree_ref:
                    tree_ref[elem] = dict()

                tree_ref = tree_ref[elem]

        return tree

    def generate_module_stats(
        self, path: Optional[str] = None, tree: Optional[dict[str, Any]] = None
    ) -> ModuleStats:
        """
        Generate statistics about the generated module content.  The statistics simply counts the amount of
        different elements in _init.cf file in each module as well as the sum of those counts for all the
        submodules of a module.
        """
        if path is None:
            path = self._module.name

        if tree is None:
            tree = self.generate_path_tree()
            for elem in path.split("::"):
                tree = tree[elem]
                assert isinstance(tree, dict)

        # Getting the stats for the module's init file
        file_stats: dict[str, int] = ModuleFileStats().dict()
        for module_element in self._model_files.get(path, []):
            element_type = utils.camel_case_to_snake_case(
                str(module_element.__class__.__name__)
            )
            if element_type == "dummy_module_element":
                # The list might contain a dummy_module_element, we don't take this into account
                # in our stats
                continue

            element_stat = f"{element_type}_count"
            file_stats[element_stat] = file_stats[element_stat] + 1

        # Getting the stats from all the sub modules
        sub_modules_stats: dict[str, ModuleStats] = dict()
        for sub_module in tree:
            sub_module_path = "::".join([path, sub_module])
            sub_modules_stats[sub_module] = self.generate_module_stats(
                sub_module_path, tree[sub_module]
            )

        # The stats of a module are the sum of all its submodules and the init file stats
        module_stats = {
            k: sum([getattr(stats, k) for stats in sub_modules_stats.values()]) + v
            for k, v in file_stats.items()
        }

        return ModuleStats(
            **module_stats,
            module_init_stats=ModuleFileStats(**file_stats),
            sub_modules_stats=sub_modules_stats,
        )

    def generate_model_file(
        self,
        model_folder: Path,
        file_key: str,
        force: bool = False,
        copyright_header_template: Optional[str] = None,
    ) -> Optional[Path]:
        if file_key not in self._model_files.keys():
            raise RuntimeError(
                "Tried to generate a file that is not part of the model, "
                f"{file_key} is not in {list(self._model_files.keys())}"
            )

        module_elements = self._model_files[file_key]
        module_elements.sort(key=lambda element: element.ordering_key)
        if not module_elements:
            LOGGER.warning(f"No module elements found for {file_key}, skipping.")
            return None

        if not all(module_element.validate() for module_element in module_elements):
            raise ValueError(f"The validation of the sub module {file_key} failed")

        file_path = model_folder / "/".join(module_elements[0].path[1:]) / "_init.cf"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if file_path.exists():
            LOGGER.warning(
                f"Generating a file where a file already exists: {str(file_path)}"
            )
            if not force:
                raise RuntimeError(
                    f"Generating this file would have overwritten and existing one: {str(file_path)}"
                )

        imports: set[str] = set()
        for module_element in module_elements:
            imports = imports.union(module_element.get_imports())

        import_list = [f"import {import_value}" for import_value in imports]
        import_list.sort()

        file_content = (
            self._module.file_header(copyright_header_template)
            + "\n"
            + "\n".join(import_list)
            + "\n\n"
            + "\n".join([str(module_element) for module_element in module_elements])
        )

        if self.allow_watermark:
            file_content += const.GENERATED_FILE_FOOTER

        file_path.write_text(file_content)

        return file_path

    def generate_plugin_file(
        self,
        plugins_folder: Path,
        force: bool = False,
        copyright_header_template: Optional[str] = None,
    ) -> Path:
        self._plugins.sort(key=lambda plugin: plugin.name)

        file_path = plugins_folder / "__init__.py"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if file_path.exists() and self._plugins:
            LOGGER.warning(
                f"Generating a file where a file already exists: {str(file_path)}"
            )
            if not force:
                raise RuntimeError(
                    f"Generating this file would have overwritten an existing one: {str(file_path)}"
                )
        elif file_path.exists() and not self._plugins:
            # A file already exists, but we don't actually need to add any plugin, so we silently skip
            # this step
            return file_path
        else:
            # No file exists, we can go on
            pass

        imports: set[str] = set()
        for plugin in self._plugins:
            imports = imports.union(plugin.get_imports())

        import_list = list(imports)
        import_list.sort()

        file_content = (
            self._module.file_header(copyright_header_template)
            + "\n"
            + "\n".join(import_list)
            + "\n\n\n"
            + "\n\n".join([str(plugin) for plugin in self._plugins])
        )

        if self.allow_watermark:
            file_content += const.GENERATED_FILE_FOOTER

        file_path.write_text(file_content)

        return file_path

    def generate_model_test(
        self,
        tests_folder: Path,
        force: bool = False,
        copyright_header_template: Optional[str] = None,
    ) -> Path:
        file_path = tests_folder / "test_basics.py"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if file_path.exists():
            LOGGER.warning(
                f"Generating a file where a file already exists: {str(file_path)}"
            )
            if not force:
                raise RuntimeError(
                    f"Generating this file would have overwritten and existing one: {str(file_path)}"
                )

        file_content = (
            self._module.file_header(copyright_header_template)
            + "\n\n"
            + "from pytest_inmanta.plugin import Project\n\n\n"
            + dedent(
                f"""
                def test_basics(project: Project) -> None:
                    project.compile("import {self._module.name}")
                """.strip(
                    "\n"
                )
            )
        )

        if self.allow_watermark:
            file_content += "\n"  # make black happy
            file_content += const.GENERATED_FILE_FOOTER

        file_path.write_text(file_content)

        return file_path

    def generate_module(
        self,
        build_location: Path,
        force: bool = False,
        copyright_header_template: Optional[str] = None,
        fix_linting: bool = False,
    ) -> inmanta.module.Module:
        build_location.mkdir(parents=True, exist_ok=True)
        template_path = cookiecutter(
            "https://github.com/inmanta/inmanta-module-template.git",
            checkout=self.generation,
            output_dir=str(build_location),
            no_input=True,
            extra_context={
                "module_name": self._module.name,
                "module_description": self._module.description,
                "author": self._module.author,
                "author_email": self._module.author_email,
                "license": self._module.license,
                "copyright": self._module.copyright,
                "minimal_compiler_version": self._module.compiler_version or "2019.3",
            },
            overwrite_if_exists=force,
        )

        module_path = Path(template_path)
        LOGGER.debug(f"Module template created at: {module_path}")

        module = inmanta.module.Module.from_path(str(module_path))
        if module is None:
            raise RuntimeError("Could not import module from template")

        LOGGER.debug(f"Module generation: {module.GENERATION.name}")
        if isinstance(module, inmanta.module.ModuleV2):
            # We mark the module as editable, otherwise get_plugin_dir will return
            # the root of the folder instead of the inmanta_plugins/<module_name> dir
            module._is_editable_install = True

        plugins_folder = Path(module.get_plugin_dir() or "")
        LOGGER.debug(f"Module's plugins folder: {plugins_folder}")

        # If no copyright header template is defined, load it from the module itself
        if copyright_header_template is None:
            copyright_header_template = utils.copyright_header_from_module(module)

        # The following parts of the module are overwritten fully by the generator
        shutil.rmtree(str(module_path / "model"))
        shutil.rmtree(str(plugins_folder))
        shutil.rmtree(str(module_path / "tests"))

        self.generate_plugin_file(plugins_folder, force, copyright_header_template)
        self.generate_model_test(
            module_path / "tests", force, copyright_header_template
        )

        if not self._model_files:
            LOGGER.warning(
                "Empty model for module, adding a default empty _init.cf file"
            )
            self.add_module_element(DummyModuleElement(path=[self._module.name]))

        for file_key in list(self._model_files.keys()):
            if file_key == self._module.name:
                continue

            splitted_key = file_key.split("::")
            parent_path = splitted_key[0]
            for part in splitted_key[1:]:
                parent_path += f"::{part}"
                if parent_path not in self._model_files:
                    self._model_files[parent_path] = [
                        DummyModuleElement(parent_path.split("::"))
                    ]

        for file_key in self._model_files.keys():
            self.generate_model_file(
                module_path / "model", file_key, force, copyright_header_template
            )

        if fix_linting:
            utils.fix_module_linting(module)

        return module

    def upgrade_existing_module(
        self,
        existing_module: inmanta.module.Module,
        fix_linting: bool = False,
    ) -> inmanta.module.Module:
        if self.allow_watermark is False:
            raise RuntimeError(
                "self.allow_watermark should be set to True to upgrade an existing module."
            )

        module_path = Path(existing_module.path)
        copyright_header_template = utils.copyright_header_from_module(existing_module)

        LOGGER.debug(f"Module generation: {existing_module.GENERATION.name}")
        if isinstance(existing_module, inmanta.module.ModuleV2):
            # We mark the module as editable, otherwise get_plugin_dir will return
            # the root of the folder instead of the inmanta_plugins/<module_name> dir
            existing_module._is_editable_install = True

        plugins_folder = Path(existing_module.get_plugin_dir() or "")
        LOGGER.debug(f"Module's plugins folder: {plugins_folder}")

        for module_inner_folder in [
            module_path / "model",
            plugins_folder,
            module_path / "tests",
        ]:
            utils.remove_watermarked_files(module_inner_folder)

        self.generate_plugin_file(plugins_folder, False, copyright_header_template)
        self.generate_model_test(
            module_path / "tests", False, copyright_header_template
        )

        for file_key in list(self._model_files.keys()):
            if file_key == self._module.name:
                continue

            splitted_key = file_key.split("::")
            parent_path = splitted_key[0]
            for part in splitted_key[1:]:
                parent_path += f"::{part}"
                real_path = Path(*parent_path.split("::")) / "_init.cf"
                if parent_path not in self._model_files and not real_path.exists():
                    self._model_files[parent_path] = [
                        DummyModuleElement(parent_path.split("::"))
                    ]

        for file_key in self._model_files.keys():
            self.generate_model_file(
                module_path / "model", file_key, False, copyright_header_template
            )

        if fix_linting:
            utils.fix_module_linting(existing_module)

        return existing_module

    @classmethod
    def from_existing_module(
        cls, existing_module: inmanta.module.Module
    ) -> "InmantaModuleBuilder":
        v1 = existing_module.GENERATION == inmanta.module.ModuleGeneration.V1
        license = existing_module.metadata.license
        module_name = existing_module.name

        return InmantaModuleBuilder(
            module=Module(
                module_name,
                license=license,
            ),
            generation="v1" if v1 else "v2",
            allow_watermark=True,
        )
