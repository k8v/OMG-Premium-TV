import requests
import re
import os

# Configuration
SOURCE_URL = "https://iptv-org.github.io/iptv/languages/fra.m3u"
OUTPUT_FILE = "generated.m3u"

# --- DICTIONNAIRE COMPLET ET EXHAUSTIF ---
CATEGORIES = {
    "🇫🇷 TNT": [
        ["TF1"], ["France 2"], ["France 3"], ["France 4"], ["France 5"], 
        ["M6"], ["Arte"], ["C8"], ["W9"], ["TMC"], ["TFX"], ["NRJ 12", "NRJ12"], 
        ["LCP"], ["France 4"], ["BFM TV", "BFMTV"], ["CNews"], ["CSTAR"], 
        ["Gulli"], ["TF1 Séries Films", "TF1 Series"], ["L'Equipe", "L'Équipe"], 
        ["6ter"], ["RMC Story"], ["RMC Découverte"], ["Chérie 25"], ["LCI"], ["Franceinfo"]
    ],
    "🎬 CINÉMA & DIV": [
        ["Canal+"], ["Canal+ Sport"], ["Canal+ Cinema"], ["Canal+ Kids"], ["Canal+ Series"],
        ["TF1+"], ["AB1"], ["Action"], ["RTL9"], ["Téva", "Teva"], ["TV5 Monde", "TV5Monde"],
        ["Paramount Channel"], ["Crime District"], ["Comedy Central"], ["Warner TV"],
        ["Ciné+ Premier", "Cine+ Premier"], ["Ciné+ Frisson"], ["Ciné+ Emotion"], 
        ["Ciné+ Famiz"], ["Ciné+ Classic"], ["Ciné+ Club"], ["Ciné+ Star"],
        ["OCS Max"], ["OCS City"], ["OCS Choc"], ["OCS Géants"]
    ],
    "⚽ SPORTS": [
        ["BeIN Sports 1"], ["BeIN Sports 2"], ["BeIN Sports 3"], 
        ["Eurosport 1"], ["Eurosport 2"], ["RMC Sport 1"], ["Equidia"], ["AutoMoto"]
    ],
    "🧸 JEUNESSE": [
        ["Disney Channel"], ["Disney Junior"], ["Nickelodeon"], ["TiJi"], 
        ["Piwi+"], ["Canal J"], ["Cartoon Network"], ["Boomerang"], ["Mangas"]
    ],
    "🌍 DÉCOUVERTE": [
        ["National Geographic", "Nat Geo"], ["Planète+"], ["Ushuaïa TV"], 
        ["Histoire TV"], ["Toute l'Histoire"], ["Science & Vie TV"], 
        ["Animaux"], ["Museum TV"], ["Le Figaro TV"], ["Montagne TV"]
    ],
    "🎶 MUSIQUE": [
        ["MCM"], ["MCM Top"], ["MCM Pop"], ["Mezzo"], ["MTV France", "MTV"], 
        ["Trace Urban"], ["RFM TV"], ["Melody"]
    ],
    "📍 RÉGIONALES & INTERNATIONAL": [
        ["7ALimoges"], ["8 Mont-Blanc"], ["Alsace 20"], ["BFM Paris"], ["BFM Lyon"],
        ["TV7 Bordeaux"], ["Télénantes"], ["Vosges TV"], ["KTO"], ["IDF1"],
        ["2M Monde"], ["Al Aoula"], ["Canal+ Afrique"], ["France 24"]
    ]
}

def normalize(text):
    """ Nettoyage profond pour le matching """
    if not text: return ""
    # Enlever (720p), (1080p), (France), etc.
    text = re.sub(r'\(.*?\)', '', text)
    # Enlever les caractères spéciaux et mettre en minuscule
    return re.sub(r'[^a-z0-9]', '', text.lower())

def filter_playlist():
    print(f"Analyse de la source : {SOURCE_URL}...")
    try:
        r = requests.get(SOURCE_URL, timeout=20)
        r.raise_for_status()
        lines = r.text.splitlines()
    except Exception as e:
        print(f"Erreur lors du téléchargement : {e}")
        return

    found_channels = {} # {NomPropre: (InfoLine, Url)}
    current_extinf = ""
    vlc_opts = []

    for line in lines:
        line = line.strip()
        if line.startswith("#EXTINF"):
            current_extinf = line
            vlc_opts = []
        elif line.startswith("#EXTVLCOPT"):
            vlc_opts.append(line)
        elif line.startswith("http"):
            # Extraction du nom après la virgule
            name_match = re.search(r',([^,]+)$', current_extinf)
            if not name_match: continue
            
            raw_name = name_match.group(1).strip()
            clean_raw = normalize(raw_name)
            
            for cat, groups in CATEGORIES.items():
                for aliases in groups:
                    main_name = aliases[0]
                    if main_name in found_channels: continue
                    
                    # Vérification si l'un des alias matche le nom brut de la source
                    if any(normalize(a) == clean_raw or normalize(a) in clean_raw for a in aliases):
                        # On reconstruit l'entrée proprement
                        # 1. On injecte la catégorie
                        info = re.sub(r'group-title="[^"]+"', f'group-title="{cat}"', current_extinf)
                        if 'group-title="' not in info:
                            info = info.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="{cat}"')
                        
                        # 2. On nettoie le nom d'affichage
                        info = re.sub(r',.*$', f',{main_name}', info)
                        
                        found_channels[main_name] = {
                            "info": info,
                            "url": line,
                            "opts": vlc_opts,
                            "cat": cat
                        }

    # Création du fichier final
    output = ["#EXTM3U"]
    for cat in CATEGORIES.keys():
        for name in [g[0] for g in CATEGORIES[cat]]:
            if name in found_channels:
                chan = found_channels[name]
                output.append(chan["info"])
                for opt in chan["opts"]:
                    output.append(opt)
                output.append(chan["url"])

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(output))

    # Rapport final
    requested = [g[0] for cat in CATEGORIES.values() for g in cat]
    missing = sorted([c for c in requested if c not in found_channels])
    
    print(f"\n--- Résumé ---")
    print(f"Chaînes trouvées : {len(found_channels)}")
    print(f"Chaînes manquantes : {len(missing)}")
    if missing:
        print(f"Manquantes : {', '.join(missing)}")

if __name__ == "__main__":
    filter_playlist()
