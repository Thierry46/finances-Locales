# -*- coding: utf-8 -*-
"""
*********************************************************
Module : genWikiCodeGraphiques.py
Auteur : Thierry Maillard (TMD)
Date : 7/10/2015

Role : Génère la wikicode pour les parties graphiques.
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
import math

def genGraphique(config, dictAllGrandeur,
                 nomVille, anneesOK,
                 courbes, largeur,
                 arrondi, arrondiStrAffiche,
                 verbose):
    """ Génère le Wikicode pour un graphique """
    if verbose:
        print("\n**********************")
        print("Entree dans genGraphique (Wiki)")
        print("dictAllGrandeur=", dictAllGrandeur)
        print("anneesOK=", anneesOK)
        print('nomVille=', nomVille)
        print("Nombre de courbes :", len(courbes))
        print("clé =", [courbe['cle'] for courbe in courbes])

    nbSeries = len(courbes)
    nbSeriesVille = len([courbe for courbe in courbes
                         if 'strate' not in courbe['sousCle']])
    if verbose:
        print("nbSeries Ville=", nbSeriesVille)
        print("nbSeries Ville + Strate =", nbSeries)

    ligne = "| {{Graphique polygonal\n"
    ligne += " | coul_fond = white\n"
    # ! Si largeur trop petite, problème de tracé :
    # Les rectangles représentants les points "bavent"
    # par un trait oblique qui les relie au bas du graphique
    ligne += " | largeur = " + config.get('Graphiques', largeur)
    ligne += " | hauteur = " + config.get('Graphiques', 'graph.hauteur')
    ligne += "\n"

    # V0.8 : margeg = 50 pour corriger pb libellé ordonnées tronquées
    #           si grand nombre et une des série proche 0
    ligne += " | marge_g = " + config.get('Graphiques', 'graph.marge_g')
    ligne += " | marge_d = " + config.get('Graphiques', 'graph.marge_d')
    ligne += " | marge_h = " + config.get('Graphiques', 'graph.marge_h')
    ligne += " | marge_b = " + config.get('Graphiques', 'graph.marge_b')
    ligne += "\n"

    ligne += " | nb_series = " + str(nbSeries) + "\n"
    nbAbscisses = len(anneesOK)
    ligne += " | nb_abscisses = " + str(nbAbscisses) + "\n"

    # Generation dates abscisses
    # V1.0.5 : Correction bug si annee manquante
    for indice, anneeI in enumerate(anneesOK):
        ligne += " | lb_x" + str(indice+1) + " = " + str(anneeI)
    ligne += "\n"

    # Détermination min, max des valeurs
    maxVal = -sys.maxsize - 1
    minVal = sys.maxsize
    for annee in anneesOK:
        for courbe in courbes:
            if courbe['cle'].startswith('Taux'):
                valeurData = \
                    round(dictAllGrandeur['Taux'][courbe['cle']][annee])
            elif courbe['sousCle'] == "":
                valeurData = round(dictAllGrandeur[courbe['cle']][annee])
            else:
                valFloat = dictAllGrandeur[courbe['sousCle']][courbe['cle']][annee]
                valeurData = round(valFloat * arrondi)
            maxVal = max(maxVal, valeurData)
            minVal = min(minVal, valeurData)
    if verbose:
        print("minVal =", minVal, ", maxVal = ", maxVal)

    # Calcul des caractéristiques des graduations de l'axe Y :
    # y_max, y_min, pas des graduations majeures et mineures
    yMin, yMax, pasSec, pasPrinc = myticks(minVal, maxVal, True, True, verbose)
    if verbose:
        print("yMin=", yMin)
        print("yMax=", yMax)
        print("pasSec=", pasSec)
        print("pasPrinc=", pasPrinc)

    ligne += " | y_max =" + str(yMax) + " | y_min = " + str(yMin) + "\n"
    ligne += " | pas_grille_principale = " + str(pasPrinc)
    ligne += " | pas_grille_secondaire = " + str(pasSec) + "\n"
    ligne += " | grille = oui\n"

    numSerie = 0
    for courbe in courbes:
        ligne += " | epaisseur_serie" + str(numSerie+1) + " = 0.9 "
        ligne += " | coul_serie_" + str(numSerie+1) + " = " + \
                 courbe['couleur'][1] + "\n"
        numSerie += 1

    # Data series
    numValeur = 1
    for annee in anneesOK:
        valeur = '%02d'%numValeur
        numSerie = 1
        for courbe in courbes:
            serie = '%02d'%numSerie
            if courbe['sousCle'] == "":
                valeurData = str(round(dictAllGrandeur[courbe['cle']][annee]))
            else:
                valFloat = dictAllGrandeur[courbe['sousCle']][courbe['cle']][annee]
                valeurData = str(round(valFloat * arrondi))
            ligne += " | S" + serie + "V" + valeur + " = " + valeurData + " "
            numSerie += 1
        ligne += "\n"
        numValeur += 1

    ligne += " | points = oui}}"

    # Légende
    # V1.0.2 : Accessibilité, remplacement des caractères Unicode
    #          par des images + chaine alt
    legendeVille = "Valeurs en " + arrondiStrAffiche + "<br />"
    legendeStrate = ""
    ecritLegendeVille = True
    ecritLegendeStrate = True

    for courbe in courbes:
        if 'strate' not in courbe['sousCle']:
            if ecritLegendeVille:
                legendeVille += (nomVille + ', ' + courbe['sousCle'] + ' : ')
                ecritLegendeVille = False
            legendeVille += "[[fichier:" + courbe['couleur'][0] + "|10px|alt=" + \
                            courbe['couleur'][2] + "|link=]] " + \
                            courbe['libelle'] + " "
        else:
            if ecritLegendeStrate:
                legendeStrate += '<br />' + courbe['sousCle'] + ' : '
                ecritLegendeStrate = False
            legendeStrate += "[[fichier:" + courbe['couleur'][0] + "|10px|alt=" + \
                             courbe['couleur'][2] + "|link=]] " + \
                             courbe['libelle'] + " "

    if verbose:
        print("ligne=", ligne)
        print("legendeVille=", legendeVille)
        print("legendeStrate =", legendeStrate)
        print("Sortie de genGraphique (Wiki)")

    return ligne, legendeVille, legendeStrate

def myticks(MinP, MaxP, fitMin, fitMax, verbose):
    '''
    Role : Generate intelligent axis scaling
    Author : David Ascher da@ski.org
    Source : https://mail.python.org/pipermail/matrix-sig/1999-March/002668.html
    Date : Thu, 18 Mar 1999

    Usage : python ticks.py MinData MaxData
    Parameters
        -MinP, MaxP : Minimum and maximum values (int) of the dataset to plot
    Return :
        - gridMin, gridMax : min and max ticks position
        - smallTicksSpace : spacing between minor ticks
        - bigTicksSpace : spacing between major ticks
        - (may be return) r and l : minor and major ticks position.

    Modifed by Thierry Maillard (TMD) on 29/5/2015
        - Suppress log supports
        - Replace calls to NumPy with standard library calls : rand, pow
        - Add test and trick if two import numbers are too close
        - Output grid ticks spaces instead of ticks position
    '''
    if verbose:
        print("\nEntree dans myticks")
        print("MinP=", MinP, "MaxP=", MaxP)

    # TMD : if values are too close, enlarge the gap
    Max = float(MaxP)
    Min = float(MinP)
    d = abs(MaxP - MinP)
    if d < 10:
        Max = Max + 5
        Min = Min - 5
        d = abs(Max - Min)

    epsilon = 1e-10
    s = math.pow(10, math.floor(math.log10(d)) - 1)
    if fitMin:
        startat = Min - (Min % (s * 10))
    else:
        startat = Min
    overmax = Max + (s * 10)
    if fitMax:
        endat = overmax - (overmax % (s * 10))
    else:
        endat = Max
    if d / (10*s) > 5.2:  # magic!
                     # small tickmarks at unit factors
        s = s * 10   # we need to upshift the scale
        maj_mod = 10 # major tick marks at factors of 10
        int_mod = 2  # intermediate tick marks at factors of 2
    else:
        maj_mod = 10 # major tick marks at factors of 10
        int_mod = 5  # minors at factors of 5
                     # smalls at factors of 1
    r = []
    l = []
    nummajors = 0 # for debugging
    numints = 0
    for x in range(int(round(startat)), int(round(endat+epsilon)), int(round(s))):
        x = int(round(x))
        r.append(x)
        if abs((x / s) % maj_mod) < epsilon:
            l.append(x)
            nummajors = nummajors + 1
        elif abs((x / s) % int_mod) < epsilon:
            l.append(x)
            numints = numints + 1

    gridMin = int(startat)
    gridMax = int(endat)
    smallTicksSpace = int(abs(r[0] - r[1]))
    bigTicksSpace = int(abs(l[0] - l[1]))

    if verbose:
        print("gridMin=", gridMin, "gridMax=", gridMax)
        print("smallTicksSpace=", smallTicksSpace, "bigTicksSpace=", bigTicksSpace)
        print("\nSortie de myticks")
    return gridMin, gridMax, smallTicksSpace, bigTicksSpace
