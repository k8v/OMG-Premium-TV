import requests

# Remplace par les URLs RAW (bouton 'Raw' sur GitHub) de TES scripts
URL_SCRIPT_ZAP  = "https://raw.githubusercontent.com/k8v/OMG-Premium-TV/main/tri_zap"
URL_SCRIPT_PAYS = "https://raw.githubusercontent.com/k8v/OMG-Premium-TV/main/countries_tri_playlist.py"

def exec_remote_script(url):
    print(f"--- Récupération de : {url.split('/')[-1]} ---")
    try:
        response = requests.get(url)
        response.raise_for_status()
        # On exécute le code python téléchargé
        exec(response.text, globals())
        print(f"Succès : {url.split('/')[-1]} exécuté.\n")
    except Exception as e:
        print(f"Erreur avec {url} : {e}")

if __name__ == "__main__":
    # 1. On lance les trie
      exec_remote_script(URL_SCRIPT_ZAP) 
      exec_remote_script(URL_SCRIPT_PAYS)
    
    print("Traitement global terminé.")
