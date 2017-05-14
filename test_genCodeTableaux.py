#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name : test_genCodeTableaux.py
Author : Thierry Maillard (TMD)
Date : 1/6/2015 - 22/10/2015
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
import pytest

import genCodeTableaux

@pytest.mark.parametrize(\
    "dictValeurs",
    [
        ({"gros" : {"Valeur totale" : 1000, "En moyenne pour la strate" : 0,
                    "Par habitant" : 0},
          "petit" : {"Valeur totale" : 2, "En moyenne pour la strate" : 0,
                     "Par habitant" : 0}
         }),
        ({"petit" : {"Valeur totale" : 2, "En moyenne pour la strate" : 0,
                     "Par habitant" : 0},
          "gros" : {"Valeur totale" : 1000, "En moyenne pour la strate" : 0,
                    "Par habitant" : 0}
         }),
        ({"petit" : {"Valeur totale" : 2, "En moyenne pour la strate" : 0,
                     "Par habitant" : 0},
          "moyen" : {"Valeur totale" : 500, "En moyenne pour la strate" : 0,
                     "Par habitant" : 0},
          "gros" : {"Valeur totale" : 1000, "En moyenne pour la strate" : 0,
                    "Par habitant" : 0}
         }),
    ])
def test_triPourCent_Tri(dictValeurs):
    """
    Test Fonction du tri des valeurs en fonction de leur contribution à
    la somme totale (ordre des valeurs résultat)
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    cletrie = genCodeTableaux.triPourCent(config, 500, dictValeurs, False, True, True)
    assert len(cletrie) == len(dictValeurs)
    assert cletrie[0] == "gros"
    assert cletrie[-1] == "petit"

@pytest.mark.parametrize(\
    "dictValeurs",
    [
        ({"gros" : {"Valeur totale" : 1000, "En moyenne pour la strate" : 0,
                    "Par habitant" : 0},
          "petit" : {"Valeur totale" : 100, "En moyenne pour la strate" : 0,
                     "Par habitant" : 0}
         }),
        ({"petit" : {"Valeur totale" : 100, "En moyenne pour la strate" : 0,
                     "Par habitant" : 0},
          "gros" : {"Valeur totale" : 1000, "En moyenne pour la strate" : 0,
                    "Par habitant" : 0}
         }),
        ({"petit" : {"Valeur totale" : 100, "En moyenne pour la strate" : 0,
                     "Par habitant" : 0},
          "moyen" : {"Valeur totale" : 500, "En moyenne pour la strate" : 0,
                     "Par habitant" : 0},
          "gros" : {"Valeur totale" : 1000, "En moyenne pour la strate" : 0,
                    "Par habitant" : 0}
         }),
    ])
def test_triPourCent_ratioValeur(dictValeurs):
    """
    Test Fonction du tri des valeurs en fonction de leur contribution à
    la somme totale (% calculés)
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    sommeValeurTotal = 500
    genCodeTableaux.triPourCent(config, sommeValeurTotal,
                                dictValeurs, False, True, True)
    for defValeur in list(dictValeurs.keys()):
        assert abs(dictValeurs[defValeur]['ratioValeur'] -
                   ((float(dictValeurs[defValeur]["Valeur totale"]) * 100.0) /
                    float(sommeValeurTotal))) < 1
        assert "%1.f"%dictValeurs[defValeur]['ratioValeur'] in \
               dictValeurs[defValeur]['ratioValeurStr']

def test_triPourCent_Strate0():
    """
    Test Fonction du tri des valeurs en fonction de leur contribution à
    la somme totale (valeur strate)
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    sommeValeurTotal = 500
    dictValeurs = {"gros" : {"Valeur totale" : 1000, "En moyenne pour la strate" : 0,
                             "Par habitant" : 0}}
    cletrie = genCodeTableaux.triPourCent(config, sommeValeurTotal,
                                          dictValeurs, False, True, True)
    assert len(cletrie) == 1
    assert dictValeurs["gros"]['ratioStrate'] == 0.0
    assert "voisin" in dictValeurs["gros"]['ratioStrateStr']
    assert dictValeurs["gros"]['ratioStratePicto'] == config.get('Picto', 'picto.ecartNul')

def test_triPourCent_Valeur0():
    """
    Test Fonction du tri des valeurs en fonction de leur contribution à
    la somme totale (valeur 0)
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    sommeValeurTotal = 1000
    dictValeurs = {"Nul" : {"Valeur totale" : 0, "En moyenne pour la strate" : 0,
                            "Par habitant" : 0}}
    cletrie = genCodeTableaux.triPourCent(config, sommeValeurTotal,
                                          dictValeurs, False, True, True)
    ratioStr = dictValeurs["Nul"]['ratioValeurStr']
    assert len(cletrie) == 1
    assert dictValeurs["Nul"]['ratioValeur'] < 1.0
    assert "inférieures" in ratioStr or "faibles" in ratioStr or "négligeables" in ratioStr

