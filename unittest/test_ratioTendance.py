#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name : test_ratioTendance.py
Author : Thierry Maillard (TMD)
Date : 5/8/2019
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
import os.path
import configparser
import pytest
import ratioTendance

import database

# Atention les seuils définis dans les properties sont pris en compte
# Pb si modif seuils dans .properties.
@pytest.mark.parametrize(\
    "dictDetteCaf,dicoRatioOk",
    [
        ({2013:[25, 1], 2012:[23, 1], 2011:[24, 1]},
         {2013:25, 2012:23, 2011:24}),
        ({2013:[25, 20], 2012:[23, 21], 2011:[24, 18]},
         {2013:1, 2012:1, 2011:1}),
        ({2013:[10, 20], 2012:[7, 21], 2011:[12, 18]},
         {2013:0, 2012:0, 2011:0}),
        ({2013:[10, 1], 2012:[7, 1], 2011:[12, 1]},
         {2013:10, 2012:7, 2011:12}),
        ({2013:[10, 1], 2012:[7, 1], 2011:[75, 1]},
         {2013:10, 2012:7, 2011:50}),
    ])
def test_calculeRatioDetteCAF(dictDetteCaf, dicoRatioOk):
    """ Test fonction évaluation du ratio dette/caf """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    dictRatio = ratioTendance.calculeRatioDetteCAF(config, dictDetteCaf, True)
    assert dictRatio == dicoRatioOk

# Atention les seuils définis dans les properties sont pris en compte
# Pb si modif seuils dans .properties.
@pytest.mark.parametrize(\
    "dictDetteCaf, chOK",
    [
        ({2013:[25, 1], 2012:[23, 1], 2011:[24, 1]},
         "est constant et élevé (supérieur à"),
        ({2013:[25, 1], 2012:[23, 1], 2011:[24, 1]},
         "15"),
        ({2013:[10, 20], 2012:[7, 21], 2011:[12, 18]},
         "4"),
        ({2013:[10, 1], 2012:[7, 1], 2011:[12, 1]},
         "7"),
        ({2013:[10, 1], 2012:[7, 1], 2011:[12, 1]},
         "maximum"),
        ({2013:[10, 1], 2012:[7, 1], 2011:[12, 1]},
         "7"),
        ({2013:[10, 1], 2012:[7, 1], 2011:[12, 1]},
         "12"),
        ({2013:[10, 1], 2012:[7, 1], 2011:[12, 1]},
         "minimum d'environ"),
        ({2013:[10, 1], 2012:[7, 1], 2011:[12, 1]},
         "maximum d'environ"),
        ({2013:[10, 1], 2012:[7, 1], 2011:[75, 1]},
         "50"),
    ])
def test_presentEvolRatio(dictDetteCaf, chOK):
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    dictRatio = ratioTendance.calculeRatioDetteCAF(config, dictDetteCaf, False)
    assert chOK in ratioTendance.presentEvolRatio(config, dictRatio, True, True)

def test_presentEvolRatio_pb1515():
    """ Test cas erreur fonction présentation du ratio dette/caf """
    dictDetteCaf = {2002:[10740000,872000], 2003:[11237000,1128000],
                    2000:[780000,8608000], 2001:[9461000,741000],
                    2006:[10489000,1016000], 2007:[12347000,684000],
                    2004:[9947000,897000], 2005:[9883000,1100000],
                    2008:[14525000,645000], 2009:[13603000,1088000],
                    2011:[12647000,1065000], 2010:[13731000,945000],
                    2013:[12284000,834000], 2012:[11696000,656000]}
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    dictRatio = ratioTendance.calculeRatioDetteCAF(config, dictDetteCaf, True)
    assert dictRatio[2008] == 22
    strTendance = ratioTendance.presentEvolRatio(config, dictRatio, True, True) 
    assert '1515' not in strTendance
    assert '22 an' in strTendance

@pytest.mark.parametrize(\
    "ratio,ch",
    [
        (0, "de moins d'un an"),
        (1, "d'environ un an"),
        (10, "10 an"),
        (10, "d'environ"),
        (22, "22 an"),
        (22, "élevé"),
        (50, "50 an"),
        (50, "très élevé"),
        (75, "75 an"),
        (75, "très élevé")
    ])
def test_presentRatioDettesCAF(ratio, ch):
    """ Test génération phrase décrivant un ratio """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    assert ch in ratioTendance.presentRatioDettesCAF(config, ratio, True, True)

def test_getTendanceRatioDetteCAF():
    """ Test calcule de tendance du rapport dette/CAF """
    
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
    assert os.path.isfile(databasePath)
    assert connDB

    # Insertion données dette et CAF pour une commune
    codeDette = config['cleFi3Valeurs']["clefi.encours de la dette au 31 12 n"]
    codeCAF = config['cleFi3Valeurs']["clefi.capacité autofinancement caf"]
    connDB.executemany("""
        INSERT INTO dataFi(codeCommune, annee, codeCle, valeur)
        VALUES (?, ?, ?, ?)
        """,
            (
                ('001008', 2000, codeCAF, 1), ('001008', 2001, codeCAF, 1),
                ('001008', 2002, codeCAF, 1),
                ('001008', 2000, codeDette, 25), ('001008', 2001, codeDette, 23),
                ('001008', 2002, codeDette, 24)
            ))
    connDB.commit()
    
    # Récupère toutes les données concernant cette ville
    dictAllGrandeur = database.getAllValeurs4Ville(connDB, '001008', False)
    listAnnees = database.getListeAnnees4Ville(connDB, '001008', False)

    # Test
    tendanceRatio, dicoRatio = ratioTendance.getTendanceRatioDetteCAF(config, dictAllGrandeur,
                                                                      True, True)
    assert "est constant et élevé (supérieur à" in tendanceRatio
    
    database.closeDatabase(connDB, True)

