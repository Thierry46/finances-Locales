#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name : test_genCodeTexte.py
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

import pytest
import genCodeTexte

# Atention les seuils définis dans les properties ne sont pas pris en compte
# Mais codage direct comme constant litteral ci-dessous.
# Pb si modif seuils dans .properties.
@pytest.mark.parametrize(\
    "defStrate,strateWikifOK",
    [
        ("bla bla de plus de 100 000 habitants appartenant ",
         "{{unité|100000|habitants}}"),
        ("bla bla communes de moins de 250 habitants appartenant ",
         "{{unité|250|habitants}}"),
        ("bla bla des communes de 500 à 2 000 habitants appartenant " + \
         "à un groupement fiscalisé (4 taxes)",
         "{{unité/2|500|à=2000|habitants}}"),
        ("bla bla des communes de 20 000 à 50 000 habitants appartenant",
         "{{unité/2|20000|à=50000|habitants}}"),
        ("bla bla des communes de 500 à 2 000 habitants appartenant " +
         "à un groupement fiscalisé (4 taxes)",
         "({{nobr|4 taxes}})"),
    ])
def test_wikifieStrate(defStrate, strateWikifOK):
    """
    Test fonction de wikification de la phrase de définition
    de la strate issue du site MinFi
    """
    strateWikif = genCodeTexte.wikifieStrate(defStrate, True)
    assert strateWikifOK in strateWikif
