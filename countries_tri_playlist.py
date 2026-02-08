#V0.3
import requests
import re
import os

# Configuration
SOURCE_URL = "https://iptv-org.github.io/iptv/countries/fr.m3u"

OUTPUT_FILE = "generated.m3u"

# --- CONFIGURATION DES CATÉGORIES ---
CATEGORIES = {
    "TNT": [
        "tf1", "france2", "france3", "france4", "france5", "m6", "arte", "c8", "w9", 
        "tmc", "tfx", "nrj12", "lcp", "bfmtv", "cnews", "cstar", "gulli", "tf1series", 
        "lequipe", "6ter", "rmcstory", "rmcdecouverte", "cherie25", "lci", "franceinfo"
    ],
    "Archives": [
        "archives", "ina", "retro", "classic"
    ],
    "Art de vivre": [
        "maison", "marmiton", "myzentv", "artdevivre", "deco", "cuisine"
    ],
    "Cinéma": [
        "canalplus", "cineplus", "ocs", "action", "studiocanal", "tcm", "sony", 
        "cinenanar", "cinewestern", "wildsidetv", "screamin", "theasylum", "emotionl"
    ],
    "Culture": [
        "museum", "culturebox", "expo", "art"
    ],
    "Divertissement": [
        "ab1", "rtl9", "teva", "comedycentral", "comedie", "justepourrire", 
        "yaquelaveritequicompte", "clique", "mcm", "mta", "enorme", "bet"
    ],
    "Documentaires": [
        "histoire", "planete", "toutehistoire", "investigation", "trek", 
        "discovery", "rmcdecouverte", "dossiersfbi"
    ],
    "Economie": [
        "bfmbusiness", "bsmart", "tvfinance", "nweconomie", "business24"
    ],
    "Généraliste": [
        "tv5monde", "ab3", "canale", "generaliste", "laune", "rtltvi"
    ],
    "Info": [
        "euronews", "france24", "i24", "figaro", "meteo", "africanews", 
        "cgtnfrench", "nwinfo", "rtfrance", "lci", "cnews", "bfmtv"
    ],
    "Jeunesse": [
        "canalj", "disney", "mangas", "piwi", "nickelodeon", "tiji", "teletoon", 
        "boomerang", "cartoon", "tivi5", "adn", "ludikids", "caillou", "bobleponge"
    ],
    "Jeux": [
        "esport", "gaming", "gameone", "nolife"
    ],
    "Local": [
        "bx1", "telenantes", "tv7", "biptv", "matele", "tl7", "monacoinfo", "tvmonaco"
    ],
    "Musique": [
        "mezzo", "mtv", "trace", "bblack", "melody", "rfm", "nrjhits", 
        "cstarhits", "m6music", "mouv", "clubbingtv", "stingray"
    ],
    "Nature": [
        "animaux", "natgeo", "ultranature", "seasons", "chasse", "peche", "wild"
    ],
    "Régional": [
        "france3", "alsace20", "weo", "tebeo", "bfmalsace", "bfmlyon", "bfmmarseille", "viatelepaese"
    ],
    "Reportages": [
        "echappeesbelles", "reportages", "envoyespecial"
    ],
    "Sciences": [
        "sciencevie", "discovery", "explora", "curiosity"
    ],
    "Séries-Films": [
        "paramount", "warner", "novelas", "crimedistrict", "serieclub", "syfy", 
        "tvbreizh", "polar", "cordier", "fillesdacote", "bbcdrama", "degrassi", 
        "heleneetlesgarcons", "lemiracledelamour", "seriemax", "intocrime"
    ],
    "Sociétal": [
        "kto", "religion", "emcitv", "ewtn", "iqraa", "handicaptv", "publicsenat"
    ],
    "Sport": [
        "sport", "bein", "eurosport", "equidia", "automoto", "rmcsport", "golf", 
        "footplus", "fighting", "nhl", "lequipe"
    ],
    "Voyage": [
        "voyage", "ushuaia", "montagne", "travelxp", "echappeesbelles", "ailleurs"
    ]
}
    "📺 PLUTO TV": [],
    "📺 SAMSUNG TV PLUS": [],
    "📺 RAKUTEN TV": [],
    "📺 SONY": [],
    "📦 AUTRES": []
}

def clean_tvg_id(info_line):
    match = re.search(r'tvg-id="([^".]+)', info_line, re.IGNORECASE)
    return match.group(1) if match else ""

def filter_playlist():
    print("Démarrage du filtrage ultime...")
    try:
        r = requests.get(SOURCE_URL, timeout=30)
        r.raise_for_status()
        content = r.text
    except Exception as e:
        print(f"Erreur : {e}")
        return

    entries = re.findall(r'(#EXTINF:.*?\n(?:#EXTVLCOPT:.*?\n)*http.*)', content, re.MULTILINE)
    output_groups = {cat: [] for cat in CATEGORIES.keys()}

    for entry in entries:
        lines = entry.splitlines()
        info_line = lines[0]
        sort_id = clean_tvg_id(info_line)
        norm_sort_id = sort_id.lower()

        # 1. Services Auto (Pluto/Samsung/Rakuten)
        auto_cat = None
        if "pluto" in norm_sort_id: auto_cat = "📺 PLUTO TV"
        elif "samsung" in norm_sort_id: auto_cat = "📺 SAMSUNG TV PLUS"
        elif "rakuten" in norm_sort_id: auto_cat = "📺 RAKUTEN TV"
        elif "sony" in norm_sort_id: auto_cat = "📺 SONY"
        
        if auto_cat:
            new_info = re.sub(r'group-title="[^"]+"', f'group-title="{auto_cat}"', info_line) if 'group-title="' in info_line else info_line.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="{auto_cat}"')
            output_groups[auto_cat].append({'sort_key': sort_id, 'data': f"{new_info}\n" + "\n".join(lines[1:])})
            continue

        # 2. Classement par catégories
        matched = False
        for cat_name, keywords in CATEGORIES.items():
            #if any(k in norm_sort_id for k in keywords):
            if any(k.lower() in norm_sort_id for k in keywords):
                if 'group-title="' in info_line:
                    new_info = re.sub(r'group-title="[^"]+"', f'group-title="{cat_name}"', info_line)
                else:
                    new_info = info_line.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="{cat_name}"')
                
                output_groups[cat_name].append({'sort_key': sort_id, 'data': f"{new_info}\n" + "\n".join(lines[1:])})
                matched = True
                break
        
        # 3. Repli si rien n'est trouvé
        if not matched:
            new_info = re.sub(r'group-title="[^"]+"', f'group-title="📦 AUTRES"', info_line) if 'group-title="' in info_line else info_line.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="📦 AUTRES"')
            output_groups["📦 AUTRES"].append({'sort_key': sort_id, 'data': f"{new_info}\n" + "\n".join(lines[1:])})

    # Écriture finale
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for cat in CATEGORIES.keys():
            # Tri alphabétique par le nom propre extrait du tvg-id
            sorted_channels = sorted(output_groups[cat], key=lambda x: x['sort_key'].lower())
            for item in sorted_channels:
                f.write(item['data'] + "\n")
    
    print(f"Playlist '{OUTPUT_FILE}' générée avec succès sur ton VPS !")

if __name__ == "__main__":
    filter_playlist()
