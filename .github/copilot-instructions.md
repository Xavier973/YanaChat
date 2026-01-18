# YanaChat — Instructions pour AI Agents

## Architecture Générale

**YanaChat** est un chatbot PoC bicouche pour la Guyane française :

1. **Couche Recherche (BM25)** — Whoosh indexe le corpus Markdown (`data/corpus/`) en documents atomiques
2. **Couche Réponse (3 cas LLM)** — Mistral API applique une politique stricte selon la pertinence de recherche

```
Utilisateur → FastAPI (/api/chat) → ChatHandler
            ↓ (étape 1)
        BM25SearchEngine (Whoosh sur data/index)
            ↓ (étape 2)
        LLMPipeline (Mistral API, politique 3 cas)
            ↓ (étape 3)
        JSONL Logging (logs/interactions.jsonl)
            → Réponse structurée
```

**Pourquoi 3 cas ?** Limiter les hallucinations : réponse complète seulement si score BM25 ≥ 2.0. Sinon, demander précision (cas 2) ou généralisable (cas 3).

---

## Structure Code

| Dossier | Rôle | Détails |
|---------|------|---------|
| `app/` | Backend FastAPI | `main.py` = endpoints (`/api/chat`, `/api/stats`, `/health`), `content_loader.py` chargement YAML |
| `src/` | Logique métier | `chat_handler.py` = orchestration, `search_bm25.py` = requêtes Whoosh, `llm_pipeline.py` = politique LLM |
| `data/corpus/` | Documents source | Markdown par catégorie (25+ fichiers `{N}-restaurants-*.md`), parsés en entités atomiques |
| `data/index/` | Index Whoosh | Généré par `index_corpus.py`, persistant, réutilisé au runtime |
| `logs/` | Audit | `interactions.jsonl` = chaque requête/réponse loggée (timestamp, session, scores, cas) |

---

## Workflow Clé : Traiter une Requête

### 1. Parser Markdown → Index
**Fichier**: [src/index_corpus.py](src/index_corpus.py)

- Format attendu: Markdown avec hiérarchie `## Ville > ### Catégorie > #### Restaurant`
- Chaque **restaurant** crée un document séparé avec `{doc_id, name, ville, categorie, excerpt, full_text}`
- Schéma Whoosh: `(ID, TEXT, STORED)` pour chaque champ
- Générer index: `python src/index_corpus.py` (crée `data/index/`)

### 2. Recherche BM25 (Étape 1)
**Fichier**: [src/search_bm25.py](src/search_bm25.py)

```python
# Workflow
query → parser avec stopwords FR → requête OR → Whoosh → score + doc_id
# Retourne: Liste de top-k avec score, excerpts, métadata (ville, catégorie)
```

**Seuil flexible**: `score_threshold=0.1` (permissif pour capture), puis filtre par top-k

### 3. Politique LLM — 3 Cas (Étape 2)
**Fichier**: [src/llm_pipeline.py](src/llm_pipeline.py)

```
CAS 1 (score ≥ 2.0)        → Réponse reformulée avec sources locales
                              Mistral reformule le top-3 BM25, cite noms/adresses/tél
                              
CAS 2 (0.5 ≤ score < 2.0)  → Demande de précision
                              Si requête ambiguë (peu de mots OU scores faibles)
                              Demande clarification utilisateur
                              
CAS 3 (score < 0.5)        → Réponse généraliste (pas de sources)
                              Pas de match BM25 → chatbot libre
                              Ne mentionne PAS YanaChat (fallback générique)
```

**Config Mistral**: Variables d'env `.env` `MISTRAL_API_URL` + `MISTRAL_API_KEY`

