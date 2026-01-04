import requests
import re
import os

# Configuration
# Utilisation de sources plus robustes et maintenues
SOURCE_URLS = [
    "https://iptv-org.github.io/iptv/languages/fra.m3u",
    "https://raw.githubusercontent.com/mcreal/m3u8-france/master/france.m3u",
    "https://raw.githubusercontent.com/freetv-app/freetv-app/master/playlists/playlist_france.m3u"
]
OUTPUT_FILE = "generated.m3u"

# --- DICTIONNAIRE DE TRI MANUEL ---
CATEGORIES = {
    "🇫🇷 TNT": [
        ["TF1", "TF 1"], ["TF1 Séries Films", "TF1 Series"], ["France 2"], ["France 3"], 
        ["France 4"], ["France 5"], ["Canal+", "Canal Plus"], ["M6"], ["Arte"], ["LCP"], 
        ["W9"], ["TMC"], ["TFX"], ["Gulli"], ["BFM TV", "BFMTV"], 
        ["CNEWS", "C NEWS"], ["LCI"], ["Franceinfo", "France info"], ["CSTAR", "C STAR"], 
        ["L'Equipe", "L'Équipe"], ["6Ter"], ["RMC Story"], ["RMC Découverte"], ["Chérie 25"]
    ],
    "🎬 CINÉMA": [
        ["AB1"], ["Action"], ["Ciné+ Premier", "Cine+ Premier"], ["Ciné+ Frisson"], 
        ["Ciné+ Emotion"], ["Ciné+ Famiz"], ["Ciné+ Classic"], ["Crime District"], 
        ["OCS Max"], ["OCS City"], ["OCS Choc"], ["OCS Géants"], ["Mangas"], 
        ["Paramount Channel"], ["RTL9"], ["Téva", "Teva"]
    ],
    "⚽ SPORTS": [
        ["Canal+ Sport"], ["Equidia"], ["Eurosport 1"], ["Eurosport 2"], ["RMC Sport 1"]
    ],
    "🧸 JEUNESSE": [
        ["Canal J"], ["Disney Channel"], ["Piwi+"], ["Game One"], ["J-One"]
    ],
    "🌍 DÉCOUVERTE": [
        ["Animaux"], ["Histoire TV"], ["Le Figaro TV"], ["Montagne TV"], 
        ["Museum TV"], ["National Geographic", "Nat Geo"], ["Planète+"], 
        ["Science & Vie TV"], ["Toute l'Histoire"], ["Ushuaïa TV"]
    ],
    "📰 INFOS": [
        ["BFM Business"], ["Euronews"], ["France 24"], ["i24 News"], ["La Chaîne Météo"]
    ],
    "📍 RÉGIONALES": [
        ["7ALimoges"], ["8 Mont-Blanc"], ["Alsace 20"], ["ASTV"], ["BFM Paris"], 
        ["BIP TV"], ["IDF1"], ["Télénantes"], ["TV7 Bordeaux"], ["Vosges TV"]
    ],
    "🌍 INTERNATIONAL": [
        ["24h au Bénin"], ["3A Telesud"], ["Africa 24"], ["Al Aoula"], ["Canal+ Afrique"]
    ]
}

def clean_name(name):
    """ Nettoie le nom pour une comparaison robuste """
    if not name: return ""
    return re.sub(r'[^a-zA-Z0-9]', '', name).lower()

def filter_playlist():
    found_targets = {} # {nom_chaine: (info, url, categorie)}
    
    # 1. Téléchargement des sources
    all_lines = []
    for url in SOURCE_URLS:
        print(f"Téléchargement de la playlist depuis {url}...")
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            all_lines.extend(r.text.splitlines())
        except Exception as e:
            print(f"Saut de la source {url} : {e}")

    # 2. Analyse
    current_info = ""
    for line in all_lines:
        line = line.strip()
        if line.startswith("#EXTINF"):
            current_info = line
        elif line.startswith("http") and current_info:
            name_match = re.search(r',([^,]+)$', current_info)
            if not name_match: continue
            
            raw_name = name_match.group(1).strip()
            clean_raw = clean_name(raw_name)
            
            for cat, channels in CATEGORIES.items():
                for aliases in channels:
                    main_name = aliases[0]
                    if main_name in found_targets: continue
                    
                    if any(clean_name(a) == clean_raw for a in aliases):
                        # Mise à jour du group-title
                        new_info = re.sub(r'group-title="[^"]+"', f'group-title="{cat}"', current_info)
                        if 'group-title="' not in new_info:
                            new_info = new_info.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="{cat}"')
                        
                        # Fix du nom final
                        final_info = re.sub(r',[^,]+$', f',{main_name}', new_info)
                        found_targets[main_name] = (final_info, line, cat)

    # 3. Écriture
    output_content = ["#EXTM3U"]
    for cat in CATEGORIES.keys():
        for name, data in found_targets.items():
            if data[2] == cat:
                output_content.append(data[0])
                output_content.append(data[1])

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(output_content))

    # 4. Rapport de contrôle dédoublonné
    all_req = list(dict.fromkeys([c[0] for cat in CATEGORIES.values() for c in cat]))
    missing = sorted([c for c in all_req if c not in found_targets])
    
    if missing:
        print(f"\n--- Chaînes toujours introuvables ({len(missing)}) ---")
        print(", ".join(missing))
    
    print(f"\nSuccès : {len(found_targets)} chaînes uniques filtrées dans {OUTPUT_FILE}.")

if __name__ == "__main__":
    filter_playlist()
