# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 11:10:49 2020

@author: Quentin
"""

import sqlite3

# Récupération des pays contenus dans la base
def db_get_countries():
    # préparation de la requête SQL :
    c = conn.cursor()
    sql = 'SELECT wp from countries'
    # récupération de l'information (ou pas) :
    c.execute(sql)
    return c.fetchall()

# Ouverture d'une connexion avec la base de données :
conn = sqlite3.connect('pays.sqlite')

dico = {}
dico_bis = {"Georgia" : '0',
            "Republic of Moldova" : '0',
            "Ireland" : '0',
            "Russian Federation" : '0'} # cas particuliers
            
r = db_get_countries()
for a in r :
    dico[a[0]] = '0'

with open("WPP2019_TotalPopulationBySex.csv","r") as f :
    
    head = f.readline().strip().split(",")
    
    location = 0
    while head[location] != "Location" :
        location = location + 1
        
    time = 0
    while head[time] != "Time" :
        time = time + 1
        
    poptotal = 0
    while head[poptotal] != "PopTotal" :
        poptotal = poptotal + 1
        
    rows = f.readlines()
    for row in rows :
        row = row.strip().split(",")
        if row[location] in dico and row[time] == '2019' :
            dico[row[location]] = row[poptotal]
        if row[location] in dico_bis and row[time] == '2019' :
            dico_bis[row[location]] = row[poptotal]

# Post-traitement :
dico["Georgia (country)"] = dico_bis["Georgia"]
dico["Moldova"] = dico_bis["Republic of Moldova"]
dico["Republic of Ireland"] = dico_bis["Ireland"]
dico["Russia"] = dico_bis["Russian Federation"]
for country in dico : # conversion en entier
    dico[country] = int(1000*float(dico[country]))

# Cas très particuliers :
dico["Kosovo"] = 1810463 # Wikipedia
dico["Vatican City"] = 825 # Wikipedia
