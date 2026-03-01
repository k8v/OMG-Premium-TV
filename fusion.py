import requests
import os

# URLs RAW de tes scripts sur GitHub
URL_SCRIPT_PAYS = "https://raw.githubusercontent.com/k8v/OMG-Premium-TV/main/countries_tri_playlist.py"
URL_SCRIPT_ZAP  = "https://raw.githubusercontent.com/k8v/OMG-Premium-TV/main/tri_zap"

def run_remote(url, name):
    print(f">>> Lancement de : {name}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        # On force l'exécution dans le contexte actuel
        exec(response.text, globals())
        print(f">>> {name} : OK")
    except Exception as e:
        print(f"!!! ERREUR avec {name} : {e}")

if __name__ == "__main__":
    # On se place dans le répertoire de l'app pour être sûr que les scripts
    # trouvent et écrivent 'playlist.m3u' au bon endroit
    os.chdir('/app')
    
    # 1. Filtre par pays
    run_remote(URL_SCRIPT_PAYS, "TRI PAYS")
    
    # 2. Tri Zapping
    run_remote(URL_SCRIPT_ZAP, "TRI ZAP")
    
    print(">>> FUSION TERMINEE : Vérifiez le nombre de chaînes dans l'interface.")
