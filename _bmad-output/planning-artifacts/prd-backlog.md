# PRD Backlog initial — YanaChat (MVP)

Priorité: haute → basse. Chaque user story suit le format: Rôle, objectif, valeur + critères d'acceptation minimal.

## PoC — périmètre
Inclus dans le PoC : **US-001 (Recherche d'information locale)**, **US-004 (Info météo & sécurité locale)**, **US-007 (Gestion des contenus locaux / CMS simple)**.
Les autres user stories sont hors périmètre PoC et pourront être planifiées ensuite.

---

## US-001 — Recherche d'information locale (PoC)
- Description : En tant que visiteur, je pose une question sur un lieu/service local et reçois une réponse concise, sourcée et actionnable.

- Critères d'acceptation détaillés :
  - Réponse retournée en médiane <= 60s lors d'un test de charge léger (simuler 50 sessions simultanées).
  - Réponse contient au moins une source identifiable (URL, nom d'office du tourisme, fiche locale) si disponible.
  - Précision automatique >= 80% mesurée sur un corpus de 100 requêtes annotées (test de validation).
  - Support minimum des intents : recherche d'adresse, horaires, description courte, contact.

- Implémentation minimale (PoC) :
  - Backend: endpoint REST `POST /api/query` -> renvoie {answer, sources[], intent, confidence}.
  - Données: index hybride (documents locaux + embeddings LLM) ; start avec dataset CSV/YAML extrait du product-brief.
  - NLU: détection d'intent simple + retrieval-augmented generation (RAG) si nécessaire.

- Tests & validation :
  - Suite de 100 requêtes annotées pour mesurer précision/recall.
  - Tests de performance: médiane latence sur 50 sessions concurrentes.

- Monitoring & métriques :
  - Latence (p95, médiane), taux de résolution (auto), taux d'escalade vers humain, score de pertinence humain.

- Dépendances / données sources :
  - Fichiers locaux (FAQ, guides touristiques), APIs publiques locales (météo, office du tourisme), dataset manuel initial.

- Définition de Done (DoD) :
  - Endpoint `POST /api/query` fonctionnel, tests automatisés passés, dataset initial indexé, dashboard métriques minimal en place.

## US-004 — Info météo & sécurité locale (PoC)
- Description : En tant que nouvel arrivant, je veux connaître la météo locale et alertes officielles pour planifier mes activités.

- Critères d'acceptation détaillés :
  - Affiche météo actuelle + prévision 3 jours pour la localité demandée.
  - Si une alerte officielle est active (source gouvernementale), affiche un message d'alerte et lien vers la source.
  - Temps de réponse médian <= 3s pour requêtes météo (via API externe).

- Implémentation minimale (PoC) :
  - Intégration API météo (ex: OpenWeatherMap ou API locale) pour récupération temps réel et prévisions.
  - Intégration flux d'alertes (si disponible) ou parsing RSS/JSON des autorités locales.
  - Endpoint `GET /api/weather?location=...` ou intégré au `POST /api/query` de US-001.

- Tests & validation :
  - Tests unitaires pour mapping des réponses météo.
  - Scénarios d'alerte simulés pour vérifier affichage et lien source.

- Monitoring & métriques :
  - Disponibilité API externe, latence des calls météo, taux d'affichage d'alertes.

- Dépendances :
  - Clé API météo (configurable), accès aux flux d'alerte locaux.

- DoD :
  - Météo 3 jours affichée correctement pour 5 localités de test, alertes simulées affichées, tests automatiques passés.

## US-007 — Gestion des contenus locaux (CMS simple) (PoC)
- Description : En tant qu'administrateur local, je veux pouvoir mettre à jour FAQ / recommandations pour corriger ou enrichir les réponses du bot.

- Critères d'acceptation détaillés :
  - Possibilité d'ajouter/modifier/retirer entrées via un fichier YAML/CSV importable ou une UI d'édition minimale.
  - Changements pris en compte par le moteur de recherche de réponses après un processus d'ingestion (max 10 min en PoC) ou par redéploiement minimal.

- Implémentation minimale (PoC) :
  - Backend: support d'un dossier `content/local` contenant fichiers YAML/CSV; endpoint `POST /api/content/reload` pour réindexer.
  - UI minimal (optionnel PoC): une page d'édition statique qui sauvegarde des fichiers dans `content/local`.

- Tests & validation :
  - Import d'un fichier YAML de test -> vérifier présence dans index et réponses modifiées.

- Monitoring & métriques :
  - Logs d'ingestion, temps d'ingestion, erreurs de parsing.

- DoD :
  - Import fonctionnel et visible dans résultats pour 10 requêtes de test, endpoint de reload documenté et testé.

---
Fichier généré automatiquement par l'agent; demandé par l'utilisateur pour PRD step-04.
