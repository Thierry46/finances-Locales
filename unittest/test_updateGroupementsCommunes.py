#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name : test_updateGroupementsCommunes.py
Author : Thierry Maillard (TMD)
Date : 9/3/2020 - 27/3/2020
Role : Tests unitaires du projet FinancesLocales avec py.test
        not global : élimine les tests globaux très long
 options :
    -s : pour voir les sorties sur stdout
Ref : http://sametmax.com/un-gros-guide-bien-gras-sur-les-tests-unitaires-en-python-partie-3/
Ref : http://pytest.org/latest/
prerequis : pip3 install pytest

Licence : GPLv3
Copyright (c) 2019 - Thierry Maillard

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
import os.path
import configparser
import urllib.request
import pytest

import updateGroupementsCommunes
import database

@pytest.mark.parametrize(\
    "nomCCVilles, listeSirenCodeCommuneOK, listSirenCCOK",
    [
        ({"046002":{"lienCC":"Communauté de communes Grand-Figeac - Haut-Ségala - Balaguier d'Olt",
                    "ancienneCommune":0,
                     "nomCC" : "Communauté de communes Grand-Figeac - Haut-Ségala - Balaguier d'Olt"},
          "046132":{"lienCC":"Communauté de communes Grand-Figeac (nouvelle)",
                    "ancienneCommune":0,
                     "nomCC" : "Communauté de communes Grand-Figeac"}},
         [("200067361", 0, "046002"), ("200067361", 0, "046132")],
         ["200067361",]
        )
    ])
def test_recupInfosCC(nomCCVilles, listeSirenCodeCommuneOK, listSirenCCOK):
    """ Test fonction de recuperation des infos sur ce groupement de communes """
    
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    
    listeSirenCodeCommune, dictSirenInfoCC = \
           updateGroupementsCommunes.recupInfosCC(config, nomCCVilles, True)
    assert listeSirenCodeCommune == listeSirenCodeCommuneOK
    assert list(dictSirenInfoCC.keys()) == listSirenCCOK
    for numSiren in dictSirenInfoCC.keys():
        assert numSiren == dictSirenInfoCC[numSiren]["sirenGroupement"]


@pytest.mark.parametrize(\
    "lienCC, dictInfos1CCOK",
    [
        ("Communauté de communes Grand-Figeac (nouvelle)",
         {"nomArticleCC":"Communauté de communes Grand-Figeac (nouvelle)",
          "sirenGroupement":"200067361",
          "nom":'Communauté de communes Grand-Figeac (nouvelle)',
          "région":"Occitanie (région administrative)",
          "département":"Lot (département) et Aveyron (département)",
          "forme":"Communauté de communes",
          "siège":"Figeac",
          "logo":"Logo CdC Grand Figeac.png",
          "siteWeb":"http://www.grand-figeac.fr"
          }),
        ("Communauté de communes Grand-Figeac - Haut-Ségala - Balaguier d'Olt",
         {"nomArticleCC":"Communauté de communes Grand-Figeac (nouvelle)",
          "sirenGroupement":"200067361",
          "nom":'Communauté de communes Grand-Figeac (nouvelle)',
          "région":"Occitanie (région administrative)",
          "département":"Lot (département) et Aveyron (département)",
          "forme":"Communauté de communes",
          "siège":"Figeac",
          "logo":"Logo CdC Grand Figeac.png",
          "siteWeb":"http://www.grand-figeac.fr"
})
    ])
def recupInfosPage1CCInfobox(lienCC, dictInfos1CCOK):
    """ Test fonction de recuperation des infos d'une pages d'une communauté de commune
        Test aussi les redirections """
    
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    assert dictInfos1CCOK == \
           updateGroupementsCommunes.recupInfosPage1CC(config, lienCC, True)

@pytest.mark.parametrize(\
    "nomArticleCC, page, dictInfos1CCOK",
    [
        ("Communauté de communes Grand-Figeac (nouvelle)",
         """
{{ébauche|intercomm|Lot|Aveyron}}
{{homon|Communauté de communes Grand-Figeac (ancienne)}}
{{Infobox Intercommunalité de France
 | nom           = Communauté de communes Grand-Figeac ''(nouvelle)''
 | logo          = Logo CdC Grand Figeac.png
 | taille logo   = <!-- facultatif -->
 | image         = <!-- facultatif -->
 | taille image  = <!-- facultatif -->
 | légende       = <!-- facultatif -->
 | région        = [[Occitanie (région administrative)|Occitanie]]
 | département   = [[Lot (département)|Lot]] et [[Aveyron (département)|Aveyron]]
 | forme         = [[Communauté de communes]]
 | siège         = [[Figeac]]
 | nbre communes = 92
 | date-création = {{Date|1|janvier|2017}}
 | date-disparition = 
 | SIREN         = 200 067 361
 | président     = Vincent Labarthe
 | étiquette     = [[Parti socialiste (France)|PS]] 
 | budget        = 
 | date-budget   = 
 | population    = 43499
 | année_pop     = 2016
 | superficie    = 1282.74
 | imageloc      = 
 | légende imageloc = 
 | site web      = [http://www.grand-figeac.fr/ grand-figeac.fr/]
}}
Bla Bla située dans les [[département français|départements]] du [[Lot (département)|Lot]] et
de l'[[Aveyron (département)|Aveyron]], en [[région française|région]]
[[Occitanie (région administrative)|Occitanie]].
         """,
         {"nomArticleCC":"Communauté de communes Grand-Figeac (nouvelle)",
          "sirenGroupement":"200067361",
          "nom":'Communauté de communes Grand-Figeac (nouvelle)',
          "région":"Occitanie (région administrative)",
          "département":"Lot (département) et Aveyron (département)",
          "forme":"Communauté de communes",
          "siège":"Figeac",
          "logo":"Logo CdC Grand Figeac.png",
          "siteWeb":"http://www.grand-figeac.fr"
          }),
        ])
