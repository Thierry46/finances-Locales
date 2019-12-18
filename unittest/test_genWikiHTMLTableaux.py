#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name : test_genWikiHTMLTableaux.py
Author : Thierry Maillard (TMD)
Date : 1/6/2015 - 11/9/2019
Role : Tests unitaires du projet FinancesLocales avec py.test
Utilisation : python3 -m pytest [-k "nomTest"] .
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
import configparser
import os.path

import pytest

import genWikiCodeTableaux
import genHTMLCodeTableaux
import genCodeTableaux
import updateDataMinFi
import database
import utilitaires

@pytest.mark.parametrize( "isWikicode, isComplet", [
    (True, False),
    (True, True),
    (False, False),
    (False, True),
    ])
def test_genereTableau(isWikicode, isComplet):
    """
        teste la génération des données tableau pour 1 ville : Wittenheim 68)
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

    nomTableau = "PRINCIPAL"
    listeVilleWalheim = [ville
                         for ville in database.getListeVilles4Departement(connDB, '068', False)
                         if ville[0] == '068376']
    ville = listeVilleWalheim[0]
    # Recup des annees de données fiscales por WALHEIN
    listAnnees = database.getListeAnnees4Ville(connDB, ville[0], False)
    assert len(listAnnees) == 3
    nbAnneesTableau = min(int(config.get('GenWIkiCode', 'gen.nbLignesTableauxEuros')),
                          len(listAnnees))

    couleurStrate = config.get('Tableaux', 'tableaux.couleurStrate')
    couleurTitres = config.get('Tableaux', 'tableaux.couleurTitres')
    couleurSolde = config.get('Tableaux', 'tableaux.couleurSolde')
    couleurRecettes = config.get('Tableaux', 'tableaux.couleurRecettes')
    couleurCharges = config.get('Tableaux', 'tableaux.couleurCharges')
    couleurDettesCAF = config.get('Tableaux', 'tableaux.couleurDettesCAF')
    couleurEmploisInvest = config.get('Tableaux', 'tableaux.couleurEmploisInvest')
    couleurRessourcesInvest = config.get('Tableaux', 'tableaux.couleurRessourcesInvest')

    verbose = True
    listeValeurs = [
                    ["total des produits de fonctionnement",
                     genCodeTableaux.genLien(config, ["Recettes publiques",
                                                      "Produits de fonctionnement"],
                                             isWikicode, verbose),
                     couleurRecettes],
                    ["total des charges de fonctionnement",
                     genCodeTableaux.genLien(config, ["Dépenses publiques",
                                                      "Charges de fonctionnement"],
                                             isWikicode, verbose),
                     couleurCharges],
                    ["resultat comptable",
                     genCodeTableaux.genLien(config, ["Résultat fiscal en France",
                                                      "Solde de la section de fonctionnement"],
                                             isWikicode, verbose),
                     couleurSolde],
                    ["total des emplois investissement",
                     genCodeTableaux.genLien(config, ["Investissement",
                                                      "Emplois investissement"],
                                             isWikicode, verbose),
                     couleurEmploisInvest],
                    ["total des ressources d'investissement",
                     genCodeTableaux.genLien(config, ["Investissement",
                                                      "Ressources d'investissement"],
                                             isWikicode, verbose),
                     couleurRessourcesInvest],
                    ["besoin ou capacité de financement de la section investissement",
                     genCodeTableaux.genLien(config, ["Résultat fiscal en France",
                                                      "Solde de la section d'investissement"],
                                             isWikicode, verbose),
                     couleurSolde],
                   ]

    # Récupère toutes les valeurs pour cette ville pour les grandeurs demandées
    dictAllGrandeur = database.getAllValeurs4Ville(connDB, ville[0], verbose)
    # Test de la generation tableau
    if isWikicode:
        ligne = genWikiCodeTableaux.genereTableau(nomTableau, ville,
                                              listAnnees, nbAnneesTableau,
                                              listeValeurs, dictAllGrandeur,
                                              couleurTitres, couleurStrate,
                                              isComplet, verbose)
    else:
        ligne = genHTMLCodeTableaux.genereTableau(nomTableau, ville,
                                              listAnnees, nbAnneesTableau,
                                              listeValeurs, dictAllGrandeur,
                                              couleurTitres, couleurStrate,
                                              isComplet, verbose)
        
    
    # Test valeur des charges en 2015
    # (cle charge) : 12659.65
    assert "12660" in ligne

    # Test valeur des charges par habitant en 2015
    # (cle fcharge) : 858.63
    assert "859" in ligne

    if isComplet:
        # Test valeur des charges de la strate en 2015
        # (cle mcharge) : 1223.21
        assert "1223" in ligne
    
@pytest.mark.parametrize( "isWikicode, isComplet", [
    (True, False),
    (True, True),
    (False, False),
    (False, True),
    ])
def test_genereTableauTaux(isWikicode, isComplet):
    """
        teste la génération des données tableau des taux
        pour 1 ville : Wittenheim 68)
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

    nomTableau = "TAXES"
    listeVilleWalheim = [ville
                         for ville in database.getListeVilles4Departement(connDB, '068', False)
                         if ville[0] == '068376']
    ville = listeVilleWalheim[0]
    # Recup des annees de données fiscales por WALHEIN
    listAnnees = database.getListeAnnees4Ville(connDB, ville[0], False)
    assert len(listAnnees) == 3
    nbAnneesTableau = min(int(config.get('GenWIkiCode', 'gen.nbLignesTableauxEuros')),
                          len(listAnnees))

    couleurStrate = config.get('Tableaux', 'tableaux.couleurStrate')
    couleurTitres = config.get('Tableaux', 'tableaux.couleurTitres')
    couleurTaxeHabitation = config.get('Tableaux', 'tableaux.couleurTaxeHabitation')
    couleurTaxeFonciereBati = config.get('Tableaux', 'tableaux.couleurTaxeFonciereBati')
    couleurTaxeFonciereNonBati = config.get('Tableaux', 'tableaux.couleurTaxeFonciereNonBati')

    verbose = True
    listeValeurs = [
                    ["taux taxe habitation",
                     "taux taxe d'habitation",
                     couleurTaxeHabitation],
                    ["taux taxe foncière bâti",
                     "taux foncier bâti",
                     couleurTaxeFonciereBati],
                    ["taux taxe foncière non bâti",
                     "taux foncier non bâti",
                     couleurTaxeFonciereNonBati],
                   ]
    
    # Récupère toutes les valeurs pour cette ville pour les grandeurs demandées
    dictAllGrandeur = database.getAllValeurs4Ville(connDB, ville[0], verbose)

    # Test de la generation tableau
    if isWikicode:
        ligne = genWikiCodeTableaux.genereTableauTaux(nomTableau, ville,
                      listAnnees, nbAnneesTableau,
                      listeValeurs, dictAllGrandeur,
                      couleurTitres, couleurStrate,
                      isComplet, verbose)
    else:
        ligne = genHTMLCodeTableaux.genereTableauTaux(nomTableau, ville,
                      listAnnees, nbAnneesTableau,
                      listeValeurs, dictAllGrandeur,
                      couleurTitres, couleurStrate,
                      isComplet, verbose)
    
    # Test valeur taux taxe d'habitation en 2015
    # (cle tth) : 10.11
    assert "10" in ligne

    if isComplet:
        # Test valeur taux taxe d'habitation pour la strate en 2015
        # (cle tmth) : 15.98
        assert "16" in ligne
