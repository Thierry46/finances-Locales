#! /usr/bin/env python
# coding: utf8
"""
*********************************************************
Programme : ratioTendance.py
Auteur : Thierry Maillard (TMD)
Date : 5/9/2015 - 19/9/2019
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

import operator

import utilitaires

def calculeRatioDetteCAF(config, dictDetteCaf, verbose):
    """
        dictDetteCaf : dictionnaire  {année:[Valeur Dette, valeur Caf]}
        Retourne :
        Un dico contenant les ratios Dette/CAF : nb années pour rembourser la dette
        pour chaque année
    """

    if verbose:
        print("\nEntree dans calculeRatioDetteCAF")
        print("dictDetteCaf=", dictDetteCaf)

    if len(dictDetteCaf) == 0:
        raise ValueError("tendanceRatioDetteCAF : dictDetteCaf vide !")

    # Récupération des limites
    seuilEcreteRatio = int(config.get('GenCode', 'gen.seuilEcreteRatio'))
    if verbose:
        print("seuilEcreteRatio =", seuilEcreteRatio)

    # Contruit un dicoRatio {annee (int) : valeurRatio=dette/caf,...}
    dicoRatio = dict()
    for annee in dictDetteCaf:
        if dictDetteCaf[annee][1] < 0.5:
            ratio = seuilEcreteRatio
        else:
            ratio = int(dictDetteCaf[annee][0] / dictDetteCaf[annee][1])
            if ratio > seuilEcreteRatio:
                ratio = seuilEcreteRatio
        dicoRatio[annee] = ratio

    if verbose:
        print("dicoRatio=", dicoRatio)
        print("Sortie de calculeRatioDetteCAF")
    return dicoRatio

def presentEvolRatio(config, dicoRatio, isWikicode, verbose):
    """
        dicoRatio : Un dico contenant les ratios Dette/CAF pour chaque année
        Retourne :
        Une chaine de caractère qui qualifie le ratio Dette/CAF
    """

    if verbose:
        print("\nEntree dans calculeRatioDetteCAF")
        print("isWikicode =", isWikicode)
        print("dicoRatio=", dicoRatio)

    # Récupération des limites
    seuilBigRatio = int(config.get('GenCode', 'gen.seuilBigRatio'))
    seuilLowRatio = int(config.get('GenCode', 'gen.seuilLowRatio'))
    if verbose:
        print("seuilBigRatio=", seuilBigRatio)
        print("seuilLowRatio=", seuilLowRatio)

    # Determine les annees et valeurs du min et du max pour les ratios
    minAnnee = min(dicoRatio.keys())
    maxAnnee = max(dicoRatio.keys())
    (minAnneeR, valMinRatio) = min(dicoRatio.items(), key=operator.itemgetter(1))
    (maxAnneeR, valMaxRatio) = max(dicoRatio.items(), key=operator.itemgetter(1))
    if verbose:
        print("minAnneeR=", minAnneeR, ", valMinRatio =", valMinRatio)
        print("maxAnneeR=", maxAnneeR, ", valMaxRatio =", valMaxRatio)

    # Construit la phrase de tendance
    strTendance = "Sur une période de "
    if isWikicode:
        strTendance += "{{nobr|"
    strTendance += str(len(dicoRatio)) +  " années"
    if isWikicode:
        strTendance += "}}"
    strTendance += ", ce ratio "
    if abs(valMaxRatio - valMinRatio) < 5:
        moyMinMaxRatio = (valMaxRatio + valMinRatio) / 2
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
        if minAnneeR != minAnnee:
            strTendance += " " +  presentRatioDettesCAF(config, valMinRatio,
                                                        isWikicode, verbose)
        strTendance += (" en " + str(minAnneeR) + " et un maximum")
        if maxAnneeR != maxAnnee:
            strTendance += " " +  presentRatioDettesCAF(config, valMaxRatio,
                                                        isWikicode, verbose)
        strTendance += (" en " + str(maxAnneeR) + ".")

    if verbose:
        print("strTendance=", strTendance)
        print("Sortie de calculeRatioDetteCAF")
    return strTendance

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

def getTendanceRatioDetteCAF(config, dictAllGrandeur,
                             isWikicode, verbose):
    """
    Retourne une phrase qualifiant le rapport dette/CAF : capacité d'autofinancement
    Pour la commune codeCommune
    """
    if verbose:
        print("\nEntrée dans getTendanceRatioDetteCAF")
        print("isWikicode =", isWikicode)

    codeCleDette = "encours de la dette au 31 12 n"
    codeCleCAF = "capacité autofinancement caf"
    dictDetteCaf = utilitaires.merge2Dict(dictAllGrandeur["Valeur totale"][codeCleDette],
                                          dictAllGrandeur["Valeur totale"][codeCleCAF],
                                          verbose)
    dicoRatio = calculeRatioDetteCAF(config, dictDetteCaf, verbose)
    tendanceRatio = presentEvolRatio(config, dicoRatio, isWikicode, verbose)

    if verbose:
        print("tendanceRatio=", tendanceRatio)
        print("Sortie de getTendanceRatioDetteCAF")
    return tendanceRatio, dicoRatio
