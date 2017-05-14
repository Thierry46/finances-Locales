#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
*********************************************************
Programme : genPaquets.py
Auteur : Thierry Maillard (TMD)
Date : 22/7/2015

Role : Génere des paquets de wikicode par département pour mise en ligne sur un site Web.
    Traite les répertoires produits par genWikicode

Options :
    -h ou --help : Affiche ce message d'aide.
    -u ou --usage : Affice des exemples de ligne lancement
    -V ou --version : Affiche la version du programme
    -v ou --verbose : Rend le programme bavard (mode debug).

paramètres : aucun.

------------------------------------------------------------
Licence : GPLv3 (en français dans le fichier gpl-3.0.fr.txt)
Copyright (c) 2015 - Thierry Maillard
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
import shutil

import utilitaires
import genHTML

##################################################
# main function
##################################################
def main(argv=None):
    """ Prepare le déploiement pour les paquets des départements. """

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
            utilitaires.traiteOptionStd(config, option, nomProg, __doc__, [])
        verbose = verbose or verboseOpt
        if sortiePgm:
            sys.exit(0)

    utilitaires.checkPythonVersion(verbose)

    if len(args) != 0:
        print(__doc__, "\nAucun paramètre accepté !", file=sys.stderr)
        sys.exit(1)

    print('Début de', nomProg)

    repertoireBase = config.get('EntreesSorties', 'io.repertoireBase')
    repTransfertWeb = config.get('EntreesSorties', 'io.repTransfertWeb')
    if not os.path.isdir(repTransfertWeb):
        os.makedirs(repTransfertWeb)
    repPaquets = os.path.join(repTransfertWeb,
                              config.get('EntreesSorties', 'io.srepPaquets'))
    if not os.path.isdir(repPaquets):
        os.makedirs(repPaquets)

    # Recherche des départements présents
    listeDepartements = [nomRepDept for nomRepDept in os.listdir('.')
                         if os.path.isdir(nomRepDept) and
                         nomRepDept.startswith(repertoireBase)]
    msg = "Aucun département à mettre en paquet !"
    assert len(listeDepartements) > 0, msg

    if verbose:
        msg = str(len(listeDepartements)) + " départements présents."
        print(msg)

    # Création d'un paquet par département
    for repDept in listeDepartements:
        msg = "\nTraitement de " + repDept + " : "
        print(msg)

        # Création du paquet zip dans la zone de transfert WEB
        pathPaquet = os.path.join(repPaquets, repDept)
        msg = "Zip de " + repDept + " dans " + os.path.basename(pathPaquet) + ".zip"
        print(msg)
        shutil.make_archive(pathPaquet, 'zip', repDept)

        # Destruction repertoire source des paquets
        shutil.rmtree(repDept)

    # Génération de la notice de déploiement
    genHTML.genNoticeDeploiement(config, verbose)

    # Copie des logos
    genHTML.copieFicAux(config, repTransfertWeb, True)

    print('Fin de', nomProg, ", transférez le répertoire",\
          repTransfertWeb, " sur le site Web.")

##################################################
#to be called as a script
if __name__ == "__main__":
    # Contournement OS X invalide locale
    if platform.system() == 'Darwin':
        locale.setlocale(locale.LC_ALL, os.getenv('LANG'))
    main()
    sys.exit(0)
