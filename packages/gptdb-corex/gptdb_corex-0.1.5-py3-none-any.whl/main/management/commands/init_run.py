# db_gpt/management/commands/gpt_init.py
from django.core.management.base import BaseCommand
from main.models import TrainingRun, ModelConfig
from main.nn_mini import MiniGPT
from main.db_bridge import store_state_dict

class Command(BaseCommand):
    help = "Create a TrainingRun and initialize model parameters in DB"

    def add_arguments(self, parser):
        parser.add_argument('--name', required=True)
        parser.add_argument('--block', type=int, default=256)
        parser.add_argument('--layers', type=int, default=6)
        parser.add_argument('--heads', type=int, default=6)
        parser.add_argument('--emb', type=int, default=384)

    def handle(self, *args, **opts):
        run, created = TrainingRun.objects.get_or_create(name=opts['name'])
        if created:
            self.stdout.write(self.style.SUCCESS(f"Initialized run '{run.name}' with fresh weights."))
        else:
            self.stdout.write(self.style.WARNING(f"⚠️ Run '{run.name}' already exists — reusing existing weights."))
            return
        
        cfg = ModelConfig.objects.create(
            run=run,
            block_size=opts['block'], n_layer=opts['layers'], n_head=opts['heads'], n_embd=opts['emb']
        )
        model = MiniGPT(vocab_size=259, block_size=cfg.block_size, n_layer=cfg.n_layer,
                        n_head=cfg.n_head, n_embd=cfg.n_embd)
        store_state_dict(run, model.state_dict())
        self.stdout.write(self.style.SUCCESS(f"Initialized run '{run.name}' with fresh weights."))