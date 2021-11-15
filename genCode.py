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

import utilitaires
import genCodeCommon
import genHTML
import database
import genereCode1Ville

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
    for opt in opts:
        verboseOpt, sortiePgm = \
            utilitaires.traiteOptionStd(config, opt[0], nomProg, __doc__,
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

    genCodeCommon.createResultDir(config, resultatsPath)

    # Ouvre la base de données
    connDB = database.createDatabase(config, databasePath, verbose)

    # Récup et traitement des départements
    traiteDepartement(config, nomProg, isMatplotlibOk, connDB, resultatsPath, verbose)

    # Ferme la base de données
    database.closeDatabase(connDB, verbose)

def traiteDepartement(config, nomProg, isMatplotlibOk, connDB, resultatsPath, verbose):
    """ Récup et traitement des départements """
    if verbose:
        print("Entree dans traiteDepartement")

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
            auMoins1villeGenere |= genereCode1Ville.traite1Ville(config, ville,
                                                                 repertoireDepBase,
                                                                 connDB, nomProg,
                                                                 isMatplotlibOk,
                                                                 verbose)

        # Génération de l'index des villes
        print("-------------")
        if auMoins1villeGenere:
            genHTML.genIndexHTML(config, repertoireDepBase, listVilles, verbose)
            print("\nOK : Resultats dans le repertoire :", repertoireDepBase)
            print("Utilisez genIndexSite.py pour préparer le déploiment WEB.")
        else:
            print("Aucune commune générée !")

    if verbose:
        print("Sortie de traiteDepartement")

##################################################
# to be called as a script
if __name__ == "__main__":
    # Contournement OS X invalide locale
    if platform.system() == 'Darwin':
        locale.setlocale(locale.LC_ALL, os.getenv('LANG'))
    main()
    sys.exit(0)
