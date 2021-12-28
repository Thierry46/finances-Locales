#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
*********************************************************
Module : updateGroupementsCommunes.py
Auteur : Thierry Maillard (TMD)
Date : 8/3/2020 - 28/12/2021

Role : met à jour dans la base les groupements de communes
       en recherchant dans Wikipedia les informations pour
       chaque ville enregistrée dans la base de données.

Options :
    -h ou --help : Affiche ce message d'aide.
    -u ou --usage : Affice des exemples de ligne lancement
    -V ou --version : Affiche la version du programme
    -v ou --verbose : Rend le programme bavard (mode debug).
    -f ou --fast : Ne lance des requetes dans Wikipedia
        que pour les seules villes dont les regoupements de
        communes ne sont pas renseignés

Paramètre :
    - chemin du fichier base de données sqlite3 d'extension .db
        à mettre à jour.
    - facultatif : nombre maxi de villes à traiter

------------------------------------------------------------
Licence : GPLv3 (en français dans le fichier gpl-3.0.fr.txt)
Copyright (c) 2021 - Thierry Maillard
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
import re

import utilitaires
import database

# Expressions régulières précompilées hors de la fonction pour performances

# | intercomm = [[CC Grand-Figeac|Communauté de communes Grand-Figeac]]
regExpNomCCAlias = re.compile(r'^[ ]*\|[ ]*intercomm[ ]*=[ ]*' +
                              r'[\[]{2}(?P<lienCC>[^\]]*?)\|(?P<nomCC>.*?)[\]]{2}')
regExpNomCCDirect = re.compile(r'^[ ]*\|[ ]*intercomm[ ]*=[ ]*' +
                               r'[\[]{2}(?P<nomCC>.*?)[\]]{2}')
regExpNomCCExemption = re.compile(r'^[ ]*\|[ ]*intercomm[ ]*=.*' +
                                  r'hors intercommunalité')

# {{Infobox Intercommunalité de France
regExpInfoboxGroupementCommunes = re.compile(r'^[ ]*[\{]{2}[ ]*Infobox Intercommunalité de France')
regExpInfoboxCommune = re.compile(r'^[ ]*[\{]{2}[ ]*Infobox Commune de France')
regExpInfoboxAncienneCommune = re.compile(r'^[ ]*[\{]{2}[ ]*Infobox Ancienne commune de France')

# Exemple de syntaxe : | SIREN         = 200 067 361
listeCleRegExp = [(motCle, champBd,
                   re.compile(r'^[ ]*\|[ ]*' + motCle + r'[ ]*=[ ]*(?P<' + champBd +
                              r'>.*)[ \|]*'))
                  for (motCle, champBd)
                  in (('SIREN', 'sirenGroupement'),
                      ('nom', 'nom'),
                      ('logo', 'logo'),
                      ('région', 'région'),
                      ('département', 'département'),
                      ('forme', 'forme'),
                      ('siège', 'siège'),
                      ('site web', 'siteWeb')
                      )]

