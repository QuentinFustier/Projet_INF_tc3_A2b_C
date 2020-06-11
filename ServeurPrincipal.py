# TD5-s1.py

# Localisation des points d'intérêts

# Application exemple : affichage de mes lieux préférés à la Croix-Rousse 2018-10-24

import http.server
import socketserver
import sqlite3
from urllib.parse import urlparse, parse_qs, unquote
import json

# définition du handler
class RequestHandler(http.server.SimpleHTTPRequestHandler):

    # sous-répertoire racine des documents statiques
    static_dir = '/client'

    # version du serveur
    server_version = 'TD3-lieux-insolites.py/0.1'

    # on surcharge la méthode qui traite les requêtes GET
    def do_GET(self):
        # on récupère les paramètres
        self.init_params()

        # le chemin d'accès commence par /time
        if self.path.startswith('/time'):
            self.send_time()

        # le chemin d'accès commence par /countries
        elif self.path.startswith('/countries'):
            self.send_countries()        

        # le chemin d'accès commence par /country et se poursuit par un nom de pays
        elif self.path_info[0] == 'country' and len(self.path_info) > 1:
            self.send_country(self.path_info[1])    
        
        # requete location - retourne la liste de lieux et leurs coordonnées géographiques
        elif self.path_info[0] == "location":
#            data=[{'id':1,'lat':45.76843,'lon':4.82667,'name':"Rue Couverte"},
#                {'id':2,'lat':45.77128,'lon':4.83251,'name':"Rue Caponi"},
#                {'id':3,'lat':45.78061,'lon':4.83196,'name':"Jardin Rosa-Mir"}]
            data = self.liste_coords()
            self.send_json(data)

        # requete description - retourne la description du lieu dont on passe l'id en paramètre dans l'URL
        elif self.path_info[0] == "description":
#            data=[{'id':1,'desc':"Il ne faut pas être <b>trop grand</b> pour marcher dans cette rue qui passe sous une maison"},
#                {'id':2,'desc':"Cette rue est <b>si étroite</b> qu'on touche les 2 côtés en tendant les bras !"},
#                {'id':3,'desc':"Ce jardin <b>méconnu</b> évoque le palais idéal du Facteur Cheval"}]
            data = self.liste_description()
            for c in data:
                if c['id'] == int(self.path_info[1]):
                    self.send_json(c)
                    break

        # le chemin d'accès commence par /service/country/...
        elif self.path_info[0] == 'service' and self.path_info[1] == 'country' and len(self.path_info) > 2:
            self.send_json_country(self.path_info[2])
#        # requête générique
#        elif self.path_info[0] == "service":
#            self.send_html('<p>Path info : <code>{}</p><p>Chaîne de requête : <code>{}</code></p>' \
#              .format('/'.join(self.path_info),self.query_string));

        # ou pas...
        else:
            self.send_static()

    # méthode pour traiter les requêtes HEAD
    def do_HEAD(self):
        self.send_static()


    # méthode pour traiter les requêtes POST - non utilisée dans l'exemple
    def do_POST(self):
        self.init_params()

        # requête générique
        if self.path_info[0] == "service":
            self.send_html(('<p>Path info : <code>{}</code></p><p>Chaîne de requête : <code>{}</code></p>' \
              + '<p>Corps :</p><pre>{}</pre>').format('/'.join(self.path_info),self.query_string,self.body));

        else:
            self.send_error(405)

    #
    # On envoie un document avec l'heure
    #
    def send_time(self):

        # on récupère l'heure
        time = self.date_time_string()

        # on génère un document au format html
        body = '<!doctype html>' + \
               '<meta charset="utf-8">' + \
               '<title>l\'heure</title>' + \
               '<div>Voici l\'heure du serveur :</div>' + \
               '<pre>{}</pre>'.format(time)

        # pour prévenir qu'il s'agit d'une ressource au format html
        headers = [('Content-Type','text/html;charset=utf-8')]

        # on envoie
        self.send(body,headers)

    #
    # On renvoie la liste des pays
    #
    def send_countries(self):

        # création d'un curseur (conn est globale)
        c = conn.cursor()

        # récupération de la liste des pays dans la base
        c.execute("SELECT name FROM countries")
        r = c.fetchall()

        # construction de la réponse
        txt = 'List of all {} countries :\n'.format(len(r))
        n = 0
        for a in r:
            n += 1
            txt = txt + '[{}] - {}\n'.format(n,a[0])

        # envoi de la réponse
        headers = [('Content-Type','text/plain;charset=utf-8')]
        self.send(txt,headers)

    # on envoie le document statique demandé
    def send_static(self):

        # on modifie le chemin d'accès en insérant le répertoire préfixe
        self.path = self.static_dir + self.path

        # on appelle la méthode parent (do_GET ou do_HEAD)
        # à partir du verbe HTTP (GET ou HEAD)
        if (self.command=='HEAD'):
            http.server.SimpleHTTPRequestHandler.do_HEAD(self)
        else:
            http.server.SimpleHTTPRequestHandler.do_GET(self)

    # on envoie un document html dynamique
    def send_html(self,content):
        headers = [('Content-Type','text/html;charset=utf-8')]
        html = '<!DOCTYPE html><title>{}</title><meta charset="utf-8">{}' \
         .format(self.path_info[0],content)
        self.send(html,headers)

    # on envoie un contenu encodé en json
    def send_json(self,data,headers=[]):
        body = bytes(json.dumps(data),'utf-8') # encodage en json et UTF-8
        self.send_response(200)
        self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',int(len(body)))
        [self.send_header(*t) for t in headers]
        self.end_headers()
        self.wfile.write(body) 

    #
    # On renvoie les informations d'un pays
    #
    def send_country(self,country):

        # on récupère le pays depuis la base de données
        r = self.db_get_country(country)

        # on n'a pas trouvé le pays demandé
        if r == None:
            self.send_error(404,'Country not found')

        # on génère un document au format html
        else:
