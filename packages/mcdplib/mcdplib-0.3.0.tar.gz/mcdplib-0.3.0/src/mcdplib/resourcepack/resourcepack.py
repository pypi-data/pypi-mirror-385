from mcdplib import BinaryResource, StaticBinaryResourceBuilderLoader
from mcdplib.core.resource.resource_object import ObjectResource, StaticObjectResourceBuilderLoader, DynamicObjectResourceBuilderLoader
from mcdplib.core.pack import Pack, PackInformation
from mcdplib.core.resource.resource import ResourceRegistry


class Resourcepack(Pack):
    def __init__(self, information: PackInformation):
        super().__init__(information, "assets")

        # TODO 20.10.2025: Add shaders support
        # TODO 20.10.2025: Add texts support
        # TODO 21.10.2025: Add gpu_warnlist.json support
        # TODO 21.10.2025: Add regional_compliancies.json support
        # TODO 21.10.2025: Add sounds.json support

        self.sounds: ResourceRegistry = ResourceRegistry(
            name="sounds",
            allowed_resource_types=[BinaryResource],
            file_extension="ogg",
            resource_builder_loaders=[
                StaticBinaryResourceBuilderLoader(
                    file_extensions=["ogg"]
                )
            ]
        )

        self.textures: ResourceRegistry = ResourceRegistry(
            name="textures",
            allowed_resource_types=[BinaryResource],
            file_extension="png",
            resource_builder_loaders=[
                StaticBinaryResourceBuilderLoader(
                    file_extensions=["png"]
                )
            ]
        )

        def create_object_resource_registry(registry_name: str) -> ResourceRegistry:
            return self.add_registry(ResourceRegistry(
                name=registry_name,
                allowed_resource_types=[ObjectResource],
                file_extension="json",
                resource_builder_loaders=[
                    StaticObjectResourceBuilderLoader(
                        file_extensions=["json"]
                    ),
                    DynamicObjectResourceBuilderLoader(
                        file_extensions=["py"]
                    )
                ]
            ))

        self.atlases: ResourceRegistry = create_object_resource_registry("atlases")
        self.blockstates: ResourceRegistry = create_object_resource_registry("blockstates")
        self.equipment: ResourceRegistry = create_object_resource_registry("equipment")
        self.font: ResourceRegistry = create_object_resource_registry("font")
        self.items: ResourceRegistry = create_object_resource_registry("items")
        self.lang: ResourceRegistry = create_object_resource_registry("lang")
        self.models: ResourceRegistry = create_object_resource_registry("models")
        self.particles: ResourceRegistry = create_object_resource_registry("particles")
        self.post_effects: ResourceRegistry = create_object_resource_registry("post_effect")
        self.waypoint_styles: ResourceRegistry = create_object_resource_registry("waypoint_style")
