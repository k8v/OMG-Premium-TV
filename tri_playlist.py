import requests
import re

# Configuration
SOURCE_URL = "https://iptv-org.github.io/iptv/languages/fra.m3u"
OUTPUT_FILE = "generated.m3u"

# --- CONFIGURATION DES CATÉGORIES (Basée sur les racines des tvg-id) ---
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
        "intocrime", "rmclife", "t18", "ab3", "cinenanar", "cinewestern", "dossiersfbi", 
        "emotionl", "heleneetlesgarcons", "instantsaga", "lemiracledelamour", "lesanneesfac", 
        "lescordier", "lesfillesdacote", "lesnouveauxdetectives", "louislabrocante", 
        "novela", "novo19", "screamin", "seriemax", "theasylum", "walkertexasranger", 
        "yaquelaveritequicompte", "bbcdrama", "degrassi", "wildsidetv"
    ],
    "🧸 JEUNESSE": [
        "canalj", "disney", "mangas", "piwi", "nickelodeon", "tiji", "teletoon", 
        "boomerang", "cartoon", "tivi5", "adn", "ludikids", "caillou", "bobleponge",
        "amouyazid", "angelaanaconda", "avatar", "babyfirst", "bubbleguppies", "doratv", 
        "inazumaeleven", "mbc3", "sabrinalaserie", "tortuesninja", "victorious"
    ],
    "🌍 DÉCOUVERTE & SAVOIR": [
        "animaux", "histoire", "museum", "natgeo", "planete", "sciencevie", "toutehistoire", 
        "ushuaia", "montagne", "discovery", "investigation", "chasse", "trek", "seasons", 
        "ultranature", "maison", "sorcier", "marmiton", "myzentv", "handicaptv", "mensuptv", 
        "mdl", "naturaltv", "3abn", "a2ireligion", "benietv", "chandel", "compassiontv", 
        "divinamour", "ecclesiatv", "emcitv", "ewtn", "fideletv", "haditv", "iqraa", 
        "manaeglise", "metanoiatv", "miracletv", "mygospeltv", "revelation", "shilo", 
        "sophiatv", "sosdocteur", "telepace", "televisionespoir", "bebtv"
    ],
    "📰 INFOS & ÉCONOMIE": [
        "bfmbusiness", "euronews", "france24", "i24", "figaro", "meteo", "bsmart", 
        "tvfinance", "africanews", "cgtnfrench", "presstvfrench", "nwinfo", "nweconomie", 
        "rtfrance", "lemediatv", "publicsenat", "francophonie24", "cna.dz", "afrique54", 
        "business24", "burkinainfo", "nwmagazine", "tr24"
    ],
    "🎶 MUSIQUE & DIVERTISSEMENT": [
        "mcm", "mezzo", "mtv", "trace", "bblack", "melody", "rfm", "nrjhits", 
        "cstarhits", "m6music", "mouv", "qwest", "fashion", "clique", "a2imusic", 
        "clubbingtv", "stingray", "radio", "franceinter", "sudradio", "funradio", "generations", "gong"
    ],
    "📍 RÉGIONALES & LOCALES": [
        "canalalpha", "7alimoges", "8montblanc", "alsace20", "astv", "biptv", "telenantes", 
        "tv7", "vosges", "kto", "canal32", "weo", "tebeo", "tebesud", "grandgeneve", "tvr", 
        "matele", "tl7", "canalzoom", "cannes", "nancy", "tv78", "arabel", "kanal9", "latele",
        "alpedhuez", "angerstele", "bfmalsace", "bfmcotedazur", "bfmdici", "bfmgrandlille", 
        "bfmgrandlittoral", "bfmlyon", "bfmmarseille", "bfmnormandie", "bfmvar", "brionnais", 
        "iltv", "lyoncapitale", "monacoinfo", "moselletv", "nrtv", "puissancetv", "qu4tre", 
        "rhonetv", "telebielingue", "telegohelle", "telemb", "tv3v", "tvlux", "tvmonaco", 
        "tvtarn", "vedia", "viaoccitanie", "viatelepaese", "chamber", "maxtv", "bluezoom", "tma", "etv", "rht", "radiotvbasse"
    ],
    "⚽ SPORTS": [
        "sport", "bein", "eurosport", "equidia", "automoto", "rmcsport", "golf", "nhl", "nautical", "failarmy"
    ],
    "🇧🇪 BELGIQUE": [
        "laune", "ladeux", "latrois", "rtltvi", "clubrtl", "plugrtl", "ln24", "tipik", 
        "bx1", "bouke", "bruzz", "belrtl", "rtlzwee", "ab3", "canalz", "qu4tre", "vedia", "tvlux", "telemb", "actv.be"
    ],
    "🇨🇭 SUISSE": [
        "rtsun", "rtsdeux", "srfinfo", "tvm3", "lemanbleu", "couleur3", "rts1", "rts2", 
        "canal9", "carac", "latele", "maxtv", "nrtv", "rhonetv", "telebielingue", "bluezoom"
    ],
    "🇨🇦 CANADA / QUÉBEC": [
        "radiocanada", "icirdi", "tva", "noovo", "lcn", "telequebec", "cbaf", "cbft", 
        "cbkf", "cblf", "cboft", "cbuft", "cbvt", "cbwft", "cftmdt", "cftudt", "civmdt", 
        "cjbrdt", "ckshdt", "cktmdt", "cktvdt", "ctbtv", "tcftv", "canaldelassemblee", 
        "legislative", "montrealgreek", "tvctk", "radioteleevangile"
    ],
    "🌍 AFRIQUE & DOM-TOM": [
        "2stv", "a12tv", "a2itv", "a2inaija", "actv.tg", "adotv", "africable", "afroculture", 
        "afromagic", "afroturk", "amanitv", "antennea", "atv.gn", "beninweb", "bossbrothers", 
        "burkinainfo", "cam10", "canaf54", "canal2", "canal3.bf", "cbctv", "ccpv", "centelevision", 
        "chabiba", "championtv", "cherifla", "cna.dz", "congoplanet", "crtv", "d3tv", "degatv", 
        "diaspora24", "digitalcongo", "dntv", "dounia", "dynamicgospel", "edentv", "equinoxe", 
        "espacetv", "evitv", "exploitstv", "fassotv", "foryou", "fusiontv", "geopolis", "guidelove", 
        "haitinews", "hmipromz", "identite", "ivoirechannel", "jostvhd", "kaback", "kajou", 
        "kalac", "kc2", "kin24", "lauradave", "lbfdr", "lifetv", "lougatv", "madertv", "mbc1", 
        "mbc5", "medi1tv", "metropole", "mikuba", "mishapi", "mouridetv", "mta", "mytv", "nazalis", 
        "nci", "nessma", "nietatv", "ntv.ci", "numerica", "onenation", "onetv", "otv.lb", 
        "playtv", "plextv", "pstvhd", "publicsn", "pvstv", "radiotele", "reflet", "rewmi", 
        "rtd4", "rtg1", "rtg2", "rtjva", "rtnc", "rtvs1", "rwanda", "saraounia", "savane", 
        "seneweb", "senjeunes", "sentv", "smatogo", "storychannel", "sunulabel", "taltv", 
        "teleboston", "telecongo", "telehaiti", "labrise", "telelouange", "telemaroc", 
        "telemasters", "telemusik", "telepacific", "telepam", "telepeyi", "telesahel", 
        "telesud", "teletchad", "televariete", "telezoukla", "tempoafric", "tfm", "tm1tv", 
        "tnh", "tntv", "tr24", "tv2", "tvcbenin", "tvfamille", "tvlacapitale", "tvt", 
        "viaatv", "vision4", "voxafrica", "walftv", "yakaartv", "yegle", "zeeone"
    ],
    "📺 PLUTO TV": [],
    "📺 SAMSUNG TV PLUS": [],
    "📺 RAKUTEN TV": [],
    "📦 AUTRES": []
}

