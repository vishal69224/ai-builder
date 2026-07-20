"""Thin wrapper around the trained Hugging Face Tokenizer."""

from __future__ import annotations

from pathlib import Path

from tokenizers import Tokenizer

from tokenizer.specials import load_special_token_map

ARTIFACTS = Path(__file__).resolve().parent / "artifacts"
DEFAULT_PATH = ARTIFACTS / "tokenizer.json"


class TinyGPTTokenizer:
    def __init__(self, path: Path | str = DEFAULT_PATH) -> None:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(
                f"Tokenizer not found at {path}. Run: python -m tokenizer.train_tokenizer"
            )
        self.tokenizer = Tokenizer.from_file(str(path))
        self.specials = load_special_token_map()

    @property
    def vocab_size(self) -> int:
        return self.tokenizer.get_vocab_size()

    def encode(self, text: str, add_special_tokens: bool = True) -> list[int]:
        return self.tokenizer.encode(text, add_special_tokens=add_special_tokens).ids

    def decode(self, ids: list[int], skip_special_tokens: bool = False) -> str:
        return self.tokenizer.decode(ids, skip_special_tokens=skip_special_tokens)

    def token_to_id(self, token: str) -> int | None:
        return self.tokenizer.token_to_id(token)

    def id_to_token(self, idx: int) -> str | None:
        return self.tokenizer.id_to_token(idx)
