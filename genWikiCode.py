#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
*********************************************************
Programme : genWikiCode.py
Auteur : Thierry Maillard (TMD)
Date : 24/5/2015 - 22/7/2015

Role : Transforme les donnees traitées par extractionMinFi.py
        en wikicode pour enrichir les sections "Finances locale" des
        articles de Wikipedia.fr concernant les villes et les villages
        de france.

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
import time
import platform
import json # To write ville dictionary in files
import configparser
import locale

import utilitaires
import genWikiCodeTexte
import genWikiCodeTableaux
import genWikiCodeGraphiques
import genHTML

##################################################
# main function
##################################################
def main(argv=None):
    """ Génère le Wikicode pour les villes d'un département """
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

    utilitaires.checkPythonVersion(verbose)

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
    repertoireWikicode = config.get('EntreesSorties', 'io.repertoirewikicode')
    repertoireDepWikicode = repertoireWikicode + '_' + numDep
    repertoireBase = config.get('EntreesSorties', 'io.repertoireBase')
    repertoireDepBase = repertoireBase + '_' + numDep

    indicateurNomFicBd = config.get('EntreesSorties', 'io.indicateurNomFicBd')
    listeFichiers = []
    if os.path.isdir(repertoireDepExtraction):
        listeFichiers = [nomFic for nomFic in os.listdir(repertoireDepExtraction)
                         if indicateurNomFicBd in nomFic]

    listeVilleDict = recupVillesFichiers(config, numDep, listeFichiers, verbose)
    msg = "Aucune ville trouvée pour générer le Wikicode dans " +\
          repertoireDepExtraction + " !"
    assert len(listeVilleDict) > 0, msg

    # v1.0.4 : Traitement prioritaire des villes importantes : Score élevé -> Tri.
    listeVilleDict.sort(key=lambda ville: ville['Score'], reverse=True)

    msg = "\nGénération du Wikicode pour " + str(len(listeVilleDict)) + " ville(s)"
    print(msg)
    for ville in listeVilleDict:
        print(ville['nom'], '...')

        listAnnees = getListAnnees(ville, verbose)
        for isDetail in [True, False]:
            textSection = genereWikicode1Ville(config, ville, listAnnees,
                                               nomProg, isDetail, verbose)

            # Création des répertoires
            if not os.path.isdir(repertoireDepWikicode):
                if verbose:
                    print("Creation repertoire de wikicode :", repertoireDepWikicode)
                os.mkdir(repertoireDepWikicode)
            if not os.path.isdir(repertoireDepBase):
                if verbose:
                    print("Creation repertoire html :", repertoireDepBase)
                os.makedirs(repertoireDepBase)

            if isDetail:
                indicateur = config.get('GenWIkiCode', 'gen.idFicSection')
            else:
                indicateur = config.get('GenWIkiCode', 'gen.idFicDetail')

            # Ecriture du fichier du Wikicode et du fichier html
            # Inclusion des fichiers Wikicode dans des fichiers HTML pour
            # éviter problèmes d'encodage et travaller uniquement dans un navigateur Web.
            nomFic = utilitaires.construitNomFic(repertoireDepWikicode, ville['nom'], indicateur)
            if verbose:
                print("Ecriture du wikicode dans :", nomFic)
            ficVille = open(nomFic, 'w')
            ficVille.write(textSection)
            ficVille.close()
            genHTML.convertWikicode2Html(config, nomFic, verbose)

    # Génération de la notice de déploiement
    print("-------------")
    genHTML.genNoticeHTML(config, numDep, listeVilleDict, verbose)

    msg = "\nOK : Resultats dans les repertoires : \n\t" + \
          repertoireDepWikicode + "\n\t" + repertoireDepBase + "\n" + \
          "Utilisez : genPaquets.py pour préparer le déploiment WEB"
    print(msg)

def getListAnnees(ville, verbose):
    """Détermination des annees pour cette ville"""
    if verbose:
        print("Entree dans getListAnnees")
        print("ville['nom'] =", ville['nom'])

    anneeCourante = int(time.strftime("%Y"))
    setAnnees = {int(annee) for cle in list(ville['data'].keys())
                 for annee in list(ville['data'][cle].keys())}
    listAnnees = sorted(list(setAnnees), reverse=True)
    msg = "anneeMax dans le futur " + str(listAnnees[0]) + '>=' + str(anneeCourante)
    assert listAnnees[0] < anneeCourante, msg
    msg = "anneeMin trop petite inférieur à 2013 : " + str(listAnnees[0])
    assert listAnnees[0] >= 2013, msg

    if verbose:
        print("listAnnees = ", listAnnees)
        print("Sortie de getListAnnees")

    return listAnnees

