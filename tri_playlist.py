import requests
import re
import os

# Configuration
SOURCE_URL = "https://iptv-org.github.io/iptv/languages/fra.m3u"
OUTPUT_FILE = "temp/generated_playlist.m3u"

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
        "cordier", "fillesdacote", "cinenanar", "cinewestern", "wildsidetv", "dossiersfbi", 
        "novo19", "bbcdrama", "degrassi", "heleneetlesgarcons", "lemiracledelamour", 
        "lesanneesfac", "lesnouveauxdetectives", "louislabrocante", "screamin", "theasylum", 
        "walkertexasranger", "yaquelaveritequicompte", "instantsaga", "seriemax", "emotionl", "ab3",
        "intocrime"
    ],
    "🧸 JEUNESSE": [
        "canalj", "disney", "mangas", "piwi", "nickelodeon", "tiji", "teletoon", 
        "boomerang", "cartoon", "tivi5", "adn", "ludikids", "caillou", "bobleponge", 
        "amuse", "bubbleguppies", "mbc3", "angelaanaconda", "avatar", "babyfirst", 
        "doratv", "inazumaeleven", "sabrina", "tortuesninja", "victorious", "amouyazid"
    ],
    "🌍 DÉCOUVERTE & SAVOIR": [
        "animaux", "histoire", "museum", "natgeo", "planete", "sciencevie", "toutehistoire", 
        "ushuaia", "montagne", "discovery", "investigation", "chasse", "trek", "seasons", 
        "ultranature", "maison", "sorcier", "marmiton", "myzentv", "geopolistv", "sosdocteur", 
        "bebtv", "3abn", "amanitv", "ecclesiatv", "ewtn", "haditv", "iqraa", "manaeglise", 
        "metanoiatv", "sophiatv", "telepace", "chandel", "divinamour", "dynamicgospel", 
        "emcitv", "faith", "hope", "kto", "revelation", "shilo", "wisdom", "religion",
        "mygospeltv", "esaie45tele", "radiotele4veh", "radioteleamen", "radiotelefullgospel", 
        "radioteleevangile", "televisionespoir47", "naturaltv", "mdl"
    ],
    "📰 INFOS & ÉCONOMIE": [
        "bfmbusiness", "euronews", "france24", "i24", "figaro", "meteo", "bsmart", 
        "tvfinance", "africanews", "cgtnfrench", "presstvfrench", "nwinfo", "nweconomie", 
        "bfm2", "bfmtechco", "tr24television", "rtfrance", "business24", "burkinainfo", "franceinfo",
        "lemediatv", "publicsenat2424", "tv5mondeinfo", "francophonie24"
    ],
    "🎶 MUSIQUE & DIVERTISSEMENT": [
        "mcm", "mezzo", "mtv", "trace", "bblack", "melody", "rfm", "nrjhits", 
        "cstarhits", "m6music", "mouv", "qwest", "fashion", "clique", "gong", "d5music", 
        "a2imusic", "clubbingtv", "stingray", "radiokaraoke", "funradio", "generations", "tl7",
        "a2inaija", "a2itv", "mensuptv", "rtl2", "sudradio", "franceinter", "radiofrontieres", 
        "arabel", "handicaptv", "mdl.fr", "rmclife"
    ],
    "📍 RÉGIONALES & LOCALES": [
        "20minutestv", "t18", "canalalpha", "7alimoges", "8montblanc", "alsace20", "astv", "biptv", "telenantes", 
        "tv7", "vosges", "kto", "canal32", "weo", "tebeo", "tebesud", "grandgeneve", "tvr", 
        "matele", "tl7", "canalzoom", "cannes", "nancy", "tv78", "iltv", "telegohelle", 
        "tv3v", "rhonetv", "telebielingue", "nrtv", "bluezoomf", "qu4treliegemedia", 
        "telemb", "tvlux", "angers", "alpedhuez", "brionnais", "monacoinfo", "tvmonaco", 
        "vedia", "viaoccitanie", "viatelepaese", "bfmalsace", "bfmcotedazur", "bfmdici", 
        "bfmgrandlille", "bfmgrandlittoral", "bfmlyon", "bfmmarseille", "bfmnormandie", 
        "bfmvar", "chamber", "latere", "maxtv", "carac", "tma", "rht", "basseterre"
    ],
    "⚽ SPORTS": [
        "sport", "bein", "eurosport", "equidia", "automoto", "rmcsport", "golf", 
        "multisports", "footplus", "fighting", "nhlcentreice", "journaldugolf", "nautical", "failarmy"
    ],
    "🇧🇪 BELGIQUE": [
        "laune", "ladeux", "latrois", "rtltvi", "clubrtl", "plugrtl", "ln24", "tipik", 
        "bx1", "bouke", "bruzz", "belrtl", "rtlzwee", "ab3", "canalz", "radiocontact", "actv"
    ],
    "🇨🇭 SUISSE": [
        "rtsun", "rtsdeux", "srfinfo", "tvm3", "lemanbleu", "couleur3", "rts1", "rts2", 
        "canal9", "carac", "la-tele", "maxtv", "nrj-leman", "kanal9", "latele"
    ],
    "🇨🇦 CANADA / QUÉBEC": [
        "radiocanada", "icitelea", "icirdi", "tva", "noovo", "lcn", "telequebec", "tcftv", 
        "cbaf", "cbft", "cbkf", "cblf", "cboft", "cbuft", "cbvt", "cbwft", "cftmdt", "cftudt", 
        "civmdt", "cjbrdt", "ckshdt", "cktmdt", "cktvdt", "ctbtv", "assemblee", "legislative",
        "canaldelassemblee", "montrealgreektv", "tvctk"
    ],
    "🌍 AFRIQUE & DOM-TOM": [
        "atv", "canal3", "cna", "kc2", "ntv", "rtvc", "tvlacapitale", "mta9africa",
        "aplus", "africa24", "africanews", "nollywood", "rtb", "rti", "ortm", "2mmonde", 
        "antennereunion", "2stv", "tfm", "sentv", "nci", "lifetv", "canal2", "benietv", 
        "beninwebtv", "bossbrotherstv", "cbctv", "ccpvtelevision", "centelevision", "crtv", 
        "d3tv", "dntv", "edentv", "equinoxtv", "evitv", "exploitstv", "foryoutv", "jostvhd", 
        "kin24", "lbfdrtv", "mbc1", "mbc5", "metropole", "misectv", "mouridetv", "onetv", 
        "plextv", "publicsntv", "reflettv", "rewmitv", "rtd4", "rtg1", "rtg2", "rtnc", 
        "rtnc3", "rtvs1", "senewebtv", "senjeunestv", "telecongo", "telesud", "tm1tv", 
        "tnh", "tv2", "tvcbenin", "tvt", "vision4", "yegletv", "etv", "fusiontv", "tntv", 
        "telepeyi", "a12tv", "actv.tg", "adotv", "afrique54", "afromagic", "afroturk", 
        "antennea", "cam10", "canaf54", "chabibatv", 
        "championtv", "cheriflatv", "compassiontv", "congoplanet", "degatv", 
        "diaspora24", "digitalcongo", "douniatv", "fasso", "haitinews", "hmipromz", 
        "identite", "ivoirechannel", "kaback", "kajou", "kalac", "lauradave", "lougatv", 
        "madertv", "medi1tv", "mikuba", "mytv", "nazalis", "nessma", "nietatv", "novelachannel", 
        "numerica", "nwmagazine", "onenation", "playtv", "pstvhd", "pvs", "rtjva", 
        "rwanda", "saraounia", "smatogo", "storychannel", "sunulabel", "taltv", "teleboston", 
        "telehaiti", "labrise", "telelouange", "telemaroc", "telemasters", "telemusik", 
        "telepacific", "telepam", "telesahel", "teletchad", "televariete", "telezoukla", 
        "tempoafric", "viaatv", "voxafrica", "walftv", "yakaartv", "zeeone", "zee-one",
        "mta1world", "mta2europe", "mta4africa", "mta8africa", "otv",
        "turkmenistan", "tv5mondeasia", "tv5mondeeurope", "tv5mondefrance", "tv5mondelatin", 
        "tv5mondepacific", "tv5mondestyle", "tvcarib", "tvfamille", "radiotele", "telemix", "rthtv1", "mta5africa"
    ],
    "📺 PLUTO TV": [],
    "📺 SAMSUNG TV PLUS": [],
    "📺 RAKUTEN TV": [],
    "📦 AUTRES": []
}

