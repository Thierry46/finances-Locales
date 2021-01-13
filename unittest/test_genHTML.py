#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name : test_genHTML.py
Author : Thierry Maillard (TMD)
Date : 1/6/2015 - 4/6/2020
Role : Tests unitaires du projet FinancesLocales avec py.test
        not global : élimine les tests globaux très long
Utilisation : python3 -m pytest [-k "nomTest"] .
 options :
    -s : pour voir les sorties sur stdout
Ref : http://sametmax.com/un-gros-guide-bien-gras-sur-les-tests-unitaires-en-python-partie-3/
Ref : http://pytest.org/latest/
prerequis : pip install pytest

Licence : GPLv3
Copyright (c) 2015 - 2020 - Thierry Maillard

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
import shutil
import configparser
import unicodedata

import pytest

import genHTML
import utilitaires

def test_enregistreIndexHTML():
    """ Test ecriture sur disque de l'index """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    numDep = "essai"
    repertoireDepBase = config.get('Test', 'io.repertoireBase')
    if os.path.isdir(repertoireDepBase):
        shutil.rmtree(repertoireDepBase, ignore_errors=True)

    repertoireDep = os.path.join(repertoireDepBase,
                config.get('EntreesSorties', 'io.repertoireBase') + '_' + numDep)
    print("Création de", repertoireDep)
    os.makedirs(repertoireDep)
    
    ficResu = config.get('EntreesSorties', 'io.nomFicIndexHTML')

    htmlText = "Salut tout le monde accentué !"
    genHTML.enregistreIndexHTML(config, repertoireDep, numDep,
                                htmlText, True)

    pathResuOK = os.path.normcase(os.path.join(repertoireDep, ficResu))
    assert os.path.isfile(pathResuOK)
    hFic = open(pathResuOK, 'r')
    page = hFic.read()
    print(page)
    hFic.close()
    assert page == htmlText

def test_enregistreIndexHTML_Pbrep():
    """ Test enregistrement répertoire inexistant """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    numDep = "essai"
    repertoireDepBase = config.get('Test', 'io.repertoireBase')
    if os.path.isdir(repertoireDepBase):
        shutil.rmtree(repertoireDepBase, ignore_errors=True)
        
    htmlText = "Salut tout le monde accentué !"
    with pytest.raises(AssertionError):
        genHTML.enregistreIndexHTML(config, repertoireDepBase, numDep,
                                    htmlText, True)

def test_litModeleHTML():
    """ Test Lecture d'un modèle en HTML """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    ficModelHTML = config.get('EntreesSorties', 'io.nomModeleIndexHTML')
    htmlText = genHTML.litModeleHTML(ficModelHTML, True)
    urlFiLoc = 'https://fr.wikipedia.org/wiki/Utilisateur:Thierry46/Finances_Locales'
    assert urlFiLoc in htmlText

def test_replaceTags():
    """ Test remplacement des mots clés dans un texte modèle """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    ficModelHTML = config.get('EntreesSorties', 'io.nomModeleIndexHTML')
    htmlText = genHTML.litModeleHTML(ficModelHTML, True)
    assert '++NOM_DEP_STR++' in htmlText
    nbCar = len(htmlText)
    nomDepStr = "Salut petit Coco !"
    assert len(nomDepStr) != len('++NOM_DEP_STR++')
    htmlText = genHTML.replaceTags(config, htmlText, nomDepStr, True)
    assert len(htmlText) != nbCar
    assert nomDepStr in htmlText
    assert '++LIGNES_VILLES++' in htmlText

def test_insertVillesTableau():
    """ Test insertion des lignes du tableux ville de l'index des départements """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    nom = 'Albas'
    html = 'Albas.html'
    wikicode = 'Albas_wikicode.html'
    score = 25
    listVilles = [
        ['007', nom, nom, 'du', 'Lot', 'FPU', 'Grosse strate', score, '99 hab.']
        ]

    htmlText = 'Bla ++LIGNES_VILLES++ Bla'
    htmlText = genHTML.insertVillesTableau(config, htmlText, listVilles, True)
    assert nom in htmlText
    assert str(score) in htmlText
    assert html in htmlText
    assert wikicode in htmlText