def recupVillesFichiers(config, numDep, listeFichiers, verbose):
    """ Lit les données des villes extraites """
    if verbose:
        print("Entree dans recupVillesFichier")
        print("listeFichiers", len(listeFichiers), "elements")
        for nomFic in listeFichiers:
            print(nomFic)

    repertoireWikicode = config.get('EntreesSorties', 'io.repertoireExtractions')
    repertoire = repertoireWikicode + '_' + numDep

    msg = "Récupération de " + str(len(listeFichiers)) + " ville(s)..."
    print(msg)
    listeVilleDict = []
    for fichier in listeFichiers:
        nomFic = os.path.normcase(os.path.join(repertoire, fichier))
        hFic = open(nomFic, 'r')
        ville = json.load(hFic)
        hFic.close()
        listeVilleDict.append(ville)

    msg = "Mauvaise lecture !"
    assert len(listeVilleDict) == len(listeFichiers), msg

    msg = str(len(listeVilleDict)) + " ville(s) récupérée(s)"
    print(msg)
    if verbose:
        print("Sortie de recupVillesFichiers")
    return listeVilleDict

def genereWikicode1Ville(config, ville, listAnnees,
                         nomProg, isDetail, verbose):
    """ Génère le Wikicode pour une ville """
    if verbose:
        print("Entree dans genereWikicode1Ville")
        print('ville=', ville['nom'])

    nomBaseModele = config.get('Modele', 'modele.nomBaseModele')
    numVersion = config.get('Version', 'version.number')
    if isDetail:
        typeSortie = config.get('GenWIkiCode', 'gen.idFicSection')
    else:
        typeSortie = config.get('GenWIkiCode', 'gen.idFicDetail')
    modele = nomBaseModele + '_' + numVersion + '_' + typeSortie + '.txt'

    isComplet = (config.get('Modele', 'modele.type') == 'complet')

    # Lecture et filtrage du fichier modèle
    textSection = lectureFiltreModele(modele, isComplet, verbose)

    # Calcule ratio dette/CAF
    dictCAF = dict()
    dictDette = dict()
    for annee in listAnnees:
        dictCAF[str(annee)] = utilitaires.getValeurIntTotale(ville,
                                                             "Capacité d'autofinancement = CAF",
                                                             annee)
        dictDette[str(annee)] = utilitaires.getValeurIntTotale(ville,
                                                               'Encours de la dette au 31/12/N',
                                                               annee)
    ratioCAFDette, tendanceRatio = tendanceRatioDetteCAF(config, dictCAF, dictDette, verbose)
    ville['data']['ratioCAFDette'] = ratioCAFDette
    ville['data']['tendanceRatio'] = tendanceRatio

    # Modification des valeurs simples
    textSection = genWikiCodeTexte.genWikiCodeTexte(config, modele, textSection, ville,
                                                    listAnnees, nomProg, verbose)

    # Génération des tableaux pictogrammes
    textSection = genWikiCodeTableaux.genWikiCodeTableauxPicto(config, textSection, ville,
                                                               listAnnees,
                                                               isComplet, verbose)

     # Génération des tableaux
    textSection = genWikiCodeTableaux.genWikiCodeTableaux(config, textSection, ville,
                                                          listAnnees, isComplet, verbose)

    # Generation des graphiques
    textSection = genWikiCodeGraphiques.genWikiCodeGraphiques(config, textSection, ville,
                                                              listAnnees, isComplet, verbose)
    if verbose:
        print("Sortie de genereWikicode1Ville")

    return textSection

def lectureFiltreModele(modele, isComplet, verbose):
    """ Lecture du fichier modèle
        et adaptation du modèle en fonction du type de sortie souhaitée """

    if verbose:
        print("Entree dans lectureFiltreModele")
        print("modele =", modele)
        print("isComplet =", str(isComplet))

    modelefile = open(modele, 'r')
    textSection = ""
    ecrit = True
    for ligne in modelefile.read().splitlines():
        if ligne.startswith("<STOP_COMPLET>"):
            ecrit = True
        elif ligne.startswith("<COMPLET>"):
            ecrit = False
        elif isComplet or ecrit:
            textSection += ligne + '\n'
    modelefile.close()

    if verbose:
        print("Sortie de lectureFiltreModele")

    return textSection

