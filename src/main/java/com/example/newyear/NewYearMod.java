package com.example.newyear;

import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.LightLayer;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;

public class NewYearMod implements ModInitializer {
    public static final String MOD_ID = "newyear";

    /** Радиус вокруг игрока, где ложится снег. */
    private static final int RADIUS = 40;
    /** Сколько случайных клеток за тик проверяется на каждого игрока (больше = быстрее). */
    private static final int ATTEMPTS_PER_PLAYER = 64;

    @Override
    public void onInitialize() {
        NewYearBlocks.register();

        ServerTickEvents.END_WORLD_TICK.register(world -> {
            if (world.dimension() != Level.OVERWORLD) return;
            keepSnowing(world);
            coverGroundWithSnow(world);
        });
    }

    /** Держим в Верхнем мире постоянный снегопад (без грозы). */
    private static void keepSnowing(ServerLevel world) {
        if (world.getGameTime() % 100L != 0L) return;
        if (!world.isRaining() || world.isThundering()) {
            world.setWeatherParameters(0, 24000, true, false);
        }
    }

    /** Снег ложится слоем и убирает траву, папоротники и сухие кусты. */
    private static void coverGroundWithSnow(ServerLevel world) {
        if (!world.isRaining()) return;
        RandomSource random = world.getRandom();

        for (ServerPlayer player : world.players()) {
            BlockPos center = player.blockPosition();
            for (int i = 0; i < ATTEMPTS_PER_PLAYER; i++) {
                BlockPos column = center.offset(
                        random.nextInt(RADIUS * 2 + 1) - RADIUS, 0,
                        random.nextInt(RADIUS * 2 + 1) - RADIUS);
                if (!world.hasChunkAt(column)) continue;

                BlockPos top = world.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING, column);
                BlockState state = world.getBlockState(top);

                boolean tallPlant = state.is(Blocks.TALL_GRASS) || state.is(Blocks.LARGE_FERN);
                boolean plant = tallPlant
                        || state.is(Blocks.SHORT_GRASS)
                        || state.is(Blocks.FERN)
                        || state.is(Blocks.DEAD_BUSH);
                if (!state.isAir() && !plant) continue;
                if (world.getBrightness(LightLayer.BLOCK, top) >= 10) continue;

                BlockState snow = Blocks.SNOW.defaultBlockState();
                if (!snow.canSurvive(world, top)) continue;

                if (tallPlant) {
                    world.setBlock(top.above(), Blocks.AIR.defaultBlockState(), 2);
                }
                world.setBlock(top, snow, 3);
            }
        }
    }
}
