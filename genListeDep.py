#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
*********************************************************
Programme : genListeDep.py
Auteur : Thierry Maillard (TMD)
Date : 24/5/2015 - 16/8/2016

Role : Pour s'affranchir des liste de communes de Wikipédia
        qui varient en fonction des modifications, génère des listes
        de ville par département extraits par extractionMinFi.py.
        Ces liste pourra servir de parametre à extractionMinFi.py.

Options :
    -h ou --help : Affiche ce message d'aide.
    -u ou --usage : Affice des exemples de ligne lancement
    -V ou --version : Affiche la version du programme
    -v ou --verbose : Rend le programme bavard (mode debug).

paramètres : aucun

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
import configparser
import os
import os.path
import sys
import getopt

import utilitaires
import utilCode

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
        opts, args = getopt.getopt(argv[1:],
                                   "huvV",
                                   ["help", "usage", "version", "verbose"])
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

    utilitaires.checkPythonVersion(config, verbose)

    if len(args) != 0:
        msg = __doc__ + "\nAucun paramètre autorisé !"
        print(msg)
        sys.exit(1)

    print('Début de', nomProg)

    # Création répertoire pour fichiers liste de sortie
    repertoireListeDep = config.get('EntreesSorties', 'io.repertoireListeDep')
    if not os.path.isdir(repertoireListeDep):
        if verbose:
            print("Creation répertoire des liste par département :", repertoireListeDep)
        os.makedirs(repertoireListeDep)

    # Recherche des départements présents
    print("\nRecherche des départements extraits par extractionWeb.py ...")
    repertoireExtraction = config.get('EntreesSorties', 'io.repertoireExtractions')
    listeDepartements = [nomRepDept for nomRepDept in os.listdir('.')
                         if os.path.isdir(nomRepDept) and
                         nomRepDept.startswith(repertoireExtraction + '_')]
    assert len(listeDepartements) > 0, "Aucun département à traiter !"

    indicateurNomFicBd = config.get('EntreesSorties', 'io.indicateurNomFicBd')
    nomFicListeVille = config.get('EntreesSorties', 'io.nomFicListeVille')
    print(str(len(listeDepartements)), "départements à traiter.")
    nbVille = 0
    for repDept in listeDepartements:
        # Construction du chemin du fichier liste pour ce département
        numDep = repDept.replace(repertoireExtraction + '_', '')
        numDep1 = numDep
        if len(numDep1) == 3 and numDep1.startswith('0'):
            numDep1 = numDep1[1:]
        nomFicListeVilleDep = nomFicListeVille + '_' + numDep1 + '.txt'
        pathFicListeVilleDep = os.path.join(repertoireListeDep, nomFicListeVilleDep)

        # Récupération des villes extraites pour ce département
        listeFichiers = []
        if os.path.isdir(repDept):
            listeFichiers = [nomFic for nomFic in os.listdir(repDept)
                             if indicateurNomFicBd in nomFic]

        listeVilleDict = utilCode.recupVillesFichiers(config, numDep, listeFichiers, verbose)
        if len(listeVilleDict) == 0:
            print("\nAucune ville trouvée pour générer le code dans ", repDept, " !")
        else:
            listeVilleDict.sort(key=lambda ville: ville['nom'])

            # Ouverture du fichier de sortie et écriture entête
            hFicVilles = open(pathFicListeVilleDep, 'w')
            hFicVilles.write("#codeInsee (3 chiffres)" +\
                             "; nom commune ; nom article Wikipédia\n")
            for ville in listeVilleDict:
                hFicVilles.write(ville['icom'] + ";" + \
                             ville['nom'] + ";" + ville['nomWkpFr'] + "\n")
                nbVille += 1

            hFicVilles.close()
            print('.', end='', flush=True)

    print("\nRésultats dans", repertoireListeDep, ":", str(nbVille), "villes traitées.")
    print("Utilisez : extractionWeb.py numDep pour produire le wikicode.")
    print("Fin de", nomProg)

##################################################
#to be called as a script
if __name__ == "__main__":
    main()
    sys.exit(0)

