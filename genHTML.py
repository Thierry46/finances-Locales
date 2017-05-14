# -*- coding: utf-8 -*-
"""
*********************************************************
Module : genHTML.py
Auteur : Thierry Maillard (TMD)
Date : 14/7/2015

Role : Routines de génération du code HTML de déploiement.
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
import os
import os.path
import shutil
import time
import re

def genNoticeHTML(config, numDep, listeVilleDict, verbose):
    """Génération de la notice de déploiement et de ses fichiers auxiliaires"""
    msg = "genHTML : Aucune ville à traiter !"
    assert len(listeVilleDict) > 0, msg

    if verbose:
        print("Entree dans genHTML")
        print(listeVilleDict[0])

    # Lecture du modèle
    ficModelHTML = config.get('EntreesSorties', 'io.nomModeleNoticeHTML')
    htmlText = litModeleHTML(ficModelHTML, verbose)

    # Remplacement des variables texte
    htmlText = replaceTags(config, htmlText, listeVilleDict[0]['nomDepStr'], verbose)

    # Insertion des lignes de tableau pour les villes prioritaires
    htmlText = insertVillesTableau(config, htmlText, listeVilleDict, verbose)

    # Enregistrement du fichier
    enregistreNoticeHTML(config, numDep, htmlText, verbose)

    # Copie des fichiers auxiliaires
    repertoireBase = config.get('EntreesSorties', 'io.repertoireBase')
    repertoireDest = os.path.normcase(repertoireBase + '_' + numDep)
    copieFicAux(config, repertoireDest, verbose)

    if verbose:
        print("Sortie de genHTML")

def litModeleHTML(ficModelHTML, verbose):
    """Lecture du fichier modèle HTML"""
    if verbose:
        print("Entree dans litModeleHTML")

    hFic = open(ficModelHTML, 'r')
    htmlText = hFic.read()

    if verbose:
        print(len(htmlText), "caractères lus dans", ficModelHTML)
        print("Sortie de litModeleHTML")
    return htmlText

def replaceTags(config, htmlText, nomDepStr, verbose):
    """ Remplace les tags ++XXXX++ dans le texte passé en paramètre """
    if verbose:
        print("Entree dans replaceTags")
        print("nomDepStr :", nomDepStr)

    htmlText = htmlText.replace("++NOM_DEP_STR++", nomDepStr)
    version = config.get('Version', 'version.number') + " (" + \
                config.get('Version', 'version.nom') + ")"
    htmlText = htmlText.replace("++VERSION++", version)
    versionDate = config.get('Version', 'version.date')
    htmlText = htmlText.replace("++VERSION_DATE++", versionDate)
    htmlText = htmlText.replace("++DATE++", time.strftime("%d %B %G"))

    if verbose:
        print("Sortie de replaceTags")
    return htmlText

# V1.0.5 : Pas de selection de ville ici :
#           c'est lors de l'extraction de la base du MinFi que se fait la sélectio
def insertVillesTableau(config, htmlText, listeVilleDict, verbose):
    """ Insere les villes dans le texte passé en paramètre """
    if verbose:
        print("Entree dans InsertVillesTableau")
        print("Nombre de ville :", len(listeVilleDict))

    baseURLWikipedia = config.get('Extraction', 'extraction.wikipediafrBaseUrl')

    lignes = ""
    for ville in listeVilleDict:
        lignes += '<tr>\n'
        lignes += '<td>' + str(ville['Score']) + '</td>\n'

        # Lien article Wikipédia
        lignes += '<td><a href="' + baseURLWikipedia + ville['lien'] + '" target="_blank">'
        lignes += ville['nom'] + '</a></td>\n'

        # Lien section Wikicode
        articleSection = ville['nom'] + '_section.html'
        lignes += '<td><a href="' + articleSection + '" target="_blank">'
        lignes += articleSection + '</a></td>\n'

        # Lien article Wikicode
        articleDetail = ville['nom'] + '_detail.html'
        lignes += '<td><a href="' + articleDetail + '" target="_blank">'
        lignes += articleDetail + ' </a></td>\n'

        lignes += '<td>' + ville['avancement'] + '</td>\n'
        lignes += '<td>' + ville['importanceCDF'] + '</td>\n'
        lignes += '<td>' + ville['importanceVDM'] + '</td>\n'
        lignes += '<td>' + ville['popularite'] + '</td>\n'
        lignes += '</tr>\n'

    htmlText = htmlText.replace("++LIGNES_VILLES++", lignes)

    if verbose:
        print("lignes :", lignes)
        print("Sortie de InsertVillesTableau")
    return htmlText

def enregistreNoticeHTML(config, numDep, htmlText, verbose):
    """ Enregistre la notice HTML """
    if verbose:
        print("Entree dans enregistreNoticeHTML")

    # Création du répertoire de préparation des paquets
    repertoireBase = config.get('EntreesSorties', 'io.repertoireBase')
    repertoire = repertoireBase + '_' + numDep

    msg = "Le répertoire " + repertoire + " n'existe pas !"
    assert os.path.isdir(os.path.normcase(repertoire)), msg

    ficResu = config.get('EntreesSorties', 'io.nomFicNoticeHTML')
    pathFileHTML = os.path.normcase(os.path.join(repertoire, ficResu))
    enregistreFicHTML(pathFileHTML, htmlText, verbose)

    if verbose:
        print("Sortie de enregistreNoticeHTML")

def enregistreFicHTML(pathFileHTML, htmlText, verbose):
    """ Enregistre un fichier HTML à l'endroit spécifé """
    if verbose:
        print("Entree dans enregistreFicHTML")

    if verbose:
        print("Ouverture de :", pathFileHTML)
    ficNotice = open(pathFileHTML, 'w')
    print("Ecriture de :", pathFileHTML)
    ficNotice.write(htmlText)
    if verbose:
        print("Fermeture de :", pathFileHTML)
    ficNotice.close()

    if verbose:
        print("Sortie de enregistreFicHTML")

