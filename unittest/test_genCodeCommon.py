#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name : test_genCodeCommon.py
Author : Thierry Maillard (TMD)
Date : 7/4/2020 - 11/5/2020
Role : Tests unitaires du projet FinancesLocales avec py.test
Utilisation :
    Pour jouer tous les test not global : élimine les tests globaux très long :
    python3 -m pytest -k "not global" .
    Pour jouer un test particulier de tous les fichiers de test
    python3 -m pytest -k "test_checkPathCSVDataGouvFrOk" test_genCode.py
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
import shutil

import pytest

import genCodeCommon
import utilitaires
import database
import updateDataMinFi
import genCodeTableaux

def test_createResultDir():
    """ Récupération position des mots clés de la table dans l'entête de test """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    resultatPath = config.get('Test', 'genCode.resultatsPath')
    if os.path.isdir(resultatPath):
        shutil.rmtree(resultatPath)
    assert not os.path.isdir(resultatPath)

    genCodeCommon.createResultDir(config, resultatPath)

    assert os.path.isdir(resultatPath)
    assert os.path.isdir(os.path.join(resultatPath,
                 config.get('EntreesSorties', 'io.RepSrcFicAux')))
    assert os.path.isfile(os.path.join(resultatPath,
                 config.get('EntreesSorties', 'io.nomNoticeTermes')))

@pytest.mark.parametrize("isWikicode", [True, False])
def test_calculeGrandeur(isWikicode):
    """
        teste le calcule de grandeurs agglomérées
    """

    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # récup données de test
    pathDatabaseMini = config.get('Test', 'genCode.pathDatabaseMini')
    pathCSVMini = config.get('Test', 'genCode.pathCSVMini')
    if os.path.isfile(pathDatabaseMini):
        print("destruction de la base :", pathDatabaseMini)
        os.remove(pathDatabaseMini)

    # Insertion dans la table ville des villes à traiter
    # Création base
    connDB = database.createDatabase(config, pathDatabaseMini, False)
    connDB.executemany("""
        INSERT INTO villes(codeCommune, nomMinFi, nom, nomWkpFr)
        VALUES (?, ?, ?, ?)
        """, (('068376', 'WITTENHEIM', 'Wittenheim', 'Wittenheim'),)
                       )
    connDB.commit()

    # Création de la création de la base de test
    param = ['updateDataMinFi.py', pathDatabaseMini, pathCSVMini]
    updateDataMinFi.main(param)
    assert os.path.isfile(pathDatabaseMini)

    # Lit dans la base les infos concernant la ville à traiter
    listeVilleWalheim = [ville
                         for ville in database.getListeVilles4Departement(connDB, '068', False)
                         if ville[0] == '068376']
    ville = listeVilleWalheim[0]

    # Recup des annees de données fiscales por WALHEIN
    dictAllGrandeur = database.getAllValeursDataMinFi4Entite(connDB, 'V',
                                                             ville[0], True)
    listAnnees = database.getListeAnneesDataMinFi4Entite(connDB, 'V', ville[0], True)
    assert len(listAnnees) == 3

    # Test calcul des valeurs
    genCodeCommon.calculeGrandeur(config, dictAllGrandeur, listAnnees, isWikicode, True)
    for grandeur in ["tendance ratio", "ratio dette / caf", "ratio n"]:
        assert grandeur in dictAllGrandeur

    # Fermeture base
    database.closeDatabase(connDB, True)

