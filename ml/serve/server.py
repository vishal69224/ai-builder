"""TinyGPT inference helpers + FastAPI server."""

from __future__ import annotations

import sys
from pathlib import Path

import torch
from fastapi import FastAPI, Request
from pydantic import BaseModel, Field

ML = Path(__file__).resolve().parents[1]
REPO = ML.parent
sys.path.insert(0, str(ML))

from model.tinygpt import TinyGPT, TinyGPTConfig
from tokenizer.specials import load_special_token_map
from tokenizer.wrapper import TinyGPTTokenizer
from train.train_stage import get_device


class GenRequest(BaseModel):
    prompt: str = Field(min_length=1)
    max_new_tokens: int = 256
    temperature: float = 0.4
    top_p: float = 0.9


def load_model(ckpt_path: Path) -> tuple[TinyGPT, TinyGPTTokenizer, dict]:
    device = get_device()
    blob = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    cfg = TinyGPTConfig.from_dict(blob["config"])
    model = TinyGPT(cfg)
    model.load_state_dict(blob["model"])
    model.to(device)
    model.eval()
    tok = TinyGPTTokenizer()
    return model, tok, {"device": str(device), "epoch": blob.get("epoch"), "val_loss": blob.get("val_loss")}


def parse_files(text: str) -> list[dict[str, str]]:
    st = load_special_token_map()
    files = []
    # Split on <|file|>
    parts = text.split(st["file"])
    for part in parts[1:]:
        if st["path"] not in part or st["content"] not in part:
            continue
        after_path = part.split(st["path"], 1)[1]
        path_part, content_part = after_path.split(st["content"], 1)
        path = path_part.strip()
        content = content_part.split(st["eos"])[0]
        if path:
            files.append({"path": path, "content": content})
    return files


@torch.no_grad()
def generate_text(
    model: TinyGPT,
    tok: TinyGPTTokenizer,
    prompt: str,
    mode: str = "comp",
    max_new_tokens: int = 256,
    temperature: float = 0.4,
    top_p: float = 0.9,
) -> str:
    st = load_special_token_map()
    prefix = f"{st['bos']}{st['user']}{prompt.strip()}{st['assistant']}{st[mode]}"
    ids = tok.encode(prefix, add_special_tokens=False)
    device = next(model.parameters()).device
    x = torch.tensor([ids], dtype=torch.long, device=device)
    eos_id = tok.token_to_id(st["eos"])
    out = model.generate(x, max_new_tokens=max_new_tokens, temperature=temperature, top_p=top_p, eos_id=eos_id)
    return tok.decode(out[0].tolist(), skip_special_tokens=False)


def create_app(default_ckpt: Path | None = None) -> FastAPI:
    app = FastAPI(title="TinyGPT Inference", version="0.1.0")
    state: dict = {"model": None, "tok": None, "meta": {}, "ckpt": None}

    def ensure_loaded() -> None:
        if state["model"] is None:
            ckpt = default_ckpt or (REPO / "checkpoints" / "tinygpt-8m-c1" / "best.pt")
            model, tok, meta = load_model(ckpt)
            state.update(model=model, tok=tok, meta=meta, ckpt=str(ckpt))

    @app.get("/v1/health")
    def health():
        ensure_loaded()
        return {
            "ok": True,
            "checkpoint": state["ckpt"],
            "meta": state["meta"],
            "vocab_size": state["tok"].vocab_size,
            "params": state["model"].param_count(),
        }

    def _gen(mode: str, req: GenRequest) -> dict:
        ensure_loaded()
        raw = generate_text(
            state["model"],
            state["tok"],
            req.prompt,
            mode=mode,
            max_new_tokens=req.max_new_tokens,
            temperature=req.temperature,
            top_p=req.top_p,
        )
        files = parse_files(raw)
        return {
            "files": files,
            "raw_text": raw,
            "checkpoint": state["ckpt"],
            "mode": mode,
        }

    async def _parse_body(request: Request) -> GenRequest:
        return GenRequest.model_validate(await request.json())

    @app.post("/v1/generate/component")
    async def gen_comp(request: Request):
        return _gen("comp", await _parse_body(request))

    @app.post("/v1/generate/page")
    async def gen_page(request: Request):
        return _gen("page", await _parse_body(request))

    @app.post("/v1/generate/site")
    async def gen_site(request: Request):
        return _gen("site", await _parse_body(request))

    return app


def main() -> None:
    import uvicorn

    ckpt = REPO / "checkpoints" / "tinygpt-8m-c1" / "best.pt"
    app = create_app(ckpt if ckpt.exists() else None)
    uvicorn.run(app, host="127.0.0.1", port=8100)


if __name__ == "__main__":
    main()
