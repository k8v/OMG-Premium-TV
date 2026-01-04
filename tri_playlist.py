import requests
import re
import os

# Configuration
# Utilisation de sources plus robustes et maintenues
SOURCE_URLS = [
    "https://iptv-org.github.io/iptv/languages/fra.m3u",
    "https://raw.githubusercontent.com/mcreal/m3u8-france/master/france.m3u", # Source alternative FR robuste
    "https://raw.githubusercontent.com/freetv-app/freetv-app/master/playlists/playlist_france.m3u" # Source complémentaire
]
OUTPUT_FILE = "generated.m3u"

# --- DICTIONNAIRE DE TRI MANUEL ---
# Les listes contiennent [Nom d'affichage, Aliases de recherche...]
CATEGORIES = {
    "🇫🇷 TNT": [
        ["TF1", "TF 1"], ["TF1 Séries Films", "TF1 Series"], ["France 2"], ["France 3"], 
        ["France 4"], ["France 5"], ["Canal+", "Canal Plus"], ["M6"], ["Arte"], ["LCP"], 
        ["W9"], ["TMC"], ["TFX"], ["Gulli"], ["BFM TV", "BFMTV"], 
        ["CNEWS", "C NEWS"], ["LCI"], ["Franceinfo", "France info"], ["CSTAR", "C STAR"], 
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
    """ Nettoie le nom pour une comparaison robuste sans espaces ni caractères spéciaux """
    if not name: return ""
    # On enlève tout ce qui n'est pas alphanumérique
    name = re.sub(r'[^a-zA-Z0-9]', '', name).lower()
    return name

def filter_playlist():
    found_targets = {} # {nom_chaine_final: (info, url)}
    
    # Étape 1 : Récupérer tout le contenu des sources
    all_lines = []
    for url in SOURCE_URLS:
        print(f"Téléchargement depuis : {url}")
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                all_lines.extend(r.text.splitlines())
            else:
                print(f"Erreur {r.status_code} sur {url}")
        except Exception as e:
            print(f"Erreur de connexion sur {url} : {e}")

    # Étape 2 : Analyser le contenu
    current_info = ""
    for line in all_lines:
        line = line.strip()
        if line.startswith("#EXTINF"):
            current_info = line
        elif line.startswith("http") and current_info:
            # Extraction du nom après la virgule
            name_match = re.search(r',([^,]+)$', current_info)
            if not name_match: continue
            
            raw_source_name = name_match.group(1).strip()
            clean_source = clean_name(raw_source_name)
            
            # Vérifier si ce flux correspond à une de nos catégories
            for cat_name, channel_groups in CATEGORIES.items():
                for aliases in channel_groups:
                    main_name = aliases[0]
                    
                    # Si déjà trouvé, on skip pour cette chaîne (priorité au premier flux trouvé)
                    if main_name in found_targets:
                        continue

                    is_match = False
                    for alias in aliases:
                        if clean_name(alias) == clean_source:
                            is_match = True
                            break
                    
                    if is_match:
                        # On injecte la catégorie dans le group-title
                        new_info = re.sub(r'group-title="[^"]+"', f'group-title="{cat_name}"', current_info)
                        if 'group-title="' not in new_info:
                            new_info = new_info.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="{cat_name}"')
                        
                        # Uniformisation du nom final
                        final_info = re.sub(r',[^,]+$', f',{main_name}', new_info)
                        found_targets[main_name] = (final_info, line, cat_name)

    # Étape 3 : Organiser et écrire le fichier
    final_m3u = ["#EXTM3U"]
    
    # On garde l'ordre des catégories défini dans le dictionnaire
    for cat_name in CATEGORIES:
        for main_name, data in found_targets.items():
            info, url, item_cat = data
            if item_cat == cat_name:
                final_m3u.append(info)
                final_m3u.append(url)

    # Étape 4 : Rapport
    all_requested = []
    for cat_list in CATEGORIES.values():
        for channel_group in cat_list:
            all_requested.append(channel_group[0])
            
    # Déduplication de la liste de contrôle
    all_requested = list(dict.fromkeys(all_requested))
    missing = [c for c in all_requested if c not in found_targets]

    if missing:
        print(f"\n--- Chaînes manquantes ({len(missing)}) ---")
        print(", ".join(sorted(missing)))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(final_m3u))
    
    print(f"\nScript terminé : {len(found_targets)} chaînes enregistrées dans {OUTPUT_FILE}.")

if __name__ == "__main__":
    filter_playlist()
