#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name : test_database.py
Author : Thierry Maillard (TMD)
Date : 30/6/2015 - 14/4/2020
Role : Tests unitaires du projet FinancesLocales avec py.test
Utilisation :
    Pour jouer les tests de ce fichier
    python3 -m pytest test_database.py
 options :
    -s : pour voir les sorties sur stdout
Ref : python3 -m pytest -h
Ref : http://sametmax.com/un-gros-guide-bien-gras-sur-les-tests-unitaires-en-python-partie-3
Ref : http://pytest.org/latest
prerequis : pip install pytest

Licence : GPLv3
Copyright (c) 2015 - Thierry Maillard

   This file is part of Finance Locales project.

   FinancesLocales project is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   FinancesLocales project is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with Finance Locales project.  If not, see <http://www.gnu.org/licenses/>.
"""
import configparser
import os.path

import pytest
import database
import sqlite3

import updateDataMinFi
import updateDataMinFiGroupementCommunes

def test_initClesMinFi():
    """
    Test fonction d'init des mots clés du ministère des finances
    pour les communes
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    listCodeCle = [list1Cles[0]
                   for list1Cles
                   in database.initClesMinFi(config, "V", True)]
    assert len(listCodeCle) == \
        (len(config['cleFi3Valeurs']) * 3 + len(config['cleFi2Valeurs']) * 2 +
         len(config['cleFi1Valeur']))
    assert config['cleFi3Valeurs']['clefi.dont charges de personnel'] in listCodeCle
    assert "f"+config['cleFi3Valeurs']['clefi.dont charges de personnel'] in listCodeCle
    assert "m"+config['cleFi3Valeurs']['clefi.dont charges de personnel'] in listCodeCle
    assert config['cleFi2Valeurs']["cletaxe.taux taxe habitation"] in listCodeCle
    assert config['cleFi2Valeurs']["cletaxe.taux taxe habitation"].replace("t", "tm", 1) in listCodeCle
    assert config['cleFi1Valeur']['clefi.codeInsee'] in listCodeCle

def test_initClesMinFiGC():
    """
    Test fonction d'init des mots clés du ministère des finances
    pour les groupements de communes
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    listCodeCle = [list1Cles[0]
                   for list1Cles
                   in database.initClesMinFi(config, "GC", True)]
    assert len(listCodeCle) == \
        (len(config['cleFi2ValeursGC']) * 2 +len(config['cleFi1ValeurGC']))
    assert config['cleFi2ValeursGC']['clefi.dont charges de personnel'] in listCodeCle
    assert config['cleFi2ValeursGC']['clefi.dont charges de personnel']+"hab" in listCodeCle
    assert config['cleFi2ValeursGC']["cletaxe.taxe habitation"] in listCodeCle
    assert "f"+config['cleFi2ValeursGC']["cletaxe.taxe habitation"] in listCodeCle
    assert config['cleFi1ValeurGC']['clefi.siren'] in listCodeCle
 
def test_initDepartements():
    """ Test fonction d'init des noms de départements """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    listeDepartements = database.initDepartements(config, True)
    assert len(listeDepartements) == 101
    assert ('046', 'Lot', 'du') in listeDepartements

def test_createMinFiTables():
    """ Test de la création des tables de la base de données """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    databasePathDir = config.get('Test', 'database.testDir')
    databasePath = os.path.join(databasePathDir, config.get('Test', 'database.testName'))
    if not os.path.isdir(databasePathDir):
        os.mkdir(databasePathDir)
    if os.path.isfile(databasePath):
        os.remove(databasePath)

    # Création base vide
    connDB = sqlite3.connect(databasePath)
    assert os.path.isfile(databasePath)
    assert connDB

    # Creation des tables
    database.createMinFiTables(connDB, True)
    
    # Test si les tables ont bien été créée
    cursor = connDB.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    listTablesRecords = cursor.fetchall()
    assert len(listTablesRecords) == 6
    listTables = [tableRecord[0] for tableRecord in listTablesRecords]
    for table in ('villes', 'clesMinFi', 'dataFi', 'departements',
                  'groupementCommunes', 'dataFiGroupement'):
        assert table in listTables

    # V4.0 : Test si la colonne ville contient bien
    #   les champs sirenGroupement et ancienneCommune
    cursor.execute("SELECT sirenGroupement, ancienneCommune FROM villes")

    # V4.0 : Test si la colonne clesMinFi contient bien un champ type
    cursor.execute("SELECT typeEntite FROM clesMinFi")

    # Fermeture base
    cursor.close()
    database.closeDatabase(connDB, True)

def test_createDatabase():
    """ Test fonction de creation de la base de données """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Recup chemin base de test et ménage
    databasePathDir = config.get('Test', 'database.testDir')
    databasePath = os.path.join(databasePathDir, config.get('Test', 'database.testName'))
    if not os.path.isdir(databasePathDir):
        os.mkdir(databasePathDir)
    if os.path.isfile(databasePath):
        os.remove(databasePath)

    # Création base vide
    print("Creation de la base :", databasePath)
    connDB = database.createDatabase(config, databasePath, False)
    assert os.path.isfile(databasePath)
    assert connDB

    # Récupère les clés existantes dans la table clesMinFi
    cursor = connDB.cursor()
    cursor.execute("""SELECT codeCle, typeEntite, nomCle, typeCle, unite
                      FROM clesMinFi""")
    values = cursor.fetchall()
    print("values in clesMinFi", values)
    # Fermeture base
    cursor.close()
    database.closeDatabase(connDB, True)

    # Enregistrements qui devraient être dans clesMinFi
    # pour les communes V et les groupements de communes GC
    listTestOk = [
        (config['cleFi3Valeurs']['clefi.dont charges de personnel'],
         "V", "dont charges de personnel",
         "Valeur totale", "En milliers d'Euros"),
        ("f"+config['cleFi3Valeurs']['clefi.dont charges de personnel'],
         "V", "dont charges de personnel par habitant",
         "Par habitant", "Euros par habitant"),
        ("m"+config['cleFi3Valeurs']['clefi.dont charges de personnel'],
         "V", "dont charges de personnel moyen",
         "En moyenne pour la strate", "En milliers d'Euros"),
        (config['cleFi2Valeurs']["cletaxe.taux taxe habitation"],
         "V", "taux taxe habitation",
         "Taux", "taux voté (%)"),
        (config['cleFi2Valeurs']["cletaxe.taux taxe habitation"].replace("t", "tm", 1),
         "V", "taux taxe habitation moyen",
         "taux moyen pour la strate", "taux moyen de la strate (%)"),
        (config['cleFi1Valeur']['clefi.codeInsee'],
         "V", "codeinsee", "Valeur simple", ""),
        (config['cleFi2ValeursGC']['clefi.dont charges de personnel'],
         "GC", "dont charges de personnel",
         "Valeur totale", "En milliers d'Euros"),
        (config['cleFi2ValeursGC']['clefi.dont charges de personnel']+"hab",
         "GC", "dont charges de personnel par habitant",
         "Par habitant", "Euros par habitant"),
        (config['cleFi2ValeursGC']["cletaxe.taxe habitation"],
         "GC", "taxe habitation",
         "Valeur totale", "En milliers d'Euros"),
        ("f"+config['cleFi2ValeursGC']["cletaxe.taxe habitation"],
         "GC", "taxe habitation par habitant",
         "Par habitant", "Euros par habitant"),
        (config['cleFi1ValeurGC']['clefi.siren'],
         "GC", "siren", "Valeur simple", ""),
        ]

    # Test
    for valuesOK in listTestOk:
        assert valuesOK in values

