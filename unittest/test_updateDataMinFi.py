#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name : test_updateDataMinFi.py
Author : Thierry Maillard (TMD)
Date : 1/7/2019 - 7/4/2020
Role : Tests unitaires du projet FinancesLocales avec py.test
Utilisation :
    Pour jouer tous les test not global : élimine les tests globaux très long :
    python3 -m pytest -k "not global" .
    Pour jouer un test particulier de tous les fichiers de test
    python3 -m pytest -k "test_checkPathCSVDataGouvFrOk" test_updateDataMinFi.py
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
import shutil
import sqlite3

import pytest

import updateDataMinFi
import updateDataMinFiCommon
import database


def test_checkPathCSVDataGouvFrOk():
    """ Test fonction de validation d'un répertoire contenant les données
        issues du site gouvernemental """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    # Ce répertoire contient les .csv extraits de
    # [Extraction]dataGouvFr.Comptes (FinancesLocales.properties)
    pathCSVDataGouvFr = config.get('Test', 'test.pathCSVDataGouvFrOk')
    # Le nombre de fichiers .csv doit être adapté au contenu du répertoire
    listFileCSVMinFi = updateDataMinFi.checkPathCSVDataGouvFr(config, pathCSVDataGouvFr, True)
    assert len(listFileCSVMinFi) == config.getint('Test', 'test.nbFilesCSVDataGouvFrOk')
    assert listFileCSVMinFi[0] == os.path.join(pathCSVDataGouvFr,
                                        config.get('Test', 'test.firstFileCSVDataGouvFrOk'))

    TwoKInFilename = True
    for filename in listFileCSVMinFi:
        if '20' not in filename:
            TwoKInFilename = False
            break
    assert TwoKInFilename, filename + ' ne contient pas 20 !'

@pytest.mark.parametrize("pathCSVDataGouvFr, msgOk",
                         [
                          ('badDir', "répertoire des .csv incorrect"),
                          ('annee_NOK1' , "annee invalide"),
                          ('annee_NOK2' , "annee invalide"),
                          ])
