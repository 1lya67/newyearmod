package com.example.newyear.mixin;

import com.example.newyear.NewYearBiomes;
import com.example.newyear.SnowCooldown;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.biome.Biome;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Во всех биомах: осадки есть, температура "морозная" -> вместо дождя идёт снег. */
@Mixin(Biome.class)
public abstract class BiomeMixin {
    @Inject(method = "hasPrecipitation", at = @At("HEAD"), cancellable = true)
    private void newyear$alwaysPrecipitation(CallbackInfoReturnable<Boolean> cir) {
        cir.setReturnValue(true);
    }

    @Inject(method = "warmEnoughToRain", at = @At("HEAD"), cancellable = true)
    private void newyear$neverWarm(CallbackInfoReturnable<Boolean> cir) {
        cir.setReturnValue(false);
    }

    @Inject(method = "coldEnoughToSnow", at = @At("HEAD"), cancellable = true)
    private void newyear$alwaysCold(CallbackInfoReturnable<Boolean> cir) {
        cir.setReturnValue(true);
    }

    /** Вода не замерзает в пустыне, саванне и болотах (и в реках рядом с ними). */
    @Inject(method = "shouldFreeze(Lnet/minecraft/world/level/LevelReader;Lnet/minecraft/core/BlockPos;Z)Z",
            at = @At("HEAD"), cancellable = true, require = 0)
    private void newyear$keepWaterLiquid3(LevelReader level, BlockPos pos, boolean mustBeAtEdge,
                                          CallbackInfoReturnable<Boolean> cir) {
        if (NewYearBiomes.isWarmRegion(level, pos)) {
            cir.setReturnValue(false);
        }
    }

    @Inject(method = "shouldFreeze(Lnet/minecraft/world/level/LevelReader;Lnet/minecraft/core/BlockPos;)Z",
            at = @At("HEAD"), cancellable = true, require = 0)
    private void newyear$keepWaterLiquid2(LevelReader level, BlockPos pos,
                                          CallbackInfoReturnable<Boolean> cir) {
        if (NewYearBiomes.isWarmRegion(level, pos)) {
            cir.setReturnValue(false);
        }
    }

    /** Ванильный снегопад тоже не должен закрывать место, где игрок только что сломал снег. */
    @Inject(method = "shouldSnow(Lnet/minecraft/world/level/LevelReader;Lnet/minecraft/core/BlockPos;)Z",
            at = @At("HEAD"), cancellable = true, require = 0)
    private void newyear$snowCooldown(LevelReader level, BlockPos pos, CallbackInfoReturnable<Boolean> cir) {
        if (SnowCooldown.isCooling(pos)) {
            cir.setReturnValue(false);
        }
    }
}
