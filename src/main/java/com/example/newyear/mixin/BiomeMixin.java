package com.example.newyear.mixin;

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
}
