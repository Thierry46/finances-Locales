#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
*********************************************************
Programme : genCode.py
Auteur : Thierry Maillard (TMD)
Date : 24/5/2015 - 3/11/2015

Role : Transforme les donnees traitées par extractionMinFi.py
        en wikicode pour enrichir les sections "Finances locale" des
        articles de Wikipedia.fr concernant les villes et les villages
        de france et en html pour un site Web.

Options :
    -h ou --help : Affiche ce message d'aide.
    -u ou --usage : Affice des exemples de ligne lancement
    -V ou --version : Affiche la version du programme
    -v ou --verbose : Rend le programme bavard (mode debug).

paramètres :
    numDep : numero du département à traiter

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
import configparser
import locale
import unicodedata

import utilitaires
import utilCode
import genCodeTexte
import genCodeTableaux
import genCodeCSV
import genCodeGraphiques
import genHTML

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
        opts, args = getopt.getopt(
            argv[1:],
            "huvV",
            ["help", "usage", "version", "verbose"]
            )
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
    isMatplotlibOk = utilitaires.checkMatplolibOK()

    if len(args) != 1:
        msg = __doc__ + "\n1 paramètre obligatoire : num_departement !"
        print(msg)
        sys.exit(1)
    numDep = args[0]

    print('Début de', nomProg)
    if verbose:
        print("\nnumDep =", numDep)

    #############
    # Génération de toutes les villes extraites par extractionWeb.py
    # Toutes les villes sont traitées car le traitement est rapide
    #############
    print("\nRecherche des fichiers a traiter deja extrait par extractionWeb.py ...")
    repertoireExtraction = config.get('EntreesSorties', 'io.repertoireExtractions')
    repertoireDepExtraction = repertoireExtraction + '_' + numDep
    repertoireBase = config.get('EntreesSorties', 'io.repertoireBase')
    repertoireDepBase = repertoireBase + '_' + numDep

    indicateurNomFicBd = config.get('EntreesSorties', 'io.indicateurNomFicBd')
    listeFichiers = []
    if os.path.isdir(repertoireDepExtraction):
        listeFichiers = [nomFic for nomFic in os.listdir(repertoireDepExtraction)
                         if indicateurNomFicBd in nomFic]

    listeVilleDict = utilCode.recupVillesFichiers(config, numDep, listeFichiers, verbose)
    msg = "Aucune ville trouvée pour générer le code dans " +\
          repertoireDepExtraction + " !"
    assert len(listeVilleDict) > 0, msg
    print(str(len(listeVilleDict)), "villes récupérées")

    # v1.3.0 : Tri des villes par ordre alphabétique.
    listeVilleDict.sort(key=lambda ville: ville['nom'])

    # Création répertoires resultat département
    if not os.path.isdir(repertoireDepBase):
        if verbose:
            print("Creation repertoire du département :", repertoireDepBase)
        os.makedirs(repertoireDepBase)

    print("\nGénération du code pour", len(listeVilleDict), "ville(s)")
    auMoins1villeGénérée = False
    for ville in listeVilleDict:
        # V2.4.0 : Conversion caractères accentués ou interdits dans un nom de fichier
        # Correction pb encoding decoding JSON pour caractères accentués,
        # Voir version.txt pour explications.
        ville['nom'] = unicodedata.normalize('NFC', ville['nom'])
        #ville['nomDisque'] = ville['nom']
        ville['nomDisque'] = utilitaires.convertLettresAccents(ville['nom'])
        print(ville['nom'], 'sur disque', ville['nomDisque'], '...')

        nomRelatifIndexVille = os.path.join(ville['nomDisque'], ville['nomDisque'])
        indicateur = config.get('GenCode', 'gen.idFicDetail')
        ville['wikicode'] = nomRelatifIndexVille + '_' +  indicateur + '.html'
        ville['html'] = nomRelatifIndexVille + '.html'
        ville['csv'] = nomRelatifIndexVille

        # V2.3.0 : on ne génère pas une ville dont le répertoire existe
        # Création du sous répertoire pour la ville
        repVille = os.path.join(repertoireDepBase, ville['nomDisque'])
        if os.path.isdir(repVille):
            print(ville['nom'], "ignoréée car le répertoire", repVille, "existe.")
        else:
            auMoins1villeGénérée = True
            if verbose:
                print("Creation répertoire de la commune :", repVille)
            os.makedirs(repVille)

            listAnnees = utilCode.getListAnnees(ville, verbose)
            for typeCode in ["wikiArticle", "HTML",
                             "CSV Valeur totale",
                             "CSV Par habitant",
                             "CSV En moyenne pour la strate"]:

                if not typeCode.startswith("CSV"):
                    textSection = genereCode1Ville(config, repVille,
                                                   ville, listAnnees,
                                                   nomProg, typeCode,
                                                   isMatplotlibOk, verbose)
                else:
                    sousCle = typeCode.replace('CSV ', '')
                    textSection = genCodeCSV.genCodeCSV1Ville(ville, listAnnees,
                                                              sousCle, verbose)

                if typeCode == "wikiArticle":
                    indicateur = config.get('GenCode', 'gen.idFicDetail')
                    extensionFic = '.txt'
                elif typeCode == "HTML":
                    indicateur = ''
                    extensionFic = '.html'
                elif typeCode.startswith("CSV"):
                    indicateur = sousCle.replace(' ', '_')
                    extensionFic = '.csv'

                # Ecriture du fichier du Wikicode et du fichier html
                # Inclusion des fichiers Wikicode dans des fichiers HTML pour
                # éviter problèmes d'encodage et travaller uniquement dans un navigateur Web.
                nomFic = utilitaires.construitNomFic(repVille, ville['nomDisque'],
                                                     indicateur, extensionFic)
                if verbose:
                    print("Ecriture du code dans :", nomFic)
                if typeCode == "HTML" or typeCode.startswith("CSV"):
                    print("Ecriture de :", nomFic)
                ficVille = open(nomFic, 'w')
                ficVille.write(textSection)
                ficVille.close()
                if typeCode == "wikiArticle":
                    genHTML.convertWikicode2Html(config, nomFic, verbose)

    # Génération de l'index des villes
    print("-------------")
    if auMoins1villeGénérée:
        genHTML.genIndexHTML(config, numDep, listeVilleDict, verbose)
        print("\nOK : Resultats dans le repertoire :", repertoireDepBase)
        print("Utilisez : genSiteWeb.py pour préparer le déploiment WEB.")
    else:
        print("Aucune commune générée !")

