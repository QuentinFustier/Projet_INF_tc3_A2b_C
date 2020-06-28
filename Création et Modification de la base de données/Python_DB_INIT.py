# Il est important que le dossier compressé .zip "europe" permettant d'extraire
# les données sur les pays européens soit situé dans le même répertoire que ce
# programme Python. La base de données sera alors créée dans ce même répertoire.

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
        if capital == 'de jure' : # exception pour la Suisse
            capital = 'Bern'
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

# Initialisation de la base de données
c = conn.cursor()
sql = "CREATE TABLE countries (wp TEXT NOT NULL UNIQUE, name TEXT, capital TEXT, latitude REAL, longitude REAL, PRIMARY KEY(wp));"
c.execute(sql)
conn.commit()


def save_country(conn,country,info) :
    # on remplace les "_" par des " "
    wp = country.replace('_',' ')
#    m = re.search(r"(?P<wp>\D+) \(country\)",wp)
#    if m != None :
#        wp = m.group('wp')
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
            # infobox de l'un des pays
            info = json.loads(z.read(f))
            save_country(conn,country,info)

init_db('europe')

# Ajout du champ 'continent'
c = conn.cursor()
sql = "ALTER TABLE countries ADD continent TEXT"
c.execute(sql)
conn.commit()

# Mise à jour du continent d'un pays dans la base de données 
def update_country_continent(conn,country,continent):
    # préparation de la commande SQL
    c = conn.cursor()
    sql = 'UPDATE countries SET continent=? WHERE wp=?'
    # soumission de la commande (noter que le second argument est un tuple)
    c.execute(sql,(continent,country))
    conn.commit()

c = conn.cursor()
sql = 'SELECT wp FROM countries'
c.execute(sql)
r = c.fetchall()
for country in r :
    update_country_continent(conn,country[0],'Europe')
    
    
  # Ajout du champ 'leader_title'
c = conn.cursor()
sql = "ALTER TABLE countries ADD leader_title TEXT"
c.execute(sql)
conn.commit()

# Ajout du champ 'leader_name'
c = conn.cursor()
sql = "ALTER TABLE countries ADD leader_name TEXT"
c.execute(sql)
conn.commit()

# Récupération du titre du dirigeant d'un pays
def get_leader_title(wp_info):
    if "leader_title1" in wp_info:
        leader_title = wp_info['leader_title1']
        m = re.match(".*?\[\[([\w\s',.()|-]+)\]\]", leader_title) 
        if m != None :
            leader_title = m.group(1)
            m_bis = re.search(r"(?P<title1>\D+)\|(?P<title2>\D+)",leader_title)
            if m_bis!= None :
                leader_title = m_bis.group('title1')
        
        # Cas particulier : Germany
        if "Germany" in leader_title :
            leader_title = wp_info['leader_title2']
            m = re.match(".*?\[\[([\w\s',.()|-]+)\]\]", leader_title) 
            if m != None :
                leader_title = m.group(1)
                m_bis = re.search(r"(?P<title1>\D+)\|(?P<title2>\D+)",leader_title)
                if m_bis!= None :
                    leader_title = m_bis.group('title1')
            leader_title = leader_title.split('(')[0].strip(' ')
        return leader_title
    # Aveu d'échec, on ne doit jamais se retrouver ici
    return None
    

def leader_title_db(continent):
    with ZipFile('{}.zip'.format(continent),'r') as z:
        # liste des documents contenus dans le fichier zip
        files = z.namelist()
        for f in files:
            country = f.split('.')[0]
            # on remplace les "_" par des " "
            wp = country.replace('_',' ')
#            m = re.search(r"(?P<wp>\D+) \(country\)",wp)
#            if m != None :
#                wp = m.group('wp')
            # infobox de l'un des pays
            info = json.loads(z.read(f))
            save_leader_title(conn,wp,info)
            