def test_getListCodeClesMiniFi():
    """
    Test fonction getListCodeClesMiniFide récupération
    des clés de la table clesMinFi
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Recup chemin base de test
    databasePathDir = config.get('Test', 'database.testDir')
    databasePath = os.path.join(databasePathDir, config.get('Test', 'database.testName'))
    # Création base
    connDB = database.createDatabase(config, databasePath, True)

    # Test getListCodeClesMiniFi pour les communes
    listCodeCle = database.getListCodeClesMiniFi(connDB, "V", True)
    print("listCodeCle (V)=", listCodeCle)
    assert len(listCodeCle) == \
        (len(config['cleFi3Valeurs']) * 3 + len(config['cleFi2Valeurs']) * 2 +
         len(config['cleFi1Valeur']))
    assert config['cleFi3Valeurs']['clefi.dont charges de personnel'] in listCodeCle
    assert config['cleFi2Valeurs']["cletaxe.taux taxe habitation"] in listCodeCle
    assert config['cleFi1Valeur']['clefi.codeInsee'] in listCodeCle

    # Test getListCodeClesMiniFi pour les groupements de communes
    listCodeCle = database.getListCodeClesMiniFi(connDB, "GC", True)
    print("listCodeCle (GC)=", listCodeCle)
    assert len(listCodeCle) == \
        (len(config['cleFi2ValeursGC']) * 2 +len(config['cleFi1ValeurGC']))
    assert config['cleFi2ValeursGC']['clefi.dont charges de personnel'] in listCodeCle
    assert config['cleFi2ValeursGC']["cletaxe.taxe habitation"] in listCodeCle
    assert config['cleFi1ValeurGC']['clefi.siren'] in listCodeCle

def test_enregistreLigneVilleMinFi():
    """ Test fonction d'enregistrement d'une ville dans la base """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Recup chemin base de test et ménage
    databasePathDir = config.get('Test', 'database.testDir')
    databasePath = os.path.join(databasePathDir, config.get('Test', 'database.testName'))
    if not os.path.isdir(databasePathDir):
        os.mkdir(databasePathDir)
    if os.path.isfile(databasePath):
        os.remove(databasePath)

    # Création base vide
    connDB = database.createDatabase(config, databasePath, False)

    # Création données de test
    dictValues = {}
    dictValues[config.get('cleFi1Valeur', 'clefi.codeInsee')] = "015"
    dictValues[config.get('cleFi1Valeur', 'clefi.annee')] = 2019
    dictValues[config.get('cleFi1Valeur', 'clefi.nomMinFi')] = 'Trifouilly-les-oies'
    dictValues[config.get('cleFi1Valeur', 'clefi.departement')] = "001"
    dictValues[config.get('cleFi1Valeur', 'clefi.nomStrate')] = 'strate 1'
    dictValues[config.get('cleFi1Valeur', 'clefi.population1_1')] = '500'
    dictValues[config.get('cleFi1Valeur', 'clefi.typeGroupement')] = 'FPU'
    dictValues['codeCommune'] = dictValues[config.get('cleFi1Valeur', 'clefi.departement')] + \
                                dictValues[config.get('cleFi1Valeur', 'clefi.codeInsee')]

    # Test création ville
    database.enregistreLigneVilleMinFi(config, dictValues, connDB, True)
    cursor = connDB.cursor()
    cursor.execute("""SELECT nomWkpFr, nomMinFi, numDepartement, nomStrate, population, typeGroupement
                      FROM villes WHERE codeCommune=?""",
                   (dictValues['codeCommune'],))
    values = cursor.fetchone()
    assert values is not None
    assert values[0] is None
    assert values[1] == dictValues[config.get('cleFi1Valeur', 'clefi.nomMinFi')]
    assert values[2] == dictValues[config.get('cleFi1Valeur', 'clefi.departement')]
    assert values[3] == dictValues[config.get('cleFi1Valeur', 'clefi.nomStrate')]
    assert values[4] == dictValues[config.get('cleFi1Valeur', 'clefi.population1_1')]
    assert values[5] == dictValues[config.get('cleFi1Valeur', 'clefi.typeGroupement')]
    cursor.close()

    # Modification données de test
    dictValues[config.get('cleFi1Valeur', 'clefi.annee')] = 2018
    dictValues[config.get('cleFi1Valeur', 'clefi.nomMinFi')] = 'Trifouilly-les-bains'
    dictValues[config.get('cleFi1Valeur', 'clefi.nomStrate')] = 'strate 2'
    dictValues[config.get('cleFi1Valeur', 'clefi.population1_1')] = '1500'
    dictValues[config.get('cleFi1Valeur', 'clefi.typeGroupement')] = 'FPU2'

    # Test mise à jour ville
    database.enregistreLigneVilleMinFi(config, dictValues, connDB, True)
    cursor = connDB.cursor()
    cursor.execute("""SELECT nomWkpFr, nomMinFi, numDepartement,
                          nomStrate, population, typeGroupement
                       FROM villes WHERE codeCommune=?""",
                   (dictValues['codeCommune'],))
    valuesTupple = cursor.fetchall()
    assert len(valuesTupple) == 1
    assert valuesTupple[0][0] is None
    assert valuesTupple[0][1] == dictValues[config.get('cleFi1Valeur', 'clefi.nomMinFi')]
    assert valuesTupple[0][2] == dictValues[config.get('cleFi1Valeur', 'clefi.departement')]
    assert valuesTupple[0][3] == dictValues[config.get('cleFi1Valeur', 'clefi.nomStrate')]
    assert valuesTupple[0][4] == dictValues[config.get('cleFi1Valeur', 'clefi.population1_1')]
    assert valuesTupple[0][5] == dictValues[config.get('cleFi1Valeur', 'clefi.typeGroupement')]
    cursor.close()

    # Fermeture base
    database.closeDatabase(connDB, True)

def test_enregistreLigneVilleMinFi_Pb_DuplicAnnee():
    """ Test fonction d'enregistrement d'une ville dans la base
        qui doit retourner une exception si on tente d'enregistrer 2 fois
        les valeurs pour une ville et une année """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Recup chemin base de test et ménage
    databasePathDir = config.get('Test', 'database.testDir')
    databasePath = os.path.join(databasePathDir, config.get('Test', 'database.testName'))
    if not os.path.isdir(databasePathDir):
        os.mkdir(databasePathDir)
    if os.path.isfile(databasePath):
        os.remove(databasePath)

    # Création base vide
    connDB = database.createDatabase(config, databasePath, False)

    # Création données de test
    dictValues = {}
    dictValues[config.get('cleFi1Valeur', 'clefi.codeInsee')] = '15'
    dictValues[config.get('cleFi1Valeur', 'clefi.annee')] = 2019
    dictValues[config.get('cleFi1Valeur', 'clefi.nomMinFi')] = 'Trifouilly-les-oies'
    dictValues[config.get('cleFi1Valeur', 'clefi.departement')] = '01'
    dictValues[config.get('cleFi1Valeur', 'clefi.nomStrate')] = 'strate 1'
    dictValues[config.get('cleFi1Valeur', 'clefi.population1_1')] = '500'
    dictValues[config.get('cleFi1Valeur', 'clefi.typeGroupement')] = 'FPU'
    dictValues['codeCommune'] = dictValues[config.get('cleFi1Valeur', 'clefi.departement')] + \
        dictValues[config.get('cleFi1Valeur', 'clefi.codeInsee')]

    # Création ville
    database.enregistreLigneVilleMinFi(config, dictValues, connDB, False)

    # Modification données de test
    dictValues[config.get('cleFi1Valeur', 'clefi.nomStrate')] = 'strate 3'
    with pytest.raises(ValueError,
                       match=("Erreur : Annee "
                              f"{dictValues[config.get('cleFi1Valeur','clefi.annee')]}"
                              " déjà présente")):
        database.enregistreLigneVilleMinFi(config, dictValues, connDB, True)

    # Fermeture base
    database.closeDatabase(connDB, True)

def test_getDictCodeCommuneAnnees_DB_empty():
    """
        Test récupération de toutes les villes de la base et leurs années enregistrées.
        Test sur base vide : doit retourner un dictionnaire vide
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Creation base vide
    databasePathDir = config.get('Test', 'database.testDir')
    databasePath = os.path.join(databasePathDir, config.get('Test', 'database.testName'))
    if not os.path.isdir(databasePathDir):
        os.mkdir(databasePathDir)
    if os.path.isfile(databasePath):
        os.remove(databasePath)
    connDB = database.createDatabase(config, databasePath, False)

    # Test si dico vide
    dictCodeCommuneAnnees = database.getDictCodeCommuneAnnees(connDB, True)
    assert not dictCodeCommuneAnnees

    # Fermeture base
    database.closeDatabase(connDB, True)

