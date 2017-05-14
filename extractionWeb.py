#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
*********************************************************
Programme : extractionWeb.py
Auteur : Thierry Maillard (TMD)
Date : 24/5/2015 - 22/7/2015

Role : Récupère les finances locales des communes sur le site du
        Ministère des Finances : alize2.finances.gouv.fr
        Ces donnees seront traitées par genWikiCode.py.

Options :
    -h ou --help : affiche ce message d'aide.
    -u ou --usage : affice des exemples de ligne lancement
    -V ou --version : affiche la version du programme
    -v ou --verbose : rend le programme bavard (mode debug)
    -c ou --complet : force l'extraction des données de toutes les villes d'un département.
            (par défaut, seules les villes prioritaires d'un département sont extraites)

paramètre :
    - nom de l'article de Wikipédia fr qui correspond à une ville à extraire
        ou à une liste de ville d'un département : toutes les villes sont extraites
        (voir aussi l'option -c)

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
import imp # To test if module are available
import json # To write ville dictionary in files
import configparser
import locale

import utilitaires
import extractionWikipediaFr
import extractionMinFi

##################################################
# main function
##################################################
def main(argv=None):
    """
    Extrait les données pour une ville ou une liste de ville d'un département
    depuis la base Alize2
    """
    # Valeur par défaut des options
    verbose = False
    toutesLesVilles = False

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
            "huvVc",
            ["help", "usage", "version", "verbose", "complet"]
            )
    except getopt.error as msg:
        print(msg)
        print("Pour avoir de l'aide : --help ou -h", file=sys.stderr)
        sys.exit(1)

    # process options
    for option, arg in opts:
        verboseOpt, sortiePgm = \
            utilitaires.traiteOptionStd(config, option, nomProg, __doc__,
                                        ['Liste des communes xxx',
                                         'nom_article_commune'])
        verbose = verbose or verboseOpt
        if sortiePgm:
            sys.exit(0)

        if option in ("-c", "--complet"):
            toutesLesVilles = True

    utilitaires.checkPythonVersion(verbose)

    # Contournement OS X invalide locale
    if platform.system() == 'Darwin' and locale.getlocale()[0] is None:
        locale.setlocale(locale.LC_ALL, os.getenv('LANG'))

    # Verif lxml disponible
    try:
        imp.find_module('lxml')
    except ImportError as exc:
        msg = "Erreur : ce programme utilise la bibliothèque lxml !\n" + \
              str(exc) + \
              "\nPour corriger le problème, télécharger lxml sous :\n" + \
              "\thttp://lxml.de/\n" + \
              "installation par sudo pip install lxml"
        print(msg, file=sys.stderr)
        raise

    # Récuperation du paramètre
    if len(args) != 1:
        msg = __doc__ + "\nDonnez 1 seul paramètre : " + \
               "nom d'article ou de liste Wikipédia !"
        if len(args) > 1:
            msg += "\nau lieu de : " + str(args)
        print(msg, file=sys.stderr)
        sys.exit(1)

    nomArticle = args[0]
    debutArticleliste = config.get('Extraction', 'extraction.debutArticleliste')
    isDepartement = nomArticle.startswith(debutArticleliste)

    nbMaxTableaux = config.getint('Tableaux', 'tableaux.nbMaxTableaux')
    nomsTableaux = []
    for num in range(nbMaxTableaux):
        nomsTableaux.extend([config.get('Tableaux', 'tableaux.nom'+str(num))])

    ############
    # Tableau et clé pour recherche sur site alize2 :

    # Tableaux de synthèse
    urlMinFi = config.get('Extraction', 'extraction.urlMinFi')
    # [numéro de tableau, début libellé à rechercher dans la page HTML]
    nomFic = config.get('Extraction', 'extraction.ficCleFi')
    hFic = open(nomFic, 'r')
    cleFi = json.load(hFic)
    hFic.close()
    for cle in cleFi:
        msg = "Erreur fichier : " + nomFic +  " clé tableau non numérique : " + cle[0]
        assert cle[0].isdigit(), msg
        msg = "Erreur fichier : " + nomFic + " cle tableau trop grande : " + cle[0]
        assert int(cle[0]) in range(nbMaxTableaux), msg

    # v0.7 : Tableaux de détail
    urlMinFiDetail = config.get('Extraction', 'extraction.urlMinFiDetail')
    nomFic = config.get('Extraction', 'extraction.ficCleFiDetail')
    hFic = open(nomFic, 'r')
    cleFiDetail = json.load(hFic)
    hFic.close()

    print('Début de', nomProg)
    if verbose:
        msg = ""
        if isDepartement:
            msg += "Extrait du site MinFi les données de toutes\n" + \
                    "\tles villes d'un département\n" + \
                    "nomArticle = " + nomArticle
            if toutesLesVilles:
                pass
        else:
            msg += "Extrait du site MinFi une commune les données d'une commune\n" + \
                    "nomArticle = " + nomArticle
        msg += "\ncleFi = "
        for cle in cleFi:
            msg += "\n\ttableau = " + cle[0] + ", clé= " + cle[1]
        msg += "\nurlMinFi = " + urlMinFi
        # v0.7 : Tableaux de détail
        msg += "\ncleFiDetail = "
        for cle in cleFiDetail:
            msg += "\n\ttitres=" + ", ".join(cle["titres"]) + \
                    "\n\tlibelles=" + ", ".join(cle["libelles"]) + \
                    "\n\talias=" + cle["alias"]
        msg += "\nurlMinFiDetail = " + urlMinFiDetail
        print(msg)

    #############
    # Extraction
    #############
    print("\nExtraction des données de Wikipédia pour :", nomArticle)
    print("\nAnalyse liste des villes...")
    if isDepartement:
        listeVilleDict = extractionWikipediaFr.recupVilles(config, nomArticle, verbose)
    else:
        listeVilleDict = extractionWikipediaFr.recup1Ville(config, nomArticle, verbose)
        toutesLesVilles = True

    print(len(listeVilleDict), "villes.")
    # v1.0.4 : Début : Récup. nom département et evaluation priorité de déploiement
    # Recuperation du nom du département en chaine de caractere pour la 1ere ville enregistree
    nomDepStr = extractionWikipediaFr.recupNomDepStr(config, listeVilleDict[0]['lien'], verbose)

    # Sauvegarde dans chaque ville du nom de leur département en toutes lettres
    for ville in listeVilleDict:
        ville['nomDepStr'] = nomDepStr

    # v1.0.5 : Corrige le code département 97
    corrigeDepartement97(listeVilleDict, verbose)

    # Récupération importances et avancement pour chaque ville dans leur PDD
    print("\nRécupération scores dans PDD :")
    extractionWikipediaFr.recupScoreDataVilles(config, listeVilleDict, verbose)

    # V1.0.5 : selection des seules villes prioritaires sauf si toutesLesVilles est vrai
    listeVilleDict = triSelectVilles(config, listeVilleDict, toutesLesVilles, verbose)

    # v1.0.4 : Fin : Récup. Nom département et evaluation priorité de déploiement

    print("\n" + str(len(listeVilleDict)), "communes à extraire de Alize2...")

    # Recupere les donnees financières sur le site urlMinFi et sauve les donnees
    extractionMinFi.recupDataMinFi(config, listeVilleDict, cleFi, urlMinFi,
                                   cleFiDetail, urlMinFiDetail,
                                   nomsTableaux, verbose)

    dep = listeVilleDict[0]['dep']
    if dep.startswith('0'):
        dep = dep[1:]
    print("\nUtilisez : genWikiCode.py", dep, "pour produire le wikicode.")
    print("Fin de", nomProg)

def triSelectVilles(config, listeVilleDict, toutesLesVilles, verbose):
    """
    Tri des villes par score décroissant et
    selection des seules villes prioritaires sauf si toutesLesVilles est vrai
    """
    if verbose:
        print("Entree dans triSelectVilles")
        print("toutesLesVilles =", toutesLesVilles)
        print("len(listeVilleDict)=", len(listeVilleDict))

    msg = "recupDataMinFi : Aucune ville à traiter !"
    assert len(listeVilleDict) > 0, msg

    scoreMinimum = int(config.get('Score', 'score.minimum'))
    # Tri des villes en commençant par les plus importantes
    listeVilleDict.sort(key=lambda ville: ville['Score'], reverse=True)

    # Elimination des villes non prioritaires
    if not toutesLesVilles:
        listeVilleDict = [ville for ville in listeVilleDict if ville['Score'] >= scoreMinimum]
        msg = "triSelectVilles : aucune ville prioritaire à traiter !"
        assert len(listeVilleDict) > 0, msg

    if verbose:
        print("len(listeVilleDict selection)=", len(listeVilleDict))
        print("Sortie de triSelectVilles")
    return listeVilleDict

def corrigeDepartement97(listeVilleDict, verbose):
    """
    Corrige les numéros des départements d'outremer
    97 -> 10x : nomenclature ministère des Finances
    """
    msg = "Aucune ville à traiter"
    assert len(listeVilleDict) > 0, msg

    if verbose:
        print("Entree dans corrigeDepartement97")
        print("Num departement :", listeVilleDict[0]['dep'])
        print(("Nom departement : " + listeVilleDict[0]['dep']))

    if listeVilleDict[0]['dep'] == '097':
        if 'Guadeloupe' in listeVilleDict[0]['nomDepStr']:
            dep = "101"
        elif 'Guyane' in listeVilleDict[0]['nomDepStr']:
            dep = "102"
        elif 'Martinique' in listeVilleDict[0]['nomDepStr']:
            dep = "103"
        elif 'Réunion' in listeVilleDict[0]['nomDepStr']:
            dep = "104"

        # Application à toute les communes de la liste
        for ville in listeVilleDict:
            ville['dep'] = dep

    if verbose:
        print("Num departement corrige :", listeVilleDict[0]['dep'])
        print("Sortie de corrigeDepartement97")


##################################################
#to be called as a script
if __name__ == "__main__":
    main()
    sys.exit(0)

