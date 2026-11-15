package com.example.newyear;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Function;
import java.util.function.UnaryOperator;

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
import net.minecraft.world.level.block.LanternBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;

public final class NewYearBlocks {
    private NewYearBlocks() {}

    public static final String[] LANTERN_COLORS = {"red", "blue", "green", "gold"};
    private static final List<Item> ITEMS = new ArrayList<>();

    private static Identifier id(String path) {
        return Identifier.fromNamespaceAndPath(NewYearMod.MOD_ID, path);
    }

    private static <B extends Block> B block(String path, Function<BlockBehaviour.Properties, B> factory,
                                             UnaryOperator<BlockBehaviour.Properties> tweak) {
        ResourceKey<Block> blockKey = ResourceKey.create(Registries.BLOCK, id(path));
        BlockBehaviour.Properties props = tweak.apply(BlockBehaviour.Properties.of().setId(blockKey));
        B block = Registry.register(BuiltInRegistries.BLOCK, blockKey, factory.apply(props));

        ResourceKey<Item> itemKey = ResourceKey.create(Registries.ITEM, id(path));
        Item item = Registry.register(BuiltInRegistries.ITEM, itemKey,
                new BlockItem(block, new Item.Properties().setId(itemKey)));
        ITEMS.add(item);
        return block;
    }

    public static void register() {
        block("new_year_tree", ChristmasTreeBlock::new,
                p -> p.noOcclusion().strength(0.4F).sound(SoundType.GRASS).lightLevel(s -> 8));

        block("new_year_tree_big", BigChristmasTreeBlock::new,
                p -> p.noOcclusion().strength(0.5F).sound(SoundType.GRASS).lightLevel(s -> 10));

        for (String color : LANTERN_COLORS) {
            block("new_year_lantern_" + color, LanternBlock::new,
                    p -> p.strength(2.0F).sound(SoundType.LANTERN).lightLevel(s -> 13).noOcclusion());
        }

        ItemGroupEvents.modifyEntriesEvent(CreativeModeTabs.FUNCTIONAL_BLOCKS)
                .register(entries -> ITEMS.forEach(item -> entries.accept(item)));
    }
}
