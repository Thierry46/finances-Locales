# -*- coding: utf-8 -*-
"""
*********************************************************
Module : genHTMLCodeTableaux.py
Auteur : Thierry Maillard (TMD)
Date : 24/5/2015 - 3/6/2015

Role : Transforme les donnees traitées par extractionMinFi.py
        en HTML pour les parties tableaux.
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

def GenereTableau(ville, listAnnees, nbAnneesTableau,
                  listeValeurs, couleurTitres, couleurStrate,
                  isComplet, verbose):
    """ Génère le code HTML pour un tableau historique sur N années """
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
    ligne += '<table border="1" cellpadding="2" cellspacing="2" width="100">\n'
    ligne += '   <tbody>\n'
    if isComplet:
        colspanAnnee = '3'
    else:
        colspanAnnee = '2'
    ligne += '      <tr>\n'
    ligne += '         <th></th>\n'
    for annee in sorted(listAnnees[:nbAnneesTableau]):
        ligne += '         <th colspan="'+ colspanAnnee + \
                 ' bgcolor="' + couleurTitres + '">' + \
                 str(annee) +'</th>\n'
    ligne += '      </tr>\n'

    ligne += '      <tr>\n'
    ligne += '         <th bgcolor="' + couleurTitres + '">' + \
             'Chiffres clés</th>\n'
    for annee in sorted(listAnnees[:nbAnneesTableau]):
        ligne += '         <th bgcolor="' + couleurTitres + '">' + \
                 'Valeur ('+ arrondiStr + ')</th>\n'
        ligne += '         <th bgcolor="' + couleurTitres + '">' + \
                 'Par hab. (€)</th>\n'
        if isComplet:
            ligne += '         <th bgcolor="' + couleurStrate + '">' + \
                     'Strate (€)</th>\n'
    ligne += '      </tr>\n'

    for valeur in listeValeurs:
        ligne += '      <tr>\n'
        ligne += '         <th bgcolor="' + valeur[2] + '">' + \
                 valeur[1] + '</th>\n'
        for annee in sorted(listAnnees[:nbAnneesTableau]):
            ligne += '         <td align="right" bgcolor="' + valeur[2] + '">' + \
                     utilitaires.getValeur(ville, valeur[0], annee, "Valeur totale", arrondi) + \
                     '</td>\n'
            ligne += '         <td align="right" bgcolor="' + valeur[2] + '">' + \
                     utilitaires.getValeur(ville, valeur[0], annee, "Par habitant") + \
                     '</td>\n'
            if isComplet:
                ligne += '         <td align="right" bgcolor="' + couleurStrate + '">' + \
                         utilitaires.getValeur(ville, valeur[0], annee,
                                               "En moyenne pour la strate") + \
                         '</td>\n'
        ligne += '      </tr>\n'

    arrondiLigne = "Les valeurs sont arrondies au " + arrondiStrAffiche + " le plus proche."
    colspanlegende = str(1 + int(colspanAnnee) * nbAnneesTableau)
    ligne += '         <td colspan="'+ colspanlegende + \
             ' bgcolor="' + couleurTitres + '">' + \
             arrondiLigne +'</td>\n'

    ligne += '   </tbody>\n'
    ligne += '<table>\n'

    if verbose:
        print("Sortie de GenereTableau")
    return ligne.strip()

def GenereTableauTaux(ville, listAnnees, nbAnneesTableau,
                      listeValeurs, couleurTitres, couleurStrate,
                      isComplet, verbose):
    """ Genere le code HTML pour un tableau de taux de fiscalité """
    if verbose:
        print("Entrée dans GenereTableauTaux (HTML)")
        print('ville=', ville['nom'])
        print("isComplet :", str(isComplet))

    # v1.0.0 : pour cas particulier Paris : Recherche années ou les taux sont disponibles
    anneesOK = [annee for annee in sorted(listAnnees[:nbAnneesTableau])
                if ville['data'][listeValeurs[0][0]][str(annee)] is not None]
    if verbose:
        print('anneesOK=', anneesOK)

    # Titres
    ligne = ""
    ligne += '<table border="1" cellpadding="2" cellspacing="2" width="100">\n'
    ligne += '   <tbody>\n'
    if isComplet:
        colspanAnnee = '2'
    else:
        colspanAnnee = '1'
    ligne += '      <tr>\n'
    ligne += '         <th></th>\n'
    for annee in anneesOK:
        ligne += '         <th colspan="'+ colspanAnnee + \
                 ' bgcolor="' + couleurTitres + '">' + \
                 str(annee) +'</th>\n'
    ligne += '      </tr>\n'
    ligne += '      <tr>\n'
    ligne += '         <th bgcolor="' + couleurTitres + '">' + \
             'Valeurs en %</th>\n'
    for annee in anneesOK:
        ligne += '         <th bgcolor="' + couleurTitres + '">' + \
                 'Taux voté</th>\n'
        if isComplet:
            ligne += '         <th bgcolor="' + couleurStrate + '">' + \
                     'Taux moyen de la strate</th>\n'
    ligne += '      </tr>\n'

    for valeur in listeValeurs:
        ligne += '      <tr>\n'
        ligne += '         <th bgcolor="' + valeur[2] + '">' + \
                 valeur[1] + '</th>\n'
        for annee in anneesOK:
            ligne += '         <td align="right" bgcolor="' + valeur[2] + '">' + \
                     utilitaires.getValeurFloat(ville, valeur[0], annee, "Taux", verbose) + \
                     '</td>\n'
            if isComplet:
                ligne += '         <td align="right" bgcolor="' + couleurStrate + '">' + \
                         utilitaires.getValeurFloat(ville, valeur[0], annee,
                                                    "Taux moyen pour la strate") + \
                         '</td>\n'
        ligne += '      </tr>\n'

    ligne += '   </tbody>\n'
    ligne += '<table>\n'

    if verbose:
        print("Sortie de GenereTableauTaux (HTML)")

    return ligne.strip()