def save_leader_title(conn,wp,info):
    # préparation de la commande SQL
    c = conn.cursor()
    sql = 'UPDATE countries SET leader_title=? WHERE wp=?'
    leader_title = get_leader_title(info)
    # soumission de la commande (noter que le second argument est un tuple)
    c.execute(sql,(leader_title,wp))
    conn.commit()

# ouverture d'une connexion avec la base de données
conn = sqlite3.connect('pays.sqlite')

# Ajout des titres des dirigeants dans la base de données
leader_title_db('europe')



# Récupération du nom du dirigeant d'un pays
def get_leader_name(wp_info):
    if "leader_name1" in wp_info:
        leader_name = wp_info['leader_name1']
        
        # Cas général
        m = re.match(".*?\[\[([\w\s',.()|-]+)\]\]", leader_name)
        if m != None :
            leader_name = m.group(1)
        
        # Pour la Belgique
        m_bis = re.search(r"(?P<name1>\D+)\|(?P<name2>\D+)",leader_name)
        if m_bis!= None :
            leader_name = m_bis.group('name1')
        
        # Pour le Liechtenstein
        m_ter = re.search(r"(?P<name1>\D+)\,(?P<name2>\D+)",leader_name)
        if m_ter!= None :
            leader_name = m_ter.group('name1')
         
        # Pour l'Angleterre     
        m_qua = re.search(".*?\[\[(?P<name1>\D+)\&(?P<name2>\D+)\;(?P<name3>\D+)\]\]", leader_name)
        if m_qua!= None :
            leader_name = m_qua.group('name1')+m_qua.group('name3')
            
        # Pour la Suisse
        m_qui = re.search(r"(?P<name2>\D)\[\[(?P<name1>\D+)\]\] \|(?P<name3>\D+)",leader_name)
        if m_qui!= None :
            leader_name = m_qui.group('name1')
        m_qui2 = re.search(r"(?P<name1>\D+)\]\] \|(?P<name3>\D+)",leader_name)
        if m_qui2!= None :
            leader_name = m_qui2.group('name1')   
            
        # Pour la Slovénie 
        m_six = re.search(r"\{\{(?P<name1>\D+)\}\}",leader_name)
        if m_six!= None :
            leader_name = wp_info['leader_name2']
            m_six2 = re.match(".*?\[\[([\w\s',.()|-]+)\]\]", leader_name)
            if m_six2 != None :
                leader_name = m_six2.group(1)
            
        # Pour l'Allemagne
        if wp_info['common_name']=="Germany":
            leader_name = wp_info['leader_name2']
            m = re.match(".*?\[\[([\w\s',.()|-]+)\]\]", leader_name)
            if m != None :
                leader_name = m.group(1)
        
        return leader_name
        
    # Aveu d'échec, on ne doit jamais se retrouver ici
    return None
    

def leader_name_db(continent):
    with ZipFile('{}.zip'.format(continent),'r') as z:
        # liste des documents contenus dans le fichier zip
        files = z.namelist()
        for f in files:
            country = f.split('.')[0]
            # on remplace les "_" par des " "
            wp = country.replace('_',' ')
#            m = re.search(r"(?P<wp>\D+) \(country\)",wp)
#            if m != None :
#                wp = m.group('wp')
            # infobox de l'un des pays
            info = json.loads(z.read(f))
            save_leader_name(conn,wp,info)
            
def save_leader_name(conn,wp,info):
    # préparation de la commande SQL
    c = conn.cursor()
    sql = 'UPDATE countries SET leader_name=? WHERE wp=?'
    leader_name = get_leader_name(info)
    # soumission de la commande (noter que le second argument est un tuple)
    c.execute(sql,(leader_name,wp))
    conn.commit()

# ouverture d'une connexion avec la base de données
conn = sqlite3.connect('pays.sqlite')

# Ajout des noms des dirigeants dans la base de données
leader_name_db('europe')




# Ajout du champ 'area_km2'
c = conn.cursor()
sql = "ALTER TABLE countries ADD area_km2 REAL"
c.execute(sql)
conn.commit()