def clean_tvg_id(info_line):
    match = re.search(r'tvg-id="([^".]+)', info_line, re.IGNORECASE)
    return match.group(1) if match else ""

def filter_playlist():
    print("Démarrage du tri profond...")
    try:
        r = requests.get(SOURCE_URL, timeout=30)
        r.raise_for_status()
        content = r.text
    except Exception as e:
        print(f"Erreur réseau : {e}")
        return

    entries = re.findall(r'(#EXTINF:.*?\n(?:#EXTVLCOPT:.*?\n)*http.*)', content, re.MULTILINE)
    output_groups = {cat: [] for cat in CATEGORIES.keys()}

    for entry in entries:
        lines = entry.splitlines()
        info_line = lines[0]
        sort_id = clean_tvg_id(info_line)
        norm_id = sort_id.lower()

        # 1. Services Auto
        auto_cat = None
        if "pluto" in norm_id: auto_cat = "📺 PLUTO TV"
        elif "samsung" in norm_id: auto_cat = "📺 SAMSUNG TV PLUS"
        elif "rakuten" in norm_id: auto_cat = "📺 RAKUTEN TV"

        if auto_cat:
            new_info = re.sub(r'group-title="[^"]+"', f'group-title="{auto_cat}"', info_line) if 'group-title="' in info_line else info_line.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="{auto_cat}"')
            output_groups[auto_cat].append({'sort_key': sort_id, 'data': f"{new_info}\n" + "\n".join(lines[1:])})
            continue

        # 2. Classement par catégories
        matched = False
        for cat_name, keywords in CATEGORIES.items():
            if not keywords: continue
            # On vérifie si le norm_id COMMENCE par un mot-clé ou est égal
            if any(norm_id.startswith(k) for k in keywords):
                if 'group-title="' in info_line:
                    new_info = re.sub(r'group-title="[^"]+"', f'group-title="{cat_name}"', info_line)
                else:
                    new_info = info_line.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="{cat_name}"')
                
                output_groups[cat_name].append({'sort_key': sort_id, 'data': f"{new_info}\n" + "\n".join(lines[1:])})
                matched = True
                break
        
        if not matched:
            new_info = re.sub(r'group-title="[^"]+"', f'group-title="📦 AUTRES"', info_line) if 'group-title="' in info_line else info_line.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="📦 AUTRES"')
            output_groups["📦 AUTRES"].append({'sort_key': sort_id, 'data': f"{new_info}\n" + "\n".join(lines[1:])})

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for cat in CATEGORIES.keys():
            sorted_channels = sorted(output_groups[cat], key=lambda x: x['sort_key'].lower())
            for item in sorted_channels:
                f.write(item['data'] + "\n")
    
    print(f"Playlist générée : {len(entries)} chaînes traitées.")

if __name__ == "__main__":
    filter_playlist()
