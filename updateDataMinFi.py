#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
*********************************************************
Module : updateDataMinFi.py
Auteur : Thierry Maillard (TMD)
Date : 1/7/2019 - 14/12/2019

Role : Met à jour la base de données du ministère des finances
    à partir des fichiers .csv du répertoire passé en paramètres
    pour toute les villes présentes dans la base.

Paramètres :
    - chemin du fichier base de données sqlite3 d'extension .db
        à créer ou à mettre à jour
    - répertoire contenant les fichiers .csv issu du site gouvernemental
        [Extraction]dataGouvFr.Comptes (FinancesLocales.properties)

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
import re
import configparser
import datetime

import utilitaires
import database

##################################################
# main function
##################################################
def main(argv=None):
    """
        Met à jour la base de données du ministère des finances
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
            utilitaires.traiteOptionStd(config, option, nomProg, __doc__,
                                        ['database/minfi.db ../recup_data_gouv_fr'])
        verbose = verbose or verboseOpt
        if sortiePgm:
            sys.exit(0)

    utilitaires.checkPythonVersion(config, verbose)

    # Récuperation et analyse des paramètres
    if len(args) != 2:
        msg = __doc__ + "\nDonnez au moins 2 paramètres :\n"  + \
                "chemin base .db et répertoire des .csv !" + \
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
    listFileCSVMinFi = []
    try:
        listFileCSVMinFi = checkPathCSVDataGouvFr(config, pathCSVDataGouvFr, verbose)
    except ValueError as exc:
        msg = __doc__ + "Erreur : paramètre répertoire des .csv !\n" + \
            "Ce repertoire doit contenir les fichiers .csv" + \
            "de données récupérés sur\n" + \
            config.get('Extraction', 'dataGouvFr.Comptes') + "\n" + \
            str(exc)
        print(msg, file=sys.stderr)
        sys.exit(3)

    print('Début de', nomProg)

    # Crée la base de données si elle n'existe pas
    connDB = database.createDatabase(config, databasePath, verbose)

    # récupère la liste des villes et des années présentes dans la base
    dictCodeCommuneAnnees = database.getDictCodeCommuneAnnees(connDB, verbose)
    if not dictCodeCommuneAnnees:
        msg = "Erreur : La base de données :\n" + databasePath + \
                "\n ne contient aucune ville à extraire, lancer extractionWikipediaFr"
        print(msg, file=sys.stderr)

    # Met à jour la base de données avec chaque fichier .CSV trouvé
    for fileCSVMinFi in listFileCSVMinFi:
        print("Traitement de :", fileCSVMinFi, "...")
        with open(fileCSVMinFi, mode='rt',
                  buffering=config.getint('Extraction',
                                          'updateDataMinFi.bufferReadingSize'),
                  encoding='utf-8') as hFicMinFi:

            # Analyse l'entête du fichier
            header = hFicMinFi.readline().strip()
            dictPositionColumns, listMissingKeys = getColumnPosition(header,
                                                                     connDB,
                                                                     verbose)
            # Print missing columns
            if len(listMissingKeys) > 0:
                print("Attention : les motcles suivants n'ont pas été trouvés :\n",
                      ";".join(listMissingKeys))

            # Enregistre si nécessaire chaque ligne du fichier
            numLine = 1
            for ligneVille in hFicMinFi:
                numLine += 1
                dictValues = analyseLigneVille(config, ligneVille,
                                               dictPositionColumns, verbose)
                if dictValues['codeCommune'] in dictCodeCommuneAnnees and \
                       int(dictValues[config.get("cleFi1Valeur", "clefi.annee")]) \
                           not in dictCodeCommuneAnnees[dictValues['codeCommune']]:
                    database.enregistreLigneVilleMinFi(config, dictValues, connDB, verbose)
            print(str(numLine) + " villes traitées")

    # Ferme la base de données
    database.closeDatabase(connDB, verbose)

def checkPathCSVDataGouvFr(config, pathCSVDataGouvFr, verbose):
    """
        Contrôle le répertoire contenant les fichiers extraits du site
        [Extraction]dataGouvFr.Comptes (FinancesLocales.properties)
        retourne la liste triée des chemin des fichiers trouvée
        """
    if verbose:
        print("Entrée dans checkPathCSVDataGouvFr")
        print("\tpathCSVDataGouvFr =", pathCSVDataGouvFr)

    if not os.path.isdir(pathCSVDataGouvFr):
        raise ValueError("Nom de répertoire des .csv incorrect : " + pathCSVDataGouvFr)

    # Filtre des fichiers du répertoire respectant le format ci-dessous
    patternFile = config.get('Extraction', 'dataGouvFr.StartFile') + \
        r'(?P<Annee>\d{4})' + \
            config.get('Extraction', 'dataGouvFr.ExtFile')
    regexp = re.compile(patternFile)
    listFileCSVMinFi = [os.path.join(pathCSVDataGouvFr, fileCSV)
                        for fileCSV in os.listdir(pathCSVDataGouvFr)
                        if regexp.search(fileCSV)]
    list.sort(listFileCSVMinFi)

    # Contrôle année des fichiers
    yearMin = config.getint('Extraction', 'dataGouvFr.YearMin')
    yearNow = datetime.date.today().year
    for pathFileMinFi in listFileCSVMinFi:
        file = os.path.basename(pathFileMinFi)
        annee = int(regexp.search(file).group('Annee'))
        if annee < yearMin or annee >= yearNow:
            raise ValueError("Fichier CSV : " + pathFileMinFi + ' annee invalide : ' + \
                             str(annee) + ' hors ]' + str(yearMin) + ',' + str(yearNow) + ']')

    if verbose:
        print("listFileCSVMinFi : ", listFileCSVMinFi)
        print("Sortie de checkPathCSVDataGouvFr")
    return listFileCSVMinFi

def getColumnPosition(header, connDB, verbose):
    """
        Contrôle que tous les codes clés de la table clesMinFi
        soient présents dans la ligne d'entête header
        passée en paramètre
        Retourne :
        - un dictionnaire (moclé : position (0:n))
        - la liste des clés manquantes
    """
    if verbose:
        print("Entrée dans getColumnPosition")
        print("header =", header)

    listMissingKeys = []

    # Récupère la liste des codes clés de la table clesMinFi
    listCodeCle = database.getListCodeClesMiniFi(connDB, verbose)

    headerList = header.replace(' ', '').split(";")
    dictPositionColumns = dict()
    for motCle in listCodeCle:
        try:
            dictPositionColumns[motCle] = headerList.index(motCle)
        except ValueError:
            listMissingKeys.append(motCle)

    if len(dictPositionColumns) == 0:
        raise ValueError("Entete CSV non valide (aucun mot-clé trouvé) " + header)

    if verbose:
        print("dictPositionColumns :", dictPositionColumns)
        print("Mots clés manquant :", listMissingKeys)
        print("Sortie de getColumnPosition")
    return dictPositionColumns, listMissingKeys

def analyseLigneVille(config, ligneVille, dictPositionColumns, verbose):
    """
    Extrait les données de ligneVille selon les position indiquées par
    dictPositionColumns
    Retourne :
    - un dictionnaire (moclé : valeurs)
    """
    if verbose:
        print("Entrée dans analyseLigneVille")
        print("ligneVille =", ligneVille)
        print("dictPositionColumns =", dictPositionColumns)

    dictValues = dict()
    lineList = ligneVille.split(";")
    try:
        for key in dictPositionColumns:
            dictValues[key] = lineList[dictPositionColumns[key]]
    except IndexError:
        raise ValueError(f"{ligneVille} : manque clé {key} "
                         f"en position {dictPositionColumns[key]}")

    # 11/12/2019 : Correction code commune et code département
    # qui à partir de 2018 sont sur 2 car au lieu de 3 dans la bd MinFi
    departement = config.get('cleFi1Valeur', 'clefi.departement')
    codeInsee = config.get('cleFi1Valeur', 'clefi.codeInsee')
    for key in [departement, codeInsee]:
        if len(dictValues[key]) not in [1, 2, 3]:
            raise ValueError(f"{ligneVille} : clé : {key} "
                             f"en position {dictPositionColumns[key]} "
                             "doit comporter 2 ou 3 caractères au lieu de "
                             f"{len(dictValues[key])}. Valeur : "
                             f"{dictValues[key]}")
        if len(dictValues[key]) == 1:
            dictValues[key] = "00" + dictValues[key]
        elif len(dictValues[key]) == 2:
            dictValues[key] = "0" + dictValues[key]

    # Création du code commune
    # Les code du département dep et code de la commune à l'intérieur du département
    # réunis forment le code commune qui sert à l'indexation des villes dans la base
    # Ref : https://fr.wikipedia.org/wiki/Code_officiel_g%C3%A9ographique#Code_commune
    dictValues['codeCommune'] = dictValues[departement] +dictValues[codeInsee]

    if verbose:
        print("dictValues :", dictValues)
        print("Sortie de analyseLigneVille")
    return dictValues
#
##################################################
#to be called as a script
if __name__ == "__main__":
    main()
    sys.exit(0)
