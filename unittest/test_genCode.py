"""
Name : test_genCode.py
Author : Thierry Maillard (TMD)
Date : 25/9/2019 - 21/11/2019
Role : Tests unitaires du projet FinancesLocales avec py.test
Utilisation : python3 -m pytest [-k "nomTest"] .
options :
    -s : pour voir les sorties sur stdout
Ref : http://sametmax.com/un-gros-guide-bien-gras-sur-les-tests-unitaires-en-python-partie-3/
Ref : http://pytest.org/latest/
prerequis : pip install pytest

#Licence : GPLv3
#Copyright (c) 2015 - 2019 - Thierry Maillard

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
import time

import pytest

import genCode
import updateDataMinFi
import database
import utilitaires

@pytest.mark.parametrize( "typeCode", ["wikiArticle", "HTML"])
def test_calculeGrandeur(typeCode):
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

    # Lecture et filtrage du fichier modèle
    nomBaseModele = config.get('Modele', 'modele.nomBaseModele')
    numVersion = config.get('Version', 'version.number')
    cle = ''
    isWikicode = False
    if typeCode == "wikiArticle":
        cle = 'gen.idFicDetail'
        isWikicode = True
    elif typeCode == "HTML":
        cle = 'gen.idFicHTML'
        isWikicode = False
    typeSortie = config.get('GenCode', cle)
    modele = nomBaseModele + '_' + numVersion + '_' + typeSortie + '.txt'
    isComplet = (config.get('Modele', 'modele.type') == 'complet')
    textSection = utilitaires.lectureFiltreModele(modele, isComplet, False)

    # Lit dans la base les infos concernant la ville à traiter
    listeVilleWalheim = [ville
                         for ville in database.getListeVilles4Departement(connDB, '068', False)
                         if ville[0] == '068376']
    ville = listeVilleWalheim[0]

    # Recup des annees de données fiscales por WALHEIN
    dictAllGrandeur = database.getAllValeurs4Ville(connDB, ville[0], True)
    listAnnees = database.getListeAnnees4Ville(connDB, ville[0], True)
    assert len(listAnnees) == 3

    # Test calcul des valeurs
    genCode.calculeGrandeur(config, dictAllGrandeur, listAnnees, isWikicode, True)
    for grandeur in ["tendance ratio", "ratio dette / caf", "ratio n"]:
        assert grandeur in dictAllGrandeur

    # Fermeture base
    database.closeDatabase(connDB, True)

@pytest.mark.parametrize( "typeCode", ["wikiArticle", "HTML"])
def test_genereCode1Ville_OK(typeCode):
    """ test génération des données pour une ville """

    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    nomProg = "test_genereCode1Ville"

    # Création répertoire de sortie hebergeant les villes
    repVilles = config.get('Test', 'genCode.pathVilles')
    if not os.path.isdir(repVilles):
        os.mkdir(repVilles)
        
    # récup données de test
    pathDatabaseMini = config.get('Test', 'genCode.pathDatabaseMini')
    pathCSVMini = config.get('Test', 'genCode.pathCSVMini')
    if os.path.isfile(pathDatabaseMini):
        print("Destruction de la base de test :", pathDatabaseMini)
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

    # Création de la base de test
    param = ['updateDataMinFi.py', pathDatabaseMini, pathCSVMini]
    updateDataMinFi.main(param)
    assert os.path.isfile(pathDatabaseMini)

    # Lit dans la base les infos concernant la ville à traiter
    listeVilleWalheim = [ville
                         for ville in database.getListeVilles4Departement(connDB, '068', False)
                         if ville[0] == '068376']
    ville = listeVilleWalheim[0]

    # Test fonction de génération
    genCode.genereCode1Ville(config, connDB,
                             repVilles, ville,
                             nomProg, typeCode,
                             True, True)
    
    # Fermeture base
    database.closeDatabase(connDB, False)
    
def test_genCodeProg():
    """
    Teste le programme de génération du code Wiki et HTML
    sur base de test 1 ville et 3 années.
    """

    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Ménage répertoire de sortie
    pathOutput = config.get('Test', 'genCode.pathOutput')
    resultatsPath = pathOutput
    print("resultatsPath =", resultatsPath)

    if os.path.isdir(resultatsPath):
        print("Effacement de :", resultatsPath)
        shutil.rmtree(resultatsPath)

    # récup données de test
    pathDatabaseMini = config.get('Test', 'genCode.pathDatabaseMini')
    pathCSVMini = config.get('Test', 'genCode.pathCSVMini')
    if os.path.isfile(pathDatabaseMini):
        print("Destruction de la base de test :", pathDatabaseMini)
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
    # Création de la base de test
    param = ['updateDataMinFi.py', pathDatabaseMini, pathCSVMini]
    updateDataMinFi.main(param)
    assert os.path.isfile(pathDatabaseMini)

    # Test du programme genCode
    param = ['genCode.py', '-v', pathDatabaseMini, resultatsPath]
    genCode.main(param)

    # Vérif des résultats
    assert os.path.isdir(resultatsPath)
    assert os.path.isdir(os.path.join(resultatsPath, "Departement_068"))
    assert os.path.isfile(os.path.join(resultatsPath,
                                      "Departement_068", "index.html"))
    assert os.path.isdir(os.path.join(resultatsPath,
                                     "Departement_068", "Wittenheim"))
    assert os.path.isfile(os.path.join(resultatsPath,
                                       "Departement_068", "Wittenheim",
                                       "Wittenheim.html"))
    assert os.path.isfile(os.path.join(resultatsPath,
                                       "Departement_068", "Wittenheim",
                                       "Wittenheim_wikicode.html"))
    assert os.path.isfile(os.path.join(resultatsPath,
                                       "Departement_068", "Wittenheim",
                                       "CHARGES_FINANCIERES_SUBVENTIONS_VERSEES.svg"))

    # Fermeture base
    database.closeDatabase(connDB, False)
  
