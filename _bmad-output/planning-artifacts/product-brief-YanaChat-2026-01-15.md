---
stepsCompleted: [1, 2, 3, 4, 5, 6]
inputDocuments: []
date: 2026-01-15
author: Xav
---

# Product Brief: YanaChat

<!-- Document initialisé depuis le template. -->

## Executive Summary

YanaChat est un chatbot intelligent dédié à la Guyane, conçu pour centraliser et livrer des informations locales fiables et pratiques. Il permet aux visiteurs, nouveaux arrivants et habitants de trouver rapidement des réponses contextuelles pour organiser un séjour, accomplir des démarches ou faciliter la vie quotidienne.

## Core Vision

Offrir une source unique, simple et respectueuse de la culture guyanaise, qui valorise le territoire tout en rendant l'information locale accessible, utile et personnalisée.

### Problem Statement

Il est difficile de trouver rapidement des informations locales fiables et pratiques sur la Guyane en un seul endroit : ressources dispersées, contenu souvent générique ou dépassé, et manque de contextualisation (saison, transport, événements locaux, démarches administratives spécifiques).

### Problem Impact

- Perte de temps et frustration pour les visiteurs et nouveaux arrivants.
- Risque d'erreurs pratiques (horaires, exigences administratives, saisonnalité).
- Sous-exploitation des richesses locales et opportunités touristiques.

### Why Existing Solutions Fall Short

Les guides généraux et moteurs de recherche renvoient souvent des informations fragmentées ou non spécialisées; les plateformes locales existent mais manquent de visibilité, d'actualisation ou d'orientation pratique pour des actions concrètes (réserver, se déplacer, démarches).

### Proposed Solution

Un chatbot conversationnel spécialisé qui :
- centralise sources vérifiées (officielles, locales, associatives),
- délivre réponses courtes et actionnables (checklists, liens directs, contacts),
- personnalise selon le profil (visiteur vs résident), la localisation et la saison,
- propose recommandations locales authentiques (événements, sorties, commerces).

### Key Differentiators

- Focus géographique et culturel sur la Guyane (contenu validé localement).
- Réponses contextualisées (saisons, transport, formalités locales).
- Orientation actionnable (liens, modèles de courrier, contacts utiles).
- Respect des usages locaux et promotion des acteurs locaux.

---

