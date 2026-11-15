package com.example.newyear;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import net.minecraft.core.BlockPos;
import net.minecraft.util.RandomSource;

/** Места, где игрок сломал снег: там снег не появляется заново 10-15 минут. */
public final class SnowCooldown {
    private static final Map<Long, Long> UNTIL = new ConcurrentHashMap<>();
    private static volatile long now = 0L;

    private SnowCooldown() {}

    public static void tick(long gameTime) {
        now = gameTime;
        if (gameTime % 1200L == 0L) {
            UNTIL.values().removeIf(until -> until <= gameTime);
        }
    }

    /** 12000-18000 тиков = 10-15 минут. */
    public static void block(BlockPos pos, long gameTime, RandomSource random) {
        UNTIL.put(pos.asLong(), gameTime + 12000L + random.nextInt(6001));
    }

    public static boolean isCooling(BlockPos pos) {
        Long until = UNTIL.get(pos.asLong());
        return until != null && now < until;
    }
}
