import requests
import re
import os

# Configuration
SOURCE_URL = "https://iptv-org.github.io/iptv/languages/fra.m3u"
OUTPUT_FILE = "generated.m3u"

# --- CONFIGURATION DES CATÉGORIES ---
CATEGORIES = {
    "🇫🇷 TNT": [
        "tf1", "france2", "france3", "france4", "france5", "m6", "arte", "c8", "w9", 
        "tmc", "tfx", "nrj12", "lcp", "bfmtv", "cnews", "cstar", "gulli", "tf1series", 
        "lequipe", "6ter", "rmcstory", "rmcdecouverte", "cherie25", "lci", "franceinfo"
    ],
    "🎬 CINÉMA & SÉRIES": [
        "canalplus", "cineplus", "ocs", "action", "ab1", "rtl9", "teva", "paramount", 
        "warner", "novelas", "crimedistrict", "serieclub", "syfy", "tvbreizh", "polar", 
        "comedycentral", "comedie", "studiocanal", "tcm", "persiana", "sony", "justepourrire", 
        "intocrime", "rmclife", "t18", "ab3"
    ],
    "🧸 JEUNESSE": [
        "canalj", "disney", "mangas", "piwi", "nickelodeon", "tiji", "teletoon", 
        "boomerang", "cartoon", "tivi5", "adn", "ludikids", "caillou", "bobleponge"
    ],
    "🌍 DÉCOUVERTE & SAVOIR": [
        "animaux", "histoire", "museum", "natgeo", "planete", "sciencevie", "toutehistoire", 
        "ushuaia", "montagne", "discovery", "investigation", "chasse", "trek", "seasons", 
        "ultranature", "maison", "sorcier", "marmiton", "myzentv", "handicaptv", "mensuptv", 
        "mdl", "naturaltv", "tv5mondestyle", "televisionespoir47"
    ],
    "📰 INFOS & ÉCONOMIE": [
        "bfmbusiness", "euronews", "france24", "i24", "figaro", "meteo", "bsmart", 
        "tvfinance", "africanews", "cgtnfrench", "presstvfrench", "nwinfo", "nweconomie", 
        "rtfrance", "lemediatv", "publicsenat", "francophonie24", "cna.dz", "tv5mondeinfo"
    ],
    "🎶 MUSIQUE & DIVERTISSEMENT": [
        "mcm", "mezzo", "mtv", "trace", "bblack", "melody", "rfm", "nrjhits", 
        "cstarhits", "m6music", "mouv", "qwest", "fashion", "clique", "a2imusic", 
        "franceinter", "sudradio", "radiofrontieres", "rtl2", "funradio", "generations"
    ],
    "📍 RÉGIONALES & LOCALES": [
        "canalalpha", "7alimoges", "8montblanc", "alsace20", "astv", "biptv", "telenantes", 
        "tv7", "vosges", "kto", "canal32", "weo", "tebeo", "tebesud", "grandgeneve", "tvr", 
        "matele", "tl7", "canalzoom", "cannes", "nancy", "tv78", "arabel", "kanal9", "latele"
    ],
    "⚽ SPORTS": [
        "sport", "bein", "eurosport", "equidia", "automoto", "rmcsport", "golf", "nhl"
    ],
    "🇨🇭 SUISSE": [
        "rtsun", "rtsdeux", "srfinfo", "tvm3", "lemanbleu", "couleur3", "rts1", "rts2", "kanal9", "latele"
    ],
    "🇨🇦 CANADA / QUÉBEC": [
        "radiocanada", "tva", "noovo", "lcn", "telequebec", "canaldelassemblee", "montrealgreek", "tvctk"
    ],
    "🌍 AFRIQUE & DOM-TOM": [
        "canal2", "aplus", "africa24", "rtb", "rti", "ortm", "2mmonde", "antennereunion", 
        "a2inaija", "a2itv", "atv.gn", "canal3.bf", "esaie45", "kc2", "ntv.ci", "otv.lb", 
        "radiotele", "rlprotv", "rthtv", "rtvc", "telemix", "turkmenistan", "tv5monde", 
        "tvcarib", "tvfamille", "tvlacapitale", "mta1", "mta2", "mta8", "mta9", "mygospeltv"
    ],
    "📺 PLUTO TV": [],
    "📺 SAMSUNG TV PLUS": [],
    "📺 RAKUTEN TV": [],
    "📦 AUTRES": []
}

def clean_tvg_id(info_line):
    # Capture tout avant le premier point
    match = re.search(r'tvg-id="([^".]+)', info_line, re.IGNORECASE)
    return match.group(1) if match else ""

def filter_playlist():
    print("Analyse de la source IPTV-org...")
    try:
        r = requests.get(SOURCE_URL, timeout=30)
        r.raise_for_status()
        content = r.text
    except Exception as e:
        print(f"Erreur réseau : {e}")
        return

    # On découpe par bloc #EXTINF
    entries = re.findall(r'(#EXTINF:.*?\n(?:#EXTVLCOPT:.*?\n)*http.*)', content, re.MULTILINE)
    output_groups = {cat: [] for cat in CATEGORIES.keys()}

    for entry in entries:
        lines = entry.splitlines()
        info_line = lines[0]
        sort_id = clean_tvg_id(info_line)
        norm_sort_id = sort_id.lower()

        # 1. Services Auto
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

    # Écriture du fichier final
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for cat in CATEGORIES.keys():
            # Tri alphabétique par le tvg-id nettoyé
            sorted_channels = sorted(output_groups[cat], key=lambda x: x['sort_key'].lower())
            for item in sorted_channels:
                f.write(item['data'] + "\n")
    
    print(f"Succès ! {len(entries)} chaînes triées dans '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    filter_playlist()