_Prochaine étape_: validez ce brouillon puis choisissez [A] Advanced Elicitation, [P] Party Mode, ou [C] Continue (sauvegarder et passer à l'étape suivante).
## First Principles — Synthèse et améliorations appliquées

### Remise en question des hypothèses

- Agrégation des sources: prévoir une couche de validation et des partenariats locaux pour garantir la fiabilité.
- Personnalisation: implémenter via opt‑in simple et signals faibles (profil, localisation, saison) en respectant la vie privée.
- Priorité: viser d'abord l'impact (réponses actionnables) plutôt que l'exhaustivité immédiate.

### Vérités fondamentales

- Les utilisateurs veulent des réponses fiables, claires et immédiatement exploitables.
- La confiance découle de la transparence des sources et de la simplicité des actions proposées.
- Les contraintes locales (connectivité, langues, pratiques) doivent guider le format et la distribution.

### Implications stratégiques

- Construire d'abord un noyau de réponses actionnables validées (checklists, contacts, procédures), puis étendre.
- Prioriser partenariats locaux et mécanismes de validation (éditeurs locaux, associations, offices de tourisme).
- Respecter la vie privée et limiter la collecte de données, personnalisation par opt‑in.

### Proposition révisée (à garder dans le document)

YanaChat centralise des informations locales fiables et actionnables pour la Guyane, en les rendant immédiatement utilisables par visiteurs, nouveaux arrivants et habitants. Le service privilégie des réponses courtes, sourcées et contextualisées (localisation, saison, statut résident/visiteur), avec des actions concrètes (checklists, contacts, modèles de courrier). Plutôt que viser l'exhaustivité immédiate, YanaChat construit un noyau vérifié de contenus à fort impact, puis étend ses sources via partenariats locaux et contributions validées.

### Differenciateurs renforcés

- Validation locale et partenariats (offices du tourisme, associations).
- Respect de la vie privée et personnalisation minimale par opt‑in.
- Mise en valeur des acteurs locaux et contenus culturels authentiques.

---

_Prochaine étape_: voulez‑vous exécuter d'autres méthodes d'Advanced Elicitation, lancer Party Mode, ou `C`ontinuer vers l'étape suivante ?

## Target Users

### Primary Users

- Visiteur — Emma, visiteuse: prépare et effectue un séjour en Guyane (tourisme, activités, démarches ponctuelles). Elle veut des réponses rapides et fiables pour organiser ses journées et démarches sans perdre de temps.

	Problem experience: l'information est dispersée entre sites officiels, blogs et forums; difficile de savoir ce qui est à jour ou adapté selon la saison et la zone.

	Success vision: obtenir une réponse courte, contextualisée et actionnable (horaires, contacts, checklist) qui lui permet d'agir immédiatement.

- Nouvel arrivant — Karim, s'installe en Guyane: déménagement pour travail/famille, cherche à accomplir démarches administratives et s'intégrer.

	Problem experience: informations pratiques locales, localisation des services et contacts souvent peu clairs ou obsolètes.

	Success vision: trouver des procédures claires, contacts actualisés et étapes à suivre pour finaliser ses démarches rapidement.

- Habitant — Marie, résident: utilise les services locaux et suit événements; veut informations fiables et à jour pour la vie quotidienne.

	Problem experience: services, événements et démarches pratiques non centralisés et pas toujours actualisés.

	Success vision: avoir un point d'accès unique pour vérifier horaires, événements, contacts et consignes locales.

### Secondary Users

- Offices de tourisme et collectivités locales: souhaitent diffuser une information locale fiable et homogène.
- Acteurs locaux (associations, entreprises): veulent améliorer la visibilité et l'accessibilité de leurs services.

### User Journey (exemple — Visiteur)

- Découverte: trouve YanaChat via recherche web ou recommandation locale.
- Onboarding: pose une question simple (ex.: «Que faire en Guyane en saison des pluies ?»).
- Usage: reçoit une réponse courte avec conseils, contacts et checklist actionnable.
- Moment "aha": obtient une information locale précise (horaires réels, localisation exacte, contacts utiles) introuvable ou mal référencée ailleurs.

---

_Prochaine étape_: [A] Advanced Elicitation, [P] Party Mode, [C] Continue.

## Success Metrics

### User Success (outcomes & behaviors)

- Time-to-answer: la majorité des requêtes simples (ex.: horaires, contacts) doivent recevoir une réponse actionnable en < 30s.
- Task completion rate: % d'utilisateurs qui suivent une action recommandée (ex.: contacté un service, consulté un lien utile) après une interaction — cible initiale 30%.
- Repeat usage: % d'utilisateurs revenant dans les 30 jours — cible initiale 20% (focus sur utilité récurrente).
- User-reported usefulness (CSAT): proportion d'utilisateurs évaluant la réponse utile (échelle 1–5) — viser ≥4 en moyenne.

### Business Objectives

- Adoption locale: X nouvelles sessions/mois provenant de recherche organique ou recommandations (objectif 3 mois: 500 sessions/mois).
- Partenariats: nombre d'acteurs locaux actifs (offices, associations) fournissant ou validant du contenu — objectif 6 mois: 5 partenaires.
- Visibilité des acteurs locaux: # de contenus locaux référencés et validés (objectif initial: 200 items validés).

### Key Performance Indicators (KPIs)

- New users / month: 500 (Q1 target) — mesuré via événements de session.
- Core journey completion rate: 30% — % d'utilisateurs complétant la checklist/action proposée.
- Retention 30-day: 20% — suivi via identifiant anonyme/session.
- CSAT (usefulness): ≥4/5 — sondage court après réponse.
- Data freshness: % de contenus sources validés dans les 90 derniers jours — viser 80%.
- Partner contributions: nombre de contenus validés par partenaires / mois.

### Measurement & Instrumentation Notes

- Instrumenter événements: `query.received`, `response.sent`, `action.clicked`, `partner.confirmed`, `session.start`, `session.return`.
- Stocker métriques agrégées quotidiennement; dashboards pour suivi hebdomadaire.
- Définir sources de vérité pour validation (partenaires officiels, pages institutionnelles, mises à jour vérifiées).

---

_Prochaine étape_: choisissez [A] Advanced Elicitation, [P] Party Mode, ou [C] Continue vers `step-05-scope.md`.

## MVP Scope

### Core Features

- Question answering engine with local knowledge retrieval (RAG) over curated Guyane sources — returns short, sourced answers.
- Actionable responses: checklists, contact details, direct links to official resources, and simple next‑steps.
- Basic user context: visitor vs résident selection and localisation approximative pour contextualiser réponses (ville/région, saison).
- Source attribution & freshness indicator for each answer; simple admin interface for partners to flag/confirm content.
- Lightweight multi‑channel delivery: web chat + SMS fallback (pour zones à faible connectivité) and PDF export of checklists.
- Minimal analytics/events instrumentation for KPIs defined (query, response, action clicks, return sessions).

### Out of Scope for MVP

- Full conversational agent with deep personalization and learning loops (version >1). 
- Exhaustive national dataset — priorité aux contenus à fort impact (démarches, horaires, contacts, événements majeurs)
- Monetisation features (paiements, réservations) et intégrations complexes tierces (systèmes de billetterie) pour la version initiale.

### MVP Success Criteria

- Core query response latency < 30s pour requêtes simples.
- Task completion rate >= 30% sur actions recommandées.
- 500 sessions/mois et retention 30‑day >= 20% à 3 mois du lancement (objectifs ajustables).
- Au moins 5 partenaires locaux actifs validant du contenu dans les 6 mois.

### Future Vision

- Enrichir la personnalisation (préférences, historique anonymisé) et la couverture locale.
- Ouvrir un portail partenarial pour contributions et validation en flux continu.
- Ajouter canaux (applications natives, intégrations plateformes touristiques) et fonctionnalités avancées (réservation, paiements, recommandations basées sur scoring local).

### Minimum Technical Approach (MVP)

- Backend: serveur léger + index vectoriel (ex: open-source Milvus/Weaviate) pour RAG sur documents validés.
- Ingestion pipeline: scripts ETL pour récupérer sources officielles + validation manuelle par partenaires.
- API: endpoints pour `query` et `action` + webchat frontend simple.
- Analytics: événements tracked, dashboard basique pour suivi KPIs.

### Rough Timeline (example)

- Weeks 0–2: finalisation discovery, collecter 100 sources prioritaires, établir premiers partenariats.
- Weeks 3–6: développer pipeline d'ingestion, indexation et prototype RAG + webchat minimal.
- Weeks 7–10: contenu validé, tests utilisateurs pilotes, itérations sur réponses actionnables.
- Week 11–12: lancement pilote public, mesure KPIs, recueillir feedback partenaires.

---

_Prochaine étape_: sélectionnez [A] Advanced Elicitation, [P] Party Mode, ou [C] Continue pour finaliser le brief (step-06). 

