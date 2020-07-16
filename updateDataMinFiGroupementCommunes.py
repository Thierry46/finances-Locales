#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
*********************************************************
Module : updateDataMinFiGroupementCommunes.py
Auteur : Thierry Maillard (TMD)
Date : 9/4/2020

Role : Met à jour les données de groupement de communes de
    la base de données du ministère des finances
    à partir des fichiers .csv du répertoire passé en paramètres
    pour toute les villes présentes dans la base.

Paramètres :
    - chemin du fichier base de données sqlite3 d'extension .db
        à mettre à jour
    - Fichier .csv des groupements de communes,
        issu du site gouvernemental
        [Extraction]dataGouvFr.Comptes (FinancesLocales.properties)

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
import configparser

import utilitaires
import database
import updateDataMinFiCommon

##################################################
# main function
##################################################
def main(argv=None):
    """
        Met à jour les données de groupement de communes de
        la base de données du ministère des finances
        à partir des fichiers .csv du répertoire passé en paramètres.
    """
    # Valeur par défaut des options
    verbose = False

    # Lecture du fichier de propriétés
    config = configparser.RawConfigParser()
    ficProperties = 'FinancesLocales.properties'
    config.read(ficProperties)

    #############################
    # Analyse des arguments reçus
    #############################
    if argv is None:
        argv = sys.argv

    nomProg = os.path.basename(argv[0])

    # parse command line options
    try:
        opts, args = getopt.getopt(argv[1:], "huvV",
                                   ["help", "usage", "version", "verbose"])
    except getopt.error as msg:
        print(msg)
        print("Pour avoir de l'aide : --help ou -h", file=sys.stderr)
        sys.exit(1)

    # process options
    for option, arg in opts:
        verboseOpt, sortiePgm = \
            utilitaires.traiteOptionStd(config, option, nomProg, __doc__, \
                 ['database/minfi.db ../recup_data_gouv_fr_colectivite/comptes-groupements.csv'])
        verbose = verbose or verboseOpt
        if sortiePgm:
            sys.exit(0)

    utilitaires.checkPythonVersion(config, verbose)

    # Récuperation et analyse des paramètres
    if len(args) != 2:
        msg = __doc__ + "\nDonnez au moins 2 paramètres :\n"  + \
                "chemin base .db et fichier .csv !" + \
                "\nau lieu de : " + str(len(args))
        print(msg, file=sys.stderr)
        sys.exit(1)

    # Vérifie et récupère le nom de la base à mettre à jour
    databasePath = args[0]
    if not databasePath.endswith(".db"):
        msg = __doc__ + "Erreur : Le nom de la base de donnée doit se terminer par .db :\n" + \
                databasePath
        print(msg, file=sys.stderr)
        sys.exit(2)

    # Vérifie et récupère les noms des fichiers de données du ministère des finances
    pathCSVDataGouvFr = args[1]
    if not os.path.isfile(pathCSVDataGouvFr):
        msg = __doc__ + "Erreur : paramètre fichier .csv !\n" + \
            "Ce fichiers .csv doit être récupérés sur\n" + \
            config.get('Extraction', 'dataGouvFr.Comptes') + ":\n" + \
            pathCSVDataGouvFr
        print(msg, file=sys.stderr)
        sys.exit(3)

    print('Début de', nomProg)

    # Crée la base de données si elle n'existe pas
    connDB = database.createDatabase(config, databasePath, verbose)

    # Récupère les numéros de SIREN des groupements dans la base
    # ainsi que leurs noms et années des infos financières déjà enregistrées.
    dictSirenInfos = database.getSirenInfosGroupementsAnnees(connDB, verbose)
    if not dictSirenInfos:
        msg = "Erreur : La base de données :\n" + databasePath + \
                "\n ne contient aucun groupement de commune à extraire," +\
                "lancer updateGroupementsCommunes"
        print(msg, file=sys.stderr)

    # Met à jour la base de données le fichier .CSV passé en paramètres
    print("Traitement de :", pathCSVDataGouvFr, "...")
    with open(pathCSVDataGouvFr, mode='rt',
              buffering=config.getint('Extraction',
                                      'updateDataMinFi.bufferReadingSize'),
              encoding='utf-8') as hFicMinFi:

        # Analyse l'entête du fichier
        header = hFicMinFi.readline().strip()
        dictPositionColumns, listMissingKeys = \
           updateDataMinFiCommon.getColumnPosition(header, "GC",
                                                   connDB, verbose)
        # Print missing columns
        if len(listMissingKeys) > 0:
            print("Attention : les motcles suivants n'ont pas été trouvés :\n",
                  ";".join(listMissingKeys))

        # Enregistre si nécessaire chaque ligne du fichier
        numLine = 1
        numGroupement = 0
        for ligneVille in hFicMinFi:
            numLine += 1
            dictValues = analyseLigneGroupement(ligneVille,
                                                dictPositionColumns,
                                                verbose)
            # Analyse et enregistre les valeurs de cette ligne
            if "siren" in dictValues and dictValues["siren"].isdigit() and \
               len(dictValues["siren"]) == 9 and \
               "exer" in dictValues and dictValues["exer"].isdigit() and \
               len(dictValues["exer"]) == 4 and \
               dictValues["siren"] in dictSirenInfos and \
               int(dictValues["exer"]) not in dictSirenInfos[dictValues["siren"]][2]:
                numGroupement += 1
                database.enregistreLigneGroupementMinFi(dictValues, connDB, verbose)
                print('.', end='', flush=True)
            else:
                print('X', end='', flush=True)

        print("\n", numLine-1, "lignes traitées,", numGroupement, "groupements enregistrés")

    # Ferme la base de données
    database.closeDatabase(connDB, verbose)


def analyseLigneGroupement(ligneGroupement,
                           dictPositionColumns,
                           verbose):
    """
    Extrait les données de ligneGroupement selon les position indiquées par
    dictPositionColumns
    Retourne :
    - un dictionnaire (moclé : valeurs)
    """
    if verbose:
        print("Entrée dans analyseLigneGroupement")
        print("ligneVille =", ligneGroupement)
        print("dictPositionColumns =", dictPositionColumns)

    dictValues = dict()
    lineList = ligneGroupement.split(";")
    for key in dictPositionColumns:
        try:
            dictValues[key] = lineList[dictPositionColumns[key]]
        except IndexError:
            # De nombreuses clés peuvent manquer dans le fichier
            pass

    if verbose:
        print("dictValues :", dictValues)
        print("Sortie de analyseLigneGroupement")
    return dictValues

#
##################################################
#to be called as a script
if __name__ == "__main__":
    main()
    sys.exit(0)
