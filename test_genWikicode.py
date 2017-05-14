#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name : test_genWikiCode.py
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
import genWikiCode

# Atention les seuils définis dans les properties ne sont pas pris en compte
# Mais codage direct comme constant litteral ci-dessous.
# Pb si modif seuils dans .properties.
@pytest.mark.parametrize(\
    "dictDette,dictCAF,ch",
    [
        ({"2013" : 25, "2012" : 23, "2011" : 24}, {"2013" : 1, "2012" : 1, "2011" : 1},
         "est constant et élevé (supérieur à"),
        ({"2013" : 25, "2012" : 23, "2011" : 24}, {"2013" : 1, "2012" : 1, "2011" : 1},
         "15"),
        ({"2013" : 25, "2012" : 23, "2011" : 24}, {"2013" : 20, "2012" : 21, "2011" : 18},
         "est constant et faible (inférieur à"),
        ({"2013" : 25, "2012" : 23, "2011" : 24}, {"2013" : 20, "2012" : 21, "2011" : 18},
         "est constant et faible (inférieur à"),
        ({"2013" : 10, "2012" : 7, "2011" : 12}, {"2013" : 1, "2012" : 1, "2011" : 1},
         "minimum"),
        ({"2013" : 10, "2012" : 7, "2011" : 12}, {"2013" : 1, "2012" : 1, "2011" : 1},
         "7"),
        ({"2013" : 7, "2012" : 6, "2011" : 12}, {"2013" : 1, "2012" : 1, "2011" : 1},
         "maximum"),
        ({"2013" : 7, "2012" : 6, "2011" : 12}, {"2013" : 1, "2012" : 1, "2011" : 1},
         "6"),
        ({"2013" : 10, "2012" : 7, "2011" : 12}, {"2013" : 1, "2012" : 1, "2011" : 1},
         "minimum d'environ"),
        ({"2013" : 10, "2012" : 7, "2011" : 12}, {"2013" : 1, "2012" : 1, "2011" : 1},
         "maximum d'environ"),
        ({"2013" : 10, "2012" : 7, "2011" : 75}, {"2013" : 1, "2012" : 1, "2011" : 1},
         "50"),
    ])
def test_tendanceRatioDetteCAF(dictDette, dictCAF, ch):
    """ Test fonction évaluation du ratio dette/caf """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    seuilEcreteRatio = int(config.get('GenWIkiCode', 'gen.seuilEcreteRatio'))
    dictRatio, strTendance = genWikiCode.tendanceRatioDetteCAF(config, dictCAF, dictDette, True)
    assert len(dictRatio) == len(dictDette)
    for annee in list(dictDette.keys()):
        ratioBrut = (int)(float(dictDette[annee])/float(dictCAF[annee]))
        print(("ratioBrut=", ratioBrut, "seuilEcreteRatio=", seuilEcreteRatio))
        if ratioBrut >= seuilEcreteRatio:
            assert dictRatio[annee] == seuilEcreteRatio
        else:
            assert dictRatio[annee] == ratioBrut
        assert ch in strTendance

def test_tendanceRatioDetteCAF_pb1515():
    """ Test cas erreur fonction évaluation du ratio dette/caf """
    dictCAF = {'2002':872000, '2003':1128000, '2000':780000, '2001':741000,
               '2006':1016000, '2007':684000, '2004':897000, '2005':1100000,
               '2008':645000, '2009':1088000, '2011':1065000, '2010':945000,
               '2013':834000, '2012':656000}
    dictDette = {'2002':10740000, '2003':11237000, '2000':8608000,
                 '2001':9461000, '2006':10489000, '2007':12347000,
                 '2004':9947000, '2005':9883000, '2008':14525000,
                 '2009':13603000, '2011':12647000, '2010':13731000,
                 '2013':12284000, '2012':11696000}
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    dictRatio, strTendance = genWikiCode.tendanceRatioDetteCAF(config, dictCAF, dictDette, True)
    assert dictRatio['2008'] == 22
    assert '1515' not in strTendance
    assert '22 an' in strTendance

