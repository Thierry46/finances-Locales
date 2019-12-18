#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name : test_utilitaires.py
Author : Thierry Maillard (TMD)
Date : 1/6/2015 - 12/11/2019
Role : Tests unitaires du projet FinancesLocales avec py.test
Utilisation : python3 -m pytest .
 options :
    -s : pour voir les sorties sur stdout
Ref : http://sametmax.com/un-gros-guide-bien-gras-sur-les-tests-unitaires-en-python-partie-3/
Ref : http://pytest.org/latest/
prerequis : pip install pytest

#Licence : GPLv3
#Copyright (c) 2015 - Thierry Maillard

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
import time
import pytest
import utilitaires

@pytest.mark.parametrize(\
    "repertoire, nomArticle, indicateur, ch",
    [
        ("", "", "i1", "_i1.txt"),
        ("", "Issendolus", "i1", "Issendolus_i1.txt"),
        ("essai", "Issendolus", "i1", "essai/Issendolus_i1.txt"),
    ])
def test_construitNomFic(repertoire, nomArticle, indicateur, ch):
    """ Test la génération d'un nom de fichier """
    assert ch in utilitaires.construitNomFic(repertoire, nomArticle,
                                             indicateur, '.txt')

@pytest.mark.parametrize(\
    "arrive, depart, attendu", [
        (0., 0., 0.),
        (200., 100., 100.),
        (100., 200., -50.)
    ])
def test_calculAugmentation(arrive, depart, attendu):
    """ Test fonction de calcul d'une augmentation """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    assert abs(attendu - utilitaires.calculAugmentation(config, arrive, depart)) < 1e-3

# V1.0.2 : Accessibilité : texte alternatif
@pytest.mark.parametrize(\
    "ratio, picto, alt",
    [
        (0., "picto.ecartNul", "picto.ecartNulAlt"),
        (5., "picto.ecartNul", "picto.ecartNulAlt"),
        (-5., "picto.ecartNul", "picto.ecartNulAlt"),
        (10., "picto.ecartMoyen", "picto.ecartMoyenAlt"),
        (-10., "picto.ecartMoyen", "picto.ecartMoyenAlt"),
        (25., "picto.ecartMoyen", "picto.ecartMoyenAlt"),
        (-25., "picto.ecartMoyen", "picto.ecartMoyenAlt"),
        (30., "picto.ecartFort", "picto.ecartFortAlt"),
        (-30., "picto.ecartFort", "picto.ecartFortAlt"),
        (100., "picto.ecartFort", "picto.ecartFortAlt"),
        (-100., "picto.ecartFort", "picto.ecartFortAlt"),
    ])
def test_choixPicto(ratio, picto, alt):
    """ Test fonction de choix d'un picto en fonction de valeurs d'écart """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    pictoResu, altResu = utilitaires.choixPicto(config, ratio, True)
    assert pictoResu == config.get('Picto', picto)
    assert altResu == config.get('Picto', alt)

@pytest.mark.parametrize(\
    "valeurN, valeurNM1, tendance",
    [
        (0., 0., ["égale", "sans variation", "constante"]),
        (103., 103., ["égale", "sans variation", "constante"]),
        (1., 1.02, ["quasiment"]),
        (1., 0.5, ["supérieure"]),
        (0.5, 1., ["inférieure"]),
        (100., 0.5, ["très supérieure"]),
        (0.5, 100., ["très inférieure"]),
    ])
def test_calculeTendance(valeurN, valeurNM1, tendance):
    """ Test fonction qui qualifie la variation entre deux valeurs annuelles """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    ok = False
    tendanceResu = utilitaires.calculeTendance(config, valeurN, valeurNM1)
    for tendanceVal in tendance:
        if tendanceVal in tendanceResu:
            ok = True
    assert ok

