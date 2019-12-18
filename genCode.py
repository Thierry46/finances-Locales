#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
*********************************************************
Programme : genCode.py
Auteur : Thierry Maillard (TMD)
Date : 24/5/2015 - 6/12/2019

Role : Transforme les donnees traitées par updateDataMinFi.py
        en wikicode pour enrichir les sections "Finances locale" des
        articles de Wikipedia.fr concernant les villes et les villages
        de france et en html pour un site Web.

Options :
    -h ou --help : Affiche ce message d'aide.
    -u ou --usage : Affice des exemples de ligne lancement
    -V ou --version : Affiche la version du programme
    -v ou --verbose : Rend le programme bavard (mode debug).

paramètres :
    - chemin du fichier base de données sqlite3 d'extension .db
        contenant les données
    - chemin du répertoire ou sont stockés les résultats

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
import sys
import getopt
import os
import os.path
import platform
import configparser
import locale
import time
import shutil

import utilitaires
import genCodeTexte
import genCodeTableaux
import genCodeGraphiques
import genHTML
import database
import ratioTendance


##################################################
# main function
##################################################
def main(argv=None):
    """ Génère le Wikicode et du HTML pour les villes d'un département """
    # Valeur par défaut des options
    verbose = False

    # Lecture du fichier de propriétés
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    #############################
    # Analyse des arguments reçus
    #############################
    if argv is None:
        argv = sys.argv

    nomProg = os.path.basename(argv[0])

    # parse command line options
    try:
        opts, args = getopt.getopt(
            argv[1:],
            "huvV",
            ["help", "usage", "version", "verbose"]
            )
    except getopt.error as msg:
        print(msg)
        print("To get help use --help ou -h")
        sys.exit(1)

    # process options
    for option, arg in opts:
        verboseOpt, sortiePgm = \
            utilitaires.traiteOptionStd(config, option, nomProg, __doc__,
                                        ["../database/minfi.db ../Resultats",])
        verbose = verbose or verboseOpt
        if sortiePgm:
            sys.exit(0)

    utilitaires.checkPythonVersion(config, verbose)
    isMatplotlibOk = utilitaires.checkMatplolibOK()

    if len(args) != 2:
        print(f'{__doc__}\nDonnez 2 paramètres :\n'
              "chemin base .db et chemin des résultats !"
              f"\nau lieu de : {len(args)}")
        sys.exit(1)

    databasePath = args[0]
    if not os.path.isfile(databasePath):
        raise ValueError(f"Le fichier base de données {databasePath} n'existe pas !")
    if not args[1]:
        raise ValueError("Donnez un chemin de répertoire résultat !")
    resultatsPath = os.path.normcase(args[1])

    print('Début de', nomProg)
    print("databasePath =", databasePath)
    print("resultatsPath =", resultatsPath)

    createResultDir(config, resultatsPath)

    # Ouvre la base de données
    connDB = database.createDatabase(config, databasePath, verbose)

    # Récup et traitement des départements
    traiteDepartement(config, nomProg, isMatplotlibOk, connDB, resultatsPath, verbose)

    # Ferme la base de données
    database.closeDatabase(connDB, verbose)

def createResultDir(config, resultatsPath):
    """ Création répertoire resultat pour les départements """

    if not os.path.isdir(resultatsPath):
        print("Creation repertoire résultats :", resultatsPath)
        os.makedirs(resultatsPath)
        # Copie du répertoire des images dans les résultats
        RepSrcFicAux = config.get('EntreesSorties', 'io.RepSrcFicAux')
        shutil.copytree(RepSrcFicAux, os.path.join(resultatsPath, RepSrcFicAux))
        nomNoticeTermes = config.get('EntreesSorties', 'io.nomNoticeTermes')
        shutil.copy(nomNoticeTermes, resultatsPath)

