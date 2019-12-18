#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Name : test_initBdFomListeDep.py
    Author : Thierry Maillard (TMD)
    Date : 21/7/2019 - 25/11/2019
    Role : Tests unitaires du projet FinancesLocales avec py.test
    not global : élimine les tests globaux très long
    Utilisation : python3 -m pytest -k "not global" .
    options :
    -s : pour voir les sorties sur stdout
    Ref : http://sametmax.com/un-gros-guide-bien-gras-sur-les-tests-unitaires-en-python-partie-3/
    Ref : http://pytest.org/latest/
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
import pytest
import initBdFomListeDep
import sqlite3

@pytest.mark.parametrize(\
                         "numDep, isOk",
                         [\
                          ('001', True),
                          ('009', True),
                          ('011', True),
                          ('019', True),
                          ('097', False),
                          ('090', True),
                          ('101', True),
                          ('104', True),
                          ('02A', True),
                          ('02B', True),
                          ('021', True),
                          ('000', False),
                          ('098', False),
                          ('200', False),
                          ('02C', False),
                          ('toto', False),
                          ('XXX', False),
                          ('1041', False)
                          ])
def test_isnumDep(numDep, isOk):
    """ Test fonction de test n° département """
    assert initBdFomListeDep.isnumDep(numDep) == isOk

@pytest.mark.parametrize(\
                         "ligne, numDep, dictResuOk",
                         [\
                          ('', '001', {}),
                          ('# Salut', '001', {}),
                          ('Salut # Tout le monde', '001', {}),
                          ('Salut', '001', {}),
                          ('#codeInsee (3 chiffres); nom article Wikipédia', '001', {}),
                          ('009;Assier;Assier', '046',
                           {'numDepartement':'046', 'icom':'009',
                           'nomWkpFr':'Assier', 'nom':'Assier',
                           'codeCommune':'046009'}),
                          ('004;;Ambérieu-en-Bugey', '001',
                           {'numDepartement':'001', 'icom':'004',
                           'nomWkpFr':'Ambérieu-en-Bugey', 'nom':'Ambérieu-en-Bugey',
                           'codeCommune':'001004'}),
                          ('074;Condat;Condat (Lot)', '046',
                           {'numDepartement':'046', 'icom':'074',
                           'nomWkpFr':'Condat (Lot)', 'nom':'Condat',
                           'codeCommune':'046074'}),
                          ])
def test_analyseLigneDep(ligne, numDep, dictResuOk):
    """ Test fonction d'analyse d'une ligne de département """
    assert initBdFomListeDep.analyseLigneDep(ligne, numDep, True) == dictResuOk

def test_recupVillesListe():
    """ Test fonction de récupération des villes dans une liste """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    listeVilles4Bd = initBdFomListeDep.recupVillesListe(config, "075", False)
    assert len(listeVilles4Bd) == 1

def test_initBdFomListeDep():
    """
        Test génération database à prtir liste de ville
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Init base
    pathDatabaseMini = config.get('Test', 'updateDataMinFi.pathDatabaseMini')
    pathCSVMini = config.get('Test', 'updateDataMinFi.pathCSVMini')
    if os.path.isfile(pathDatabaseMini):
        print("destruction de la base :", pathDatabaseMini)
        os.remove(pathDatabaseMini)

    # Données pour les villes de 2 départements de test
    listeVillesPath = config.get('Test', 'test.testInitBdFromListeDep')

    # Insertion dans la table ville des villes du Lot
    param = ['initBdFomListeDep.py', pathDatabaseMini, listeVillesPath]
    initBdFomListeDep.main(param)
    assert os.path.isfile(pathDatabaseMini)

    # Test villes insérées
    connDB = sqlite3.connect(pathDatabaseMini)
    cursor = connDB.cursor()
    cursor.execute("SELECT COUNT(*) FROM villes")
    assert cursor.fetchone()[0] == (26 + 17)

    cursor.execute("""
                    SELECT numDepartement, icom, nomWkpFr, nom
                    FROM villes
                    WHERE codeCommune=?""", ('046127',))
    listVilles = cursor.fetchall()
    assert len(listVilles) == 1
    assert listVilles[0] == ('046', '127', 'Gourdon (Lot)', 'Gourdon')
    cursor.close()
    connDB.close()