def test_recupInfosPage1CCInfobox(nomArticleCC, page, dictInfos1CCOK):
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    assert dictInfos1CCOK == \
           updateGroupementsCommunes.recupInfosPage1CCInfobox(nomArticleCC, page, True)

@pytest.mark.parametrize(\
    "nomArticleCC, page, msgOk",
    [
        ("Page Vide", "", "Pas d'Infobox Intercommunalité de France"),
        ("Page bla bla", "Bla Bla", "Pas d'Infobox Intercommunalité de France"),
        ("Infobox pas cle SIREN",
         """{{Infobox Intercommunalité de France
 | nom           = Communauté de communes Grand-Figeac ''(nouvelle)''
 | logo          = Logo CdC Grand Figeac.png
 }}
         """,
         "Pas de mot clé SIREN dans l'infobox"),
        ("Infobox cle SIREN non numérique",
         """{{Infobox Intercommunalité de France
 | nom           = Communauté de communes Grand-Figeac ''(nouvelle)''
 | logo          = Logo CdC Grand Figeac.png
 | SIREN         = 200a067b361c
 }}
         """,
         "Code Siren non numérique dans page Wikipedia")

    ])
def test_recupInfosPage1CCInfobox_PB(nomArticleCC, page, msgOk):
    """ Test fonction de recuperation du nom de groupement de commune
        d'appartenance de la ville avec problème dans l'infobox """
    
    with pytest.raises(ValueError, match=msgOk):
           updateGroupementsCommunes.recupInfosPage1CCInfobox(nomArticleCC, page, True)


@pytest.mark.parametrize(\
    "page, dictInfosCCOK",
    [
        ("{{Infobox Commune de France\n|intercomm=[[alias|article]]}}",
         {"lienCC":"alias", "ancienneCommune":0, "nomCC":"article"}),
        ("{{Infobox Commune de France\n|intercomm=[[article]]}}",
         {"lienCC":"article", "ancienneCommune":0, "nomCC":"article"}),
        ("{{Infobox Commune de France\nInfobox Commune de France\n| intercomm    = [[Com Grand-Figeac (nouvelle)|Communauté de communes Grand-Figeac]]}}",
         {"lienCC":"Com Grand-Figeac (nouvelle)", "ancienneCommune":0, "nomCC":"Communauté de communes Grand-Figeac"}),
        ("{{Infobox Ancienne commune de France\n| intercomm=[[article]]}}", {"ancienneCommune":1}),
    ])
def test_recupNomCC1Ville(page, dictInfosCCOK):
    """ Test fonction de recuperation du nom de groupement de commune
        d'appartenance de la ville """

    assert dictInfosCCOK == \
           updateGroupementsCommunes.recupNomCC1Ville(page, True)

@pytest.mark.parametrize(\
    "page, msgOk",
    [
        ("", "Pas d'infobox commune de France"),
        ("Bla Bla", "Pas d'infobox commune de France"),
        ("{{Infobox Commune de France\n| intercomm    = Pas de lien",
         "Pas de champ intercom dans infobox d'une commune existante"),
        ("{{Infobox Commune de France\n|Bla Bla",
         "Pas de champ intercom dans infobox d'une commune existante"),
        ("{{Infobox Commune de France\n|intercomm = CU [[Angers Loire Métropole]]}}",
         "Pas de champ intercom dans infobox d'une commune existante"),
        ("{{Infobox Commune de France\n| intercomm = ''" + \
         "[[:Catégorie:Commune de France hors intercommunalité " + \
         "à fiscalité propre|Commune exemptée]]''}}",
         "Commune hors intercommunalité"),
    ])
def test_recupNomCC1Ville_PB(page, msgOk):
    """ Test fonction de recuperation du nom de groupement de commune
        d'appartenance de la ville avec problème dans l'infobox """
    
    with pytest.raises(ValueError, match=msgOk):
           updateGroupementsCommunes.recupNomCC1Ville(page, True)


