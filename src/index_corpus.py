"""
Indexeur offline pour corpus Markdown avec Whoosh BM25.
Génère un index persistant pour TOUT le corpus (restaurants + autres documents).
"""

import shutil
from pathlib import Path
from whoosh.fields import Schema, TEXT, ID, STORED
from whoosh.index import create_in
from typing import List, Dict

# Configuration
CORPUS_DIR = Path(__file__).parent.parent / "data" / "corpus"
INDEX_DIR = Path(__file__).parent.parent / "data" / "index"


def parse_restaurants_from_markdown(content: str, filename: str) -> List[Dict]:
    """
    Parse le Markdown pour extraire chaque restaurant individuellement.
    
    Format attendu :
    ## Ville
    ### Catégorie
    #### Restaurant Name
    - **Type :** Créole
    - **Adresse :** ...
    - **Téléphone :** ...
    - **Site web :** ...
    - **Google Maps :** ...
    
    Args:
        content (str): Contenu du fichier Markdown
        filename (str): Nom du fichier (ex: "13-restaurants-kourou")
    
    Returns:
        List[Dict]: Liste des restaurants avec leurs détails
    """
    import re
    restaurants = []
    lines = content.split('\n')
    
    current_ville = None
    current_categorie = None
    current_restaurant = None
    current_text = []
    current_website = None
    current_gmaps = None
    
    for line in lines:
        # Détecter ville (## Ville)
        if line.startswith('## ') and not line.startswith('### '):
            current_ville = line.replace('## ', '').strip()
        
        # Détecter catégorie (### Catégorie)
        elif line.startswith('### '):
            current_categorie = line.replace('### ', '').strip()
        
        # Détecter restaurant (#### Restaurant Name)
        elif line.startswith('#### '):
            # Sauvegarder le restaurant précédent
            if current_restaurant:
                restaurant_text = '\n'.join(current_text).strip()
                restaurants.append({
                    'doc_id': f"{filename}_{current_restaurant['name'][:25].replace(' ', '_')}",
                    'name': current_restaurant['name'],
                    'ville': current_ville,
                    'categorie': current_categorie,
                    'excerpt': restaurant_text[:300],
                    'full_text': restaurant_text,
                    'doc_type': 'restaurant',
                    'website': current_website or '',
                    'google_maps': current_gmaps or '',
                })
            
            # Démarrer nouveau restaurant
            current_restaurant = {'name': line.replace('#### ', '').strip()}
            current_text = [line]
            current_website = None
            current_gmaps = None
        
        # Accumuler le texte du restaurant et extraire liens
        elif current_restaurant:
            current_text.append(line)
            # Extraire site web
            if '**Site web :**' in line or '**Site web:**' in line:
                match = re.search(r'\*\*Site web\s*:\*\*\s*(.+)', line)
                if match:
                    current_website = match.group(1).strip()
            # Extraire Google Maps
            if '**Google Maps :**' in line or '**Google Maps:**' in line:
                match = re.search(r'\[Voir\]\((.+?)\)', line)
                if match:
                    current_gmaps = match.group(1).strip()
    
    # Sauvegarder le dernier restaurant
    if current_restaurant:
        restaurant_text = '\n'.join(current_text).strip()
        restaurants.append({
            'doc_id': f"{filename}_{current_restaurant['name'][:25].replace(' ', '_')}",
            'name': current_restaurant['name'],
            'ville': current_ville,
            'categorie': current_categorie,
            'excerpt': restaurant_text[:300],
            'full_text': restaurant_text,
            'doc_type': 'restaurant',
            'website': current_website or '',
            'google_maps': current_gmaps or '',
        })
    
    return restaurants


def parse_generic_markdown(content: str, filename: str) -> List[Dict]:
    """
    Parse un fichier Markdown générique (non-restaurant).
    Crée des documents SÉPARÉS pour chaque section (## Titre).
    Cela permet une meilleure indexation et recherche granulaire.
    
    Format :
    # Titre Principal
    ## Section 1
    Contenu section 1...
    
    ## Section 2
    Contenu section 2...
    
    Args:
        content (str): Contenu du fichier Markdown
        filename (str): Nom du fichier
    
    Returns:
        List[Dict]: Liste de documents (un par section majeure)
    """
    import re
    documents = []
    lines = content.split('\n')
    
    # Extraire titre principal (première ligne avec #)
    main_title = filename
    for line in lines:
        if line.startswith('# ') and not line.startswith('## '):
            main_title = line.replace('# ', '').strip()
            break
    
    # Splitter par sections de niveau 2 (##)
    current_section = None
    current_section_content = []
    
    for line in lines:
        # Détecter nouvelle section (## Titre)
        if line.startswith('## ') and not line.startswith('### '):
            # Sauvegarder la section précédente
            if current_section:
                section_text = '\n'.join(current_section_content).strip()
                if section_text:  # Ne sauvegarder que si non-vide
                    doc_id = f"{filename}_{current_section[:25].replace(' ', '_').replace('é', 'e')}"
                    documents.append({
                        'doc_id': doc_id,
                        'name': current_section,
                        'excerpt': section_text[:300],
                        'full_text': section_text,
                        'doc_type': 'generic',
                    })
            
            # Démarrer nouvelle section
            current_section = line.replace('## ', '').strip()
            current_section_content = [line]
        
        # Accumuler le contenu de la section
        elif current_section:
            current_section_content.append(line)
    
    # Sauvegarder la dernière section
    if current_section:
        section_text = '\n'.join(current_section_content).strip()
        if section_text:
            doc_id = f"{filename}_{current_section[:25].replace(' ', '_').replace('é', 'e')}"
            documents.append({
                'doc_id': doc_id,
                'name': current_section,
                'excerpt': section_text[:300],
                'full_text': section_text,
                'doc_type': 'generic',
            })
    
    # Si aucune section trouvée, créer document global
    if not documents:
        excerpt = content[:300]
        if len(content) > 300:
            excerpt += "..."
        documents.append({
            'doc_id': filename,
            'name': main_title,
            'excerpt': excerpt,
            'full_text': content,
            'doc_type': 'generic',
        })
    
    return documents


