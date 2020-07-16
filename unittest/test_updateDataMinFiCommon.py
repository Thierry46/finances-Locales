#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name : test_updateDataMinFiCommon.py
Author : Thierry Maillard (TMD)
Date : 7/4/2020
Role : Tests unitaires du projet FinancesLocales avec py.test
Utilisation :
    Pour jouer tous les test not global : élimine les tests globaux très long :
    python3 -m pytest -k "not global" .
    Pour jouer un test particulier de tous les fichiers de test
    python3 -m pytest -k "test_checkPathCSVDataGouvFrOk" test_updateDataMinFi.py
 options :
    -s : pour voir les sorties sur stdout
Ref : python3 -m pytest -h
Ref : http://sametmax.com/un-gros-guide-bien-gras-sur-les-tests-unitaires-en-python-partie-3
Ref : http://pytest.org/latest
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
import os
import os.path
import configparser

import pytest

import updateDataMinFiCommon
import database

@pytest.mark.parametrize("headerTest, dictKeyOk, missingKey",
                         [
                          ('prod;fprod;mprod;tmth' , {"prod":0, "tmth":3}, "res1"),
                          ('an;dep;icom;inom;reg;pop1;nomsst2;prod;fprod;mprod;impo1;fimpo1;mimpo1;rimpo1;rmimpo1;impo2;fimpo2;mimpo2;rmimpo2;dgf;fdgf;mdgf;rdgf;rmdgf;charge;fcharge;mcharge;perso;fperso;mperso;rperso;rmperso;achat;fachat;machat;rachat;rmachat;fin;ffin;mfin;rfin;rmfin;cont;fcont;mcont;rcont;rmcont;subv;fsubv;msubv;rsubv;rmsubv;res1;fres1;mres1;pth;fpth;mpth;tth;tmth;pfb;fpfb;mpfb;tfb;tmfb;pfnb;fpfnb;mpfnb;tfnb;tmfnb;ttp;tmtp;recinv;frecinv;mrecinv;emp;femp;memp;remp;rmemp;subr;fsubr;msubr;rsubr;rmsubr;fctva;ffctva;mfctva;rfctva;rmfctva;raff;fraff;mraff;rraff;rmraff;depinv;fdepinv;mdepinv;equip;fequip;mequip;requip;rmequip;remb;fremb;mremb;rremb;rmremb;repart;frepart;mrepart;rrepart;rmrepart;daff;fdaff;mdaff;rdaff;rmdaff;bf1;fbf1;mbf1;solde;fsolde;msolde;bf2;fbf2;mbf2;res2;fres2;mres2;ebf;febf;mebf;rebf;rmebf;caf;fcaf;mcaf;rcaf;rmcaf;cafn;fcafn;mcafn;rcafn;rmcafn;dette;fdette;mdette;rdette;rmdette;annu;fannu;mannu;rannu;rmannu;fdr;ffdr;mfdr;bth;fbth;mbth;bthexod;fbthexod;mbthexod;bfb;fbfb;mbfb;bfbexod;fbfbexod;mbfbexod;bfnb;fbfnb;mbfnb;bfnbexod;fbfnbexod;mbfnbexod;btafnb;fbtafnb;mbtafnb;btp;fbtp;mbtp;btpexod;fbtpexod;mbtpexod;ptafnb;fptafnb;mptafnb;tafnb;mtmtafnb;pcfe;fpcfe;mpcfe;cvaec;fcvaec;mcvaec;iferc;fiferc;miferc;tascomc;ftascomc;mtascomc;nomsst1;encdbr;fencdbr;rencdbr;mencdbr;rmencdbr;pfcaf;fpfcaf;mpfcaf;cfcaf;fcfcaf;mcfcaf;det2cal;fdet2cal;rdet2cal;mdet2cal;rmdet2cal',
                           {"prod":7, "tmth":59}, ""),
                          ('an;dep;icom;inom;reg;pop1;nomsst2;prod;fprod;mprod;impo1;fimpo1;mimpo1;rimpo1;rmimpo1;impo2;fimpo2;mimpo2;rmimpo2;dgf;fdgf;mdgf;rdgf;rmdgf;charge;fcharge;mcharge;perso;fperso;mperso;rperso;rmperso;achat;fachat;machat;rachat;rmachat;fin;ffin;mfin;rfin;rmfin;cont;fcont;mcont;rcont;rmcont;subv;fsubv;msubv;rsubv;rmsubv;res1;fres1;mres1;pth;fpth;mpth;tth;tmth;pfb;fpfb;mpfb;tfb;tmfb;pfnb;fpfnb;mpfnb;tfnb;tmfnb;ttp;tmtp;recinv;frecinv;mrecinv;emp;femp;memp;remp;rmemp;subr;fsubr;msubr;rsubr;rmsubr;fctva;ffctva;mfctva;rfctva;rmfctva;raff;fraff;mraff;rraff;rmraff;depinv;fdepinv;mdepinv;equip;fequip;mequip;requip;rmequip;remb;fremb;mremb;rremb;rmremb;repart;frepart;mrepart;rrepart;rmrepart;daff;fdaff;mdaff;rdaff;rmdaff;bf1;fbf1;mbf1;solde;fsolde;msolde;bf2;fbf2;mbf2;res2;fres2;mres2;ebf;febf;mebf;rebf;rmebf;caf;fcaf;mcaf;rcaf;rmcaf;cafn;fcafn;mcafn;rcafn;rmcafn;dette;fdette;mdette;rdette;rmdette;annu;fannu;mannu;rannu;rmannu;fdr;ffdr;mfdr;bth;fbth;mbth;bthexod;fbthexod;mbthexod;bfb;fbfb;mbfb;bfbexod;fbfbexod;mbfbexod;bfnb;fbfnb;mbfnb;bfnbexod;fbfnbexod;mbfnbexod;btafnb;fbtafnb;mbtafnb;btp;fbtp;mbtp;btpexod;fbtpexod;mbtpexod;ptafnb;fptafnb;mptafnb;tafnb;mtmtafnb;pcfe;fpcfe;mpcfe;cvaec;fcvaec;mcvaec;iferc;fiferc;miferc;tascomc;ftascomc;mtascomc;nomsst1;encdbr;fencdbr;rencdbr;mencdbr;rmencdbr;pfcaf;fpfcaf;mpfcaf;cfcaf;fcfcaf;mcfcaf;det2cal;fdet2cal;rdet2cal;mdet2cal;rmdet2cal;dfctva;fdfctva;rdfctva;mdfctva;rmdfctva;dpserdom;fpserdom;rpserdom;mpserdom;rmpserdom',
                           {"prod":7, "tmth":59}, "")
                          ])
