#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name : test_extractionWikipediaFr.py
Author : Thierry Maillard (TMD)
Date : 1/6/2015 - 2/6/2015
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
import urllib.request, urllib.parse, urllib.error
import pytest
import extractionWikipediaFr

@pytest.mark.parametrize("nomArticleUrl", [
    "Issendolus",
    "Toulouse",
    "Montfaucon (Lot)",
    ])
def test_getPageWikipediaFr(nomArticleUrl):
    """ Test récupération d'une page Wikipédia """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    page = extractionWikipediaFr.getPageWikipediaFr(config, nomArticleUrl, True)
    assert len(page) > 0
    assert nomArticleUrl.split()[0] in page
    assert '[[Catégorie:'  in page

def test_getPageWikipediaFr_PbNomville():
    """ Test cas erreur : récupération d'une page Wikipédia """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    with pytest.raises(urllib.error.HTTPError):
        extractionWikipediaFr.getPageWikipediaFr(config, 'PetitCocoVille', True)

@pytest.mark.parametrize("nomArticleUrl, nomDepStrOK", [
    ("Issendolus", "du Lot"),
    ("Toulouse", "de la Haute-Garonne"),
    ("Grenoble", "de l'Isère"),
    ("Strasbourg", "du Bas-Rhin"),
    ("Rochefourchat", "de la Drôme"),
    ("Albas (Lot)", "du Lot")
    ])
def test_recupNomDepStr(nomArticleUrl, nomDepStrOK):
    """ Test récupération numéro de département dans l'infobox une page Wikipédia """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    nomDepStr = extractionWikipediaFr.recupNomDepStr(config, nomArticleUrl, True)
    assert nomDepStr == nomDepStrOK

@pytest.mark.parametrize("nomArticle, nomOK, icomOK, depOK", [
    ("Issendolus", "Issendolus", "132", "046"),
    ("Montfaucon (Lot)", "Montfaucon", "204", "046")
    ])
def test_recup1Ville(nomArticle, nomOK, icomOK, depOK):
    """ Test récupération infos d'une ville dans une page Wikipédia """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    listeVilleDict = extractionWikipediaFr.recup1Ville(config, nomArticle, True)
    assert len(listeVilleDict) == 1
    assert listeVilleDict[0]['nom'] == nomOK
    assert listeVilleDict[0]['nomWkpFr'] == nomArticle
    assert listeVilleDict[0]['icom'] == icomOK
    assert listeVilleDict[0]['dep'] == depOK

@pytest.mark.parametrize("articleListe, nbvilleOk, nom1ereVille, depOk, icomOk", [
    ('Liste des communes du Lot', 340, 'Albas', '046', '001'),
    ('Liste des communes du Doubs', 593, 'Abbans-Dessous', '025', '001'),
    ('Liste des communes de La Réunion', 24, 'Les Avirons', '097', '401'),
    ('Liste des communes de la Corse-du-Sud', 124, 'Afa', '02A', '001'),
    ('Liste des communes de la Haute-Corse', 236, 'Aghione', '02B', '002')
    ])
def test_recupVilles(articleListe, nbvilleOk, nom1ereVille, depOk, icomOk):
    """
    Test récupération infos de villes d'un département
    dans une page de liste de commune de Wikipédia
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    listeVilleDict = extractionWikipediaFr.recupVilles(config, articleListe, True)
    assert len(listeVilleDict) == nbvilleOk
    assert listeVilleDict[0]['nom'] == nom1ereVille
    assert listeVilleDict[0]['icom'] == icomOk
    assert listeVilleDict[0]['dep'] == depOk

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

    listeCriteres = extractionWikipediaFr.recupScoreData1Ville(config, page, True)
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
    with pytest.raises(ValueError) as e:
        extractionWikipediaFr.recupScoreData1Ville(config, page, True)
    print(e)
    assert "NimporteNawak" in str(e)

@pytest.mark.parametrize(\
    "listeVilleDict, listeDicoOK, scoreOK",
    [
        ([{'lien' : "Issendolus"}],
         [{'importanceCDF' : "faible", 'avancement' : "BD",
           'importanceVDM' : "?", 'popularite' : "?"}],
         [9]),
        ([{'lien' : "Toulouse"}],
         [{'importanceCDF' : "maximum", 'avancement' : "AdQ",
           'importanceVDM' : "moyenne", 'popularite' : "moyenne"}],
         [36]),
        ([{'lien' : "Issendolus"}, {'lien' : "Toulouse"}],
         [{'importanceCDF' : "faible", 'avancement' : "BD",
           'importanceVDM' : "?", 'popularite' : "?"},
          {'importanceCDF' : "maximum", 'avancement' : "AdQ",
           'importanceVDM' : "moyenne", 'popularite' : "moyenne"}
         ],
         [9, 36]),
    ])
def test_recupScoreDataVilles(listeVilleDict, listeDicoOK, scoreOK):
    """ Test recup score pour une série de villes """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    extractionWikipediaFr.recupScoreDataVilles(config, listeVilleDict, True)
    assert len(listeVilleDict) == len(listeDicoOK)
    for numVille in range(len(listeVilleDict)):
        for cle in list(listeDicoOK[numVille].keys()):
            assert listeDicoOK[numVille][cle] == listeVilleDict[numVille][cle]
        assert listeVilleDict[numVille]['Score'] == scoreOK[numVille]

@pytest.mark.parametrize("ville, nomOk, lienOk", [
    ({'nomWkpFr' : "Issendolus"}, "Issendolus", "Issendolus"),
    ({'nomWkpFr' : "Bagnac-sur-Célé"}, "Bagnac-sur-Célé", "Bagnac-sur-C%C3%A9l%C3%A9"),
    ({'nomWkpFr' : "Albas (Lot)"}, "Albas", "Albas%20%28Lot%29"),
    ({'nomWkpFr' : "Puy-l'Évêque"}, "Puy-l'Évêque", "Puy-l%27%C3%89v%C3%AAque"),
    ])
def test_setArticleLiens(ville, nomOk, lienOk):
    """ Test enregistrement nom de ville et URL ville """
    extractionWikipediaFr.setArticleLiens(ville, True)
    assert ville['nom'] == nomOk
    assert ville['lien'] == lienOk

def test_setInseeDep():
    """ Test fonction parsing code pépartement et Insee """
    codeInsee = "46205"
    ville = dict()
    ville['nom'] = "Trifouillis"
    extractionWikipediaFr.setInseeDep(ville, codeInsee, True)
    assert ville['icom'] == "205"
    assert ville['dep'] == "046"

@pytest.mark.parametrize("codeInsee", ["215203", "", "12"])
def test_setInseeDep_Pb(codeInsee):
    """ Test cas erreur fonction parsing code pépartement et Insee """
    ville = dict()
    ville['nom'] = "Trifouillis"
    with pytest.raises(AssertionError):
        extractionWikipediaFr.setInseeDep(ville, codeInsee, True)
