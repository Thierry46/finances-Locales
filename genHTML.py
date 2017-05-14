# -*- coding: utf-8 -*-
"""
*********************************************************
Module : genHTML.py
Auteur : Thierry Maillard (TMD)
Date : 15/7/2015

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

def genIndexHTML(config, numDep, listeVilleDict, verbose):
    """Génération de l'index des viles d'un département"""
    msg = "genIndexHTML : Aucune ville à traiter !"
    assert len(listeVilleDict) > 0, msg

    if verbose:
        print("Entree dans genNoticeHTML")
        print(listeVilleDict[0])

    # Lecture du modèle
    ficModelHTML = config.get('EntreesSorties', 'io.nomModeleIndexHTML')
    htmlText = litModeleHTML(ficModelHTML, verbose)

    # Remplacement des variables texte
    htmlText = replaceTags(config, htmlText, listeVilleDict[0]['nomDepStr'], verbose)

    # Insertion des lignes de tableau les villes traitées
    htmlText = insertVillesTableau(htmlText, listeVilleDict, verbose)

    # Enregistrement du fichier
    enregistreIndexHTML(config, numDep, htmlText, verbose)

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
def insertVillesTableau(htmlText, listeVilleDict, verbose):
    """ Insere les villes dans le texte passé en paramètre """
    if verbose:
        print("Entree dans InsertVillesTableau")
        print("Nombre de ville :", len(listeVilleDict))

    lignes = ""
    for ville in listeVilleDict:
        lignes += '<tr>\n'

        # Lien article Finances locales
        lignes += '<td><a href="' + ville['html'] + '" target="_blank">'
        lignes += ville['nom'] + ' (HTML)</a></td>\n'

        # Lien Wikicode
        lignes += '<td><a href="' + ville['wikicode'] +  \
                  '" target="_blank">Wiki</a></td>\n'

        # Liens CSV
        lignes += '<td><a href="' + ville['csv'] +  \
                  '_Valeur_totale.csv' + \
                  '" target="_blank">Valeur totale (CSV)</a></td>\n'
        lignes += '<td><a href="' + ville['csv'] +  \
                  '_Par_habitant.csv' + \
                  '" target="_blank">Par habitant (CSV)</a></td>\n'
        lignes += '<td><a href="' + ville['csv'] +  \
                  '_En_moyenne_pour_la_strate.csv' + \
                  '" target="_blank">strate (CSV)</a></td>\n'

        # Info score Wikipédia
        lignes += '<td>' + str(ville['Score']) + '</td>\n'
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

def enregistreIndexHTML(config, numDep, htmlText, verbose):
    """ Enregistre la notice HTML """
    if verbose:
        print("Entree dans enregistreIndexHTML")
        print("numDep =", numDep)

    # Création du répertoire de préparation des paquets
    repertoireBase = config.get('EntreesSorties', 'io.repertoireBase')
    repertoire = repertoireBase + '_' + numDep

    msg = "Le répertoire " + repertoire + " n'existe pas !"
    assert os.path.isdir(os.path.normcase(repertoire)), msg

    ficResu = config.get('EntreesSorties', 'io.nomFicIndexHTML')
    pathFileHTML = os.path.normcase(os.path.join(repertoire, ficResu))
    enregistreFicHTML(pathFileHTML, htmlText, verbose)

    if verbose:
        print("Sortie de enregistreIndexHTML")

def enregistreFicHTML(pathFileHTML, htmlText, verbose):
    """ Enregistre un fichier HTML à l'endroit spécifé """
    if verbose:
        print("Entree dans enregistreFicHTML")
        print("pathFileHTML :", pathFileHTML)

    if verbose:
        print("Ouverture de :", pathFileHTML)
    ficNotice = open(pathFileHTML, 'w')
    print("Ecriture de :", os.path.basename(pathFileHTML))
    ficNotice.write(htmlText)
    if verbose:
        print("Fermeture de :", pathFileHTML)
    ficNotice.close()

    if verbose:
        print("Sortie de enregistreFicHTML")

def copieRepertoire(repertoireSource, repertoireDest, verbose):
    """Copie d'un répertoire"""
    if verbose:
        print("Entree dans copieRepertoire")

    msg = "Le répertoire " + repertoireDest + " n'existe pas !"
    assert os.path.isdir(repertoireDest), msg
    repertoireDestTotal = os.path.normcase(os.path.join(repertoireDest, repertoireSource))
    if os.path.isdir(repertoireDestTotal):
        if verbose:
            print("effacement ancien", repertoireDestTotal)
        shutil.rmtree(repertoireDestTotal)
    shutil.copytree(repertoireSource, repertoireDestTotal)
    if verbose:
        print(repertoireSource + " copié dans", repertoireDest)
        print("Sortie de copieRepertoire")

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

def genIndexDepartement(config, verbose):
    """Genere l'index des déparetements disponibles"""

    # Récupère la liste des departements disponibles + tri
    repertoireBase = config.get('EntreesSorties', 'io.repertoireBase')
    repTransfertWeb = config.get('EntreesSorties', 'io.repTransfertWeb')
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