def test_getDictCodeCommuneAnnees_DB_2_rec():
    """
        Test récupération de toutes les villes de la base et leurs années enregistrées.
        Test sur base avec 2 enregistrements
        """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Creation base vide
    databasePathDir = config.get('Test', 'database.testDir')
    databasePath = os.path.join(databasePathDir, config.get('Test', 'database.testName'))
    if not os.path.isdir(databasePathDir):
        os.mkdir(databasePathDir)
    if os.path.isfile(databasePath):
        os.remove(databasePath)
    connDB = database.createDatabase(config, databasePath, False)

    # Ajout 1 ville sans annee
    cursor = connDB.cursor()
    cursor.execute("INSERT INTO villes(codeCommune) VALUES(?)", ('001007',))
    # Ajout 1 ville Avec 2 annee
    cursor.execute("INSERT INTO villes(codeCommune) VALUES(?)", ('001008',))
    connDB.executemany("""
        INSERT INTO dataFi(codeCommune, annee)
        VALUES (?, ?)
        """, (('001008', 2000), ('001008', 2001)))
    cursor.close()
    connDB.commit()

    # Test dico
    dictCodeCommuneAnnees = database.getDictCodeCommuneAnnees(connDB, True)
    assert dictCodeCommuneAnnees['001007'] == []
    assert dictCodeCommuneAnnees['001008'] == [2000, 2001]

    # Fermeture base
    database.closeDatabase(connDB, True)

def test_enregistreVilleWKP():
    """ Test enregistrement dans la base de données des villes """
    
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Creation base vide
    databasePathDir = config.get('Test', 'database.testDir')
    databasePath = os.path.join(databasePathDir, config.get('Test', 'database.testName'))
    if not os.path.isdir(databasePathDir):
        os.mkdir(databasePathDir)
    if os.path.isfile(databasePath):
        os.remove(databasePath)
    connDB = database.createDatabase(config, databasePath, False)
    database.closeDatabase(connDB, False)              

    # Préparation structure avec 2 villes
    listeVilles4Bd = [
        {'numDepartement':'025', 'icom':'027',
         'nomWkpFr': 'Badevel', 'nom':'Badevel', 'codeCommune':'003076'},
         {'numDepartement':'046', 'icom':'133',
         'nomWkpFr': 'Issendolus', 'nom':'Issendol', 'codeCommune':'046077'},
        ]

    # Enregistrement Bd
    database.enregistreVilleWKP(config, databasePath, listeVilles4Bd, True)

    # Test
    connDB = database.createDatabase(config, databasePath, False)
    cursor = connDB.cursor()
    cursor.execute("""SELECT numDepartement, icom, nomWkpFr, nom
                        FROM villes WHERE codeCommune=?""", ('003076',))
    listVille = cursor.fetchall()
    assert len(listVille) == 1
    assert listVille[0][0] == '025' and listVille[0][1]=='027' and \
         listVille[0][2]== 'Badevel' and  listVille[0][3] == 'Badevel'

    cursor.execute("""SELECT numDepartement, icom, nomWkpFr, nom
                        FROM villes WHERE codeCommune=?""", ('046077',))
    listVille = cursor.fetchall()
    assert len(listVille) == 1
    assert listVille[0][0] == '046' and listVille[0][1]=='133' and \
         listVille[0][2]== 'Issendolus' and  listVille[0][3] == 'Issendol'

    cursor.close()
    database.closeDatabase(connDB, False)              