def get_area_km2(wp_info):
    if "area_km2" in wp_info:
        area_km2 = wp_info['area_km2']
        area_km2 = area_km2.replace(',','')
        #print(area_km2)
        return area_km2
    # Aveu d'échec, on ne doit jamais se retrouver ici
    return None
    

def area_km2_db(continent):
    with ZipFile('{}.zip'.format(continent),'r') as z:
        # liste des documents contenus dans le fichier zip
        files = z.namelist()
        for f in files:
            country = f.split('.')[0]
            # on remplace les "_" par des " "
            wp = country.replace('_',' ')
#            m = re.search(r"(?P<wp>\D+) \(country\)",wp)
#            if m != None :
#                wp = m.group('wp')
            # infobox de l'un des pays
            info = json.loads(z.read(f))
            save_area_km2(conn,wp,info)
            
def save_area_km2(conn,wp,info):
    # préparation de la commande SQL
    c = conn.cursor()
    sql = 'UPDATE countries SET area_km2=? WHERE wp=?'
    area_km2 = get_area_km2(info)
    # soumission de la commande (noter que le second argument est un tuple)
    c.execute(sql,(area_km2,wp))
    conn.commit()

# ouverture d'une connexion avec la base de données
conn = sqlite3.connect('pays.sqlite')

# Ajout de la surface des pays dans la base de données
area_km2_db('europe')



# Ajout du champ 'percent_water'
c = conn.cursor()
sql = "ALTER TABLE countries ADD percent_water REAL"
c.execute(sql)
conn.commit()


def get_percent_water(wp_info):
    if "percent_water" in wp_info:
        percent_water= wp_info['percent_water']
        percent_water = percent_water.replace(' ','')
        m_bis = re.search(r"(?P<name1>\d+)\.(?P<name3>\d+)(?P<name2>\D+)",percent_water)
        
        if m_bis!= None :
            percent_water = m_bis.group('name1')+'.'+m_bis.group('name3')
            
        
        percent_water = percent_water.replace('%','')
        m = re.search(r"(?P<name1>\d+)\&(?P<name2>\D+)",percent_water)
        if m!= None :
            percent_water = m.group('name1')
        
        m3 = re.search(r"negligible",percent_water)
        if m3!= None :
            percent_water = '0.0'
             
        
        return percent_water
    # Aveu d'échec, on ne doit jamais se retrouver ici
    return None
    

def percent_water_db(continent):
    with ZipFile('{}.zip'.format(continent),'r') as z:
        # liste des documents contenus dans le fichier zip
        files = z.namelist()
        for f in files:
            country = f.split('.')[0]
            # on remplace les "_" par des " "
            wp = country.replace('_',' ')
#            m = re.search(r"(?P<wp>\D+) \(country\)",wp)
#            if m != None :
#                wp = m.group('wp')
            # infobox de l'un des pays
            info = json.loads(z.read(f))
            save_percent_water(conn,wp,info)
            
def save_percent_water(conn,wp,info):
    # préparation de la commande SQL
    c = conn.cursor()
    sql = 'UPDATE countries SET percent_water=? WHERE wp=?'
    percent_water = get_percent_water(info)
    # soumission de la commande (noter que le second argument est un tuple)
    c.execute(sql,(percent_water,wp))
    conn.commit()

# ouverture d'une connexion avec la base de données
conn = sqlite3.connect('pays.sqlite')

# Ajout du pourcentage d'eau dans la base de données
percent_water_db('europe')






# Ajout du champ 'currency'
c = conn.cursor()
sql = "ALTER TABLE countries ADD currency TEXT"
c.execute(sql)
conn.commit()

