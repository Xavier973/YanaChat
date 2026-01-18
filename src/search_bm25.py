"""
Moteur de recherche BM25 avec Whoosh.
Encapsule la logique de recherche et scoring.
"""

from pathlib import Path
from whoosh.index import open_dir
from whoosh.qparser import QueryParser, QueryParserError, OrGroup

# Configuration
INDEX_DIR = Path(__file__).parent.parent / "data" / "index"


class BM25SearchEngine:
    """Moteur de recherche BM25 basé sur Whoosh."""
    
    def __init__(self, index_dir=INDEX_DIR):
        """Initialise le moteur de recherche."""
        self.index_dir = Path(index_dir)
        self.ix = None
        self._load_index()
    
    def _load_index(self):
        """Charge l'index Whoosh existant."""
        if not self.index_dir.exists():
            raise FileNotFoundError(f"Index directory not found: {self.index_dir}")
        
        try:
            self.ix = open_dir(str(self.index_dir))
            print(f"✓ Index chargé depuis {self.index_dir}")
        except Exception as e:
            raise RuntimeError(f"Erreur chargement index: {e}")
    
    def search(self, query_text, top_k=3, score_threshold=0.1):
        """
        Recherche dans le corpus avec BM25.
        
        Args:
            query_text (str): Requête utilisateur
            top_k (int): Nombre de résultats à retourner
            score_threshold (float): Score minimum requis
        
        Returns:
            list: Liste de dictionnaires {score, doc_id, excerpt, ...}
        """
        
        if not self.ix:
            return []
        
        try:
            with self.ix.searcher() as searcher:
                # Parser de requête avec mode OR (plus permissif)
                query_parser = QueryParser("content", self.ix.schema, group=OrGroup)
                query_parser.allow_wildcards = True
                
                # Extraire tous les mots significatifs
                stopwords = {
                    'où', 'pas', 'de', 'à', 'un', 'le', 'la', 'et', 'ou', 'pour', 
                    'en', 'que', 'ce', 'qui', 'je', 'tu', 'il', 'elle', 'nous', 
                    'vous', 'ils', 'elles', 'je', 'cherche', 'un', 'une', 'sur'
                }
                words = query_text.lower().split()
                keywords = [w for w in words if w not in stopwords and len(w) > 2]
                
                # Si tous les mots sont des stopwords, utiliser la requête brute
                if not keywords:
                    keywords = words
                
                # Construire requête OR (plus flexible)
                query_text_or = " OR ".join(keywords)
                
                try:
                    query = query_parser.parse(query_text_or)
                except QueryParserError as e:
                    # Fallback : utiliser la requête brute
                    query = query_parser.parse(query_text)
                
                # Exécuter la recherche
                results = searcher.search(query, limit=None)
                
                print(f"  🔍 Trouvé {len(results)} résultats pour: {query_text}")
                
                # Filtrer par seuil et top_k
                filtered_results = []
                for hit in results:
                    if hit.score >= score_threshold:
                        filtered_results.append({
                            "score": hit.score,
                            "doc_id": hit["doc_id"],
                            "name": hit.get("name", ""),
                            "doc_type": hit.get("doc_type", "unknown"),
                            "ville": hit.get("ville", ""),
                            "categorie": hit.get("categorie", ""),
                            "excerpt": hit.get("excerpt", "")[:200] + "..."
                        })
                
                print(f"  ✓ Retour {len(filtered_results)} résultats filtrés")
                return filtered_results[:top_k]
        
        except Exception as e:
            print(f"✗ Erreur recherche BM25: {e}")
            import traceback
            traceback.print_exc()
            return []


# Instance globale
search_engine = None


def get_search_engine():
    """Retourne l'instance globale du moteur de recherche."""
    global search_engine
    if search_engine is None:
        try:
            search_engine = BM25SearchEngine()
        except Exception as e:
            print(f"❌ Impossible de charger le moteur de recherche: {e}")
            return None
    return search_engine


if __name__ == "__main__":
    # Test simple
    print("\n" + "="*60)
    print("🧪 Test du moteur BM25")
    print("="*60 + "\n")
    
    engine = get_search_engine()
    
    if not engine:
        print("❌ Moteur de recherche indisponible")
        exit(1)
    
    test_queries = [
        "restaurant Kourou",
        "Où manger créole à Cayenne",
        "fruits de mer",
        "hôtel pas cher",
        "aéroport transport",
    ]
    
    for q in test_queries:
        print(f"\n🔍 Requête: '{q}'")
        results = engine.search(q, top_k=2)
        if results:
            for i, r in enumerate(results, 1):
                print(f"  {i}. [{r['score']:.2f}] {r['name'][:50]}")
                print(f"     Doc: {r['doc_id']}")
        else:
            print("  ✗ Aucun résultat")
    
    print("\n" + "="*60 + "\n")