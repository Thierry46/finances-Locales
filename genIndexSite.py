#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
*********************************************************
Programme : genIndexSite.py
Auteur : Thierry Maillard (TMD)
Date : 5/12/2019

Role : Génere l'index des départements

Options :
    -h ou --help : Affiche ce message d'aide.
    -u ou --usage : Affice des exemples de ligne lancement
    -V ou --version : Affiche la version du programme
    -v ou --verbose : Rend le programme bavard (mode debug).

paramètres :
    - chemin du répertoire ou sont stockés les résultats
        produits par genIndexSite.py

------------------------------------------------------------
Licence : GPLv3 (en français dans le fichier gpl-3.0.fr.txt)
Copyright (c) 2015 - 2020 - Thierry Maillard
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
import locale
import configparser

import utilitaires
import genHTML

##################################################
# main function
##################################################
def main(argv=None):
    """ Génere l'index des départements """

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
                                        ["../Resultats",])
        verbose = verbose or verboseOpt
        if sortiePgm:
            sys.exit(0)

    utilitaires.checkPythonVersion(config, verbose)

    if len(args) != 1:
        print(f'{__doc__}\nDonnez 1 paramètres :\n'
              "chemin des résultats de genCode.py !"
              f"\nau lieu de : {len(args)}")
        sys.exit(1)

    if not args[0]:
        raise ValueError("Donnez un chemin de répertoire à traiter !")
    resultatsPath = args[0]

    print('Début de', nomProg)

    # Recherche des départements présents
    repertoireBase = config.get('EntreesSorties', 'io.repertoireBase')
    listeDepartements = [os.path.join(resultatsPath, nomRepDept)
                         for nomRepDept in os.listdir(resultatsPath)
                         if os.path.join(resultatsPath, nomRepDept) and
                         nomRepDept.startswith(repertoireBase + '_')]
    assert len(listeDepartements) > 0, "Aucun département à traiter !"

    if verbose:
        print(f'{len(listeDepartements)} départements présents.')

    # Génération de la notice de déploiement
    genHTML.genIndexDepartement(config, resultatsPath, verbose)

    print('Fin de', nomProg, ": transférez le répertoire",\
          resultatsPath, "sur le site Web.")

##################################################
#to be called as a script
if __name__ == "__main__":
    # Contournement OS X invalide locale
    if platform.system() == 'Darwin':
        locale.setlocale(locale.LC_ALL, os.getenv('LANG'))
    main()
    sys.exit(0)