@pytest.mark.parametrize(\
    "dictValeurs, ecart, ecartStr, picto",
    [
        ({"ecartpc100" : {"Valeur totale" : 1000, "En moyenne pour la strate" : 10,
                          "Par habitant" : 20}},
         100., "supérieur", "picto.ecartFort"),
        ({"ecartpcm100" : {"Valeur totale" : 1000, "En moyenne pour la strate" : 20,
                           "Par habitant" : 10}},
         -50., "inférieur", "picto.ecartFort"),
        ({"ecartpc1" : {"Valeur totale" : 1000, "En moyenne pour la strate" : 100,
                        "Par habitant" : 101}},
         1, "voisin", "picto.ecartNul")
    ])
def test_triPourCent_StrateVal(dictValeurs, ecart, ecartStr, picto):
    """
    Test Fonction du tri des valeurs en fonction de leur contribution à
    la somme totale (valeur de la strate)
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    sommeValeurTotal = 500
    genCodeTableaux.triPourCent(config, sommeValeurTotal,
                                dictValeurs, False, True, True)
    defValeur = list(dictValeurs.keys())[0]
    assert abs(dictValeurs[defValeur]['ratioStrate'] - ecart) < 1.0
    assert ecartStr in dictValeurs[defValeur]['ratioStrateStr']
    assert dictValeurs[defValeur]['ratioStratePicto'] == config.get('Picto', picto)

@pytest.mark.parametrize("unite", ["euro", "%"])
def test_genlignesTableauPicto(unite):
    """
    Test Fonction de génération des lignes d'un tableau de pictogramme
    qui qualifie une commune par rapport à sa strate
    """
    motCle = 'CHARGE'
    couleur = "#ffd9ff"
    nbLignes = 3
    lignes = genCodeTableaux.genlignesTableauPicto(motCle, nbLignes,
                                                   couleur, unite,
                                                   True, True)
    assert len(lignes) == nbLignes
    numLigne = 1
    for ligne in lignes:
        for ch in [motCle, couleur, str(numLigne),
                   '<LIBELLE_PICTO_', 'row', 'VALEUR',
                   '_PAR_HABITANT', '_STRATE', 'PICTO_']:
            assert ch in ligne
        numLigne += 1

@pytest.mark.parametrize(\
    "isWikicode, strOK",
    [
        (True, "[[fichier:"),
        (True, "|10px|alt="),
        (False, "<tr><td"),
        (False, '<img alt="'),
        (False, '" src="'),
        (False, '</td></tr>'),
    ])
def test_genLegendePicto1(isWikicode, strOK):
    """
    V2.1.0 : test Fonction génération légende
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    legende = genCodeTableaux.genLegendePicto(config, isWikicode, True)
    assert strOK in legende

@pytest.mark.parametrize("isWikicode", [True, False])
def test_genLegendePicto2(isWikicode):
    """
    V2.1.0 : Test Fonction génération légende
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    if isWikicode:
        prefix = 'picto'
    else:
        prefix = 'pictoHtml'
    pictoFaible = config.get('Picto', prefix + '.ecartNul')
    pictoMoyen = config.get('Picto', prefix + '.ecartMoyen')
    pictoFort = config.get('Picto', prefix + '.ecartFort')
    ecartNulAlt = config.get('Picto', 'picto.ecartNulAlt')
    ecartMoyenAlt = config.get('Picto', 'picto.ecartMoyenAlt')
    ecartFortAlt = config.get('Picto', 'picto.ecartFortAlt')
    legende = genCodeTableaux.genLegendePicto(config, isWikicode, True)
    assert pictoFaible in legende
    assert pictoMoyen in legende
    assert pictoFort in legende
    assert ecartNulAlt in legende
    assert ecartMoyenAlt in legende
    assert ecartFortAlt in legende


