package com.example.newyear;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.biome.Biomes;

/** Определяет "тёплые" регионы (саванна, болото, мангровое болото, пустыня), где вода не замерзает. */
public final class NewYearBiomes {
    private NewYearBiomes() {}

    /** Проверяем сам биом и четыре точки рядом, чтобы реки среди таких биомов тоже не замерзали. */
    public static boolean isWarmRegion(LevelReader level, BlockPos pos) {
        try {
            return isWarm(level, pos)
                    || isWarm(level, pos.east(12))
                    || isWarm(level, pos.west(12))
                    || isWarm(level, pos.north(12))
                    || isWarm(level, pos.south(12));
        } catch (RuntimeException e) {
            return false;
        }
    }

    private static boolean isWarm(LevelReader level, BlockPos pos) {
        Holder<Biome> biome = level.getBiome(pos);
        return biome.is(Biomes.DESERT)
                || biome.is(Biomes.SAVANNA)
                || biome.is(Biomes.SAVANNA_PLATEAU)
                || biome.is(Biomes.WINDSWEPT_SAVANNA)
                || biome.is(Biomes.SWAMP)
                || biome.is(Biomes.MANGROVE_SWAMP);
    }
}