def test_checkPathCSVDataGouvFrPb(pathCSVDataGouvFr, msgOk):
    """ Test cas d'erreur fonction de validation d'un répertoire contenant les données
        issues du site gouvernemental
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    testPathCSVDataGouvFr = os.path.join(config.get('Test', 'test.testDirExtraction'),
                                         pathCSVDataGouvFr)

    with pytest.raises(ValueError, match=msgOk):
        updateDataMinFi.checkPathCSVDataGouvFr(config, testPathCSVDataGouvFr, True)

@pytest.mark.parametrize("ligneVille, header, dictVerif",
                         [
                          ('001;007;ST PIERRE DU MONT;25.6;2.5;4.7;2.6;20.6;Salut',
                           'dep;icom;inom;prod;fprod;mprod;tmth',
                           {"dep":'001', "icom":'007',
                            "inom":"ST PIERRE DU MONT",
                            "prod":'25.6', "fprod":'2.5', "mprod":'4.7', "tmth":'2.6',
                            "codeCommune":'001007'}),
                          ('068;101;WALHEIM;ndef;-4;4.7;a5;x.y;Hello',
                           'dep;icom;inom;prod;fprod;mprod;tmth',
                           {"dep":'068', "icom":'101',
                            "inom":"WALHEIM",
                           "prod":'ndef', "fprod":'-4', "mprod":'4.7', "tmth":'a5',
                           "codeCommune":'068101'}),
                          ('2018;56;34;CARNAC',
                           'an;dep;icom;inom',
                           {'an':'2018', "dep":'056', "icom":'034', "inom":"CARNAC",
                           "codeCommune":'056034'}),
                          ])
def test_analyseLigneVille(ligneVille, header, dictVerif):
    """ Récupération des valeurs dans une ligne de valeur pour une ville """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Recup chemin base de test
    databasePathDir = config.get('Test', 'database.testDir')
    databasePath = os.path.join(databasePathDir, config.get('Test', 'database.testName'))
    # Création base
    connDB = database.createDatabase(config, databasePath, False)

    dictPositionColumns, listMissingKeys = \
        updateDataMinFiCommon.getColumnPosition(header, "V", connDB, False)

    dictValues = updateDataMinFi.analyseLigneVille(config, ligneVille, dictPositionColumns, True)
    assert dictValues == dictVerif

    # Fermeture base
    database.closeDatabase(connDB, True)

def test_analyseLigneVille_Manque_Champ():
    """ Ligne de description d'une ville trop courte : 3 champs au lieu de 4
        manque champ tmth """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Recup chemin base de test
    databasePathDir = config.get('Test', 'database.testDir')
    databasePath = os.path.join(databasePathDir, config.get('Test', 'database.testName'))
    # Création base
    connDB = database.createDatabase(config, databasePath, False)

    dictPositionColumns, listMissingKeys = \
        updateDataMinFiCommon.getColumnPosition('dep;icom;prod;fprod;mprod;tmth',
                                                "V", connDB, False)

    with pytest.raises(ValueError, match=r'manque clé tmth'):
        dictValues = updateDataMinFi.analyseLigneVille(config, '068;101;25.6;2.5;4.7',
                                                       dictPositionColumns, True)

    # Fermeture base
    database.closeDatabase(connDB, True)

def test_analyseLigneVille_Pb_dep():
    """ Ligne de description d'une ville trop courte : 3 champs au lieu de 4
        manque champ tmth """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Recup chemin base de test
    databasePathDir = config.get('Test', 'database.testDir')
    databasePath = os.path.join(databasePathDir, config.get('Test', 'database.testName'))
    # Création base
    connDB = database.createDatabase(config, databasePath, False)

    dictPositionColumns, listMissingKeys = \
        updateDataMinFiCommon.getColumnPosition('dep;icom', "V", connDB, False)

    with pytest.raises(ValueError, match=r'doit comporter 2 ou 3 caractères'):
        dictValues = updateDataMinFi.analyseLigneVille(config, '0685;4',
                                                       dictPositionColumns, True)

    # Fermeture base
    database.closeDatabase(connDB, True)

def test_createDbDataMinFi():
    """
        Test génération database avec un fichier CSV réduit à 2 villes
        """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # récup données de test
    pathDatabaseMini = config.get('Test', 'updateDataMinFi.pathDatabaseMini')
    pathCSVMini = config.get('Test', 'updateDataMinFi.pathCSVMini')
    if os.path.isfile(pathDatabaseMini):
        print("destruction de la base :", pathDatabaseMini)
        os.remove(pathDatabaseMini)

    # Insertion dans la table ville des villes à traiter
    # Création base
    connDB = database.createDatabase(config, pathDatabaseMini, False)
    connDB.executemany("""
        INSERT INTO villes(codeCommune, nomMinFi)
        VALUES (?, ?)
        """, (('068356', 'WALHEIM'), ('040281', 'ST PIERRE DU MONT')))
    connDB.commit()
    database.closeDatabase(connDB, True)

    # Appel programme
    param = ['updateDataMinFi.py', pathDatabaseMini, pathCSVMini]
    updateDataMinFi.main(param)
    assert os.path.isfile(pathDatabaseMini)

    # Test info ville 1
    connDB = sqlite3.connect(pathDatabaseMini)
    cursor = connDB.cursor()
    cursor.execute("SELECT codeCommune, nomMinFi, nomStrate FROM villes ORDER BY codeCommune")
    listVilles = cursor.fetchall()
    assert len(listVilles) == 2
    assert listVilles[0][0] == '040281'
    assert listVilles[0][1] == 'ST PIERRE DU MONT'
    assert listVilles[0][2] == "n'appartenant à aucun groupement fiscalisé"
    assert listVilles[1][0] == '068356'
    assert listVilles[1][1] == 'WALHEIM'
    assert listVilles[1][2] == "n'appartenant à aucun groupement fiscalisé"
    cursor.close()

    connDB.close()