def test_enregistreVilleWKP_existData():
    """ Test enregistrement dans la base de données des villes """
    
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Creation base vide
    databasePathDir = config.get('Test', 'database.testDir')
    databasePath = os.path.join(databasePathDir, config.get('Test', 'database.testName'))
    if not os.path.isdir(databasePathDir):
        os.mkdir(databasePathDir)
    if os.path.isfile(databasePath):
        os.remove(databasePath)
    connDB = database.createDatabase(config, databasePath, False)
    database.closeDatabase(connDB, False)

    # Enregistre 2 villes
    test_enregistreVilleWKP()

    # Préparation structure avec modif 1 ville existante et 1 ville nouvelle
    listeVilles4Bd = [
        {'numDepartement':'025', 'icom':'027',
         'nomWkpFr': 'Badevel (Doubs)', 'nom':'Badevel', 'codeCommune':'003076'},
         {'numDepartement':'02A', 'icom':'133',
         'nomWkpFr': 'Bastia', 'nom':'Bastia', 'codeCommune':'02A077'},
        ]

    # Enregistrement Bd
    database.enregistreVilleWKP(config, databasePath, listeVilles4Bd, True)

    # Test ville ok dans la base
    connDB = database.createDatabase(config, databasePath, False)
    cursor = connDB.cursor()
    cursor.execute("SELECT codeCommune FROM villes")
    listVille = cursor.fetchall()
    assert len(listVille) == 3
    listeCode = [ville[0] for ville in listVille]
    for code in ('003076', '046077', '02A077'):
        assert code in listeCode

    # Test si le changement sur le nom de département a bien été effectué
    cursor.execute("""SELECT nomWkpFr
                        FROM villes WHERE codeCommune=?""", ('003076',))
    listVille = cursor.fetchall()
    assert len(listVille) == 1
    assert listVille[0][0] == 'Badevel (Doubs)'

    cursor.close()
    database.closeDatabase(connDB, False)              

def test_enregistreVilleWKP_Vide():
    """ Test enregistrement vide dans la base de données des villes """
    
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Creation base vide
    databasePathDir = config.get('Test', 'database.testDir')
    databasePath = os.path.join(databasePathDir, config.get('Test', 'database.testName'))
    if not os.path.isdir(databasePathDir):
        os.mkdir(databasePathDir)
    if os.path.isfile(databasePath):
        os.remove(databasePath)
    connDB = database.createDatabase(config, databasePath, False)
    database.closeDatabase(connDB, False)              

    # Préparation structure vide
    listeVilles4Bd = []
    
    # Enregistrement Bd
    database.enregistreVilleWKP(config, databasePath, listeVilles4Bd, True)
    
    # Test aucun enregistrement dans la base
    connDB = database.createDatabase(config, databasePath, False)
    cursor = connDB.cursor()
    cursor.execute("SELECT icom FROM villes")
    listVille = cursor.fetchall()
    assert len(listVille) == 0
    cursor.close()
    database.closeDatabase(connDB, False)              

def test_enregistreVilleWKP_Pb_doublon():
    """ Test enregistrement vide dans la base de données des villes """
    
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Creation base vide
    databasePathDir = config.get('Test', 'database.testDir')
    databasePath = os.path.join(databasePathDir, config.get('Test', 'database.testName'))
    if not os.path.isdir(databasePathDir):
        os.mkdir(databasePathDir)
    if os.path.isfile(databasePath):
        os.remove(databasePath)
    connDB = database.createDatabase(config, databasePath, False)
    database.closeDatabase(connDB, False)              

    listeVilles4Bd = [
        {'nomDepartement':'Doubs', 'numDepartement':'025', 'icom':'027',
         'nomWkpFr': 'Badevel', 'nom':'Badevel', 'codeCommune':'003076'},
         {'nomDepartement':'Doubs', 'numDepartement':'025', 'icom':'027',
         'nomWkpFr': 'Badevel', 'nom':'Badevel', 'codeCommune':'003076'},
        ]

    with pytest.raises(sqlite3.IntegrityError,
                       match=r".*UNIQUE constraint failed.*"):
        database.enregistreVilleWKP(config, databasePath, listeVilles4Bd, True)
    
@pytest.mark.parametrize(\
    "isFast, nbCommuneOK, listCodeCommuneNomWkpOK",
    [
        (False, 3,
          [
            ('046123', 'Biars'),
            ('001007', 'Trifouilly-les Oies (Ain)'),
            ('046111', 'Chat Ours Ville')
          ]),
        (True, 2,
          [
            ('046123', 'Biars'),
            ('046111', 'Chat Ours Ville')
          ])
    ])
