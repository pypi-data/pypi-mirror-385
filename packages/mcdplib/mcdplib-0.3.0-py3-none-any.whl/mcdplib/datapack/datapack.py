from __future__ import annotations
from mcdplib.core.resource.resource import Resource, ResourceBuilder, ResourceRegistry
from mcdplib.core.resource.resource_binary import BinaryResource, StaticBinaryResourceBuilderLoader
from mcdplib.core.resource.resource_object import ObjectResource, StaticObjectResourceBuilderLoader, DynamicObjectResourceBuilderLoader
from mcdplib.core.resource.resource_string import StringResource, StaticStringResourceBuilderLoader
from mcdplib.datapack.function import FunctionResourceBuilderLoader
from mcdplib.core.pack import Pack, PackInformation
from mcdplib.datapack.function_template import FunctionTemplateResourceBuilderLoader


class Datapack(Pack):
    def __init__(self, information: PackInformation):
        super().__init__(information, "data")

        self.functions: ResourceRegistry = self.add_registry(ResourceRegistry(
            name="function",
            allowed_resource_types=[StringResource],
            file_extension="mcfunction",
            resource_builder_loaders=[
                StaticStringResourceBuilderLoader(
                    file_extensions=["mcfunction"]
                ),
                FunctionResourceBuilderLoader(
                    file_extensions=["mcf"]
                ),
                FunctionTemplateResourceBuilderLoader(
                    file_extensions=["mcft"]
                )
            ]
        ))
        self.structures: ResourceRegistry = self.add_registry(ResourceRegistry(
            name="structure",
            allowed_resource_types=[BinaryResource],
            file_extension="nbt",
            resource_builder_loaders=[StaticBinaryResourceBuilderLoader(
                file_extensions=["nbt"]
            )]
        ))

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

        self.banner_pattern_tags: ResourceRegistry = create_object_resource_registry("tags/banner_pattern")
        self.block_tags: ResourceRegistry = create_object_resource_registry("tags/block")
        self.damage_type_tags: ResourceRegistry = create_object_resource_registry("tags/damage_type")
        self.dialog_tags: ResourceRegistry = create_object_resource_registry("tags/dialog")
        self.enchantment_tags: ResourceRegistry = create_object_resource_registry("tags/enchantment")
        self.entity_type_tags: ResourceRegistry = create_object_resource_registry("tags/entity_type")
        self.fluid_tags: ResourceRegistry = create_object_resource_registry("tags/fluid")
        self.function_tags: ResourceRegistry = create_object_resource_registry("tags/function")
        self.game_event_tags: ResourceRegistry = create_object_resource_registry("tags/game_event")
        self.instrument_tags: ResourceRegistry = create_object_resource_registry("tags/instrument")
        self.item_tags: ResourceRegistry = create_object_resource_registry("tags/item")
        self.painting_variant_tags: ResourceRegistry = create_object_resource_registry("tags/painting_variant")
        self.point_of_interest_type_tags: ResourceRegistry = create_object_resource_registry("tags/point_of_interest_type")
        self.worldgen_biome_tags: ResourceRegistry = create_object_resource_registry("tags/worldgen/biome")
        self.worldgen_flat_level_generator_preset_tags: ResourceRegistry = create_object_resource_registry("tags/worldgen/flat_level_generator_preset")
        self.worldgen_structure_tags: ResourceRegistry = create_object_resource_registry("tags/worldgen/structure")
        self.worldgen_world_preset_tags: ResourceRegistry = create_object_resource_registry("tags/worldgen/world_preset")

        self.advancements: ResourceRegistry = create_object_resource_registry("advancement")
        self.banner_patterns: ResourceRegistry = create_object_resource_registry("banner_pattern")
        self.cat_variants: ResourceRegistry = create_object_resource_registry("cat_variant")
        self.chat_types: ResourceRegistry = create_object_resource_registry("chat_type")
        self.chicken_variants: ResourceRegistry = create_object_resource_registry("chicken_variant")
        self.cow_variants: ResourceRegistry = create_object_resource_registry("cow_variant")
        self.damage_types: ResourceRegistry = create_object_resource_registry("damage_type")
        self.dialogs: ResourceRegistry = create_object_resource_registry("dialog")
        self.dimensions: ResourceRegistry = create_object_resource_registry("dimension")
        self.dimension_types: ResourceRegistry = create_object_resource_registry("dimension_type")
        self.enchantments: ResourceRegistry = create_object_resource_registry("enchantment")
        self.enchantment_providers: ResourceRegistry = create_object_resource_registry("enchantment_provider")
        self.frog_variants: ResourceRegistry = create_object_resource_registry("frog_variant")
        self.instruments: ResourceRegistry = create_object_resource_registry("instrument")
        self.item_modifiers: ResourceRegistry = create_object_resource_registry("item_modifier")
        self.jukebox_songs: ResourceRegistry = create_object_resource_registry("jukebox_song")
        self.loot_tables: ResourceRegistry = create_object_resource_registry("loot_table")
        self.painting_variants: ResourceRegistry = create_object_resource_registry("painting_variant")
        self.pig_variants: ResourceRegistry = create_object_resource_registry("pig_variant")
        self.predicates: ResourceRegistry = create_object_resource_registry("predicate")
        self.recipes: ResourceRegistry = create_object_resource_registry("recipe")
        self.test_environments: ResourceRegistry = create_object_resource_registry("test_environment")
        self.test_instances: ResourceRegistry = create_object_resource_registry("test_instance")
        self.trial_spawners: ResourceRegistry = create_object_resource_registry("trial_spawner")
        self.trim_materials: ResourceRegistry = create_object_resource_registry("trim_material")
        self.trim_patterns: ResourceRegistry = create_object_resource_registry("trim_pattern")
        self.wolf_sound_variants: ResourceRegistry = create_object_resource_registry("wolf_sound_variant")
        self.wolf_variants: ResourceRegistry = create_object_resource_registry("wolf_variant")

        self.worldgen_biomes: ResourceRegistry = create_object_resource_registry("worldgen/biome")
        self.worldgen_configured_carvers: ResourceRegistry = create_object_resource_registry("worldgen/configured_carver")
        self.worldgen_configured_features: ResourceRegistry = create_object_resource_registry("worldgen/configured_feature")
        self.worldgen_density_functions: ResourceRegistry = create_object_resource_registry("worldgen/density_function")
        self.worldgen_noises: ResourceRegistry = create_object_resource_registry("worldgen/noise")
        self.worldgen_noise_settings: ResourceRegistry = create_object_resource_registry("worldgen/noise_settings")
        self.worldgen_placed_features: ResourceRegistry = create_object_resource_registry("worldgen/placed_feature")
        self.worldgen_processor_lists: ResourceRegistry = create_object_resource_registry("worldgen/processor_list")
        self.worldgen_structures: ResourceRegistry = create_object_resource_registry("worldgen/structure")
        self.worldgen_structure_sets: ResourceRegistry = create_object_resource_registry("worldgen/structure_set")
        self.worldgen_template_pools: ResourceRegistry = create_object_resource_registry("worldgen/template_pool")
        self.worldgen_world_presets: ResourceRegistry = create_object_resource_registry("worldgen/world_preset")
        self.worldgen_flat_level_generator_presets: ResourceRegistry = create_object_resource_registry("worldgen/flat_level_generator_preset")
        self.worldgen_multi_noise_biome_source_parameter_lists: ResourceRegistry = create_object_resource_registry("worldgen/multi_noise_biome_source_parameter_list")
