"""
Convertisseur CSV → Markdown pour restaurants Guyane.
Génère UN SEUL fichier Markdown avec tous les restaurants (500+).
"""

import csv
import pandas as pd
import sys
from pathlib import Path
from typing import Dict, List


class CSVToMarkdownConverter:
    """Convertit CSV restaurants en UN SEUL fichier Markdown structuré."""
    
    # Liste complète des communes de Guyane (ordre alphabétique)
    GUYANE_COMMUNES = [
        "Apatou",
        "Awala-Yalimapo",
        "Camopi",
        "Cayenne",
        "Grand-Santi",
        "Iracoubo",
        "Kourou",
        "Macouria",
        "Mana",
        "Maripasoula",
        "Matoury",
        "Montsinéry-Tonnegrande",
        "Ouanary",
        "Papaïchton",
        "Régina",
        "Rémire-Montjoly",
        "Roura",
        "Saint-Élie",
        "Saint-Georges de l'Oyapock",
        "Saint-Laurent-du-Maroni",
        "Saül",
        "Sinnamary",
    ]
    
    def __init__(self, csv_path: str, output_dir: str = None):
        """
        Args:
            csv_path (str): Chemin du fichier CSV
            output_dir (str): Répertoire de sortie (default: project/data/corpus)
        """
        self.csv_path = Path(csv_path)
        
        # Déterminer output_dir par rapport à la racine du projet
        if output_dir is None:
            project_root = Path(__file__).parent.parent
            output_dir = project_root / "data" / "corpus"
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Charger CSV
        try:
            self.df = pd.read_csv(self.csv_path, encoding='utf-8')
            print(f"✓ CSV chargé: {len(self.df)} restaurants")
            print(f"  Colonnes détectées: {list(self.df.columns)}\n")
        except FileNotFoundError:
            print(f"❌ Fichier CSV non trouvé: {self.csv_path}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Erreur lecture CSV: {e}")
            sys.exit(1)
    
    def _clean_value(self, val) -> str:
        """Nettoie les valeurs (NaN, espaces, etc.)."""
        if pd.isna(val):
            return ""
        return str(val).strip()
    
    def _normalize_float(self, val: str) -> float:
        """
        Convertit une chaîne en float.
        Gère les formats décimaux français (virgule) et anglais (point).
        
        Args:
            val (str): Valeur à convertir (ex: "4,5" ou "4.5")
        
        Returns:
            float: Nombre ou 0 si conversion impossible
        """
        if not val:
            return 0.0
        
        val = str(val).strip()
        
        # Remplacer virgule par point (format français → format Python)
        val = val.replace(',', '.')
        
        try:
            return float(val)
        except ValueError:
            return 0.0
    
    def _extract_city(self, address: str) -> str:
        """
        Extrait la ville de l'adresse.
        Utilise la liste exhaustive des communes de Guyane.
        
        Args:
            address (str): Adresse complète
        
        Returns:
            str: Commune de Guyane (ou "Autres" si pas trouvée)
        """
        
        if not address:
            return "Autres"
        
        address_lower = address.lower()
        
        # Chercher match avec les communes connues (exact match d'abord)
        for commune in self.GUYANE_COMMUNES:
            if commune.lower() in address_lower:
                return commune
        
        # Fallback: dernière partie de l'adresse
        parts = address.split(',')
        if len(parts) > 0:
            last_part = parts[-1].strip()
            if last_part:
                # Chercher si c'est une commune connue
                for commune in self.GUYANE_COMMUNES:
                    if commune.lower() == last_part.lower():
                        return commune
                return last_part
        
        return "Autres"
    
    def _get_restaurants_by_city(self) -> Dict[str, List[Dict]]:
        """
        Groupe tous les restaurants par ville (sans sous-catégories).
        
        Returns:
            dict: {
                'Cayenne': [...restaurants...],
                'Kourou': [...restaurants...]
            }
        """
        
        grouped = {}
        
        for idx, row in self.df.iterrows():
            # Extraire localisation/ville
            localisation = self._clean_value(row.get('address', ''))
            ville = self._extract_city(localisation)
            
            # Initialiser liste pour ville
            if ville not in grouped:
                grouped[ville] = []
            
            # Extraire catégorie
            categorie = self._clean_value(row.get('categorie', 'Autre'))
            if not categorie:
                categorie = "Autre"
            
            # Extraire et normaliser la note
            note_str = self._clean_value(row.get('note', ''))
            note_float = self._normalize_float(note_str)
            
            # Ajouter restaurant
            restaurant = {
                'name': self._clean_value(row.get('name', 'Restaurant sans nom')),
                'address': localisation,
                'phone': self._clean_value(row.get('phone', '')),
                'website': self._clean_value(row.get('website', '')),
                'google_url': self._clean_value(row.get('google_url', '')),
                'note': note_str,  # Garder la valeur originale pour affichage
                'note_float': note_float,  # Garder la valeur numérique pour tri
                'nb_avis': self._clean_value(row.get('nb_avis', '')),
                'categorie': categorie,
                'accessible': self._clean_value(row.get('accessible', '')),
                'chiens_acceptes': self._clean_value(row.get('chiens_acceptes', '')),
                'livraison': self._clean_value(row.get('livraison', '')),
                'repas_sur_place': self._clean_value(row.get('repas_sur_place', '')),
            }
            
            grouped[ville].append(restaurant)
        
        return grouped
    
    def _format_rating(self, note: str, nb_avis: str) -> str:
        """Formate la note Google."""
        if not note:
            return ""
        
        rating = note  # Garder le format original (virgule ou point)
        if nb_avis:
            rating += f" ({nb_avis} avis)"
        
        return rating
    
    def _format_services(self, restaurant: Dict) -> str:
        """Formate les services disponibles."""
        services = []
        
        service_map = {
            'repas_sur_place': 'Repas sur place',
            'livraison': 'Livraison',
            'accessible': 'Accessible PMR',
            'chiens_acceptes': 'Chiens acceptés',
        }
        
        for key, label in service_map.items():
            value = restaurant.get(key, '').lower()
            if value in ['true', 'oui', '1', 'yes']:
                services.append(label)
        
        return ", ".join(services) if services else ""
    
    def _format_restaurant_md(self, restaurant: Dict) -> str:
        """
        Formate un restaurant en Markdown.
        
        Args:
            restaurant (dict): Données du restaurant
        
        Returns:
            str: Bloc Markdown formaté
        """
        
        md = f"\n#### {restaurant['name']}\n"
        
        if restaurant['categorie']:
            md += f"- **Type :** {restaurant['categorie']}\n"
        
        if restaurant['address']:
            md += f"- **Adresse :** {restaurant['address']}\n"
        
        if restaurant['phone']:
            md += f"- **Téléphone :** {restaurant['phone']}\n"
        
        # Note
        rating = self._format_rating(restaurant['note'], restaurant['nb_avis'])
        if rating:
            md += f"- **Note :** {rating}\n"
        
        # Services
        services = self._format_services(restaurant)
        if services:
            md += f"- **Services :** {services}\n"
        
        if restaurant['website']:
            md += f"- **Site web :** {restaurant['website']}\n"
        
        if restaurant['google_url']:
            md += f"- **Google Maps :** [Voir]({restaurant['google_url']})\n"
        
        return md
    
    def convert(self) -> None:
        """
        Convertit le CSV en fichiers Markdown par ville.
        Génère des fichiers numérotés (12-restaurants-cayenne.md, etc.)
        """
        
        print(f"\n{'='*60}")
        print("🔄 Conversion CSV → Markdown (par ville)")
        print('='*60 + "\n")
        
        grouped = self._get_restaurants_by_city()
        
        # Ordre de priorité (communes majeures en premier)
        priority_order = [
            "Cayenne",
            "Kourou",
            "Matoury",
            "Rémire-Montjoly",
            "Saint-Laurent-du-Maroni",
            "Sinnamary",
            "Macouria",
            "Iracoubo",
            "Roura",
            "Régina",
        ]
        
        # Ordonner les villes
        ordered_cities = []
        for city in priority_order:
            if city in grouped:
                ordered_cities.append(city)
        
        # Ajouter les autres villes (non-prioritaires)
        for city in sorted(grouped.keys()):
            if city not in ordered_cities:
                ordered_cities.append(city)
        
        # Générer 1 fichier par ville
        file_counter = 12
        total_restaurants = 0
        files_generated = []
        
        for city in ordered_cities:
            restaurants = grouped[city]
            restaurant_count = len(restaurants)
            total_restaurants += restaurant_count
            
            # Déterminer nom fichier
            if city == "Cayenne":
                filename = "12-restaurants-cayenne.md"
            elif city == "Kourou":
                filename = "13-restaurants-kourou.md"
            elif city == "Saint-Laurent-du-Maroni":
                filename = "14-restaurants-saint-laurent.md"
            else:
                ville_slugified = city.lower().replace('-', '_').replace(' ', '_').replace('é', 'e').replace('î', 'i')
                filename = f"{file_counter:02d}-restaurants-{ville_slugified}.md"
                file_counter += 1
            
            output_path = self.output_dir / filename
            
            # Construire contenu Markdown
            content = f"# 🍽️ Restaurants - {city}\n\n"
            content += f"**{restaurant_count} restaurants répertoriés à {city}**\n\n"
            content += "---\n\n"
            
            # Grouper par catégorie
            by_category = {}
            for restaurant in restaurants:
                cat = restaurant['categorie']
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(restaurant)
            
            # Écrire par catégorie
            for categorie in sorted(by_category.keys()):
                cat_restaurants = by_category[categorie]
                content += f"## {categorie}\n\n"
                
                # Trier par note décroissante (utiliser note_float)
                sorted_restaurants = sorted(
                    cat_restaurants,
                    key=lambda r: r['note_float'],
                    reverse=True
                )
                
                for restaurant in sorted_restaurants:
                    content += self._format_restaurant_md(restaurant)
            
            # Écrire fichier
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            files_generated.append(filename)
            print(f"✓ {filename:<35} : {restaurant_count:>4} restaurants")
        
        print(f"\n{'='*60}")
        print(f"✅ Conversion terminée !")
        print(f"   📊 Total restaurants : {total_restaurants}")
        print(f"   📁 Communes : {len(ordered_cities)}")
        print(f"   📄 Fichiers générés : {len(files_generated)}")
        print(f"   📂 Répertoire : {self.output_dir}")
        print('='*60)
        print(f"\n🔄 Prochaine étape:")
        print(f"   python src/reindex_corpus.py")


def main():
    """Point d'entrée."""
    
    # Chemin du CSV (relatif à la racine du projet)
    project_root = Path(__file__).parent.parent
    csv_path = project_root / "data" / "restaurant_guyane_20251026_012226_dedup.csv"
    
    if not csv_path.exists():
        print(f"\n❌ Fichier CSV non trouvé: {csv_path}")
        print("\n📝 Instructions:")
        print(f"   1. Placer votre CSV à: {csv_path}")
        print(f"   2. S'assurer que les colonnes sont:")
        print(f"      - name, address, categorie, phone, website")
        print(f"      - note, nb_avis, google_url")
        print(f"      - accessible, chiens_acceptes, livraison, repas_sur_place")
        print(f"\n   3. Exécuter: python src/csv_to_md.py")
        sys.exit(1)
    
    converter = CSVToMarkdownConverter(str(csv_path))
    converter.convert()


if __name__ == "__main__":
    main()