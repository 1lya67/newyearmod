package com.example.newyear;

import java.util.Set;

import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.event.player.PlayerBlockBreakEvents;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.LightLayer;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.levelgen.Heightmap;

public class NewYearMod implements ModInitializer {
    public static final String MOD_ID = "newyear";

    /** Радиус вокруг игрока, где ложится снег. */
    private static final int RADIUS = 40;
    /** Сколько случайных клеток за тик проверяется на каждого игрока (больше = быстрее). */
    private static final int ATTEMPTS_PER_PLAYER = 64;

    /** Растения, которые снег закрывает и убирает (проверка по id, чтобы не зависеть от версии). */
    private static final Set<String> COVERABLE = Set.of(
            "short_grass", "tall_grass", "fern", "large_fern", "dead_bush",
            "short_dry_grass", "tall_dry_grass", "bush", "firefly_bush",
            "pink_petals", "wildflowers", "leaf_litter",
            "sunflower", "lilac", "rose_bush", "peony", "pitcher_plant");

    @Override
    public void onInitialize() {
        NewYearBlocks.register();

        // Сломал слой снега -> 10-15 минут на этом месте он не появляется заново.
        PlayerBlockBreakEvents.AFTER.register((world, player, pos, state, blockEntity) -> {
            if (state.is(Blocks.SNOW)) {
                SnowCooldown.block(pos, world.getGameTime(), world.getRandom());
            }
        });

        ServerTickEvents.END_WORLD_TICK.register(world -> {
            if (world.dimension() != Level.OVERWORLD) return;
            SnowCooldown.tick(world.getGameTime());
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

    private static boolean isCoverable(BlockState state) {
        if (state.is(BlockTags.SMALL_FLOWERS)) return true;
        var id = BuiltInRegistries.BLOCK.getKey(state.getBlock());
        return "minecraft".equals(id.getNamespace()) && COVERABLE.contains(id.getPath());
    }

    /** Снег ложится слоем и убирает траву, кусты, цветы и лепестки. */
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
                if (SnowCooldown.isCooling(top)) continue;

                BlockState state = world.getBlockState(top);
                boolean plant = isCoverable(state);
                if (!state.isAir() && !plant) continue;
                if (world.getBrightness(LightLayer.BLOCK, top) >= 10) continue;

                BlockState snow = Blocks.SNOW.defaultBlockState();
                if (!snow.canSurvive(world, top)) continue;

                if (plant && state.hasProperty(BlockStateProperties.DOUBLE_BLOCK_HALF)) {
                    BlockPos above = top.above();
                    if (world.getBlockState(above).is(state.getBlock())) {
                        world.setBlock(above, Blocks.AIR.defaultBlockState(), 2);
                    }
                }
                world.setBlock(top, snow, 3);
            }
        }
    }
}
