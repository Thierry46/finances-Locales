#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name : test_genCodeTableaux.py
Author : Thierry Maillard (TMD)
Date : 1/6/2015 - 11/5/2020
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
import genCodeCommon

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
    dictAllGrandeur = database.getAllValeursDataMinFi4Entite(connDB, 'V', ville[0], False)
    listAnnees = database.getListeAnneesDataMinFi4Entite(connDB, 'V',
                                                         ville[0], False)
    assert len(listAnnees) == 3
    # Agglomère certaines grandeurs et complète dictAllGrandeur
    genCodeCommon.calculeGrandeur(config, dictAllGrandeur,
                            listAnnees, isWikicode, False)

    verbose = True

    # Lecture du modèle
    nomBaseModele = config.get('Modele', 'modele.nomBaseModele')
    typeSortie = config.get('GenCode', 'gen.idFicDetail')
    modele = nomBaseModele + '_' + typeSortie + '.txt'
    textSection = utilitaires.lectureFiltreModele(modele, isComplet, verbose)

    textSection = genCodeTableaux.genCodeTableaux(config, dictAllGrandeur,
                                                  textSection,
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

    # Recup des annees de données fiscales pour WALHEIN
    dictAllGrandeur = database.getAllValeursDataMinFi4Entite(connDB, 'V', ville[0], True)
    listAnnees = database.getListeAnneesDataMinFi4Entite(connDB, 'V',
                                                         ville[0], False)
    assert len(listAnnees) == 3
    # Agglomère certaines grandeurs et complète dictAllGrandeur
    genCodeCommon.calculeGrandeur(config, dictAllGrandeur,
                            listAnnees, isWikicode, False)
    verbose = True

    # Lecture du modèle
    nomBaseModele = config.get('Modele', 'modele.nomBaseModele')
    typeSortie = config.get('GenCode', 'gen.idFicDetail')
    modele = nomBaseModele + '_' + typeSortie + '.txt'
    textSection = utilitaires.lectureFiltreModele(modele, isComplet, verbose)

    textSection = genCodeTableaux.genCodeTableaux(config, dictAllGrandeur,
                                                  textSection,
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
