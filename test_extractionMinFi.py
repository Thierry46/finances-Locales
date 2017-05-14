#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name : test_extractionMinFi.py
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
import urllib.request, urllib.error, urllib.parse
import pytest
import extractionMinFi

@pytest.mark.parametrize("cle", [
    "TOTAL DES PRODUITS DE FONCTIONNEMENT = A",
    "TOTAL DES PRODUITS",
    ])
def test_extractDonneesLigneTableau_OK(cle):
    """ Test extraction de 2 valeurs d'une page de synthèse MinFi """
    # Ouverture de la page
    print("Ouverture de la page")
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    url = "http://alize2.finances.gouv.fr/communes/eneuro/tableau.php" + \
          "?dep=046&type=BPS&icom=042&param=0&exercice=2013"
    infile = opener.open(url)
    page = infile.read()
    assert len(page) > 0

    # extraction de la cle
    dictValue = extractionMinFi.extractDonneesLigneTableau(page, cle, True)
    assert dictValue is not None
    assert dictValue["Valeur totale"] == 27271000
    assert dictValue["Par habitant"] == 1278
    assert dictValue["En moyenne pour la strate"] == 1471

@pytest.mark.parametrize("annee, url, values", [
    (
        "2013",
        "http://alize2.finances.gouv.fr/communes/eneuro/detail.php?" + \
        "dep=046&type=BPS&icom=042&param=0&exercice=2013",
        [16.55, 18.00]),
    (
        "2000",
        "http://alize2.finances.gouv.fr/communes/eneuro/detail.php" + \
        "?dep=046&type=BPS&icom=042&param=0&exercice=2000",
        [11.27, 15.41])
    ])
def test_extractDonneesLigneTableauDetail_OK(annee, url, values):
    """ Test extraction de 2 taux de 2 pages de détail MinFi """
    # Ouverture de la page
    print("Ouverture de la page")
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    infile = opener.open(url)
    page = infile.read()
    assert len(page) > 0

    # extraction de la cle
    titre = ["Les taux et les produits de la fiscalité directe locale",
             "Potentiel fiscal"]
    libelle = ["Taxe d'habitation (y compris THLV)",
               "Produits taxe d'habitation"]
    dictValue = extractionMinFi.extractDonneesLigneTableauDetail(page, titre, libelle, True)
    print(annee, "Recu", dictValue, "Attendu", values)
    assert dictValue is not None
    assert abs(dictValue["Taux"] - values[0]) < 1e-2
    assert abs(dictValue["Taux moyen pour la strate"] - values[1]) < 1e-2