def get_currency(wp_info):
    if "currency" in wp_info:
        currency = wp_info['currency']
        
        m = re.match(".*?\[\[([\w\s',.()|-]+)\]\]", currency)
        if m != None :
            currency = m.group(1)
        m_bis = re.search(r"(?P<title1>\D+)\|(?P<title2>\D+)",currency)
        if m_bis!= None :
            currency = m_bis.group('title1')
        
        m2 = re.search(r"(?P<name1>\D+)\[\[(?P<name2>\D+)\]\](?P<name3>\D+)",currency)
        if m2!= None :
            currency = m2.group('name2')
        
        m3 = re.search(r"(?P<name1>\D+)\((?P<name2>\D+)",currency)
        if m3!= None :
            currency = m3.group('name1')
        
        m4 = re.search(r"(?P<name1>\D+)\;(?P<name2>\D+)\]\]",currency)
        if m4!= None :
            currency = m4.group('name2')
        
        
        return currency
    # Aveu d'échec, on ne doit jamais se retrouver ici
    return None
    

def currency_db(continent):
    with ZipFile('{}.zip'.format(continent),'r') as z:
        # liste des documents contenus dans le fichier zip
        files = z.namelist()
        for f in files:
            country = f.split('.')[0]
            # on remplace les "_" par des " "
            wp = country.replace('_',' ')
#            m = re.search(r"(?P<wp>\D+) \(country\)",wp)
#            if m != None :
#                wp = m.group('wp')
            # infobox de l'un des pays
            info = json.loads(z.read(f))
            save_currency(conn,wp,info)
            
def save_currency(conn,wp,info):
    # préparation de la commande SQL
    c = conn.cursor()
    sql = 'UPDATE countries SET currency=? WHERE wp=?'
    currency = get_currency(info)
    # soumission de la commande (noter que le second argument est un tuple)
    c.execute(sql,(currency,wp))
    conn.commit()

# ouverture d'une connexion avec la base de données
conn = sqlite3.connect('pays.sqlite')

# Ajout des titres des dirigeants dans la base de données
currency_db('europe')





# Ajout du champ 'GDP_PPP_per_capita'
c = conn.cursor()
sql = "ALTER TABLE countries ADD GDP_PPP_per_capita REAL"
c.execute(sql)
conn.commit()

def get_GDP_PPP_per_capita(wp_info):
    if "GDP_PPP_per_capita" in wp_info:
        GDP_PPP_per_capita = wp_info['GDP_PPP_per_capita']
        
        GDP_PPP_per_capita = GDP_PPP_per_capita.replace(',','')
        
        m_bis = re.search(r"(?P<title1>\D*)\$(?P<title2>\d+)(?P<title3>\D*)",GDP_PPP_per_capita)
        if m_bis!= None :
            GDP_PPP_per_capita = m_bis.group('title2')
        
        return GDP_PPP_per_capita
    
    elif "GDP_nominal_per_capita" in wp_info:
        GDP_PPP_per_capita = wp_info['GDP_nominal_per_capita']
        
        GDP_PPP_per_capita = GDP_PPP_per_capita.replace(',','')
        
        m_bis = re.search(r"(?P<title1>\D*)\$(?P<title2>\d+)(?P<title3>\D*)",GDP_PPP_per_capita)
        if m_bis!= None :
            GDP_PPP_per_capita = m_bis.group('title2')
        
        #print(GDP_PPP_per_capita)
        return GDP_PPP_per_capita
    # Aveu d'échec, on ne doit jamais se retrouver ici
    return None
    

def GDP_PPP_per_capita_db(continent):
    with ZipFile('{}.zip'.format(continent),'r') as z:
        # liste des documents contenus dans le fichier zip
        files = z.namelist()
        for f in files:
            country = f.split('.')[0]
            # on remplace les "_" par des " "
            wp = country.replace('_',' ')
#            m = re.search(r"(?P<wp>\D+) \(country\)",wp)
#            if m != None :
#                wp = m.group('wp')
            # infobox de l'un des pays
            info = json.loads(z.read(f))
            save_GDP_PPP_per_capita(conn,wp,info)
            
