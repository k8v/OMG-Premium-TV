import requests
import re
import os

# Configuration
SOURCE_URL = "https://iptv-org.github.io/iptv/languages/fra.m3u"
OUTPUT_FILE = "generated.m3u"

# --- CONFIGURATION DES CATÉGORIES ---
CATEGORIES = {
    "🇫🇷 TNT": [
        ["TF1", ["TF1"]], ["France 2", ["France 2"]], ["France 3", ["France 3"]], 
        ["France 4", ["France 4"]], ["France 5", ["France 5"]], 
        ["M6", ["M6"]], ["Arte", ["Arte", "arte"]], ["C8", ["C8", "D8"]], 
        ["W9", ["W9"]], ["TMC", ["TMC"]], ["TFX", ["TFX"]], ["NRJ 12", ["NRJ 12"]], 
        ["LCP", ["LCP", "Public Senat", "Assemblée Nationale"]], ["BFM TV", ["BFM TV", "BFMTV"]], 
        ["CNews", ["CNews"]], ["CSTAR", ["CSTAR"]], ["Gulli", ["Gulli"]], 
        ["TF1 Séries Films", ["TF1 Series", "TF1 Séries"]], ["L'Equipe", ["L'Equipe", "L'Équipe"]], 
        ["6ter", ["6ter"]], ["RMC Story", ["RMC Story"]], ["RMC Découverte", ["RMC Découverte"]], 
        ["Chérie 25", ["Chérie 25"]], ["LCI", ["LCI"]], ["Franceinfo", ["Franceinfo"]]
    ],
    "🎬 CINÉMA & SÉRIES": [
        ["Canal+", ["Canal+", "Canal +"]], ["Ciné+", ["Ciné+", "Cine+"]], ["OCS", ["OCS"]],
        ["Action", ["Action"]], ["AB1", ["AB1"]], ["RTL9", ["RTL9"]], ["Téva", ["Téva"]], 
        ["Paramount Channel", ["Paramount Channel"]], ["Warner TV", ["Warner TV"]], 
        ["Novelas TV", ["Novelas TV", "Afro Novelas", "Fréquence Novelas"]], ["Crime District", ["Crime District"]],
        ["Zylo Cinéma", ["Zylo", "Ciné Nanar", "Ciné Western"]], ["Série Club", ["Série Club"]],
        ["Syfy", ["Syfy"]], ["TV Breizh", ["TV Breizh"]], ["Polar+", ["Polar+"]],
        ["Comedy Central", ["Comedy Central"]], ["Comedie+", ["Comedie+"]], ["Studiocanal", ["Studiocanal"]],
        ["TCM Cinéma", ["TCM Cinéma"]], ["Persiana", ["Persiana"]], ["Sony One", ["Sony One"]],
        ["Juste pour Rire", ["Juste pour Rire"]], ["Les Cordier", ["Les Cordier"]], ["Les filles d'à côté", ["Les filles d'à côté"]]
    ],
    "🧸 JEUNESSE": [
        ["Canal J", ["Canal J"]], ["Disney Channel", ["Disney Channel"]], ["Mangas", ["Mangas"]], 
        ["Piwi+", ["Piwi+"]], ["Nickelodeon", ["Nickelodeon"]], ["TiJi", ["TiJi"]],
        ["Teletoon+", ["Teletoon+"]], ["Boomerang", ["Boomerang"]], ["Cartoon Network", ["Cartoon Network"]],
        ["TiVi5 Monde", ["TiVi5 Monde"]], ["Gulli", ["Gulli"]], ["ADN TV+", ["ADN TV+"]],
        ["Disney Junior", ["Disney Junior"]], ["Nickelodeon Junior", ["Nickelodeon Junior"]],
        ["Nickelodeon Teen", ["Nickelodeon Teen"]], ["Ludikids", ["Ludikids"]], ["Caillou", ["Caillou"]],
        ["Bob l'éponge", ["Bob l'éponge"]], ["Amuse Animation", ["Amuse Animation"]]
    ],
    "🌍 DÉCOUVERTE & SAVOIR": [
        ["Animaux", ["Animaux"]], ["Histoire TV", ["Histoire TV"]], ["Museum TV", ["Museum TV"]], 
        ["National Geographic", ["National Geographic"]], ["Planète+", ["Planète+"]], 
        ["Science & Vie TV", ["Science & Vie TV"]], ["Toute l'Histoire", ["Toute l'Histoire"]], 
        ["Ushuaïa TV", ["Ushuaïa TV"]], ["Montagne TV", ["Montagne TV", "Alpe d'Huez TV"]],
        ["Discovery Channel", ["Discovery Channel"]], ["Investigation Discovery", ["Investigation Discovery"]],
        ["Chasse & Pêche", ["Chasse & Pêche"]], ["Trek", ["Trek"]], ["Seasons", ["Seasons"]],
        ["Ultra Nature", ["Ultra Nature"]], ["Maison & Travaux TV", ["Maison & Travaux TV"]],
        ["L'Esprit Sorcier TV", ["L'Esprit Sorcier TV"]], ["Marmiton TV", ["Marmiton TV"]]
    ],
    "📰 INFOS & ÉCONOMIE": [
        ["BFM Business", ["BFM Business"]], ["Euronews", ["Euronews"]], ["France 24", ["France 24"]], 
        ["i24 News", ["i24 News"]], ["Le Figaro TV", ["Le Figaro TV", "Le Figaro Live"]], 
        ["La Chaîne Météo", ["Météo"]], ["B Smart TV", ["B Smart TV"]], ["TV Finance", ["TV Finance"]],
        ["LCI", ["LCI"]], ["CNews", ["CNews"]], ["Franceinfo", ["Franceinfo"]], ["Africanews", ["Africanews"]]
    ],
    "🎶 MUSIQUE & DIVERTISSEMENT": [
        ["MCM", ["MCM"]], ["Mezzo", ["Mezzo"]], ["MTV", ["MTV"]], ["Trace", ["Trace"]], 
        ["Bblack!", ["Bblack"]], ["Melody", ["Melody"]], ["RFM TV", ["RFM TV"]], ["NRJ Hits", ["NRJ Hits"]],
        ["C Star Hits", ["C Star Hits"]], ["M6 Music", ["M6 Music"]], ["Mouv' TV", ["Mouv' TV"]],
        ["Qwest TV", ["Qwest TV"]], ["Fashion TV", ["Fashion TV", "FashionTV"]], ["Clique TV", ["Clique TV"]]
    ],
    "📍 RÉGIONALES & LOCALES": [
        ["Canal Alpha", ["Canal Alpha"]], ["7ALimoges", ["7ALimoges"]], ["8 Mont-Blanc", ["8 Mont-Blanc"]], 
        ["Alsace 20", ["Alsace 20"]], ["ASTV", ["ASTV"]], ["BFM", ["BFM Alsace", "BFM Lyon", "BFM Marseille", "BFM Paris", "BFM Normandie", "BFM Var"]], 
        ["BIP TV", ["BIP TV"]], ["Télénantes", ["Télénantes"]], ["TV7 Bordeaux", ["TV7 Bordeaux"]], 
        ["Vosges TV", ["Vosges TV"]], ["KTO", ["KTO"]], ["Canal 32", ["Canal 32"]], ["Wéo", ["Wéo"]],
        ["Tébéo", ["Tébéo"]], ["TébéSud", ["TébéSud"]], ["Grand Genève TV", ["Grand Genève TV"]],
        ["TVR", ["TVR"]], ["Matélé", ["Matélé"]], ["TL7", ["TL7"]]
    ],
    "⚽ SPORTS": [
        ["Canal+ Sport", ["Canal+ Sport", "Canal+ Foot", "Canal+ Sport 360", "Canal+ MotoGP", "Canal+ Formula 1", "Infosport+"]], 
        ["BeIN Sports", ["BeIN Sports", "beIN"]], ["Eurosport", ["Eurosport"]], 
        ["Equidia", ["Equidia"]], ["Automoto", ["Automoto"]], ["RMC Sport", ["RMC Sport"]], 
        ["Golf +", ["Golf +", "Golf Channel", "Journal Du Golf"]], ["MultiSports", ["MultiSports", "Foot+"]], 
        ["Sport en France", ["Sport en France"]], ["MGG TV", ["MGG TV"]], ["Motorsport.tv", ["Motorsport.tv"]],
        ["Africa 24 Sport", ["Africa 24 Sport"]], ["Fighting Spirit", ["Fighting Spirit"]]
    ],
    "🇧🇪 BELGIQUE": [
        ["La Une", ["La Une"]], ["La Deux", ["La Deux"]], ["La Trois", ["La Trois"]], 
        ["RTL-TVI", ["RTL-TVI", "RTL TVI"]], ["Club RTL", ["Club RTL"]], ["Plug RTL", ["Plug RTL"]],
        ["LN24", ["LN24"]], ["Tipik", ["Tipik"]], ["BX1", ["BX1"]], ["Bouke", ["Bouke"]], ["Bruzz", ["Bruzz"]]
    ],
    "🇨🇭 SUISSE": [
        ["RTS Un", ["RTS Un"]], ["RTS Deux", ["RTS Deux"]], ["SRF info", ["SRF info"]],
        ["TVM3", ["TVM3"]], ["Léman Bleu", ["Léman Bleu"]], ["Canal Alpha", ["Canal Alpha"]]
    ],
    "🇨🇦 CANADA / QUÉBEC": [
        ["ICI Radio-Canada", ["Radio-Canada", "ICI Tele", "ICI RDI"]], ["TVA", ["TVA"]], 
        ["Noovo", ["Noovo"]], ["LCN", ["LCN"]], ["Télé-Québec", ["Télé-Québec"]]
    ],
    "🌍 AFRIQUE & DOM-TOM": [
        ["A+", ["A+", "A Plus"]], ["Africa 24", ["Africa 24"]], ["Africanews", ["Africanews"]], 
        ["Nollywood TV", ["Nollywood TV"]], ["TV5Monde Afrique", ["TV5Monde Afrique"]], 
        ["RTB", ["RTB"]], ["RTI", ["RTI"]], ["ORTM", ["ORTM"]], ["2M Monde", ["2M Monde"]],
        ["Antenne Réunion", ["Antenne Réunion"]], ["France Ô", ["France Ô"]], ["2STV", ["2STV"]],
        ["TFM", ["TFM"]], ["Sen TV", ["Sen TV"]], ["NCI", ["NCI"]], ["Life TV", ["Life TV"]]
    ],
    "📺 PLUTO TV": [],
    "📺 SAMSUNG TV PLUS": [],
    "📺 RAKUTEN TV": [],
    "📦 AUTRES": []
}