def copieFicAux(config, repertoireDest, verbose):
    """Copie des fichiers auxiliaires"""
    if verbose:
        print("Entree dans copieFicAux")

    msg = "Le répertoire " + repertoireDest + " n'existe pas !"
    assert os.path.isdir(repertoireDest), msg
    repertoireSource = config.get('EntreesSorties', 'io.RepSrcFicAux')
    repertoireDestTotal = os.path.normcase(os.path.join(repertoireDest, repertoireSource))
    if os.path.isdir(repertoireDestTotal):
        if verbose:
            print("effacement ancien", repertoireDestTotal)
        shutil.rmtree(repertoireDestTotal)
    shutil.copytree(repertoireSource, repertoireDestTotal)
    if verbose:
        print(repertoireSource + " copié dans", repertoireDest)
        print("Sortie de copieFicAux")

def convertWikicode2Html(config, pathVille, verbose):
    """Conversion d'un fichier wikicode en HTML"""
    if verbose:
        print("Entree dans convertWikicode2Html")
        print("pathVille =", pathVille)

    repertoirewikicode = config.get('EntreesSorties', 'io.repertoirewikicode')
    repertoireBase = config.get('EntreesSorties', 'io.repertoireBase')

    # Lecture du wikicode produit en utf8
    if verbose:
        print("Lecture du wikicode dans :", pathVille)
    hFic = open(pathVille, 'r')
    wikicode = hFic.read()
    wikicode = wikicode.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    # Lecture du modèle
    ficModelHTML = config.get('EntreesSorties', 'io.nomModeleCodeHTML')
    if verbose:
        print("Lecture du modèle dans :", ficModelHTML)
    htmlText = litModeleHTML(ficModelHTML, verbose)

    # Insertion dans le modèle HTML du wikicode
    titrePage = ("Pour " +
                 os.path.basename(pathVille).replace('.txt', '').replace('_', ' '))
    htmlText = htmlText.replace("++TITRE++", titrePage)
    htmlText = htmlText.replace("++CODE++", wikicode)

    # Sauvegarde
    pathFicResu = pathVille.replace('.txt', '.html')
    pathFicResu = pathFicResu.replace(repertoirewikicode, repertoireBase)
    if verbose:
        print("Ecriture de :", pathFicResu)
    enregistreFicHTML(pathFicResu, htmlText, verbose)

    if verbose:
        print("Sortie de convertWikicode2Html")

def genNoticeDeploiement(config, verbose):
    """Genere la notice de déploiement selon les paquets disponibles"""

    # Expresion régulière de sélection du numéro de département
    selectNumDep = config.get('EntreesSorties', 'io.repertoireBase') + '_' + \
                   r'(?P<NumDep>\d?[0-9AB]\d)\.zip'

    # Récupère la liste des paquets disponibles et la trie par département
    repTransfertWeb = config.get('EntreesSorties', 'io.repTransfertWeb')
    assert os.path.isdir(repTransfertWeb)
    srepPaquets = config.get('EntreesSorties', 'io.srepPaquets')
    repPaquets = os.path.join(repTransfertWeb, srepPaquets)
    regexpNumDep = re.compile(selectNumDep)
    listePaquets = [pathPaquet for pathPaquet in os.listdir(repPaquets)
                    if os.path.isfile(os.path.join(repPaquets, pathPaquet)) and
                    regexpNumDep.search(pathPaquet) is not None]
    listePaquets.sort()
    assert len(listePaquets) > 0

    # Lecture modèle de la Notice de Deploiement
    ficModelHTML = config.get('EntreesSorties', 'io.nomModeleNoticeDeploiement')
    if verbose:
        print("Lecture du modèle dans :", ficModelHTML)
    htmlText = litModeleHTML(ficModelHTML, verbose)

    # Remplacement des tags
    htmlText = htmlText.replace("++OUTIL_NOM++", config.get('Version', 'version.appName'))
    version = config.get('Version', 'version.number') + " : " + \
              config.get('Version', 'version.nom')
    htmlText = htmlText.replace("++VERSION++", version)
    htmlText = htmlText.replace("++DATE++", time.strftime("%d %B %G - %H:%M:%S"))

    # Construction des lignes de paquet du tableau
    lignesPaquets = ""
    for pathPaquet in listePaquets:
        lignesPaquets += '<tr>\n'

        # Numéro du département
        m = regexpNumDep.search(pathPaquet)
        msg = "Problème nom de paquet " + pathPaquet
        assert m, msg
        lignesPaquets += '<td>' + m.group('NumDep') + '</td>\n'

        # Lien zip
        lignesPaquets += '<td><a href="' + os.path.join(srepPaquets, pathPaquet) + '">'
        lignesPaquets += pathPaquet + '</a></td>\n'

        # Récupération de la date de modification du paquet
        timeSecEpoch = os.path.getmtime(os.path.join(repPaquets, pathPaquet))
        tDeniereModif = time.strftime("%d %B %G - %H:%M:%S", time.localtime(timeSecEpoch))
        lignesPaquets += '<td>' + tDeniereModif + '</td>\n'

        lignesPaquets += '</tr>\n'
    htmlText = htmlText.replace("++LIGNES_PAQUETS++", lignesPaquets)

    # Sauvegarde
    nomNoticeDeploiement = config.get('EntreesSorties', 'io.nomNoticeDeploiement')
    pathFicResu = os.path.join(repTransfertWeb, nomNoticeDeploiement)
    if verbose:
        print("Ecriture de :", pathFicResu)
    enregistreFicHTML(pathFicResu, htmlText, verbose)
