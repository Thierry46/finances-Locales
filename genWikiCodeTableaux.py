# -*- coding: utf-8 -*-
"""
*********************************************************
Module : genWikiCodeTableaux.py
Auteur : Thierry Maillard (TMD)
Date : 24/5/2015 - 3/6/2015

Role : Transforme les donnees traitées par extractionMinFi.py
        en wikicode pour les parties tableaux.
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
import utilitaires

def GenereTableau(nomTableau, ville, listAnnees, nbAnneesTableau,
                  listeValeurs, couleurTitres, couleurStrate,
                  isComplet, verbose):
    """ Génère le Wikicode pour un tableau historique sur N années """
    if verbose:
        print("Entrée dans GenereTableau")
        print('ville=', ville['nom'])
        print("isComplet :", str(isComplet))

    # Détermination de l'arrondi à utiliser :
    # Arrondi en million sauf si une des valeurs à afficher est < 1000000
    arrondi = 2
    arrondiStr = 'M€'
    arrondiStrAffiche = "million d'euros (M€)"
    for valeur in listeValeurs:
        for annee in sorted(listAnnees[:nbAnneesTableau]):
            valeurData = utilitaires.getValeur(ville, valeur[0], annee, "Valeur totale")
            if int(valeurData) < 1000000:
                arrondi = 1
                arrondiStr = 'k€'
                arrondiStrAffiche = "millier d'euros (k€)"
    if verbose:
        print("arrondi =", arrondi, ", arrondiStr = ", arrondiStr)
        print("arrondiStrAffiche = ", arrondiStrAffiche)

    # Titres
    ligne = ""
    ligne += ' |\n'
    if isComplet:
        colspanAnnee = '3'
    else:
        colspanAnnee = '2'
    for annee in sorted(listAnnees[:nbAnneesTableau]):
        ligne += ' ! id="' + nomTableau + str(annee) + '" colspan="'+ colspanAnnee + \
                 '" style="background-color: ' + couleurTitres + '" |' + str(annee) +'\n'
    ligne += ' |-\n'
    ligne += ' ! id="' + nomTableau + 'h" style="background:' + couleurTitres + \
             '" | Chiffres clés\n'
    for annee in sorted(listAnnees[:nbAnneesTableau]):
        ligne += ' ! id="' + nomTableau + str(annee) + 'V" headers="'+ nomTableau + \
                 str(annee) + '" scope="col" style="background-color: ' + \
                 couleurTitres + '" | Valeur ('+ arrondiStr + ')\n'
        ligne += ' ! id="' + nomTableau + str(annee) + 'P" headers="'+ nomTableau + \
                 str(annee) + '" scope="col" style="background-color: ' + \
                 couleurTitres + '" | Par hab. (€)\n'
        if isComplet:
            ligne += ' ! id="' + nomTableau + str(annee) + 'S" headers="'+ nomTableau + \
                     str(annee) + '" scope="col" style="background-color: ' + \
                     couleurStrate + '" | Strate (€)\n'
    ligne += ' |-\n'

    for valeur in listeValeurs:
        ligne += ' ! headers="'+ nomTableau + 'h" scope="row" style="background-color: ' + \
                 valeur[2] + '" | ' + valeur[1] + '\n'
        for annee in sorted(listAnnees[:nbAnneesTableau]):
            ligne += ' | headers="'+ nomTableau + str(annee) + ' ' + nomTableau + \
                     str(annee) + 'V"' + ' style="text-align:right;background-color: ' + \
                     valeur[2] + '" | {{unité|' + \
                     utilitaires.getValeur(ville, valeur[0], annee,
                                           "Valeur totale", arrondi) + \
                     '}}\n'
            ligne += ' | headers="'+ nomTableau + str(annee) + ' ' + nomTableau + \
                     str(annee) + 'P"' + ' style="text-align:right;background-color: ' + \
                     valeur[2] + '" | {{unité|' + \
                     utilitaires.getValeur(ville, valeur[0], annee, "Par habitant") + \
                     '}}\n'
            if isComplet:
                ligne += ' | headers="'+ nomTableau + str(annee) + ' ' + nomTableau + \
                         str(annee) + 'S"' + ' style="text-align:right;background-color: ' + \
                         couleurStrate + '" | {{unité|' + \
                         utilitaires.getValeur(ville, valeur[0], annee,
                                               "En moyenne pour la strate") + \
                         '}}\n'
        ligne += ' |-\n'
    arrondiLigne = "Les valeurs sont arrondies au " + arrondiStrAffiche + " le plus proche."
    colspanlegende = str(1 + int(colspanAnnee) * nbAnneesTableau)
    ligne += ' ! colspan="'+ colspanlegende + \
             '" style="background-color: ' + couleurTitres + '" | ' + \
             arrondiLigne + '\n'
    ligne += ' |-\n'

    if verbose:
        print("Sortie de GenereTableau")

    return ligne.strip()

def GenereTableauTaux(nomTableau, ville, listAnnees, nbAnneesTableau,
                      listeValeurs, couleurTitres, couleurStrate,
                      isComplet, verbose):
    """ Genere le wikicode pour un tableau de taux de fiscalité """
    if verbose:
        print("Entrée dans GenereTableauTaux")
        print('ville=', ville['nom'])
        print("isComplet :", str(isComplet))

    # v1.0.0 : pour cas particulier Paris : Recherche années ou les taux sont disponibles
    anneesOK = [annee for annee in sorted(listAnnees[:nbAnneesTableau])
                if ville['data'][listeValeurs[0][0]][str(annee)] is not None]
    if verbose:
        print('anneesOK=', anneesOK)

    # Titres
    ligne = ""
    ligne += ' |\n'
    if isComplet:
        colspanAnnee = '2'
    else:
        colspanAnnee = '1'
    for annee in anneesOK:
        ligne += ' ! id="' + nomTableau + str(annee) + '" colspan="'+ colspanAnnee + \
                 '" style="background-color: ' + couleurTitres + '" |' + str(annee) +'\n'
    ligne += ' |-\n'
    ligne += ' ! id="' + nomTableau + 'h" style="background:' + couleurTitres + \
             '" | Chiffres clés\n'
    for annee in anneesOK:
        ligne += ' ! id="' + nomTableau + str(annee) + 'TV" headers="'+ nomTableau + \
                 str(annee) + '" scope="col" style="background-color: ' + \
                 couleurTitres + '" | Taux voté %\n'
        if isComplet:
            ligne += ' ! id="' + nomTableau + str(annee) + 'TM" headers="'+ \
                     nomTableau + str(annee) + \
                    '" scope="col" style="background-color: ' + couleurStrate + \
                    '" | ' + "Taux moyen de la strate %\n"
    ligne += ' |-\n'

    for valeur in listeValeurs:
        ligne += ' ! headers="'+ nomTableau + 'h" scope="row" style="background-color: ' + \
                 valeur[2] + '" | ' + valeur[1] + '\n'
        for annee in anneesOK:
            ligne += ' | headers="'+ nomTableau + str(annee) + ' ' + nomTableau + \
                     str(annee) + 'TV"' + ' style="text-align:right;background-color: ' + \
                     valeur[2] + '" | {{unité|' + \
                     utilitaires.getValeurFloat(ville, valeur[0], annee, "Taux", verbose) + \
                     '}}\n'
            if isComplet:
                ligne += ' | headers="'+ nomTableau + str(annee) + ' ' + nomTableau + \
                         str(annee) + 'TS"' + \
                         ' style="text-align:right;background-color: ' + couleurStrate + \
                         '" | {{unité|' + \
                         utilitaires.getValeurFloat(ville, valeur[0], annee,
                                                    "Taux moyen pour la strate") + \
                         '}}\n'
        ligne += ' |-\n'

    if verbose:
        print("Sortie de GenereTableauTaux")

    return ligne.strip()
