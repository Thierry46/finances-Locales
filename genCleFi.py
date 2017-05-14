#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
*********************************************************
Programme : genCleFi.py
Auteur : Thierry Maillard (TMD)
Date : 24/5/2015 - 2/8/2015

Role : Génere le cles d'accès MinFi pour extractionMinFi.py

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
import configparser
import json
import sys

def main():
    """ Génère la liste des clé utiles pour les pages du ministère des Finances """
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    cleFi = \
    [
        ['0', "RESULTAT COMPTABLE"],
        ['0', "TOTAL DES PRODUITS DE FONCTIONNEMENT"],
        ['0', "TOTAL DES CHARGES DE FONCTIONNEMENT"],
        ['0', "TOTAL DES RESSOURCES D'INVESTISSEMENT"],
        ['0', "Besoin ou capacité de financement de la section d'investissement"],
        ['0', "TOTAL DES EMPLOIS D'INVESTISSEMENT"],
        ['1', "dont : Charges de personnel"],
        ['1', "Achats et charges externes"],
        ['1', "dont : Impôts Locaux"],
        ['1', "Autres impôts et taxes"],
        ['1', "Dotation globale de fonctionnement"],
        ['1', "Charges financières"],
        ['1', "Subventions versées"],
        ['1', "Contingents"],
        ['2', "TOTAL DES EMPLOIS D'INVESTISSEMENT"],
        ['2', "Subventions reçues"],
        ['2', "FCTVA"],
        ['2', "dont : Dépenses d'équipement"],
        ['2', "Remboursement d'emprunts et dettes assimilées"],
        ['2', "dont : Emprunts bancaires et dettes assimilées"],
        ['3', "Taxe d'habitation (y compris THLV)"],
        ['3', "Foncier bâti"],
        ['3', "Foncier non bâti"],
        ['4', "Capacité d'autofinancement = CAF"],
        ['5', "Encours de la dette au 31/12/N"],
        ['5', "Annuité de la dette"]
    ]

    nomFic = config.get('Extraction', 'extraction.ficCleFi')
    hFic = open(nomFic, 'w')
    # V2.4.0 : Correction problème encoding caractères accentués lors dump json : ensure_ascii=False
    json.dump(cleFi, hFic, indent=4, sort_keys=True, ensure_ascii=False)
    hFic.close()
    print("OK :", nomFic)

    cleFiDetail = \
    [
        {
            "titres" :
            [
                "Les taux et les produits de la fiscalité directe locale",
                "Potentiel fiscal"
            ],
            "libelles" :
            [
                "Taxe d'habitation (y compris THLV)",
                "Produits taxe d'habitation"
            ],
            "alias" : "Taux Taxe d'habitation",
        },
        {
            "titres" :
            [
                "Les taux et les produits de la fiscalité directe locale",
                "Produits taxe d'habitation"
            ],
            "libelles" :
            [
                "Taxe foncière sur les propriétés bâties",
                "Produits foncier bâti"
            ],
            "alias" : "Taux Taxe foncière bâti",
        },
        {
            "titres" :
            [
                "Les taux et les produits de la fiscalité directe locale",
                "Produits taxe d'habitation"
            ],
            "libelles" :
                [
                    "Taxe foncière sur les propriétés non bâties",
                    "Produits foncier non bâti"
                ],
            "alias" : "Taux Taxe foncière non bâti",
        }
    ]

    nomFic = config.get('Extraction', 'extraction.ficCleFiDetail')
    hFic = open(nomFic, 'w')
    # V2.4.0 : Correction problème encoding caractères accentués lors dump json : ensure_ascii=False
    json.dump(cleFiDetail, hFic, indent=4, sort_keys=True, ensure_ascii=False)
    hFic.close()
    print("OK :", nomFic)

##################################################
#to be called as a script
if __name__ == "__main__":
    main()
    sys.exit(0)
