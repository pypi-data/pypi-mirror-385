# db_gpt/admin.py
from django.contrib import admin
from .models import (
    TrainingRun, ModelConfig, Parameter,
    OptimState, TrainingExample, TrainingStep,
    
    Checkpoint, PredictionLog
)

# ---------- Inlines ----------

class ModelConfigInline(admin.StackedInline):
    model = ModelConfig
    extra = 0


class ParameterInline(admin.TabularInline):
    model = Parameter
    extra = 0
    readonly_fields = ("layer", "name")
    fields = ("layer", "name")
    can_delete = False


class OptimStateInline(admin.TabularInline):
    model = OptimState
    extra = 0
    readonly_fields = ("param_key", "state_key")
    fields = ("param_key", "state_key")
    can_delete = False


class TrainingExampleInline(admin.TabularInline):
    model = TrainingExample
    extra = 0
    fields = ("text",)


class TrainingStepInline(admin.TabularInline):
    model = TrainingStep
    extra = 0
    fields = ("step", "loss", "lr", "timestamp")


class CheckpointInline(admin.TabularInline):
    model = Checkpoint
    extra = 0
    fields = ("label", "created_at")


# ---------- Main Admin Models ----------
@admin.register(TrainingRun)
class TrainingRunAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "notes")
    search_fields = ("name", "notes")
    inlines = [
        ModelConfigInline,
        ParameterInline,
        OptimStateInline,
        TrainingExampleInline,
        TrainingStepInline,
        CheckpointInline,
    ]


@admin.register(PredictionLog)
class PredictionLogAdmin(admin.ModelAdmin):
    list_display = ("run", "created_at", "user_text_short", "response_short", "temperature", "top_k")
    list_filter = ("run", "created_at")
    search_fields = ("user_text", "response_text")

    def user_text_short(self, obj):
        return (obj.user_text[:70] + "...") if len(obj.user_text) > 70 else obj.user_text
    user_text_short.short_description = "User Text"

    def response_short(self, obj):
        return (obj.response_text[:70] + "...") if len(obj.response_text) > 70 else obj.response_text
    response_short.short_description = "Response"


@admin.register(TrainingStep)
class TrainingStepAdmin(admin.ModelAdmin):
    list_display = ("run", "step", "loss", "lr", "timestamp")
    list_filter = ("run",)
    search_fields = ("run__name",)
    ordering = ("-timestamp",)


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    list_display = ("run", "layer", "name")
    search_fields = ("run__name", "layer", "name")


@admin.register(OptimState)
class OptimStateAdmin(admin.ModelAdmin):
    list_display = ("run", "param_key", "state_key")
    search_fields = ("run__name", "param_key", "state_key")


@admin.register(Checkpoint)
class CheckpointAdmin(admin.ModelAdmin):
    list_display = ("run", "label", "created_at")
    list_filter = ("run", "created_at")


@admin.register(TrainingExample)
class TrainingExampleAdmin(admin.ModelAdmin):
    list_display = ("run", "text_short")
    search_fields = ("text", "run__name")

    def text_short(self, obj):
        return (obj.text[:80] + "...") if len(obj.text) > 80 else obj.text
    text_short.short_description = "Text"
