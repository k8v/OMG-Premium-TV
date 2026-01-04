import requests
import re
import os

# Configuration
SOURCE_URL = "https://iptv-org.github.io/iptv/languages/fra.m3u"
# On va générer le fichier à deux endroits pour maximiser la détection par l'addon
OUTPUT_FILE = "generated_playlist.m3u"
TEMP_FILE = "temp/generated_playlist.m3u"

def filter_playlist():
    print(f"Téléchargement de la playlist depuis {SOURCE_URL}...")
    try:
        response = requests.get(SOURCE_URL, timeout=30)
        response.raise_for_status()
    except Exception as e:
        print(f"Erreur lors du téléchargement : {e}")
        return

    lines = response.text.splitlines()
    filtered_lines = ["#EXTM3U"]
    
    # Mots-clés pour exclure les chaînes indésirables
    EXCLUDE = ["SHOPPING", "RELIGION", "ADULT", "RADIO", "PROMO", "LOTTO"]
    
    # Liste des chaînes de la TNT française pour un groupe dédié
    TNT_FR = [
        "TF1", "FRANCE 2", "FRANCE 3", "CANAL+", "FRANCE 5", "M6", "ARTE", "C8", 
        "W9", "TMC", "TFX", "NRJ 12", "LCP", "PUBLIC SENAT", "FRANCE 4", "BFM TV", 
        "CNEWS", "CSTAR", "GULLI", "FRANCE INFO", "25", "L'EQUIPE", "6TER", 
        "RMC STORY", "RMC DECOUVERTE", "CHERIE 25"
    ]

    current_info = ""
    count = 0

    for line in lines:
        if line.startswith("#EXTINF"):
            current_info = line
        elif line.startswith("http"):
            # 1. Vérification de l'exclusion
            if any(word in current_info.upper() for word in EXCLUDE):
                continue

            # 2. Identification du Pays
            country_prefix = "🌍 AUTRES"
            if "France" in current_info or "(France)" in current_info:
                country_prefix = "🇫🇷 FRANCE"
            elif "Belgium" in current_info or "Belgique" in current_info:
                country_prefix = "🇧🇪 BELGIQUE"
            elif "Canada" in current_info:
                country_prefix = "🇨🇦 CANADA"
            elif "Switzerland" in current_info or "Suisse" in current_info:
                country_prefix = "🇨🇭 SUISSE"
            elif "Africa" in current_info or "Afrique" in current_info:
                country_prefix = "🌍 AFRIQUE"

            # 3. Identification du Type (Genre)
            genre = "Général"
            info_upper = current_info.upper()
            
            # Test spécifique pour la TNT Française
            is_tnt = False
            if country_prefix == "🇫🇷 FRANCE":
                for tnt_chan in TNT_FR:
                    if tnt_chan in info_upper:
                        genre = "TNT"
                        is_tnt = True
                        break

            if not is_tnt:
                if any(x in info_upper for x in ["SPORT", "BEIN", "CANAL+", "EQUIPE"]):
                    genre = "Sports"
                elif any(x in info_upper for x in ["NEWS", "INFO", "JOURNAL", "LCI", "FRANCE 24"]):
                    genre = "Infos"
                elif any(x in info_upper for x in ["KIDS", "ENFANT", "CARTOON", "DISNEY", "NICKELODEON"]):
                    genre = "Enfants"
                elif any(x in info_upper for x in ["CINEMA", "FILM", "MOVIE", "ACTION"]):
                    genre = "Cinéma"
                elif any(x in info_upper for x in ["MUSIC", "MTV", "TRACE", "MEZZO"]):
                    genre = "Musique"
                elif any(x in info_upper for x in ["DOCUMENTAIRE", "DISCOVERY", "HISTORY", "PLANETE", "SCIENCE"]):
                    genre = "Documentaires"

            # 4. Reconstruction du groupe (group-title)
            new_group = f'{country_prefix} | {genre}'
            
            if 'group-title="' in current_info:
                current_info = re.sub(r'group-title="[^"]+"', f'group-title="{new_group}"', current_info)
            else:
                current_info = current_info.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="{new_group}"')

            # 5. Nettoyage du nom de la chaîne
            match = re.search(r',(.+)$', current_info)
            if match:
                channel_name = match.group(1).strip()
                channel_name = re.sub(r'\s?\(.*\)', '', channel_name).strip()
                current_info = current_info[:match.start(1)] + channel_name

            filtered_lines.append(current_info)
            filtered_lines.append(line)
            count += 1

    # Gestion de la sortie
    content = "\n".join(filtered_lines)
    
    try:
        # Écriture à la racine (plus de chances d'être vu par l'addon)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Écriture dans temp au cas où
        if not os.path.exists("temp"):
            os.makedirs("temp", exist_ok=True)
        with open(TEMP_FILE, "w", encoding="utf-8") as f:
            f.write(content)
            
        print(f"Succès ! {count} chaînes triées.")
        print(f"Fichiers créés : {os.path.abspath(OUTPUT_FILE)} et {os.path.abspath(TEMP_FILE)}")
        
        # DEBUG : Lister les fichiers pour voir où ils sont réellement
        print("Contenu du dossier actuel :", os.listdir('.'))
        
    except Exception as e:
        print(f"Erreur lors de l'écriture : {str(e)}")

if __name__ == "__main__":
    filter_playlist()
