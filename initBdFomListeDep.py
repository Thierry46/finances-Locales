#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    *********************************************************
    Programme : initBdFomListeDep.py
    Auteur : Thierry Maillard (TMD)
    Date : 21/7/2019 - 24/11/2019

    Role : Ajoute dans la base de données fournie en parametre
    les villes à extraire désignées par les fichier par département
    updateDataMinFi.py extraiera enuite les infos pour ces seules villes.

    Options :
    -h ou --help : affiche ce message d'aide.
    -u ou --usage : affice des exemples de ligne lancement
    -V ou --version : affiche la version du programme
    -v ou --verbose : rend le programme bavard (mode debug)

    Paramètres :
    - chemin du fichier base de données sqlite3 d'extension .db
    à créer ou à mettre à jour
    - chemin d'un répertoire contenant les listes de ville par département
    à insérer dans la base
        format d'un nom de fichier : xxx_numdep.txt

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
import sqlite3
import configparser

import database
import utilitaires

##################################################
# main function
##################################################
def main(argv=None):
    """
        Stocke dans la base de données les villes indiquées dans une liste
        Sans accès à Internet.
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
        opts, args = getopt.getopt(
            argv[1:],
            "huvV",
            ["help", "usage", "version", "verbose"]
            )
    except getopt.error as msg:
        print(msg)
        print("Pour avoir de l'aide : --help ou -h", file=sys.stderr)
        sys.exit(1)

    # process options
    for option, arg in opts:
        verboseOpt, sortiePgm = \
            utilitaires.traiteOptionStd(config, option, nomProg, __doc__,
                                        ['../database/minfi.db',
                                         '../Listes_villes_par_departement'])
        verbose = verbose or verboseOpt
        if sortiePgm:
            sys.exit(0)

    # Récuperation et analyse des paramètres
    if len(args) != 2:
        msg = (f"{__doc__}\nDonnez au moins 2 paramètres :\n"
               "\tchemin base .db, nom répertoire des listes de villes !\n"
               f"\tau lieu de : {len(args)}")
        print(msg, file=sys.stderr)
        sys.exit(1)

    # Vérifie et récupère le nom de la base à mettre à jour
    databasePath = args[0]
    if not databasePath.endswith(".db"):
        msg = (f"{__doc__}\nErreur : "
               "Le nom de la base de donnée doit se terminer par .db :\n"
               f"\t{databasePath}")
        print(msg, file=sys.stderr)
        sys.exit(2)

    # Vérifie et récupère le nom du répertoire contenant les fichiers de villes par dépatement
    listeVillesPath = args[1]
    if not os.path.isdir(listeVillesPath):
        msg = (f"{__doc__}\nErreur : "
               "Le répertoire des villes par département doit exister :\n" + \
               f"\t{listeVillesPath}")
        print(msg, file=sys.stderr)
        sys.exit(2)

    listeVillesFic = [fic for fic in os.listdir(listeVillesPath)
                      if fic.endswith(".txt") and '_' in fic]
    if not listeVillesFic:
        msg = (f"{__doc__}\nErreur : "
               f"Le répertoire des villes {listeVillesPath}\n" + \
               "\tne contient aucun fichier d'extension .txt et incluant un _")
        print(msg, file=sys.stderr)
        sys.exit(3)

    print(f"Début de {nomProg}")

    for ficVille in listeVillesFic:
        try:
            posPoint = ficVille.rindex('.')
            posUnderscore = ficVille.rindex('_')
            numDep = ficVille[posUnderscore+1:posPoint]
            if len(numDep) == 2:
                numDep = f"0{numDep}"
            if isnumDep(numDep):
                print(f"Récupère les villes pour le département {numDep}")
                listeVilles4Bd = recupVillesListe(config, numDep, verbose)
                database.enregistreVilleWKP(config, databasePath, listeVilles4Bd, verbose)
            else:
                raise ValueError(f"Numéro de département invalide : {numDep}")
        except ValueError as exc:
            print(f"Fichier {ficVille} ignoré :\n{exc.value}")
        except sqlite3.IntegrityError:
            print(f"Fichier {ficVille} ignoré :\ndoublons code commune détectés")

    print("Lancer updateDataMinFi.py pour extraire les infos")
    print(f"Fin de {nomProg}")

def isnumDep(numDep):
    """
        Détermine si numDep est un nom de répertoire valide.
        Retourne True si OK
        v2.4.2 : Correction bug : retournait False pour pour numDep de la forme 02[1-9]
        """
    return len(numDep) == 3 and numDep[0] in "01" and \
        numDep[1].isnumeric() and numDep != "000" and \
        ((numDep[0] == "0" and numDep[1] == "2" and numDep[2] in 'AB') or \
         (numDep[0] == "0" and numDep[1] == "2" and numDep[2] in '123456789') or \
         (numDep[0] == "0" and numDep[1] == "9" and numDep[2] in '012345') or \
         (numDep[0] == "0" and numDep[1] not in "29" and numDep[2].isnumeric()) or \
         (numDep[0] == "1" and numDep[1] == "0" and numDep[2] in '1234'))

def recupVillesListe(config, numDep, verbose):
    """
        Récupère les villes du fichier texte
    """
    if verbose:
        print("Entrée dans recupVillesListe")
        print("\tnumDep =", numDep)

    # Construit le nom du fichier liste
    repertoireListeDep = config.get('EntreesSorties', 'io.repertoireListeDep')
    nomFicListeVille = config.get('EntreesSorties', 'io.nomFicListeVille')
    # Modif v2.4.2 : Suppr 0 devant nombre nomdep
    numDep1 = numDep
    if len(numDep1) == 3 and numDep1.startswith('0'):
        numDep1 = numDep1[1:]
    nomFicListeVilleDep = nomFicListeVille + '_' + numDep1 + '.txt'
    pathFicListeVilleDep = os.path.join(repertoireListeDep, nomFicListeVilleDep)
    print("Lecture de", pathFicListeVilleDep)

    listeVilles4Bd = []
    with open(pathFicListeVilleDep, 'r') as hFic:
        for line in hFic.read().splitlines():
            ville = analyseLigneDep(line, numDep, verbose)
            if ville:
                listeVilles4Bd.append(ville)
            print('.', end='', flush=True)

    print(f"\n{len(listeVilles4Bd)} villes lues dans {pathFicListeVilleDep}\n")

    if verbose:
        print("listeVilles4Bd (2 premiers) :\n", listeVilles4Bd[:2])
        print("Sortie de recupVilles")

    return listeVilles4Bd

def analyseLigneDep(line, numDep, verbose):
    """
        Analyse une ligne de fichier de liste de ville par département
    """
    if verbose:
        print("Entrée dans analyseLigneDep")
        print("\tline =", line)
        print("\tnumDep =", numDep)

    # Eliminate comment
    posComment = line.find('#')
    if posComment != -1:
        line = line[:posComment]

    # If not parameter line, register key and value in dictionnary ville
    elements = line.split(';')

    ville = {}
    if len(elements) == 3:
        ville['numDepartement'] = numDep
        ville['icom'] = elements[0].strip()
        ville['nomWkpFr'] = elements[2].strip()
        nomCourt = ville['nomWkpFr']
        posDept = ville['nomWkpFr'] .rfind(' (')
        if posDept != -1:
            nomCourt = ville['nomWkpFr'] [:posDept]
        ville['nom'] = nomCourt
        ville['codeCommune'] = ville['numDepartement'] + ville['icom']
    elif line: #Ligne non vide apprès suppression commentaire
        print("Erreur pour ligne :", line)

    if verbose:
        print("ville =", ville)
        print("Sortie de recupVilles")

    return ville

#################################################
#to be called as a script
if __name__ == "__main__":
    main()
    sys.exit(0)
