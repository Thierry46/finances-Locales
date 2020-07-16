# -*- coding: utf-8 -*-
"""
*********************************************************
Module : genCodeGroupementTableaux.py
Auteur : Thierry Maillard (TMD)
Date : 13/5/2020

Role : Transforme les donnees traitées par
        updateDataMinFiGroupementCommunes.py
        en code pour les parties tableaux.
------------------------------------------------------------
Licence : GPLv3 (en français dans le fichier gpl-3.0.fr.txt)
Copyright (c) 2020 - Thierry Maillard
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

import genCodeCommon

def defTableauxGroupementPicto(config, dictAllGrandeur, listAnnees,
                               isWikicode, verbose):
    """
    Définition du contenu des tableaux picto spécifiques aux groupements de communes
    Retourne la structure grandeursAnalyse qui contient toutes les infos
    """
    if verbose:
        print("Entrée dans defTableauxGroupementPicto")

    couleurSolde = config.get('Tableaux', 'tableaux.couleurSolde')
    couleurRecettes = config.get('Tableaux', 'tableaux.couleurRecettes')
    couleurCharges = config.get('Tableaux', 'tableaux.couleurCharges')
    couleurDettesCAF = config.get('Tableaux', 'tableaux.couleurDettesCAF')
    couleurCAF = config.get('Tableaux', 'tableaux.couleurCAF')
    couleurEmploisInvest = config.get('Tableaux', 'tableaux.couleurEmploisInvest')
    couleurRessourcesInvest = config.get('Tableaux', 'tableaux.couleurRessourcesInvest')

    codeCle = "total des charges de fonctionnement"
    chargesF = dictAllGrandeur["Valeur totale"][codeCle][listAnnees[0]] * 1e3
    codeCle = "total des emplois investissement"
    emploisI = dictAllGrandeur["Valeur totale"][codeCle][listAnnees[0]] * 1e3
    codeCle = "total des produits de fonctionnement"
    produitsF = dictAllGrandeur["Valeur totale"][codeCle][listAnnees[0]] * 1e3
    codeCle = "total des ressources d'investissement"
    ressourcesI = dictAllGrandeur["Valeur totale"][codeCle][listAnnees[0]] * 1e3

    # Pour comparaison valeur par habitant des données de l'année la plus récente
    grandeursAnalyse = []
    dictCharges = \
    {
        'des ' + genCodeCommon.genLien(config,
                                       ["Charge (comptabilité)",
                                        "charges"],
                                       isWikicode, verbose) + ' de personnels' :
        {
            'libellePicto' : 'Charges de personnels',
            'cle' : "dont charges de personnel",
            'note' : "Les « charges de personnel » regroupent les frais " + \
                     "de [[rémunération]] des employés du groupement.",
            'noteHtml' : "7",
            'nul' : 'aucune ' + genCodeCommon.genLien(config,
                                                      ["Charge (comptabilité)",
                                                       "charges"],
                                                      isWikicode, verbose) + \
            ' de personnel'
        },
        'des ' + genCodeCommon.genLien(config, ["achats"], isWikicode, verbose) + \
        ' et charges externes' :
        {
            'libellePicto' : 'Achats et charges ext.',
            'cle' : "achats et charges externes",
            'note' : "Le poste « achats et charges externes » regroupe " + \
                     "les achats non stockés de matières et fournitures " + \
                     "([[Eau potable|eau]], [[énergie]]...), le petit matériel, " +\
                     "les achats de [[Crédit-bail|crédits-bails]], " + \
                     "les [[location]]s, [[Prime d'assurance|primes d'assurances]]...",
            'noteHtml' : "8",
            'nul' : 'aucun ' + genCodeCommon.genLien(config,
                                                     ["achats", "achat"],
                                                     isWikicode, verbose) + \
            ' ou charge externe'
        },
        'des charges financières' :
        {
            'libellePicto' : 'charges financières',
            'cle' : "charges financières",
            'note' : "Les « charges financières » correspondent à la rémunération " + \
                         "des ressources d'[[Emprunt (finance)|emprunt]].",
            'noteHtml' : "9",
            'nul' : 'aucune charge financière'
        },
        'des ' + genCodeCommon.genLien(config, ["subventions"],
                                       isWikicode, verbose) + \
        ' versées' :
        {
            'libellePicto' : 'subventions versées',
            'cle' : "subventions versées",
            'note' : "Les « subventions versées » rassemblent l'ensemble " + \
                     "des [[subvention]]s à des associations votées par le " + \
                     "[[Établissement public de coopération intercommunale|"+ \
            "conseil communautaire]].",
            'noteHtml' : "10",
            'nul' : 'aucune ' + genCodeCommon.genLien(config, ["subvention"],
                                                      isWikicode, verbose) + ' versée'
        },
    }
    grandeursAnalyse.append([dictCharges, chargesF, "CHARGE", couleurCharges])

    dictEncoursDette = \
    {
        "l'encours de la dette" :
        {
            'libellePicto' : 'Encours de la dette',
            'cle' : 'encours de la dette au 31 12 n',
            'note' : "",
            'noteHtml' : '',
            'nul' : "pas d'encours pour la dette"
        }
    }
    grandeursAnalyse.append([dictEncoursDette, 0, "ENCOURS_DETTE", couleurDettesCAF])

    dictAnnuiteDette = \
    {
        "l'annuité de la dette" :
        {
            'libellePicto' : 'annuité de la dette',
            'cle' : "annuité de la dette",
            'note' : "",
            'noteHtml' : '',
            'nul' : 'aucune annuité pour la dette'
        }
    }
    grandeursAnalyse.append([dictAnnuiteDette, 0, "ANNUITE_DETTE", couleurDettesCAF])

    # Recettes
    dictRecettes = \
    {
        'des ' + genCodeCommon.genLien(config,
                                       ["Impôts locaux en France",
                                        "impôts locaux"],
                                       isWikicode, verbose) :
        {
            'libellePicto' : 'Impôts locaux',
            'cle' : "dont impôts locaux",
            'note' : "Les « [[Impôts locaux en France|impôts locaux]] » " +\
                    "désignent les [[impôt]]s prélevés par les " + \
                    "[[Collectivité territoriale|collectivités territoriales]] " + \
                    "pour alimenter leur budget. Ils regroupent " + \
                    "les [[Taxe foncière|impôts fonciers]], la [[taxe d'habitation]] " + \
                    "ou encore, pour les [[entreprise]]s, les " + \
                    "[[Cotisation foncière des entreprises|cotisations foncières]] ou " + \
                    "sur la [[valeur ajoutée]].",
            'noteHtml' : "12",
            'nul' : 'aucun ' + genCodeCommon.genLien(config,
                                                     ["Impôts locaux en France",
                                                      "impôt local"],
                                                     isWikicode, verbose)
        },
        "de la " + genCodeCommon.genLien(config,
                                         ["dotation globale de fonctionnement"],
                                         isWikicode, verbose) + " (DGF)" :
        {
            'libellePicto' : 'dotation globale de fonctionnement',
            'cle' : 'dotation globale de fonctionnement',
            'note' : "Les « [[Finances locales en France#Dotations et subventions de " + \
                     "l'État|dotations globales de fonctionnement]] » désignent, en " + \
                     "[[France]], des concours financiers de l'[[État]] au [[budget]] " + \
                     "des [[Collectivité territoriale|collectivités territoriales]].",
            'noteHtml' : "13",
            'nul' : 'aucune somme au titre de la [[dotation globale de fonctionnement]]'
        },
        'des ' + genCodeCommon.genLien(config,
                                       ["Impôts locaux en France", "autres impôts"],
                                       isWikicode, verbose) :
        {
            'libellePicto' : 'Autres impôts',
            'cle' : "autres impôts et taxes",
            'note' : "Les « autres impôts » couvrent certains impôts et [[taxe]]s " + \
                     "autres que les [[Impôts locaux en France|impôts locaux]].",
            'noteHtml' : "14",
            'nul' : 'aucun ' + genCodeCommon.genLien(config,
                                                     ["Impôts locaux en France",
                                                      "autre impôt"],
                                                     isWikicode, verbose)
        }
    }
    grandeursAnalyse.append([dictRecettes, produitsF, "RECETTE", couleurRecettes])

    dictSoldeF = \
    {
        'Solde de la section de fonctionnement' :
        {
            'libellePicto' : 'Résultat comptable',
            'cle' : "resultat comptable",
            'note' : "Le « solde de la section de fonctionnement » résulte de la " + \
                     "différence entre les [[Recettes publiques|recettes]] et les " + \
                     "[[Dépenses publiques|charges]] de fonctionnement.",
            'noteHtml' : "15",
            'nul' : 'solde nul'
        }
    }
    grandeursAnalyse.append([dictSoldeF, 0, "SOLDE_FONCT", couleurSolde])

    dictEmploiInvest = \
    {
        "des dépenses d'équipement" :
        {
            'libellePicto' : "Dépenses d'équipement",
            'cle' : "dont dépenses équipement",
            'note' : "Les « dépenses d’équipement » servent à financer des projets " + \
                     "d’envergure ayant pour objet d’augmenter la valeur du " + \
                     "[[Patrimoine (finance)|patrimoine]] du groupement et d’améliorer " + \
                     "la qualité des équipements municipaux, voire d’en créer de nouveaux.",
            'noteHtml' : "16",
            'nul' : "aucune dépense d'équipement"
        },
        "des " + genCodeCommon.genLien(config,
                                       ["Plan de remboursement",
                                        "remboursements"],
                                       isWikicode, verbose) + " d'emprunts" :
        {
            'libellePicto' : "Remboursements d'emprunts",
            'cle' : "remboursement emprunts et dettes assimilées",
            'note' : "Les « [[Plan de remboursement|remboursement]]s d'emprunts » " + \
                     "représentent les sommes affectées par le groupement au " + \
                     "remboursement du capital de la dette.",
            'noteHtml' : "17",
            'nul' : "aucun " + genCodeCommon.genLien(config,
                                                     ["Plan de remboursement",
                                                      "remboursement"],
                                                     isWikicode, verbose) + \
            " d'emprunt"
        }
    }
    grandeursAnalyse.append([dictEmploiInvest, emploisI,
                             "EMPLOI_INVEST", couleurEmploisInvest])

    dictRessourcesInvest = \
    {
        genCodeCommon.genLien(config, ["Emprunt (finance)", "nouvelles dettes"],
                              isWikicode, verbose) :
        {
            'libellePicto' : 'Nouvelles dettes',
            'cle' : "dont emprunts bancaires et dettes assimilées",
            'note' : "",
            'noteHtml' : '',
            'nul' : "aucune " + genCodeCommon.genLien(config,
                                                      ["Emprunt (finance)",
                                                       "nouvelles dettes"],
                                                      isWikicode, verbose)
        },
        genCodeCommon.genLien(config, ["subventions"], isWikicode, verbose) + " reçues" :
        {
            'libellePicto' : 'subventions reçues',
            'cle' : "subventions reçues",
            'note' : "",
            'noteHtml' : '',
            'nul' : "aucune " + genCodeCommon.genLien(config,
                                                      ["subventions", "subvention"],
                                                      isWikicode, verbose) + " reçue"
        },
        genCodeCommon.genLien(config, ["fonds de Compensation pour la TVA"],
                              isWikicode, verbose) :
        {
            'libellePicto' : 'fctva',
            'cle' : "fctva",
            'note' : "",
            'noteHtml' : '',
            'nul' : "aucune somme au titre des " + \
                    genCodeCommon.genLien(config,
                                          ["fonds de Compensation pour la TVA"],
                                          isWikicode, verbose)
        }
    }
    grandeursAnalyse.append([dictRessourcesInvest, ressourcesI,
                             "RESSOURCES_INVEST", couleurRessourcesInvest])

    dictCAF = \
    {
        "la " + genCodeCommon.genLien(config, ["capacité d'autofinancement"],
                                      isWikicode, verbose) + \
        " (CAF)" :
        {
            'libellePicto' : "Capacité d'autofinancement",
            'cle' : "capacité autofinancement caf",
            'note' : "",
            'noteHtml' : '',
            'nul' : "aucune " + genCodeCommon.genLien(config,
                                                      ["capacité d'autofinancement"],
                                                      isWikicode, verbose)
        }
    }
    grandeursAnalyse.append([dictCAF, 0, "CAF", couleurCAF])

    if verbose:
        print("\nSortie de defTableauxGroupementPicto")
    return grandeursAnalyse
