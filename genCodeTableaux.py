# -*- coding: utf-8 -*-
"""
*********************************************************
Module : genCodeTableaux.py
Auteur : Thierry Maillard (TMD)
Date : 24/5/2015 - 12/5/2020

Role : Transforme les donnees traitées par extractionMinFi.py
        en code pour les parties tableaux.
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

import genCodeCommon
import genWikiCodeTableaux
import genHTMLCodeTableaux
import utilitaires

def genCodeTableaux(config, dictAllGrandeur,
                    textSection,
                    listAnnees, isComplet,
                    isWikicode, verbose):
    """
        Génère le code pour les tableaux historiques sur N années
        pour une commune ou un groupement de communes donné,
        dictAllGrandeur contient toutes les donnes pour ce groupement
        pour les mot clé de de comparaison des données
        sur différentes années du modèle.
        Le texte du modèle en entrée est fourni dans la chaine textSection.
        Le type de sortie peut être du Wikicode ou du HTML.
        Le texte résultat est retourné à l'appelant.
    """
    if verbose:
        print("Entrée dans genCodeTableaux")

    nbAnneesTableau = min(int(config.get('GenWIkiCode', 'gen.nbLignesTableauxEuros')),
                          len(listAnnees))
    textSection = textSection.replace("<ANNEE-N>", str(listAnnees[nbAnneesTableau-1]))

    # https://fr.wikipedia.org/wiki/Aide:Couleurs
    couleurTaxeHabitation = config.get('Tableaux', 'tableaux.couleurTaxeHabitation')
    couleurTaxeFonciereBati = config.get('Tableaux', 'tableaux.couleurTaxeFonciereBati')
    couleurTaxeFonciereNonBati = config.get('Tableaux', 'tableaux.couleurTaxeFonciereNonBati')
    couleurStrate = config.get('Tableaux', 'tableaux.couleurStrate')
    couleurTitres = config.get('Tableaux', 'tableaux.couleurTitres')
    couleurSolde = config.get('Tableaux', 'tableaux.couleurSolde')
    couleurRecettes = config.get('Tableaux', 'tableaux.couleurRecettes')
    couleurCharges = config.get('Tableaux', 'tableaux.couleurCharges')
    couleurDettesCAF = config.get('Tableaux', 'tableaux.couleurDettesCAF')
    couleurEmploisInvest = config.get('Tableaux', 'tableaux.couleurEmploisInvest')
    couleurRessourcesInvest = config.get('Tableaux', 'tableaux.couleurRessourcesInvest')

    listeTableaux = list()
    # V1.0.5 : Précision investissement : ajout 2 lignes
    tableauPrincipal = \
        {
            'nomTableau' : "PRINCIPAL",
            'listLigne' :
                [
                    ["total des produits de fonctionnement",
                     genCodeCommon.genLien(config, ["Recettes publiques",
                                                    "Produits de fonctionnement"],
                                           isWikicode, verbose),
                     couleurRecettes],

                    ["total des charges de fonctionnement",
                     genCodeCommon.genLien(config, ["Dépenses publiques",
                                                    "Charges de fonctionnement"],
                                           isWikicode, verbose),
                     couleurCharges],
                    ["resultat comptable",
                     genCodeCommon.genLien(config, ["Résultat fiscal en France",
                                                    "Solde de la section de fonctionnement"],
                                           isWikicode, verbose),
                     couleurSolde],
                    ["total des emplois investissement",
                     genCodeCommon.genLien(config, ["Investissement",
                                                    "Emplois d'investissement"],
                                           isWikicode, verbose),
                     couleurEmploisInvest],
                    ["total des ressources d'investissement",
                     genCodeCommon.genLien(config, ["Investissement",
                                                    "Ressources d'investissement"],
                                           isWikicode, verbose),
                     couleurRessourcesInvest],
                    ["besoin ou capacité de financement de la section investissement",
                     genCodeCommon.genLien(config,
                                           ["Résultat fiscal en France",
                                            "Solde de la section d'investissement"],
                                           isWikicode, verbose),
                     couleurSolde],
                ]
        }
    listeTableaux.append(tableauPrincipal)

    tableauDetteCAF = \
        {
            'nomTableau' : "DETTE_CAF",
            'listLigne' :
                [
                    ["encours de la dette au 31 12 n",
                     genCodeCommon.genLien(config, ["Encours"], isWikicode, verbose) + \
                     " de la " + genCodeCommon.genLien(config, ["Emprunt (finance)",
                                                                "dette"],
                                                       isWikicode, verbose) + \
                     " au 31 décembre de l'année",
                     couleurDettesCAF],
                    ["capacité autofinancement caf",
                     genCodeCommon.genLien(config,
                                           ["Capacité d'autofinancement"],
                                           isWikicode,
                                           verbose) + " (CAF)",
                     couleurDettesCAF]
                ]
        }
    listeTableaux.append(tableauDetteCAF)

    tableauProduitsCharges = \
        {
            'nomTableau' : "PRODUITS_CHARGES",
            'listLigne' :
                [
                    ["dont impôts locaux",
                     "Impôts Locaux",
                     couleurRecettes],
                    ["autres impôts et taxes",
                     "autres impôts et taxes",
                     couleurRecettes],
                    ["dotation globale de fonctionnement",
                     "DGF",
                     couleurRecettes],
                    ["dont charges de personnel",
                     "Charges de personnel",
                     couleurCharges],
                    ["achats et charges externes",
                     "achats et charges externes",
                     couleurCharges],
                    ["charges financières",
                     "charges financières",
                     couleurCharges],
                    ["subventions versées",
                     "subventions versées",
                     couleurCharges]
                ]
        }
    listeTableaux.append(tableauProduitsCharges)

    tableauInvest = \
        {
            'nomTableau' : "INVEST",
            'listLigne' :
                [
                    ["dont dépenses équipement",
                     genCodeCommon.genLien(config, ["Dépenses publiques",
                                                    "Dépenses"],
                                           isWikicode, verbose) + " d'équipement",
                     couleurRecettes],
                    ["remboursement emprunts et dettes assimilées",
                     genCodeCommon.genLien(config, ["Plan de remboursement",
                                                    "Remboursements"],
                                           isWikicode, verbose) + \
                     " " + genCodeCommon.genLien(config, ["Emprunt (finance)",
                                                          "emprunts"],
                                                 isWikicode, verbose),
                     couleurRecettes],
                    ["dont emprunts bancaires et dettes assimilées",
                     "Nouvelles " + genCodeCommon.genLien(config, ["Emprunt (finance)",
                                                                   "dettes"],
                                                          isWikicode, verbose),
                     couleurCharges],
                ]
        }
    listeTableaux.append(tableauInvest)

    # Generation des tableaux et remplacement des mot-clés TABLEAU_
    for tableau in listeTableaux:
        if verbose:
            print("\n************************************")
            print("tableau :", tableau['nomTableau'])
            print("************************************")

        if isWikicode:
            tableauWiki = \
                genWikiCodeTableaux.genereTableau(tableau['nomTableau'],
                                                  listAnnees, nbAnneesTableau,
                                                  tableau['listLigne'],
                                                  dictAllGrandeur,
                                                  couleurTitres, couleurStrate,
                                                  isComplet, verbose)
        else:
            tableauWiki = \
                genHTMLCodeTableaux.genereTableau(tableau['nomTableau'],
                                                  listAnnees, nbAnneesTableau,
                                                  tableau['listLigne'],
                                                  dictAllGrandeur,
                                                  couleurTitres, couleurStrate,
                                                  isComplet, verbose)
        textSection = textSection.replace("<TABLEAU_" + tableau['nomTableau'] + ">",
                                          tableauWiki)

    # Generation du tableau des taux des taxes
    nbAnneesTableau = min(int(config.get('GenWIkiCode', 'gen.nbLignesTableauxTaux')),
                          len(listAnnees))
    textSection = textSection.replace("<ANNEE-N_TAUX>",
                                      str(listAnnees[nbAnneesTableau-1]))
    tableauTaxes = \
        {
            'nomTableau' : "TAXES",
            'listLigne' :
                [
                    ["taux taxe habitation",
                     "taux taxe d'habitation",
                     couleurTaxeHabitation],
                    ["taux taxe foncière bâti",
                     "taux foncier bâti",
                     couleurTaxeFonciereBati],
                    ["taux taxe foncière non bâti",
                     "taux foncier non bâti",
                     couleurTaxeFonciereNonBati],
                ]
        }
    if verbose:
        print("\n************************************")
        print("tableau :", tableauTaxes['nomTableau'])
        print("************************************")

    if isWikicode:
        tableauWiki = \
                genWikiCodeTableaux.genereTableauTaux(tableauTaxes['nomTableau'],
                                                      listAnnees, nbAnneesTableau,
                                                      tableauTaxes['listLigne'],
                                                      dictAllGrandeur,
                                                      couleurTitres, couleurStrate,
                                                      isComplet, verbose)
    else:
        tableauWiki = \
                genHTMLCodeTableaux.genereTableauTaux(tableauTaxes['nomTableau'],
                                                      listAnnees, nbAnneesTableau,
                                                      tableauTaxes['listLigne'],
                                                      dictAllGrandeur,
                                                      couleurTitres, couleurStrate,
                                                      isComplet, verbose)
    textSection = textSection.replace("<TABLEAU_" + tableauTaxes['nomTableau'] + ">",
                                      tableauWiki)

    if verbose:
        print("Sortie de genCodeTableaux")
    return textSection

def defTableauxPicto(config, dictAllGrandeur, listAnnees,
                     isWikicode, verbose):
    """
    Définition du contenu des tableaux picto spécifiques aux communes
    Retourne la structure grandeursAnalyse qui contient toutes les infos
    """
    if verbose:
        print("Entrée dans defTableauxPicto")

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

    # Pour comparaison valeur par habitant / Strate des données de l'année la plus récente
    grandeursAnalyse = []
    dictCharges = \
    {
        'des ' + genCodeCommon.genLien(config, ["Charge (comptabilité)",
                                                "charges"],
                                       isWikicode, verbose) + ' de personnels' :
        {
            'libellePicto' : 'Charges de personnels',
            'cle' : "dont charges de personnel",
            'note' : "Les « charges de personnel » regroupent les frais " + \
                     "de [[rémunération]] des employés.",
            'noteHtml' : "7",
            'nul' : 'aucune ' + genCodeCommon.genLien(config, ["Charge (comptabilité)",
                                                               "charges"],
                                                      isWikicode, verbose) + ' de personnel'
        },
        'des ' + genCodeCommon.genLien(config, ["achats"],
                                       isWikicode, verbose) + \
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
            'nul' : 'aucun ' + genCodeCommon.genLien(config, ["achats",
                                                              "achat"],
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
                     "[[Conseil municipal (France)|conseil municipal]].",
            'noteHtml' : "10",
            'nul' : 'aucune ' + genCodeCommon.genLien(config, ["subvention"],
                                                      isWikicode, verbose) + \
            ' versée'
        },
        'des contingents' :
        {
            'libellePicto' : 'contingents',
            'cle' : "contingents",
            'note' : "Les « contingents » représentent des participations " + \
                     "obligatoires au financement de services " + \
                     "départementaux, notamment aux [[Pompier|sapeurs-pompiers]] " + \
                     "du département.",
            'noteHtml' : "11",
            'nul' : 'aucun contingent versé'
        }
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
                                       ["Impôts locaux en France",
                                        "autres impôts"],
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
                     "[[Patrimoine (finance)|patrimoine]] de la commune et d’améliorer " + \
                     "la qualité des équipements municipaux, voire d’en créer de nouveaux.",
            'noteHtml' : "16",
            'nul' : "aucune dépense d'équipement"
        },
        "des " + genCodeCommon.genLien(config, ["Plan de remboursement",
                                                "remboursements"],
                                       isWikicode, verbose) + " d'emprunts" :
        {
            'libellePicto' : "Remboursements d'emprunts",
            'cle' : "remboursement emprunts et dettes assimilées",
            'note' : "Les « [[Plan de remboursement|remboursement]]s d'emprunts » " + \
                     "représentent les sommes affectées par la commune au " + \
                     "remboursement du capital de la dette.",
            'noteHtml' : "17",
            'nul' : "aucun " + genCodeCommon.genLien(config,
                                                     ["Plan de remboursement",
                                                      "remboursement"],
                                                     isWikicode, verbose) + " d'emprunt"
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
        genCodeCommon.genLien(config, ["subventions"],
                              isWikicode, verbose) + " reçues" :
        {
            'libellePicto' : 'subventions reçues',
            'cle' : "subventions reçues",
            'note' : "",
            'noteHtml' : '',
            'nul' : "aucune " + genCodeCommon.genLien(config, ["subventions",
                                                               "subvention"],
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
                    genCodeCommon.genLien(config, ["fonds de Compensation pour la TVA"],
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
        print("\nSortie de defTableauxPicto")
    return grandeursAnalyse
