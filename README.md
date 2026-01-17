# YanaChat PoC

PoC minimal: API FastAPI exposant une recherche par mots-clés (BM25) sur contenus YAML locaux.

Run locally (recommended virtualenv):

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Or with Docker Compose:

```bash
docker compose up --build
```

Endpoints:
- `POST /api/query` body `{ "text": "question", "top_k": 5 }`
- `POST /api/content/reload` reload YAML content and reindex
- `GET /health`

UI chat:
- Open `http://localhost:8000/` to use the simple chat UI.

LLM (Mistral) configuration:
- To enable LLM responses, set the environment variables `MISTRAL_API_URL` and `MISTRAL_API_KEY`.
- Example (local run):

```bash
export MISTRAL_API_URL="https://api.mistral.ai/v1/models/<model>/outputs"
export MISTRAL_API_KEY="sk_..."
uvicorn app.main:app --reload --port 8000
```

If the Mistral variables are not set, the service will fallback to returning the top BM25 document text.

Content:
- Add YAML files under `content/local/` with items containing `id`, `title`, `text`, `source`, `intent`.
