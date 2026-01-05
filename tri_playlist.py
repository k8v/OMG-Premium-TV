import requests
import re
import os

# Configuration
SOURCE_URL = "https://iptv-org.github.io/iptv/languages/fra.m3u"
OUTPUT_FILE = "generated.m3u"

# --- CONFIGURATION DES CATÉGORIES ---
# Les mots-clés servent uniquement à classer la chaîne dans le bon dossier
CATEGORIES = {
    "🇫🇷 TNT": ["tf1", "france2", "france3", "france4", "france5", "m6", "arte", "c8", "w9", "tmc", "tfx", "nrj12", "lcp", "bfmtv", "cnews", "cstar", "gulli", "tf1series", "lequipe", "6ter", "rmcstory", "rmcdecouverte", "cherie25", "lci", "franceinfo"],
    "🎬 CINÉMA & SÉRIES": ["canalplus", "cineplus", "ocs", "action", "ab1", "rtl9", "teva", "paramount", "warner", "novelas", "crimedistrict", "serieclub", "syfy", "tvbreizh", "polar", "comedycentral", "comedie", "studiocanal", "tcm", "persiana", "sony", "justepourrire", "cordier", "fillesdacote", "cinenanar", "cinewestern"],
    "🧸 JEUNESSE": ["canalj", "disney", "mangas", "piwi", "nickelodeon", "tiji", "teletoon", "boomerang", "cartoon", "tivi5", "adn", "ludikids", "caillou", "bobleponge", "amuse"],
    "🌍 DÉCOUVERTE & SAVOIR": ["animaux", "histoire", "museum", "natgeo", "planete", "sciencevie", "toutehistoire", "ushuaia", "montagne", "discovery", "investigation", "chasse", "trek", "seasons", "ultranature", "maison", "sorcier", "marmiton"],
    "📰 INFOS & ÉCONOMIE": ["bfmbusiness", "euronews", "france24", "i24", "figaro", "meteo", "bsmart", "tvfinance", "africanews"],
    "🎶 MUSIQUE & DIVERTISSEMENT": ["mcm", "mezzo", "mtv", "trace", "bblack", "melody", "rfm", "nrjhits", "cstarhits", "m6music", "mouv", "qwest", "fashion", "clique"],
    "📍 RÉGIONALES & LOCALES": ["canalalpha", "7alimoges", "8montblanc", "alsace20", "astv", "biptv", "telenantes", "tv7", "vosges", "kto", "canal32", "weo", "tebeo", "tebesud", "grandgeneve", "tvr", "matele", "tl7", "canalzoom", "cannes", "nancy"],
    "⚽ SPORTS": ["sport", "bein", "eurosport", "equidia", "automoto", "rmcsport", "golf", "multisports", "footplus", "fighting"],
    "🇧🇪 BELGIQUE": ["laune", "ladeux", "latrois", "rtltvi", "clubrtl", "plugrtl", "ln24", "tipik", "bx1", "bouke", "bruzz"],
    "🇨🇭 SUISSE": ["rtsun", "rtsdeux", "srfinfo", "tvm3", "lemanbleu"],
    "🇨🇦 CANADA / QUÉBEC": ["radiocanada", "icitelea", "icirdi", "tva", "noovo", "lcn", "telequebec"],
    "🌍 AFRIQUE & DOM-TOM": ["aplus", "africa24", "africanews", "nollywood", "rtb", "rti", "ortm", "2mmonde", "antennereunion", "2stv", "tfm", "sentv", "nci", "lifetv", "canal2"],
    "📺 PLUTO TV": [],
    "📺 SAMSUNG TV PLUS": [],
    "📺 RAKUTEN TV": [],
    "📦 AUTRES": []
}

def clean_tvg_id(info_line):
    """Extrait le tvg-id et ne garde que le texte avant le premier point."""
    match = re.search(r'tvg-id="([^".]+)', info_line, re.IGNORECASE)
    if match:
        return match.group(1)
    return ""

def filter_playlist():
    print("Démarrage du filtrage et du tri par TVG-ID...")
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
        
        # Extraction du TVG-ID nettoyé (ex: RMCStory)
        sort_id = clean_tvg_id(info_line)
        norm_sort_id = sort_id.lower()

        # 1. Services Auto (Pluto, Samsung, etc.)
        auto_cat = None
        if "pluto" in norm_sort_id: auto_cat = "📺 PLUTO TV"
        elif "samsung" in norm_sort_id: auto_cat = "📺 SAMSUNG TV PLUS"
        elif "rakuten" in norm_sort_id: auto_cat = "📺 RAKUTEN TV"

        if auto_cat:
            new_info = re.sub(r'group-title="[^"]+"', f'group-title="{auto_cat}"', info_line) if 'group-title="' in info_line else info_line.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="{auto_cat}"')
            output_groups[auto_cat].append({'sort_key': sort_id, 'data': f"{new_info}\n" + "\n".join(lines[1:])})
            continue

        # 2. Classement par catégories
        matched = False
        for cat_name, keywords in CATEGORIES.items():
            # On vérifie si le sort_id contient l'un des mots-clés
            if any(k in norm_sort_id for k in keywords):
                if 'group-title="' in info_line:
                    new_info = re.sub(r'group-title="[^"]+"', f'group-title="{cat_name}"', info_line)
                else:
                    new_info = info_line.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="{cat_name}"')
                
                output_groups[cat_name].append({'sort_key': sort_id, 'data': f"{new_info}\n" + "\n".join(lines[1:])})
                matched = True
                break
        
        # 3. Repli
        if not matched:
            new_info = re.sub(r'group-title="[^"]+"', f'group-title="📦 AUTRES"', info_line) if 'group-title="' in info_line else info_line.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="📦 AUTRES"')
            output_groups["📦 AUTRES"].append({'sort_key': sort_id, 'data': f"{new_info}\n" + "\n".join(lines[1:])})

    # Écriture finale
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for cat in CATEGORIES.keys():
            # Tri alphabétique basé sur le TVG-ID nettoyé
            sorted_channels = sorted(output_groups[cat], key=lambda x: x['sort_key'].lower())
            for item in sorted_channels:
                f.write(item['data'] + "\n")
    
    print(f"Terminé ! Fichier '{OUTPUT_FILE}' généré.")

if __name__ == "__main__":
    filter_playlist()