def normalize(text):
    if not text: return ""
    return re.sub(r'[^a-z0-9]', '', text.lower())

def get_tvg_id(info_line):
    match = re.search(r'tvg-id="([^"]+)"', info_line)
    return match.group(1).lower() if match else ""

def filter_playlist():
    print("Démarrage du filtrage...")
    try:
        r = requests.get(SOURCE_URL, timeout=30)
        r.raise_for_status()
        content = r.text
    except Exception as e:
        print(f"Erreur lors du téléchargement : {e}")
        return

    entries = re.findall(r'(#EXTINF:.*?\n(?:#EXTVLCOPT:.*?\n)*http.*)', content, re.MULTILINE)
    output_groups = {cat: [] for cat in CATEGORIES.keys()}

    for entry in entries:
        lines = entry.splitlines()
        info_line = lines[0]
        
        # Identification du nom affiché
        name_match = re.search(r',([^,]+)$', info_line)
        if not name_match: continue
        raw_name = name_match.group(1).strip()
        norm_name = normalize(raw_name)
        
        # Extraction du tvg-id pour le tri futur
        tvg_id = get_tvg_id(info_line)

        matched_at_least_once = False

        # 1. Services Automatiques
        auto_cat = None
        if "pluto" in norm_name: auto_cat = "📺 PLUTO TV"
        elif "samsung tv plus" in norm_name: auto_cat = "📺 SAMSUNG TV PLUS"
        elif "rakuten tv" in norm_name: auto_cat = "📺 RAKUTEN TV"

        if auto_cat:
            new_info = re.sub(r'group-title="[^"]+"', f'group-title="{auto_cat}"', info_line) if 'group-title="' in info_line else info_line.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="{auto_cat}"')
            output_groups[auto_cat].append({'tvg_id': tvg_id, 'data': f"{new_info}\n" + "\n".join(lines[1:])})
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
                    
                    output_groups[cat_name].append({'tvg_id': tvg_id, 'data': f"{new_info}\n" + "\n".join(lines[1:])})
                    matched_at_least_once = True
                    break 
        
        # 3. Repli
        if not matched_at_least_once:
            new_info = re.sub(r'group-title="[^"]+"', f'group-title="📦 AUTRES"', info_line) if 'group-title="' in info_line else info_line.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="📦 AUTRES"')
            output_groups["📦 AUTRES"].append({'tvg_id': tvg_id, 'data': f"{new_info}\n" + "\n".join(lines[1:])})

    # Écriture du fichier final avec tri par TVG-ID
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for cat in CATEGORIES.keys():
            if output_groups[cat]:
                # Tri de la liste par l'ID TVG
                sorted_channels = sorted(output_groups[cat], key=lambda x: x['tvg_id'])
                for item in sorted_channels:
                    f.write(item['data'] + "\n")
    
    print(f"Terminé ! Fichier '{OUTPUT_FILE}' généré avec tri par tvg-id.")

if __name__ == "__main__":
    filter_playlist()
