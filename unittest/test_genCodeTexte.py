#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name : test_genCodeTexte.py
Author : Thierry Maillard (TMD)
Date : 1/6/2015 - 14/4/2020
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

import genCodeTexte
import updateDataMinFi
import database
import utilitaires
import genCode
import genCodeCommon


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

@pytest.mark.parametrize( "typeCode", ["wikiArticle", "HTML"])
def test_genCodeTexte_func(typeCode):
    """
        test la génération des données texte pour 1 ville : Wittenheim 68)
        Choisir Wittenheim et les années 2013 à 2015 pour comparaison avec
        http://marielaure.monde.free.fr/Finances_Locales_Web/Departement_68/Wittenheim/Wittenheim.html
    """

    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # récup données de test
    pathDatabaseMini = config.get('Test', 'genCode.pathDatabaseMini')
    print("pathDatabaseMini =", pathDatabaseMini)
    pathCSVMini = config.get('Test', 'genCode.pathCSVMini')
    print("pathCSVMini =", pathCSVMini)
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
    isWikicode = True
    if typeCode == "wikiArticle":
        cle = 'gen.idFicDetail'
        isWikicode = True
    elif typeCode == "HTML":
        cle = 'gen.idFicHTML'
        isWikicode = False
    typeSortie = config.get('GenCode', cle)
    modele = nomBaseModele + '_' + typeSortie + '.txt'
    isComplet = (config.get('Modele', 'modele.type') == 'complet')
    textSection = utilitaires.lectureFiltreModele(modele, isComplet, False)

    # Lit dans la base les infos concernant la ville à traiter
    listeVilleWalheim = [ville
                         for ville in database.getListeVilles4Departement(connDB, '068', False)
                         if ville[0] == '068376']
    ville = listeVilleWalheim[0]

    # Recup des annees de données fiscales por WALHEIN
    dictAllGrandeur = database.getAllValeursDataMinFi4Entite(connDB, 'V',
                                                             ville[0], True)
    
    listAnnees = database.getListeAnneesDataMinFi4Entite(connDB, 'V',
                                                         ville[0], True)
    print("listAnnees =", listAnnees)
    assert len(listAnnees) == 3

    infosGroupement = ('200066041', 'Communauté de communes Sundgau',
                       'CC du Sundgau')
    
    # Agglomère certaines grandeurs et complète dictAllGrandeur
    genCodeCommon.calculeGrandeur(config, dictAllGrandeur,
                                  listAnnees, isWikicode, False)


    # Test de la generation du texte
    textSection = genCodeTexte.genTexte(config, dictAllGrandeur,
                                        infosGroupement,
                                        modele, textSection,
                                        ville, listAnnees,
                                        "test_genCodeTexte", isWikicode,
                                        True)
    assert "21547710" in textSection
    if not isWikicode:
        assert "Sundgau" in textSection
    database.closeDatabase(connDB, False)
   
