"""
Main — A self-contained GPT database engine built with Django + Torch.
Auto-configures SQLite, runs migrations, and provides a GPT interface.
"""

from .apps import MainConfig

__all__ = ["GPT", "MainConfig", "setup", "auto_run", "train_run", "chat_run"]


def setup(sqlite_path: str = "gptdb.sqlite3", auto_migrate: bool = True):
    """
    Allow running without a Django project (standalone mode).

    Args:
        sqlite_path (str): Path to the SQLite database file.
        auto_migrate (bool): Automatically run migrations if True.
    """
    from django.conf import settings

    if not settings.configured:
        settings.configure(
            INSTALLED_APPS=[
                "django.contrib.contenttypes",
                "django.contrib.auth",
                "main",
            ],
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": sqlite_path,
                }
            },
            USE_TZ=True,
            TIME_ZONE="UTC",
            SECRET_KEY="gptdb-standalone",
            DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        )

        import django
        django.setup()

        if auto_migrate:
            from django.core.management import call_command
            call_command("migrate", interactive=False, run_syncdb=True, verbosity=0)

    print(f"✅ GPT-DB setup complete (SQLite: {sqlite_path})")

    # Lazy import to ensure Django is ready
    global GPT
    from .nn_mini import MiniGPT as GPT


# Auto-load if already in a Django project
try:
    from django.conf import settings
    if settings.configured:
        from .nn_mini import MiniGPT as GPT
except Exception:
    pass


# ============================================================
# 🚀 Generic Utility Functions
# ============================================================
from django.core.management import call_command


def auto_run(name="demo", steps=300, text="Hello!"):
    """
    🚀 Fully automatic setup, seeding (if needed), training, and chatting.
    """
    setup()
    from main.models import TrainingRun, TrainingExample

    run, created = TrainingRun.objects.get_or_create(name=name)
    if created:
        print(f"🧠 Created new TrainingRun '{name}'")
        call_command("init_run", "--name", name)
    else:
        print(f"♻️ Reusing existing TrainingRun '{name}'")

    # Add some sample data if none exist
    if not run.examples.exists():
        TrainingExample.objects.bulk_create([
            TrainingExample(run=run, text="<|system|>You are a helpful assistant.</|system|>\n<|user|>Hello!</|user|>\n<|assistant|>Hi! How can I help?</|assistant|>"),
            TrainingExample(run=run, text="<|system|>You are a helpful assistant.</|system|>\n<|user|>Tell me something interesting.</|user|>\n<|assistant|>Did you know honey never spoils?</|assistant|>"),
            TrainingExample(run=run, text="<|system|>You are a helpful assistant.</|system|>\n<|user|>Who created you?</|user|>\n<|assistant|>I was trained with GPT-DB Core.</|assistant|>"),
        ])
        print("✅ Added default examples.")
    else:
        print("📚 Using existing training examples.")

    train_run(name, steps)
    chat_run(name, text)


def train_run(name="demo", steps=500):
    """
    🧩 Train an existing GPT-DB model using examples from the database.
    """
    setup()
    print(f"🧠 Training run '{name}' for {steps} steps...")
    call_command("train", "--name", name, "--steps", str(steps))
    print("✅ Training complete.")


def chat_run(name="demo", text="Hello!"):
    """
    💬 Generate a response from a trained GPT-DB model.
    """
    setup()
    print(f"💬 Chatting with '{name}'...")
    call_command("chat", "--name", name, "--text", text)
