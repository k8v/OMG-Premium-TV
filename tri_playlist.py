import requests
import re
import os

# Configuration
SOURCE_URL = "https://iptv-org.github.io/iptv/languages/fra.m3u"
OUTPUT_FILE = "generated.m3u"

# --- DICTIONNAIRE DE TRI MANUEL (Mise à jour selon liste utilisateur) ---
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
        "Canal J", "Disney Channel", "Gulli", "Mangas", "Piwi+"
    ],
    "🌍 DÉCOUVERTE": [
        "Animaux", "Histoire TV", "Le Figaro TV", "Montagne TV", "Museum TV", 
        "National Geographic", "Planète+", "Science & Vie TV", "Toute l'Histoire", 
        "Ushuaïa TV", "RMC Découverte"
    ],
    "📰 INFOS": [
        "BFM Business", "Euronews (Français)", "France 24 (Français)", 
        "i24 News (Français)", "Le Figaro TV", "LCI", "La Chaîne Météo"
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

def filter_playlist():
    print(f"Téléchargement de la playlist depuis {SOURCE_URL}...")
    try:
        response = requests.get(SOURCE_URL, timeout=30)
        response.raise_for_status()
    except Exception as e:
        print(f"Erreur de téléchargement : {e}")
        return

    lines = response.text.splitlines()
    organized_content = {cat: [] for cat in CATEGORIES}
    
    current_info = ""
    for line in lines:
        if line.startswith("#EXTINF"):
            current_info = line
        elif line.startswith("http"):
            match = re.search(r',(.+)$', current_info)
            if not match: continue
            
            raw_name = match.group(1).strip()
            # Nettoyage pour comparaison : on enlève les parenthèses (ex: (Français)) pour la recherche
            clean_name_for_comp = re.sub(r'\s?\(.*\)', '', raw_name).strip().lower()
            
            for cat_name, channel_list in CATEGORIES.items():
                for target_channel in channel_list:
                    # On nettoie aussi le nom cible pour la comparaison
                    target_clean = re.sub(r'\s?\(.*\)', '', target_channel).strip().lower()
                    
                    # Logique de correspondance (exacte ou partielle si nom long)
                    if target_clean == clean_name_for_comp or (target_clean in clean_name_for_comp and len(target_clean) > 3):
                        # On met à jour le groupe et on force le nom propre défini dans la liste
                        display_info = re.sub(r'group-title="[^"]+"', f'group-title="{cat_name}"', current_info)
                        display_info = re.sub(r',(.+)$', f',{target_channel}', display_info)
                        
                        organized_content[cat_name].append((display_info, line))
    
    # Génération du fichier M3U final
    final_lines = ["#EXTM3U"]
    count = 0
    for cat in CATEGORIES:
        seen_urls = set()
        for info, url in organized_content[cat]:
            if url not in seen_urls:
                final_lines.append(info)
                final_lines.append(url)
                seen_urls.add(url)
                count += 1

    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(final_lines))
        print(f"Succès ! {count} entrées générées dans {OUTPUT_FILE} avec les nouvelles catégories.")
    except Exception as e:
        print(f"Erreur lors de l'écriture : {e}")

if __name__ == "__main__":
    filter_playlist()