@pytest.mark.parametrize(\
    "nomValeur, dictAneeesValeur, minAnneeOK, maxAnneeOK," + \
    "croissanteOK, decroissanteOK, constanteOK",
    [
        ("TestEgale", {"2000":10, "2002":10, "2003":10, "2004":10, "2005":10},
         "2005", "2005", False, False, True),
        ("TestCroissant", {"2000":10, "2001":20, "2002":25, "2003":30, "2004":50},
         "2000", "2004", True, False, False),
        ("TestDecroissant", {"2000":100, "2001":70, "2002":60, "2003":20, "2004":10},
         "2004", "2000", False, True, False),
        ("TestFluctue", {"2000":100, "2001":70, "2002":160, "2003":20, "2004":10},
         "2004", "2002", False, False, False),
        ("TestManqueAnneeEgale", {"2000":10, "2002":10, "2004":10, "2005":10},
         "2005", "2005", False, False, True),
        ("TestManqueAnneeCroissant", {"2000":10, "2001":20, "2002":25, "2004":50},
         "2000", "2004", True, False, False),
        ("TestManqueAnneeDecroissant", {"2000":100, "2001":70, "2002":60, "2004":10},
         "2004", "2000", False, True, False),
        ("TestManqueAnneeFluctue", {"2000":100, "2001":70, "2002":160, "2004":10},
         "2004", "2002", False, False, False),
        ("TestPbCAFLunegarde", {"2013":215, "2012":230, "2011":397, "2010":-497},
         "2010", "2011", False, False, False),
        ("TestPbCAFLunegarde2", {"2013":215, "2012":230, "2011":397},
         "2013", "2011", False, True, False),
    ])
def test_calculeTendanceSerieBase(nomValeur, dictAneeesValeur,
                                  minAnneeOK, maxAnneeOK, croissanteOK,
                                  decroissanteOK, constanteOK):
    """ Test fonction de base qui évalue la variation des valeurs d'une série """
    minAnnee, maxAnnee, croissante, decroissante, constante = \
        utilitaires.calculeTendanceSerie(nomValeur, dictAneeesValeur, True)
    assert minAnnee == minAnneeOK
    assert maxAnnee == maxAnneeOK
    assert decroissante == decroissanteOK
    assert constante == constanteOK
    assert croissante == croissanteOK

@pytest.mark.parametrize(\
    "nomValeur, dictAneeesValeur, unite, strTendanceOK",
    [
        ("TestEgaleTendance",
         {"2000":10, "2002":10, "2003":10, "2004":10, "2005":10},
         "", "constant et proche de"),
        ("TestEgaleVal",
         {"2000":10, "2002":10, "2003":10, "2004":10, "2005":10},
         "", "10"),
        ("TestEgalUnite",
         {"2000":10, "2002":10, "2003":10, "2004":10, "2005":10},
         "Zorglub", "Zorglub"),
        ("TestNom",
         {"2000":10, "2002":10, "2003":10, "2004":10, "2005":10},
         "", "TestNom"),
        ("TestCroissantTendance",
         {"2000":10, "2001":20, "2002":25, "2003":30, "2004":50},
         "", "augmente de façon continue de"),
        ("TestCroissantMin",
         {"2000":10, "2001":20, "2002":25, "2003":30, "2004":50},
         "", "10"),
        ("TestCroissantMax",
         {"2000":10, "2001":20, "2002":25, "2003":30, "2004":50},
         "", "50"),
        ("TestCroissantUnite",
         {"2000":10, "2001":20, "2002":25, "2003":30, "2004":50},
         "Zorglub", "Zorglub"),
        ("TestDecroissantTendance",
         {"2000":100, "2001":50, "2002":20, "2003":10},
         "", "diminue de façon continue de"),
        ("TestDecroissantMax",
         {"2000":100, "2001":70, "2002":60, "2003":20},
         "", "100"),
        ("TestDecroissantMin",
         {"2000":100, "2001":70, "2002":60, "2003":21},
         "", "21"),
        ("TestDecroissantUnite",
         {"2000":100, "2001":70, "2002":60, "2003":21},
         "Zorglub", "Zorglub"),
        ("TestFluctueTendance",
         {"2000":100, "2001":70, "2002":160, "2003":20, "2004":10},
         "", "fluctue et présente"),
        ("TestFluctueMinAnnee",
         {"2000":100, "2001":70, "2002":160, "2003":20, "2004":10},
         "", "2004"),
        ("TestFluctueMinValeur",
         {"2000":100, "2001":70, "2002":160, "2003":20, "2004":10},
         "", "10"),
        ("TestFluctueMaxAnnee",
         {"2000":100, "2001":70, "2002":160, "2003":20, "2004":10},
         "", "2002"),
        ("TestFluctueMaxValeur",
         {"2000":100, "2001":70, "2002":160, "2003":20, "2004":10},
         "", "160"),
        ("TestFluctueMaxUnite",
         {"2000":100, "2001":70, "2002":160, "2003":20, "2004":10},
         "Zorglub", "Zorglub"),
    ])
