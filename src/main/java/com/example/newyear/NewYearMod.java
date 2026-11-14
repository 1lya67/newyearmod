package com.example.newyear;

import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.minecraft.world.level.Level;

public class NewYearMod implements ModInitializer {
    public static final String MOD_ID = "newyear";

    @Override
    public void onInitialize() {
        // Держим в Верхнем мире постоянный снегопад (без грозы).
        ServerTickEvents.END_WORLD_TICK.register(world -> {
            if (world.dimension() != Level.OVERWORLD) return;
            if (world.getGameTime() % 100L != 0L) return;

            if (!world.isRaining() || world.isThundering()) {
                world.setWeatherParameters(0, 24000, true, false);
            }
        });
    }
}