@pytest.mark.parametrize(\
    "listeCodeCommuneNomWkp, dictNomCCVillesOK",
    [
        ([("046138", "Labastide-Murat"),],
         {"046138":{"ancienneCommune":1}}
         ),
        ([("046132", "Issendolus"),],
         {"046132":{"lienCC":"Communauté de communes Grand-Figeac (nouvelle)",
                    "ancienneCommune":0,
                     "nomCC" : "Communauté de communes Grand-Figeac"}}
         ),
        # Le test suivant portait pour Albiac une redirection :
        # Communauté de communes Grand-Figeac - Haut-Ségala - Balaguier d'Olt ->
        # Communauté de communes Grand-Figeac (nouvelle)
        # Mais Roland45 a éliminé dans Wikipedia toutes les redirections
        #vers les pages de commuauté de commubes
        ([("046002", "Albiac (Lot)"), ("046132", "Issendolus")],
         {"046002":{"lienCC":"Communauté de communes Grand-Figeac (nouvelle)",
                    "ancienneCommune":0,
                    "nomCC" : "Communauté de communes Grand-Figeac"},
          "046132":{"lienCC":"Communauté de communes Grand-Figeac (nouvelle)",
                    "ancienneCommune":0,
                    "nomCC" : "Communauté de communes Grand-Figeac"}
          }
         ),
        ([("046999", "ThierryVille"), ("046132", "Issendolus")],
         {          "046132":{"lienCC":"Communauté de communes Grand-Figeac (nouvelle)",
                    "ancienneCommune":0,
                     "nomCC" : "Communauté de communes Grand-Figeac"}}
         ),
        ([("046999", "Gouffre de Padirac"), ("046132", "Issendolus")],
         {"046132":{"lienCC":"Communauté de communes Grand-Figeac (nouvelle)",
                    "ancienneCommune":0,
                     "nomCC" : "Communauté de communes Grand-Figeac"}}
         ),
    ])
def test_recupNomCCVilles(listeCodeCommuneNomWkp, dictNomCCVillesOK):
    """ Test fonction d'analyse de recuperation du nom de groupement à partir de pages Wikipedia """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    assert dictNomCCVillesOK == \
           updateGroupementsCommunes.recupNomCCVilles(config, listeCodeCommuneNomWkp, True)

def test_updateGroupementsCommunesProg():
    """
    Test le programme de mise à jour dans la base les groupements de
    communes en recherchant leur information pour
    chaque villes enregistrée dans Wikipedia FR
    """

    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # récup données de test
    pathDatabaseCC = os.path.join(config.get('Test', 'database.testDir'),
                                  config.get('Test', 'database.testNameCC'))
    print("\test_updateGroupementsCommunesProg : base =", pathDatabaseCC)
    if os.path.isfile(pathDatabaseCC):
        print("destruction de la base :", pathDatabaseCC)
        os.remove(pathDatabaseCC)

    # Insertion dans la table villes des villes existantes
    # Création base
    connDB = database.createDatabase(config, pathDatabaseCC, False)
    
    # Villes dont il faut chercher les infos Siren + groupement de commune
    listeCodenomWkpFrCommune = (
                                ('040001', "Aire-sur-l'Adour"), # Commune avec nom complexe dans l'infobox CC
                                ('068376', 'Wittenheim'),
                                ('046132', 'Issendolus'),
                                ('046128', 'Gramat'),
                                ('075056', 'Paris'), # Commune sans nom dans l'infobox CC
                                ('012021', "La Bastide-l'Évêque") # Ancienne commune de France
                               )
    
    connDB.executemany("INSERT INTO villes(codeCommune, nomWkpFr) VALUES (?, ?)",
                       listeCodenomWkpFrCommune)
    # Groupement de commune déjà existant dans la base pour tester mise à jour
    connDB.executemany("""
        INSERT INTO groupementCommunes(nomArticleCC, nom, sirenGroupement)
        VALUES (?, ?, ?)
        """, (('Communauté_de_communes_Grand-Figeac_(nouvelle)',
               'CC Grand Figeac', '200067361'),))
    connDB.commit()

    # Test du programme updateGroupementsCommunes
    param = ['updateGroupementsCommunes.py', '-v', pathDatabaseCC]
    updateGroupementsCommunes.main(param)

     # Contrôle des valeurs de la base
    cursor = connDB.cursor()
    cursor.execute("SELECT sirenGroupement FROM villes")
    listSirenGroupement = cursor.fetchall()
    assert len(listSirenGroupement) == len(listeCodenomWkpFrCommune)
    listNumSiren = [numSiren[0] for numSiren in listSirenGroupement]
    for numSirenOK in ('200030435', '200067361', '200066009', '200066371', '200054781'):
        assert numSirenOK in listNumSiren

    cursor.execute("SELECT sirenGroupement, nom FROM groupementCommunes")
    listResultat = cursor.fetchall()
    for tupple in (('200030435', "Communauté de communes d'Aire-sur-l'Adour"),
                   ('200067361', "Communauté de communes Grand-Figeac (nouvelle)"),
                   ('200066009', "Mulhouse Alsace Agglomération"),
                   ('200066371', "Communauté de communes Causses et Vallée de la Dordogne"),
                   ('200054781', "Métropole du Grand Paris")):
        assert tupple in listResultat

    # Fermeture base
    cursor.close()
    database.closeDatabase(connDB, True)   