def test_calculeTendanceSerieStr1(nomValeur, dictAneeesValeur,
                                  unite, strTendanceOK):
    """ Test Génération phrase de qualification de l'évolution d'une série """
    strTendance = \
        utilitaires.calculeTendanceSerieStr(nomValeur, dictAneeesValeur,
                                            unite, True, True)
    assert strTendanceOK in strTendance

@pytest.mark.parametrize(\
    "nomValeur, dictAneeesValeur, unite, strTendanceOK1, strTendanceOK2",
    [
        ("TestNbAnnees1",
         {"2000":100, "2001":70, "2002":160, "2003":20, "2004":10},
         "", "2000", "5"),
        ("TestNbAnnees2",
         {"2000":100, "2001":70, "2002":160, "2003":20, "2004":10},
         "", "2004", "5")
    ])
def test_calculeTendanceSerieStr2(nomValeur, dictAneeesValeur,
                                  unite, strTendanceOK1,
                                  strTendanceOK2):
    """
    Test Génération phrase de qualification de l'évolution d'une série
    v1.2.1 : Ajout suite utilisation random.choice()
    """
    strTendance = \
        utilitaires.calculeTendanceSerieStr(nomValeur, dictAneeesValeur,
                                            unite, True, True)
    assert strTendanceOK1 in strTendance or strTendanceOK2 in strTendance

@pytest.mark.parametrize(\
    "option, verboseOK, sortiePgmOK",
    [
        ("-h", False, True),
        ("--help", False, True),
        ("-u", False, True),
        ("--usage", False, True),
        ("-v", True, False),
        ("--verbose", True, False),
        ("-V", False, True),
        ("--version", False, True),
    ])
def test_traiteOptionStd(option, verboseOK, sortiePgmOK):
    """ Test fonction d'analyse des options courantes """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    verbose, sortiePgm = utilitaires.traiteOptionStd(config, option,
                                                     "Test", "Doc", [])
    assert verbose == verboseOK
    assert sortiePgm == sortiePgmOK

# V1.3.0 : Wikicode + HTML
@pytest.mark.parametrize(\
    "valeur, isWikicode, resultOK",
    [
        ("5", True, "{{euro|5}}"),
        ("5", False, "5&nbsp;€"),
    ])
def test_modeleEuro(valeur, isWikicode, resultOK):
    """ Test fonction de formattage valeur Euro """
    assert utilitaires.modeleEuro(valeur, isWikicode) == resultOK

# V2.4.0 : Conversion caractères accentués ou interdits dans un nom de fichier
@pytest.mark.parametrize(\
    "valeur, resultOK",
    [
        ("àãáâa", "a"*5),
        ("ÀÃÁÂA", "A"*5),
        ("éèêëe", "e"*5),
        ("ÉÈÊËE", "E"*5),
        ("îïi", "i"*3),
        ("ÎÏI", "I"*3),
        ("ab/cd/AB", "ab/cd/AB"),
        ("ùüû", "u"*3),
        ("ÙÜÛ", "U"*3),
        ("ôö", "o"*2),
        ("ÔÖ", "O"*2),
        ("œæç", "oeaec"),
        ("ŒÆÇ", "OEAEC"),
        ("(1)", "_1_"),
    ])
def test_convertLettresAccents(valeur, resultOK):
    """ Test Conversion caractères accentués ou interdits """
    assert utilitaires.convertLettresAccents(valeur) == resultOK