def test_getListeCodeCommuneNomWkp(isFast, nbCommuneOK,
                                   listCodeCommuneNomWkpOK):
    """
        Test récupération de toutes les villes de la base et leur nomWikipedia.
        Test sur base avec 2 enregistrements
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Creation base vide
    databasePathDir = config.get('Test', 'database.testDir')
    databasePath = os.path.join(databasePathDir, config.get('Test', 'database.testName'))
    if not os.path.isdir(databasePathDir):
        os.mkdir(databasePathDir)
    if os.path.isfile(databasePath):
        os.remove(databasePath)
    connDB = database.createDatabase(config, databasePath, False)

    # Ajout 3 villes : 2 anciennes commune et une existante
    connDB.executemany("""INSERT INTO villes(codeCommune, ancienneCommune,nomWkpFr)
                            VALUES (?, ?, ?)""",
                       (('001007', 1, 'Trifouilly-les Oies (Ain)'),
                        ('046123', 0, 'Biars'),
                        ('046111', 0, 'Chat Ours Ville')))
    connDB.commit()

    # Test getListeCodeCommuneNomWkp pour toutes les villes
    listCodeCommuneNomWkp = database.getListeCodeCommuneNomWkp(connDB,
                                                    isFast, "score", True)
    assert len(listCodeCommuneNomWkp) == nbCommuneOK
    for codeCommuneNomWkpOK in listCodeCommuneNomWkpOK:
        assert codeCommuneNomWkpOK in listCodeCommuneNomWkp
 
    # Renseignement d'un score pour Biars
    connDB.execute("UPDATE villes SET score=25  WHERE codeCommune='046123'")
    connDB.commit()
    
    # Test getListeCodeCommuneNomWkp pour les villes de score NULL
    listCodeCommuneNomWkp = database.getListeCodeCommuneNomWkp(connDB,
                                                    isFast, "score", True)
    if isFast:
        nbCommuneOK -= 1
    assert len(listCodeCommuneNomWkp) == nbCommuneOK
    for codeCommuneNomWkpOK in listCodeCommuneNomWkpOK[1:]:
        assert codeCommuneNomWkpOK in listCodeCommuneNomWkp

    # Fermeture base
    database.closeDatabase(connDB, True)

def test_updateScoresVille():
    """
        Teste la mise à jour des scores dans la base.
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    
    # Creation base vide
    databasePathDir = config.get('Test', 'database.testDir')
    databasePath = os.path.join(databasePathDir, config.get('Test', 'database.testName'))
    if not os.path.isdir(databasePathDir):
        os.mkdir(databasePathDir)
    if os.path.isfile(databasePath):
        os.remove(databasePath)
    connDB = database.createDatabase(config, databasePath, False)

    # Ajout 2 villes
    connDB.executemany("""INSERT INTO villes(codeCommune, nomWkpFr)
                            VALUES (?, ?)""",
                       (('001007', 'Trifouilly-les Oies (Ain)'),
                        ('046123', 'Biars')))
    connDB.commit()

    # Mise à jour des scores
    scoresVille = {'001007':20, '046123':35}
    database.updateScoresVille(connDB, scoresVille, True)

    # Test
    cursor = connDB.cursor()
    cursor.execute("SELECT codeCommune, score FROM villes ORDER BY codeCommune")
    listVilleScore = cursor.fetchall()
    assert len(listVilleScore) == 2
    assert listVilleScore == [('001007', 20), ('046123', 35)]

    cursor.close()
    database.closeDatabase(connDB, False)              
  
