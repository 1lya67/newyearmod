package com.example.newyear.mixin;

import java.util.ArrayList;
import java.util.List;

import com.example.newyear.NewYearDecorators;
import net.minecraft.world.level.levelgen.feature.configurations.TreeConfiguration;
import net.minecraft.world.level.levelgen.feature.treedecorators.TreeDecorator;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Mutable;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Добавляет гирлянды в конфиг КАЖДОГО дерева (генерация мира и саженцы). */
@Mixin(TreeConfiguration.class)
public abstract class TreeConfigurationMixin {
    @Shadow @Final @Mutable
    public List<TreeDecorator> decorators;

    @Inject(method = "<init>", at = @At("RETURN"))
    private void newyear$addGarland(CallbackInfo ci) {
        List<TreeDecorator> all = new ArrayList<>(this.decorators);
        all.addAll(NewYearDecorators.garland());
        this.decorators = List.copyOf(all);
    }
}
