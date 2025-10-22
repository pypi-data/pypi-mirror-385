from __future__ import annotations
from mcdplib.core.resource import ResourceRegistry, ResourceBuilder, Resource
from mcdplib.core.identifier import Identifier
from mcdplib.core.text import TextLike
from mcdplib.core.file import write_json_file
import shutil
import os

PackFormatLike = int | tuple[int] | tuple[int, int]


class PackInformation:
    def __init__(self, min_format: PackFormatLike, max_format: PackFormatLike, description: TextLike):
        self.min_format: PackFormatLike = min_format
        self.max_format: PackFormatLike = max_format
        self.description: TextLike = description

    def build(self) -> dict:
        return {
            "description": self.description,
            "min_format": self.min_format,
            "max_format": self.max_format
        }


class Pack:
    def __init__(self, information: PackInformation, local_registries_directory: str):
        self.information: PackInformation = information
        self.local_registries_directory: str = local_registries_directory

        self.resource_builders: list[ResourceBuilder] = list()
        self.__registries: dict[str, ResourceRegistry] = dict()

    def get_registry(self, name: str) -> ResourceRegistry:
        if name not in self.__registries:
            raise KeyError(f"Registry with name {name} does not exist")
        return self.__registries[name]

    def get_registries(self) -> list[ResourceRegistry]:
        return list(self.__registries.values())

    def add_registry(self, registry: ResourceRegistry) -> ResourceRegistry:
        if registry.name in self.__registries:
            raise KeyError(f"Registry with name {registry.name} already exists")
        self.__registries[registry.name] = registry
        return registry

    def build_pack_mcmeta(self) -> dict:
        pack_mcmeta: dict = {
            "pack": self.information.build()
        }
        return pack_mcmeta

    def load(self, data_directory: str) -> None:
        def load_resource_builders_in_directory(directory: str, parent_name: str | None = None) -> list[ResourceBuilder]:
            resource_builders: list[ResourceBuilder] = list()
            for local_entry in os.listdir(directory):
                entry: str = f"{directory}/{local_entry}"
                if os.path.isdir(entry):
                    child_name: str = local_entry
                    if parent_name is not None:
                        child_name = f"{parent_name}/{local_entry}"
                    resource_builders.extend(load_resource_builders_in_directory(entry, child_name))
                elif os.path.isfile(entry):
                    local_name, extension = os.path.splitext(local_entry)
                    extension = extension.removeprefix(".")
                    name: str = local_name
                    if parent_name is not None:
                        name = f"{parent_name}/{local_name}"
                    for resource_builder_loader in registry.resource_builder_loaders:
                        if extension in resource_builder_loader.file_extensions:
                            resource_builders.append(resource_builder_loader.load(directory, entry, registry.name, Identifier(namespace, name)))
            return resource_builders

        for registry in self.__registries.values():
            for namespace in os.listdir(data_directory):
                namespace_directory: str = f"{data_directory}/{namespace}"
                registry_directory: str = f"{namespace_directory}/{registry.name}"
                if not os.path.exists(registry_directory):
                    continue
                self.resource_builders.extend(load_resource_builders_in_directory(registry_directory))

    def build(self, context: dict, pack_field: str | None = "pack", resource_builder_field: str | None = "resource_builder") -> None:
        if pack_field is not None:
            context[pack_field] = self
        for resource_builder in self.resource_builders:
            if resource_builder_field is not None:
                context[resource_builder_field] = resource_builder
            resources: list[Resource] = resource_builder.build(context)
            for resource in resources:
                self.get_registry(resource.registry).add(resource)

    def write(self, directory: str) -> None:
        os.makedirs(directory, exist_ok=True)
        write_json_file(f"{directory}/pack.mcmeta", self.build_pack_mcmeta())
        registries_directory = f"{directory}/{self.local_registries_directory}"
        if os.path.exists(registries_directory):
            shutil.rmtree(registries_directory)
        for registry in self.__registries.values():
            registry.write(registries_directory)
