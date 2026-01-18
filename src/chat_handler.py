"""
Orchestrateur BM25 + LLM.
Reçoit une requête utilisateur et retourne réponse (Cas 1/2/3).
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from search_bm25 import get_search_engine
from llm_pipeline import get_llm_pipeline


# Configuration logging
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Handler pour fichier JSON
log_file = LOGS_DIR / "interactions.jsonl"
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)


class ChatHandler:
    """Gère le flux complet: requête → BM25 → LLM → réponse."""
    
    def __init__(self):
        """Initialise les composants BM25 et LLM."""
        self.search_engine = get_search_engine()
        self.llm_pipeline = get_llm_pipeline()
        print("✓ ChatHandler initialisé (BM25 + LLM)")
    
    def handle_query(
        self,
        user_query: str,
        top_k: int = 3,
        score_threshold: float = 1.0,
        session_id: str = None
    ) -> Dict:
        """
        Traite une requête utilisateur end-to-end.
        
        Args:
            user_query (str): Question utilisateur
            top_k (int): Nombre de résultats BM25 à considérer
            score_threshold (float): Seuil de pertinence BM25
            session_id (str): ID de session pour tracking
        
        Returns:
            dict: {
                'case': 1|2|3,
                'response': str,
                'sources': [urls],
                'metadata': {...}
            }
        """
        
        timestamp = datetime.utcnow().isoformat()
        
        print(f"\n{'='*60}")
        print(f"[{timestamp}] Requête: {user_query}")
        print('='*60)
        
        # Étape 1 : Recherche BM25
        print(f"  [1/3] Recherche BM25...")
        search_results = self.search_engine.search(
            user_query,
            top_k=top_k,
            score_threshold=0.1  # Seuil permissif pour capture
        )
        
        print(f"  → {len(search_results)} résultats trouvés")
        for r in search_results[:3]:
            print(f"    - {r['doc_id']}: score={r['score']:.2f}")
        
        # Étape 2 : Pipeline LLM (politique de réponse)
        print(f"  [2/3] Pipeline LLM...")
        result = self.llm_pipeline.process(
            user_query,
            search_results,
            score_threshold=score_threshold
        )
        
        case_name = ["Aucun", "Réponse", "Précision", "Refus"][result['case']]
        print(f"  → Cas {result['case']}: {case_name}")
        
        # Étape 3 : Logging
        print(f"  [3/3] Logging...")
        self._log_interaction(
            user_query,
            search_results,
            result,
            timestamp,
            session_id
        )
        
        print(f"  ✓ Réponse générée")
        print('='*60)
        
        return result
    
    def _log_interaction(
        self,
        user_query: str,
        search_results: List[Dict],
        result: Dict,
        timestamp: str,
        session_id: str = None
    ) -> None:
        """
        Enregistre l'interaction en JSON.
        
        Args:
            user_query (str): Requête utilisateur
            search_results (List[Dict]): Résultats BM25
            result (Dict): Résultat du pipeline LLM
            timestamp (str): Timestamp ISO
            session_id (str): ID de session
        """
        
        # Préparer données de log
        log_entry = {
            "timestamp": timestamp,
            "session_id": session_id or "unknown",
            "user_query": user_query,
            "search": {
                "results_count": len(search_results),
                "top_result": search_results[0]['doc_id'] if search_results else None,
                "top_score": search_results[0]['score'] if search_results else 0
            },
            "response": {
                "case": result['case'],
                "text": result['response'][:500],  # Limiter la taille
                "sources": result.get('sources', []),
                "metadata": result.get('metadata', {})
            }
        }
        
        # Écrire dans fichier JSONL
        try:
            with open(LOGS_DIR / "interactions.jsonl", "a", encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            print(f"  ✓ Interaction loggée")
        except Exception as e:
            print(f"  ⚠️ Erreur logging: {e}")
    
    def get_stats(self) -> Dict:
        """
        Retourne statistiques d'utilisation depuis les logs.
        
        Returns:
            dict: {total_queries, by_case, avg_search_score, ...}
        """
        
        if not log_file.exists():
            return {"error": "Aucun log trouvé"}
        
        total = 0
        by_case = {1: 0, 2: 0, 3: 0}
        scores = []
        
        try:
            with open(log_file, "r", encoding='utf-8') as f:
                for line in f:
                    entry = json.loads(line.strip())
                    total += 1
                    by_case[entry['response']['case']] += 1
                    if entry['search']['top_score'] > 0:
                        scores.append(entry['search']['top_score'])
            
            return {
                "total_queries": total,
                "by_case": {
                    "case_1_answer": by_case[1],
                    "case_2_clarification": by_case[2],
                    "case_3_refusal": by_case[3]
                },
                "avg_search_score": sum(scores) / len(scores) if scores else 0,
                "case_1_rate": f"{100 * by_case[1] / total:.1f}%" if total > 0 else "N/A"
            }
        except Exception as e:
            return {"error": str(e)}


# Instance globale
chat_handler = None


def get_chat_handler() -> ChatHandler:
    """Retourne l'instance globale du chat handler."""
    global chat_handler
    if chat_handler is None:
        chat_handler = ChatHandler()
    return chat_handler


if __name__ == "__main__":
    # Test complet
    handler = get_chat_handler()
    
    test_queries = [
        "Où dormir pas cher à Cayenne?",
        "Bus depuis l'aéroport",
        "Comment faire la pizza?",
        "Musées à Cayenne",
        "Urgences médicales",
    ]
    
    print("\n" + "🔄 TEST CHAT HANDLER COMPLET" + "\n")
    
    for i, q in enumerate(test_queries, start=1):
        result = handler.handle_query(q, session_id=f"test_session_{i}")
        print(f"\nRéponse (Cas {result['case']}):")
        print(f"  {result['response'][:150]}...")
    
    # Afficher stats
    print("\n" + "="*60)
    print("📊 STATISTIQUES")
    print("="*60)
    stats = handler.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")