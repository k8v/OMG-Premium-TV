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
        ["LCP", ["LCP", "Public Senat", "Assemblée Nationale", "Sénat Direct"]], ["BFM TV", ["BFM TV", "BFMTV"]], 
        ["CNews", ["CNews"]], ["CSTAR", ["CSTAR", "C Star"]], ["Gulli", ["Gulli"]], 
        ["TF1 Séries Films", ["TF1 Series", "TF1 Séries"]], ["L'Equipe", ["L'Equipe", "L'Équipe"]], 
        ["6ter", ["6ter"]], ["RMC Story", ["RMC Story"]], ["RMC Découverte", ["RMC Découverte"]], 
        ["Chérie 25", ["Chérie 25"]], ["LCI", ["LCI"]], ["Franceinfo", ["Franceinfo"]]
    ],
    "🎬 CINÉMA & SÉRIES": [
        ["Canal+", ["Canal Plus", "Canal+", "C+ France"]], ["AB1", ["AB1"]], ["Action", ["Action"]],
        ["Ciné+ Premier", ["Ciné+ Premier", "Cine+ Premier"]], ["Ciné+ Frisson", ["Ciné+ Frisson", "Cine+ Frisson"]],
        ["Ciné+ Emotion", ["Ciné+ Emotion", "Cine+ Emotion", "Emotion'L"]], ["Ciné+ Famiz", ["Ciné+ Famiz", "Cine+ Family"]],
        ["Ciné+ Classic", ["Ciné+ Classic", "Cine+ Classic"]], ["Ciné+ Festival", ["Cine+ Festival"]],
        ["Ciné+ OCS", ["Cine+ OCS", "OCS"]], ["Paramount Channel", ["Paramount Channel"]],
        ["Warner TV", ["Warner TV", "WarnerTV", "Warner TV Next"]], ["Série Club", ["Série Club", "Serie Club"]],
        ["TV Breizh", ["TV Breizh"]], ["Téva", ["Téva", "Teva"]], ["RTL9", ["RTL9"]],
        ["Novelas TV", ["Novelas TV", "Afro Novelas", "Fréquence Novelas"]], ["Crime District", ["Crime District", "Into Crime"]],
        ["Syfy", ["Syfy"]], ["Comedie+", ["Comedie+"]], ["Comedy Central", ["Comedy Central", "MyComedy", "Novocomedy"]],
        ["TCM Cinéma", ["TCM Cinéma", "TCM Cinema"]], ["Polar+", ["Polar+"]], ["Studiocanal", ["Studiocanal"]],
        ["Sony One", ["Sony One"]], ["Scream IN", ["Scream IN"]], ["Wild Side TV", ["Wild Side TV"]],
        ["Ciné Nanar", ["Ciné Nanar"]], ["Ciné Western", ["Ciné Western"]], ["Zylo Cinéma", ["Zylo"]]
    ],
    "🧸 JEUNESSE": [
        ["Disney Channel", ["Disney Channel"]], ["Disney Junior", ["Disney Junior"]],
        ["Nickelodeon", ["Nickelodeon", "Nickelodeon Junior", "Nickelodeon Teen"]], 
        ["Canal J", ["Canal J"]], ["TiJi", ["TiJi"]], ["Piwi+", ["Piwi+"]], 
        ["Télétoon+", ["Télétoon+", "Teletoon"]], ["Boomerang", ["Boomerang"]], 
        ["Mangas", ["Mangas", "ADN TV+"]], ["Gulli", ["Gulli"]], ["TiVi5 Monde", ["TiVi5 Monde"]],
        ["Ludikids", ["Ludikids"]], ["Bob l'éponge", ["Bob l'éponge"]], ["Caillou", ["Caillou"]],
        ["Amuse Animation", ["Amuse Animation"]], ["Nathan TV", ["Nathan TV"]]
    ],
    "🌍 DÉCOUVERTE & SAVOIR": [
        ["Animaux", ["Animaux"]], ["Histoire TV", ["Histoire TV"]], ["Toute l'Histoire", ["Toute l'Histoire"]],
        ["National Geographic", ["National Geographic", "Nat Geo"]], ["Planète+", ["Planète+", "Planete+"]],
        ["Ushuaïa TV", ["Ushuaïa TV", "Ushuaia"]], ["Science & Vie TV", ["Science & Vie TV"]],
        ["Museum TV", ["Museum TV"]], ["Chasse & Pêche", ["Chasse & Pêche"]], ["Trek", ["Trek"]],
        ["Ultra Nature", ["Ultra Nature"]], ["L'Esprit Sorcier TV", ["L'Esprit Sorcier"]],
        ["Maison & Travaux TV", ["Maison & Travaux"]], ["Atelier des chefs", ["Atelier des chefs"]],
        ["Marmiton TV", ["Marmiton"]], ["Discovery Channel", ["Discovery Channel"]],
        ["Investigation Discovery", ["Investigation Discovery", "Dossiers FBI"]]
    ],
    "📰 INFOS & ÉCONOMIE": [
        ["BFM Business", ["BFM Business"]], ["BFM Tech & Co", ["BFM Tech & Co"]], ["Euronews", ["Euronews"]],
        ["France 24", ["France 24"]], ["i24 News", ["i24 News"]], ["Le Figaro TV", ["Le Figaro TV", "Le Figaro Live"]],
        ["La Chaîne Météo", ["Météo", "La Chaine Meteo"]], ["B Smart TV", ["B Smart"]], ["TV Finance", ["TV Finance"]]
    ],
    "🎶 MUSIQUE & DIVERTISSEMENT": [
        ["MCM", ["MCM", "MCM Top"]], ["MTV", ["MTV"]], ["Mezzo", ["Mezzo"]], ["Melody", ["Melody"]],
        ["RFM TV", ["RFM TV"]], ["NRJ Hits", ["NRJ Hits"]], ["Trace Urban", ["Trace Urban", "Trace Hip-Hop", "Trace Latina"]],
        ["Trace Caribbean", ["Trace Caribbean", "Trace Ayiti"]], ["Trace Gospel", ["Trace Gospel"]],
        ["Bblack!", ["Bblack"]], ["C STAR Hits", ["C Star Hits"]], ["M6 Music", ["M6 Music"]],
        ["Wataaa TV", ["Wataaa"]], ["Qwest TV", ["Qwest TV"]], ["Fashion TV", ["Fashion TV", "FashionTV"]],
        ["Clique TV", ["Clique TV"]], ["Juste pour Rire", ["Juste pour Rire"]]
    ],
    "📍 RÉGIONALES & LOCALES": [
        ["8 Mont-Blanc", ["8 Mont-Blanc", "Radio Mont Blanc", "TV8 Mont-Blanc"]],
        ["BFM Régions", ["BFM Alsace", "BFM Lyon", "BFM Marseille", "BFM Paris", "BFM Nice", "BFM Cote d'Azur", "BFM Normandie", "BFM Var", "BFM DICI", "BFM Grand Lille", "BFM Grand Littoral"]],
        ["Télénantes", ["Télénantes"]], ["TV7 Bordeaux", ["TV7 Bordeaux"]], ["Vosges TV", ["Vosges TV", "Vosges Télévision"]],
        ["KTO", ["KTO", "Chrétiens TV", "HolyGod", "EMCI", "Evangile TV", "DieuTV", "Radio Télé Silo"]],
        ["Canal 32", ["Canal 32", "La Chaîne 32"]], ["Wéo", ["Wéo", "Wéo Picardie"]], 
        ["7ALimoges", ["7ALimoges"]], ["Angers Télé", ["Angers Télé"]], ["ASTV", ["ASTV"]],
        ["BIP TV", ["BIP TV"]], ["LM TV Sarthe", ["LM TV Sarthe"]], ["TL7", ["TL7"]],
        ["TVR", ["TVR"]], ["Canal Zoom", ["Canal Zoom"]], ["Canal Alpha", ["Canal Alpha"]],
        ["Mosaïk Cristal", ["Mosaïk Cristal"]], ["IDF1", ["IDF1"]]
    ],
    "⚽ SPORTS": [
        ["Canal+ Sport", ["Canal+ Sport", "Canal+ Foot", "Canal+ MotoGP", "Canal+ Formula 1", "Canal+ Sport 360", "Canal+ Top 14", "Canal+ Premier League"]],
        ["BeIN Sports", ["BeIN Sports", "beIN 1", "beIN 2", "beIN 3"]], ["Eurosport", ["Eurosport"]],
        ["Equidia", ["Equidia"]], ["RMC Sport", ["RMC Sport"]], ["Infosport+", ["Infosport+"]],
        ["Golf+", ["Golf +", "Golf Channel"]], ["Africa 24 Sport", ["Africa 24 Sport", "Africa Sports TV"]],
        ["Sport en France", ["Sport en France"]], ["NHL Centre Ice", ["NHL Centre Ice"]]
    ],
    "🇧🇪 BELGIQUE": [
        ["La Une", ["La Une"]], ["La Deux", ["La Deux"]], ["La Trois", ["La Trois"]], 
        ["RTL-TVI", ["RTL-TVI", "RTL TVI"]], ["Club RTL", ["Club RTL"]], ["Plug RTL", ["Plug RTL"]],
        ["LN24", ["LN24"]], ["Tipik", ["Tipik"]], ["BX1", ["BX1"]]
    ],
    "🇨🇭 SUISSE": [
        ["RTS Un", ["RTS Un"]], ["RTS Deux", ["RTS Deux"]], ["SRF info", ["SRF info"]],
        ["TVM3", ["TVM3"]], ["Couleur 3", ["Couleur 3"]]
    ],
    "🇨🇦 CANADA / QUÉBEC": [
        ["ICI Radio-Canada", ["Radio-Canada", "ICI Tele"]], ["TVA", ["TVA"]], 
        ["Noovo", ["Noovo"]], ["LCN", ["LCN"]], ["ICI RDI", ["ICI RDI"]],
        ["Télé-Québec", ["Télé-Québec"]]
    ],
    "🌍 AFRIQUE & DOM-TOM": [
        ["A+", ["A+", "A Plus"]], ["Africa 24", ["Africa 24"]], ["Africanews", ["Africanews"]], 
        ["Nollywood TV", ["Nollywood TV"]], ["TV5Monde", ["TV5 Monde", "TV5Monde"]], 
        ["RTB", ["RTB"]], ["RTI", ["RTI"]], ["ORTM", ["ORTM"]], ["2M Monde", ["2M Monde"]],
        ["Antenne Réunion", ["Antenne Réunion"]], ["Bblack! Africa", ["Bblack! Africa"]],
        ["Trace Africa", ["Trace Africa"]], ["Canal 3 Monde", ["Canal 3 Monde"]],
        ["RTNC", ["RTNC"]], ["RTS 1", ["RTS 1"]], ["TFM", ["TFM"]], ["Life TV", ["Life TV"]]
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
        name_match = re.search(r',([^,]+)$', info_line)
        if not name_match: continue
        raw_name = name_match.group(1).strip()
        norm_name = normalize(raw_name)

        matched_at_least_once = False

        # 1. Services Automatiques (Pluto, Samsung, Rakuten uniquement)
        auto_cat = None
        if "pluto" in norm_name: auto_cat = "📺 PLUTO TV"
        elif "samsung tv plus" in norm_name: auto_cat = "📺 SAMSUNG TV PLUS"
        elif "rakuten tv" in norm_name: auto_cat = "📺 RAKUTEN TV"

        if auto_cat:
            new_info = re.sub(r'group-title="[^"]+"', f'group-title="{auto_cat}"', info_line) if 'group-title="' in info_line else info_line.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="{auto_cat}"')
            output_groups[auto_cat].append(f"{new_info}\n" + "\n".join(lines[1:]))
            continue

        # 2. Catégories Manuelles
        # On parcourt les catégories. Dès qu'un match est trouvé, on s'arrête pour cette catégorie.
        for cat_name, channels in CATEGORIES.items():
            found_in_cat = False
            for display_name, keywords in channels:
                # On vérifie si un mot-clé correspond parfaitement ou si le nom normalisé contient le mot-clé normalisé
                if any(normalize(k) == norm_name or (len(normalize(k)) > 3 and normalize(k) in norm_name) for k in keywords):
                    new_info = re.sub(r',.*$', f',{display_name}', info_line)
                    if 'group-title="' in new_info:
                        new_info = re.sub(r'group-title="[^"]+"', f'group-title="{cat_name}"', new_info)
                    else:
                        new_info = new_info.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="{cat_name}"')
                    
                    output_groups[cat_name].append(f"{new_info}\n" + "\n".join(lines[1:]))
                    matched_at_least_once = True
                    found_in_cat = True
                    break 
            if found_in_cat: break
        
        # 3. Repli si aucun match
        if not matched_at_least_once:
            new_info = re.sub(r'group-title="[^"]+"', f'group-title="📦 AUTRES"', info_line) if 'group-title="' in info_line else info_line.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="📦 AUTRES"')
            output_groups["📦 AUTRES"].append(f"{new_info}\n" + "\n".join(lines[1:]))

    # Écriture du fichier final
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for cat in CATEGORIES.keys():
            if output_groups[cat]:
                for item in output_groups[cat]:
                    f.write(item + "\n")
    
    print(f"Terminé ! Fichier '{OUTPUT_FILE}' généré.")

if __name__ == "__main__":
    filter_playlist()
