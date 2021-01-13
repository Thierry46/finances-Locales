# -*- coding: utf-8 -*-
"""
*********************************************************
Module : genHTML.py
Auteur : Thierry Maillard (TMD)
Date : 15/7/2015 - 2/7/2020

Role : Routines de génération du code HTML de déploiement.
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
import os
import os.path
import time

import utilitaires

def genIndexHTML(config, repertoireDepBase, listVilles, verbose):
    """
    Génération de l'index des viles d'un département
    listVilles : liste des villes traitées
        Format d'une ville :
        [codeCommune, nom, nomWkpFr, article, nomDepartement,
         typeGroupement, nomStrate, score, population, numDepartement]
    """
    assert len(listVilles) > 0, "genIndexHTML : Aucune ville à traiter !"

    if verbose:
        print("Entree dans genIndexHTML")
        print("repertoireDepBase=", repertoireDepBase)
        print("listVilles =", listVilles)

    # Lecture du modèle
    ficModelHTML = config.get('EntreesSorties', 'io.nomModeleIndexHTML')
    htmlText = litModeleHTML(ficModelHTML, verbose)

    # Remplacement des variables texte
    nomDepStr = listVilles[0][3]
    if not listVilles[0][3].endswith("'"):
        nomDepStr += ' '
    nomDepStr += listVilles[0][4]
    htmlText = replaceTags(config, htmlText, nomDepStr, verbose)

    # Insertion des lignes de tableau les villes traitées
    htmlText = insertVillesTableau(config, htmlText, listVilles, verbose)

    # Enregistrement du fichier
    enregistreIndexHTML(config, repertoireDepBase,
                        listVilles[0][9], htmlText, verbose)

    if verbose:
        print("Sortie de genIndexHTML")

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
def insertVillesTableau(config, htmlText, listVilles, verbose):
    """
    Insere les villes dans le texte passé en paramètre
    listVilles : liste des villes traitées
        Format d'une ville :
        [codeCommune, nom, nomWkpFr, article, nomDepartement,
         typeGroupement, nomStrate, score, population]

    """
    if verbose:
        print("Entree dans InsertVillesTableau")
        print("Nombre de ville :", len(listVilles))

    lignes = ""
    for ville in listVilles:
        dictNomsVille = utilitaires.getNomsVille(config, ville[1],
                                                 "", verbose)
        lignes += '<tr>\n'

        # Lien article Finances locales
        lignes += '<td><a href="' + dictNomsVille['villeHtml'] + \
                  '" target="_blank">'
        lignes += ville[1] + ' (HTML)</a></td>\n'

        # Lien Wikicode
        lignes += '<td><a href="' + dictNomsVille['villeWikicode'] +  \
                  '" target="_blank">Wiki</a></td>\n'

        # Info score Wikipédia
        lignes += '<td>' + str(ville[7]) + '</td>\n'
        lignes += '<td>' + ville[8] + '</td>\n'
        lignes += '</tr>\n'

    htmlText = htmlText.replace("++LIGNES_VILLES++", lignes)

    if verbose:
        print("lignes :", lignes)
        print("Sortie de InsertVillesTableau")
    return htmlText

def enregistreIndexHTML(config, repertoireDepBase, numDep,
                        htmlText, verbose):
    """ Enregistre la notice HTML """
    if verbose:
        print("Entree dans enregistreIndexHTML")
        print("repertoireDepBase =", repertoireDepBase)
        print("numDep =", numDep)

    # Le répertoire qui accueillera les fichiers du département doit exister
    repertoire = repertoireDepBase
    assert os.path.isdir(os.path.normcase(repertoire)),\
           "Le répertoire " + repertoire + " n'existe pas !"

    nomFicIndexHTML = config.get('EntreesSorties', 'io.nomFicIndexHTML')
    pathFileHTML = os.path.normcase(os.path.join(repertoire, nomFicIndexHTML))
    enregistreFicHTML(pathFileHTML, htmlText, verbose)

    if verbose:
        print("Fichier index écrit dans : ", pathFileHTML)
        print("Sortie de enregistreIndexHTML")

def enregistreFicHTML(pathFileHTML, htmlText, verbose):
    """ Enregistre un fichier HTML à l'endroit spécifé """
    if verbose:
        print("Entree dans enregistreFicHTML")
        print("pathFileHTML :", pathFileHTML)

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

def convertWikicode2Html(config, pathVille, verbose):
    """Conversion d'un fichier wikicode en HTML"""
    if verbose:
        print("Entree dans convertWikicode2Html")
        print("pathVille =", pathVille)

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

    # Sauvegarde du html et suppresion fichier texte
    pathFicResu = pathVille.replace('.txt', '.html')
    if verbose:
        print("Ecriture de :", pathFicResu)
    enregistreFicHTML(pathFicResu, htmlText, verbose)
    os.remove(pathVille)
    if verbose:
        print("Sortie de convertWikicode2Html")

