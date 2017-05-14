#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name : test_extractionWeb.py
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
import pytest
import extractionWeb

@pytest.mark.parametrize(\
    "listeVilleDict, nbVillesOk, toutesLesVilles",
    [
        ([{'nom':'grosseVille', 'Score':25}, {'nom':'petiteVille', 'Score':1}],
         2, True),
        ([{'nom':'grosseVille', 'Score':25}, {'nom':'petiteVille', 'Score':1}],
         1, False),
        ([{'nom':'petiteVille', 'Score':1}, {'nom':'grosseVille', 'Score':25}],
         2, True),
        ([{'nom':'petiteVille', 'Score':1}, {'nom':'grosseVille', 'Score':25}],
         1, False),
    ])
def test_triSelectVilles(listeVilleDict, nbVillesOk, toutesLesVilles):
    """ Test tri des villes par score """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    listeVilleDict = extractionWeb.triSelectVilles(config, listeVilleDict, toutesLesVilles, True)
    assert len(listeVilleDict) == nbVillesOk
    assert listeVilleDict[0]['nom'] == 'grosseVille'

@pytest.mark.parametrize(\
    "listeVilleDict, toutesLesVilles, msgOk",
    [
        ([], True, "Aucune ville à traiter"),
        ([], False, "Aucune ville à traiter"),
        ([{'nom':'petiteVille', 'Score':1}], False, "prioritaire"),
    ])
def test_triSelectVilles_Pb(listeVilleDict, toutesLesVilles, msgOk):
    """ Test cas d'erreur pour le tri des villes par score """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    with pytest.raises(AssertionError) as e:
        extractionWeb.triSelectVilles(config, listeVilleDict, toutesLesVilles, True)
    print(e)
    assert msgOk in str(e)

@pytest.mark.parametrize(\
    "listeVilleDict, deptOk",
    [
        ([{'dep':'025', 'nomDepStr':'du Doubs'},
          {'dep':'025', 'nomDepStr':'du Doubs'}], "025"),
        ([{'dep':'097', 'nomDepStr':'de la Guadeloupe'},
          {'dep':'097', 'nomDepStr':'de la Guadeloupe'}], "101"),
        ([{'dep':'097', 'nomDepStr':'de la Guyane'}], "102"),
        ([{'dep':'097', 'nomDepStr':'de la Martinique'}], "103"),
        ([{'dep':'097', 'nomDepStr':'de la Réunion'}], "104"),
    ])
def test_corrigeDepartement97(listeVilleDict, deptOk):
    """ Test fonction de correction du département 97 """
    extractionWeb.corrigeDepartement97(listeVilleDict, True)
    for ville in listeVilleDict:
        assert ville['dep'] == deptOk
