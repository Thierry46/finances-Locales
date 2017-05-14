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
import os.path
import shutil
import pytest
import extractionWeb
import genListeDep

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

@pytest.mark.parametrize(\
   "numDep, isOk",
   [\
        ('001', True),
        ('009', True),
        ('011', True),
        ('019', True),
        ('097', True),
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
    """ Test fonction de test n°département """
    assert extractionWeb.isnumDep(numDep) == isOk

def test_recupVillesListe_global():
    """
    V2.2.0 : Test génération liste ville, relecture
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Extration d'un département si nécessaire
    numDep = config.get('Test', 'test.numDepDepartementExtraction')
    repertoireBase = config.get('EntreesSorties', 'io.repertoireExtractions')
    repertoireExtractions = os.path.normcase(repertoireBase + '_' + numDep)
    if not os.path.isdir(repertoireExtractions):
        depExtraction = config.get('Test', 'test.departementExtraction')
        param = ['extractionWeb.py', depExtraction]
        extractionWeb.main(param)
    assert os.path.isdir(repertoireExtractions)
    indicateurNomFicBd = config.get('EntreesSorties', 'io.indicateurNomFicBd')
    listFicrepertoireExtractions = [fic for fic in os.listdir(repertoireExtractions)
                                    if fic.endswith(indicateurNomFicBd + '.txt')]
    nbFicDepartementExtractionOk = int(config.get('Test', 'test.nbFicDepartementExtraction'))
    assert len(listFicrepertoireExtractions) == nbFicDepartementExtractionOk

    # Génération listes pour les départements extraits
    repertoireListeDep = config.get('EntreesSorties', 'io.repertoireListeDep')
    shutil.rmtree(repertoireListeDep, ignore_errors=True)
    param = ['genListeDep.py']
    genListeDep.main(param)

    # Test si liste pour le département de test présente
    nomFicListeVille = config.get('EntreesSorties', 'io.nomFicListeVille')
    nomFicListeVilleDep = nomFicListeVille + '_' + numDep + '.txt'
    pathFicListeVilleDep = os.path.join(repertoireListeDep, nomFicListeVilleDep)
    assert os.path.isfile(pathFicListeVilleDep)
    shutil.rmtree(repertoireExtractions, ignore_errors=True)

    # Lecture liste des villes produite et reextraction par extractionWeb
    param = ['extractionWeb.py', '-v', numDep]
    extractionWeb.main(param)
    assert os.path.isdir(repertoireExtractions)
    listFicrepertoireExtractions2 = [fic for fic in os.listdir(repertoireExtractions)
                                     if fic.endswith(indicateurNomFicBd + '.txt')]
    assert len(listFicrepertoireExtractions2) == nbFicDepartementExtractionOk

