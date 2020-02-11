#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
*********************************************************
Module : updateScoreWikipedia.py
Auteur : Thierry Maillard (TMD)
Date : 27/7/2019 - 10/2/2020

Role : Met à jour dans la base les scores de chaque ville
    à partir des pages de discussion Wikipedia FR.

Options :
    -h ou --help : Affiche ce message d'aide.
    -u ou --usage : Affice des exemples de ligne lancement
    -V ou --version : Affiche la version du programme
    -v ou --verbose : Rend le programme bavard (mode debug).
    -f ou --fast : Ne lance des requetes dans Wikipedia
        que pour les seules villes dont les scores
        Wikipédia ne sont pas renseignés

Paramètre :
    - chemin du fichier base de données sqlite3 d'extension .db
        à mettre à jour.

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
import configparser
import urllib.request
import urllib.error
import urllib.parse
import re

import utilitaires
import database

##################################################
# main function
##################################################
def main(argv=None):
    """
        Met à jour la base de données avec les scores Wikipedia.
    """
    # Valeur par défaut des options
    verbose = False
    isFast = False

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
        opts, args = getopt.getopt(argv[1:], "huvVf",
                                   ["help", "usage", "version", "verbose",
                                    "fast"])
    except getopt.error as msg:
        print(msg)
        print("Pour avoir de l'aide : --help ou -h", file=sys.stderr)
        sys.exit(1)

    # process options
    for option, arg in opts:
        verboseOpt, sortiePgm = \
            utilitaires.traiteOptionStd(config, option, nomProg, __doc__,
                                        ['database/minfi.db'])
        verbose = verbose or verboseOpt
        if sortiePgm:
            sys.exit(0)

        if option in ("-f", "--fast"):
            print("mode fast : ne traite que les villes de scores inconnus")
            isFast = True

    utilitaires.checkPythonVersion(config, verbose)

    # Récuperation et analyse des paramètres
    if len(args) != 1:
        msg = __doc__ + "\nDonnez 1 paramètre :\n"  + \
                "chemin base .db !" + \
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

    print('Début de', nomProg)

    # Crée la base de données si elle n'existe pas
    connDB = database.createDatabase(config, databasePath, verbose)

    # Récupère la liste des villes et des années présentes dans la base
    listeCodeCommuneNomWkp = database.getListeCodeCommuneNomWkp(connDB,
                                                                isFast,
                                                                verbose)
    if not listeCodeCommuneNomWkp:
        msg = "Erreur : La base de données :\n" + databasePath + \
                "\n ne contient aucune ville à extraire, lancer extractionWikipediaFr"
        print(msg, file=sys.stderr)

    # Calcule les scores pour chaque commune
    scoresVille = recupScoreDataVilles(config, listeCodeCommuneNomWkp, verbose)

    # Met à jour la base de données
    database.updateScoresVille(connDB, scoresVille, verbose)

    print("Sortie de", nomProg)

def recupScoreDataVilles(config, listeCodeCommuneNomWkp, verbose):
    """
    Récupération dans les Pages de discussion de chaque ville
    des données pour calculer leurs scores
    """
    if verbose:
        print("Entrée dans recupScoreDataVilles")

    # Récupération pondération de chaque label et
    # conversion en minuscule pour éviter pb casse
    dicoPoids = {
        '?' : config.getint('Score', 'poids.Indetermine'),
        'ébauche' : config.getint('Score', 'poids.Ebauche'),
        'BD' : config.getint('Score', 'poids.BD'),
        'B' : config.getint('Score', 'poids.B'),
        'A' : config.getint('Score', 'poids.A'),
        'BA' : config.getint('Score', 'poids.BA'),
        'AdQ' : config.getint('Score', 'poids.AdQ'),
        'faible' : config.getint('Score', 'poids.Faible'),
        'Faible' : config.getint('Score', 'poids.Faible'),
        'moyenne' : config.getint('Score', 'poids.Moyenne'),
        'Moyenne' : config.getint('Score', 'poids.Moyenne'),
        'élevée' : config.getint('Score', 'poids.Elevee'),
        'maximum' : config.getint('Score', 'poids.Maximum'),
        'avancement' : config.getint('Score', 'coef.avancement'),
        'importanceCDF' : config.getint('Score', 'coef.importanceCDF'),
        'importanceVDM' : config.getint('Score', 'coef.importanceVDM'),
        'popularite' : config.getint('Score', 'coef.popularite')
        }

    scoresVille = dict()
    for (codeCommune, nomWkpFr) in listeCodeCommuneNomWkp:
        # Construction du nom de la page de discussion (PDD) pour cette ville
        nomArticlePDD = config.get('Extraction', 'wikipediaFr.discussion') + \
                        urllib.request.pathname2url(nomWkpFr)

        # Lecture et analyse des criteres d'avancement et de popularité de la PDD
        # Avec délai entre 2 requetes Wikipedia pour ne pas faire croire à une attaque DOS
        utilitaires.wait2requete(config, verbose)
        try:
            page = getPageWikipediaFr(config, nomArticlePDD, verbose)
            listeCriteres = recupScoreData1Ville(config, page, nomArticlePDD, verbose)
            criteres1ville = dict()
            for critere in listeCriteres:
                criteres1ville[critere['cle']] = critere['valeur']

            # Calcule le score pour cette ville
            score = \
                dicoPoids['avancement'] * dicoPoids[criteres1ville['avancement']] + \
                dicoPoids['importanceCDF'] * dicoPoids[criteres1ville['importanceCDF']] + \
                dicoPoids['importanceVDM'] * dicoPoids[criteres1ville['importanceVDM']] + \
                dicoPoids['popularite'] * dicoPoids[criteres1ville['popularite']]
            scoresVille[codeCommune] = score
        except (urllib.error.HTTPError, ValueError) as exc:
            print("\nErreur page :", nomArticlePDD, exc, file=sys.stderr)

    print()
    if verbose:
        print("Scores des 3 premières communes :\n", scoresVille)
        print("Sortie de recupScoreDataVilles")
    return scoresVille

