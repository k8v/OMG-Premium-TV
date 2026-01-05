import requests
import re
import os

# Configuration
SOURCE_URL = "https://iptv-org.github.io/iptv/languages/fra.m3u"
OUTPUT_FILE = "generated.m3u"

# --- CONFIGURATION DES CATÉGORIES (Simplifiée pour la détection) ---
# On garde les noms de ton immense liste pour le filtrage
CATEGORIES = {
    "🇫🇷 TNT": ["TF1", "France 2", "France 3", "France 4", "France 5", "M6", "Arte", "C8", "W9", "TMC", "TFX", "NRJ 12", "LCP", "BFM TV", "CNews", "CSTAR", "Gulli", "TF1 Séries Films", "L'Equipe", "6ter", "RMC Story", "RMC Découverte", "Chérie 25", "LCI", "Franceinfo"],
    "🎬 CINÉMA & SÉRIES": ["Canal+", "Ciné+", "OCS", "Action", "AB1", "RTL9", "Téva", "Paramount Channel", "Warner TV", "Novelas TV", "Crime District", "Série Club", "Syfy", "TV Breizh", "Polar+", "Comedy Central", "Comedie+", "Studiocanal", "TCM Cinéma", "Persiana", "Sony One", "Juste pour Rire", "Les Cordier", "Les filles d'à côté", "Ciné Nanar", "Ciné Western"],
    "🧸 JEUNESSE": ["Canal J", "Disney Channel", "Mangas", "Piwi+", "Nickelodeon", "TiJi", "Teletoon+", "Boomerang", "Cartoon Network", "TiVi5 Monde", "Gulli", "ADN TV+", "Ludikids", "Caillou", "Bob l'éponge", "Amuse Animation"],
    "🌍 DÉCOUVERTE & SAVOIR": ["Animaux", "Histoire TV", "Museum TV", "National Geographic", "Planète+", "Science & Vie TV", "Toute l'Histoire", "Ushuaïa TV", "Montagne TV", "Discovery Channel", "Investigation Discovery", "Chasse & Pêche", "Trek", "Seasons", "Ultra Nature", "Maison & Travaux TV", "L'Esprit Sorcier TV", "Marmiton TV"],
    "📰 INFOS & ÉCONOMIE": ["BFM Business", "Euronews", "France 24", "i24 News", "Le Figaro TV", "La Chaîne Météo", "B Smart TV", "TV Finance", "Africanews"],
    "🎶 MUSIQUE & DIVERTISSEMENT": ["MCM", "Mezzo", "MTV", "Trace", "Bblack!", "Melody", "RFM TV", "NRJ Hits", "C Star Hits", "M6 Music", "Mouv' TV", "Qwest TV", "Fashion TV", "Clique TV"],
    "📍 RÉGIONALES & LOCALES": ["Canal Alpha", "7ALimoges", "8 Mont-Blanc", "Alsace 20", "ASTV", "BIP TV", "Télénantes", "TV7 Bordeaux", "Vosges TV", "KTO", "Canal 32", "Wéo", "Tébéo", "TébéSud", "Grand Genève TV", "TVR", "Matélé", "TL7", "Canal Zoom", "Cannes Lérins", "Nancy Web TV"],
    "⚽ SPORTS": ["Sport", "BeIN Sports", "Eurosport", "Equidia", "Automoto", "RMC Sport", "Golf", "MultiSports", "Foot+", "Fighting Spirit"],
    "🇧🇪 BELGIQUE": ["La Une", "La Deux", "La Trois", "RTL-TVI", "Club RTL", "Plug RTL", "LN24", "Tipik", "BX1", "Bouke", "Bruzz"],
    "🇨🇭 SUISSE": ["RTS Un", "RTS Deux", "SRF info", "TVM3", "Léman Bleu"],
    "🇨🇦 CANADA / QUÉBEC": ["Radio-Canada", "ICI Tele", "ICI RDI", "TVA", "Noovo", "LCN", "Télé-Québec"],
    "🌍 AFRIQUE & DOM-TOM": ["A+", "Africa 24", "Africanews", "Nollywood", "RTB", "RTI", "ORTM", "2M Monde", "Antenne Réunion", "2STV", "TFM", "Sen TV", "NCI", "Life TV", "Canal 2 International"],
    "📺 PLUTO TV": [],
    "📺 SAMSUNG TV PLUS": [],
    "📺 RAKUTEN TV": [],
    "📦 AUTRES": []
}

def normalize(text):
    if not text: return ""
    return re.sub(r'[^a-z0-9]', '', text.lower())

def get_tvg_id(info_line):
    # Recherche précise de tvg-id="..."
    match = re.search(r'tvg-id="([^"]+)"', info_line, re.IGNORECASE)
    return match.group(1) if match else "zzz_no_id"

def filter_playlist():
    print("Démarrage du filtrage...")
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
        
        # On récupère le nom tel qu'il est dans le fichier source (ex: "Canal 32")
        name_match = re.search(r',([^,]+)$', info_line)
        if not name_match: continue
        original_name = name_match.group(1).strip()
        norm_name = normalize(original_name)
        
        tvg_id = get_tvg_id(info_line)

        # 1. Services Auto
        auto_cat = None
        if "pluto" in norm_name: auto_cat = "📺 PLUTO TV"
        elif "samsungtvplus" in norm_name: auto_cat = "📺 SAMSUNG TV PLUS"
        elif "rakuten" in norm_name: auto_cat = "📺 RAKUTEN TV"

        if auto_cat:
            new_info = re.sub(r'group-title="[^"]+"', f'group-title="{auto_cat}"', info_line) if 'group-title="' in info_line else info_line.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="{auto_cat}"')
            output_groups[auto_cat].append({'id': tvg_id, 'data': f"{new_info}\n" + "\n".join(lines[1:])})
            continue

        # 2. Attribution par mots-clés (sans renommer la chaîne)
        matched = False
        for cat_name, keywords in CATEGORIES.items():
            if not keywords: continue
            if any(normalize(k) in norm_name for k in keywords):
                # On garde original_name, on change juste le groupe
                if 'group-title="' in info_line:
                    new_info = re.sub(r'group-title="[^"]+"', f'group-title="{cat_name}"', info_line)
                else:
                    new_info = info_line.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="{cat_name}"')
                
                output_groups[cat_name].append({'id': tvg_id, 'data': f"{new_info}\n" + "\n".join(lines[1:])})
                matched = True
                break
        
        if not matched:
            new_info = re.sub(r'group-title="[^"]+"', f'group-title="📦 AUTRES"', info_line) if 'group-title="' in info_line else info_line.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="📦 AUTRES"')
            output_groups["📦 AUTRES"].append({'id': tvg_id, 'data': f"{new_info}\n" + "\n".join(lines[1:])})

    # Écriture finale
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for cat in CATEGORIES.keys():
            # Tri alphabétique par tvg-id au sein de chaque catégorie
            sorted_channels = sorted(output_groups[cat], key=lambda x: x['id'].lower())
            for item in sorted_channels:
                f.write(item['data'] + "\n")
    
    print(f"Terminé ! Tri par tvg-id effectué pour {len(entries)} entrées.")

if __name__ == "__main__":
    filter_playlist()