def test_calculeGrandeurCleBesoin():
    """
        teste le calcule de grandeurs agglomérées
    """
    isWikicode = True
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # récup données de test
    pathDatabaseMini = config.get('Test', 'genCode.pathDatabaseMini')
    pathCSVMini = config.get('Test', 'genCode.pathCSVMini')
    if os.path.isfile(pathDatabaseMini):
        print("destruction de la base :", pathDatabaseMini)
        os.remove(pathDatabaseMini)

    # Insertion dans la table ville des villes à traiter
    # Création base
    connDB = database.createDatabase(config, pathDatabaseMini, False)
    connDB.executemany("""
        INSERT INTO villes(codeCommune, nomMinFi, nom, nomWkpFr)
        VALUES (?, ?, ?, ?)
        """, (('068376', 'WITTENHEIM', 'Wittenheim', 'Wittenheim'),)
                       )
    connDB.commit()

    # Création de la création de la base de test
    param = ['updateDataMinFi.py', pathDatabaseMini, pathCSVMini]
    updateDataMinFi.main(param)
    assert os.path.isfile(pathDatabaseMini)

    # Lit dans la base les infos concernant la ville à traiter
    listeVilleWalheim = [ville
                         for ville in database.getListeVilles4Departement(connDB, '068', False)
                         if ville[0] == '068376']
    ville = listeVilleWalheim[0]

    # Recup des annees de données fiscales por WALHEIN
    dictAllGrandeur = database.getAllValeursDataMinFi4Entite(connDB, 'V',
                                                             ville[0], False)
    listAnnees = database.getListeAnneesDataMinFi4Entite(connDB, 'V', ville[0], False)
    assert len(listAnnees) == 3

    # Appel fonction à tester pour un ville
    genCodeCommon.calculeGrandeur(config, dictAllGrandeur, listAnnees, isWikicode, False)
    print("Avant Suppression")
    print("Valeur totale=", dictAllGrandeur['Valeur totale'].keys())
    print("Par habitant=", dictAllGrandeur['Par habitant'].keys())

    # Test valeur présente pour une ville et svg valeurs
    cleManquante = "besoin ou capacité de financement de la section investissement"
    cleManquanteHab = "besoin ou capacité de financement de la section investissement par habitant"
    assert cleManquante in dictAllGrandeur['Valeur totale']
    assert cleManquanteHab in dictAllGrandeur['Par habitant']
    ValeursTotale = dictAllGrandeur['Valeur totale'][cleManquante]
    ValeursHab = dictAllGrandeur['Par habitant'][cleManquanteHab]

    cleRessourceInv = "total des ressources d'investissement"
    assert cleRessourceInv in dictAllGrandeur['Valeur totale']

    # Suppresion de la clé pour se mettre dans la situation d'un groupement de commune
    del dictAllGrandeur['Valeur totale'][cleManquante]
    del dictAllGrandeur['Par habitant'][cleManquanteHab]
    assert cleManquante not in dictAllGrandeur['Valeur totale']
    assert cleManquanteHab not in dictAllGrandeur['Par habitant']

    # Appel fonction à tester pour un ville
    genCodeCommon.calculeGrandeur(config, dictAllGrandeur, listAnnees, isWikicode, False)

    # Test valeur présente à nouveau pour une ville et controle valeurs
    assert cleManquante in dictAllGrandeur['Valeur totale']
    assert cleManquanteHab in dictAllGrandeur['Par habitant']
    ValeursTotaleNew = dictAllGrandeur['Valeur totale'][cleManquante]
    ValeursHabNew = dictAllGrandeur['Par habitant'][cleManquanteHab]

    # Comparaison à un chouia près : 1e-3
    assert ValeursTotale == pytest.approx(ValeursTotaleNew, rel=1e-3)
    assert ValeursHab == pytest.approx(ValeursHabNew, rel=1e-3)
    
    # Fermeture base
    database.closeDatabase(connDB, True)

@pytest.mark.parametrize("defLien, isWikicode, lienOK, nomLienOK",
                         [
                             [("lien",), True, "lien", "lien"],
                             [("lien",), False, "lien", "lien"],
                             [("lien", "alias"), True, "lien", "alias"],
                             [("lien", "alias"), False, "lien", "alias"],
                         ])
