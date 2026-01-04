import requests
import re
import os

# Configuration
SOURCE_URL = "https://iptv-org.github.io/iptv/languages/fra.m3u"
OUTPUT_FILE = "generated.m3u"

# --- DICTIONNAIRE COMPLET ET EXHAUSTIF ---
CATEGORIES = {
    "🇫🇷 TNT": [
        ["TF1", ["TF1"]], ["France 2", ["France 2"]], ["France 3", ["France 3"]], 
        ["France 4", ["France 4"]], ["France 5", ["France 5"]], 
        ["M6", ["M6"]], ["Arte", ["Arte"]], ["C8", ["C8", "D8"]], 
        ["W9", ["W9"]], ["TMC", ["TMC"]], ["TFX", ["TFX"]], ["NRJ 12", ["NRJ 12", "NRJ12"]], 
        ["LCP", ["LCP", "Public Senat"]], ["BFM TV", ["BFM TV", "BFMTV"]], 
        ["CNews", ["CNews"]], ["CSTAR", ["CSTAR"]], ["Gulli", ["Gulli"]], 
        ["TF1 Séries Films", ["TF1 Series", "TF1 Séries"]], ["L'Equipe", ["L'Equipe", "L'Équipe"]], 
        ["6ter", ["6ter"]], ["RMC Story", ["RMC Story"]], ["RMC Découverte", ["RMC Découverte"]], 
        ["Chérie 25", ["Chérie 25"]], ["LCI", ["LCI"]], ["Franceinfo", ["Franceinfo"]]
    ],
    "🎬 CINÉMA & DIV": [
        ["Canal+", ["Canal+"]], ["Canal+ Sport", ["Canal+ Sport"]], 
        ["Canal+ Cinema", ["Canal+ Cinema", "Ciné+"]], ["Canal+ Kids", ["Canal+ Kids"]], 
        ["Canal+ Series", ["Canal+ Series"]], ["AB1", ["AB1"]], ["Action", ["Action"]], 
        ["RTL9", ["RTL9"]], ["Téva", ["Téva", "Teva"]], ["TV5 Monde", ["TV5 Monde", "TV5Monde"]],
        ["Paramount Channel", ["Paramount Channel"]], ["Crime District", ["Crime District"]], 
        ["Comedy Central", ["Comedy Central"]], ["Warner TV", ["Warner TV"]],
        ["OCS Max", ["OCS Max"]], ["OCS City", ["OCS City"]], ["OCS Choc", ["OCS Choc"]], 
        ["OCS Géants", ["OCS Géants"]]
    ],
    "⚽ SPORTS": [
        ["BeIN Sports 1", ["BeIN Sports 1"]], ["BeIN Sports 2", ["BeIN Sports 2"]], 
        ["BeIN Sports 3", ["BeIN Sports 3"]], ["Eurosport 1", ["Eurosport 1"]], 
        ["Eurosport 2", ["Eurosport 2"]], ["RMC Sport 1", ["RMC Sport 1"]], 
        ["Equidia", ["Equidia"]], ["AutoMoto", ["AutoMoto"]]
    ],
    "🧸 JEUNESSE": [
        ["Disney Channel", ["Disney Channel"]], ["Disney Junior", ["Disney Junior"]], 
        ["Nickelodeon", ["Nickelodeon"]], ["TiJi", ["TiJi"]], ["Piwi+", ["Piwi+"]], 
        ["Canal J", ["Canal J"]], ["Cartoon Network", ["Cartoon Network"]], 
        ["Boomerang", ["Boomerang"]], ["Mangas", ["Mangas"]]
    ],
    "🌍 DÉCOUVERTE": [
        ["National Geographic", ["National Geographic", "Nat Geo"]], 
        ["Planète+", ["Planète+", "Planete+"]], ["Ushuaïa TV", ["Ushuaïa TV"]], 
        ["Histoire TV", ["Histoire TV"]], ["Toute l'Histoire", ["Toute l'Histoire"]], 
        ["Science & Vie TV", ["Science & Vie TV"]], ["Animaux", ["Animaux"]], 
        ["Museum TV", ["Museum TV"]], ["Le Figaro TV", ["Le Figaro TV"]], 
        ["Montagne TV", ["Montagne TV"]]
    ]
}

