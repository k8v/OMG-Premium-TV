import requests

# URLs RAW de tes scripts sur GitHub
URL_SCRIPT_PAYS = "https://raw.githubusercontent.com/k8v/OMG-Premium-TV/main/countries_tri_playlist.py"
URL_SCRIPT_ZAP  = "https://raw.githubusercontent.com/k8v/OMG-Premium-TV/main/tri_zap"

def exec_remote_script(url):
    print(f"--- Recupération de : {url.split('/')[-1]} ---")
    try:
        response = requests.get(url)
        response.raise_for_status()
        # On exécute le code python téléchargé dans l'espace global
        exec(response.text, globals())
        print(f"Succès : {url.split('/')[-1]} execute.\n")
    except Exception as e:
        print(f"Erreur avec {url} : {e}")

if __name__ == "__main__":
    # 1. On lance d'abord le tri par pays
    exec_remote_script(URL_SCRIPT_ZAP)
    
    # 2. On lance ensuite le tri zap
    exec_remote_script(URL_SCRIPT_PAYS)
    
    print("Traitement global termine.")
