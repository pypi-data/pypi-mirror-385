import torch
import re
from django.core.management.base import BaseCommand, CommandError
from main.models import TrainingRun, ModelConfig, PredictionLog
from main.nn_mini import MiniGPT
from main.tokenizer import ByteTokenizer
from main.db_bridge import load_state_dict

SYSTEM_PROMPT = "You are a helpful assistant."

B_SYS, E_SYS = "<|system|>", "</|system|>"
B_USR, E_USR = "<|user|>", "</|user|>"
B_AST, E_AST = "<|assistant|>", "</|assistant|>"


class Command(BaseCommand):
    """Generate a response using a DB-backed MiniGPT model and log the prediction."""
    help = "Chat with a DB-backed MiniGPT model and log responses into the database."

    def add_arguments(self, parser):
        parser.add_argument('--name', required=True, help='Name of the TrainingRun to use.')
        parser.add_argument('--text', required=True, help='User input text.')
        parser.add_argument('--max_new', type=int, default=200, help='Max new tokens to generate.')
        parser.add_argument('--temp', type=float, default=0.9, help='Sampling temperature.')
        parser.add_argument('--topk', type=int, default=50, help='Top-K sampling cutoff.')

    def handle(self, *args, **opts):
        name = opts['name']
        text = opts['text']
        max_new = opts['max_new']
        temp = opts['temp']
        topk = opts['topk']

        try:
            run = TrainingRun.objects.get(name=name)
        except TrainingRun.DoesNotExist:
            raise CommandError(f"No TrainingRun found with name '{name}'")

        cfg = getattr(run, "config", None)
        if not cfg:
            raise CommandError("TrainingRun is missing an associated ModelConfig.")

        tokenizer = ByteTokenizer()
        device = "cuda" if torch.cuda.is_available() else "cpu"

        # --- Build and load model ---
        model = MiniGPT(
            vocab_size=tokenizer.vocab_size,
            block_size=cfg.block_size,
            n_layer=cfg.n_layer,
            n_head=cfg.n_head,
            n_embd=cfg.n_embd
        ).to(device)

        model.load_state_dict(load_state_dict(run), strict=False)
        model.eval()

        # --- Build prompt ---
        prompt = f"{B_SYS}{SYSTEM_PROMPT}{E_SYS}\n{B_USR}{text}{E_USR}\n{B_AST}"

        # --- Encode and generate ---
        input_ids = tokenizer.encode(prompt, add_bos=True)
        x = torch.tensor([input_ids[-cfg.block_size:]], dtype=torch.long, device=device)

        with torch.no_grad():
            y = model.generate(
                x,
                max_new_tokens=max_new,
                temperature=temp,
                top_k=topk
            )

        out_text = tokenizer.decode(y[0].tolist())

        # --- Extract assistant’s reply safely ---
        start = out_text.find(B_AST) + len(B_AST)
        stop = out_text.find(E_AST, start)
        reply = out_text[start:stop].strip() if stop != -1 else out_text[start:].strip()
        reply = re.split(r"<\|system\|>|<\|user\|>", reply)[0].strip()

        # --- Save log to database ---
        PredictionLog.objects.create(
            run=run,
            system_prompt=SYSTEM_PROMPT,
            user_text=text,
            response_text=reply,
            max_new_tokens=max_new,
            temperature=temp,
            top_k=topk
        )

        self.stdout.write(self.style.SUCCESS(f"\nAssistant:\n{reply}\n"))
