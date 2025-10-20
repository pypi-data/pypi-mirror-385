# db_gpt/db_bridge.py
import re, torch, numpy as np
from typing import Dict
from django.db import transaction
from .models import TrainingRun, ModelConfig, Parameter, OptimState

# Helper to make a stable key like 'layers.0.attn.key.weight'
_key_cleaner = re.compile(r"[^a-zA-Z0-9_.]")

def _pkey(layer: str, name: str) -> str:
    return _key_cleaner.sub("_", f"{layer}.{name}")

@transaction.atomic
def store_state_dict(run: TrainingRun, state: Dict[str, torch.Tensor]):
    # Strategy: split keys into (layer, name) by last dot
    for full, tensor in state.items():
        layer, name = full.rsplit('.', 1) if '.' in full else (full, 'weight')
        arr = tensor.detach().cpu().numpy().astype(np.float32, copy=False)
        Parameter.objects.update_or_create(
            run=run, layer=layer, name=name, defaults={"data": arr}
        )

@transaction.atomic
def load_state_dict(run: TrainingRun) -> Dict[str, torch.Tensor]:
    out: Dict[str, torch.Tensor] = {}
    for p in Parameter.objects.filter(run=run).iterator():
        full = f"{p.layer}.{p.name}" if p.name else p.layer
        out[full] = torch.from_numpy(p.data)
    return out

@transaction.atomic
def store_adam_state(run: TrainingRun, adam_state):
    # adam_state is like {param_tensor: {'exp_avg': t, 'exp_avg_sq': t2, ...}}
    # We'll index by the param key present in state_dict
    # Caller must pass a mapping {param_key -> state_dict}
    for param_key, s in adam_state.items():
        for sk, tensor in s.items():
            arr = tensor.detach().cpu().numpy().astype(np.float32, copy=False)
            OptimState.objects.update_or_create(
                run=run, param_key=param_key, state_key=sk, defaults={"tensor": arr}
            )

@transaction.atomic
def load_adam_state(run: TrainingRun):
    result = {}
    for row in OptimState.objects.filter(run=run).iterator():
        result.setdefault(row.param_key, {})[row.state_key] = torch.from_numpy(row.tensor)
    return result