##################################################
# main function
##################################################
def main(argv=None):
    """
        Met à jour la base de données avec les
        infos sur les regroupements de communes.
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
    for opt in opts:
        verboseOpt, sortiePgm = \
            utilitaires.traiteOptionStd(config, opt[0], nomProg, __doc__,
                                        ['database/minfi.db'])
        verbose = verbose or verboseOpt
        if sortiePgm:
            sys.exit(0)

        if opt[0] in ("-f", "--fast"):
            print("\nMode fast : ne traite que les villes (non anciennes)\n"
                  "\tdont les numéros de SIREN sont inconnus")
            isFast = True

    utilitaires.checkPythonVersion(config, verbose)

    # Récuperation et analyse des paramètres
    if len(args) not in [1, 2]:
        print(f'{__doc__}\nDonnez 1 ou 2 paramètres :\n'
              "chemin base .db\nOptionnel : nb max de villes à traiter !"
              f"\nau lieu de : {len(args)}", file=sys.stderr)
        sys.exit(1)

    # Vérifie et récupère le nom de la base à mettre à jour
    databasePath = args[0]
    if not databasePath.endswith(".db"):
        print(f'{__doc__}\nNom de base de données non valide :\n'
              f'il doit se terminer par .db : {databasePath}',
              file=sys.stderr)
        sys.exit(2)

    nbMaxVille = 0
    if len(args) == 2:
        nbMaxVille = int(args[1])

    print('Début de', nomProg, "database=", databasePath,
          ', nbMaxVille=', nbMaxVille)

    # Ouvre la base de données
    connDB = database.createDatabase(config, databasePath, verbose)

    # Récupère la liste des villes et des années présentes dans la base
    listeCodeCommuneNomWkp = \
            database.getListeCodeCommuneNomWkp(connDB,
                                               isFast,
                                               "sirenGroupement",
                                               verbose)
    if not listeCodeCommuneNomWkp:
        print(f'Erreur : La base de données :\n{databasePath}'
              "\n ne contient aucune ville à extraire, lancer extractionWikipediaFr",
              file=sys.stderr)
    if nbMaxVille > 0:
        print(f'Attention : seulement {nbMaxVille} communes traitées !'
              "\nUtilisez l'option -f au prochain run.")
        listeCodeCommuneNomWkp = listeCodeCommuneNomWkp[:nbMaxVille]

    print("\nCodes utilisés :\n"
          "- . Extraction d'une page Wikipédia ;\n"
          "- Z Attente pour ne pas surcharger Wikipédia ;\n"
          "- A Ancienne commune : ignorée et marquée dans la base ;\n"
          "- R Page de redirection traversée ;\n")

    print("Récuperation des noms des groupements des villes...")
    nomCCVilles = recupNomCCVilles(config, listeCodeCommuneNomWkp, verbose)

    print("Récupération des infos sur les communautés de communes...")
    # Récupération des infos sur les communautés de communes
    listeSirenCodeCommune, dictSirenInfoCC = recupInfosCC(config, nomCCVilles, verbose)

    # Met à jour la base de données
    print("Enregistrement dans la base...")
    database.updateInfosGroupement(connDB, listeSirenCodeCommune,
                                   dictSirenInfoCC, verbose)

    print("Sortie de", nomProg)

def recupInfosCC(config, nomCCVilles, verbose):
    """
    Récupération dans les Pages Wikipedia, pour chaque communauté de communes
    présente dans nomCCVilles, des infos sur ce groupement de communes.
    Entrée : nomCCVilles : dict {codeCommune:{"lienCC", "ancienneCommune", "nomCC"}}
    Sortie :
        - listeSirenCodeCommune liste [sirenGroupement, ancienneCommune, codeCommune]
        - dictSirenInfoCC dict {sirenGroupement, dictInfos1CC}
    """
    if verbose:
        print("Entrée dans recupInfosCC")

    # Itération sur les liens CC sans doublons pour récupérer les infos sur les CC
    dictInfoCC = {}
    for lienCC in {nomCCVilles[codeCommune]["lienCC"]
                       for codeCommune in nomCCVilles
                       if nomCCVilles[codeCommune]["ancienneCommune"] == 0}:
        try:
            dictInfoCC[lienCC] = recupInfosPage1CC(config, lienCC, verbose)
        except ValueError as exc:
            print("\n", exc, file=sys.stderr)

    # Création liste [codeComune, ancienneCommune, numéros de Siren] pour maj tables villes
    listeSirenCodeCommune = []
    for codeCommune in nomCCVilles:
        sirenGroupement = None
        if "lienCC" in nomCCVilles[codeCommune]:
            if nomCCVilles[codeCommune]["lienCC"] in dictInfoCC:
                sirenGroupement = dictInfoCC[nomCCVilles[codeCommune]["lienCC"]]["sirenGroupement"]
        if sirenGroupement or nomCCVilles[codeCommune]["ancienneCommune"] == 1:
            listeSirenCodeCommune.append((sirenGroupement,
                                          nomCCVilles[codeCommune]["ancienneCommune"],
                                          codeCommune))

    # Construction de dictSirenInfoCC dict {sirenGroupement, dictInfos1CC}
    # Pour éliminer les numéros de Siren en double
    dictSirenInfoCC = {dictInfoCC[lienCC]["sirenGroupement"]:
                       dictInfoCC[lienCC]
                       for lienCC in dictInfoCC}

    if verbose:
        print("Sortie de recupInfosCC")
    return listeSirenCodeCommune, dictSirenInfoCC

def recupInfosPage1CC(config, lienCC, verbose):
    """
    Récupération dans l'infobox d'un article Wikipedia d'une communauté de commune
    des informations présentes dans l'Infobox Intercommunalité de France
    retour dictInfos1CC {nomArticleCC, sirenGroupement + champs définis dans listeCleRegExp}
    Exception ValueError : si page Wikipedia inexistante

    Remarque :
    Certaines informations existent dans l'infobox mais peuvent être difficile à récupéré :
    population (nombre d'habitants de l'EPCI), superficie, nombre de communes.
    car elles sont affichées par le modèle EPCI-pop1
    https://fr.wikipedia.org/wiki/Mod%C3%A8le:EPCI-pop1
    Je ne sais pas récupérer les données produites par un modèle.
    """
    if verbose:
        print("Entrée dans recupInfosPage1CC :", lienCC)

    # Elimine les redirections de pages Wikipedia et lit la page finale
    nomArticleCC, page = utilitaires.jumpRedirGetPageWikipediaFr(config, lienCC, verbose)

    # Recuperation des information pour cette communauté de commune
    dictInfos1CC = recupInfosPage1CCInfobox(nomArticleCC, page, verbose)

    if verbose:
        print("Sortie de recupInfosPage1CC")
    return dictInfos1CC

def recupInfosPage1CCInfobox(nomArticleCC, page, verbose):
    """
    Récupère dans la chaine de caractere page les informations
    présentes dans l'Infobox Intercommunalité de France
    Entrée :
        - nomArticleCC : nom d'article à enregistrer dans le dico
        - page : la page contenant l'infobox d'un article Wikipedia
            d'une communauté de commune
    retour dictInfos1CC {nomArticleCC, sirenGroupement + champs définis dans listeCleRegExp}
    """
    if verbose:
        print("Entrée dans recupInfosPage1CCInfobox")
        print("page Wikipedia nomArticleCC=", nomArticleCC)

    dictInfos1CC = {}
    dictInfos1CC["nomArticleCC"] = urllib.request.url2pathname(nomArticleCC)

    foundInfobox = False
    motCleSirenFound = False
    inInfobox = False
    levelAccolade = 0
    for line in page.splitlines():
        if not inInfobox and regExpInfoboxGroupementCommunes.search(line):
            foundInfobox = True
            inInfobox = True
        # Comptage des double accolades ouvrantes
        if inInfobox:
            levelAccolade += (line.count("{{") - line.count("}}"))

            # Recherche de mots clés
            for (motCle, champBd, regExp) in listeCleRegExp:
                m = regExp.search(line)
                if m:
                    valeurStr = m.group(champBd).strip()

                    # Correction / conversion des valeurs
                    if valeurStr:
                        if motCle == "SIREN":
                            motCleSirenFound = True
                            valeurStr = valeurStr.replace(' ', '')
                            if not valeurStr.isdigit():
                                raise ValueError("Code Siren non numérique dans page Wikipedia : " +
                                                 dictInfos1CC["nomArticleCC"] + ' : ' +
                                                 valeurStr)

                        # Enregistrement du champ dans la structure si non vide après
                        # Suppression formattages Wikipedia
                        if valeurStr:
                            valeurStr = utilitaires.removeFormatWikipedia(valeurStr)
                            if  valeurStr and not valeurStr.isspace():
                                dictInfos1CC[champBd] = valeurStr

            # Si on sort du modèle Infobox, arrêt recherche des mot-clés
            if levelAccolade <= 0:
                break

    if not foundInfobox:
        raise ValueError("Pas d'Infobox Intercommunalité de France dans article " +
                         dictInfos1CC["nomArticleCC"])
    if not motCleSirenFound:
        raise ValueError("Pas de mot clé SIREN dans l'infobox Intercommunalité de l' article " +
                         dictInfos1CC["nomArticleCC"])

    # Attribution du champ nom = nomArticleCC par défaut
    if "nom" not in dictInfos1CC:
        dictInfos1CC["nom"] = dictInfos1CC["nomArticleCC"]

    if verbose:
        print("Sortie de recupInfosPage1CCInfobox")
    return dictInfos1CC

def recupNomCCVilles(config, listeCodeCommuneNomWkp, verbose):
    """
    Récupération dans les Pages Wikipedia de chaque ville
    du nom de sa communauté de commune de rattachement.
    Entrée : listeCodeCommuneNomWkp : liste (codeCommune, nomWkpFr)
    Sortie : dict nomCCVilles {codeCommune:{"lienCC", "ancienneCommune", "nomCC"}}
    """
    if verbose:
        print("Entrée dans recupNomCCVilles")
        print("listeCodeCommuneNomWkp=", listeCodeCommuneNomWkp)

    nomCCVilles = {}
    for (codeCommune, nomWkpFr) in listeCodeCommuneNomWkp:
        # Construction du lien sur l'article Wikipedia pour cette ville
        nomArticle = urllib.request.pathname2url(nomWkpFr)

        # Lecture et analyse de la page
        try:
            page = utilitaires.getPageWikipediaFr(config, nomArticle, verbose)
            nomCCVilles[codeCommune] = recupNomCC1Ville(page, verbose)
        except (urllib.error.HTTPError, ValueError) as exc:
            print("\nPage Wikipedia :", nomWkpFr, ":", exc, file=sys.stderr)

    print()
    if verbose:
        print("Sortie de recupNomCCVilles")
    return nomCCVilles

def recupNomCC1Ville(page, verbose):
    """
    Récupération dans un article Wikipedia
    du lien et du nom de la communauté de commune de rattachement de cette ville
    retour dictInfosCC {"lienCC", "ancienneCommune", "nomCC"}
    Pour un commune ancienne, le seul champ retourné est "ancienneCommune"
    """
    if verbose:
        print("Entrée dans recupNomCC1Ville")

    # Définition des expressions régulières de selection
    dictInfosCC = {}
    inInfobox = False
    levelAccolade = 0
    for line in page.splitlines():

        if not inInfobox and regExpInfoboxAncienneCommune.search(line):
            print('A', end='', flush=True)
            dictInfosCC["ancienneCommune"] = 1
            break

        if not inInfobox and regExpInfoboxCommune.search(line):
            inInfobox = True
            dictInfosCC["ancienneCommune"] = 0

        # Comptage des double accolades ouvrantes
        if inInfobox:
            levelAccolade += (line.count("{{") - line.count("}}"))

            # Recherche dans l'infobox
            m = regExpNomCCAlias.search(line)
            if m: # si l'expression régulière s'applique à la ligne
                dictInfosCC["lienCC"] = m.group("lienCC")
                dictInfosCC["nomCC"] = m.group("nomCC")
            else:
                m = regExpNomCCDirect.search(line)
                if m:
                    dictInfosCC["lienCC"] = m.group("nomCC")
                    dictInfosCC["nomCC"] = dictInfosCC["lienCC"]
                elif regExpNomCCExemption.search(line):
                    raise ValueError("Commune hors intercommunalité")
            if m:
                break

            # Si on sort du modèle Infobox, arrêt recherche des mot-clés
            if levelAccolade <= 0:
                break

    # Problème dans la récupération dans l'infobox d'une commune
    if not dictInfosCC:
        raise ValueError("Pas d'infobox commune de France")
    if "lienCC" not in dictInfosCC and "nomCC" not in dictInfosCC \
       and "ancienneCommune" in dictInfosCC and dictInfosCC["ancienneCommune"] == 0:
        raise ValueError("Pas de champ intercom dans infobox d'une commune existante")

    if verbose:
        print("Sortie de recupNomCC1Ville")
        print("dictInfosCC=", dictInfosCC)
    return dictInfosCC

#
##################################################
#to be called as a script
if __name__ == "__main__":
    main()
    sys.exit(0)
