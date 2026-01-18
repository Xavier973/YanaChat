import os
import glob
import yaml
from rank_bm25 import BM25Okapi
from typing import List, Dict


class ContentLoader:
    def __init__(self, content_path: str = './content/local'):
        self.content_path = content_path
        self.docs: List[Dict] = []
        self.bm25 = None
        self.corpus_tokens = []

    def load_content(self):
        self.docs = []
        files = glob.glob(os.path.join(self.content_path, '*.yaml'))
        for fp in files:
            try:
                with open(fp, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if isinstance(data, list):
                        items = data
                    else:
                        items = [data]
                    for item in items:
                        doc = {
                            'id': item.get('id') or os.path.basename(fp),
                            'title': item.get('title', ''),
                            'text': item.get('text', ''),
                            'source': item.get('source', ''),
                            'intent': item.get('intent', 'info')
                        }
                        self.docs.append(doc)
            except Exception:
                continue
        # build BM25
        self.corpus_tokens = [self._tokenize(d['text']) for d in self.docs]
        if self.corpus_tokens:
            self.bm25 = BM25Okapi(self.corpus_tokens)

    def _tokenize(self, text: str):
        return text.lower().split()

    def search(self, query: str, top_k: int = 5):
        if not self.bm25:
            return []
        q_tokens = self._tokenize(query)
        scores = self.bm25.get_scores(q_tokens)
        ranked = sorted([{'doc': d, 'score': float(scores[i])} for i, d in enumerate(self.docs)], key=lambda x: x['score'], reverse=True)
        ranked = [r for r in ranked if r["score"] > 0.0]
        results = []
        for r in ranked[:top_k]:
            doc = r['doc'].copy()
            doc['score'] = r['score']
            results.append(doc)
        return results
