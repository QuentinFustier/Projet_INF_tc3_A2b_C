# Il est important que les autres fichiers Python du type "Python_DB_INIT_partie_X.py"
# se trouvent dans le même dossier que celui-ci, au même titre que le dossier
# "europe" permettant d'extraire les données sur les pays européens. La base de
# données sera alors créée dans ce même répertoire.

# Récupération de l'infobox d'un pays sur wikipédia
def get_info(country):
    # récupération de la page du pays passé en argument
    # on peut ajouter silent=True pour éviter le message sur fond rose
    page = wptools.page(country, silent=True)
    # analyse du contenu de la page
    # l'argument False sert à ne pas afficher de message sur fond rose
    page.get_parse(False)
    # On renvoie l'infobox
    return page.data['infobox']

# import du module permettant d'exploiter des expressions régulières
import re

# Récupération du nom complet d'un pays depuis l'infobox wikipédia
def get_name(wp_info):  
    # cas général
    if 'conventional_long_name' in wp_info:
        name = wp_info['conventional_long_name']
        m = re.search(r"\{\{nowrap\|(?P<name>\D+)\}\}",name)
        if m != None :
            name = m.group('name')
        m_bis = re.search(r"(?P<name>\D+) \{\{small\|ref label\|nomenclature\|a\}\} \{\{ref label\|nomenclature\|a\}\}",name)
        if m_bis != None :
            name = m_bis.group('name')
        return name
    # Aveu d'échec, on ne doit jamais se retrouver ici
    print('Could not fetch country name {}'.format(wp_info))
    return None

# Récupération de la capitale d'un pays depuis l'infobox wikipédia
def get_capital(wp_info):  
    # cas général
    if 'capital' in wp_info:      
        # parfois l'information récupérée comporte plusieurs lignes
        # on remplace les retours à la ligne par un espace
        capital = wp_info['capital'].replace('\n',' ')       
        # le nom de la capitale peut comporter des lettres, des espaces,
        # ou l'un des caractères ',.()|- compris entre crochets [[...]]
        m = re.match(".*?\[\[([\w\s',.()|-]+)\]\]", capital)     
        # on récupère le contenu des [[...]]
        capital = m.group(1)    
        m_bis = re.search(r"City of (?P<city1>\D+)\|(?P<city2>\D+)",capital)
        if m_bis != None :
            if m_bis.group('city1') == m_bis.group('city2') :
                capital = m_bis.group('city1')      
        return capital
    # Aveu d'échec, on ne doit jamais se retrouver ici
    print(' Could not fetch country capital {}'.format(wp_info))
    return None

# Conversion d'une chaîne de caractères décrivant une position géographique
# en coordonnées numériques latitude et longitude
#
def cv_coords(str_coords):
    # on découpe au niveau des "|" 
    c = str_coords.split('|')
    # on extrait la latitude en tenant compte des divers formats
    lat = float(c.pop(0))
    if (c[0] == 'N'):
        c.pop(0)
    elif ( c[0] == 'S' ):
        lat = -lat
        c.pop(0)
    elif ( len(c) > 1 and c[1] == 'N' ):
        lat += float(c.pop(0))/60
        c.pop(0)
    elif ( len(c) > 1 and c[1] == 'S' ):
        lat += float(c.pop(0))/60
        lat = -lat
        c.pop(0)
    elif ( len(c) > 2 and c[2] == 'N' ):
        lat += float(c.pop(0))/60
        lat += float(c.pop(0))/3600
        c.pop(0)
    elif ( len(c) > 2 and c[2] == 'S' ):
        lat += float(c.pop(0))/60
        lat += float(c.pop(0))/3600
        lat = -lat
        c.pop(0)
    # on fait de même avec la longitude
    lon = float(c.pop(0))
    if (c[0] == 'W'):
        lon = -lon
        c.pop(0)
    elif ( c[0] == 'E' ):
        c.pop(0)
    elif ( len(c) > 1 and c[1] == 'W' ):
        lon += float(c.pop(0))/60
        lon = -lon
        c.pop(0)
    elif ( len(c) > 1 and c[1] == 'E' ):
        lon += float(c.pop(0))/60
        c.pop(0)
    elif ( len(c) > 2 and c[2] == 'W' ):
        lon += float(c.pop(0))/60
        lon += float(c.pop(0))/3600
        lon = -lon
        c.pop(0)
    elif ( len(c) > 2 and c[2] == 'E' ):
        lon += float(c.pop(0))/60
        lon += float(c.pop(0))/3600
        c.pop(0)
    # on renvoie un dictionnaire avec les deux valeurs
    return {'lat':float(round(lat,2)), 'lon':float(round(lon,2)) }

# Récupération des coordonnées de la capitale depuis l'infobox d'un pays
def get_coords(wp_info):
    # S'il existe des coordonnées dans l'infobox du pays
    # (cas le plus courant)
    if 'coordinates' in wp_info:
        # (?i) - ignorecase - matche en majuscules ou en minuscules
        # ça commence par "{{coord" et se poursuit avec zéro ou plusieurs
        #   espaces suivis par une barre "|"
        # après ce motif, on mémorise la chaîne la plus longue possible
        #   ne contenant pas de },
        # jusqu'à la première occurence de "}}"
        m = re.match('(?i).*{{coord\s*\|([^}]*)}}', wp_info['coordinates'])
        # l'expression régulière ne colle pas, on affiche la chaîne analysée pour nous aider
        # mais c'est un aveu d'échec, on ne doit jamais se retrouver ici
        if m == None :
            print(' Could not parse coordinates info {}'.format(wp_info['coordinates']))
            return None
        # cf. https://en.wikipedia.org/wiki/Template:Coord#Examples
        # on a récupère une chaîne comme :
        # 57|18|22|N|4|27|32|W|display=title
        # 44.112|N|87.913|W|display=title
        # 44.112|-87.913|display=title
        str_coords = m.group(1)
        # on convertit en numérique et on renvoie
        if str_coords[0:1] in '0123456789':
            return cv_coords(str_coords)
    elif 'largest_settlement' in wp_info:
        m = re.match('(?i).*{{coord\s*\|([^}]*)}}', wp_info['largest_settlement'])
        if m == None :
            print(' Could not parse coordinates info {}'.format(wp_info['largest_settlement']))
            return None
        str_coords = m.group(1)
        if str_coords[0:1] in '0123456789':
            return cv_coords(str_coords)

# import du module d'accès à la base de données
import sqlite3

# Ouverture d'une connexion avec la base de données
conn = sqlite3.connect('pays.sqlite')

# Pour initialiser la base de données, il est nécessaire d'éxécuter ce
# programme dans un premier temps. Puis, en ouvrant la base de données depuis
# l'application DB Browser (SQLite), une table 'countries' doit être créée de
# la façon suivante :
#    CREATE TABLE `countries` (             -- la table est nommé "countries"
#    	`wp`	TEXT NOT NULL UNIQUE,       -- nom de la page wikipédia, non nul, unique
#    	`name`	TEXT,                       -- nom complet du pays
#    	`capital`	TEXT,                   -- nom de la capitale
#    	`latitude`	REAL,                   -- latitude, champ numérique à valeur décimale
#    	`longitude`	REAL,                   -- longitude, champ numérique à valeur décimale
#    	PRIMARY KEY(`wp`)                   -- wp est la clé primaire
#    );
# Puis, et seulement ensuite, le programme "Python_DB_INIT_partie_2.py" doit
# être éxécuté pour finaliser l'initialisation de la base de données.