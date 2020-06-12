# Il est important que les autres fichiers Python du type "Python_DB_INIT_partie_X.py"
# se trouvent dans le même dossier que celui-ci, au même titre que le dossier
# "europe" permettant d'extraire les données sur les pays européens. La base de
# données sera alors créée dans ce même répertoire.

# Pour initialiser la base de données, il est nécessaire d'éxécuter le
# programme "Python_DB_INIT_partie_1.py" dans un premier temps. Puis, en
# ouvrant la base de données depuis l'application DB Browser (SQLite), une
# table 'countries' doit être créée de la façon suivante :
#    CREATE TABLE `countries` (             -- la table est nommé "countries"
#    	`wp`	TEXT NOT NULL UNIQUE,       -- nom de la page wikipédia, non nul, unique
#    	`name`	TEXT,                       -- nom complet du pays
#    	`capital`	TEXT,                   -- nom de la capitale
#    	`latitude`	REAL,                   -- latitude, champ numérique à valeur décimale
#    	`longitude`	REAL,                   -- longitude, champ numérique à valeur décimale
#    	PRIMARY KEY(`wp`)                   -- wp est la clé primaire
#    );
# Puis, et seulement ensuite, ce programme doit être éxécuté pour finaliser
# l'initialisation de la base de données.

from Python_DB_INIT_partie_1 import *

# ouverture d'une connexion avec la base de données
conn = sqlite3.connect('pays.sqlite')

def save_country(conn,country,info) :
    # on remplace les "_" par des " "
    wp = country.replace('_',' ')
    m = re.search(r"(?P<wp>\D+) \(country\)",wp)
    if m != None :
        wp = m.group('wp')
    # préparation de la commande SQL
    c = conn.cursor()
    sql = 'INSERT INTO countries VALUES (?, ?, ?, ?, ?)'
    # les infos à enregistrer
    name = get_name(info)
    capital = get_capital(info)
    coords = get_coords(info)
    # prendre en compte chaque cité-état
    if capital == 'city-state' :
        capital = wp
    # soumission de la commande (noter que le second argument est un tuple)
    c.execute(sql,(wp,name, capital, coords['lat'],coords['lon']))
    conn.commit()

# On essaie de lire un pays dans la base
def read_country(conn,country):
    # préparation de la commande SQL
    c = conn.cursor()
    sql = 'SELECT * FROM countries WHERE wp=?'
    # récupération de l'information (ou pas)
    c.execute(sql,(country,))
    r = c.fetchone()
    return r

# Récupération depuis un fichier zip 
from zipfile import ZipFile
import json

# Initialisation des informations dans la base de données
def init_db(continent):
    with ZipFile('{}.zip'.format(continent),'r') as z:
        # liste des documents contenus dans le fichier zip
        files = z.namelist()
        for f in files:
            country = f.split('.')[0]
            print(country)
            # infobox de l'un des pays
            info = json.loads(z.read(f))
            save_country(conn,country,info)

init_db('europe')

# Ce programme doit être éxécuté pour finaliser l'initialisation de la base de
# données. Par la suite, un champ nommé "continent" doit être ajouté dans la
# table "countries". Cette tâche doit être réalisée à l'aide de l'application
# DB Browser (SQLite). Puis, et seulement après, le programme "Python_DB_INIT_partie_3.py"
# doit être éxécuté pour compléter ce champ "continent".