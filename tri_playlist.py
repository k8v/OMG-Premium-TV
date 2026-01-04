import requests
import re
import os

# Configuration
SOURCE_URL = "https://iptv-org.github.io/iptv/languages/fra.m3u"
# On utilise le dossier temp interne à OMG
OUTPUT_FILE = "temp/generated_playlist.m3u"

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
    EXCLUDE = ["SHOPPING", "RELIGION", "ADULT", "RADIO", "PROMO"]
    
    current_info = ""
    count = 0

    for line in lines:
        if line.startswith("#EXTINF"):
            current_info = line
        elif line.startswith("http"):
            # 1. Vérification de l'exclusion
            if any(word in current_info.upper() for word in EXCLUDE):
                continue

            # 2. Identification du Pays (Basé sur le nom ou tags iptv-org)
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
            if any(x in info_upper for x in ["SPORT", "BEIN", "CANAL+"]):
                genre = "Sports"
            elif any(x in info_upper for x in ["NEWS", "INFO", "JOURNAL", "LCI"]):
                genre = "Infos"
            elif any(x in info_upper for x in ["KIDS", "ENFANT", "CARTOON", "DISNEY"]):
                genre = "Enfants"
            elif any(x in info_upper for x in ["CINEMA", "FILM", "MOVIE"]):
                genre = "Cinéma"
            elif any(x in info_upper for x in ["MUSIC", "MTV", "TRACE"]):
                genre = "Musique"

            # 4. Reconstruction du groupe (group-title)
            # On remplace le groupe existant par notre tri : PAYS | GENRE
            new_group = f'{country_prefix} | {genre}'
            
            # Regex pour remplacer le group-title existant ou l'ajouter
            if 'group-title="' in current_info:
                current_info = re.sub(r'group-title="[^"]+"', f'group-title="{new_group}"', current_info)
            else:
                current_info = current_info.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="{new_group}"')

            # 5. Nettoyage du nom de la chaîne (optionnel)
            # On peut enlever les "(France)" etc du nom affiché
            current_info = re.sub(r',(.+?)\s?\(.*\)', r',\1', current_info)

            filtered_lines.append(current_info)
            filtered_lines.append(line)
            count += 1

    # Création du dossier temp si absent
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(filtered_lines))
    
    print(f"Succès ! {count} chaînes triées dans {OUTPUT_FILE}")

if __name__ == "__main__":
    filter_playlist()
