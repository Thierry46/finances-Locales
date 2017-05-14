#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name : test_global.py
Author : Thierry Maillard (TMD)
Date : 2/8/2015 - 13/9/2015
Role : Tests unitaires globaux du projet FinancesLocales avec py.test
Utilisation : python3 -m pytest -s -k global .
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
import shutil
import os
import os.path

import extractionWeb
import utilitaires
import genCode
import genSiteWeb
import genCleFi

def test_globalExtractionWeb1Ville():
    """
    Test global d'extraction d'une commune seulement
    du site du Ministère des finances
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Suppression Résultats run precédents
    repertoireBase = config.get('EntreesSorties', 'io.repertoireExtractions')
    numDep = config.get('Test', 'test.numDepvilleExtraction')
    repertoire = os.path.normcase(repertoireBase + '_' + numDep)
    shutil.rmtree(repertoire, ignore_errors=True)

    villeExtraction = config.get('Test', 'test.villeExtraction')
    param = ['extractionWeb.py', villeExtraction]
    extractionWeb.main(param)

    assert os.path.isdir(repertoire)
    indicateurNomFicBd = config.get('EntreesSorties', 'io.indicateurNomFicBd')
    ficVille = utilitaires.construitNomFic(repertoire, villeExtraction,
                                           indicateurNomFicBd, '.txt')
    assert os.path.isfile(ficVille)
    villeTailleResuOk = int(config.get('Test', 'test.villeTailleResu'))
    villeTailleTolerance = float(config.get('Test', 'test.villeTailleTolerance'))
    tailleResu = os.path.getsize(ficVille)
    assert abs(tailleResu - villeTailleResuOk) <= villeTailleResuOk * villeTailleTolerance

    # Test 2ème extraction de la même ville
    extractionWeb.main(param)
    tailleResu2 = os.path.getsize(ficVille)
    assert tailleResu == tailleResu2

def test_globalExtractionWeb1Departement():
    """
    Test global d'extraction des communes d'un département
    du site du Ministère des finances
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Suppression Résultats run precédents
    repertoireBase = config.get('EntreesSorties', 'io.repertoireExtractions')
    numDep = config.get('Test', 'test.numDepDepartementExtraction')
    repertoire = os.path.normcase(repertoireBase + '_' + numDep)
    shutil.rmtree(repertoire, ignore_errors=True)

    depExtraction = config.get('Test', 'test.departementExtraction')
    param = ['extractionWeb.py', depExtraction]
    extractionWeb.main(param)

    assert os.path.isdir(repertoire)
    indicateurNomFicBd = config.get('EntreesSorties', 'io.indicateurNomFicBd')
    listFicRepertoire = [fic for fic in os.listdir(repertoire)
                         if fic.endswith(indicateurNomFicBd + '.txt')]
    nbFicDepartementExtractionOk = int(config.get('Test', 'test.nbFicDepartementExtraction'))
    assert len(listFicRepertoire) == nbFicDepartementExtractionOk

def test_globalGenCode1Departement():
    """ Test de génération du Wikicode pour toutes les villes d'un département """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    repertoireBase = config.get('EntreesSorties', 'io.repertoireExtractions')
    numDep = config.get('Test', 'test.numDepDepartementExtraction')
    repertoire = os.path.normcase(repertoireBase + '_' + numDep)
    assert os.path.isdir(repertoire), 'test dependant de test_globalExtractionWeb1Departement'

    indicateurNomFicBd = config.get('EntreesSorties', 'io.indicateurNomFicBd')
    listFicRepertoireExtraction = [fic for fic in os.listdir(repertoire)
                                   if fic.endswith(indicateurNomFicBd + '.txt')]
    nbFicDepartementExtractionOk = int(config.get('Test', 'test.nbFicDepartementExtraction'))
    assert len(listFicRepertoireExtraction) == nbFicDepartementExtractionOk, \
        'test dependant de test_globalExtractionWeb1Departement'

    # Suppression Résultats run precédents
    repertoireBase = config.get('EntreesSorties', 'io.repertoireBase')
    repertoireHTML = os.path.normcase(repertoireBase + '_' + numDep)
    shutil.rmtree(repertoireHTML, ignore_errors=True)

    param = ['genCode.py', numDep]
    genCode.main(param)

    assert os.path.isdir(repertoireHTML)

    listFicRepertoireDep = [fic for fic in os.listdir(repertoireHTML)]
    assert len(listFicRepertoireDep) == nbFicDepartementExtractionOk + 1
    nomFicIndexHTML = config.get('EntreesSorties', 'io.nomFicIndexHTML')
    assert nomFicIndexHTML in listFicRepertoireDep
    idFicDetail = config.get('GenCode', 'gen.idFicDetail')
    for villesExtraction in listFicRepertoireExtraction:
        ville = villesExtraction.replace('_' + indicateurNomFicBd + '.txt', '')
        assert ville in listFicRepertoireDep
        repVille = os.path.join(repertoireHTML, ville)
        listFicVille = [fic for fic in os.listdir(repVille)
                        if fic.endswith('.html')]
        assert ville + '.html' in listFicVille
        assert ville + '_' + idFicDetail + '.html' in listFicVille

def test_globalGenSiteWeb():
    """ Test global génération des paquets de déploiement """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    repertoireBase = config.get('EntreesSorties', 'io.repertoireBase')
    numDep = config.get('Test', 'test.numDepDepartementExtraction')
    repertoireHTML = os.path.normcase(repertoireBase + '_' + numDep)
    assert os.path.isdir(repertoireHTML), 'test dependant de test_globalGenWikicode1Departement'

    # Suppression Résultats run precédents
    repTransfertWeb = config.get('EntreesSorties', 'io.repTransfertWeb')
    shutil.rmtree(repTransfertWeb, ignore_errors=True)

    param = ['genSiteWeb.py', '-v']
    genSiteWeb.main(param)

    assert os.path.isdir(repTransfertWeb)
    repSrcFicAux = config.get('EntreesSorties', 'io.RepSrcFicAux')
    pathRepSrcFicAux = os.path.join(repTransfertWeb, repSrcFicAux)
    assert os.path.isdir(pathRepSrcFicAux)
    nomNoticeDeploiement = config.get('EntreesSorties', 'io.nomNoticeDeploiement')
    pathNoticeDeploiement = os.path.join(repTransfertWeb, nomNoticeDeploiement)
    assert os.path.isfile(pathNoticeDeploiement)

def test_globalGenCleFi():
    """ Test génération des clés d'extraction """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Suppresion run précedents
    nomFicCleFi = config.get('Extraction', 'extraction.ficCleFi')
    if os.path.isfile(nomFicCleFi):
        os.remove(nomFicCleFi)
    nomFicCleFiDetail = config.get('Extraction', 'extraction.ficCleFiDetail')
    if os.path.isfile(nomFicCleFiDetail):
        os.remove(nomFicCleFiDetail)

    genCleFi.main()

    assert os.path.isfile(nomFicCleFi)
    assert os.path.isfile(nomFicCleFiDetail)
 