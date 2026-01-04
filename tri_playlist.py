import requests
import re

# Configuration
SOURCE_URL = "https://iptv-org.github.io/iptv/languages/fra.m3u"
OUTPUT_FILE = "generated.m3u"

# --- DICTIONNAIRE DE TRI (Basé sur ta liste) ---
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
    "⚽ SPORTS": [
        ["Canal+ Sport", ["Canal+ Sport", "Canal + Sport"]], 
        ["BeIN Sports 1", ["BeIN Sports 1", "beIN 1"]],
        ["BeIN Sports 2", ["BeIN Sports 2", "beIN 2"]],
        ["BeIN Sports 3", ["BeIN Sports 3", "beIN 3"]],
        ["Eurosport 1", ["Eurosport 1"]], 
        ["Eurosport 2", ["Eurosport 2"]], 
        ["Equidia", ["Equidia"]], 
        ["Automoto la chaîne", ["Automoto"]],
        ["Africa 24 Sport", ["Africa 24 Sport"]],
        ["Sport en France", ["Sport en France"]],
        ["Trace Sport Stars", ["Trace Sport Stars"]]
    ],
    "🎬 CINÉMA & SÉRIES": [
        ["Canal+", ["Canal+"]], 
        ["Canal+ Cinema", ["Canal+ Cinema", "Ciné+", "Cine+"]], 
        ["Ciné+ Premier", ["Ciné+ Premier"]],
        ["Ciné+ Frisson", ["Ciné+ Frisson"]],
        ["Ciné+ Emotion", ["Ciné+ Emotion"]],
        ["Ciné+ Famiz", ["Ciné+ Famiz"]],
        ["Ciné+ Classic", ["Ciné+ Classic"]],
        ["Action", ["Action"]], 
        ["AB1", ["AB1"]],
        ["RTL9", ["RTL9"]], 
        ["Téva", ["Téva"]], 
        ["Paramount Channel", ["Paramount Channel"]], 
        ["Warner TV", ["Warner TV"]], 
        ["Novelas TV", ["Novelas TV"]], 
        ["Crime District", ["Crime District"]],
        ["OCS Max", ["OCS Max"]],
        ["OCS City", ["OCS City"]],
        ["OCS Choc", ["OCS Choc"]],
        ["OCS Géants", ["OCS Géants"]],
        ["Zylo Cinéma", ["Zylo", "Ciné Nanar", "Ciné Western"]]
    ],
    "🇧🇪 BELGIQUE": [
        ["La Une", ["La Une"]], 
        ["La Deux", ["La Deux"]], 
        ["La Trois", ["La Trois"]], 
        ["RTL-TVI", ["RTL-TVI", "RTL TVI"]], 
        ["Club RTL", ["Club RTL"]], 
        ["Plug RTL", ["Plug RTL"]]
    ],
    "🇨Header 🇨🇭 SUISSE": [
        ["RTS Un", ["RTS Un"]], 
        ["RTS Deux", ["RTS Deux"]], 
        ["SRF info", ["SRF info"]]
    ],
    "🇨🇦 CANADA / QUÉBEC": [
        ["ICI Radio-Canada", ["Radio-Canada", "ICI Tele"]], 
        ["TVA", ["TVA"]], 
        ["Noovo", ["Noovo"]], 
        ["LCN", ["LCN"]]
    ],
    "🌍 AFRIQUE & DOM-TOM": [
        ["A+", ["A+", "A Plus"]], 
        ["Africa 24", ["Africa 24"]],
        ["Africanews", ["Africanews", "Africa News"]], 
        ["Nollywood TV", ["Nollywood TV"]],
        ["TV5Monde Afrique", ["TV5Monde Afrique"]], 
        ["RTB", ["RTB"]], 
        ["RTI", ["RTI"]], 
        ["ORTM", ["ORTM"]], 
        ["2M Monde", ["2M Monde"]],
        ["Antenne Réunion", ["Antenne Réunion"]],
        ["Canal 10", ["Canal 10"]],
        ["Canal 3 Monde", ["Canal 3 Monde"]],
        ["France Ô", ["France Ô"]],
        ["3A Telesud", ["Telesud", "3A Telesud"]],
        ["Bblack! Africa", ["Bblack! Africa"]],
        ["Trace Africa", ["Trace Africa"]]
    ],
    "💎 CANAL+": [], # Catégorie pour les flux "FAST" Canal+ ou automatiques
    "📺 PLUTO TV": [],
    "📺 SAMSUNG TV PLUS": [],
    "📺 RAKUTEN TV": []
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

    # Extraction des entrées M3U
    entries = re.findall(r'(#EXTINF:.*?\n(?:#EXTVLCOPT:.*?\n)*http.*)', content, re.MULTILINE)
    
    output_groups = {cat: [] for cat in CATEGORIES.keys()}
    output_groups["AUTRES"] = []

    for entry in entries:
        lines = entry.splitlines()
        info_line = lines[0]
        
        name_match = re.search(r',([^,]+)$', info_line)
        if not name_match: continue
        raw_name = name_match.group(1).strip()
        norm_name = normalize(raw_name)

        # 1. Détection automatique des services FAST
        auto_cat = None
        if "pluto" in norm_name:
            auto_cat = "📺 PLUTO TV"
        elif "samsung" in norm_name:
            auto_cat = "📺 SAMSUNG TV PLUS"
        elif "rakuten" in norm_name:
            auto_cat = "📺 RAKUTEN TV"
        # On ne met en auto "CANAL+" que s'il n'est pas déjà spécifiquement trié dans Sport ou Ciné
        elif "canal" in norm_name and not any(k in norm_name for k in ["sport", "cinema", "cine"]):
            auto_cat = "💎 CANAL+"

        if auto_cat:
            new_info = info_line
            if 'group-title="' in info_line:
                new_info = re.sub(r'group-title="[^"]+"', f'group-title="{auto_cat}"', info_line)
            else:
                new_info = info_line.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="{auto_cat}"')
            output_groups[auto_cat].append(f"{new_info}\n" + "\n".join(lines[1:]))
            continue

        # 2. Match avec le dictionnaire fixe
        matched = False
        for cat_name, channels in CATEGORIES.items():
            if not channels: continue
            for display_name, keywords in channels:
                if any(normalize(k) in norm_name for k in keywords):
                    # Forcer le nom propre et le groupe
                    new_info = re.sub(r',.*$', f',{display_name}', info_line)
                    if 'group-title="' in new_info:
                        new_info = re.sub(r'group-title="[^"]+"', f'group-title="{cat_name}"', new_info)
                    else:
                        new_info = new_info.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="{cat_name}"')
                    
                    output_groups[cat_name].append(f"{new_info}\n" + "\n".join(lines[1:]))
                    matched = True
                    break
            if matched: break
        
        if not matched:
            output_groups["AUTRES"].append(entry)

    # Création du fichier final
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for cat in CATEGORIES.keys():
            if output_groups[cat]:
                f.write(f"\n# --- {cat} ---\n")
                for item in output_groups[cat]:
                    f.write(item + "\n")
    
    print(f"Fichier '{OUTPUT_FILE}' généré avec succès.")

if __name__ == "__main__":
    filter_playlist()