def genIndexDepartement(config, repTransfertWeb, verbose):
    """
    Genere l'index des départements disponibles
    repTransfertWeb : repertoire où écrire les résultats
    """

    # Récupère la liste des departements disponibles + tri
    repertoireBase = config.get('EntreesSorties', 'io.repertoireBase')
    assert os.path.isdir(repTransfertWeb)
    listeDept = [dept for dept in os.listdir(repTransfertWeb)
                 if os.path.isdir(os.path.join(repTransfertWeb, dept)) and
                 dept.startswith(repertoireBase + '_')]
    listeDept.sort()
    assert len(listeDept) > 0

    # Lecture modèle de la Notice de Deploiement
    ficModelHTML = config.get('EntreesSorties', 'io.nomModeleNoticeDeploiement')
    if verbose:
        print("Lecture du modèle dans :", ficModelHTML)
    htmlText = litModeleHTML(ficModelHTML, verbose)

    # Remplacement des tags
    htmlText = htmlText.replace("++OUTIL_NOM++",
                                config.get('Version', 'version.appName'))
    version = config.get('Version', 'version.number') + " : " + \
              config.get('Version', 'version.nom')
    htmlText = htmlText.replace("++VERSION++", version)
    htmlText = htmlText.replace("++URL_BASE++",
                                '<a href="' + \
                                config.get('GenCode', 'gen.siteAlize2') + \
                                '" target="_blank">Alize2</a>')
    htmlText = htmlText.replace("++DATE++", time.strftime("%d %B %G - %H:%M:%S"))

    # Construction des lignes de departements du tableau
    lignesDept = ""
    for dept in listeDept:
        lignesDept += '<tr>\n'

        # Numéro et lien département
        lignesDept += '<td><a href="' + dept + '/index.html" target="_blank">' + \
                         dept.replace(repertoireBase + '_', '') + \
                         '</a></td>\n'

        # Récupération de la date de modification du paquet
        timeSecEpoch = os.path.getmtime(os.path.join(repTransfertWeb, dept))
        tDeniereModif = time.strftime("%d %B %G - %H:%M:%S", time.localtime(timeSecEpoch))
        lignesDept += '<td>' + tDeniereModif + '</td>\n'

        lignesDept += '</tr>\n'
    htmlText = htmlText.replace("++LIGNES_DEPARTEMENTS++", lignesDept)

    # Sauvegarde
    nomNoticeDeploiement = config.get('EntreesSorties', 'io.nomNoticeDeploiement')
    pathFicResu = os.path.join(repTransfertWeb, nomNoticeDeploiement)
    if verbose:
        print("Ecriture de :", pathFicResu)
    enregistreFicHTML(pathFicResu, htmlText, verbose)

def genIndexGroupementHTML(config, repertoireGroupements,
                           listGroupements, verbose):
    """
    Génération de l'index des viles d'un département
    repertoireGroupements : path du répertoire dans lequel sera produit l'index
    listGroupements : liste des groupements de communes traités traitées
        Format d'un enregistrement :
        [sirenGroupement, nomArticleCC, nom,
                            région, département, forme, siège,
                            logo, siteWeb]
    """
    assert listGroupements, "genIndexGroupementHTML : Aucune ville à traiter !"

    if verbose:
        print("Entree dans genIndexGroupementHTML")
        print("repertoireGroupements=", repertoireGroupements)
        print("listGroupements =", listGroupements)

    # Lecture du modèle
    ficModelHTML = config.get('EntreesSorties', 'io.nomModeleIndexGroupementHTML')
    htmlText = litModeleHTML(ficModelHTML, verbose)

    # Remplacement des variables texte
    htmlText = replaceTags(config, htmlText, "", verbose)

    # Insertion des lignes de tableau les Groupements traitées
    htmlText = insertGroupementTableau(htmlText, listGroupements, verbose)

    # Enregistrement du fichier
    nomFicIndexHTML = config.get('EntreesSorties', 'io.nomFicGroupementHTML')
    pathFileHTML = os.path.normcase(os.path.join(repertoireGroupements, nomFicIndexHTML))
    enregistreFicHTML(pathFileHTML, htmlText, verbose)

    if verbose:
        print("Sortie de genIndexGroupementHTML")

def insertGroupementTableau(htmlText, listGroupements, verbose):
    """
    Insere les groupements de communes dans le texte passé en paramètre
    listGroupements : liste des groupements de communes traités traitées
        Format d'un enregistrement :
        [sirenGroupement, nomArticleCC, nom,
                            région, département, forme, siège,
                            logo, siteWeb]
    """
    if verbose:
        print("Entree dans insertGroupementTableau")
        print("Nombre de groupents de communes :", len(listGroupements))
        if listGroupements:
            print(listGroupements[0])

    lignes = ""
    for groupement in listGroupements:
        dictNomsGroupement = utilitaires.getNomsGroupement(groupement[2],
                                                           "",
                                                           verbose)
        lignes += '<tr>\n'

        # Lien article Finances locales
        nomFic = utilitaires.construitNomFic(dictNomsGroupement['repGroupement'],
                                             dictNomsGroupement['groupementNomDisque'],
                                             "HTML", '.html')
        lignes += '<td><a href="' + nomFic +  '" target="_blank">'
        lignes += groupement[1] + ' (HTML)</a></td>\n'

        # Lien Wikicode
        nomFic = utilitaires.construitNomFic(dictNomsGroupement['repGroupement'],
                                             dictNomsGroupement['groupementNomDisque'],
                                             "wikicode", '.txt')
        lignes += '<td><a href="' + nomFic + '" target="_blank">Wiki</a></td>\n'

        # Info score Wikipédia
        lignes += '<td>' + groupement[3] + '</td>\n'
        lignes += '<td>' + groupement[4] + '</td>\n'
        lignes += '<td>' + groupement[0] + '</td>\n'
        lignes += '</tr>\n'

    htmlText = htmlText.replace("++LIGNES_GROUPEMENTS++", lignes)

    if verbose:
        print("lignes :", lignes)
        print("Sortie de insertGroupementTableau")
    return htmlText