def save_GDP_PPP_per_capita(conn,wp,info):
    # préparation de la commande SQL
    c = conn.cursor()
    sql = 'UPDATE countries SET GDP_PPP_per_capita=? WHERE wp=?'
    GDP_PPP_per_capita = get_GDP_PPP_per_capita(info)
    # soumission de la commande (noter que le second argument est un tuple)
    c.execute(sql,(GDP_PPP_per_capita,wp))
    conn.commit()

# ouverture d'une connexion avec la base de données
conn = sqlite3.connect('pays.sqlite')

# Ajout des titres des dirigeants dans la base de données
GDP_PPP_per_capita_db('europe')



# Ajout du champ 'population_estimate'
c = conn.cursor()
sql = "ALTER TABLE countries ADD population_estimate INTEGER"
c.execute(sql)
conn.commit()

def get_population_estimate(wp_info):
    
    
    if "population_estimate" in wp_info:
        population_estimate = wp_info['population_estimate']
        population_estimate = population_estimate.replace(',','')
        
        m_bis = re.search(r"(?P<title1>\D*)(?P<title2>\d+)",population_estimate)
        if m_bis!= None :
            population_estimate = m_bis.group('title2')
            
            return population_estimate
        
        elif "population_census" in wp_info :
            population_estimate = wp_info['population_census']
            population_estimate = population_estimate.replace(',','')
            m = re.search('(?P<title1>\D*)(?P<title2>\d+)(?P<title3>\D*)', population_estimate)
            if m!= None :
                population_estimate = m.group('title2')
        
                return population_estimate
    
    
    if "population_census" in wp_info:
        population_estimate = wp_info['population_census']
        population_estimate = population_estimate.replace(',','')
    
        m = re.search('(?P<title1>\D*)(?P<title2>\d+)(?P<title3>\D*)', population_estimate)
        if m!= None :
            population_estimate = m.group('title2')
        
        return population_estimate
    
    # Aveu d'échec, on ne doit jamais se retrouver ici
    return None
    

def population_estimate_db(continent):
    with ZipFile('{}.zip'.format(continent),'r') as z:
        # liste des documents contenus dans le fichier zip
        files = z.namelist()
        for f in files:
            country = f.split('.')[0]
            # on remplace les "_" par des " "
            wp = country.replace('_',' ')
#            m = re.search(r"(?P<wp>\D+) \(country\)",wp)
#            if m != None :
#                wp = m.group('wp')
            # infobox de l'un des pays
            info = json.loads(z.read(f))
            save_population_estimate(conn,wp,info)
            
def save_population_estimate(conn,wp,info):
    # préparation de la commande SQL
    c = conn.cursor()
    sql = 'UPDATE countries SET population_estimate=? WHERE wp=?'
    population_estimate = get_population_estimate(info)
    # soumission de la commande (noter que le second argument est un tuple)
    c.execute(sql,(population_estimate,wp))
    conn.commit()

# ouverture d'une connexion avec la base de données
conn = sqlite3.connect('pays.sqlite')

# Ajout des titres des dirigeants dans la base de données
population_estimate_db('europe')






