"""Train a byte-level BPE tokenizer for TinyGPT (React / Tailwind focused)."""

from __future__ import annotations

import json
from pathlib import Path

from tokenizers import Tokenizer, decoders, models, pre_tokenizers, processors, trainers
from tokenizers.normalizers import NFC

from tokenizer.build_corpus import CORPUS_FILE, build_corpus
from tokenizer.specials import load_special_token_map, special_token_list

ROOT = Path(__file__).resolve().parent
ARTIFACTS = ROOT / "artifacts"
TOKENIZER_JSON = ARTIFACTS / "tokenizer.json"
META_JSON = ARTIFACTS / "tokenizer_meta.json"

VOCAB_SIZE = 16384


def train_tokenizer(vocab_size: int = VOCAB_SIZE) -> Path:
    if not CORPUS_FILE.exists():
        build_corpus()

    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    specials = special_token_list()
    st_map = load_special_token_map()

    tokenizer = Tokenizer(models.BPE(unk_token=None))
    tokenizer.normalizer = NFC()
    # ByteLevel pre-tokenizer: robust for any UTF-8 / code
    tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
    tokenizer.decoder = decoders.ByteLevel()

    trainer = trainers.BpeTrainer(
        vocab_size=vocab_size,
        min_frequency=1,
        special_tokens=specials,
        show_progress=True,
        initial_alphabet=pre_tokenizers.ByteLevel.alphabet(),
    )

    tokenizer.train([str(CORPUS_FILE)], trainer)

    bos_id = tokenizer.token_to_id(st_map["bos"])
    eos_id = tokenizer.token_to_id(st_map["eos"])
    # Template: optional BOS prefix; EOS handled in training data explicitly
    tokenizer.post_processor = processors.TemplateProcessing(
        single=f"{st_map['bos']}:0 $A:0",
        special_tokens=[(st_map["bos"], bos_id)],
    )

    tokenizer.save(str(TOKENIZER_JSON))

    meta = {
        "vocab_size": tokenizer.get_vocab_size(),
        "requested_vocab_size": vocab_size,
        "special_tokens": st_map,
        "special_token_ids": {k: tokenizer.token_to_id(v) for k, v in st_map.items()},
        "tokenizer_path": str(TOKENIZER_JSON),
        "corpus": str(CORPUS_FILE),
        "model_type": "BPE_ByteLevel",
        "phase": 2,
    }
    META_JSON.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta, indent=2))
    return TOKENIZER_JSON


if __name__ == "__main__":
    train_tokenizer()
