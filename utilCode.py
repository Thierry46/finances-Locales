#! /usr/bin/env python
# coding: utf8
"""
*********************************************************
Programme : utilCode.py
Auteur : Thierry Maillard (TMD)
Date : 5/9/2015 - 22/10/2015
Role : Fonctions communes utiles pour la génération du code
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
import time
import datetime
import os
import os.path
import json

import utilitaires

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

    listeVilleDict = []
    for fichier in listeFichiers:
        nomFic = os.path.normcase(os.path.join(repertoire, fichier))
        hFic = open(nomFic, 'r')
        ville = json.load(hFic)
        hFic.close()
        # v2.1.0 : recup date création des fichiers d'extraction
        dateExtractionSeconds = datetime.datetime.fromtimestamp(os.path.getmtime(nomFic))
        ville['dateExtraction'] = dateExtractionSeconds.strftime("%d %B %G")
        listeVilleDict.append(ville)

    assert len(listeVilleDict) == len(listeFichiers), "Mauvaise lecture !"

    if verbose:
        print("Sortie de recupVillesFichiers")
    return listeVilleDict

def lectureFiltreModele(modele, isComplet, verbose):
    """ Lecture du fichier modèle
        et adaptation du modèle en fonction du type de sortie souhaitée """

    if verbose:
        print("Entree dans lectureFiltreModele")
        print("modele =", modele)
        print("isComplet =", str(isComplet))

    modelefile = open(modele, 'r')
    htmlPage = ""
    ecrit = True
    for ligne in modelefile.read().splitlines():
        if ligne.startswith("<STOP_COMPLET>"):
            ecrit = True
        elif ligne.startswith("<COMPLET>"):
            ecrit = False
        elif isComplet or ecrit:
            htmlPage += ligne + '\n'
    modelefile.close()

    if verbose:
        print("Sortie de lectureFiltreModele")

    return htmlPage

def calculeRatioDetteCAF(config, listAnnees, ville, isWikicode, verbose):
    """ Calcule ratio dette/CAF et enregistrement dans structure ville """

    if verbose:
        print("Entree dans calculeRatioDetteCAF")
        print("listAnnees =", listAnnees)
        print("ville =", ville['nom'])

    dictCAF = dict()
    dictDette = dict()
    for annee in listAnnees:
        dictCAF[str(annee)] = utilitaires.getValeurIntTotale(ville,
                                                             "Capacité d'autofinancement = CAF",
                                                             annee)
        dictDette[str(annee)] = utilitaires.getValeurIntTotale(ville,
                                                               'Encours de la dette au 31/12/N',
                                                               annee)
    ratioCAFDette, tendanceRatio = tendanceRatioDetteCAF(config, dictCAF, dictDette,
                                                         isWikicode, verbose)
    ville['data']['ratioCAFDette'] = ratioCAFDette
    ville['data']['tendanceRatio'] = tendanceRatio

    if verbose:
        print("Sortie de calculeRatioDetteCAF")

def tendanceRatioDetteCAF(config, dictCAF, dictDette, isWikicode, verbose):
    """ Retourne une chaine de caractère qui qualifie le ratio Dette/CAF """

    if verbose:
        print("\nEntree dans calculeRatioDetteCAF")
        print("isWikicode =", isWikicode)

    msg = "tendanceRatioDetteCAF : CAF vide !"
    assert len(dictCAF) > 0, msg
    msg = "tendanceRatioDetteCAF : CAF dictCAF et dictDette sont de taille différentes!"
    assert len(dictCAF) == len(dictDette), msg

    seuilEcreteRatio = int(config.get('GenCode', 'gen.seuilEcreteRatio'))
    seuilBigRatio = int(config.get('GenCode', 'gen.seuilBigRatio'))
    seuilLowRatio = int(config.get('GenCode', 'gen.seuilLowRatio'))

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
    strTendance = "Sur une période de "
    if isWikicode:
        strTendance += "{{nobr|"
    strTendance += str(len(listeAnneesStr)) +  " années"
    if isWikicode:
        strTendance += "}}"
    strTendance += ", ce ratio "
    if abs(dicoRatio[maxAnneeR] - dicoRatio[minAnneeR]) < 5:
        moyMinMaxRatio = (dicoRatio[maxAnneeR] + dicoRatio[minAnneeR]) / 2
        if verbose:
            print("moyMinMaxRatio=", moyMinMaxRatio)
        if moyMinMaxRatio > seuilBigRatio:
            strTendance += "est constant et élevé (supérieur à "
            if isWikicode:
                strTendance += "{{nobr|"
            strTendance += str(seuilBigRatio)
            if isWikicode:
                strTendance += "}}"
            strTendance += " ans)"
        elif moyMinMaxRatio < seuilLowRatio:
            strTendance += "est constant et faible (inférieur à "
            if isWikicode:
                strTendance += "{{nobr|"
            strTendance += str(seuilLowRatio)
            if isWikicode:
                strTendance += "}}"
            strTendance += " ans)"
        else:
            strTendance += "est constant (autour de "
            if isWikicode:
                strTendance += "{{nobr|"
            strTendance += str(moyMinMaxRatio)
            if isWikicode:
                strTendance += "}}"
            strTendance += " ans)"
    else:
        strTendance += "présente un minimum"
        if minAnneeR != listeAnneesStr[0]:
            strTendance += " " +  presentRatioDettesCAF(config, dicoRatio[minAnneeR],
                                                        isWikicode, verbose)
        strTendance += (" en " + str(minAnneeR) + " et un maximum")
        if maxAnneeR != listeAnneesStr[0]:
            strTendance += " " +  presentRatioDettesCAF(config, dicoRatio[maxAnneeR],
                                                        isWikicode, verbose)
        strTendance += (" en " + str(maxAnneeR) + ".")

    if verbose:
        print("dicoRatio=", dicoRatio)
        print("strTendance=", strTendance)
        print("Sortie de calculeRatioDetteCAF")
    return dicoRatio, strTendance

def presentRatioDettesCAF(config, ratio, isWikicode, verbose):
    """
    Construit une chaine de caractères qualifiant le ration Dettes / CAF
    V0.8 : précision qualification ratio
    """
    if verbose:
        print("\nEntrée dans presentRatioDettesCAF")
        print("Ratio =", ratio)
        print("isWikicode =", isWikicode)

    seuilBigRatioStr = int(config.get('GenCode', 'gen.seuilBigRatio'))
    seuilEcreteRatio = int(config.get('GenCode', 'gen.seuilEcreteRatio'))
    if verbose:
        print("seuilBigRatioStr =", seuilBigRatioStr)

    if ratio < 1:
        ratioStr = "de moins d'un an"
    elif ratio < 2:
        ratioStr = "d'environ un an"
    else:
        if ratio >= seuilEcreteRatio:
            ratioStr = "très élevé, de plus de "
        elif ratio >= seuilBigRatioStr:
            ratioStr = "élevé d'un montant de "
        else:
            ratioStr = "d'environ "
        if isWikicode:
            ratioStr += "{{nobr|"
        ratioStr += "%.0f années"%ratio
        if isWikicode:
            ratioStr += "}}"

    if verbose:
        print("ratioStr=", ratioStr)
        print("Sortie de presentRatioDettesCAF")
    return ratioStr
