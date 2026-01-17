
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from .content_loader import ContentLoader
from fastapi.staticfiles import StaticFiles
import requests


app = FastAPI(title="YanaChat PoC API")

# mount static UI (served at root)
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")

loader = ContentLoader(content_path="./content/local")
loader.load_content()


class QueryRequest(BaseModel):
    text: str
    top_k: Optional[int] = 5


def call_mistral(prompt: str) -> Optional[str]:
    """Call the Mistral API using env vars MISTRAL_API_URL and MISTRAL_API_KEY.
    If not configured, return None to indicate fallback behavior."""
    url = os.getenv("MISTRAL_API_URL")
    key = os.getenv("MISTRAL_API_KEY")
    if not url or not key:
        return None
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {"input": prompt}
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=15)
        r.raise_for_status()
        data = r.json()
        # Try common response shapes
        if isinstance(data, dict):
            if "output" in data and isinstance(data["output"], list):
                # join content fields if present
                parts = []
                for item in data["output"]:
                    if isinstance(item, dict):
                        parts.append(item.get("content") or item.get("text") or str(item))
                    else:
                        parts.append(str(item))
                return "\n".join(parts).strip()
            if "choices" in data and data["choices"]:
                c0 = data["choices"][0]
                return c0.get("text") or c0.get("message", {}).get("content") or str(c0)
            # fallback to a top-level text field
            for key in ("text", "result", "output_text"):
                if key in data:
                    return str(data[key])
        return str(data)
    except Exception:
        return None


@app.post('/api/query')
def query(req: QueryRequest):
    if not req.text:
        raise HTTPException(status_code=400, detail="text required")
    results = loader.search(req.text, top_k=req.top_k)
    if not results:
        return {"answer": "Aucune information trouvée.", "sources": [], "intent": "unknown", "confidence": 0.0}

    # Build prompt for the LLM using top results as context
    ctx_parts = []
    sources = []
    for i, d in enumerate(results, start=1):
        title = d.get("title") or d.get("id")
        text = d.get("text", "")
        src = d.get("source")
        sources.append(src) if src else None
        ctx_parts.append(f"[{i}] {title}: {text}")

    context = "\n\n".join(ctx_parts)
    prompt = (
        "You are a concise assistant. Use the provided documents as sources. "
        "Answer the user briefly (<= 2 sentences), and then list the sources used.\n\n"
        f"Documents:\n{context}\n\nUser question: {req.text}\n\nAnswer:" 
    )

    llm_resp = call_mistral(prompt)
    top_doc = results[0]
    confidence = float(top_doc.get('score', 0.0))

    if llm_resp:
        answer = llm_resp.strip()
    else:
        # fallback: return top doc text
        answer = top_doc.get('text')

    return {"answer": answer, "sources": [s for s in sources if s], "intent": top_doc.get('intent', 'info'), "confidence": confidence}


@app.post('/api/content/reload')
def reload_content():
    loader.load_content()
    return {"status": "reloaded", "count": len(loader.docs)}


@app.get('/health')
def health():
    return {"status": "ok", "docs_indexed": len(loader.docs)}
