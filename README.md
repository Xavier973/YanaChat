# YanaChat PoC

Chatbot bicouche pour la Guyane française : **Recherche BM25** (Whoosh) + **Politique LLM intelligente** (Mistral API) appliquant 3 cas selon la pertinence du score.

## Architecture

```
Utilisateur → FastAPI (/api/chat) → ChatHandler
          ↓ (étape 1)
      BM25SearchEngine (Whoosh sur data/index/)
          ↓ (étape 2)
      LLMPipeline (Mistral API, politique 3 cas)
          ↓ (étape 3)
      JSONL Logging (logs/interactions.jsonl)
          → Réponse structurée + sources
```

## Quick Start

**Local (recommended with virtualenv):**

```bash
python -m venv .venv
.venv\Scripts\activate             # Windows
# ou: source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

# Générer l'index Whoosh (si corpus modifié)
python src/index_corpus.py

# Lancer l'API
uvicorn app.main:app --reload --port 8000
```

Puis ouvrir `http://localhost:8000/` pour l'interface chat.

**Avec Docker Compose:**

```bash
docker compose up --build
```

## API Endpoints

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/chat` | `POST` | Requête principal. Body: `{ "query": "...", "session_id": "...", "top_k": 3 }` |
| `/api/stats` | `GET` | Statistiques d'utilisation (cas LLM, scores moyens) |
| `/health` | `GET` | Santé de l'API |

**Exemple requête `/api/chat`:**
```json
{
  "query": "Où dormir à Cayenne ?",
  "session_id": "user_abc123",
  "top_k": 3
}
```

**Réponse:**
```json
{
  "case": 1,
  "response": "À Cayenne, vous pouvez séjourner à...",
  "sources": [
    {"name": "Hôtel X", "ville": "Cayenne", "categorie": "Hébergement"}
  ],
  "metadata": {
    "top_score": 2.82,
    "results_count": 1,
    "status": "success"
  }
}
```

## Politique LLM (3 cas)

| Cas | Score BM25 | Comportement |
|-----|-----------|--------------|
| **1** | ≥ 2.0 | Mistral reformule top-3 BM25 avec sources locales (noms, adresses, tél) |
| **2** | 0.5 ≤ score < 2.0 | Demande de précision utilisateur (requête ambiguë) |
| **3** | < 0.5 | Réponse généraliste sans sources (fallback générique) |

## Configuration Mistral

Définir les variables d'environnement pour activer LLM :

```bash
export MISTRAL_API_URL="https://api.mistral.ai/v1"
export MISTRAL_API_KEY="sk_..."
```

Ou dans un fichier `.env` :
```
MISTRAL_API_URL=https://api.mistral.ai/v1
MISTRAL_API_KEY=sk_...
```

**Sans ces variables:** L'API continue de fonctionner en retournant les top résultats BM25 (mode dégradé).

## Corpus & Indexation

### Structure

- **Corpus source:** `data/corpus/` → Markdown par catégorie et localité
  - `01-hebergements.md`, `02-transports.md`, etc.
  - `12-restaurants-cayenne.md`, `13-restaurants-kourou.md`, etc.
  
- **Index Whoosh:** `data/index/` → Généré offline via `python src/index_corpus.py`

### Format Markdown attendu

```markdown
## Cayenne

### Restaurants

#### Le Creole
- Adresse: 123 Rue de la Paix
- Téléphone: +594 594 XXX
- Cuisine: Créole
```

Chaque restaurant crée un document atomique dans l'index avec métadata (ville, catégorie, etc.).

### Mettre à jour le corpus

1. Ajouter/éditer fichiers Markdown dans `data/corpus/`
2. Régénérer l'index: `python src/index_corpus.py`
3. Redémarrer l'API (ou POST `/api/content/reload` si implémenté)

## Logging

Chaque interaction est loggée en **JSONL** dans `logs/interactions.jsonl` :

```json
{
  "timestamp": "2026-01-18T10:30:45",
  "session_id": "user_abc123",
  "user_query": "Où manger à Cayenne ?",
  "search": {"count": 3, "top_score": 2.82},
  "response": {"case": 1, "text": "...", "sources": [...]}
}
```

## Développement

### Tester BM25 isolé

```bash
python src/search_bm25.py    # Script debug = requêtes hardcodées
```

### Vérifier index Whoosh

```bash
python src/debug_index.py    # Inspecter documents indexés
```

### Structure du code

| Fichier | Rôle |
|---------|------|
| `app/main.py` | Endpoints FastAPI (`/api/chat`, `/api/stats`, `/health`) |
| `src/chat_handler.py` | Orchestration requête → réponse + logging |
| `src/search_bm25.py` | Moteur de recherche Whoosh (BM25) |
| `src/llm_pipeline.py` | Politique LLM (3 cas + Mistral) |
| `src/index_corpus.py` | Parser Markdown → Index Whoosh |

## Notes

- ⚠️ **Index statique:** Ajouter docs au runtime n'est pas supporté. Modifier corpus + régénérer.
- ⚠️ **JSONL append-only:** Logs croissent indéfiniment. Prévoir archivage pour production.
- ✅ **Stopwords FR:** Query parser utilise stopwords français pour meilleure pertinence.
