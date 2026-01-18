"""
Script de debug pour vérifier l'indexation et la recherche.
"""

from pathlib import Path
from whoosh.index import open_dir
from whoosh.qparser import QueryParser

INDEX_DIR = Path(__file__).parent.parent / "data" / "index"
CORPUS_DIR = Path(__file__).parent.parent / "data" / "corpus"

print("=" * 60)
print("DEBUG INDEXATION")
print("=" * 60)

# 1. Vérifier les fichiers Markdown
print("\n📁 Fichiers Markdown dans corpus :")
md_files = sorted(CORPUS_DIR.glob("*.md"))
for f in md_files:
    size = f.stat().st_size
    print(f"  ✓ {f.name} ({size} bytes)")

# 2. Vérifier l'index
print(f"\n📊 Index dans {INDEX_DIR} :")
if not INDEX_DIR.exists():
    print("  ✗ Index directory doesn't exist!")
else:
    ix = open_dir(str(INDEX_DIR))
    print(f"  ✓ Index trouvé")
    
    # 3. Afficher tous les documents indexés
    print(f"\n📚 Documents indexés :")
    with ix.searcher() as searcher:
        doc_count = ix.doc_count_all()
        print(f"  Total documents : {doc_count}")
        
        # Afficher les 50 premiers résultats pour "guyane"
        from whoosh.qparser import QueryParser
        qp = QueryParser("content", ix.schema)
        query = qp.parse("guyane")
        results = searcher.search(query, limit=50)
        
        print(f"\n  Résultats pour 'guyane' : {len(results)} documents")
        for hit in results[:5]:
            print(f"    - Doc: {hit['doc_id']}, Score: {hit.score:.2f}")
            print(f"      Content preview: {hit['content'][:100]}...")

# 4. Test direct de recherche
print(f"\n🔍 Tests de recherche :")
test_queries = ["dormir", "hebergement", "hotel", "cayenne"]

for q in test_queries:
    with ix.searcher() as searcher:
        qp = QueryParser("content", ix.schema)
        query = qp.parse(q)
        results = searcher.search(query, limit=5)
        print(f"  '{q}' : {len(results)} résultats")
        for r in results[:2]:
            print(f"    - {r['doc_id']}: score={r.score:.2f}")