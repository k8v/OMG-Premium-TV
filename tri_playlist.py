import requests
import re
import os

# Configuration
# Note : Ce script dépend de la disponibilité des flux sur la source externe.
SOURCE_URL = "https://iptv-org.github.io/iptv/languages/fra.m3u"
OUTPUT_FILE = "generated.m3u"

# --- DICTIONNAIRE DE TRI MANUEL ---
# Liste basée sur vos préférences réelles, excluant les chaînes non demandées.
CATEGORIES = {
    "🇫🇷 TNT": [
        "TF1", "TF1 Séries Films", "France 2", "France 3", "France 4", "France 5", 
        "Canal+", "M6", "Arte", "LCP", "w9", "TMC", "TFX", "Gulli", "BFM TV", 
        "CNEWS", "LCI", "Franceinfo:", "CSTAR", "CMI TV", "OFTV", "L'Equipe", 
        "6Ter", "RMC Story", "RMC Découverte", "Chérie 25"
    ],
    "🎬 CINÉMA": [
        "AB1", "Action", "Ciné+ Premier", "Ciné+ Frisson", "Ciné+ Emotion", 
        "Ciné+ Famiz", "Ciné+ Classic", "Crime District", "OCS Max", "OCS City", 
        "OCS Choc", "OCS Géants", "Mangas", "Paramount Channel", "RTL9", "Téva"
    ],
    "⚽ SPORTS": [
        "Canal+ Sport", "Equidia", "Eurosport 1", "Eurosport 2", "L'Equipe", "RMC Sport 1"
    ],
    "🧸 JEUNESSE": [
        "Canal J", "Disney Channel", "Gulli", "Mangas", "Piwi+", "Game One", "J-One"
    ],
    "🌍 DÉCOUVERTE": [
        "Animaux", "Histoire TV", "Le Figaro TV", "Montagne TV", "Museum TV", 
        "National Geographic", "Planète+", "Science & Vie TV", "Toute l'Histoire", 
        "Ushuaïa TV", "RMC Découverte"
    ],
    "📰 INFOS": [
        "BFM Business", "Euronews", "France 24", "i24 News", "Le Figaro TV", "LCI", "La Chaîne Météo"
    ],
    "🎶 MUSIQUE & DIVERTISSEMENT": [
        "MCM", "Mezzo", "MTV France"
    ],
    "📍 RÉGIONALES": [
        "7ALimoges", "8 Mont-Blanc", "Alsace 20", "ASTV", "BFM Grand Lille", 
        "BFM Grand Littoral", "BFM Lyon", "BFM Marseille", "BFM Nice", 
        "BFM Paris", "BIP TV", "IDF1", "Télénantes", "TV7 Bordeaux", 
        "Vosges TV", "Charente Libre", "Canal Alpha", "KTO"
    ],
    "🌍 INTERNATIONAL": [
        "24h au Bénin", "3A Telesud", "Africa 24", "Africanews", "Al Aoula", 
        "Antenne Réunion", "BFM West", "BRTV", "Canal 10", "Canal 3 Monde", 
        "Canal+ Afrique", "France Ô", "TV5 Monde"
    ]
}

def clean_name(name):
    """ Nettoie le nom pour une comparaison robuste (minuscules, sans caractères spéciaux) """
    if not name: return ""
    name = re.sub(r'\(.*\)', '', name)
    name = re.sub(r'[^a-zA-Z0-9]', '', name).lower()
    return name

def filter_playlist():
    print(f"Téléchargement de la playlist depuis {SOURCE_URL}...")
    try:
        # On tente de récupérer la liste brute
        response = requests.get(SOURCE_URL, timeout=30)
        response.raise_for_status()
    except Exception as e:
        print(f"Erreur lors de la récupération de la source : {e}")
        return

    lines = response.text.splitlines()
    organized_content = {cat: [] for cat in CATEGORIES}
    found_targets = set()
    
    current_info = ""
    for line in lines:
        if line.startswith("#EXTINF"):
            current_info = line
        elif line.startswith("http"):
            # Extraction du nom après la virgule dans la ligne #EXTINF
            match = re.search(r',(.+)$', current_info)
            if not match: continue
            
            raw_source_name = match.group(1).strip()
            clean_source = clean_name(raw_source_name)
            
            # On compare avec notre dictionnaire de catégories
            for cat_name, channel_list in CATEGORIES.items():
                for target_channel in channel_list:
                    clean_target = clean_name(target_channel)
                    
                    # Matching intelligent : correspondance exacte ou inclusion
                    if clean_target == clean_source or (clean_target in clean_source and len(clean_target) > 3):
                        # On réécrit la ligne pour inclure le groupe (catégorie) et le nom propre
                        new_info = re.sub(r'group-title="[^"]+"', f'group-title="{cat_name}"', current_info)
                        new_info = re.sub(r',(.+)$', f',{target_channel}', new_info)
                        
                        organized_content[cat_name].append((new_info, line))
                        found_targets.add(target_channel)
                        break

    # Génération du fichier M3U final sur le disque du container
    final_lines = ["#EXTM3U"]
    total_count = 0
    
    for cat in CATEGORIES:
        category_urls = set()
        for info, url in organized_content[cat]:
            # Éviter les doublons de flux pour une même catégorie
            if url not in category_urls:
                final_lines.append(info)
                final_lines.append(url)
                category_urls.add(url)
                total_count += 1

    # Rapport des chaînes non trouvées dans la source actuelle
    all_targets = set([chan for sublist in CATEGORIES.values() for chan in sublist])
    missing = all_targets - found_targets
    if missing:
        print(f"\n--- Chaînes manquantes dans la source ({len(missing)}) ---")
        print(", ".join(sorted(list(missing))))

    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(final_lines))
        print(f"\nScript terminé : {total_count} chaînes filtrées et enregistrées dans {OUTPUT_FILE}.")
    except Exception as e:
        print(f"Erreur d'écriture du fichier : {e}")

if __name__ == "__main__":
    filter_playlist()
