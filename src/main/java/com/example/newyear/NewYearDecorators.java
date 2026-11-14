package com.example.newyear;

import java.util.List;

import net.minecraft.core.Direction;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.feature.stateproviders.BlockStateProvider;
import net.minecraft.world.level.levelgen.feature.treedecorators.AttachedToLeavesDecorator;
import net.minecraft.world.level.levelgen.feature.treedecorators.TreeDecorator;

/** Светящиеся "шары" разных цветов, которые свисают с нижних листьев. */
public final class NewYearDecorators {
    private static final float CHANCE = 0.06F;

    private NewYearDecorators() {}

    private static TreeDecorator bauble(Block block) {
        // шанс, радиус-XZ, радиус-Y, блок, свободных блоков под листвой, направления
        return new AttachedToLeavesDecorator(
                CHANCE, 1, 1, BlockStateProvider.simple(block), 1, List.of(Direction.DOWN));
    }

    public static List<TreeDecorator> garland() {
        return List.of(
                bauble(Blocks.SHROOMLIGHT),         // тёплый красно-оранжевый
                bauble(Blocks.OCHRE_FROGLIGHT),     // жёлтый
                bauble(Blocks.VERDANT_FROGLIGHT),   // зелёный
                bauble(Blocks.PEARLESCENT_FROGLIGHT), // розово-фиолетовый
                bauble(Blocks.SEA_LANTERN)          // холодный белый
        );
    }
}