def traiteDepartement(config, nomProg, isMatplotlibOk, connDB, resultatsPath, verbose):
    """ Récup et traitement des départements """
    for departement in database.getListeDepartement(connDB, verbose):
        print("===================\nTraitement du département",
              departement[0], ":", departement[2], "...")

        # Création répertoire résultat pour ce département
        repertoireDepBase = os.path.join(resultatsPath,
                                         config.get('EntreesSorties',
                                                    'io.repertoireBase') +
                                         '_' + departement[0])
        if not os.path.isdir(repertoireDepBase):
            print("Creation repertoire du département :", repertoireDepBase)
            os.makedirs(repertoireDepBase)

        # Récup et traitement des villes du département
        auMoins1villeGenere = False
        listVilles = database.getListeVilles4Departement(connDB, departement[0], verbose)
        for ville in listVilles:
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
                                                   dictNomsVille['repVille'], ville,
                                                   nomProg, typeCode,
                                                   isMatplotlibOk, verbose)

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

        # Génération de l'index des villes
        print("-------------")
        if auMoins1villeGenere:
            genHTML.genIndexHTML(config, repertoireDepBase, listVilles, verbose)
            print("\nOK : Resultats dans le repertoire :", repertoireDepBase)
            print("Utilisez genIndexSite.py pour préparer le déploiment WEB.")
        else:
            print("Aucune commune générée !")

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
    numVersion = config.get('Version', 'version.number')
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
    modele = nomBaseModele + '_' + numVersion + '_' + typeSortie + '.txt'

    # v2.1.0 : pour cas particulier Paris : Strate = Ville -> pas de strate dans les sorties
    if ville[1] == 'Paris':
        isComplet = False
    else:
        isComplet = (config.get('Modele', 'modele.type') == 'complet')

    # Lecture et filtrage du fichier modèle
    textSection = utilitaires.lectureFiltreModele(modele, isComplet, verbose)

    # Récupère toutes les données concernant cette ville
    dictAllGrandeur = database.getAllValeurs4Ville(connDB, ville[0], verbose)
    listAnnees = database.getListeAnnees4Ville(connDB, ville[0], verbose)

    # Agglomère certaines grandeurs et complète dictAllGrandeur
    calculeGrandeur(config, dictAllGrandeur, listAnnees, isWikicode, verbose)

    # Modification des valeurs simples
    textSection = genCodeTexte.genTexte(config, dictAllGrandeur,
                                        modele, textSection,
                                        ville, listAnnees, nomProg,
                                        isWikicode, verbose)

    # Génération des tableaux pictogrammes
    textSection = genCodeTableaux.genCodeTableauxPicto(config, dictAllGrandeur,
                                                       textSection,
                                                       listAnnees,
                                                       isComplet,
                                                       isWikicode, verbose)
     # Génération des tableaux
    textSection = genCodeTableaux.genCodeTableaux(config, dictAllGrandeur,
                                                  textSection, ville,
                                                  listAnnees, isComplet,
                                                  isWikicode, verbose)

    # Generation des graphiques
    textSection = genCodeGraphiques.genCodeGraphiques(config,
                                                      repVille, dictAllGrandeur,
                                                      textSection, ville,
                                                      listAnnees, isComplet,
                                                      isWikicode, isMatplotlibOk,
                                                      verbose)

    if verbose:
        print("Sortie de genereCode1Ville")

    return textSection

def calculeGrandeur(config, dictAllGrandeur, listAnnees, isWikicode, verbose):
    """ Aglomère certaines grandeurs et complète dictAllGrandeur """

    if verbose:
        print("Entree calculeGrandeur")
    dictAllGrandeur["tendance ratio"], dictAllGrandeur["ratio dette / caf"] = \
            ratioTendance.getTendanceRatioDetteCAF(config, dictAllGrandeur,
                                                   isWikicode, verbose)
    ratioCAFDetteN = dictAllGrandeur["ratio dette / caf"][listAnnees[0]]
    dictAllGrandeur["ratio n"] = \
                           ratioTendance.presentRatioDettesCAF(config,
                                                               ratioCAFDetteN,
                                                               isWikicode, verbose)
    if verbose:
        for grandeur in ["tendance ratio", "ratio dette / caf", "ratio n"]:
            print(grandeur, "=", dictAllGrandeur[grandeur])
        print("Sortie de calculeGrandeur")

##################################################
# to be called as a script
if __name__ == "__main__":
    # Contournement OS X invalide locale
    if platform.system() == 'Darwin':
        locale.setlocale(locale.LC_ALL, os.getenv('LANG'))
    main()
    sys.exit(0)
