"""
FastAPI Backend pour YanaChat.
Endpoints: POST /api/chat, GET /api/stats, GET /health
"""

import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from starlette.responses import FileResponse
from pydantic import BaseModel

# Ajouter src au path Python
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from chat_handler import get_chat_handler

# Initialiser FastAPI
app = FastAPI(
    title="YanaChat API",
    description="Chatbot local pour la Guyane (BM25 + Mistral LLM)",
    version="0.1.0"
)


# ============================================================
# Modèles Pydantic
# ============================================================

class ChatRequest(BaseModel):
    """Requête de chat."""
    query: str
    session_id: Optional[str] = None
    top_k: Optional[int] = 3


class ChatResponse(BaseModel):
    """Réponse de chat."""
    case: int
    response: str
    sources: list
    metadata: dict


class StatsResponse(BaseModel):
    """Statistiques d'utilisation."""
    total_queries: int
    by_case: dict
    avg_search_score: float
    case_1_rate: str


# ============================================================
# Endpoints
# ============================================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint principal de chat.
    
    **Requête :**
    ```json
    {
      "query": "Où dormir à Cayenne?",
      "session_id": "user123",
      "top_k": 3
    }
    ```
    
    **Réponse :**
    ```json
    {
      "case": 1,
      "response": "Pour dormir à Cayenne...",
      "sources": [],
      "metadata": {
        "top_score": 2.82,
        "results_count": 1,
        "status": "success"
      }
    }
    ```
    """
    try:
        # Valider requête
        if not request.query or len(request.query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Query ne peut pas être vide")
        
        if len(request.query) > 500:
            raise HTTPException(status_code=400, detail="Query trop longue (max 500 chars)")
        
        # Obtenir chat handler
        handler = get_chat_handler()
        
        # Traiter requête
        result = handler.handle_query(
            user_query=request.query,
            top_k=request.top_k or 3,
            session_id=request.session_id
        )
        
        # Formater réponse
        return ChatResponse(
            case=result['case'],
            response=result['response'],
            sources=result.get('sources', []),
            metadata=result.get('metadata', {})
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur /api/chat: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")


@app.get("/api/stats", response_model=StatsResponse)
async def stats():
    """
    Retourne les statistiques d'utilisation.
    
    **Réponse :**
    ```json
    {
      "total_queries": 5,
      "by_case": {
        "case_1_answer": 5,
        "case_2_clarification": 0,
        "case_3_refusal": 0
      },
      "avg_search_score": 4.05,
      "case_1_rate": "100.0%"
    }
    ```
    """
    try:
        handler = get_chat_handler()
        stats_data = handler.get_stats()
        
        if "error" in stats_data:
            return StatsResponse(
                total_queries=0,
                by_case={"case_1_answer": 0, "case_2_clarification": 0, "case_3_refusal": 0},
                avg_search_score=0.0,
                case_1_rate="0%"
            )
        
        return StatsResponse(**stats_data)
    
    except Exception as e:
        print(f"❌ Erreur /api/stats: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")


@app.get("/health")
async def health_check():
    """
    Health check simple.
    
    **Réponse :**
    ```json
    {
      "status": "ok",
      "service": "YanaChat"
    }
    ```
    """
    return {
        "status": "ok",
        "service": "YanaChat",
        "version": "0.1.0"
    }


# ============================================================
# Frontend HTML (serveur statique)
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Servez l'interface web depuis un fichier statique."""
    index_path = Path(__file__).parent / "static" / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=500, detail="index.html manquant dans app/static/")
    return FileResponse(str(index_path))

# Monter les fichiers statiques (si besoin pour assets futurs)
app.mount(
    "/static",
    StaticFiles(directory=str(Path(__file__).parent / "static")),
    name="static"
)


# ============================================================
# Démarrage
# ============================================================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🚀 Démarrage YanaChat API")
    print("="*60)
    print("✓ Endpoint: http://localhost:8000")
    print("✓ API Docs: http://localhost:8000/docs")
    print("✓ Frontend: http://localhost:8000/")
    print("="*60 + "\n")
    
    uvicorn.run(
        "main:app",  # ← Module path au lieu d'objet app
        host="0.0.0.0",
        port=8000,
        reload=True,  # ← Auto-reload activé
        log_level="info"
    )
