"""
Name : test_genCodeGroupement.py
Author : Thierry Maillard (TMD)
Date : 25/9/2019 - 14/4/2020
Role : Tests unitaires du projet FinancesLocales avec py.test
Utilisation : python3 -m pytest [-k "nomTest"] .
options :
    -s : pour voir les sorties sur stdout
Ref : http://sametmax.com/un-gros-guide-bien-gras-sur-les-tests-unitaires-en-python-partie-3/
Ref : http://pytest.org/latest/
prerequis : pip install pytest

#Licence : GPLv3
#Copyright (c) 2015 - 2020 - Thierry Maillard

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

import genCodeGroupement
import updateDataMinFiGroupementCommunes
import database
import utilitaires
import genereCode1Groupement

@pytest.mark.parametrize( "typeCode", ["wikicode", "HTML"])
def test_genereCode1Goupement_OK(typeCode):
    """ test génération des données pour une ville """

    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    nomProg = "test_genereCode1Goupement"

    # Création répertoire de sortie hebergeant les Groupements de communes
    repGroupements = config.get('Test', 'genCode.pathGroupements')
    if not os.path.isdir(repGroupements):
        os.mkdir(repGroupements)
        
    # récup données de test
    pathDatabaseMini = config.get('Test', 'updateDataMinFiGroupement.pathDatabaseMini')
    pathCSVMini = config.get('Test', 'updateDataMinFiGroupement.pathCSVMini')
    if os.path.isfile(pathDatabaseMini):
        print("destruction de la base :", pathDatabaseMini)
        os.remove(pathDatabaseMini)

    # Insertion dans la table ville des numéros de siren à traiter
    # Création base
    connDB = database.createDatabase(config, pathDatabaseMini, False)
    # ARDON : CC Portes de Sologne présente dans fichier CSV, doit apparaitre
    connDB.executemany("""
        INSERT INTO villes(codeCommune, nomMinFi, sirenGroupement)
        VALUES (?, ?, ?)
        """, (('045006', 'ARDON', '200005932'),))
    connDB.executemany("""
        INSERT INTO groupementCommunes(sirenGroupement, nomArticleCC, nom,
        région, département, forme, siège,
                            logo, siteWeb)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (('200005932', 'CC des Portes de Sologne',
               'Communauté de communes des Portes de Sologne',
               'Centre-Val de Loire', 'Loiret',
               'Communauté de communes', 'La Ferté-Saint-Aubin',
               'Logo_EPCI_Portes_de_Sologne.png',
               'http://www.cc-lafertesaintaubin.fr'),))
    connDB.commit()

    # Appel programme
    param = ['updateDataMinFiGroupementCommunes.py',
             pathDatabaseMini, pathCSVMini]
    updateDataMinFiGroupementCommunes.main(param)
    assert os.path.isfile(pathDatabaseMini)

    if typeCode == "wikicode":
        isWikicode = True
    else:
        isWikicode = False
    modele = 'modele_groupement_' + typeCode + '.txt'
    isComplet = True

    # Récupération du groupement de commune de la base
    listGroupements = database.getListeGroupements(connDB, True)
    assert len(listGroupements) == 1
    groupement = listGroupements[0]

    # Test fonction de génération
    genereCode1Groupement.genereCode1Groupement(config, connDB,
                             repGroupements, groupement,
                             nomProg, typeCode,
                             True, True)
    
    # Fermeture base
    database.closeDatabase(connDB, False)
    
@pytest.mark.parametrize( "verbose", [True, False])
def test_genCodeGroupementProg(verbose):
    """
    Teste le programme de génération du code Wiki et HTML
    sur base de test 1 ville et 3 années.
    """

    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Ménage répertoire de sortie
    pathOutput = config.get('Test', 'genCode.pathGroupementsOutput')
    resultatsPath = pathOutput
    print("resultatsPath =", resultatsPath)

    if os.path.isdir(resultatsPath):
        print("Effacement de :", resultatsPath)
        shutil.rmtree(resultatsPath)

    pathDatabaseMini = config.get('Test', 'updateDataMinFiGroupement.pathDatabaseMini')
    pathCSVMini = config.get('Test', 'updateDataMinFiGroupement.pathCSVMini')
    if os.path.isfile(pathDatabaseMini):
        print("destruction de la base :", pathDatabaseMini)
        os.remove(pathDatabaseMini)

    # Insertion dans la table ville des numéros de siren à traiter
    # Création base
    connDB = database.createDatabase(config, pathDatabaseMini, False)
    # ARDON : CC Portes de Sologne présente dans fichier CSV, doit apparaitre
    connDB.executemany("""
        INSERT INTO villes(codeCommune, nomMinFi, sirenGroupement)
        VALUES (?, ?, ?)
        """, (('045006', 'ARDON', '200005932'),))
    connDB.executemany("""
        INSERT INTO groupementCommunes(sirenGroupement, nomArticleCC, nom,
        région, département, forme, siège,
                            logo, siteWeb)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (('200005932', 'CC des Portes de Sologne',
               'Communauté de communes des Portes de Sologne',
               'Centre-Val de Loire', 'Loiret',
               'Communauté de communes', 'La Ferté-Saint-Aubin',
               'Logo_EPCI_Portes_de_Sologne.png',
               'http://www.cc-lafertesaintaubin.fr'),))
    connDB.commit()

    # Appel programme
    param = ['updateDataMinFiGroupementCommunes.py',
             pathDatabaseMini, pathCSVMini]
    updateDataMinFiGroupementCommunes.main(param)
    assert os.path.isfile(pathDatabaseMini)

    isComplet = True

    # Test du programme genCode
    if verbose:
        param = ['genCodeGroupement.py', '-v', pathDatabaseMini, resultatsPath]
    else:
        param = ['genCodeGroupement.py', pathDatabaseMini, resultatsPath]
    genCodeGroupement.main(param)

    # Vérif des résultats
    assert os.path.isdir(resultatsPath)
    assert os.path.isdir(os.path.join(resultatsPath, "Groupements"))
    assert os.path.isdir(os.path.join(resultatsPath,
                                      "Groupements",
                                       "Communaute_de_communes_des_Portes_de_Sologne"))
    assert os.path.isfile(os.path.join(resultatsPath,
                                      "Groupements",
                                       "index_groupement.html"))
    assert os.path.isfile(os.path.join(resultatsPath,
                                      "Groupements",
                                       "Communaute_de_communes_des_Portes_de_Sologne",
                                       "Communaute_de_communes_des_Portes_de_Sologne_HTML.html"))
    assert os.path.isfile(os.path.join(resultatsPath,
                                      "Groupements",
                                       "Communaute_de_communes_des_Portes_de_Sologne",
                                       "Communaute_de_communes_des_Portes_de_Sologne_wikicode.txt"))
    # Fermeture base
    database.closeDatabase(connDB, False)
