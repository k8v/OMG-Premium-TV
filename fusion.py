import requests
import re
import os

# Configuration Docker Oracle
OUTPUT_FILE = "/app/omg/playlist.m3u"

# Sources
SOURCE_TVRADIOZAP = "https://tvradiozap.eu/live/g/1/x/vlc/d/tvzeu.m3u"
SOURCE_IPTV_ORG = "https://iptv-org.github.io/iptv/countries/fr.m3u"

# --- CONFIGURATION DE L'ORDRE DES CATÉGORIES (IPTV-ORG) ---
CATEGORIES_CONFIG = {
    "TNT": [
        "tf1", "france2", "france3", "france4", "france5", "m6", "arte", "c8", "w9", 
        "tmc", "tfx", "nrj12", "lcp", "bfmtv", "cnews", "cstar", "gulli", "tf1series", 
        "lequipe", "6ter", "rmcstory", "rmcdecouverte", "cherie25", "lci", "franceinfo"
    ],
    "Archives": [
        "archives", "ina", "retro", "classic"
    ],
    "Art de vivre": [
        "maison", "marmiton", "myzentv", "artdevivre", "deco", "cuisine", "MensUPTV", "RMCLife"
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
        "yaquelaveritequicompte", "clique", "mcm", "mta", "enorme", "bet", "Gong", "Novocomedy", "MonteCarloDigitalTelevision", "motorvision"
    ],
    "Documentaires": [
        "histoire", "planete", "toutehistoire", "investigation", "trek", 
        "discovery", "rmcdecouverte", "dossiersfbi", "MDL"
    ],
    "Economie": [
        "bfmbusiness", "bsmart", "tvfinance", "nweconomie", "business24"
    ],
    "Généraliste": [
        "tv5monde", "ab3", "canale", "generaliste", "laune", "rtltvi"
    ],
    "Info": [
        "euronews", "france24", "i24", "figaro", "meteo", "africanews", 
        "cgtnfrench", "nwinfo", "rtfrance", "lci", "cnews", "bfmtv", "BFM", "FranceInter", "Francophonie24"
    ],
    "Jeunesse": [
        "canalj", "disney", "mangas", "piwi", "nickelodeon", "tiji", "teletoon", 
        "boomerang", "cartoon", "tivi5", "adn", "ludikids", "caillou", "bobleponge", 
        "amuse", "bubbleguppies", "mbc3", "angelaanaconda", "avatar", "babyfirst", 
        "doratv", "inazumaeleven", "sabrina", "tortuesninja", "victorious", "amouyazid"
    ],
    "Jeux": [
        "esport", "gaming", "gameone", "nolife"
    ],
    "Local": [
        "20minutestv", "t18", "canalalpha", "7alimoges", "8montblanc", "alsace20", "astv", "biptv", "telenantes", 
        "tv7", "vosges", "kto", "canal32", "weo", "tebeo", "tebesud", "grandgeneve", "tvr", 
        "matele", "tl7", "canalzoom", "cannes", "nancy", "tv78", "iltv", "telegohelle", 
        "tv3v", "rhonetv", "telebielingue", "nrtv", "bluezoomf", "qu4treliegemedia", 
        "telemb", "tvlux", "angers", "alpedhuez", "brionnais", "monacoinfo", "tvmonaco", 
        "vedia", "viaoccitanie", "viatelepaese", "bfmalsace", "bfmcotedazur", "bfmdici", 
        "bfmgrandlille", "bfmgrandlittoral", "bfmlyon", "bfmmarseille", "bfmnormandie", 
        "bfmvar", "chamber", "latere", "maxtv", "carac", "tma", "rht", "basseterre", "iciElsass"
    ],
    "Musique": [
        "mezzo", "mtv", "trace", "bblack", "melody", "rfm", "nrjhits", 
        "cstarhits", "m6music", "mouv", "clubbingtv", "stingray", "AraBel", "FunRadio", "GenerationsTV", "QwestTVJazzBeyond", 
        "RadioKaraoke", "SudRadio", "TZiK", "RadioFrontieres", "RTL2", "zenith"
    ],
    "Nature": [
        "animaux", "natgeo", "ultranature", "seasons", "chasse", "peche", "wild"
    ],
    "Régional": [
        "france3", "alsace20", "weo", "tebeo", "bfmalsace", "bfmlyon", "bfmmarseille", "viatelepaese", "MoselleTV"
    ],
    "Reportages": [
        "echappeesbelles", "reportages", "envoyespecial"
    ],
    "Sciences": [
        "sciencevie", "discovery", "explora", "curiosity"
    ],
    "Séries-Films": [
        "canalplus", "cineplus", "ocs", "action", "ab1", "rtl9", "teva", "paramount", 
        "warner", "novelas", "crimedistrict", "serieclub", "syfy", "tvbreizh", "polar", 
        "comedycentral", "comedie", "studiocanal", "tcm", "persiana", "sony", "justepourrire", 
        "cordier", "fillesdacote", "cinenanar", "cinewestern", "wildsidetv", "dossiersfbi", 
        "novo19", "bbcdrama", "degrassi", "heleneetlesgarcons", "lemiracledelamour", 
        "lesanneesfac", "lesnouveauxdetectives", "louislabrocante", "screamin", "theasylum", 
        "walkertexasranger", "yaquelaveritequicompte", "instantsaga", "seriemax", "emotionl", "ab3",
        "intocrime"
    ],
    "Sociétal": [
        "kto", "religion", "emcitv", "ewtn", "iqraa", "handicaptv", "publicsenat", "MyGospelTV"
    ],
    "Sport": [
        "sport", "bein", "eurosport", "equidia", "automoto", "rmcsport", "golf", 
        "multisports", "footplus", "fighting", "nhlcentreice", "journaldugolf", "nautical", "failarmy"
    ],
    "Voyage": [
        "voyage", "ushuaia", "montagne", "travelxp", "echappeesbelles", "ailleurs"
    ],
    "AFRIQUE & DOM-TOM": [
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
    "📺 SONY": [],
    "📦 AUTRES": []
}

def get_tvg_id(line):
    match = re.search(r'tvg-id="([^".]+)', line, re.IGNORECASE)
    return match.group(1).lower() if match else ""

def main():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    final_m3u_lines = ["#EXTM3U"]

    # --- PARTIE 1 : TVRADIOZAP (D'ABORD) ---
    print("Traitement TVRadioZap...")
    try:
        r1 = requests.get(SOURCE_TVRADIOZAP, timeout=30)
        r1.raise_for_status()
        lines = r1.text.splitlines()
        current_inf = None
        for line in lines:
            if line.startswith("#EXTINF:"):
                info_lower = line.lower()
                new_group = None
                if "pluto" in info_lower: new_group = "📺 PLUTO TV"
                elif "samsung" in info_lower: new_group = "📺 SAMSUNG TV PLUS"
                elif "rakuten" in info_lower: new_group = "📺 RAKUTEN TV"
                elif "sony" in info_lower: new_group = "📺 SONY"

                if new_group:
                    if 'group-title="' in line:
                        start = line.find('group-title="') + 13
                        end = line.find('"', start)
                        line = line[:start] + new_group + line[end:]
                    else:
                        line = line.replace('#EXTINF:', f'#EXTINF:-1 group-title="{new_group}" ')
                current_inf = line
            elif line.startswith("http") and current_inf:
                final_m3u_lines.append(current_inf)
                final_m3u_lines.append(line)
                current_inf = None
    except Exception as e: print(f"Erreur Source 1: {e}")

    # --- PARTIE 2 : IPTV-ORG (CLASSÉ PAR TON ORDRE) ---
    print("Traitement IPTV-org...")
    iptv_storage = {cat: [] for cat in CATEGORIES_CONFIG.keys()}

    try:
        r2 = requests.get(SOURCE_IPTV_ORG, timeout=30)
        r2.raise_for_status()
        entries = re.findall(r'(#EXTINF:.*?\n(?:#EXTVLCOPT:.*?\n)*http.*)', r2.text, re.MULTILINE)
        
        for entry in entries:
            lines = entry.splitlines()
            info_line = lines[0]
            norm_id = get_tvg_id(info_line)
            
            matched = False
            for cat_name, keywords in CATEGORIES_CONFIG.items():
                if keywords and any(k.lower() in norm_id for k in keywords):
                    new_info = re.sub(r'group-title="[^"]+"', f'group-title="{cat_name}"', info_line) if 'group-title="' in info_line else info_line.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="{cat_name}"')
                    iptv_storage[cat_name].append(f"{new_info}\n" + "\n".join(lines[1:]))
                    matched = True
                    break
            
            if not matched:
                new_info = re.sub(r'group-title="[^"]+"', f'group-title="📦 AUTRES"', info_line) if 'group-title="' in info_line else info_line.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="📦 AUTRES"')
                iptv_storage["📦 AUTRES"].append(f"{new_info}\n" + "\n".join(lines[1:]))

        # On ajoute les chaines IPTV-org en respectant l'ordre des clés de CATEGORIES_CONFIG
        for cat in CATEGORIES_CONFIG.keys():
            for item_data in iptv_storage[cat]:
                final_m3u_lines.append(item_data)

    except Exception as e: print(f"Erreur Source 2: {e}")

    # --- ECRITURE FINALE ---
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(final_m3u_lines))
    
    print(f"Terminé ! Playlist sauvegardée dans {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
