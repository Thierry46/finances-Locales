#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name : test_genCodeTableaux.py
Author : Thierry Maillard (TMD)
Date : 1/6/2015 - 22/9/2019
Role : Tests unitaires du projet FinancesLocales avec py.test
Utilisation : python3 -m pytest [-k "nomTest"] .
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

import pytest

import updateDataMinFi
import genCodeTableaux
import database
import utilitaires
import genCode

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
    sommeValeurTotal = 500*1e3
    genCodeTableaux.triPourCent(config, sommeValeurTotal,
                                dictValeurs, False, True, True)
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

@pytest.mark.parametrize( "isComplet", [False, True])
def test_genCodeTableauxWikicode(isComplet):
    """
        teste la génération de tous les tableaux pour 1 ville : Wittenheim 68)
        Wittenheim et les années 2013 à 2015 pour comparaison avec
        http://marielaure.monde.free.fr/Finances_Locales_Web/Departement_68/Wittenheim/Wittenheim.html
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

    listeVilleWalheim = [ville
                         for ville in database.getListeVilles4Departement(connDB, '068', False)
                         if ville[0] == '068376']
    ville = listeVilleWalheim[0]

    # Recup des données fiscales por WALHEIN
    dictAllGrandeur = database.getAllValeurs4Ville(connDB, ville[0], False)
    listAnnees = database.getListeAnnees4Ville(connDB, ville[0], False)
    assert len(listAnnees) == 3
    # Agglomère certaines grandeurs et complète dictAllGrandeur
    genCode.calculeGrandeur(config, dictAllGrandeur,
                            listAnnees, isWikicode, False)

    verbose = True

    # Lecture du modèle
    nomBaseModele = config.get('Modele', 'modele.nomBaseModele')
    numVersion = config.get('Version', 'version.number')
    typeSortie = config.get('GenCode', 'gen.idFicDetail')
    modele = nomBaseModele + '_' + numVersion + '_' + typeSortie + '.txt'
    textSection = utilitaires.lectureFiltreModele(modele, isComplet, verbose)

    textSection = genCodeTableaux.genCodeTableaux(config, dictAllGrandeur,
                                                  textSection, ville,
                                                  listAnnees, isComplet,
                                                  isWikicode, verbose)
    # Test valeur des charges en 2015
    # (cle charge) : 12659.65
    assert "12660" in textSection

    # Test valeur des charges par habitant en 2015
    # (cle fcharge) : 858.63
    assert "859" in textSection

    if isComplet:
        # Test valeur des charges de la strate en 2015
        # (cle mcharge) : 1223.21
        assert "1223" in textSection
   
    # Test valeur taux taxe d'habitation en 2015
    # (cle tth) : 10.11
    assert "10" in textSection

    if isComplet:
        # Test valeur taux taxe d'habitation pour la strate en 2015
        # (cle tmth) : 15.98
        assert "16" in textSection
    
    database.closeDatabase(connDB, True)

@pytest.mark.parametrize( "isComplet", [False, True])
def test_genCodeTableauxHtml(isComplet):
    """
        teste la génération de tous les tableau pour 1 ville : Wittenheim 68)
        Wittenheim et les années 2013 à 2015 pour comparaison avec
        http://marielaure.monde.free.fr/Finances_Locales_Web/Departement_68/Wittenheim/Wittenheim.html
    """

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
    dictAllGrandeur = database.getAllValeurs4Ville(connDB, ville[0], True)
    listAnnees = database.getListeAnnees4Ville(connDB, ville[0], False)
    assert len(listAnnees) == 3
    # Agglomère certaines grandeurs et complète dictAllGrandeur
    genCode.calculeGrandeur(config, dictAllGrandeur,
                            listAnnees, isWikicode, False)
    verbose = True

    # Lecture du modèle
    nomBaseModele = config.get('Modele', 'modele.nomBaseModele')
    numVersion = config.get('Version', 'version.number')
    typeSortie = config.get('GenCode', 'gen.idFicDetail')
    modele = nomBaseModele + '_' + numVersion + '_' + typeSortie + '.txt'
    textSection = utilitaires.lectureFiltreModele(modele, isComplet, verbose)

    textSection = genCodeTableaux.genCodeTableaux(config, dictAllGrandeur,
                                                  textSection, ville,
                                                  listAnnees, isComplet,
                                                  isWikicode, verbose)

    # Test valeur des charges en 2015
    # (cle charge) : 12659.65
    assert "12660" in textSection

    # Test valeur des charges par habitant en 2015
    # (cle fcharge) : 858.63
    assert "859" in textSection

    if isComplet:
        # Test valeur des charges de la strate en 2015
        # (cle mcharge) : 1223.21
        assert "1223" in textSection

    # Test valeur taux taxe d'habitation en 2015
    # (cle tth) : 10.11
    assert "10" in textSection

    if isComplet:
        # Test valeur taux taxe d'habitation pour la strate en 2015
        # (cle tmth) : 15.98
        assert "16" in textSection
    
    database.closeDatabase(connDB, True)

def test_getValeursDict():
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
    listAnnees = database.getListeAnnees4Ville(connDB, ville[0], False)
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

    dictAllGrandeur = database.getAllValeurs4Ville(connDB, ville[0], verbose)
    
    nbAnneesTendance = int(config.get('GenWIkiCode', 'gen.nbAnneesTendance'))
    listeAnneesTendance = sorted(listAnnees[:nbAnneesTendance])


    for grandeurs in grandeursAnalyse:
        genCodeTableaux.getValeursDict(dictAllGrandeur,
                   listeAnneesTendance, listAnnees[0],
                   grandeurs[0],
                   verbose)
        assert grandeurs[0]["l'encours de la dette"]['Valeur totale'] == 10817
        assert grandeurs[0]["l'encours de la dette"]['Par habitant'] == 734
        assert grandeurs[0]["l'encours de la dette"]['En moyenne pour la strate'] == 944
        assert grandeurs[0]["l'encours de la dette"]['dictAnneesValeur'][2013] == pytest.approx(479.18)
        assert grandeurs[0]["l'encours de la dette"]['dictAnneesValeur'][2014] == pytest.approx(671.41)
        assert grandeurs[0]["l'encours de la dette"]['dictAnneesValeur'][2015] == pytest.approx(733.67)
        break

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
    dictAllGrandeur = database.getAllValeurs4Ville(connDB, ville[0], False)
    listAnnees = database.getListeAnnees4Ville(connDB, ville[0], False)
    assert len(listAnnees) == 3
    # Agglomère certaines grandeurs et complète dictAllGrandeur
    genCode.calculeGrandeur(config, dictAllGrandeur,
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

    print("textSection AVANT genCodeTableauxPicto=", textSection)
    textSection = genCodeTableaux.genCodeTableauxPicto(config, dictAllGrandeur,
                                                       textSection,
                                                       listAnnees, isComplet,
                                                       isWikicode, False)

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
