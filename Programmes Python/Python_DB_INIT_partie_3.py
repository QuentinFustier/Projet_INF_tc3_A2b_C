# Il est important que les autres fichiers Python du type "Python_DB_INIT_partie_X.py"
# se trouvent dans le même dossier que celui-ci, au même titre que le dossier
# "europe" permettant d'extraire les données sur les pays européens. La base de
# données sera alors créée dans ce même répertoire.

# Le programme "Python_DB_INIT_partie_2.py" doit être éxécuté pour finaliser
# l'initialisation de la base de données. Par la suite, un champ nommé
# "continent" doit être ajouté dans la table "countries". Cette tâche doit être
# réalisée à l'aide de l'application DB Browser (SQLite). Puis, et seulement
# après, ce programme doit être éxécuté pour compléter ce champ "continent".

import sqlite3

# Mise à jour du continent d'un pays dans la base de données 
def update_country_continent(conn,country,continent):
    # préparation de la commande SQL
    c = conn.cursor()
    sql = 'UPDATE countries SET continent=? WHERE wp=?'
    # soumission de la commande (noter que le second argument est un tuple)
    c.execute(sql,(continent,country))
    conn.commit()

# ouverture d'une connexion avec la base de données
conn = sqlite3.connect('pays.sqlite')

c = conn.cursor()
sql = 'SELECT wp FROM countries'
c.execute(sql)
r = c.fetchall()
for country in r :
    update_country_continent(conn,country[0],'Europe')

# La base de données "pays.sqlite" est alors initialisée. Une table "countries"
# contient les champs suivants :
#   - wp
#   - name
#   - capital
#   - latitude
#   - longitude
#   - continent
# Cette base de données sera enrichies par la suite avec de nouveaux champs.