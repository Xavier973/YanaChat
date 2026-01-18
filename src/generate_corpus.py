"""
Générateur automatique de corpus à partir de sources publiques.
Utilise GPT-4/Claude pour formatter les données.
"""

import os
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Configuration
CORPUS_DIR = Path(__file__).parent.parent / "data" / "corpus"
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_API_URL = os.getenv("MISTRAL_API_URL")


def call_mistral(prompt: str) -> str:
    """Appel Mistral pour formater des données."""
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "mistral-small-latest",
        "messages": [
            {"role": "system", "content": "Tu es un expert en structuration de données touristiques."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }
    
    r = requests.post(MISTRAL_API_URL, headers=headers, json=payload, timeout=30)
    return r.json()["choices"][0]["message"]["content"]


# ============================================================
# Templates de génération
# ============================================================

def generate_hotels():
    """Génère 07-hotels.md avec 15 hôtels."""
    
    prompt = """
Génère un fichier Markdown structuré avec 15 hôtels/gîtes en Guyane (Cayenne, Kourou, Saint-Laurent).

Format EXACT :
```markdown
# Hébergements détaillés - Guyane

## Cayenne

### Hôtel [Nom]
- **Type :** [Hôtel/Gîte/Auberge] [1-5 étoiles]
- **Adresse :** [Rue], Cayenne
- **Prix :** [XX-XX] €/nuit
- **Services :** [WiFi, piscine, restaurant, etc.]
- **Contact :** +594 594 XX XX XX
- **Email :** contact@hotel.gf
- **URL :** https://www.hotel.gf
- **Particularité :** [Vue mer, centre-ville, etc.]
```

Utilise des noms **réalistes** (Hôtel Amazonia, Le Mahury, etc.).
Ajoute 5 à Cayenne, 5 à Kourou, 5 à Saint-Laurent.
"""
    
    response = call_mistral(prompt)
    
    output_file = CORPUS_DIR / "07-hotels-detailles.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(response)
    
    print(f"✓ Généré: {output_file}")


def generate_restaurants():
    """Génère 08-restaurants.md avec 20 restaurants."""
    
    prompt = """
Génère un fichier Markdown avec 20 restaurants en Guyane (Cayenne principalement).

Format EXACT :
```markdown
# Restaurants - Guyane

## Cayenne - Centre-ville

### Restaurant [Nom]
- **Type :** [Créole/Français/Brésilien/Chinois/Fruits de mer]
- **Adresse :** [Rue], Cayenne
- **Spécialités :** [Plat 1, Plat 2, Plat 3]
- **Prix moyen :** [XX-XX] € par personne
- **Horaires :** [Lun-Sam 11h-14h, 18h-22h]
- **Contact :** +594 594 XX XX XX
- **Particularité :** [Terrasse, vue, spécialité locale]
```

Inclure des spécialités guyanaises réalistes (bouillon d'awara, accras, colombo, etc.).
20 restaurants variés (créole, brésilien, asiatique, français).
"""
    
    response = call_mistral(prompt)
    
    output_file = CORPUS_DIR / "08-restaurants.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(response)
    
    print(f"✓ Généré: {output_file}")


def generate_activities():
    """Génère 09-activites.md avec 15 activités."""
    
    prompt = """
Génère un fichier Markdown avec 15 activités/excursions en Guyane.

Format EXACT :
```markdown
# Activités & Excursions - Guyane

## Nature & Aventure

### [Nom activité]
- **Type :** [Randonnée/Kayak/Observation faune/Plage/etc.]
- **Lieu :** [Localisation], [Ville]
- **Durée :** [XX heures/jours]
- **Tarif :** [XX] € par personne
- **Niveau :** [Facile/Moyen/Difficile]
- **Inclus :** [Guide, équipement, repas, etc.]
- **Contact :** +594 594 XX XX XX
- **Particularité :** [Tortues luth, singes hurleurs, forêt primaire, etc.]
```

Inclure activités réalistes : Îles du Salut, Montagne de Kaw, plages Awala-Yalimapo (tortues), forêts, fleuves, etc.
15 activités variées (nature, culture, aventure).
"""
    
    response = call_mistral(prompt)
    
    output_file = CORPUS_DIR / "09-activites.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(response)
    
    print(f"✓ Généré: {output_file}")


def generate_transport_details():
    """Génère 10-transports-details.md avec tarifs/horaires complets."""
    
    prompt = """
Génère un fichier Markdown détaillé sur les transports en Guyane.

Format EXACT :
```markdown
# Transports détaillés - Guyane

## Bus urbains (CTG)

### Ligne [Numéro] : [Trajet]
- **Fréquence :** Toutes les [XX] minutes
- **Horaires :** [6h-20h] en semaine, [8h-18h] week-end
- **Tarif :** [X] € par trajet, [XX] € carte mensuelle
- **Arrêts principaux :** [Arrêt 1, Arrêt 2, Arrêt 3]

## Taxis

### Taxi [Compagnie]
- **Zone :** [Cayenne/Kourou/Saint-Laurent]
- **Tarifs :** [XX] € base + [X] €/km
- **Contact :** +594 594 XX XX XX
- **Services :** [24/7, réservation, bagages]

## Location voitures

### [Agence]
- **Localisation :** [Aéroport/Centre-ville]
- **Tarifs :** [XX-XX] €/jour selon véhicule
- **Véhicules :** [Citadine, SUV, 4x4]
- **Contact :** +594 594 XX XX XX
```

Inclure lignes bus CTG, taxis, location voitures (Hertz, Avis, Europcar).
Tarifs et horaires réalistes pour 2026.
"""
    
    response = call_mistral(prompt)
    
    output_file = CORPUS_DIR / "10-transports-details.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(response)
    
    print(f"✓ Généré: {output_file}")


def generate_services_pratiques():
    """Génère 11-services-pratiques.md avec infos utiles."""
    
    prompt = """
Génère un fichier Markdown avec services pratiques en Guyane.

Format EXACT :
```markdown
# Services pratiques - Guyane

## Santé

### Pharmacie [Nom]
- **Adresse :** [Rue], [Ville]
- **Horaires :** [Lun-Ven Xh-Xh, Sam Xh-Xh]
- **Services :** [Médicaments, conseils, tests COVID]
- **Contact :** +594 594 XX XX XX

### Cabinet médical [Nom]
- **Spécialité :** [Généraliste/Dentiste/etc.]
- **Adresse :** [Rue], [Ville]
- **Tarifs :** [XX] € consultation
- **Contact :** +594 594 XX XX XX

## Banques & Change

### Banque [Nom]
- **Adresse :** [Rue], [Ville]
- **Horaires :** [Lun-Ven Xh-Xh]
- **Services :** [Retraits, change EUR/USD, virements]
- **Contact :** +594 594 XX XX XX

## Supermarches

### [Enseigne]
- **Adresse :** [Rue], [Ville]
- **Horaires :** [Lun-Sam Xh-Xh, Dim Xh-Xh]
- **Services :** [Épicerie, boucherie, boulangerie, retrait cash]
```

Inclure pharmacies, cabinets médicaux, banques, supermarchés (Carrefour, Leader Price, etc.).
15-20 établissements pratiques.
"""
    
    response = call_mistral(prompt)
    
    output_file = CORPUS_DIR / "11-services-pratiques.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(response)
    
    print(f"✓ Généré: {output_file}")


# ============================================================
# Exécution
# ============================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🤖 Génération automatique du corpus")
    print("="*60 + "\n")
    
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    
    generators = [
        ("Hôtels détaillés", generate_hotels),
        ("Restaurants", generate_restaurants),
        ("Activités", generate_activities),
        ("Transports détaillés", generate_transport_details),
        ("Services pratiques", generate_services_pratiques),
    ]
    
    for name, func in generators:
        print(f"📝 Génération: {name}...")
        try:
            func()
            print(f"  ✓ {name} généré\n")
        except Exception as e:
            print(f"  ✗ Erreur {name}: {e}\n")
    
    print("="*60)
    print("✅ Génération terminée !")
    print("="*60)
    print("\n🔄 Prochaine étape : Réindexer le corpus")
    print("  → python src/index_corpus.py")