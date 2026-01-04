import requests
import re
import os

# Configuration
# On définit plusieurs sources pour maximiser les chances de trouver les chaînes de la TNT
SOURCE_URLS = [
    "https://iptv-org.github.io/iptv/languages/fra.m3u",
    "https://raw.githubusercontent.com/PolySnd/frenchnews/master/frenchnews.m3u",
    "https://raw.githubusercontent.com/The-Beast-2/Playlist-IPTV-Gratuit/main/Playlist-IPTV-Gratuit.m3u"
]
OUTPUT_FILE = "generated.m3u"

# --- DICTIONNAIRE DE TRI MANUEL ---
CATEGORIES = {
    "🇫🇷 TNT": [
        ["TF1"], ["TF1 Séries Films", "TF1 Series"], ["France 2"], ["France 3"], 
        ["France 4"], ["France 5"], ["Canal+"], ["M6"], ["Arte"], ["LCP"], 
        ["W9"], ["TMC"], ["TFX"], ["Gulli"], ["BFM TV", "BFMTV"], 
        ["CNEWS"], ["LCI"], ["Franceinfo", "France info"], ["CSTAR"], 
        ["CMI TV"], ["OFTV"], ["L'Equipe", "L'Équipe"], ["6Ter"], 
        ["RMC Story"], ["RMC Découverte"], ["Chérie 25"]
    ],
    "🎬 CINÉMA": [
        ["AB1"], ["Action"], ["Ciné+ Premier", "Cine+ Premier"], ["Ciné+ Frisson"], 
        ["Ciné+ Emotion"], ["Ciné+ Famiz"], ["Ciné+ Classic"], ["Crime District"], 
        ["OCS Max"], ["OCS City"], ["OCS Choc"], ["OCS Géants"], ["Mangas"], 
        ["Paramount Channel"], ["RTL9"], ["Téva", "Teva"]
    ],
    "⚽ SPORTS": [
        ["Canal+ Sport"], ["Equidia"], ["Eurosport 1"], ["Eurosport 2"], 
        ["L'Equipe"], ["RMC Sport 1"]
    ],
    "🧸 JEUNESSE": [
        ["Canal J"], ["Disney Channel"], ["Gulli"], ["Mangas"], ["Piwi+"], 
        ["Game One"], ["J-One"]
    ],
    "🌍 DÉCOUVERTE": [
        ["Animaux"], ["Histoire TV"], ["Le Figaro TV"], ["Montagne TV"], 
        ["Museum TV"], ["National Geographic", "Nat Geo"], ["Planète+"], 
        ["Science & Vie TV"], ["Toute l'Histoire"], ["Ushuaïa TV"], ["RMC Découverte"]
    ],
    "📰 INFOS": [
        ["BFM Business"], ["Euronews"], ["France 24"], ["i24 News"], 
        ["Le Figaro TV"], ["LCI"], ["La Chaîne Météo"]
    ],
    "🎶 MUSIQUE & DIVERTISSEMENT": [
        ["MCM"], ["Mezzo"], ["MTV France", "MTV"]
    ],
    "📍 RÉGIONALES": [
        ["7ALimoges"], ["8 Mont-Blanc"], ["Alsace 20"], ["ASTV"], ["BFM Grand Lille"], 
        ["BFM Grand Littoral"], ["BFM Lyon"], ["BFM Marseille"], ["BFM Nice"], 
        ["BFM Paris"], ["BIP TV"], ["IDF1"], ["Télénantes"], ["TV7 Bordeaux"], 
        ["Vosges TV"], ["Charente Libre"], ["Canal Alpha"], ["KTO"]
    ],
    "🌍 INTERNATIONAL": [
        ["24h au Bénin"], ["3A Telesud"], ["Africa 24"], ["Africanews"], ["Al Aoula"], 
        ["Antenne Réunion"], ["BFM West"], ["BRTV"], ["Canal 10"], ["Canal 3 Monde"], 
        ["Canal+ Afrique"], ["France Ô"], ["TV5 Monde"]
    ]
}

def clean_name(name):
    """ Nettoie le nom pour une comparaison robuste """
    if not name: return ""
    name = re.sub(r'\(.*\)', '', name) 
    name = re.sub(r'[^a-zA-Z0-9]', '', name).lower()
    return name

def filter_playlist():
    found_targets = {} # Stocke {nom_chaine: (info, url)}
    all_content = []

    for url in SOURCE_URLS:
        print(f"Téléchargement de la playlist depuis {url}...")
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            all_content.extend(response.text.splitlines())
        except Exception as e:
            print(f"Saut de la source {url} : {e}")

    organized_content = {cat: [] for cat in CATEGORIES}
    
    current_info = ""
    for line in all_content:
        if line.startswith("#EXTINF"):
            current_info = line
        elif line.startswith("http"):
            match = re.search(r',(.+)$', current_info)
            if not match: continue
            
            raw_source_name = match.group(1).strip()
            clean_source = clean_name(raw_source_name)
            
            for cat_name, channel_groups in CATEGORIES.items():
                for aliases in channel_groups:
                    main_name = aliases[0]
                    
                    # Si on a déjà trouvé cette chaîne, on ne la traite plus (sauf si flux vide)
                    if main_name in found_targets:
                        continue

                    found_alias = False
                    for alias in aliases:
                        clean_alias = clean_name(alias)
                        if clean_alias == clean_source or (clean_alias in clean_source and len(clean_alias) > 3):
                            found_alias = True
                            break
                    
                    if found_alias:
                        new_info = re.sub(r'group-title="[^"]+"', f'group-title="{cat_name}"', current_info)
                        if 'group-title="' not in new_info:
                            new_info = new_info.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="{cat_name}"')
                        
                        new_info = re.search(r'#EXTINF:[^,]+', new_info).group(0) + f",{main_name}"
                        found_targets[main_name] = (new_info, line)
                        organized_content[cat_name].append((new_info, line))

    final_lines = ["#EXTM3U"]
    total_count = 0
    
    for cat in CATEGORIES:
        for info, stream_url in organized_content[cat]:
            final_lines.append(info)
            final_lines.append(stream_url)
            total_count += 1

    # Rapport final
    all_targets_list = [group[0] for cat in CATEGORIES.values() for group in cat]
    missing = [t for t in all_targets_list if t not in found_targets]
    
    if missing:
        print(f"\n--- Chaînes toujours introuvables ({len(missing)}) ---")
        print(", ".join(sorted(missing)))

    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(final_lines))
        print(f"\nSuccès : {total_count} chaînes uniques filtrées dans {OUTPUT_FILE}.")
    except Exception as e:
        print(f"Erreur d'écriture : {e}")

if __name__ == "__main__":
    filter_playlist()