def test_genLien(defLien, isWikicode, lienOK, nomLienOK):
    """
        teste la génération de liens Wikipedia ou HTML
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    
    lien = genCodeCommon.genLien(config, defLien, isWikicode, True)

    assert lienOK in lien
    assert nomLienOK in lien

    if isWikicode:
        assert '[[' in lien
        assert ']]' in lien
        if len(defLien) > 1 :
            assert '|' in lien
        else:
            assert '|' not in lien
    else:
        assert '<a href=' in lien
        assert '</a>' in lien
        assert 'target="_blank">' in lien
        assert config.get('Extraction', 'wikipediaFr.baseUrl') in lien
        
@pytest.mark.parametrize(\
    "dictValeurs",
    [
        ({"gros" : {"Valeur totale" : 1000,
                    "Par habitant" : 0},
          "petit" : {"Valeur totale" : 2,
                     "Par habitant" : 0}
         }),
        ({"petit" : {"Valeur totale" : 2,
                     "Par habitant" : 0},
          "gros" : {"Valeur totale" : 1000,
                    "Par habitant" : 0}
         }),
        ({"petit" : {"Valeur totale" : 2,
                     "Par habitant" : 0},
          "moyen" : {"Valeur totale" : 500,
                     "Par habitant" : 0},
          "gros" : {"Valeur totale" : 1000,
                    "Par habitant" : 0}
         }),
    ])
def test_triPourCent_Tri_Groupement(dictValeurs):
    """
    Test Fonction du tri des valeurs en fonction de leur contribution à
    la somme totale (ordre des valeurs résultat)
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    cletrie = genCodeCommon.triPourCent(config, 500, dictValeurs,
                                                    False, True, False,
                                                    True)
    assert len(cletrie) == len(dictValeurs)
    assert cletrie[0] == "gros"
    assert cletrie[-1] == "petit"

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
def test_triPourCent_Tri_Ville(dictValeurs):
    """
    Test Fonction du tri des valeurs en fonction de leur contribution à
    la somme totale (ordre des valeurs résultat)
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    cletrie = genCodeCommon.triPourCent(config, 500, dictValeurs,
                                        False, True, True,
                                        True)
    assert len(cletrie) == len(dictValeurs)
    assert cletrie[0] == "gros"
    assert cletrie[-1] == "petit"

    for defValeur in dictValeurs:
        assert 'ratioStrate' in dictValeurs[defValeur]
        assert 'ratioStratePicto' in dictValeurs[defValeur]
        assert 'ratioStratePictoAlt' in dictValeurs[defValeur]

@pytest.mark.parametrize(\
    "dictValeurs",
    [
        ({"gros" : {"Valeur totale" : 1000,
                    "Par habitant" : 0},
          "petit" : {"Valeur totale" : 100,
                     "Par habitant" : 0}
         }),
        ({"petit" : {"Valeur totale" : 100,
                     "Par habitant" : 0},
          "gros" : {"Valeur totale" : 1000,
                    "Par habitant" : 0}
         }),
        ({"petit" : {"Valeur totale" : 100,
                     "Par habitant" : 0},
          "moyen" : {"Valeur totale" : 500,
                     "Par habitant" : 0},
          "gros" : {"Valeur totale" : 1000,
                    "Par habitant" : 0}
         }),
    ])
def test_triPourCent_ratioValeur_Groupement(dictValeurs):
    """
    Test Fonction du tri des valeurs en fonction de leur contribution à
    la somme totale (% calculés)
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    sommeValeurTotal = 500*1e3
    genCodeCommon.triPourCent(config, sommeValeurTotal, dictValeurs,
                              False, True, False,
                              True)
    for defValeur in list(dictValeurs.keys()):
        assert abs(dictValeurs[defValeur]['ratioValeur'] -
                   ((float(dictValeurs[defValeur]["Valeur totale"]*1e3) * 100.0) /
                    float(sommeValeurTotal))) < 1
        assert "%1.f"%dictValeurs[defValeur]['ratioValeur'] in \
               dictValeurs[defValeur]['ratioValeurStr']

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
def test_triPourCent_ratioValeur_Ville(dictValeurs):
    """
    Test Fonction du tri des valeurs en fonction de leur contribution à
    la somme totale (% calculés)
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    sommeValeurTotal = 500*1e3
    genCodeCommon.triPourCent(config, sommeValeurTotal, dictValeurs,
                              False, True, True,
                              True)
    for defValeur in list(dictValeurs.keys()):
        assert abs(dictValeurs[defValeur]['ratioValeur'] -
                   ((float(dictValeurs[defValeur]["Valeur totale"]*1e3) * 100.0) /
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
    cletrie = genCodeCommon.triPourCent(config, sommeValeurTotal, dictValeurs,
                                        False, True, True,
                                        True)
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
    cletrie = genCodeCommon.triPourCent(config, sommeValeurTotal, dictValeurs,
                                        False, True, True,
                                        True)
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
    genCodeCommon.triPourCent(config, sommeValeurTotal, dictValeurs,
                              False, True, True,
                              True)
    defValeur = list(dictValeurs.keys())[0]
    assert abs(dictValeurs[defValeur]['ratioStrate'] - ecart) < 1.0
    assert ecartStr in dictValeurs[defValeur]['ratioStrateStr']
    assert dictValeurs[defValeur]['ratioStratePicto'] == config.get('Picto', picto)

@pytest.mark.parametrize("avecStrate", [False, True])
def test_getValeursDict(avecStrate):
    """ Teste la fonction getValeursDict """

    isWikicode = False
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # récup données de test
    pathDatabaseMini = config.get('Test', 'genCode.pathDatabaseMini')
    pathCSVMini = config.get('Test', 'genCode.pathCSVMini')
    if os.path.isfile(pathDatabaseMini):
        print("destruction de la base :", pathDatabaseMini)
        os.remove(pathDatabaseMini)

    # Insertion dans la table ville des villes à traiter
    # Création base
    connDB = database.createDatabase(config, pathDatabaseMini, False)
    connDB.executemany("""
        INSERT INTO villes(codeCommune, nomMinFi, nom, nomWkpFr)
        VALUES (?, ?, ?, ?)
        """, (('068376', 'WITTENHEIM', 'Wittenheim', 'Wittenheim'),)
                       )
    connDB.commit()

    # Création de la création de la base de test
    param = ['updateDataMinFi.py', pathDatabaseMini, pathCSVMini]
    updateDataMinFi.main(param)
    assert os.path.isfile(pathDatabaseMini)

    listeVilleWalheim = [ville
                         for ville in database.getListeVilles4Departement(connDB, '068', False)
                         if ville[0] == '068376']
    ville = listeVilleWalheim[0]

    # Recup des annees de données fiscales por WALHEIN
    listAnnees = database.getListeAnneesDataMinFi4Entite(connDB, 'V',
                                                         ville[0], False)
    assert len(listAnnees) == 3

    verbose = True
    grandeursAnalyse = []
    couleurDettesCAF = config.get('Tableaux', 'tableaux.couleurDettesCAF')
    dictEncoursDette = \
    {
        "l'encours de la dette" :
        {
            'libellePicto' : 'Encours de la dette',
            'cle' : 'encours de la dette au 31 12 n',
            'note' : "",
            'noteHtml' : '',
            'nul' : "pas d'encours pour la dette"
        }
    }
    grandeursAnalyse.append([dictEncoursDette, 0, "ENCOURS_DETTE", couleurDettesCAF])

    dictAnnuiteDette = \
    {
        "l'annuité de la dette" :
        {
            'libellePicto' : 'annuité de la dette',
            'cle' : "annuité de la dette",
            'note' : "",
            'noteHtml' : '',
            'nul' : 'aucune annuité pour la dette'
        }
    }
    grandeursAnalyse.append([dictAnnuiteDette, 0, "ANNUITE_DETTE", couleurDettesCAF])

    dictAllGrandeur = database.getAllValeursDataMinFi4Entite(connDB, 'V', ville[0], verbose)
    
    nbAnneesTendance = int(config.get('GenWIkiCode', 'gen.nbAnneesTendance'))
    listeAnneesTendance = sorted(listAnnees[:nbAnneesTendance])


    for grandeurs in grandeursAnalyse:
        genCodeCommon.getValeursDict(dictAllGrandeur,
                   listeAnneesTendance, listAnnees[0],
                   grandeurs[0], avecStrate,
                   verbose)
        print(grandeurs[0], "=", grandeurs[0])
        assert grandeurs[0]["l'encours de la dette"]['Valeur totale'] == 10817
        assert grandeurs[0]["l'encours de la dette"]['Par habitant'] == 734
        if avecStrate:
            assert grandeurs[0]["l'encours de la dette"]['En moyenne pour la strate'] == 944
        else:
            assert not 'En moyenne pour la strate' in grandeurs[0]["l'encours de la dette"]
        assert grandeurs[0]["l'encours de la dette"]['dictAnneesValeur'][2013] == pytest.approx(479.18)
        assert grandeurs[0]["l'encours de la dette"]['dictAnneesValeur'][2014] == pytest.approx(671.41)
        assert grandeurs[0]["l'encours de la dette"]['dictAnneesValeur'][2015] == pytest.approx(733.67)
        break

@pytest.mark.parametrize("unite, avecStrate",
                         [
                             ("euro", False),
                             ("%", False),
                             ("euro", True),
                             ("%", True)
                         ])
def test_genlignesTableauPicto(unite, avecStrate):
    """
    Test Fonction de génération des lignes d'un tableau de pictogramme
    qui qualifie une commune par rapport à sa strate
    """
    motCle = 'CHARGE'
    couleur = "#ffd9ff"
    nbLignes = 3
    isGroupement = False
    lignes = genCodeCommon.genlignesTableauPicto(motCle, nbLignes,
                                                 couleur, unite,
                                                 True, avecStrate,
                                                 isGroupement,
                                                 True)
    assert len(lignes) == nbLignes
    for numLigne, ligne in enumerate(lignes, start=1):
        listChOk = [motCle, couleur, str(numLigne),
                   '<LIBELLE_PICTO_', 'row', 'VALEUR', '_PAR_HABITANT']
        if avecStrate:
            listChOk.append('_STRATE')
            listChOk.append('PICTO_')
        for ch in listChOk:
            assert ch in ligne

@pytest.mark.parametrize( "isComplet, isWikicode",
                          [
                              (False, True),
                              (True, True),
                              (False, False),
                              (True, False)
                          ])
def test_genCodeTableauxPicto(isComplet, isWikicode):
    """
        teste la génération de tous les tableau pour 1 ville : Wittenheim 68)
        Wittenheim et les années 2013 à 2015 pour comparaison avec
        http://marielaure.monde.free.fr/Finances_Locales_Web/Departement_68/Wittenheim/Wittenheim.html
    """

    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # récup données de test
    pathDatabaseMini = config.get('Test', 'genCode.pathDatabaseMini')
    pathCSVMini = config.get('Test', 'genCode.pathCSVMini')
    if os.path.isfile(pathDatabaseMini):
        print("destruction de la base :", pathDatabaseMini)
        os.remove(pathDatabaseMini)

    # Insertion dans la table ville des villes à traiter
    # Création base
    connDB = database.createDatabase(config, pathDatabaseMini, False)
    connDB.executemany("""
        INSERT INTO villes(codeCommune, nomMinFi, nom, nomWkpFr)
        VALUES (?, ?, ?, ?)
        """, (('068376', 'WITTENHEIM', 'Wittenheim', 'Wittenheim'),)
                       )
    connDB.commit()

    # Création de la création de la base de test
    param = ['updateDataMinFi.py', pathDatabaseMini, pathCSVMini]
    updateDataMinFi.main(param)
    assert os.path.isfile(pathDatabaseMini)

    listeVilleWalheim = [ville
                         for ville in database.getListeVilles4Departement(connDB, '068', False)
                         if ville[0] == '068376']
    ville = listeVilleWalheim[0]

    # Recup des données fiscales por WALHEIN
    dictAllGrandeur = database.getAllValeursDataMinFi4Entite(connDB, 'V',
                                                             ville[0], False)
    listAnnees = database.getListeAnneesDataMinFi4Entite(connDB, 'V',
                                                         ville[0], False)
    assert len(listAnnees) == 3
    # Agglomère certaines grandeurs et complète dictAllGrandeur
    genCodeCommon.calculeGrandeur(config, dictAllGrandeur,
                            listAnnees, isWikicode, False)

    # Lecture du modèle de test reduit au tableau picto
    nomBaseModele = config.get('Test', 'genCodeTableauxPicto.ficModele')
    typeSortie = ""
    if isWikicode:
        typeSortie = "wikicode"
    else:
        typeSortie = "HTML"
    modele = nomBaseModele + '_' + typeSortie + '.txt'
    textSection = utilitaires.lectureFiltreModele(modele, isComplet, False)
    isGroupement = False

    print("textSection AVANT genCodeTableauxPicto=", textSection)
    
    # Définit le contenu des tableaux picto
    grandeursAnalyse = genCodeTableaux.defTableauxPicto(config,
                                        dictAllGrandeur, listAnnees,
                                        isWikicode, False)   
    textSection = genCodeCommon.genCodeTableauxPicto(config,
                                                       dictAllGrandeur,
                                                       grandeursAnalyse,
                                                       textSection,
                                                       listAnnees, isComplet,
                                                       isWikicode,
                                                     True,
                                                     isGroupement,
                                                     False)

    # Test Résultat comptable en 2015
    # (cle fres1) : 12.94
    print("textSection APRES genCodeTableauxPicto=", textSection)
    assert "13" in textSection

    # Test valeur des Charges de personnels par habitant en 2015
    # (cle fperso) : 470.19
    assert "470" in textSection

    if isComplet:
        # Test valeur des charges de la strate en 2015
        # (cle mres1) : 131.95
        assert "132" in textSection

    # Test valeur taux taxe d'habitation en 2015
    # (cle tth) : 10.11
    assert "10" in textSection

    if isComplet:
        # Test valeur taux taxe d'habitation pour la strate en 2015
        # (cle tmth) : 15.98
        assert "16" in textSection
    
    database.closeDatabase(connDB, True)
