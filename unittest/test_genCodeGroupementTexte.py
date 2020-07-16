#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name : test_genCodeGroupementTexte.py
Author : Thierry Maillard (TMD)
Date : 14/4/2020
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

import pytest

import genCodeGroupementTexte
import updateDataMinFiGroupementCommunes
import database
import utilitaires
import genCode
import genCodeCommon

@pytest.mark.parametrize( "typeCode", ["wikicode", "HTML"])
def test_genCodeGroupementTexte_func(typeCode):
    """
        test la génération des données texte pour un groupement de commune :
        ARDON)
        Choisir Wittenheim et les années 2013 à 2015 pour comparaison avec
        http://marielaure.monde.free.fr/Finances_Locales_Web/Departement_68/Wittenheim/Wittenheim.html
    """

    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    verbose = True

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
    listGroupements = database.getListeGroupements(connDB, verbose)
    assert len(listGroupements) == 1
    groupement = listGroupements[0]

    # Lecture et filtrage du fichier modèle
    modele = 'modele_groupement_' + typeCode + '.txt'
    with open(modele, 'r') as modelefile:
        textSection = modelefile.read()

         # Récupère toutes les données concernant ce groupement
        dictAllGrandeur = database.getAllValeursDataMinFi4Entite(connDB, "GC",
                                                                 groupement[0],
                                                                 verbose)
        listAnnees = database.getListeAnneesDataMinFi4Entite(connDB, 'GC',
                                                             groupement[0],
                                                             verbose)

        # Agglomère certaines grandeurs et complète dictAllGrandeur
        genCodeCommon.calculeGrandeur(config, dictAllGrandeur,
                                      listAnnees, isWikicode,
                                      verbose)

        # Modification des valeurs simples
        textSection = genCodeGroupementTexte.genTexte(config, dictAllGrandeur,
                                        modele, textSection,
                                        groupement, listAnnees,
                                        "test_genCodeGroupementTexte",
                                        isWikicode, verbose)
        assert textSection
        assert "Communauté de communes des Portes de Sologne" in textSection
        if typeCode != "wikicode":
            assert "CC des Portes de Sologne" in textSection
            assert '200005932' in textSection
        assert "4831000" in textSection # charges de fonctionnement
        assert "1727000" in textSection # emplois d'investissement
        
    database.closeDatabase(connDB, False)
   