def normalize(text):
    """ Nettoyage pour comparaison """
    if not text: return ""
    text = re.sub(r'\(.*?\)', '', text)
    text = text.lower()
    text = re.sub(r'[^a-z0-9]', '', text)
    return text

def filter_playlist():
    print(f"Analyse de la source : {SOURCE_URL}...")
    try:
        r = requests.get(SOURCE_URL, timeout=20)
        r.raise_for_status()
        content = r.text
    except Exception as e:
        print(f"Erreur de téléchargement : {e}")
        return

    entries = re.findall(r'(#EXTINF:.*?\n(?:#EXTVLCOPT:.*?\n)*http.*)', content, re.MULTILINE)
    
    found_channels = {} # {MainName: {info, url, opts}}
    other_channels = [] # Liste des chaînes non catégorisées

    for entry in entries:
        lines = entry.splitlines()
        info_line = lines[0]
        url_line = lines[-1]
        vlc_opts = [l for l in lines[1:-1] if l.startswith("#EXTVLCOPT")]

        name_match = re.search(r',([^,]+)$', info_line)
        if not name_match: continue
        raw_name = name_match.group(1).strip()
        clean_raw = normalize(raw_name)

        matched = False
        for cat, groups in CATEGORIES.items():
            for item in groups:
                main_name = item[0]
                aliases = item[1]
                
                if main_name in found_channels: 
                    if any(normalize(a) == clean_raw for a in aliases):
                        matched = True # On considère comme traité même si doublon
                        break
                    continue

                if any(normalize(a) == clean_raw or normalize(a) in clean_raw for a in aliases):
                    new_info = info_line
                    if 'group-title="' in new_info:
                        new_info = re.sub(r'group-title="[^"]+"', f'group-title="{cat}"', new_info)
                    else:
                        new_info = new_info.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="{cat}"')
                    
                    new_info = re.sub(r',.*$', f',{main_name}', new_info)

                    found_channels[main_name] = {
                        "info": new_info,
                        "url": url_line,
                        "opts": vlc_opts
                    }
                    matched = True
                    break
            if matched: break
        
        # Si la chaîne n'a pas été trouvée dans les catégories, on la garde dans "AUTRES"
        if not matched:
            other_info = info_line
            if 'group-title="' in other_info:
                other_info = re.sub(r'group-title="[^"]+"', 'group-title="🌐 AUTRES CHAÎNES"', other_info)
            else:
                other_info = other_info.replace('#EXTINF:-1', '#EXTINF:-1 group-title="🌐 AUTRES CHAÎNES"')
            
            other_channels.append({
                "info": other_info,
                "url": url_line,
                "opts": vlc_opts
            })

    # Génération du fichier
    output = ["#EXTM3U"]
    # 1. Chaînes triées
    for cat in CATEGORIES.keys():
        for item in CATEGORIES[cat]:
            name = item[0]
            if name in found_channels:
                chan = found_channels[name]
                output.append(chan["info"])
                output.extend(chan["opts"])
                output.append(chan["url"])
    
    # 2. Toutes les autres chaînes
    for chan in other_channels:
        output.append(chan["info"])
        output.extend(chan["opts"])
        output.append(chan["url"])

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(output))

    print(f"\n--- Résumé ---")
    print(f"Chaînes catégorisées : {len(found_channels)}")
    print(f"Chaînes ajoutées en vrac : {len(other_channels)}")
    print(f"Total : {len(found_channels) + len(other_channels)}")

if __name__ == "__main__":
    filter_playlist()
