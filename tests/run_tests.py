import time
import requests
import statistics

BASE = "http://localhost:8000"

templates = [
    ("Office du Tourisme", ["office", "tourisme", "cayenne"]),
    ("Plage Montjoly informations", ["plage", "montjoly"]),
    ("Horaires Office du Tourisme", ["horaires", "ouvert"]),
    ("Où est l'office du tourisme?", ["place des palmistes", "cayenne"]),
    ("Contact office tourisme Cayenne", ["contact", "+594"]),
    ("Que faire à Montjoly?", ["kitesurf", "plage"]),
    ("Adresse office du tourisme Cayenne", ["place des palmistes"]),
    ("Informations événements locaux Cayenne", ["événements", "brochures"]),
    ("Parking Montjoly", ["parking"]),
    ("Protection solaire plage", ["protection solaire"]),
]

def make_queries(n=100):
    qs = []
    for i in range(n):
        tpl, keys = templates[i % len(templates)]
        qs.append((tpl, keys))
    return qs


def run(n=100):
    qs = make_queries(n)
    latencies = []
    has_sources = 0
    correct = 0
    responses = []

    for i, (q, keys) in enumerate(qs, start=1):
        payload = {"text": q, "top_k": 3}
        t0 = time.time()
        try:
            r = requests.post(f"{BASE}/api/query", json=payload, timeout=10)
            elapsed = time.time() - t0
            latencies.append(elapsed)
            data = r.json()
        except Exception as e:
            print(f"Request {i} failed: {e}")
            latencies.append(10.0)
            data = {"answer": "", "sources": [], "intent": "error", "confidence": 0.0}

        responses.append(data)
        if data.get("sources"):
            if len(data.get("sources")) > 0:
                has_sources += 1
        ans = (data.get("answer") or "").lower()
        # heuristic: if any expected key in answer -> count correct
        if any(k.lower() in ans for k in keys):
            correct += 1

    total = len(qs)
    print("--- Test summary ---")
    print(f"Total requests: {total}")
    print(f"Responses with sources: {has_sources} ({has_sources/total:.2%})")
    print(f"Heuristic precision: {correct}/{total} ({correct/total:.2%})")
    print(f"Latency median: {statistics.median(latencies):.3f}s")
    print(f"Latency mean: {statistics.mean(latencies):.3f}s")
    print(f"Latency p95: {statistics.quantiles(latencies, n=100)[94]:.3f}s")

    print('\nSample responses (first 5):')
    for i, resp in enumerate(responses[:5], start=1):
        print(f"#{i}: intent={resp.get('intent')} confidence={resp.get('confidence')}")
        print(resp.get('answer'))
        print('sources=', resp.get('sources'))
        print('---')


if __name__ == '__main__':
    run(100)
