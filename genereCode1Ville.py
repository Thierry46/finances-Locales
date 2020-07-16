# -*- coding: utf-8 -*-
"""
*********************************************************
Programme : genereCode1Ville.py
Auteur : Thierry Maillard (TMD)
Date : 13/5/2020

Role : Genere le wikicode et le HTML pour une ville.

------------------------------------------------------------
Licence : GPLv3 (en français dans le fichier gpl-3.0.fr.txt)
Copyright (c) 2015 - 2019 - Thierry Maillard
------------------------------------------------------------

    This file is part of FinancesLocales project.

    FinancesLocales project is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    FinancesLocales project is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with FinancesLocales project.
    If not, see <http://www.gnu.org/licenses/gpl-3.0.html>.
*********************************************************
"""

import os
import os.path

import utilitaires
import database
import genCodeCommon
import genCodeTexte
import genCodeTableaux
import genCodeGraphiques
import genHTML

def traite1Ville(config, ville, repertoireDepBase,
                 connDB, nomProg, isMatplotlibOk,
                 verbose):
    """ Genere le code HTML et WikiCode pour une ville """
    if verbose:
        print("Entree dans traite1Ville")

    auMoins1villeGenere = False
    
    dictNomsVille = utilitaires.getNomsVille(config, ville[1],
                                             repertoireDepBase,
                                             verbose)
    print(dictNomsVille['nom'], 'sur disque',
          dictNomsVille['repVille'], '...')

    # V2.3.0 : on ne génère pas une ville dont le répertoire existe
    # Création du sous répertoire pour la ville
    if os.path.isdir(dictNomsVille['repVille']):
        print(ville[1], "ignoréée car le répertoire",
              dictNomsVille['repVille'], "existe.")
    else:
        auMoins1villeGenere = True
        if verbose:
            print("Creation répertoire de la commune :", dictNomsVille['repVille'])
        os.makedirs(dictNomsVille['repVille'])

        for typeCode in ["wikiArticle", "HTML"]:
            textSection = genereCode1Ville(config, connDB,
                                                            dictNomsVille['repVille'],
                                                            ville,
                                                            nomProg,
                                                            typeCode,
                                                            isMatplotlibOk,
                                                            verbose)

            if typeCode == "wikiArticle":
                indicateur = config.get('GenCode', 'gen.idFicDetail')
                extensionFic = '.txt'
            elif typeCode == "HTML":
                indicateur = ''
                extensionFic = '.html'

            # Ecriture du fichier du Wikicode et du fichier html
            # Inclusion des fichiers Wikicode dans des fichiers HTML pour
            # éviter problèmes d'encodage et travaller uniquement dans un navigateur Web.
            nomFic = utilitaires.construitNomFic(dictNomsVille['repVille'],
                                                 dictNomsVille['villeNomDisque'],
                                                 indicateur, extensionFic)
            if verbose:
                print("Ecriture du code dans :", nomFic)
            with open(nomFic, 'w') as ficVille:
                ficVille.write(textSection)

            if typeCode == "wikiArticle":
                genHTML.convertWikicode2Html(config, nomFic, verbose)

    if verbose:
        print("Sortie de traite1Ville")
        print("auMoins1villeGenere=", auMoins1villeGenere)
    return auMoins1villeGenere

def genereCode1Ville(config, connDB, repVille, ville,
                     nomProg, typeCode,
                     isMatplotlibOk, verbose):
    """ Génère le Wikicode pour une ville """
    if verbose:
        print("Entree dans genereWikicode1Ville")
        print("repVille=", repVille)
        print('ville =', ville)
        print('typeCode =', typeCode)
        print('isMatplotlibOk', isMatplotlibOk)

    nomBaseModele = config.get('Modele', 'modele.nomBaseModele')
    if typeCode == "wikiArticle":
        cle = 'gen.idFicDetail'
        isWikicode = True
    elif typeCode == "wikiSection":
        cle = 'gen.idFicSection'
        isWikicode = True
    else:
        cle = 'gen.idFicHTML'
        isWikicode = False
    typeSortie = config.get('GenCode', cle)
    modele = nomBaseModele + '_' + typeSortie + '.txt'

    # v2.1.0 : pour cas particulier Paris : Strate = Ville -> pas de strate dans les sorties
    if ville[1] == 'Paris':
        isComplet = False
    else:
        isComplet = (config.get('Modele', 'modele.type') == 'complet')
    isGroupement = False

    # Lecture et filtrage du fichier modèle
    textSection = utilitaires.lectureFiltreModele(modele, isComplet, verbose)

    # Récupère toutes les données concernant cette ville
    dictAllGrandeur = database.getAllValeursDataMinFi4Entite(connDB, "V",
                                                             ville[0], verbose)
    listAnnees = database.getListeAnneesDataMinFi4Entite(connDB, 'V',
                                                         ville[0], verbose)
    infosGroupement = database.getListeVilleGroupement(connDB, ville[0],
                                                       verbose)

    # Agglomère certaines grandeurs et complète dictAllGrandeur
    genCodeCommon.calculeGrandeur(config, dictAllGrandeur,
                                  listAnnees, isWikicode, verbose)

    # Modification des valeurs simples
    textSection = genCodeTexte.genTexte(config, dictAllGrandeur,
                                        infosGroupement,
                                        modele, textSection,
                                        ville, listAnnees, nomProg,
                                        isWikicode, verbose)

    # Définit le contenu des tableaux picto
    grandeursAnalyse = genCodeTableaux.defTableauxPicto(config,
                                        dictAllGrandeur, listAnnees,
                                        isWikicode, verbose)   

    # Génération des tableaux pictogrammes
    textSection = genCodeCommon.genCodeTableauxPicto(config, dictAllGrandeur,
                                                     grandeursAnalyse,
                                                     textSection,
                                                     listAnnees,
                                                     isComplet,
                                                     isWikicode,
                                                     True,
                                                     isGroupement,
                                                     verbose)
     # Génération des tableaux
    textSection = genCodeTableaux.genCodeTableaux(config, dictAllGrandeur,
                                                  textSection,
                                                  listAnnees, isComplet,
                                                  isWikicode, verbose)

    # Generation des graphiques
    textSection = genCodeGraphiques.genCodeGraphiques(config,
                                                      repVille, dictAllGrandeur,
                                                      textSection, ville[1],
                                                      listAnnees, isComplet,
                                                      isWikicode, isMatplotlibOk,
                                                      verbose)

    if verbose:
        print("Sortie de genereCode1Ville")

    return textSection