def recupScoreData1Ville(config, page, nomArticlePDD, verbose):
    """
    Récupération dans page de texte des données de score
    """
    if verbose:
        print("Entrée dans recupScoreData1Ville")
        print("nomArticlePDD", nomArticlePDD)

    # V1.0.5 : Précision labels acceptés et paramétrage
    avancementsOk = config.get('Score', 'label.avancementsOk').split('|')
    importancesOk = config.get('Score', 'label.importancesOk').split('|')

    # Définition des éléments déterminant le score
    # Ligne du type : | Communes de France | faible ou  | avancement = AdQ
    listeCriteres = list()
    critereimportanceCDF = {
        'cle' : 'importanceCDF',
        'nomLabel' : config.get('Score', 'nom.importanceCDF'),
        'select' : r'^[ ]*\|[ ]*' + config.get('Score', 'nom.importanceCDF') +\
                   r'[ ]*\|[ ]*(?P<importanceCDF>[A-Za-zé?]+)',
        'accept' : importancesOk
        }
    listeCriteres.append(critereimportanceCDF)
    critereavancement = {
        'cle' : 'avancement',
        'nomLabel' : config.get('Score', 'nom.avancement'),
        'select' : r'^[ ]*\|[ ]*' + config.get('Score', 'nom.avancement') +\
                   r'[ ]*=[ ]*(?P<avancement>[A-Za-zé?]+)',
        'accept' : avancementsOk
    }
    listeCriteres.append(critereavancement)
    critereimportanceVDM = {
        'cle' : 'importanceVDM',
        'nomLabel' : config.get('Score', 'nom.importanceVDM'),
        'select' : r'^[ ]*\|[ ]*' + config.get('Score', 'nom.importanceVDM') +\
                   r'[ ]*\|[ ]*(?P<importanceVDM>[A-Za-zé?]+)',
        'accept' : importancesOk
    }
    listeCriteres.append(critereimportanceVDM)
    criterepopularite = {
        'cle' : 'popularite',
        'nomLabel' : config.get('Score', 'nom.popularite'),
        'select' : r'^[ ]*\|[ ]*' + config.get('Score', 'nom.popularite') +\
                   r'[ ]*\|[ ]*(?P<popularite>[A-Za-zé?]+)',
        'accept' : importancesOk
    }
    listeCriteres.append(criterepopularite)

    # Init et compilation des expressions régulières
    for critere in listeCriteres:
        critere['valeur'] = "?"
        critere['regexp'] = re.compile(critere['select'])

    # Recherche et extraction des éléments déterminant le score
    # et conversion en minuscule pour éviter les pb de casse
    for line in page.splitlines():
        for critere in listeCriteres:
            m = critere['regexp'].search(line)
            if m: # si l'expression régulière s'applique à la ligne
                valeur = m.group(critere['cle'])
                # V1.0.5 : Précision labels acceptés et paramétrage
                trouve = False
                for labelOk in critere['accept']:
                    if labelOk == valeur:
                        trouve = True
                        critere['valeur'] = valeur
                if not trouve:
                    msg = "Problème d'analyse du modèle Wikiprojet dans cette PDD : " + \
                          nomArticlePDD + ", valeur " + valeur + \
                          " non autorisé pour le label " + \
                          critere['nomLabel'] + "!"
                    raise ValueError(msg)

    if verbose:
        print("Sortie de recupScoreData1Ville")
    return listeCriteres

def getPageWikipediaFr(config, nomArticleUrl, verbose):
    """
    Ouvre une page de Wikipedia et retourne le texte brut de la page
    if problem urllib ssl.SSLError :
    Launch "Install Certificates.command" located in Python installation directory :
    sudo '/Applications/Python 3.6/Install Certificates.command'
    """
    if verbose:
        print("Entrée dans getPageWikipediaFr")
        print("Recuperation de l'article :", nomArticleUrl)
    print('.', end='', flush=True)

    # Pour ressembler à un navigateur Mozilla/5.0
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]

    # Construction URL à partir de la config et du nom d'article
    baseWkpFrUrl = config.get('Extraction', 'wikipediaFr.baseUrl')
    actionTodo = config.get('Extraction', 'wikipediaFr.actionRow')
    urltoGet = baseWkpFrUrl + nomArticleUrl + actionTodo
    if verbose:
        print("urltoGet =", urltoGet)

    # Envoi requete, lecture de la page et decodage vers Unicode
    infile = opener.open(urltoGet)
    page = infile.read().decode('utf8')

    if verbose:
        print("Sortie de getPageWikipediaFr")
        print("Nombre de caracteres lus :", len(page))
    return page
#
##################################################
#to be called as a script
if __name__ == "__main__":
    main()
    sys.exit(0)