def test_merge2Dict():
    """ Test fusion de liste """
    dict1 = {2009:2.4, 2010:12.4, 2013:122.4, 2015:0.4}
    dict2 = {2008:-5.4, 2010:112.4, 2013:522.4}

    # Test
    assert utilitaires.merge2Dict(dict1, dict2, True)  == \
           {2010:[12.4, 112.4], 2013:[122.4, 522.4]}

def test_lectureFiltreModele():
    """ Test Lecture modele """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Recup chemin modele
    modelePathDir = config.get('Test', 'modele.testDir')
    modelePath = os.path.join(modelePathDir, config.get('Test', 'modele.testName'))
    
    # Test extraction reduite du modele
    page = utilitaires.lectureFiltreModele(modelePath, False, True)
    assert "Ligne début" in page
    assert "Ligne complet" not in page
    assert "Ligne fin" in page
    assert "COMPLET" not in page

    # Test extraction reduite du modele
    page = utilitaires.lectureFiltreModele(modelePath, True, True)
    assert "Ligne début" in page
    assert "Ligne complet" in page
    assert "Ligne fin" in page
    assert "COMPLET" not in page

@pytest.mark.parametrize(\
    "dictAllGrandeurAnneeValeur, listAnneesOK, resultOK",
    [
        ({"g1":{1990:2e3, 1995:2e4, 2000:2e0},
          "g2":{1990:2e7, 1995:2e6, 2000:2e8}},
         [1990, 1995, 2000],
         (1, 'k€', "millier d'euros (k€)")),
        ({"g1":{1990:2e3, 1995:2e4, 2000:2e0},
          "g2":{1990:2e7, 1995:2e6, 2000:2e8}},
          [1990, 1995],
         (1e-3, 'M€', "million d'euros (M€)")),
    ])
def test_setArrondi_OK(dictAllGrandeurAnneeValeur, listAnneesOK, resultOK):
    """ Test fonction de détermination des arrondis """
    assert utilitaires.setArrondi(dictAllGrandeurAnneeValeur, listAnneesOK,
                                  1000.0, None,
                                  True) == \
           resultOK

@pytest.mark.parametrize(\
    "dictAllGrandeurAnneeValeur, listAnneesOK, msgOk",
    [
        ({"g1":{1990:'a', 1995:2e4, 2000:2e0},
          "g2":{1990:2e7, 1995:2e6, 2000:2e8}},
         [1990, 1995, 2000],
         "1990"),
        ({}, [1990, 1995], "pas de valeurs à arrondir"),
        ({"g1":{1990:'2e3', 1995:2e4, 2000:2e0},
          "g2":{1990:2e7, 1995:2e6, 2000:2e8}},
          [],
         "aucune année de sélection"),
    ])
def test_setArrondi_PB(dictAllGrandeurAnneeValeur, listAnneesOK, msgOk):
    """ Test erreurs fonction de détermination des arrondis """
    with pytest.raises(ValueError, match=msgOk):
        utilitaires.setArrondi(dictAllGrandeurAnneeValeur, listAnneesOK,
                                  1000.0, None,
                                  True) 

@pytest.mark.parametrize("nomVille, repertoireDepBase, dictOK",
    [
        ["Issendolus", "parentDir",
         {'nom':'Issendolus', 'villeNomDisque':'Issendolus',
                        'nomRelatifIndexVille':'Issendolus/Issendolus',
                        'villeWikicode':'Issendolus/Issendolus_wikicode.html',
                        'villeHtml':'Issendolus/Issendolus.html',
                        'repVille':'parentDir/Issendolus'}],
        ["Boissières", "parentDir",
         {'nom':'Boissières', 'villeNomDisque':'Boissieres',
                        'nomRelatifIndexVille':'Boissieres/Boissieres',
                        'villeWikicode':'Boissieres/Boissieres_wikicode.html',
                        'villeHtml':'Boissieres/Boissieres.html',
                        'repVille':'parentDir/Boissieres'}]
    ])
def test_getNomsVille(nomVille, repertoireDepBase, dictOK):
    """ Test fonction de génération des noms de villes """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    assert utilitaires.getNomsVille(config,
                                    nomVille,
                                    repertoireDepBase,
                                    True)  == dictOK
