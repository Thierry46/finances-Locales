#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
*********************************************************
Programme : genCodeCSV.py
Auteur : Thierry Maillard (TMD)
Date : 12/10/2015

Role : Transforme les donnees brutes traitées par
       extractionMinFi.py en texte CSV.
       Comma Separated Values Français : colonnes séparées par des ;
       nombre comportant des , pour les décimales
       https://fr.wikipedia.org/wiki/Comma-separated_values

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
import json
import configparser

import utilitaires

def genCodeCSV1Ville(ville, listAnnees,
                     sousCle, verbose):
    """
    Transforme les donnees brutes extraites pour une ville en texte CSV.
    Comma Separated Values Français : colonnes séparées par des ;
    nombre comportant des , pour les décimales
    https://fr.wikipedia.org/wiki/Comma-separated_values
    """
    if verbose:
        print("Entree dans genCodeCSV1Ville")
        print('ville =', ville['nom'])

    # V 2.1.0 : Ajout ref : Pour correspondance clé - ref du MinFi
    config = configparser.RawConfigParser()
    ficProperties = 'FinancesLocales.properties'
    config.read(ficProperties)

    nomFic = config.get('Extraction', 'extraction.ficCleFi')
    hFic = open(nomFic, 'r')
    cleFi = json.load(hFic)
    hFic.close()

    listAnneesTri = sorted(listAnnees)

    # Entetes
    textSection = '"Grandeurs"'
    for annee in listAnneesTri:
        textSection += ";" + str(annee)
    textSection += '";Références"'
    textSection += "\n"

    # Valeurs
    for cle in ville['data'].keys():
        if cle not in ["tendanceRatio", "ratioCAFDette"]:
            textSection += '"' + cle + '"'
            for annee in listAnneesTri:
                textSection += ";"
                if ville['data'][cle][str(annee)] is not None:
                    if cle.startswith("Taux"):
                        if sousCle in ["Valeur totale", "Par habitant"]:
                            sousCleTaux = "Taux"
                        elif sousCle == "En moyenne pour la strate":
                            sousCleTaux = "Taux moyen pour la strate"
                        textSection += \
                            str(ville['data'][cle][str(annee)][sousCleTaux]).\
                                replace('.', ',')
                    else:
                        textSection += \
                            utilitaires.getValeur(ville, cle, annee, sousCle)

            # V 2.1.0 : Ajout ref : Recherche et écriture numéro de tableau MinFi de la clé
            numTab = ""
            for cleMinFi in cleFi:
                if cleMinFi[1] == cle:
                    numTab = cleMinFi[0]
            textSection += ';"'
            if numTab == "":
                textSection += ville['refDetail']['url']
            else:
                textSection += ville['ref'][numTab]['url']
            textSection += '"\n'

    if verbose:
        print("Sortie de genCodeCSV1Ville")

    return textSection
 