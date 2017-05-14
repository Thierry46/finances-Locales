#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name : test_utilitaires.py
Author : Thierry Maillard (TMD)
Date : 1/6/2015 - 13/9/2015
Role : Tests unitaires du projet FinancesLocales avec py.test
        not global : élimine les tests globaux très long
Utilisation : python3 -m pytest -k "not global" .
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


# V1.0.5 : Délai entre deux requêtes au MinFi
def test_wait2requete():
    """ Test fonction de génération de délai entre 2 requ^tes HTTP """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    delaiEntre2Requetes = config.getfloat('Extraction', 'extraction.delaiEntre2Requetes')

    # Il ne doit pas y avoir de délai inséré lors du premier appel
    t0 = time.time()
    utilitaires.wait2requete(config, True)
    t1 = time.time()
    assert (t1 - t0) < 1.0

    # Pour les appels suivants, le délai doit s'appliquer
    for i in range(4):
        print("Essai", i+1)
        t2 = time.time()
        utilitaires.wait2requete(config, True)
        t3 = time.time()
        assert (t3 - t2) >= delaiEntre2Requetes * 0.9 # A 10% près voir notice sleep python

# V1.0.5 : On n'extrait pas deux fois un même fichier
def test_isCommuneDejaExtraite():
    """ Test fonction qui renvoie vrai si une comune a déjà été extraite """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    ville = dict()
    ville['nom'] = 'Existe'
    ville['dep'] = '099'

    # Création du répertoire et de la ville
    repertoire = "Resultats_Extractions_99"
    if not os.path.isdir(repertoire):
        os.makedirs(repertoire)
    ficResu = ville['nom'] + '_bd_minfi.txt'
    path = os.path.normcase(os.path.join(repertoire, ficResu))
    if not os.path.isfile(path):
        hFic = open(path, 'w')
        hFic.close()
    dejaExtraite = utilitaires.isCommuneDejaExtraite(config, ville, True)
    assert dejaExtraite

    ville['nom'] = 'QueDalle'
    ficResu = ville['nom'] + '_bd_minfi.txt'
    path = os.path.normcase(os.path.join(repertoire, ficResu))
    if os.path.isfile(path):
        os.remove(path)
    dejaExtraite = utilitaires.isCommuneDejaExtraite(config, ville, True)
    assert not dejaExtraite

    # Nettoyage
    shutil.rmtree(repertoire)

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

