#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name : test_database.py
Author : Thierry Maillard (TMD)
Date : 30/6/2015 - 12/11/2019
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


def test_initClesMinFi():
    """ Test fonction d'init des mots clés du ministère des finances """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    listCodeCle = [list1Cles[0] for list1Cles in database.initClesMinFi(config, True)]
    assert config['cleFi3Valeurs']['clefi.dont charges de personnel'] in listCodeCle
    assert config['cleFi2Valeurs']["cletaxe.taux taxe habitation"] in listCodeCle
    assert config['cleFi1Valeur']['clefi.codeInsee'] in listCodeCle

def test_initDepartements():
    """ Test fonction d'init des noms de départements """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    listeDepartements = database.initDepartements(config, True)
    assert len(listeDepartements) == 101
    assert ('046', 'Lot', 'du') in listeDepartements

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
    connDB = database.createDatabase(config, databasePath, True)
    assert os.path.isfile(databasePath)
    assert connDB

    # Test si les tables ont bien été créée
    cursor = connDB.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    listTablesRecords = cursor.fetchall()
    assert len(listTablesRecords) == 4
    listTables = [tableRecord[0] for tableRecord in listTablesRecords]
    for table in ('villes', 'clesMinFi', 'dataFi', 'departements'):
        assert table in listTables

    # Fermeture base
    cursor.close()
    database.closeDatabase(connDB, True)

def test_getListCodeClesMiniFi():
    """ Test fonction de creation de la base de données """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Recup chemin base de test
    databasePathDir = config.get('Test', 'database.testDir')
    databasePath = os.path.join(databasePathDir, config.get('Test', 'database.testName'))
    # Création base
    connDB = database.createDatabase(config, databasePath, True)

    # Test getListCodeClesMiniFi
    listCodeCle = database.getListCodeClesMiniFi(connDB, True)
    assert len(listCodeCle) == \
        (len(config['cleFi3Valeurs']) * 3 + len(config['cleFi2Valeurs']) * 2 +
         len(config['cleFi1Valeur']))
    assert config['cleFi3Valeurs']['clefi.dont charges de personnel'] in listCodeCle
    assert config['cleFi2Valeurs']["cletaxe.taux taxe habitation"] in listCodeCle
    assert config['cleFi1Valeur']['clefi.codeInsee'] in listCodeCle

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
    
def test_getListeCodeCommuneNomWkp_2_rec():
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

    # Ajout 2 villes
    connDB.executemany("""INSERT INTO villes(codeCommune, nomWkpFr)
                            VALUES (?, ?)""",
                       (('001007', 'Trifouilly-les Oies (Ain)'),
                        ('046123', 'Biars')))
    connDB.commit()

    # Test getListeCodeCommuneNomWkp pour toutes les villes
    isFast = False
    listCodeCommuneNomWkp = database.getListeCodeCommuneNomWkp(connDB, isFast, True)
    assert len(listCodeCommuneNomWkp) == 2
    assert listCodeCommuneNomWkp[0] == ('001007', 'Trifouilly-les Oies (Ain)')
    assert listCodeCommuneNomWkp[1] == ('046123', 'Biars')

    # Renseignement d'un score pour Biars
    connDB.execute("""UPDATE villes SET score=25  WHERE codeCommune='046123'""")
    connDB.commit()
    
    # Test getListeCodeCommuneNomWkp pour les villes de score NULL
    isFast = True
    listCodeCommuneNomWkp = database.getListeCodeCommuneNomWkp(connDB, isFast, True)
    assert len(listCodeCommuneNomWkp) == 1
    assert listCodeCommuneNomWkp[0] == ('001007', 'Trifouilly-les Oies (Ain)')

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

def test_getListeAnnees4Ville():
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
    listeAnnee = database.getListeAnnees4Ville(connDB, '001001', True)
    assert len(listeAnnee) == 3
    assert listeAnnee == [1998, 1910, 1900]

    # Fermeture base
    database.closeDatabase(connDB, True)


def test_getAllValeurs4Ville():
    """
        Test récup valeurs pour une ville
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # récup données de test
    pathDatabaseMini = config.get('Test', 'genCode.pathDatabaseMini')
    pathCSVMini = config.get('Test', 'genCode.pathCSVMini')
    if os.path.isfile(pathDatabaseMini):
        print("destruction de la base :", pathDatabaseMini)
        os.remove(pathDatabaseMini)

    # Insertion dans la table ville des villes à traiter
    # Création base
    connDB = database.createDatabase(config, pathDatabaseMini, False)
    connDB.executemany("""
        INSERT INTO villes(codeCommune, nomMinFi, nom, nomWkpFr)
        VALUES (?, ?, ?, ?)
        """, (('068376', 'WITTENHEIM', 'Wittenheim', 'Wittenheim'),)
                       )
    connDB.commit()

    # Création de la création de la base de test
    param = ['updateDataMinFi.py', pathDatabaseMini, pathCSVMini]
    updateDataMinFi.main(param)
    assert os.path.isfile(pathDatabaseMini)

    # Test fonction getAllValeurs4Ville
    # Récupère toutes les valeurs pour cette ville pour les grandeurs demandées
    dictAllGrandeur = database.getAllValeurs4Ville(connDB, '068376', True)
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
