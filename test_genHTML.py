#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name : test_genHTML.py
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
import os
import os.path
import shutil
import configparser
import pytest
import genHTML

def test_enregistreNoticeHTML():
    """ Test ecrire sur disque de la notice """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    numDep = "essai"
    repertoire = config.get('EntreesSorties', 'io.repertoireBase') + '_' + numDep
    if not os.path.isdir(repertoire):
        os.makedirs(repertoire)
    ficResu = config.get('EntreesSorties', 'io.nomFicNoticeHTML')
    pathResuOK = os.path.normcase(os.path.join(repertoire, ficResu))
    if os.path.isfile(pathResuOK):
        os.remove(pathResuOK)

    htmlText = "Salut tout le monde accentué !"
    genHTML.enregistreNoticeHTML(config, numDep, htmlText, True)
    assert os.path.isfile(pathResuOK)
    hFic = open(pathResuOK, 'r')
    page = hFic.read()
    print(page)
    hFic.close()
    assert page == htmlText
    shutil.rmtree(repertoire)

def test_enregistreNoticeHTML_Pbrep():
    """ Test enregistrement répertoire inexistant """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    numDep = "essai"
    htmlText = "Salut tout le monde accentué !"
    repertoire = config.get('EntreesSorties', 'io.repertoireBase') + '_' + numDep
    shutil.rmtree(repertoire, ignore_errors=True)
    with pytest.raises(AssertionError):
        genHTML.enregistreNoticeHTML(config, numDep, htmlText, True)

def test_copieFicAux():
    """ Test copie répertoire des images, et licences """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    numDep = "essai"
    repertoireBase = config.get('EntreesSorties', 'io.repertoireBase')
    repertoireDest = os.path.normcase(repertoireBase + '_' + numDep)
    if not os.path.isdir(repertoireDest):
        os.makedirs(repertoireDest)

    repertoireSource = config.get('EntreesSorties', 'io.RepSrcFicAux')
    repertoireDestTotal = os.path.normcase(os.path.join(repertoireDest, repertoireSource))
    pathFicLogo = os.path.normcase(os.path.join(repertoireDestTotal, "finances_locales_logo.png"))

    genHTML.copieFicAux(config, repertoireDest, True)
    assert os.path.isdir(repertoireDestTotal)
    assert os.path.isfile(pathFicLogo)
    shutil.rmtree(repertoireDest)

def test_copieFicAux_Pbrep():
    """
    Test copie répertoire des images,
    licences dans répertoire de destination inexistant
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    numDep = "essai"
    repertoire = config.get('EntreesSorties', 'io.repertoireBase') + '_' + numDep
    shutil.rmtree(repertoire, ignore_errors=True)
    repertoireBase = config.get('EntreesSorties', 'io.repertoireBase')
    repertoireDest = os.path.normcase(repertoireBase + '_' + numDep)
    with pytest.raises(AssertionError):
        genHTML.copieFicAux(config, repertoireDest, True)

def test_lectureFicModelHTML():
    """ Test Lecture d'un modèle en HTML """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    ficModelHTML = config.get('EntreesSorties', 'io.nomModeleNoticeHTML')
    htmlText = genHTML.litModeleHTML(ficModelHTML, True)
    urlFiLoc = 'https://fr.wikipedia.org/wiki/Utilisateur:Thierry46/Finances_Locales'
    assert urlFiLoc in htmlText

def test_replaceTags():
    """ Test remplacement des mots clés dans un texte modèle """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    ficModelHTML = config.get('EntreesSorties', 'io.nomModeleNoticeHTML')
    htmlText = genHTML.litModeleHTML(ficModelHTML, True)
    assert '++NOM_DEP_STR++' in htmlText
    nbCar = len(htmlText)
    nomDepStr = "Salut petit Coco !"
    assert len(nomDepStr) != len('++NOM_DEP_STR++')
    htmlText = genHTML.replaceTags(config, htmlText, nomDepStr, True)
    assert len(htmlText) != nbCar
    assert nomDepStr in htmlText
    assert '++LIGNES_VILLES++' in htmlText

def test_insertVillesTableau():
    """ Test insertion des lignes du tableux ville de la notice des paquets """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    nom = 'Albas'
    lien = 'Albas (Lot)'
    Score = 25
    avancement = 'BD'
    importanceCDF = 'moyen'
    importanceVDM = 'faible'
    popularite = 'nulle'
    listeVilleDict = [
        {'nom' : nom, 'lien' : lien, 'Score' : Score, 'avancement' : avancement,
         'importanceCDF' : importanceCDF, 'importanceVDM' : importanceVDM,
         'popularite' : popularite}
        ]

    htmlText = 'Bla ++LIGNES_VILLES++ Bla'
    htmlText = genHTML.insertVillesTableau(config, htmlText, listeVilleDict, True)
    assert nom in htmlText
    assert lien in htmlText
    assert str(Score) in htmlText
    assert importanceCDF in htmlText
    assert importanceVDM in htmlText
    assert popularite in htmlText

def test_genHTML():
    """ Test génération de la notice de déploiement d'un paquet """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    nom = 'Albas'
    lien = 'Albas (Lot)'
    Score = 25
    avancement = 'BD'
    importanceCDF = 'moyen'
    importanceVDM = 'faible'
    popularite = 'nulle'
    nomDepStr = 'Coco Dept'
    listeVilleDict = [
        {'nom' : nom, 'lien' : lien, 'Score' : Score, 'avancement' : avancement,
         'importanceCDF' : importanceCDF, 'importanceVDM' : importanceVDM,
         'popularite' : popularite, 'nomDepStr' : nomDepStr}
        ]
    numDep = "essai"
    repertoireDest = config.get('EntreesSorties', 'io.repertoireBase') + '_' + numDep
    if not os.path.isdir(repertoireDest):
        os.makedirs(repertoireDest)

    pathResuOK = os.path.normcase(os.path.join(repertoireDest,
                                               config.get('EntreesSorties',
                                                          'io.nomFicNoticeHTML')))
    if os.path.isfile(pathResuOK):
        os.remove(pathResuOK)

    genHTML.genNoticeHTML(config, numDep, listeVilleDict, True)

    assert os.path.isfile(pathResuOK)
    hFic = open(pathResuOK, 'r')
    page = hFic.read()
    hFic.close()
    assert nom in page
    assert lien in page
    assert str(Score) in page
    assert importanceCDF in page
    assert importanceVDM in page
    assert popularite in page
    assert nomDepStr in page
    shutil.rmtree(repertoireDest)

def test_convertWikicode2Html():
    """ Test l'insertion du wikicode d'une ville dans un fichier HTML """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    pathVille = 'essai/Issendolus_detail.txt'
    assert os.path.isfile(pathVille)
    genHTML.convertWikicode2Html(config, pathVille, True)
    ficResu = pathVille.replace('.txt', '.html')
    htmlText = genHTML.litModeleHTML(ficResu, True)
    assert os.path.isfile(ficResu)
    assert '<PRE>' in htmlText
    assert '</PRE>' in htmlText
    assert '++CODE++' not in htmlText