#            body = '<!DOCTYPE html>\n<meta charset="utf-8">\n'
#            body += '<title>{}</title>'.format(country)
#            body += '<link rel="stylesheet" href="/TD2-s8.css">'
#            body += '<main>'
            body = '<div class="fiche-pays">'
            body += '<link rel="stylesheet" href="/TD2-s8.css">'
            body += '<h1>{}</h1>'.format(r['name'])
            body += '<ul>'
            body += '<li>{}: {}</li>'.format('Continent',r['continent'].capitalize())
            body += '<li>{}: {}</li>'.format('Capital',r['capital'])
            body += '<li>{}: {:.3f}</li>'.format('Latitude',r['latitude'])
            body += '<li>{}: {:.3f}</li>'.format('Longitude',r['longitude'])
            body += '</ul>'
            body += '</div>'
#            body += '</main>'

            # on envoie la réponse
            headers = [('Content-Type','text/html;charset=utf-8')]
            self.send(body,headers)

    #
    # On renvoie les informations d'un pays au format json
    #
    def send_json_country(self,country):

        # on récupère le pays depuis la base de données
        r = self.db_get_country(country)

        # on n'a pas trouvé le pays demandé
        if r == None:
            self.send_error(404,'Country not found')

        # on renvoie un dictionnaire au format JSON
        else:
            data = {k:r[k] for k in r.keys()}
            json_data = json.dumps(data, indent=4)
            headers = [('Content-Type','application/json')]
            self.send(json_data,headers)

    #
    # Récupération d'un pays dans la base
    #
    def db_get_country(self,country):
        # préparation de la requête SQL
        c = conn.cursor()
        sql = 'SELECT * from countries WHERE wp=?'

        # récupération de l'information (ou pas)
        c.execute(sql,(country,))
        return c.fetchone()
        
    #
    # On envoie les entêtes et le corps fourni
    #
    def send(self,body,headers=[]):

        # on encode la chaine de caractères à envoyer
        encoded = bytes(body, 'UTF-8')

        self.send_raw(encoded,headers)

    def send_raw(self,data,headers=[]):
        # on envoie la ligne de statut
        self.send_response(200)

        # on envoie les lignes d'entête et la ligne vide
        [self.send_header(*t) for t in headers]
        self.send_header('Content-Length',int(len(data)))
        self.end_headers()

        # on envoie le corps de la réponse
        self.wfile.write(data)

    # on analyse la requête pour initialiser nos paramètres
    def init_params(self):
        # analyse de l'adresse
        info = urlparse(self.path)
        self.path_info = [unquote(v) for v in info.path.split('/')[1:]]  # info.path.split('/')[1:]
        self.query_string = info.query
        self.params = parse_qs(info.query)

        # récupération du corps
        length = self.headers.get('Content-Length')
        ctype = self.headers.get('Content-Type')
        if length:
            self.body = str(self.rfile.read(int(length)),'utf-8')
            if ctype == 'application/x-www-form-urlencoded' : 
                self.params = parse_qs(self.body)
        else:
            self.body = ''

        # traces
        print('info_path =',self.path_info)
        print('body =',length,ctype,self.body)
        print('params =', self.params)
        
    # on renvoie une liste de dictionnaires des coordonnées géographiques
    def liste_coords(self) :

        # création d'un curseur (conn est globale)
        c = conn.cursor()

        # récupération de la liste des pays dans la base
        c.execute("SELECT latitude, longitude, wp FROM countries")
        r = c.fetchall()

        # initialisation de la liste des dictionnaires
        data = []
        
        # construction de chaque dictionnaire
        n = 0
        for a in r:
            n += 1
            data.append({'id':n,'lat':a[0],'lon':a[1],'name':a[2]})
        
        return data

    # on renvoie une liste de dictionnaires des capitales
    def liste_description(self) :

        # création d'un curseur (conn est globale)
        c = conn.cursor()

        # récupération de la liste des pays dans la base
        c.execute("SELECT capital FROM countries")
        r = c.fetchall()

        # initialisation de la liste des dictionnaires
        data = []
        
        # construction de chaque dictionnaire
        n = 0
        for a in r:
            n += 1
            data.append({'id':n,'desc':"Capitale : " + a[0]})
        
        return data
    
#
# Ouverture d'une connexion avec la base de données
#
conn = sqlite3.connect('pays.sqlite')
# Pour accéder au résultat des requêtes sous forme d'un dictionnaire
conn.row_factory = sqlite3.Row
# instanciation et lancement du serveur
httpd = socketserver.TCPServer(("", 8081), RequestHandler)
httpd.serve_forever()