def is_restaurant_file(filename: str) -> bool:
    """
    Détermine si un fichier est un fichier de restaurants.
    
    Args:
        filename (str): Nom du fichier (ex: "13-restaurants-kourou")
    
    Returns:
        bool: True si c'est un fichier de restaurants
    """
    return 'restaurant' in filename.lower()


def create_index():
    """
    Crée l'index Whoosh à partir de TOUT le corpus Markdown.
    - Restaurants : indexés individuellement
    - Autres documents : indexés entièrement
    """
    
    print(f"\n{'='*60}")
    print("📚 Création de l'index Whoosh (Corpus complet)")
    print('='*60 + "\n")
    
    # Vérifier que le corpus existe
    if not CORPUS_DIR.exists():
        print(f"❌ Corpus directory not found: {CORPUS_DIR}")
        print("   Création du répertoire vide...")
        CORPUS_DIR.mkdir(parents=True, exist_ok=True)
        return
    
    # Nettoyer ancien index
    if INDEX_DIR.exists():
        shutil.rmtree(INDEX_DIR)
        print(f"🗑️  Index précédent supprimé\n")
    
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    
    # Schéma Whoosh (pour restaurants ET documents génériques)
    schema = Schema(
        doc_id=ID(stored=True),  # ID unique
        name=TEXT(stored=True, field_boost=2.0),  # Titre/Nom
        excerpt=TEXT(stored=True),  # Court extrait pour affichage
        content=TEXT(stored=True, phrase=True),  # Contenu complet pour recherche
        doc_type=STORED(),  # Type de document (restaurant, generic, etc.)
        ville=STORED(),  # Ville (pour restaurants)
        categorie=STORED(),  # Catégorie (pour restaurants)
        filename=STORED(),  # Fichier d'origine
        website=STORED(),  # Site web (pour restaurants)
        google_maps=STORED(),  # Lien Google Maps (pour restaurants)
    )
    
    ix = create_in(str(INDEX_DIR), schema)
    writer = ix.writer()
    
    # Trouver tous les fichiers Markdown
    markdown_files = sorted(CORPUS_DIR.glob("*.md"))
    
    if not markdown_files:
        print(f"⚠️  Aucun fichier Markdown trouvé dans {CORPUS_DIR}")
        return
    
    print(f"📄 Traitement de {len(markdown_files)} fichier(s)...\n")
    
    total_documents = 0
    restaurants_count = 0
    generic_count = 0
    
    # Indexer chaque fichier
    for md_file in markdown_files:
        try:
            filename = md_file.stem  # Nom sans extension
            
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Déterminer le type de fichier
            if is_restaurant_file(filename):
                # ✅ Fichier de restaurants : indexer individuellement
                restaurants = parse_restaurants_from_markdown(content, filename)
                
                if not restaurants:
                    print(f"  ⚠️  {md_file.name}: Aucun restaurant détecté")
                    continue
                
                # Indexer chaque restaurant
                for restaurant in restaurants:
                    writer.add_document(
                        doc_id=restaurant['doc_id'],
                        name=restaurant['name'],
                        excerpt=restaurant['excerpt'],
                        content=restaurant['full_text'],
                        doc_type=restaurant['doc_type'],
                        ville=restaurant.get('ville', 'Unknown'),
                        categorie=restaurant.get('categorie', 'Unknown'),
                        filename=filename,
                        website=restaurant.get('website', ''),
                        google_maps=restaurant.get('google_maps', ''),
                    )
                
                print(f"  ✓ {md_file.name:<35} : {len(restaurants):>3} restaurants")
                restaurants_count += len(restaurants)
                total_documents += len(restaurants)
            
            else:
                # ✅ Fichier générique : indexer par sections
                docs = parse_generic_markdown(content, filename)
                
                for doc in docs:
                    writer.add_document(
                        doc_id=doc['doc_id'],
                        name=doc['name'],
                        excerpt=doc['excerpt'],
                        content=doc['full_text'],
                        doc_type=doc['doc_type'],
                        ville='',
                        categorie='',
                        filename=filename,
                        website='',
                        google_maps='',
                    )
                
                print(f"  ✓ {md_file.name:<35} : {len(docs)} section(s)")
                generic_count += len(docs)
                total_documents += len(docs)
        
        except Exception as e:
            print(f"  ✗ Erreur {md_file.name}: {e}")
    
    # Commit et fermer l'index
    writer.commit()
    
    print(f"\n{'='*60}")
    print(f"✅ Index créé avec succès !")
    print(f"   📊 Total documents indexés : {total_documents}")
    print(f"      - Restaurants : {restaurants_count}")
    print(f"      - Documents génériques : {generic_count}")
    print(f"   📂 Répertoire : {INDEX_DIR}")
    print('='*60 + "\n")


if __name__ == "__main__":
    create_index()