def test_getListeDepartement():
    """
        Test récupération des départements.
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Creation base vide
    databasePathDir = config.get('Test', 'database.testDir')
    databasePath = os.path.join(databasePathDir, config.get('Test', 'database.testName'))
    if not os.path.isdir(databasePathDir):
        os.mkdir(databasePathDir)
    if os.path.isfile(databasePath):
        os.remove(databasePath)
    connDB = database.createDatabase(config, databasePath, False)

    # Test getListeDepartement
    listeDepartement = database.getListeDepartement(connDB, True)
    assert len(listeDepartement) == 101
    assert listeDepartement[0] == ('001', "de l'", 'Ain')

    # Fermeture base
    database.closeDatabase(connDB, True)

def test_getListeVilles4Departement():
    """
        Test récupération des villes d'un département.
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Creation base vide
    databasePathDir = config.get('Test', 'database.testDir')
    databasePath = os.path.join(databasePathDir, config.get('Test', 'database.testName'))
    if not os.path.isdir(databasePathDir):
        os.mkdir(databasePathDir)
    if os.path.isfile(databasePath):
        os.remove(databasePath)
    connDB = database.createDatabase(config, databasePath, False)

    # Insertion de villes dans la base
    connDB.executemany("""INSERT INTO villes
                            (codeCommune, nom, nomWkpFr, numDepartement,
                            typeGroupement, nomStrate, score, population)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                       (('001007', 'Trifouilly-les Oies',
                         'Trifouilly-les Oies (Ain)', '001',
                         'communes de 2 000 à 3 500 hab',
                         'appartenant à un groupement fiscalisé (FPU)',
                         25, "48 hab."),
                        ('046123', 'Biars', 'Biars (Lot)', '046',
                         'communes de 2 000 à 3 500 hab',
                         'appartenant à un groupement fiscalisé (FPU)',
                         40, "148 hab."),
                        ('001001', 'Abenditdonc', 'Abenditdonc', '001',
                         'communes de 2 000 à 3 500 hab',
                         'appartenant à un groupement fiscalisé (FPU)',
                         100, "2 hab."))
                       )
    connDB.executemany("""INSERT INTO departements
                            (numDepartement, nomDepartement, article)
                            VALUES (?, ?, ?)""",
                       (('001', 'Ain', "de l'"), ('046', 'Lot', "du"))
                       )
    connDB.commit()
    
    # Test getListeVilles4Departement
    listeVilles = database.getListeVilles4Departement(connDB, "001", True)
    assert len(listeVilles) == 2
    assert listeVilles[0] == ('001001', 'Abenditdonc', 'Abenditdonc', "de l'",
                              "Ain", 'communes de 2 000 à 3 500 hab',
                              'appartenant à un groupement fiscalisé (FPU)',
                              100, "2 hab.", "001")
    assert listeVilles[1] == ('001007', 'Trifouilly-les Oies',
                              'Trifouilly-les Oies (Ain)', "de l'",
                              "Ain", 'communes de 2 000 à 3 500 hab',
                              'appartenant à un groupement fiscalisé (FPU)',
                              25, "48 hab.", "001")

    # Fermeture base
    database.closeDatabase(connDB, True)

def test_getValeurs4VilleCle():
    """
        Test récup valeur pour une clé et une ville
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Creation base vide
    databasePathDir = config.get('Test', 'database.testDir')
    databasePath = os.path.join(databasePathDir, config.get('Test', 'database.testName'))
    if not os.path.isdir(databasePathDir):
        os.mkdir(databasePathDir)
    if os.path.isfile(databasePath):
        os.remove(databasePath)
    connDB = database.createDatabase(config, databasePath, False)

    # Insertion de valeurs dans la base
    connDB.executemany("""INSERT INTO dataFi(codeCommune, annee, codeCle, valeur)
                            VALUES (?, ?, ?, ?)""",
                       (
                            ('001007', 1998, "GrosSous1", "2000.5"),
                            ('046123', 2000, "GrosSous1", "180"),
                            ('001001', 1998, "GrosSous1", "5.5"),
                            ('001001', 1900, "GrosSous1", "1.5"),
                            ('001001', 1910, "GrosSous1", "11.5"),
                            ('001001', 1900, "GrosSous2", "0.5"),
                       )
                       )
    connDB.commit()

    # Test
    listeAnneeValeur = database.getValeurs4VilleCle(connDB, '001001', "GrosSous1", True)
    assert len(listeAnneeValeur) == 3
    assert listeAnneeValeur == [(1998, "5.5"), (1910, "11.5"), (1900, "1.5")]
    listeAnneeValeur = database.getValeurs4VilleCle(connDB, '001001', "GrosSous2", True)
    assert len(listeAnneeValeur) == 1
    listeAnneeValeur = database.getValeurs4VilleCle(connDB, '001001', "GrosSous3", True)
    assert len(listeAnneeValeur) == 0
    listeAnneeValeur = database.getValeurs4VilleCle(connDB, '091007', "GrosSous1", True)
    assert len(listeAnneeValeur) == 0
 
    # Fermeture base
    database.closeDatabase(connDB, True)

def test_getListeAnneesDataMinFi4Entite():
    """
        Test récup années des données financières pour une clé et une ville
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Creation base vide
    databasePathDir = config.get('Test', 'database.testDir')
    databasePath = os.path.join(databasePathDir, config.get('Test', 'database.testName'))
    if not os.path.isdir(databasePathDir):
        os.mkdir(databasePathDir)
    if os.path.isfile(databasePath):
        os.remove(databasePath)
    connDB = database.createDatabase(config, databasePath, False)

    # Insertion de valeurs dans la base
    connDB.executemany("""INSERT INTO dataFi(codeCommune, annee, codeCle, valeur)
                            VALUES (?, ?, ?, ?)""",
                       (
                            ('001001', 1998, "GrosSous1", "2000.5"),
                            ('001007', 2000, "GrosSous1", "180"),
                            ('001007', 1998, "GrosSous2", "5.5"),
                            ('001001', 1900, "GrosSous1", "1.5"),
                            ('001001', 1910, "GrosSous1", "11.5"),
                            ('001001', 1900, "GrosSous2", "0.5"),
                       )
                       )
    connDB.commit()

    # Test
    listeAnnee = database.getListeAnneesDataMinFi4Entite(connDB, 'V', '001001', True)
    assert len(listeAnnee) == 3
    assert listeAnnee == [1998, 1910, 1900]

    # Fermeture base
    database.closeDatabase(connDB, True)

def test_getListeAnneesDataMinFi4EntiteGroupement():
    """
        Test récup années des données financières pour une clé et
        un groupement de communes
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Creation base vide
    databasePathDir = config.get('Test', 'database.testDir')
    databasePath = os.path.join(databasePathDir, config.get('Test', 'database.testName'))
    if not os.path.isdir(databasePathDir):
        os.mkdir(databasePathDir)
    if os.path.isfile(databasePath):
        os.remove(databasePath)
    connDB = database.createDatabase(config, databasePath, False)

    # Insertion de valeurs dans la base
    connDB.executemany("""INSERT INTO dataFiGroupement(sirenGroupement, annee,
                                                       codeCle, valeur)
                            VALUES (?, ?, ?, ?)""",
                       (
                            ('001001', 1998, "GrosSous1", "2000.5"),
                            ('001007', 2000, "GrosSous1", "180"),
                            ('001007', 1998, "GrosSous2", "5.5"),
                            ('001001', 1900, "GrosSous1", "1.5"),
                            ('001001', 1910, "GrosSous1", "11.5"),
                            ('001001', 1900, "GrosSous2", "0.5"),
                       )
                       )
    connDB.commit()

    # Test
    listeAnnee = database.getListeAnneesDataMinFi4Entite(connDB, 'GC', '001001', True)
    assert len(listeAnnee) == 3
    assert listeAnnee == [1998, 1910, 1900]

    # Fermeture base
    database.closeDatabase(connDB, True)

def test_getAllValeursDataMinFi4Ville():
    """
        Test récup valeurs financières pour une ville
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # récup données de test
    pathDatabaseMini = config.get('Test', 'genCode.pathDatabaseMini')
    pathCSVMini = config.get('Test', 'genCode.pathCSVMini')
    print("\ntest_getAllValeursDataMinFi4Ville : base =", pathDatabaseMini)
    if os.path.isfile(pathDatabaseMini):
        print("destruction de la base :", pathDatabaseMini)
        os.remove(pathDatabaseMini)

    # Insertion dans la table villes des villes à traiter
    # Création base
    connDB = database.createDatabase(config, pathDatabaseMini, False)
    connDB.executemany("""
        INSERT INTO villes(codeCommune, nomMinFi, nom, nomWkpFr)
        VALUES (?, ?, ?, ?)
        """, (('068376', 'WITTENHEIM', 'Wittenheim', 'Wittenheim'),)
                       )
    connDB.commit()

    # Création de la base de test
    param = ['updateDataMinFi.py', pathDatabaseMini, pathCSVMini]
    updateDataMinFi.main(param)
    assert os.path.isfile(pathDatabaseMini)

    # Test fonction getAllValeursDataMinFi4Entite
    # Récupère toutes les valeurs pour cette ville pour les grandeurs demandées
    dictAllGrandeur = database.getAllValeursDataMinFi4Entite(connDB, 'V',
                                                             '068376', True)
    assert dictAllGrandeur["Taux"]["taux taxe habitation"][2013]  == \
               pytest.approx(10.11)
    assert dictAllGrandeur["taux moyen pour la strate"]["taux taxe habitation moyen"][2013]  == \
               pytest.approx(15.68)
    assert dictAllGrandeur["Taux"]["taux taxe habitation"][2015]  == \
               pytest.approx(10.11)
    assert dictAllGrandeur["taux moyen pour la strate"]["taux taxe habitation moyen"][2015]  == \
               pytest.approx(15.98)
    assert dictAllGrandeur["taux moyen pour la strate"]["taux taxe foncière bâti moyen"][2015]  == \
               pytest.approx(22.48)
    
    assert dictAllGrandeur["Valeur totale"]["total des produits de fonctionnement"][2013]  == \
               pytest.approx(13210.12)
    assert dictAllGrandeur["Par habitant"]["total des produits de fonctionnement par habitant"][2013]  == \
               pytest.approx(917.18)
    assert dictAllGrandeur["En moyenne pour la strate"]["total des produits de fonctionnement moyen"][2013]  == \
               pytest.approx(1336.52)
    assert dictAllGrandeur["Valeur totale"]["total des produits de fonctionnement"][2014]  == \
               pytest.approx(13399.69)
    assert dictAllGrandeur["Par habitant"]["total des produits de fonctionnement par habitant"][2014]  == \
               pytest.approx(926.48)
    assert dictAllGrandeur["En moyenne pour la strate"]["total des produits de fonctionnement moyen"][2014]  == \
               pytest.approx(1336.99)

    assert dictAllGrandeur["Valeur totale"]["dont dépenses équipement"][2015]  == \
               pytest.approx(4322.98)
    assert dictAllGrandeur["Par habitant"]["dont dépenses équipement par habitant"][2015]  == \
               pytest.approx(293.20)
    assert dictAllGrandeur["En moyenne pour la strate"]["dont dépenses équipement moyen"][2015]  == \
               pytest.approx(268.35)

    database.closeDatabase(connDB, False)

def test_getAllValeursDataMinFi4Groupement():
    """
        Test récup valeurs financières pour un groupement de communes
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # récup données de test
    pathDatabaseMini = config.get('Test', 'updateDataMinFiGroupement.pathDatabaseMini')
    pathCSVMini = config.get('Test', 'updateDataMinFiGroupement.pathCSVMini')
    print("\ntest_getAllValeursDataMinFi4Groupement : base =", pathDatabaseMini)
    if os.path.isfile(pathDatabaseMini):
        print("destruction de la base :", pathDatabaseMini)
        os.remove(pathDatabaseMini)

    # Insertion dans la table groupementCommunes des groupements à traiter
    # Création base
    connDB = database.createDatabase(config, pathDatabaseMini, False)
    connDB.executemany("""
        INSERT INTO villes(codeCommune, nomMinFi, sirenGroupement)
        VALUES (?, ?, ?)
        """, (('045006', 'ARDON', '200005932'),))
    connDB.executemany("""
        INSERT INTO groupementCommunes(sirenGroupement, nom)
        VALUES (?, ?)
        """, (('200005932', 'Communauté de communes des Portes de Sologne'),))
    connDB.commit()

    # Création de la base de test
    # Appel programme
    param = ['updateDataMinFiGroupementCommunes.py', pathDatabaseMini, pathCSVMini]
    updateDataMinFiGroupementCommunes.main(param)
    assert os.path.isfile(pathDatabaseMini)

    # Test fonction getAllValeursDataMinFi4Entite
    # Récupère toutes les valeurs pour ce groupement
    dictAllGrandeur = database.getAllValeursDataMinFi4Entite(connDB, 'GC',
                                                             '200005932', True)

    # Test
    assert dictAllGrandeur["Valeur totale"]['total des produits de fonctionnement'][2018]  == \
               pytest.approx(6526.)
    assert dictAllGrandeur["Par habitant"]["total des produits de fonctionnement par habitant"][2018]  == \
               pytest.approx(417.)

    
    assert dictAllGrandeur["Valeur simple"]["nomminfi"][2018]  == \
               'CC DES PORTES DE SOLOGNE'
    assert dictAllGrandeur["Taux"]["taux taxe habitation"][2018]  == \
               pytest.approx(8.18)

    database.closeDatabase(connDB, False)

def test_updateInfosGroupement():
    """
        Test mise à jour dans la base des infos des groupements de communes
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # récup données de test
    pathDatabaseCC = os.path.join(config.get('Test', 'database.testDir'),
                                  config.get('Test', 'database.testNameCC'))
    print("\ntest_updateInfosGroupement : base =", pathDatabaseCC)
    if os.path.isfile(pathDatabaseCC):
        print("destruction de la base :", pathDatabaseCC)
        os.remove(pathDatabaseCC)

    # Insertion dans la table villes des villes existantes et
    # d'un groupement de commune
    # Création base
    connDB = database.createDatabase(config, pathDatabaseCC, False)
    connDB.executemany("""
        INSERT INTO villes(codeCommune, ancienneCommune, nom)
        VALUES (?, ?, ?)
        """, (('068376', 0, 'Wittenheim'), ('046132', 0, 'Issendolus')))
    connDB.executemany("""
        INSERT INTO groupementCommunes(nomArticleCC, nom, sirenGroupement)
        VALUES (?, ?, ?)
        """, (('Communauté_de_communes_Grand-Figeac_(nouvelle)',
               'CC Grand Figeac', '200067361'),))
    connDB.commit()

    # Définition valeurs de test
    listeSirenCodeCommune=[('200067361', 1, '046132'), ('200066009', 0, '068376')]
    dictSirenInfoCC={'200067361':
                     {"nomArticleCC":"Communauté de communes Grand-Figeac (nouvelle)",
                      "sirenGroupement":"200067361",
                      "nom":"Communauté de communes Grand-Figeac",
                      "région":"[[Occitanie (région administrative)|Occitanie]]",
                      "département":"[[Lot (département)|Lot]] et [[Aveyron (département)|Aveyron]]",
                      "forme":"[[Communauté de communes]]",
                      "siège":"[[Figeac]]",
                      "nombreCommunes":92,
                      "population":43499,
                      "annéePop":2016,
                      "superficie":1283,
                      "logo":"Logo CdC Grand Figeac.png",
                      "siteWeb":"[http://www.grand-figeac.fr/ grand-figeac.fr/]"
                     },
                     '200066009':
                     {"nomArticleCC":"Communauté de communes Grand-Figeac (nouvelle)",
                      "sirenGroupement":"200066009",
                      "nom":"Mulhouse Alsace Agglomération",
                      "région":"[[Grand Est]]",
                      "département":"[[Haut-Rhin]]",
                      "forme":"[[Communauté d'agglomération]]",
                      "siège":"[[Mulhouse]]",
                      "nombreCommunes":39,
                      "population":272985,
                      "annéePop":2016,
                      "superficie":439,
                      "logo":"Logo officiel de Mulhouse Alsace Agglomération.png|vignette Logo m2a.jpg|vignette",
                      "siteWeb":"[http://www.mulhouse-alsace.fr www.mulhouse-alsace.fr]"
                     }
                    }

    # Test fonction
    database.updateInfosGroupement(connDB, listeSirenCodeCommune,
                          dictSirenInfoCC, True)

    # Contrôle des valeurs de la base
    cursor = connDB.cursor()
    cursor.execute("SELECT sirenGroupement, ancienneCommune FROM villes")
    listSirenGroupement = cursor.fetchall()
    assert len(listSirenGroupement) == 2
    listNumSiren = [numSiren[0] for numSiren in listSirenGroupement]
    for numSirenOK in ('200067361', '200066009'):
        assert numSirenOK in listNumSiren
    assert ('200067361', 1) in listSirenGroupement # Issendolus est devenue une ancienne commune
    assert ('200066009', 0) in listSirenGroupement

    cursor.execute("SELECT sirenGroupement, nom FROM groupementCommunes")
    listResultat = cursor.fetchall()
    for tupple in (('200067361', "Communauté de communes Grand-Figeac"),
                              ('200066009', "Mulhouse Alsace Agglomération")):
        assert tupple in listResultat

    # Fermeture base
    cursor.close()
    database.closeDatabase(connDB, True)

def test_getSirenInfosGroupementsAnnees():
    """
    Test récupération des numéros de SIREN des groupements déjà présents dans la base
    ainsi que leurs noms et années des infos financières déjà enregistrées.
    table groupementCommunes.
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Init de la base
    pathDatabaseCC = os.path.join(config.get('Test', 'database.testDir'),
                                  config.get('Test', 'database.testNameCC'))
    print("\ntest_getSirenInfosGroupementsAnnees : base =", pathDatabaseCC)
    if os.path.isfile(pathDatabaseCC):
        print("destruction de la base :", pathDatabaseCC)
        os.remove(pathDatabaseCC)

    # Insertion d'un groupement de commune
    # Création base
    connDB = database.createDatabase(config, pathDatabaseCC, False)
    connDB.executemany("""
        INSERT INTO villes(sirenGroupement)
        VALUES (?)
        """,
                       (('1',), ('2',)))
    connDB.executemany("""
        INSERT INTO groupementCommunes(nom, sirenGroupement, nomArticleCC)
        VALUES (?, ?, ?)
        """, (('CC1', '1', 'CC1Wkp'), ('CC2', '2', 'CC2Wkp')))
    connDB.commit()

    # Aucune données financières dans la table dataFiGroupement
    dictSirenInfos = database.getSirenInfosGroupementsAnnees(connDB, True)
    assert dictSirenInfos == {'1': ('CC1', 'CC1Wkp', []), '2': ('CC2', 'CC2Wkp', [])}

    # Ajout de l'annee 2019 et 2020 pour le groupement 2 dans la table dataFiGroupement
    connDB.executemany("""
        INSERT INTO dataFiGroupement(sirenGroupement, annee, codeCle, valeur)
        VALUES (?, ?, ?, ?)
        """, (('2', '2020', 'prod1', '45.2'),
              ('2', '2020', 'prod2', '105.3'),
              ('2', '2019', 'prod3', '2105.3'),
              ('3', '2020', 'prod1', '0.2'))
                       )
    connDB.commit()

    dictSirenInfos = database.getSirenInfosGroupementsAnnees(connDB, True)
    assert dictSirenInfos == {'1': ('CC1', 'CC1Wkp', []),
                              '2': ('CC2', 'CC2Wkp', [2019, 2020])}

    # Fermeture base
    database.closeDatabase(connDB, True)

def test_enregistreLigneGroupementMinFi():
    """
    Test enregistrement de valeurs dans la table dataFiGroupement.
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Init de la base
    pathDatabaseCC = os.path.join(config.get('Test', 'database.testDir'),
                                  config.get('Test', 'database.testNameCC'))
    print("\ntest_getSirenInfosGroupementsAnnees : base =", pathDatabaseCC)
    if os.path.isfile(pathDatabaseCC):
        print("destruction de la base :", pathDatabaseCC)
        os.remove(pathDatabaseCC)
    connDB = database.createDatabase(config, pathDatabaseCC, False)

    # Test
    dictValues = {'siren':'1', 'exer':'2020', 'prod1':'45.2', 'prod2':'100.5'}
    database.enregistreLigneGroupementMinFi(dictValues, connDB, True)

    # Vérification
    listDataFiOk = [('1', 2020, 'prod1', '45.2'), ('1', 2020, 'prod2', '100.5')]
    cursor = connDB.cursor()
    cursor.execute("""SELECT sirenGroupement, annee, codeCle, valeur
                        FROM dataFiGroupement
                        """)
    assert listDataFiOk == cursor.fetchall()
  
    # Fermeture base
    cursor.close()
    database.closeDatabase(connDB, True)
   
def test_getListeVilleGroupement():
    """
        Test récupération des villes et de leurs info groupement.
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Creation base vide
    databasePathDir = config.get('Test', 'database.testDir')
    databasePath = os.path.join(databasePathDir, config.get('Test',
                                                            'database.testName'))
    if not os.path.isdir(databasePathDir):
        os.mkdir(databasePathDir)
    if os.path.isfile(databasePath):
        os.remove(databasePath)
    connDB = database.createDatabase(config, databasePath, False)

    # Insertion de villes dans la base
    connDB.executemany("""INSERT INTO villes
                            (codeCommune, sirenGroupement)
                            VALUES (?, ?)""",
                       (('001007', 'SIREN1'),
                        ('046123', 'SIREN1'),
                        ('001001', 'SIREN2'),
                        ('002001', ''))
                       )
    connDB.executemany("""INSERT INTO groupementCommunes
                            (sirenGroupement, nomArticleCC, nom)
                            VALUES (?, ?, ?)""",
                       (('SIREN1', 'nomArticleCCSiren1', "nomArticleCCSiren1"),
                        ('SIREN2', 'nomArticleCCSiren2', "nomArticleCCSiren2"),
                        ('SIREN3', 'nomArticleCCSiren3', "nomArticleCCSiren3"))
                       )
    connDB.commit()
    
    # Test getListeVilleGroupement
    infosGroupement = database.getListeVilleGroupement(connDB, '001007', True)
    assert infosGroupement == ('SIREN1', 'nomArticleCCSiren1', "nomArticleCCSiren1")
    infosGroupement = database.getListeVilleGroupement(connDB, '046123', True)
    assert infosGroupement == ('SIREN1', 'nomArticleCCSiren1', "nomArticleCCSiren1")
    infosGroupement = database.getListeVilleGroupement(connDB, '001001', True)
    assert infosGroupement == ('SIREN2', 'nomArticleCCSiren2', "nomArticleCCSiren2")
    infosGroupement = database.getListeVilleGroupement(connDB, '002001', True)
    assert not infosGroupement
    infosGroupement = database.getListeVilleGroupement(connDB, '999999', True)
    assert not infosGroupement

    # Fermeture base
    database.closeDatabase(connDB, True)
