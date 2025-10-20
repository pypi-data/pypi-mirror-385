
# db_gpt/models.py
from __future__ import annotations
import io, uuid, numpy as np
from django.db import models
from django.utils import timezone

# ---------- Custom field: stores a NumPy array as bytes (np.save/.load) ----------
class NumpyArrayField(models.BinaryField):
    description = "NumPy array serialized with np.save"

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        bio = io.BytesIO(value)
        return np.load(bio, allow_pickle=False)

    def to_python(self, value):
        if value is None or isinstance(value, np.ndarray):
            return value
        bio = io.BytesIO(value)
        return np.load(bio, allow_pickle=False)

    def get_prep_value(self, value):
        if value is None:
            return None
        if not isinstance(value, np.ndarray):
            raise TypeError("NumpyArrayField expects a numpy.ndarray")
        bio = io.BytesIO()
        np.save(bio, value, allow_pickle=False)
        return bio.getvalue()

# ---------- Core entities ----------
class TrainingRun(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

class ModelConfig(models.Model):
    run = models.OneToOneField(TrainingRun, on_delete=models.CASCADE, related_name="config")
    vocab_size = models.IntegerField(default=259)
    block_size = models.IntegerField(default=256)
    n_layer = models.IntegerField(default=6)
    n_head = models.IntegerField(default=6)
    n_embd = models.IntegerField(default=384)
    dropout = models.FloatField(default=0.0)

class Parameter(models.Model):
    run = models.ForeignKey(TrainingRun, on_delete=models.CASCADE, related_name="parameters")
    layer = models.CharField(max_length=200)
    name = models.CharField(max_length=200)  # e.g. 'weight', 'bias'
    data = NumpyArrayField(null=False)

    class Meta:
        unique_together = [("run", "layer", "name")]

class OptimState(models.Model):
    run = models.ForeignKey(TrainingRun, on_delete=models.CASCADE, related_name="optim_states")
    param_key = models.CharField(max_length=400)  # layer.name key
    state_key = models.CharField(max_length=100)  # e.g. 'exp_avg', 'exp_avg_sq'
    tensor = NumpyArrayField(null=False)

    class Meta:
        unique_together = [("run", "param_key", "state_key")]

class TrainingExample(models.Model):
    run = models.ForeignKey(TrainingRun, on_delete=models.CASCADE, related_name="examples")
    text = models.TextField()

class TrainingStep(models.Model):
    run = models.ForeignKey(TrainingRun, on_delete=models.CASCADE, related_name="steps")
    step = models.BigIntegerField()
    loss = models.FloatField()
    lr = models.FloatField()
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = [("run", "step")]

class Checkpoint(models.Model):
    run = models.ForeignKey(TrainingRun, on_delete=models.CASCADE, related_name="checkpoints")
    label = models.CharField(max_length=200)
    created_at = models.DateTimeField(default=timezone.now)

class ChatSession(models.Model):
    run = models.ForeignKey(TrainingRun, on_delete=models.CASCADE, related_name="sessions")
    session_id = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

class PredictionLog(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages", null=True)
    run = models.ForeignKey(TrainingRun, on_delete=models.CASCADE, related_name="predictions")
    user_text = models.TextField()
    system_prompt = models.TextField(blank=True)
    response_text = models.TextField()
    max_new_tokens = models.IntegerField(default=200)
    temperature = models.FloatField(default=0.9)
    top_k = models.IntegerField(default=50)
    created_at = models.DateTimeField(default=timezone.now)

