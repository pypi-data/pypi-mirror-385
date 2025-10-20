import argparse
from main import setup
from main.management.commands import chat, train, init_run

def main():
    parser = argparse.ArgumentParser(description="GPT-DB command-line interface.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # --- Init ---
    p_init = sub.add_parser("init", help="Initialize a new GPT model")
    p_init.add_argument("--name", required=True)
    p_init.add_argument("--block", type=int, default=256)
    p_init.add_argument("--layers", type=int, default=6)
    p_init.add_argument("--heads", type=int, default=6)
    p_init.add_argument("--emb", type=int, default=384)

    # --- Train ---
    p_train = sub.add_parser("train", help="Train a MiniGPT model")
    p_train.add_argument("--name", required=True)
    p_train.add_argument("--steps", type=int, default=1000)
    p_train.add_argument("--batch", type=int, default=8)
    p_train.add_argument("--lr", type=float, default=3e-4)
    p_train.add_argument("--ckpt_every", type=int, default=200)

    # --- Chat ---
    p_chat = sub.add_parser("chat", help="Chat with a MiniGPT model")
    p_chat.add_argument("--name", required=True)
    p_chat.add_argument("--text", required=True)
    p_chat.add_argument("--max_new", type=int, default=200)
    p_chat.add_argument("--temp", type=float, default=0.9)
    p_chat.add_argument("--topk", type=int, default=50)

    args = parser.parse_args()
    setup()

    if args.cmd == "init":
        init_run(
            name=args.name,
            block=args.block,
            layers=args.layers,
            heads=args.heads,
            emb=args.emb,
        )

    elif args.cmd == "train":
        train(
            name=args.name,
            steps=args.steps,
            batch=args.batch,
            lr=args.lr,
            ckpt_every=args.ckpt_every
        )

    elif args.cmd == "chat":
        chat(
            name=args.name,
            text=args.text,
            max_new=args.max_new,
            temp=args.temp,
            topk=args.topk
        )