def genereCode1Ville(config, repVille, ville, listAnnees,
                     nomProg, typeCode,
                     isMatplotlibOk, verbose):
    """ Génère le Wikicode pour une ville """
    if verbose:
        print("Entree dans genereWikicode1Ville")
        print('ville =', ville['nom'])
        print('typeCode =', typeCode)
        print('isMatplotlibOk', isMatplotlibOk)

    nomBaseModele = config.get('Modele', 'modele.nomBaseModele')
    numVersion = config.get('Version', 'version.number')
    if typeCode == "wikiArticle":
        cle = 'gen.idFicDetail'
        isWikicode = True
    elif typeCode == "wikiSection":
        cle = 'gen.idFicSection'
        isWikicode = True
    else:
        cle = 'gen.idFicHTML'
        isWikicode = False
    typeSortie = config.get('GenCode', cle)
    modele = nomBaseModele + '_' + numVersion + '_' + typeSortie + '.txt'

    # v2.1.0 : pour cas particulier Paris : Strate = Ville -> pas de strate dans les sorties
    if ville['nom'] == 'Paris':
        isComplet = False
    else:
        isComplet = (config.get('Modele', 'modele.type') == 'complet')

    # Lecture et filtrage du fichier modèle
    textSection = utilCode.lectureFiltreModele(modele, isComplet, verbose)

    # Calcule ratio dette/CAF
    utilCode.calculeRatioDetteCAF(config, listAnnees, ville, isWikicode, verbose)

    # Modification des valeurs simples
    textSection = genCodeTexte.genCodeTexte(config, modele, textSection, ville,
                                            listAnnees, nomProg, isWikicode, verbose)
    # Génération des tableaux pictogrammes
    textSection = genCodeTableaux.genCodeTableauxPicto(config, textSection,
                                                       ville, listAnnees,
                                                       isComplet,
                                                       isWikicode, verbose)
     # Génération des tableaux
    textSection = genCodeTableaux.genCodeTableaux(config, textSection, ville,
                                                  listAnnees, isComplet,
                                                  isWikicode, verbose)

    # Generation des graphiques
    textSection = genCodeGraphiques.genCodeGraphiques(config, repVille, textSection, ville,
                                                      listAnnees, isComplet,
                                                      isWikicode, isMatplotlibOk,
                                                      verbose)

    if verbose:
        print("Sortie de genereCode1Ville")

    return textSection

##################################################
#to be called as a script
if __name__ == "__main__":
    # Contournement OS X invalide locale
    if platform.system() == 'Darwin':
        locale.setlocale(locale.LC_ALL, os.getenv('LANG'))
    main()
    sys.exit(0)

