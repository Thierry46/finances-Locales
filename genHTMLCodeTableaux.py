# -*- coding: utf-8 -*-
"""
*********************************************************
Module : genHTMLCodeTableaux.py
Auteur : Thierry Maillard (TMD)
Date : 24/5/2015 - 12/5/2020

Role : Transforme les donnees traitées par extractionMinFi.py
        en HTML pour les parties tableaux.
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
import utilitaires

def genereTableau(nomTableau,
                  listAnnees, nbAnneesTableau,
                  listeGrandeurs,
                  dictAllGrandeur,
                  couleurTitres, couleurStrate,
                  avecStrate, verbose):
    """ Génère le code HTML pour un tableau historique sur N années """
    if verbose:
        print("Entrée dans genereTableau (HTML)")
        print("nomTableau=", nomTableau)
        print('listAnnees=', listAnnees)
        print('nbAnneesTableau=', nbAnneesTableau)
        print('dictAllGrandeur=', dictAllGrandeur)
        print("avecStrate :", avecStrate)

    arrondi, arrondiStr, arrondiStrAffiche = \
             utilitaires.setArrondi(dictAllGrandeur["Valeur totale"], listAnnees,
                                    1000.0, None, verbose)

    # Titres
    ligne = ""
    ligne += '<table border="1" cellpadding="2" cellspacing="2" width="100">\n'
    ligne += '   <tbody>\n'
    if avecStrate:
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
        if avecStrate:
            ligne += '         <th bgcolor="' + couleurStrate + '">' + \
                     'Strate (€)</th>\n'
    ligne += '      </tr>\n'

    for grandeur in listeGrandeurs:
        nomGrandeur = grandeur[0]
        ligne += '      <tr>\n'
        ligne += '         <th bgcolor="' + grandeur[2] + '">' + \
                 grandeur[1] + '</th>\n'
        for annee in sorted(listAnnees[:nbAnneesTableau]):
            ligne += '         <td align="right" bgcolor="' + grandeur[2] + '">' + \
                     str(round(dictAllGrandeur["Valeur totale"][nomGrandeur][annee] * arrondi)) + \
                     '</td>\n'
            ngph = nomGrandeur + " par habitant"
            ligne += '         <td align="right" bgcolor="' + grandeur[2] + '">' + \
                     str(round(dictAllGrandeur["Par habitant"][ngph][annee])) + \
                     '</td>\n'
            if avecStrate:
                ngm = nomGrandeur + " moyen"
                ligne += '         <td align="right" bgcolor="' + couleurStrate + '">' + \
                         str(round(dictAllGrandeur["En moyenne pour la strate"][ngm][annee])) + \
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
        print("Sortie de genereTableau (HTML)")
    return ligne.strip()

def genereTableauTaux(nomTableau,
                      listAnnees, nbAnneesTableau,
                      listeGrandeurs,
                      dictAllGrandeur,
                      couleurTitres, couleurStrate,
                      avecStrate, verbose):
    """ Genere le code HTML pour un tableau de taux de fiscalité """
    if verbose:
        print("Entrée dans genereTableautaux (HTML)")
        print("nomTableau=", nomTableau)
        print('listAnnees=', listAnnees)
        print('nbAnneesTableau=', nbAnneesTableau)
        print('listeGrandeurs=', listeGrandeurs)
        print("avecStrate :", avecStrate)

    # Titres
    ligne = ""
    ligne += '<table border="1" cellpadding="2" cellspacing="2" width="100">\n'
    ligne += '   <tbody>\n'
    if avecStrate:
        colspanAnnee = '2'
    else:
        colspanAnnee = '1'
    ligne += '      <tr>\n'
    ligne += '         <th></th>\n'
    for annee in sorted(listAnnees[:nbAnneesTableau]):
        ligne += '         <th colspan="'+ colspanAnnee + \
                 ' bgcolor="' + couleurTitres + '">' + \
                 str(annee) +'</th>\n'
    ligne += '      </tr>\n'
    ligne += '      <tr>\n'
    ligne += '         <th bgcolor="' + couleurTitres + '">' + \
             'Valeurs en %</th>\n'
    for annee in sorted(listAnnees[:nbAnneesTableau]):
        ligne += '         <th bgcolor="' + couleurTitres + '">' + \
                 'taux voté</th>\n'
        if avecStrate:
            ligne += '         <th bgcolor="' + couleurStrate + '">' + \
                     'taux moyen de la strate</th>\n'
    ligne += '      </tr>\n'

    for grandeur in listeGrandeurs:
        nomGrandeur = grandeur[0]
        ligne += '      <tr>\n'
        ligne += '         <th bgcolor="' + grandeur[2] + '">' + \
                 grandeur[1] + '</th>\n'
        for annee in sorted(listAnnees[:nbAnneesTableau]):
            ligne += '         <td align="right" bgcolor="' + grandeur[2] + '">' + \
                     str(round(dictAllGrandeur["Taux"][nomGrandeur][annee], 2)) + \
                     '</td>\n'
            if avecStrate:
                ngm = nomGrandeur + " moyen"
                ligne += '         <td align="right" bgcolor="' + couleurStrate + '">' + \
                         str(round(dictAllGrandeur["taux moyen pour la strate"][ngm][annee], 2)) + \
                         '</td>\n'
        ligne += '      </tr>\n'

    ligne += '   </tbody>\n'
    ligne += '<table>\n'

    if verbose:
        print("Sortie de genereTableautaux (HTML)")

    return ligne.strip()