def normalize(text):
    if not text: return ""
    return re.sub(r'[^a-z0-9]', '', text.lower())

def filter_playlist():
    # S'assurer que le dossier temp existe
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    print(f"Téléchargement de la playlist depuis {SOURCE_URL}...")
    try:
        r = requests.get(SOURCE_URL, timeout=30)
        r.raise_for_status()
        content = r.text
    except Exception as e:
        print(f"Erreur lors du téléchargement : {e}")
        return

    entries = re.findall(r'(#EXTINF:.*?\n(?:#EXTVLCOPT:.*?\n)*http.*)', content, re.MULTILINE)
    output_groups = {cat: [] for cat in CATEGORIES.keys()}
    count = 0

    for entry in entries:
        lines = entry.splitlines()
        info_line = lines[0]
        name_match = re.search(r',([^,]+)$', info_line)
        if not name_match: continue
        raw_name = name_match.group(1).strip()
        norm_name = normalize(raw_name)

        matched_at_least_once = False

        # 1. Services Automatiques
        auto_cat = None
        if "pluto" in norm_name: auto_cat = "📺 PLUTO TV"
        elif "samsung tv plus" in norm_name: auto_cat = "📺 SAMSUNG TV PLUS"
        elif "rakuten tv" in norm_name: auto_cat = "📺 RAKUTEN TV"
        elif "canal+" in norm_name and not any(k in norm_name for k in ["sport", "cinema", "cine"]):
            auto_cat = "💎 CANAL+"

        if auto_cat:
            new_info = re.sub(r'group-title="[^"]+"', f'group-title="{auto_cat}"', info_line) if 'group-title="' in info_line else info_line.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="{auto_cat}"')
            output_groups[auto_cat].append(f"{new_info}\n" + "\n".join(lines[1:]))
            count += 1
            continue

        # 2. Catégories Manuelles
        for cat_name, channels in CATEGORIES.items():
            if not channels: continue
            for display_name, keywords in channels:
                if any(normalize(k) in norm_name for k in keywords):
                    new_info = re.sub(r',.*$', f',{display_name}', info_line)
                    if 'group-title="' in new_info:
                        new_info = re.sub(r'group-title="[^"]+"', f'group-title="{cat_name}"', new_info)
                    else:
                        new_info = new_info.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="{cat_name}"')
                    
                    output_groups[cat_name].append(f"{new_info}\n" + "\n".join(lines[1:]))
                    matched_at_least_once = True
                    count += 1
                    break
        
        # 3. Repli
        if not matched_at_least_once:
            new_info = re.sub(r'group-title="[^"]+"', f'group-title="📦 AUTRES"', info_line) if 'group-title="' in info_line else info_line.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="📦 AUTRES"')
            output_groups["📦 AUTRES"].append(f"{new_info}\n" + "\n".join(lines[1:]))
            count += 1

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for cat in CATEGORIES.keys():
            if output_groups[cat]:
                for item in output_groups[cat]:
                    f.write(item + "\n")
    
    print(f"Succès ! {count} chaînes triées dans {OUTPUT_FILE}")

if __name__ == "__main__":
    filter_playlist()
