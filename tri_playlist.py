import requests
import re
import os

# Configuration
SOURCE_URL = "https://iptv-org.github.io/iptv/languages/fra.m3u"
OUTPUT_FILE = "generated.m3u"

# --- DICTIONNAIRE DE TRI MANUEL (Mise à jour 2026) ---
CATEGORIES = {
    "🇫🇷 TNT (Arcom)": [
        "TF1", "France 2", "France 3", "Canal+", "France 5", "M6", "Arte", "C8", 
        "W9", "TMC", "TFX", "NRJ 12", "LCP", "Public Sénat", "France 4", "BFM TV", 
        "CNews", "CStar", "Gulli", "France Info", "TF1 Séries Films", "L'Equipe", 
        "6ter", "RMC Story", "RMC Découverte", "Chérie 25"
    ],
    "🎬 CINÉMA & SÉRIES": [
        "AB1", "Action", "Ciné+ Premier", "Ciné+ Frisson", "Ciné+ Emotion", 
        "Ciné+ Famiz", "Ciné+ Classic", "Crime District", "OCS Max", "OCS City", 
        "OCS Choc", "OCS Géants", "Paramount Channel", "RTL9", "Téva", "Mangas"
    ],
    "⚽ SPORTS": [
        "Canal+ Sport", "Equidia", "Eurosport 1", "Eurosport 2", "L'Equipe", "RMC Sport 1"
    ],
    "🧸 JEUNESSE": [
        "Canal J", "Disney Channel", "Gulli", "Mangas", "Piwi+"
    ],
    "🌍 DÉCOUVERTE": [
        "Animaux", "Histoire TV", "Museum TV", "National Geographic", "Planète+", 
        "Science & Vie TV", "Toute l'Histoire", "Ushuaïa TV", "Montagne TV", "Le Figaro TV"
    ],
    "📰 INFOS": [
        "BFM Business", "Euronews", "France 24", "i24 News", "LCI", "La Chaîne Météo"
    ],
    "🎶 MUSIQUE": [
        "MCM", "Mezzo", "MTV France"
    ],
    "🌍 INTERNATIONAL & RÉGIONAL": [
        "TV5 Monde", "Al Aoula", "Antenne Réunion", "Africa 24", "Africanews", "3A Telesud"
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
            # Nettoyage pour comparaison : on enlève les parenthèses et on met en minuscule
            clean_name_for_comp = re.sub(r'\s?\(.*\)', '', raw_name).strip().lower()
            
            for cat_name, channel_list in CATEGORIES.items():
                for target_channel in channel_list:
                    # Comparaison exacte ou contenue sans tenir compte de la casse
                    target_lower = target_channel.lower()
                    
                    # Logique de correspondance
                    if target_lower == clean_name_for_comp or (target_lower in clean_name_for_comp and len(target_lower) > 3):
                        # On prépare l'info de la chaîne avec le bon groupe
                        display_info = re.sub(r'group-title="[^"]+"', f'group-title="{cat_name}"', current_info)
                        # On force le nom propre défini dans notre dictionnaire pour un affichage propre
                        display_info = re.sub(r',(.+)$', f',{target_channel}', display_info)
                        
                        organized_content[cat_name].append((display_info, line))
                        # On ne fait pas de break ici pour autoriser la chaîne à être dans une autre catégorie
    
    # Génération du fichier M3U
    final_lines = ["#EXTM3U"]
    count = 0
    for cat in CATEGORIES:
        # On utilise un set pour éviter les doublons STRICTS au sein d'une même catégorie
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
        print(f"Succès ! {count} entrées générées dans {OUTPUT_FILE}.")
    except Exception as e:
        print(f"Erreur lors de l'écriture : {e}")

if __name__ == "__main__":
    filter_playlist()