dico_anthem = {
        "Albania":"https://upload.wikimedia.org/wikipedia/commons/5/52/Hymni_i_Flamurit_instrumental.ogg",
        "Andorra":"https://upload.wikimedia.org/wikipedia/commons/5/5b/El_Gran_Carlemany.ogg",
        "Armenia":"https://upload.wikimedia.org/wikipedia/commons/c/c7/Mer_Hayrenik_instrumental.ogg",
        "Austria":"https://upload.wikimedia.org/wikipedia/commons/7/7c/Land_der_Berge_Land_am_Strome_instrumental.ogg",
        "Azerbaijan":"https://upload.wikimedia.org/wikipedia/commons/5/5d/Az%C9%99rbaycan_mar%C5%9F%C4%B1_instrumental.ogg",
        "Belarus":"https://upload.wikimedia.org/wikipedia/commons/f/f6/Belarusian_national_anthem%2C_performed_by_the_United_States_Navy_Band.mp3",
        "Belgium":"https://upload.wikimedia.org/wikipedia/commons/e/e8/La_Braban%C3%A7onne.oga",
        "Bosnia and Herzegovina":"https://upload.wikimedia.org/wikipedia/en/d/dd/Bosnia_and_Herzegovina%27s_national_anthem.ogg",
        "Bulgaria":"https://upload.wikimedia.org/wikipedia/commons/4/4f/Mila_Rodino_instrumental.ogg",
        "Croatia":"https://upload.wikimedia.org/wikipedia/commons/d/df/Lijepa_nasa_domovino_instrumental.ogg",
        "Cyprus":"https://upload.wikimedia.org/wikipedia/commons/d/db/Hymn_to_liberty_instrumental.oga",
        "Czechia":"https://upload.wikimedia.org/wikipedia/commons/6/6e/Czech_anthem.ogg",
        "Denmark":"https://upload.wikimedia.org/wikipedia/commons/0/06/United_States_Navy_Band_-_Der_er_et_yndigt_land.ogg",
        "Estonia":"https://upload.wikimedia.org/wikipedia/commons/5/52/US_Navy_band_-_National_anthem_of_Estonia.ogg",
        "Finland":"https://upload.wikimedia.org/wikipedia/commons/6/61/United_States_Navy_Band_-_Maamme.ogg",
        "France":"https://upload.wikimedia.org/wikipedia/commons/3/30/La_Marseillaise.ogg",
        "Georgia (country)":"https://upload.wikimedia.org/wikipedia/commons/b/b6/Georgian_national_anthem.oga",
        "Germany":"https://upload.wikimedia.org/wikipedia/commons/a/a6/German_national_anthem_performed_by_the_US_Navy_Band.ogg",
        "Greece":"https://upload.wikimedia.org/wikipedia/commons/d/db/Hymn_to_liberty_instrumental.oga",
        "Hungary":"https://upload.wikimedia.org/wikipedia/commons/7/79/Hungarian_national_anthem%2C_performed_by_the_United_States_Navy_Band_%281997_arrangement%29.mp3",
        "Iceland":"https://upload.wikimedia.org/wikipedia/commons/4/4b/Lofs%C3%B6ngur.ogg",
        "Republic of Ireland":"https://upload.wikimedia.org/wikipedia/commons/7/7c/United_States_Navy_Band_-_Amhr%C3%A1n_na_bhFiann.ogg",
        "Italy":"https://upload.wikimedia.org/wikipedia/commons/c/c0/National_anthem_of_Italy_-_U.S._Navy_Band_%28long_version%29.ogg",
        "Kazakhstan":"https://upload.wikimedia.org/wikipedia/commons/d/d9/Kazakhstan_%28instrumental%29.oga",
        "Kosovo":"https://upload.wikimedia.org/wikipedia/commons/0/0a/National_Anthem_of_the_Republic_of_Kosovo.ogg",
        "Latvia":"https://upload.wikimedia.org/wikipedia/commons/5/55/Latvian_National_Anthem.ogg",
        "Liechtenstein":"https://upload.wikimedia.org/wikipedia/commons/6/61/Oben_am_jungen_Rhein%2C_by_the_U.S._Navy_Band.ogg",
        "Lithuania":"https://upload.wikimedia.org/wikipedia/commons/c/ca/Tauti%C5%A1ka_giesme_instumental.ogg",
        "Luxembourg":"https://upload.wikimedia.org/wikipedia/commons/f/f6/Ons_Heemecht.ogg",
        "Malta":"https://upload.wikimedia.org/wikipedia/commons/8/80/Malta_anthem_%28instrumental%29.ogg",
        "Moldova":"https://upload.wikimedia.org/wikipedia/commons/a/ad/Imnul_Republicii_Moldova_US_NAVY.ogg",
        "Monaco":"https://upload.wikimedia.org/wikipedia/commons/c/c2/Monaco_National_Anthem.ogg",
        "Montenegro":"https://upload.wikimedia.org/wikipedia/commons/a/a2/National_Anthem_of_Montenegro.ogg",
        "Netherlands":"https://upload.wikimedia.org/wikipedia/commons/2/2e/United_States_Navy_Band_-_Het_Wilhelmus.ogg",
        "North Macedonia":"https://upload.wikimedia.org/wikipedia/en/b/b6/North_Macedonia%27s_national_anthem_%28instrumental%29.ogg",
        "Norway":"https://upload.wikimedia.org/wikipedia/commons/f/f6/Norway_%28National_Anthem%29.ogg",
        "Poland":"https://upload.wikimedia.org/wikipedia/commons/b/b1/Mazurek_Dabrowskiego.ogg",
        "Portugal":"https://upload.wikimedia.org/wikipedia/commons/5/58/A_Portuguesa.ogg",
        "Romania":"https://upload.wikimedia.org/wikipedia/commons/7/77/Desteapta-te%2C_romane%21.ogg",
        "Russia":"https://upload.wikimedia.org/wikipedia/commons/4/41/National_Anthem_of_Russia_%282000%29%2C_instrumental%2C_one_verse.ogg",
        "San Marino":"https://upload.wikimedia.org/wikipedia/commons/d/d9/Inno_Nazionale_della_Repubblica.ogg",
        "Serbia":"https://upload.wikimedia.org/wikipedia/commons/8/8e/Serbian_national_anthem%2C_instrumental.oga",
        "Slovakia":"https://upload.wikimedia.org/wikipedia/commons/e/e8/Nad_Tatrou_sa_bl%C3%BDska.ogg",
        "Slovenia":"https://upload.wikimedia.org/wikipedia/commons/3/30/Slovenia%27s_national_anthem%2C_performed_by_the_United_States_Navy_Band.oga",
        "Spain":"https://upload.wikimedia.org/wikipedia/commons/c/c8/Marcha_Real-Royal_March_by_US_Navy_Band.ogg",
        "Sweden":"https://upload.wikimedia.org/wikipedia/commons/0/02/United_States_Navy_Band_-_Sweden.ogg",
        "Switzerland":"https://upload.wikimedia.org/wikipedia/commons/0/00/Swiss_Psalm.ogg",
        "Turkey":"https://upload.wikimedia.org/wikipedia/commons/5/50/IstiklalMarsi-2013.ogg",
        "Ukraine":"https://upload.wikimedia.org/wikipedia/commons/6/6d/National_anthem_of_Ukraine%2C_instrumental.oga",
        "United Kingdom":"https://upload.wikimedia.org/wikipedia/commons/d/de/United_States_Navy_Band_-_God_Save_the_Queen.ogg",
        "Vatican City":"https://upload.wikimedia.org/wikipedia/commons/d/d1/United_States_Navy_Band_-_Inno_e_Marcia_Pontificale.ogg"}

def anthem_db(conn,dico):
    
    # préparation de la requête SQL :
    c = conn.cursor()
    sql = 'SELECT wp from countries'

    # récupération de l'information (ou pas) :
    c.execute(sql)
    r = c.fetchall()
    for country in r:
        wp = country[0]
        # préparation de la commande SQL
        c = conn.cursor()
        sql = 'UPDATE countries SET anthem=? WHERE wp=?'
        anthem = dico[wp]
        c.execute(sql,(anthem,wp))
        conn.commit()        

# ouverture d'une connexion avec la base de données
conn = sqlite3.connect('pays.sqlite')

# Ajout du champ 'anthem'
c = conn.cursor()
sql = "ALTER TABLE countries ADD anthem TEXT"
c.execute(sql)
conn.commit()

# Ajout des hymnes dans la base de données
anthem_db(conn,dico_anthem)
