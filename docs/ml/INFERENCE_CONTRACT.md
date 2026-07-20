# Inference API Contract (Design)

Base URL: `http://127.0.0.1:8100` (separate from FastAPI `:8000`)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/v1/health` | Model loaded? device? |
| POST | `/v1/generate/component` | C1 |
| POST | `/v1/generate/page` | C2 |
| POST | `/v1/generate/site` | C3 |

### Request (site)

```json
{
  "prompt": "Build a coffee shop website",
  "max_new_tokens": 2048,
  "temperature": 0.4,
  "top_p": 0.95
}
```

### Response

```json
{
  "files": [{"path": "src/App.tsx", "content": "..."}],
  "raw_text": "...",
  "checkpoint": "tinygpt-8m-c3-best",
  "stats": {"tokens": 1200, "ms": 8000}
}
```

Implementation: **Phase 6**. Product wiring: **Phase 9**.