### 4. Logging Structuré (Étape 3)
**Fichier**: [src/chat_handler.py](src/chat_handler.py#L114) → `_log_interaction()`

Chaque interaction écrite en JSONL avec: `{timestamp, session_id, user_query, search (count/score), response (case/text/sources)}`

---

## Developer Workflows

### Local Dev
```bash
# Setup
python -m venv .venv
.venv\Scripts\activate                    # Windows
pip install -r requirements.txt

# Générer index (une fois ou si corpus changé)
python src/index_corpus.py

# Lancer API
uvicorn app.main:app --reload --port 8000
# UI: http://localhost:8000/
```

### Docker
```bash
docker compose up --build          # Démarre API + volumes persistants
# Logs: docker compose logs -f yana-backend
# Health: curl http://localhost:8000/health
```

### Tester la Recherche Isolée
```bash
python src/search_bm25.py          # Script debug = teste BM25 sur requêtes hardcodées
```

### Mettre à jour le Corpus
1. Ajouter/éditer fichiers Markdown dans `data/corpus/`
2. Régénérer index: `python src/index_corpus.py`
3. Recharger API: `POST /api/content/reload` (redémarre BM25SearchEngine + LLMPipeline)

---

## Patterns Importants

### Pattern 1: Requête Parser Flexible
**Problème**: Utilisateur peut poser une requête vague ("Où manger à Guyane?")

**Solution** [src/search_bm25.py](src/search_bm25.py#L50):
- Extraire mots > 2 chars, exclure stopwords FR
- Construire requête OR (`"manger" OR "guyane"` = plus permissif que AND)
- Si parsing échoue, fallback requête brute

### Pattern 2: Score Threshold ≠ Top-K
**Problème**: BM25 retourne N résultats mais certains inutiles

**Solution** [src/search_bm25.py](src/search_bm25.py#L71):
- Appliquer `score_threshold` (ex: 0.1 = permissif)
- PUIS limiter à `top_k` (ex: 3)
- Raison: Capture tous les matches pertinents, puis sélectionner top-3

### Pattern 3: Métadata Enrichissante
**Problème**: Un restaurant "Le Creole" trouvé, mais sans contexte ville/catégorie

**Solution** [src/index_corpus.py](src/index_corpus.py#L40):
- Parser Markdown préserve **ville** + **categorie** comme champs STORED
- Résultat BM25 inclut `{doc_id, name, ville, categorie, excerpt}`
- Prompt Mistral peut utiliser pour reformulation contextualisée

### Pattern 4: Fallback Gracieux (Cas 3)
**Problème**: Pas de score BM25 ≥ 0.5, impossible de sourcer

**Solution** [src/llm_pipeline.py](src/llm_pipeline.py#L250):
- Cas 3 = LLM répond librement SANS citer sources
- Mistral génère réponse généraliste (ex: "Guyane a 200 restaurants indiens")
- NE PAS tromper l'utilisateur = transparent sur absence de sources locales

---

## Conventions Spécifiques

| Aspect | Convention |
|--------|------------|
| **Logging** | JSONL uniquement (pas de SQL), 1 ligne = 1 interaction |
| **Index** | Régénéré offline via `index_corpus.py`, jamais en runtime |
| **Doc Atomicité** | Chaque restaurant = 1 document (pas 1 fichier = 1 doc) |
| **Score Seuil** | BM25: 0.1 (permissif), Cas1: 2.0, Cas2/3: <2.0 |
| **LLM Limites** | Cas 1 = sources ONLY, Cas 3 = no sources, jamais mix |
| **Markdown Format** | Strict: `##` Ville, `###` Catégorie, `####` Restaurant |

---

## Points Critiques à Respecter

1. **Ne jamais ajouter de docs au runtime**: Index est statique. Ajouter au corpus + régénérer.
2. **BM25 n'est pas un ranker final**: C'est un signal pour la politique LLM. Cas 3 permet fallback.
3. **Mistral API obligatoire pour Cas 1**: Si `.env` incomplet, le service crash. Gérer `LLMPipeline.__init__()` avec try/except.
4. **JSONL append-only**: Logs croissent indéfiniment. Prévoir archivage pour prod.
5. **Stopwords FR vs EN**: Query parser utilise stopwords FR (`où, pas, de, à, ...`). Ne pas oublier pour adaptations.

---

## Debugging Tips

- **Requête silencieuse**: Vérifier `data/index/` existe (run `python src/index_corpus.py`)
- **Score toujours < 0.5**: Corpus vide ou mots-clés mal parsés. Debug avec `python src/search_bm25.py`
- **Erreur Mistral**: `.env` manquant. Consulter `src/llm_pipeline.py:__init__()`
- **JSONL vide**: `logs/` dossier inexistant. Crée auto dans `ChatHandler.__init__()`, mais vérifier permissions
