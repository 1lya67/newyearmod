package com.example.newyear;

import net.fabricmc.fabric.api.itemgroup.v1.ItemGroupEvents;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;

public final class NewYearBlocks {
    private NewYearBlocks() {}

    public static final ResourceKey<Block> TREE_BLOCK_KEY = ResourceKey.create(
            Registries.BLOCK, Identifier.fromNamespaceAndPath(NewYearMod.MOD_ID, "new_year_tree"));
    public static final ResourceKey<Item> TREE_ITEM_KEY = ResourceKey.create(
            Registries.ITEM, Identifier.fromNamespaceAndPath(NewYearMod.MOD_ID, "new_year_tree"));

    public static Block TREE_BLOCK;
    public static Item TREE_ITEM;

    public static void register() {
        TREE_BLOCK = Registry.register(BuiltInRegistries.BLOCK, TREE_BLOCK_KEY,
                new ChristmasTreeBlock(BlockBehaviour.Properties.of()
                        .setId(TREE_BLOCK_KEY)
                        .noOcclusion()
                        .strength(0.4F)
                        .sound(SoundType.GRASS)
                        .lightLevel(state -> 8)));

        TREE_ITEM = Registry.register(BuiltInRegistries.ITEM, TREE_ITEM_KEY,
                new BlockItem(TREE_BLOCK, new Item.Properties().setId(TREE_ITEM_KEY)));

        ItemGroupEvents.modifyEntriesEvent(CreativeModeTabs.FUNCTIONAL_BLOCKS)
                .register(entries -> entries.accept(TREE_ITEM));
    }
}
