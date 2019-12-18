#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name : test_updateScoreWikipedia.py
Author : Thierry Maillard (TMD)
Date : 27/7/2019 - 12/11/2019
Role : Tests unitaires du projet FinancesLocales avec py.test
        not global : élimine les tests globaux très long
 options :
    -s : pour voir les sorties sur stdout
Ref : http://sametmax.com/un-gros-guide-bien-gras-sur-les-tests-unitaires-en-python-partie-3/
Ref : http://pytest.org/latest/
prerequis : pip3 install pytest

Licence : GPLv3
Copyright (c) 2019 - Thierry Maillard

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
import os.path
import configparser
import urllib.request, urllib.parse, urllib.error
import pytest

import updateScoreWikipedia
import database

@pytest.mark.parametrize("nomArticleUrl", [
    "Issendolus",
    "Toulouse",
    "Montfaucon_(Lot)",
    ])
def test_getPageWikipediaFr(nomArticleUrl):
    """ Test récupération d'une page Wikipédia """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    page = updateScoreWikipedia.getPageWikipediaFr(config, nomArticleUrl, True)
    assert len(page) > 0
    assert nomArticleUrl.split("_")[0] in page
    assert '[[Catégorie:'  in page

def test_getPageWikipediaFr_PbNomville():
    """ Test cas erreur : récupération d'une page Wikipédia """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    with pytest.raises(urllib.error.HTTPError):
        updateScoreWikipedia.getPageWikipediaFr(config, 'PetitCocoVille', True)

@pytest.mark.parametrize(\
    "page, dicoOK",
    [
        ("",
         {'importanceCDF' : "?", 'avancement' : "?",
          'importanceVDM' : "?", 'popularite' : "?"}),
        (r"""
         critereimportanceCDF = {
         'cle' : 'importanceCDF',
         'select' : r'^[ ]*\|[ ]*Communes de France[ ]*\|[ ]*(?P<importanceCDF>\S+)'
         }
         listeCriteres.append(critereimportanceCDF)
         """,
         {'importanceCDF' : "?", 'avancement' : "?",
          'importanceVDM' : "?", 'popularite' : "?"}),
        ("""
         |Communes de France|maximum
         |Villes du monde|moyenne
         |Les plus consultés|moyenne
         |avancement=AdQ
         """,
         {'importanceCDF' : "maximum", 'avancement' : "AdQ",
          'importanceVDM' : "moyenne", 'popularite' : "moyenne"}),
        ("""
         {{Wikiprojet
         | Toulouse | maximum
         | Occitanie | maximum
         | Midi-Pyrénées| maximum
         | Communes de France | maximum
         | Villes du monde | moyenne
         | Les plus consultés | moyenne
         | avancement = AdQ
         | WP1.0      = oui

         | lumière 1  = {{date|2|mars|2008}}
         }}""",
         {'importanceCDF' : "maximum", 'avancement' : "AdQ",
          'importanceVDM' : "moyenne", 'popularite' : "moyenne"}),
        ("""
         {{Wikiprojet
         |Communes de France|faible
         |avancement=BD
         }}""",
         {'importanceCDF' : "faible", 'avancement' : "BD",
          'importanceVDM' : "?", 'popularite' : "?"}),
        ("""{{Wikiprojet
         |Communes de France|élevée
         |France d'outre-mer|élevée
         |avancement=BD}}""",
         {'importanceCDF' : "élevée", 'avancement' : "BD",
          'importanceVDM' : "?", 'popularite' : "?"})
    ])
def test_recupScoreData1Ville(page, dicoOK):
    """ Test fonction d'analyse du score """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    listeCriteres = updateScoreWikipedia.recupScoreData1Ville(config, page, "test", True)
    assert len(listeCriteres) == len(dicoOK)
    for critere in listeCriteres:
        assert critere['valeur'] == dicoOK[critere['cle']]

# V1.0.5 : Précision labels acceptés et paramétrage
def test_recupScoreData1Ville_PbLabel():
    """
    Test erreur et fonction d'analyse du score
    V1.0.5 : Précision labels acceptés et paramétrage
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    page = "|avancement=NimporteNawak"
    with pytest.raises(ValueError, match=r".*NimporteNawak.*"):
        updateScoreWikipedia.recupScoreData1Ville(config, page, "test", True)
 
@pytest.mark.parametrize(\
    "listeCodeCommuneNomWkp, scoresVilleOK",
    [
        ([("046101", "Issendolus"),], {"046101":9}),
        ([("031101", "Toulouse"),], {"031101":32}),
        ([("046101", "Issendolus"), ("031101", "Toulouse")],
         {"046101":9, "031101":32 }),
    ])
def test_recupScoreDataVilles(listeCodeCommuneNomWkp, scoresVilleOK):
    """ Test recup score pour une série de villes """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    scoresVille = updateScoreWikipedia.recupScoreDataVilles(config, listeCodeCommuneNomWkp, True)
    assert len(listeCodeCommuneNomWkp) == len(scoresVille)
    assert scoresVille == scoresVilleOK

def test_recupScoreDataVilles_Pb404():
    """ Test recup score pour une série de villes """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    listCommuneBad = [("046101", "Pourri-sur-crotte"),]
    scoresVille = updateScoreWikipedia.recupScoreDataVilles(config, listCommuneBad, True)
    assert len(scoresVille) == 0
 
def test_updateScoreWikipedia():
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

    # Insertion de 2 villes
    connDB = database.createDatabase(config, pathDatabaseMini, False)
    connDB.executemany("""INSERT INTO villes(codeCommune, nomWkpFr)
                            VALUES (?, ?)""",
                       (('046204', 'Rocamadour'),
                        ('046003', 'Alvignac')))
    connDB.commit()

    # Insertion des scores dans la table des villes du Lot
    param = ['updateScoreWikipedia.py', '-v', pathDatabaseMini]
    updateScoreWikipedia.main(param)

    # Test villes insérées
    cursor = connDB.cursor()
    cursor.execute("SELECT codeCommune, score FROM villes ORDER BY codeCommune")
    listVilles = cursor.fetchall()
    assert len(listVilles) == 2
    assert listVilles == [('046003', 13), ('046204', 10)]
    cursor.close()
    connDB.close()
