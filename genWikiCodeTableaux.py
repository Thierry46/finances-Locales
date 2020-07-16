# -*- coding: utf-8 -*-
"""
*********************************************************
Module : genWikiCodeTableaux.py
Auteur : Thierry Maillard (TMD)
Date : 24/5/2015 - 12/5/2020

Role : Transforme les donnees traitées par extractionMinFi.py
        en wikicode pour les parties tableaux.
------------------------------------------------------------
Licence : GPLv3 (en français dans le fichier gpl-3.0.fr.txt)
Copyright (c) 2015 - 2019 - Thierry Maillard
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

def genereTableau(nomTableau,
                  listAnnees, nbAnneesTableau,
                  listeGrandeurs,
                  dictAllGrandeur,
                  couleurTitres, couleurStrate,
                  avecStrate, verbose):
    """ Génère le Wikicode pour un tableau historique sur N années """
    if verbose:
        print("Entrée dans genereTableau (Wikicode)")
        print('listAnnees=', listAnnees)
        print('nbAnneesTableau=', nbAnneesTableau)
        print('dictAllGrandeur=', dictAllGrandeur)
        print("avecStrate :", avecStrate)

    arrondi, arrondiStr, arrondiStrAffiche = \
             utilitaires.setArrondi(dictAllGrandeur["Valeur totale"], listAnnees,
                                    1000.0, None, verbose)

    # Titres
    ligne = ""
    ligne += ' |\n'
    if avecStrate:
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
        if avecStrate:
            ligne += ' ! id="' + nomTableau + str(annee) + 'S" headers="'+ nomTableau + \
                     str(annee) + '" scope="col" style="background-color: ' + \
                     couleurStrate + '" | Strate (€)\n'
    ligne += ' |-\n'

    for grandeur in listeGrandeurs:
        nomGrandeur = grandeur[0]
        ligne += ' ! headers="'+ nomTableau + 'h" scope="row" style="background-color: ' + \
                 grandeur[2] + '" | ' + grandeur[1] + '\n'
        for annee in sorted(listAnnees[:nbAnneesTableau]):
            ligne += ' | headers="'+ nomTableau + str(annee) + ' ' + nomTableau + \
                     str(annee) + 'V"' + ' style="text-align:right;background-color: ' + \
                     grandeur[2] + '" | {{unité|' + \
                     str(round(dictAllGrandeur["Valeur totale"][nomGrandeur][annee] * arrondi)) + \
                     '}}\n'
            valFloat = dictAllGrandeur["Par habitant"][nomGrandeur + " par habitant"][annee]
            ligne += ' | headers="'+ nomTableau + str(annee) + ' ' + nomTableau + \
                     str(annee) + 'P"' + ' style="text-align:right;background-color: ' + \
                     grandeur[2] + '" | {{unité|' + \
                     str(round(valFloat)) + '}}\n'
            if avecStrate:
                ngm = nomGrandeur + " moyen"
                valFloat = dictAllGrandeur["En moyenne pour la strate"][ngm][annee]
                ligne += ' | headers="'+ nomTableau + str(annee) + ' ' + nomTableau + \
                         str(annee) + 'S"' + ' style="text-align:right;background-color: ' + \
                         couleurStrate + '" | {{unité|' + \
                         str(round(valFloat)) + '}}\n'
        ligne += ' |-\n'
    arrondiLigne = "Les valeurs sont arrondies au " + arrondiStrAffiche + " le plus proche."
    colspanlegende = str(1 + int(colspanAnnee) * nbAnneesTableau)
    ligne += ' ! colspan="'+ colspanlegende + \
             '" style="background-color: ' + couleurTitres + '" | ' + \
             arrondiLigne + '\n'
    ligne += ' |-\n'

    if verbose:
        print("ligne=", ligne)
        print("Sortie de genereTableau (Wikicode)")

    return ligne.strip()

def genereTableauTaux(nomTableau,
                      listAnnees, nbAnneesTableau,
                      listeGrandeurs,
                      dictAllGrandeur,
                      couleurTitres, couleurStrate,
                      avecStrate, verbose):
    """ Genere le wikicode pour un tableau de taux de fiscalité """
    if verbose:
        print("Entrée dans genereTableautaux (Wikicode)")
        print('listAnnees=', listAnnees)
        print('nbAnneesTableau=', nbAnneesTableau)
        print('dictAllGrandeur=', dictAllGrandeur)
        print("avecStrate :", avecStrate)

    # Titres
    ligne = ""
    ligne += ' |\n'
    if avecStrate:
        colspanAnnee = '2'
    else:
        colspanAnnee = '1'

    for annee in sorted(listAnnees[:nbAnneesTableau]):
        ligne += ' ! id="' + nomTableau + str(annee) + '" colspan="'+ colspanAnnee + \
                 '" style="background-color: ' + couleurTitres + '" |' + str(annee) +'\n'
    ligne += ' |-\n'
    ligne += ' ! id="' + nomTableau + 'h" style="background:' + couleurTitres + \
             '" | Chiffres clés\n'
    for annee in sorted(listAnnees[:nbAnneesTableau]):
        ligne += ' ! id="' + nomTableau + str(annee) + 'TV" headers="'+ nomTableau + \
                 str(annee) + '" scope="col" style="background-color: ' + \
                 couleurTitres + '" | taux voté %\n'
        if avecStrate:
            ligne += ' ! id="' + nomTableau + str(annee) + 'TM" headers="'+ \
                     nomTableau + str(annee) + \
                    '" scope="col" style="background-color: ' + couleurStrate + \
                    '" | ' + "taux moyen de la strate %\n"
    ligne += ' |-\n'

    for grandeur in listeGrandeurs:
        nomGrandeur = grandeur[0]
        ligne += ' ! headers="'+ nomTableau + 'h" scope="row" style="background-color: ' + \
                 grandeur[2] + '" | ' + grandeur[1] + '\n'
        for annee in sorted(listAnnees[:nbAnneesTableau]):
            ligne += ' | headers="'+ nomTableau + str(annee) + ' ' + nomTableau + \
                     str(annee) + 'TV"' + ' style="text-align:right;background-color: ' + \
                     grandeur[2] + '" | {{unité|' + \
                     str(round(dictAllGrandeur["Taux"][nomGrandeur][annee], 2)) + \
                     '}}\n'
            if avecStrate:
                ngm = nomGrandeur + " moyen"
                valFloat = dictAllGrandeur["taux moyen pour la strate"][ngm][annee]
                ligne += ' | headers="'+ nomTableau + str(annee) + ' ' + nomTableau + \
                         str(annee) + 'TS"' + \
                         ' style="text-align:right;background-color: ' + couleurStrate + \
                         '" | {{unité|' + str(round(valFloat, 2)) + '}}\n'
        ligne += ' |-\n'

    if verbose:
        print("Sortie de genereTableautaux (Wikicode)")

    return ligne.strip()
