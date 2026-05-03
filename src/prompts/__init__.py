from pathlib import Path


PROMPTS_DIR = Path(__file__).resolve().parent


def load_prompt(filename: str) -> str:
    """Load an agent prompt from the prompts directory."""
    return (PROMPTS_DIR / filename).read_text(encoding="utf-8").strip()