def test_genIndexHTML():
    """ Test génération de l'index html des villes d'un département """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    nom = 'Albas'
    nomWKP = 'Albas (Lot)'
    article = "du"
    nomDepartement = "Lot"
    typeGroupement = "FPU"
    nomStrate = "Grosse strate"
    score = 99
    population= "25 hab."
    numDepartement = "046"
    
    listVilles = [
        ['007', nom, nomWKP, article, nomDepartement,
         typeGroupement, nomStrate, score, population,
         numDepartement]
        ]
    repertoireDepBase = config.get('Test', 'io.repertoireBase')
    if os.path.isdir(repertoireDepBase):
        shutil.rmtree(repertoireDepBase, ignore_errors=True)
    repertoireDest = os.path.join(repertoireDepBase,
                                  config.get('EntreesSorties', 'io.repertoireBase')
                                  + '_' + listVilles[0][9])
    print("Creation du répertoire :", repertoireDest)
    os.makedirs(repertoireDest)

    genHTML.genIndexHTML(config, repertoireDepBase, listVilles, True)

    pathFileHTML = os.path.normcase(os.path.join(repertoireDepBase,
                       config.get('EntreesSorties', 'io.nomFicIndexHTML')))
    print("pathFileHTML=", pathFileHTML)
    assert os.path.isfile(pathFileHTML)
    hFic = open(pathFileHTML, 'r')
    page = hFic.read()
    hFic.close()
    assert nom in page
    assert str(score) in page
    assert article in page
    assert nomDepartement in page
    assert population in page

def test_convertWikicode2Html():
    """ Test l'insertion du wikicode d'une ville dans un fichier HTML """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    repTest = "essai"
    if not os.path.isdir(repTest):
        os.makedirs(repTest)

    pathVille = os.path.join(repTest, "test_convertWikicode2Html.txt")
    hFic = open(pathVille, 'w')
    chTest = """
<!--------------------------------------------------------------------
Copiez le texte ci-dessous dans l'article Finances de la commune d'Alvignac
--------------------------------------------------------------------->

<!-- !!! Contenu généré automatiquement par l'outil Finances locales !!!
    Généré le 13 septembre 2015 par le programme genWikiCode.py (complet)
    version 1.2.1 : Yin Yang Kappa du 11/8/2015
    et le modèle modele_1.2.1_detail.txt pour l'article Finances de la commune d'Alvignac.
    En cas de problème, contactez-moi SVP : Utilisateur:Thierry46
    Additionnons nos forces, partageons nos connaissances ! -->
Cet article est consacré aux [[Finances locales en France|finances locales]] d'Alvignac de 2000 à 2013<ref group="Note">Cet article ''Finances de la commune d'Alvignac'' présente une synthèse des données du site [http://www.collectivites-locales.gouv.fr/comptes-des-communes-et-des-groupements-a-fiscalite-propre-donnees-individuelles-millesimes-2000-a alize2.finances.gouv.fr] du [[Ministère de l'Économie et des Finances (France)|ministère de l'Économie et des Finances]].
Les données sont présentées de façon standardisée pour toutes les communes et ne concerne que le périmètre municipal.
Elle ne prend pas en compte les finances des [[Établissement public de coopération intercommunale|EPCI]] à fiscalité propre.
Pour constituer cette partie, l'outil Finances locales version 1.2.1 : Yin Yang Kappa [[File:Finances locales logo.png|20px|alt=Logo de l'outil Finances locales]][[File:Kappa_uc_lc.svg|20px|alt=Lettre grecque Kappa en majuscule et minuscule]] a effectué la synthèse des {{nobr|98 pages}} du site [http://www.collectivites-locales.gouv.fr/comptes-des-communes-et-des-groupements-a-fiscalite-propre-donnees-individuelles-millesimes-2000-a alize2.finances.gouv.fr] concernant Alvignac.
Finances locales est un [[logiciels libres|logiciel libre]] distribué en [[copyleft]] sous [[licence (juridique)|licence]] [[Licence publique générale GNU|GNU GPL version 3]].
</ref>.

{{Article général|Alvignac|Finances locales en France}}

Les comparaisons des [[Fraction (mathématiques)|ratio]]s par habitant sont effectuées avec ceux des communes de {{unité/2|500|à=2000|habitants}} appartenant à un groupement fiscalisé, c'est à dire à la même {{page h'|Strate#En_sciences_sociales|strate}} fiscale.

== Budget général ==
Pour l'exercice 2013, le compte administratif du [[budget]] municipal d'Alvignac s'établit à  {{euro|1161000}} en [[Dépenses publiques|dépenses]] et {{euro|1151000}} en [[Recettes publiques|recettes]]<ref group="A2" name="Alize2_2013_0"/> :
* les dépenses se répartissent en {{euro|731000}} de [[Charge (comptabilité)|charges]] de fonctionnement et {{euro|430000}} d'emplois d'[[investissement]] ;
* les recettes proviennent des {{euro|1024000}} de [[Produit (comptabilité)|produits]] de fonctionnement et de {{euro|127000}} de ressources d'investissement.

Pour Alvignac en 2013, la section de fonctionnement<ref group="Note">La  « section de fonctionnement » est constituée des [[Dépenses publiques|dépense]]s courantes et récurrentes nécessaires au bon fonctionnement des services municipaux et à la mise en œuvre des actions décidées par les élus, mais sans influence sur la consistance du [[Patrimoine (droit)|patrimoine]] de la commune. Y figure aussi le [[Plan de remboursement|remboursement]] des [[Intérêt (finance)|intérêt]]s des [[Emprunt (finance)|emprunt]]s. Elle enregistre également les [[Recettes publiques|recettes]] fiscales, les [[Dotation publique|dotation]]s et participations de l’État ainsi que les recettes d’exploitation des services municipaux.</ref> se répartit en {{euro|731000}}  de charges ({{euro|967}} par habitant) pour {{euro|1024000}} de produits ({{euro|1355}} par habitant), soit un solde de la section de fonctionnement de {{euro|293000}} ({{euro|388}} par habitant)<ref group="A2" name="Alize2_2013_0">
{{Lien web
 |titre=Les comptes des communes - Alvignac
 |sous-titre=chiffres clés
 |url=http://alize2.finances.gouv.fr/communes/eneuro/tableau.php?type=BPS&exercice=2013&dep=046&param=0&icom=003
 |consulté le=13 septembre 2015
}}.</ref>{{,}}<ref group="A2" name="Alize2_2013_1">
"""
    hFic.write(chTest)
    hFic.close()
    genHTML.convertWikicode2Html(config, pathVille, True)
    ficResu = pathVille.replace('.txt', '.html')
    htmlText = genHTML.litModeleHTML(ficResu, True)
    assert os.path.isfile(ficResu)
    assert '<PRE>' in htmlText
    assert '</PRE>' in htmlText
    assert '++TITRE++' not in htmlText
    assert '++CODE++' not in htmlText
    assert '&amp;' in htmlText
    assert '&lt;' in htmlText
    assert '&gt;' in htmlText
    # Nettoyage
    shutil.rmtree(repTest)

