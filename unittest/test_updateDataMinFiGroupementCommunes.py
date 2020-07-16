#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name : test_updateDataMinFiGroupementCommunes.py
Author : Thierry Maillard (TMD)
Date : 8/4/2020 - 10/4/2020
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
Copyright (c) 2020 - Thierry Maillard

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
import sqlite3

import pytest

import updateDataMinFiGroupementCommunes
import updateDataMinFiCommon
import database


@pytest.mark.parametrize("ligneGroupement, header, dictVerif",
                         [
                          ('150;CA ALBIGEOIS (C2A);2020;25.6;200412412',
                           'mpoid;lbudg;exer;nbbaspic;siren',
                           {"lbudg":'CA ALBIGEOIS (C2A)', "exer":'2020',
                            "siren":'200412412'}),
                          ])
def test_analyseLigneGroupement(ligneGroupement, header, dictVerif):
    """ Récupération des valeurs dans une ligne de valeur pour une ville """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Recup chemin base de test
    databasePathDir = config.get('Test', 'database.testDir')
    databasePath = os.path.join(databasePathDir, config.get('Test', 'database.testName'))
    # Création base
    connDB = database.createDatabase(config, databasePath, False)

    dictPositionColumns, listMissingKeys = \
        updateDataMinFiCommon.getColumnPosition(header, "GC", connDB, False)

    dictValues = updateDataMinFiGroupementCommunes.analyseLigneGroupement(ligneGroupement,
                                                                          dictPositionColumns,
                                                                          True)
    assert dictValues == dictVerif

    # Fermeture base
    database.closeDatabase(connDB, True)

def test_createDbDataMinFiGroupement():
    """
    Test génération database avec un fichier groupement de communes
    CSV réduit à 2 villes
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # récup données de test
    pathDatabaseMini = config.get('Test', 'updateDataMinFiGroupement.pathDatabaseMini')
    pathCSVMini = config.get('Test', 'updateDataMinFiGroupement.pathCSVMini')
    if os.path.isfile(pathDatabaseMini):
        print("destruction de la base :", pathDatabaseMini)
        os.remove(pathDatabaseMini)

    # Insertion dans la table ville des numéros de siren à traiter
    # Création base
    connDB = database.createDatabase(config, pathDatabaseMini, False)
    # WALHEIM : CC SUNDGAU non présente dans fichier CSV, ne doit pas apparaitre dans résultats
    # ARDON : CC Portes de Sologne présente dans fichier CSV, doit apparaitre
    connDB.executemany("""
        INSERT INTO villes(codeCommune, nomMinFi, sirenGroupement)
        VALUES (?, ?, ?)
        """, (('068356', 'WALHEIM', '200066041'), ('045006', 'ARDON', '200005932')))
    connDB.executemany("""
        INSERT INTO groupementCommunes(sirenGroupement, nom)
        VALUES (?, ?)
        """, (('200066041', 'Communauté de communes Sundgau'),
              ('200005932', 'Communauté de communes des Portes de Sologne')))
    connDB.commit()
    database.closeDatabase(connDB, True)

    # Appel programme
    param = ['updateDataMinFiGroupementCommunes.py', pathDatabaseMini, pathCSVMini]
    updateDataMinFiGroupementCommunes.main(param)
    assert os.path.isfile(pathDatabaseMini)

    # Test info CC Portes de Sologne présentes dans dataFiGroupement
    connDB = sqlite3.connect(pathDatabaseMini)
    cursor = connDB.cursor()
    cursor.execute("SELECT DISTINCT sirenGroupement, annee FROM dataFiGroupement")
    listSirenAnnee = cursor.fetchall()
    assert len(listSirenAnnee) == 1
    assert listSirenAnnee[0] == ('200005932', 2018)
  
    cursor.execute("SELECT sirenGroupement, annee, codeCle, valeur FROM dataFiGroupement")
    listCleValeur = cursor.fetchall()
    assert len(listCleValeur) > 1
    assert ('200005932', 2018, 'pftot', '6526.0') in listCleValeur
    assert ('200005932', 2018, 'pftothab', '417.0') in listCleValeur
    cursor.close()

    connDB.close()
