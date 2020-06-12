# Ce programme Python a permis d'ajouter les liens utilisés par Wikipédia pour
# écouter l'hymne national de chaque pays. L'objectif est d'ajouter l'hymne
# d'un pays dans la base de données.

from zipfile import ZipFile
import json

# import du module permettant d'exploiter des expressions régulières
import re

# import du module d'accès à la base de données
import sqlite3

# Récupération de l'hymne d'un pays depuis l'infobox wikipédia
def get_anthem(wp_info):
   
    # cas général
    if "national_anthem" in wp_info:
        anthem0 = wp_info["national_anthem"]
        if "[[File:" in anthem0 :
            anthem1 = anthem0.split("[[File:")[1]
            if ".ogg" in anthem1 :
                anthem2 = anthem1.split(".ogg")[0]
                return anthem2 + ".ogg"
            elif ".oga" in anthem1 :
                anthem2 = anthem1.split(".oga")[0]
                return anthem2 + ".oga"
            elif ".wav" in anthem1 :
                anthem2 = anthem1.split(".wav")[0]
                return anthem2 + ".wav"
    elif "anthem" in wp_info:
        anthem0 = wp_info["anthem"]
        if "[[File:" in anthem0 :
            anthem1 = anthem0.split("[[File:")[1]
            if ".ogg" in anthem1 :
                anthem2 = anthem1.split(".ogg")[0]
                return anthem2 + ".ogg"
            elif ".oga" in anthem1 :
                anthem2 = anthem1.split(".oga")[0]
                return anthem2 + ".oga"
            elif ".wav" in anthem1 :
                anthem2 = anthem1.split(".wav")[0]
                return anthem2 + ".wav"
    if "common_name" in wp_info :
        if wp_info["common_name"] == "Bosnia and Herzegovina" :
            return "Bosnia and Herzegovina's national anthem.ogg"
    # Aveu d'échec, on ne doit jamais se retrouver ici
    return None

def anthem_db(continent):
    with ZipFile('{}.zip'.format(continent),'r') as z:
        # liste des documents contenus dans le fichier zip
        files = z.namelist()
        for f in files:
            country = f.split('.')[0]
            # on remplace les "_" par des " "
            wp = country.replace('_',' ')
            m = re.search(r"(?P<wp>\D+) \(country\)",wp)
            if m != None :
                wp = m.group('wp')
            print(wp)
            # infobox de l'un des pays
            info = json.loads(z.read(f))
            save_anthem(conn,wp,info)
            
def save_anthem(conn,wp,info):
    # préparation de la commande SQL
    c = conn.cursor()
    sql = 'UPDATE countries SET anthem=? WHERE wp=?'
    anthem = get_anthem(info)
    print(anthem)
    # soumission de la commande (noter que le second argument est un tuple)
    c.execute(sql,(anthem,wp))
    conn.commit()

# ouverture d'une connexion avec la base de données
conn = sqlite3.connect('pays.sqlite')

# Ajout des hymnes dans la base de données
anthem_db('europe')
