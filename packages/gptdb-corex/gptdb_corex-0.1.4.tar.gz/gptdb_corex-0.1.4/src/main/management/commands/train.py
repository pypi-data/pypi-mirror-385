import torch, math
from torch.utils.data import Dataset, DataLoader
from django.core.management.base import BaseCommand
from django.db import transaction
from main.models import TrainingRun, ModelConfig, TrainingExample, TrainingStep, Checkpoint
from main.nn_mini import MiniGPT
from main.tokenizer import ByteTokenizer
from main.db_bridge import load_state_dict, store_state_dict

class TextDataset(Dataset):
    def __init__(self, texts, tok, block=256):
        self.tok = tok; self.block = block
        ids = []
        for t in texts:
            ids.extend(self.tok.encode(t, add_bos=False))
        self.data = torch.tensor(ids, dtype=torch.long)
    def __len__(self):
        return max(0, len(self.data) - self.block - 1)
    def __getitem__(self, i):
        chunk = self.data[i:i+self.block+1]
        x = chunk[:-1]; y = chunk[1:]
        return x, y

class Command(BaseCommand):
    help = "Train the mini GPT using samples stored in DB"

    def add_arguments(self, parser):
        parser.add_argument('--name', required=True, help='TrainingRun name')
        parser.add_argument('--steps', type=int, default=1000)
        parser.add_argument('--batch', type=int, default=8)
        parser.add_argument('--lr', type=float, default=3e-4)
        parser.add_argument('--ckpt_every', type=int, default=200)

    def handle(self, *args, **opts):
        run = TrainingRun.objects.get(name=opts['name'])
        cfg = run.config
        tok = ByteTokenizer()
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        model = MiniGPT(vocab_size=tok.vocab_size, block_size=cfg.block_size,
                        n_layer=cfg.n_layer, n_head=cfg.n_head, n_embd=cfg.n_embd).to(device)
        # load weights from DB
        state = load_state_dict(run)
        model.load_state_dict(state, strict=False)
        opt = torch.optim.AdamW(model.parameters(), lr=opts['lr'], betas=(0.9,0.95), weight_decay=0.1)

        texts = list(run.examples.values_list('text', flat=True))
        ds = TextDataset(texts, tok, cfg.block_size)
        dl = DataLoader(ds, batch_size=opts['batch'], shuffle=True, drop_last=True)

        step = 0
        model.train()
        while step < opts['steps']:
            for x, y in dl:
                x, y = x.to(device), y.to(device)
                _, loss = model(x, y)
                opt.zero_grad(); loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                opt.step()

                # Log to DB
                TrainingStep.objects.update_or_create(
                    run=run, step=step,
                    defaults={"loss": float(loss.item()), "lr": float(opts['lr'])}
                )
                if step % 50 == 0:
                    self.stdout.write(f"step {step} loss {loss.item():.4f}")
                if step % opts['ckpt_every'] == 0 and step > 0:
                    store_state_dict(run, model.state_dict())
                    Checkpoint.objects.create(run=run, label=f"step-{step}")
                step += 1
                if step >= opts['steps']:
                    break
        # Final persist
        store_state_dict(run, model.state_dict())
        Checkpoint.objects.create(run=run, label="final")
        self.stdout.write(self.style.SUCCESS("Training complete and weights saved to DB."))