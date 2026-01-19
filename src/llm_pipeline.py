"""
Pipeline LLM avec politique de réponse stricte (3 cas).
Intègre Mistral API avec reformulation et refus contrôlés.
"""

import os
import requests
from pathlib import Path
from typing import Optional, Dict, List
from enum import Enum

# Charger .env au démarrage
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class ResponseCase(Enum):
    """Cas de réponse selon la politique."""
    CASE_1_ANSWER = "Réponse autorisée avec sources locales"
    CASE_2_CLARIFICATION = "Demande de précision"
    CASE_3_GENERALISTE = "Réponse généraliste (pas de sources)"


class LLMPipeline:
    """Pipeline LLM avec politique de réponse stricte (3 cas)."""
    
    def __init__(self):
        """Initialise le pipeline avec credentials Mistral."""
        self.api_url = os.getenv("MISTRAL_API_URL")
        self.api_key = os.getenv("MISTRAL_API_KEY")
        
        if not self.api_url or not self.api_key:
            raise RuntimeError(
                "❌ Mistral API non configurée. "
                "Définir MISTRAL_API_URL et MISTRAL_API_KEY dans .env"
            )
        
        print(f"✓ LLMPipeline initialisé (Mistral API)")
    
    def _call_mistral(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """
        Appel API Mistral avec gestion d'erreur.
        
        Args:
            system_prompt (str): Prompt système
            user_prompt (str): Prompt utilisateur
        
        Returns:
            Optional[str]: Réponse Mistral ou None si erreur
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "mistral-small-latest",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3
        }
        
        try:
            r = requests.post(self.api_url, headers=headers, json=payload, timeout=20)
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"].strip()
        except requests.exceptions.Timeout:
            print("⚠️ Timeout Mistral API (20s)")
            return None
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Erreur requête Mistral: {e}")
            return None
        except Exception as e:
            print(f"⚠️ Erreur parsing réponse Mistral: {e}")
            return None
    
    def process(
        self,
        user_query: str,
        search_results: List[Dict],
        score_threshold: float = 1.0
    ) -> Dict:
        """
        Traite la requête selon la politique de réponse (3 cas).
        
        Args:
            user_query (str): Requête utilisateur
            search_results (List[Dict]): Résultats BM25
            score_threshold (float): Seuil de pertinence minimum
        
        Returns:
            Dict: {
                'case': 1|2|3,
                'response': str,
                'sources': [urls],
                'metadata': {...}
            }
        """
        
        # Cas 1 : Résultats pertinents (score >= 2.0) ET sémantiquement proches
        if search_results and search_results[0]['score'] >= 2.0:
            pertinent_results = [r for r in search_results if r['score'] >= score_threshold]
            if pertinent_results:
                # Vérifier que les résultats sont sémantiquement pertinents
                if self._is_semantically_relevant(user_query, pertinent_results):
                    return self._case_1_answer(user_query, pertinent_results)
                else:
                    # Score haut mais pas pertinent sémantiquement → Cas 3
                    return self._case_3_generaliste(user_query)
        
        # Cas 2 : Résultats faibles/ambigus (0.5 <= score < 2.0)
        if search_results and 0.5 <= search_results[0]['score'] < 2.0:
            # Vérifier ambiguïté
            if self._is_ambiguous(user_query, search_results):
                return self._case_2_clarification(user_query)
        
        # Cas 3 : Aucun résultat pertinent → Chatbot généraliste
        return self._case_3_generaliste(user_query)
    
    def _is_ambiguous(self, query: str, results: List[Dict]) -> bool:
        """
        Détecte si la requête est ambiguë malgré des résultats.
        
        Args:
            query (str): Requête utilisateur
            results (List[Dict]): Résultats de recherche
        
        Returns:
            bool: True si ambiguë
        """
        word_count = len(query.split())
        avg_score = sum(r['score'] for r in results) / len(results) if results else 0
        
        return word_count < 5 and avg_score < 1.5
    
    def _is_semantically_relevant(self, query: str, results: List[Dict]) -> bool:
        """
        Vérifie que les résultats sont sémantiquement pertinents pour la requête.
        Détecte les faux positifs BM25 (ex: restaurants trouvés pour "vaccins").
        
        Politique différenciée :
        - Documents génériques (07-culture, 01-hebergements, etc.) : acceptés si score ≥ 2.0
        - Restaurants : validation stricte (au moins 30% des mots-clés match)
        
        Args:
            query (str): Requête utilisateur
            results (List[Dict]): Résultats de recherche
        
        Returns:
            bool: True si les résultats sont pertinents
        """
        if not results:
            return False
        
        top_result = results[0]
        doc_id = top_result.get('doc_id', '')
        
        # Documents génériques : pas de validation stricte
        # Exemples: "07-culture", "01-hebergements", "02-transports", etc.
        generic_docs = {'01-hebergements', '02-transports', '03-attractions', 
                        '04-administrations', '05-services', '06-entreprises', '07-culture'}
        
        is_generic = any(doc_id.startswith(prefix) for prefix in generic_docs)
        
        if is_generic:
            # Pour documents génériques, faire confiance à BM25 si score ≥ 2.0
            print(f"  ✓ Document générique accepté : {doc_id}")
            return True
        
        # Pour restaurants : validation stricte
        # Extraire les mots-clés de la requête
        query_lower = query.lower()
        query_words = set(word.strip('.,!?;:') for word in query_lower.split() if len(word) > 2)
        
        # Vérifier que les excerpts contiennent des mots de la requête
        excerpt_concat = " ".join([r.get('excerpt', '').lower() for r in results]).lower()
        
        # Besoin d'une couverture minimum des mots-clés
        matches = sum(1 for word in query_words if word in excerpt_concat)
        coverage = matches / len(query_words) if query_words else 0
        
        # Au moins 30% des mots-clés doivent être dans les excerpts
        if coverage < 0.3:
            print(f"  ⚠️ Faible pertinence sémantique ({coverage:.0%}): '{query_words}' vs excerpts")
            return False
        
        print(f"  ✓ Pertinence sémantique validée ({coverage:.0%})")
        return True
    
    def _case_1_answer(
        self,
        user_query: str,
        search_results: List[Dict]
    ) -> Dict:
        """
        **Cas 1 — Réponse avec sources locales**
        
        Reformule la réponse à partir des sources locales.
        Le LLM ne peut pas ajouter d'information externe.
        """
        
        # PRIORITÉ : Mettre les documents génériques avant les restaurants
        # Raison : requête "Est-ce qu'il y a beaucoup de chinois" veut info démographique,
        # pas une liste de restaurants
        generic_docs = {'01-hebergements', '02-transports', '03-attractions', 
                        '04-administrations', '05-services', '06-entreprises', '07-culture'}
        
        def is_generic(result):
            doc_id = result.get('doc_id', '')
            return any(doc_id.startswith(prefix) for prefix in generic_docs)
        
        # Séparer et retrier : génériques d'abord (par score), puis restaurants
        generic_results = sorted([r for r in search_results if is_generic(r)], 
                                key=lambda x: x.get('score', 0), reverse=True)
        restaurant_results = sorted([r for r in search_results if not is_generic(r)], 
                                   key=lambda x: x.get('score', 0), reverse=True)
        
        # Recombiner : génériques + restaurants (max 3 total)
        prioritized_results = generic_results + restaurant_results
        
        # Construire contexte à partir des résultats triés
        context_parts = []
        sources = []
        
        for i, result in enumerate(prioritized_results[:3], start=1):  # Top-3 avec priorité génériques
            excerpt = result.get('excerpt', result.get('content', ''))
            
            # Limiter à 500 caractères pour avoir des infos concrètes
            if len(excerpt) > 500:
                excerpt = excerpt[:500] + "..."
            
            doc_id = result.get('doc_id', 'unknown')
            website = result.get('website', '')
            google_maps = result.get('google_maps', '')
            
            # Ajouter les liens au contexte si disponibles
            links_info = ""
            if website:
                links_info += f"\nSite web: {website}"
            if google_maps:
                links_info += f"\nGoogle Maps: {google_maps}"
            
            context_parts.append(f"[Source {i} - {doc_id}]\n{excerpt}{links_info}")
            sources.append({
                'doc_id': doc_id,
                'score': result.get('score', 0),
                'website': website,
                'google_maps': google_maps
            })
        
        context = "\n\n".join(context_parts)
        
        system_prompt = (
            "Tu es un assistant spécialisé dans les informations sur la Guyane française. "
            "Réponds TOUJOURS en utilisant UNIQUEMENT les informations fournies dans les sources. "
            "Si la requête parle de démographie, culture, ou faits généraux sur la Guyane, "
            "privilégie les documents génériques (07-culture, etc.) pour des réponses riches et détaillées. "
            "Si c'est une recherche de restaurant/service, utilise les sources structurées. "
            "Cite TOUS les détails concrets (nombres, pourcentages, noms, localisations, communautés, langues). "
            "Sois précis et exhaustif, ne résume pas à une ligne. "
            "CRUCIAL : Inclus les liens (site web, Google Maps) si disponibles. "
            "Format : liste numérotée si plusieurs entrées, sinon paragraphes structurés."
        )
        
        user_prompt = (
            f"Sources disponibles:\n{context}\n\n"
            f"Question de l'utilisateur: {user_query}\n\n"
            f"Utilise les informations ci-dessus pour répondre de manière concrète et utile."
        )
        
        llm_response = self._call_mistral(system_prompt, user_prompt)
        
        if not llm_response:
            # Fallback : utiliser le premier excerpt
            llm_response = search_results[0].get('excerpt', '(Pas de reformulation disponible)')
        
        return {
            "case": 1,
            "response": llm_response,
            "sources": sources,
            "metadata": {
                "top_score": search_results[0]['score'],
                "results_count": len(search_results),
                "status": "success",
                "source_type": "local"
            }
        }
    
    def _case_2_clarification(self, user_query: str) -> Dict:
        """
        **Cas 2 — Demande de précision**
        
        La requête est ambiguë ou trop générale.
        Demander à l'utilisateur de clarifier.
        """
        
        system_prompt = (
            "Tu es un assistant de support pour la Guyane. "
            "La question de l'utilisateur est ambiguë ou trop générale. "
            "Demande-lui de préciser poliment et succinctement (une seule question). "
            "Propose des exemples spécifiques (localité, type de service)."
        )
        
        user_prompt = (
            f"La question suivante est ambiguë ou nécessite des précisions:\n"
            f"\"{user_query}\"\n\n"
            f"Demande à l'utilisateur de préciser."
        )
        
        llm_response = self._call_mistral(system_prompt, user_prompt)
        
        if not llm_response:
            llm_response = (
                f"Votre question pourrait être plus spécifique. "
                "Préciseriez-vous votre localité (Cayenne, Kourou, etc.) ou le type de service ?"
            )
        
        return {
            "case": 2,
            "response": llm_response,
            "sources": [],
            "metadata": {
                "status": "clarification_needed"
            }
        }
    
    def _case_3_generaliste(self, user_query: str) -> Dict:
        """
        **Cas 3 — Réponse généraliste (pas de sources locales)**
        
        Aucune source locale trouvée.
        Le LLM peut répondre de manière générale, mais avertit l'utilisateur.
        """
        
        system_prompt = (
            "Tu es un assistant généraliste utile et ami. "
            "L'utilisateur pose une question hors de ta base de données locale (Guyane). "
            "Tu peux répondre de manière généraliste, MAIS tu dois proposer de relancer avec une question sur la Guyane\n"
            "Sois concis." # (max 3-4 phrases)
        )
        
        user_prompt = (
            f"Question de l'utilisateur: {user_query}\n\n"
            f"Réponds de manière généraliste. Termine en proposant "
            f"une question sur la Guyane."
        )
        
        llm_response = self._call_mistral(system_prompt, user_prompt)
        
        if not llm_response:
            llm_response = (
                f"Je n'ai pas d'information spécifique sur '{user_query}' dans ma base locale. "
                "Cependant, je peux vous aider avec des questions sur les hébergements, transports, "
                "attractions et services en Guyane. Posez-moi une question !"
            )
        
        return {
            "case": 3,
            "response": llm_response,
            "sources": [],
            "metadata": {
                "status": "generaliste",
                "source_type": "llm_only"
            }
        }


# Instance globale
llm_pipeline = None


def get_llm_pipeline() -> LLMPipeline:
    """Retourne l'instance globale du pipeline LLM."""
    global llm_pipeline
    if llm_pipeline is None:
        llm_pipeline = LLMPipeline()
    return llm_pipeline


if __name__ == "__main__":
    # Test simple
    try:
        pipeline = get_llm_pipeline()
        
        # Test Cas 1
        print("\n" + "="*60)
        print("TEST CAS 1 — Réponse avec sources locales")
        print("="*60)
        results_case1 = [
            {
                "score": 4.5,
                "doc_id": "02-transports",
                "excerpt": "Bus CTG depuis aéroport: 3€, 1h30, départ toutes les 2h."
            }
        ]
        resp1 = pipeline.process(
            "Comment aller de l'aéroport au centre-ville?",
            results_case1
        )
        print(f"Cas: {resp1['case']} | Métadonnées: {resp1['metadata']}")
        print(f"Réponse: {resp1['response']}\n")
        
        # Test Cas 2
        print("="*60)
        print("TEST CAS 2 — Demande de précision")
        print("="*60)
        results_case2 = [
            {
                "score": 1.2,
                "doc_id": "01-hebergements",
                "excerpt": "Hôtel Le Brésilien: 80-120€, Gîte Amazonie: 60-90€"
            }
        ]
        resp2 = pipeline.process(
            "Où dormir?",
            results_case2
        )
        print(f"Cas: {resp2['case']} | Métadonnées: {resp2['metadata']}")
        print(f"Réponse: {resp2['response']}\n")
        
        # Test Cas 3 — Généraliste
        print("="*60)
        print("TEST CAS 3 — Réponse généraliste (pas de sources)")
        print("="*60)
        resp3 = pipeline.process(
            "Comment faire un gâteau au chocolat?",
            []
        )
        print(f"Cas: {resp3['case']} | Métadonnées: {resp3['metadata']}")
        print(f"Réponse: {resp3['response']}\n")
        
        # Test Cas 3 — Question hors-sujet
        print("="*60)
        print("TEST CAS 3 — Question générale")
        print("="*60)
        resp4 = pipeline.process(
            "Quelle est la capitale de la France?",
            []
        )
        print(f"Cas: {resp4['case']} | Métadonnées: {resp4['metadata']}")
        print(f"Réponse: {resp4['response']}")
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()