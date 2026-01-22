import time
import requests
import statistics
import sys
from pathlib import Path
import yaml

BASE = "http://localhost:8000"
REQUEST_TIMEOUT = 15  # Augmenté de 10s à 30s (API Mistral peut être lente)
DELAY_BETWEEN_REQUESTS = 0.5  # Délai entre requêtes (500ms)


def load_queries():
    """Charge les requêtes depuis test_queries.yaml."""
    queries_file = Path(__file__).parent / "test_queries.yaml"
    
    if not queries_file.exists():
        print(f"❌ Fichier {queries_file} non trouvé")
        sys.exit(1)
    
    with open(queries_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    if not data or 'queries' not in data:
        print(f"❌ Format invalide dans {queries_file}")
        sys.exit(1)
    
    return data['queries']


def make_queries(n=None):
    """Crée les requêtes de test.
    
    Args:
        n: Nombre de requêtes. Si None, utilise toutes les questions du fichier une fois.
           Si > nombre de questions, répète les questions.
    """
    templates = load_queries()
    
    if n is None:
        n = len(templates)  # Par défaut, une seule fois chaque question
    
    qs = []
    for i in range(n):
        q = templates[i % len(templates)]
        qs.append(q)
    return qs, len(templates)


def check_server_health():
    """Vérifie que l'API est accessible."""
    try:
        r = requests.get(f"{BASE}/health", timeout=5)
        if r.status_code == 200:
            print(f"✓ Serveur accessible: {BASE}")
            return True
    except Exception as e:
        print(f"❌ Erreur: Serveur non accessible: {e}")
        print(f"   Démarrez l'API avec: uvicorn app.main:app --reload --port 8000")
        return False


def run(n=None):
    """Lance le test.
    
    Args:
        n: Nombre de requêtes à lancer. 
           - None (défaut) : 1 cycle de toutes les questions
           - int: répète les questions n fois pour tester la charge
    
    Exemples:
        run()          # Toutes les questions (une fois)
        run(50)        # Toutes les questions répétées
    """
    # Vérifier que le serveur est up
    if not check_server_health():
        sys.exit(1)
    
    qs, num_templates = make_queries(n)
    
    if n is None:
        n = num_templates
    
    num_cycles = n // num_templates if n > num_templates else 1
    print(f"\nLancement de {n} requêtes ({num_cycles} cycle(s) × {num_templates} questions)")
    print(f"Timeout={REQUEST_TIMEOUT}s, délai={DELAY_BETWEEN_REQUESTS}s\n")
    latencies = []
    has_sources = 0
    responses = []
    failed_requests = 0

    for i, q in enumerate(qs, start=1):
        payload = {"query": q, "top_k": 3}
        t0 = time.time()
        try:
            r = requests.post(f"{BASE}/api/chat", json=payload, timeout=REQUEST_TIMEOUT)
            elapsed = time.time() - t0
            latencies.append(elapsed)
            
            if r.status_code != 200:
                print(f"  ⚠ Request {i}: HTTP {r.status_code}")
                data = {"case": 0, "response": "", "sources": [], "metadata": {}}
                failed_requests += 1
            else:
                data = r.json()
        except requests.exceptions.Timeout as e:
            elapsed = time.time() - t0
            latencies.append(elapsed)
            print(f"  ⏱ Request {i} timeout ({elapsed:.1f}s): {str(e)[:50]}...")
            data = {"case": 0, "response": "", "sources": [], "metadata": {}}
            failed_requests += 1
        except Exception as e:
            elapsed = time.time() - t0
            latencies.append(elapsed)
            print(f"  ❌ Request {i} failed ({elapsed:.1f}s): {str(e)[:50]}...")
            data = {"case": 0, "response": "", "sources": [], "metadata": {}}
            failed_requests += 1

        responses.append(data)
        if data.get("sources"):
            if len(data.get("sources")) > 0:
                has_sources += 1
        
        # Délai avant la prochaine requête
        if i < len(qs):
            time.sleep(DELAY_BETWEEN_REQUESTS)

    total = len(qs)
    print("\n" + "="*60)
    print("--- Test Summary ---")
    print("="*60)
    print(f"Total requests: {total}")
    print(f"Successful: {total - failed_requests}/{total} ({(total - failed_requests)/total:.1%})")
    print(f"Failed/Timeout: {failed_requests}/{total}")
    print(f"Responses with sources: {has_sources} ({has_sources/total:.1%})")
    print()
    print(f"Latency stats:")
    if latencies:
        print(f"  Median: {statistics.median(latencies):.3f}s")
        print(f"  Mean:   {statistics.mean(latencies):.3f}s")
        print(f"  Min:    {min(latencies):.3f}s")
        print(f"  Max:    {max(latencies):.3f}s")
        if len(latencies) > 20:
            print(f"  P95:    {statistics.quantiles(latencies, n=100)[94]:.3f}s")
    print("="*60)

    print('\nSample responses (first 5):')
    for i, resp in enumerate(responses[:5], start=1):
        print(f"\n#{i}: case={resp.get('case')} | sources={len(resp.get('sources', []))} | status={resp.get('metadata', {}).get('status', 'unknown')}")
        ans = (resp.get('response') or "")[:200]
        print(f"    {ans}...")


if __name__ == '__main__':
    run()