def test_genIndexDepartement():
    """ Test de la generation de l'index des départements disponibles """
    
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Récupération repertoire de génération de test pour les départements
    repTransfertWeb = config.get('Test', 'io.repTransfertWeb')

    # Destruction résultat précédent
    nomNoticeDeploiement = config.get('EntreesSorties', 'io.nomNoticeDeploiement')
    pathFicResu = os.path.join(repTransfertWeb, nomNoticeDeploiement)
    if os.path.isfile(pathFicResu):
        os.remove(pathFicResu)
    
     # Test fonction genIndexDepartement
    genHTML.genIndexDepartement(config, repTransfertWeb, True)

    assert os.path.isfile(pathFicResu)
    with open(pathFicResu, 'r') as hFicResu:
        text = "".join(hFicResu.readlines())
        assert "Departement_001/index.html" in text
        
def test_genIndexGroupementHTML():
    """ Test génération de l'index html des groupements de communes """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    
    sirenGroupement = '256365'
    nomArticleCC = 'CC Lot'
    nom = 'Communauté de Commune du Lot'
    region = 'Occitanie'
    département = 'Lot'
    
    listGroupements = [
        [sirenGroupement, nomArticleCC, nom, region, département]
        ]
    repertoireGroupements = config.get('Test', 'io.repertoireGroupements')
    if os.path.isdir(repertoireGroupements):
        shutil.rmtree(repertoireGroupements, ignore_errors=True)
    print("Creation du répertoire :", repertoireGroupements)
    os.makedirs(repertoireGroupements)

    genHTML.genIndexGroupementHTML(config, repertoireGroupements,
                                   listGroupements, True)

    pathFileHTML = os.path.normcase(os.path.join(repertoireGroupements,
                       config.get('EntreesSorties',
                                  'io.nomFicGroupementHTML')))
    print("pathFileHTML=", pathFileHTML)
    assert os.path.isfile(pathFileHTML)
    hFic = open(pathFileHTML, 'r')
    page = hFic.read()
    hFic.close()
    assert sirenGroupement in page
    assert utilitaires.convertLettresAccents(
        unicodedata.normalize('NFC', nom)) in page
    assert nomArticleCC in page
    assert region in page
    assert département in page

def test_insertGroupementTableau():
    """
    Test insertion des lignes du tableaux des groupements de communes
    """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')
    sirenGroupement = '256365'
    nomArticleCC = 'CC Lot'
    nom = 'Communauté de Commune du Lot'
    region = 'Occitanie'
    département = 'Lot'
    
    listGroupements = [
         [sirenGroupement, nomArticleCC, nom, region, département]
        ]

    htmlText = 'Bla ++LIGNES_GROUPEMENTS++ Bla'
    htmlText = genHTML.insertGroupementTableau(htmlText, listGroupements, True)
    assert sirenGroupement in htmlText
    assert utilitaires.convertLettresAccents(
        unicodedata.normalize('NFC', nom)) in htmlText
    assert nomArticleCC in htmlText
    assert region in htmlText
    assert département in htmlText