def tendanceRatioDetteCAF(config, dictCAF, dictDette, verbose):
    """ Retourne une chaine de caractère qui qualifie le ratio Dette/CAF """

    if verbose:
        print("\nEntree dans calculeRatioDetteCAF")

    msg = "tendanceRatioDetteCAF : CAF vide !"
    assert len(dictCAF) > 0, msg
    msg = "tendanceRatioDetteCAF : CAF dictCAF et dictDette sont de taille différentes!"
    assert len(dictCAF) == len(dictDette), msg

    seuilEcreteRatio = int(config.get('GenWIkiCode', 'gen.seuilEcreteRatio'))
    seuilBigRatio = int(config.get('GenWIkiCode', 'gen.seuilBigRatio'))
    seuilLowRatio = int(config.get('GenWIkiCode', 'gen.seuilLowRatio'))

    if verbose:
        print("seuilEcreteRatio =", seuilEcreteRatio)
        print("seuilBigRatio=", seuilBigRatio)
        print("seuilLowRatio=", seuilLowRatio)
        print("dictCAF=", dictCAF)
        print("dictDette=", dictDette)

    strTendance = ""
    listeAnneesStr = sorted(list(dictCAF.keys()), reverse=True)
    if verbose:
        print("listeAnneesStr=", listeAnneesStr)
    dicoRatio = dict()
    for annee in listeAnneesStr:
        caf = dictCAF[annee]
        dette = dictDette[annee]
        if float(caf) < 0.5:
            ratio = seuilEcreteRatio
        else:
            ratio = int(float(dette) / float(caf))
            if ratio > seuilEcreteRatio:
                ratio = seuilEcreteRatio
        dicoRatio[str(annee)] = ratio

     # Determine l'annee du max et du min
    minAnneeR = maxAnneeR = listeAnneesStr[0]
    for annee in listeAnneesStr:
        if dicoRatio[annee] > dicoRatio[maxAnneeR]:
            maxAnneeR = annee
        if dicoRatio[annee] < dicoRatio[minAnneeR]:
            minAnneeR = annee

    if verbose:
        print("minAnneeR=", minAnneeR, ", dicoRatio[minAnneeR] =", dicoRatio[minAnneeR])
        print("maxAnneeR=", maxAnneeR, ", dicoRatio[maxAnneeR] =", dicoRatio[maxAnneeR])

    # Construit la phrase de tendance
    strTendance = "Sur une période de {{nobr|" + str(len(listeAnneesStr)) + \
                  " années}}, ce ratio "
    if abs(dicoRatio[maxAnneeR] - dicoRatio[minAnneeR]) < 5:
        moyMinMaxRatio = (dicoRatio[maxAnneeR] + dicoRatio[minAnneeR]) / 2
        if verbose:
            print("moyMinMaxRatio=", moyMinMaxRatio)
        if moyMinMaxRatio > seuilBigRatio:
            strTendance += "est constant et élevé (supérieur à {{nobr|" + \
                           str(seuilBigRatio) + "}} ans)"
        elif moyMinMaxRatio < seuilLowRatio:
            strTendance += "est constant et faible (inférieur à {{nobr|" + \
                           str(seuilLowRatio) + "}} ans)"
        else:
            strTendance += "est constant (autour de {{nobr|" + str(moyMinMaxRatio) + \
                           "}} ans)"
    else:
        strTendance += "présente un minimum"
        if minAnneeR != listeAnneesStr[0]:
            strTendance += " " + \
                           utilitaires.presentRatioDettesCAF(config,
                                                             dicoRatio[minAnneeR],
                                                             verbose)
        strTendance += (" en " + str(minAnneeR) + " et un maximum")
        if maxAnneeR != listeAnneesStr[0]:
            strTendance += " " + \
                           utilitaires.presentRatioDettesCAF(config,
                                                             dicoRatio[maxAnneeR],
                                                             verbose)
        strTendance += (" en " + str(maxAnneeR) + ".")

    if verbose:
        print("dicoRatio=", dicoRatio)
        print("strTendance=", strTendance)
        print("Sortie de calculeRatioDetteCAF")
    return dicoRatio, strTendance

##################################################
#to be called as a script
if __name__ == "__main__":
    # Contournement OS X invalide locale
    if platform.system() == 'Darwin':
        locale.setlocale(locale.LC_ALL, os.getenv('LANG'))
    main()
    sys.exit(0)

