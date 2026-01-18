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
    """Serve l'interface web HTML+JS."""
    return """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>YanaChat - Assistant Guyane</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            
            .container {
                width: 100%;
                max-width: 600px;
                background: white;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
                display: flex;
                flex-direction: column;
                height: 80vh;
                max-height: 700px;
            }
            
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 12px 12px 0 0;
                text-align: center;
            }
            
            .header h1 {
                font-size: 24px;
                margin-bottom: 5px;
            }
            
            .header p {
                font-size: 13px;
                opacity: 0.9;
            }
            
            .chat-box {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                background: #f8f9fa;
            }
            
            .message {
                margin-bottom: 15px;
                animation: fadeIn 0.3s ease-in;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .message.user {
                text-align: right;
            }
            
            .message.user .bubble {
                background: #667eea;
                color: white;
            }
            
            .message.assistant .bubble {
                background: #e9ecef;
                color: #333;
            }
            
            .bubble {
                display: inline-block;
                padding: 12px 16px;
                border-radius: 12px;
                max-width: 80%;
                word-wrap: break-word;
                font-size: 14px;
                line-height: 1.4;
            }
            
            .case-badge {
                font-size: 11px;
                margin-top: 5px;
                opacity: 0.7;
                font-weight: bold;
            }
            
            .case-1 { color: #28a745; }
            .case-2 { color: #ffc107; }
            .case-3 { color: #dc3545; }
            
            .input-area {
                padding: 20px;
                border-top: 1px solid #e9ecef;
                display: flex;
                gap: 10px;
            }
            
            .input-area input {
                flex: 1;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 8px;
                font-size: 14px;
                outline: none;
                transition: border-color 0.3s;
            }
            
            .input-area input:focus {
                border-color: #667eea;
            }
            
            .input-area button {
                padding: 12px 24px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-weight: bold;
                transition: transform 0.2s;
            }
            
            .input-area button:hover {
                transform: translateY(-2px);
            }
            
            .input-area button:active {
                transform: translateY(0);
            }
            
            .input-area button:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
            
            .loading {
                display: inline-block;
                width: 8px;
                height: 8px;
                background: #667eea;
                border-radius: 50%;
                animation: pulse 1.5s infinite;
                margin: 0 2px;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 0.3; }
                50% { opacity: 1; }
            }
            
            .stats {
                font-size: 12px;
                padding: 10px;
                background: #f0f0f0;
                border-radius: 8px;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌴 YanaChat</h1>
                <p>Assistant local pour la Guyane</p>
            </div>
            
            <div class="chat-box" id="chatBox"></div>
            
            <div class="input-area">
                <input 
                    type="text" 
                    id="queryInput" 
                    placeholder="Posez une question... (hébergements, transports, services)"
                    autocomplete="off"
                >
                <button id="sendBtn" onclick="sendMessage()">Envoyer</button>
            </div>
        </div>

        <script>
            const chatBox = document.getElementById('chatBox');
            const queryInput = document.getElementById('queryInput');
            const sendBtn = document.getElementById('sendBtn');
            
            let sessionId = 'session_' + Date.now();
            
            // Permet d'envoyer avec Entrée
            queryInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') sendMessage();
            });
            
            async function sendMessage() {
                const query = queryInput.value.trim();
                
                if (!query) {
                    alert('Veuillez entrer une question');
                    return;
                }
                
                if (query.length > 500) {
                    alert('Question trop longue (max 500 caractères)');
                    return;
                }
                
                // Afficher message utilisateur
                addMessage(query, 'user');
                queryInput.value = '';
                sendBtn.disabled = true;
                
                // Afficher indicateur loading
                const loadingDiv = document.createElement('div');
                loadingDiv.className = 'message assistant';
                loadingDiv.innerHTML = '<div class="bubble"><span class="loading"></span><span class="loading"></span><span class="loading"></span></div>';
                chatBox.appendChild(loadingDiv);
                chatBox.scrollTop = chatBox.scrollHeight;
                
                try {
                    // Appel API
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            query: query,
                            session_id: sessionId,
                            top_k: 3
                        })
                    });
                    
                    if (!response.ok) {
                        throw new Error(`Erreur serveur: ${response.status}`);
                    }
                    
                    const data = await response.json();
                    
                    // Supprimer loading
                    chatBox.removeChild(loadingDiv);
                    
                    // Afficher réponse
                    const caseNames = ['?', 'Réponse', 'Précision', 'No data'];
                    const caseClasses = ['', 'case-1', 'case-2', 'case-3'];
                    
                    let responseHtml = `<div class="bubble">
                        ${data.response}
                        <div class="case-badge ${caseClasses[data.case]}">
                            Cas ${data.case}: ${caseNames[data.case]}
                        </div>
                    </div>`;
                    
                    addMessage(responseHtml, 'assistant');
                    
                } catch (error) {
                    chatBox.removeChild(loadingDiv);
                    addMessage(`❌ Erreur: ${error.message}`, 'assistant');
                }
                
                sendBtn.disabled = false;
                queryInput.focus();
            }
            
            function addMessage(content, role) {
                const msgDiv = document.createElement('div');
                msgDiv.className = `message ${role}`;
                
                if (role === 'assistant') {
                    msgDiv.innerHTML = content;
                } else {
                    msgDiv.innerHTML = `<div class="bubble">${escapeHtml(content)}</div>`;
                }
                
                chatBox.appendChild(msgDiv);
                chatBox.scrollTop = chatBox.scrollHeight;
            }
            
            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
            
            // Message de bienvenue
            window.addEventListener('load', () => {
                addMessage("Bonjour! 👋 Je suis YanaChat, votre assistant pour la Guyane. Je peux vous aider avec des informations sur les hébergements, transports, attractions et services. Posez-moi une question!", 'assistant');
            });
        </script>
    </body>
    </html>
    """


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