def test_getColumnPosition(headerTest, dictKeyOk, missingKey):
    """ Récupération position des mots clés de la table dans l'entête de test """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Recup chemin base de test
    databasePathDir = config.get('Test', 'database.testDir')
    databasePath = os.path.join(databasePathDir, config.get('Test', 'database.testName'))
    # Création base
    connDB = database.createDatabase(config, databasePath, True)

    dictPositionColumns, listMissingKeys = \
        updateDataMinFiCommon.getColumnPosition(headerTest, "V", connDB, True)

    # Controle des clés présentes et de leur position dans headerTest
    for keyOk in dictKeyOk:
        assert dictPositionColumns[keyOk] == dictKeyOk[keyOk]

    if listMissingKeys:
        assert missingKey in listMissingKeys
    else:
        assert not missingKey

    database.closeDatabase(connDB, True)

def test_getColumnPosition_Pb():
    """ Test cas d'erreur fonction de validation d'un répertoire contenant les données
        issues du site gouvernemental
        """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Recup chemin base de test
    databasePathDir = config.get('Test', 'database.testDir')
    databasePath = os.path.join(databasePathDir, config.get('Test', 'database.testName'))
    # Création base
    connDB = database.createDatabase(config, databasePath, True)

    with pytest.raises(ValueError,
                       match=r".*Entete CSV non valide.*"):
        dictPositionColumns, listMissingKeys = \
            updateDataMinFiCommon.getColumnPosition("Entete tout moisi",
                                                    "V", connDB, True)

    database.closeDatabase(connDB, True)
