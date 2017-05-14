# -*- coding: utf-8 -*-
"""
*********************************************************
Module : genCodeTableaux.py
Auteur : Thierry Maillard (TMD)
Date : 24/5/2015 - 20/12/2016

Role : Transforme les donnees traitées par extractionMinFi.py
        en code pour les parties tableaux.
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
    
Modif :
- 20/12/2016 : Manque une espace avant "par habitant, ratio"
*********************************************************
"""
import operator
import random

import genWikiCodeTableaux
import genHTMLCodeTableaux
import utilitaires

def genCodeTableaux(config, textSection, ville,
                    listAnnees, isComplet,
                    isWikicode, verbose):
    """ Génère le code pour les tableaux historiques sur N années """
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
                    ["TOTAL DES PRODUITS DE FONCTIONNEMENT",
                     genLien(config, ["Recettes publiques", "Produits de fonctionnement"],
                             isWikicode, verbose),
                     couleurRecettes],
                    ["TOTAL DES CHARGES DE FONCTIONNEMENT",
                     genLien(config, ["Dépenses publiques", "Charges de fonctionnement"],
                             isWikicode, verbose),
                     couleurCharges],
                    ["RESULTAT COMPTABLE",
                     genLien(config, ["Résultat fiscal en France",
                                      "Solde de la section de fonctionnement"],
                             isWikicode, verbose),
                     couleurSolde],
                    ["TOTAL DES EMPLOIS D'INVESTISSEMENT",
                     genLien(config, ["Investissement", "Emplois d'investissement"],
                             isWikicode, verbose),
                     couleurEmploisInvest],
                    ["TOTAL DES RESSOURCES D'INVESTISSEMENT",
                     genLien(config, ["Investissement", "Ressources d'investissement"],
                             isWikicode, verbose),
                     couleurRessourcesInvest],
                    ["Besoin ou capacité de financement de la section d'investissement",
                     genLien(config, ["Résultat fiscal en France",
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
                    ["Encours de la dette au 31/12/N",
                     genLien(config, ["Encours"], isWikicode, verbose) + \
                     " de la " + genLien(config, ["Emprunt (finance)", "dette"],
                                         isWikicode, verbose) + \
                     " au 31 décembre de l'année",
                     couleurDettesCAF],
                    ["Capacité d'autofinancement = CAF",
                     genLien(config, ["Capacité d'autofinancement"], isWikicode, verbose) + \
                     " (CAF)",
                     couleurDettesCAF]
                ]
        }
    listeTableaux.append(tableauDetteCAF)

    tableauProduitsCharges = \
        {
            'nomTableau' : "PRODUITS_CHARGES",
            'listLigne' :
                [
                    ["dont : Impôts Locaux",
                     "Impôts Locaux",
                     couleurRecettes],
                    ["Autres impôts et taxes",
                     "Autres impôts et taxes",
                     couleurRecettes],
                    ["Dotation globale de fonctionnement",
                     "DGF",
                     couleurRecettes],
                    ["dont : Charges de personnel",
                     "Charges de personnel",
                     couleurCharges],
                    ["Achats et charges externes",
                     "Achats et charges externes",
                     couleurCharges],
                    ["Charges financières",
                     "Charges financières",
                     couleurCharges],
                    ["Subventions versées",
                     "Subventions versées",
                     couleurCharges]
                ]
        }
    listeTableaux.append(tableauProduitsCharges)

    tableauInvest = \
        {
            'nomTableau' : "INVEST",
            'listLigne' :
                [
                    ["dont : Dépenses d'équipement",
                     genLien(config, ["Dépenses publiques", "Dépenses"],
                             isWikicode, verbose) + " d'équipement",
                     couleurRecettes],
                    ["Remboursement d'emprunts et dettes assimilées",
                     genLien(config, ["Plan de remboursement", "Remboursements"],
                             isWikicode, verbose) + \
                     " " + genLien(config, ["Emprunt (finance)", "emprunts"],
                                   isWikicode, verbose),
                     couleurRecettes],
                    ["dont : Emprunts bancaires et dettes assimilées",
                     "Nouvelles " + genLien(config, ["Emprunt (finance)", "dettes"],
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
                genWikiCodeTableaux.GenereTableau(tableau['nomTableau'],
                                                  ville, listAnnees, nbAnneesTableau,
                                                  tableau['listLigne'], couleurTitres,
                                                  couleurStrate, isComplet, verbose)
        else:
            tableauWiki = \
                genHTMLCodeTableaux.GenereTableau(ville, listAnnees, nbAnneesTableau,
                                                  tableau['listLigne'], couleurTitres,
                                                  couleurStrate, isComplet, verbose)
        textSection = textSection.replace("<TABLEAU_" + tableau['nomTableau'] + ">",
                                          tableauWiki)

    # Generation du tableau des taxes
    nbAnneesTableau = min(int(config.get('GenWIkiCode', 'gen.nbLignesTableauxTaux')),
                          len(listAnnees))
    textSection = textSection.replace("<ANNEE-N_TAUX>", str(listAnnees[nbAnneesTableau-1]))
    tableauTaxes = \
        {
            'nomTableau' : "TAXES",
            'listLigne' :
                [
                    ["Taux Taxe d'habitation",
                     "Taux taxe d'habitation",
                     couleurTaxeHabitation],
                    ["Taux Taxe foncière bâti",
                     "Taux foncier bâti",
                     couleurTaxeFonciereBati],
                    ["Taux Taxe foncière non bâti",
                     "Taux foncier non bâti",
                     couleurTaxeFonciereNonBati],
                ]
        }
    if verbose:
        print("\n************************************")
        print("tableau :", tableauTaxes['nomTableau'])
        print("************************************")

    if isWikicode:
        tableauWiki = \
                genWikiCodeTableaux.GenereTableauTaux(tableauTaxes['nomTableau'],
                                                      ville, listAnnees, nbAnneesTableau,
                                                      tableauTaxes['listLigne'],
                                                      couleurTitres, couleurStrate,
                                                      isComplet, verbose)
    else:
        tableauWiki = \
                genHTMLCodeTableaux.GenereTableauTaux(ville, listAnnees, nbAnneesTableau,
                                                      tableauTaxes['listLigne'],
                                                      couleurTitres, couleurStrate,
                                                      isComplet, verbose)
    textSection = textSection.replace("<TABLEAU_" + tableauTaxes['nomTableau'] + ">",
                                      tableauWiki)

    if verbose:
        print("Sortie de genCodeTableaux")
    return textSection

def genLien(config, defLien, isWikicode, verbose):
    """ Génère un lien Wikicode ou HTML """
    if verbose:
        print("Entrée dans genLien")
        print("defLien =", defLien, ", isWikicode =", isWikicode)

    assert len(defLien) in [1, 2]

    if isWikicode:
        lien = '[[' + defLien[0]
        if len(defLien) == 2:
            lien += '|' + defLien[1]
        lien += ']]'
    else:
        alias = defLien[-1]
        lien = '<a href="' + config.get('Extraction', 'extraction.wikipediafrBaseUrl') + \
               defLien[0] + '" target="_blank">' + alias + '</a>'

    if verbose:
        print("Lien : ", lien)
        print("Sortie de genLien")
    return lien

def genCodeTableauxPicto(config, textSection, ville, listAnnees, isComplet,
                         isWikicode, verbose):
    """
    Génère le Wikicode pour un tableau de pitogramme de comparaison
    année N et N-1
    """
    if verbose:
        print("Entrée dans genWikiCodeTableauxPicto")

    couleurSolde = config.get('Tableaux', 'tableaux.couleurSolde')
    couleurRecettes = config.get('Tableaux', 'tableaux.couleurRecettes')
    couleurCharges = config.get('Tableaux', 'tableaux.couleurCharges')
    couleurDettesCAF = config.get('Tableaux', 'tableaux.couleurDettesCAF')
    couleurCAF = config.get('Tableaux', 'tableaux.couleurCAF')
    couleurEmploisInvest = config.get('Tableaux', 'tableaux.couleurEmploisInvest')
    couleurRessourcesInvest = config.get('Tableaux', 'tableaux.couleurRessourcesInvest')
    couleurTaxes = config.get('Tableaux', 'tableaux.couleurTaxes')

    chargesF = int(utilitaires.getValeur(ville, 'TOTAL DES CHARGES DE FONCTIONNEMENT',
                                         listAnnees[0], "Valeur totale"))
    emploisI = int(utilitaires.getValeur(ville, "TOTAL DES EMPLOIS D'INVESTISSEMENT",
                                         listAnnees[0], "Valeur totale"))
    produitsF = int(utilitaires.getValeur(ville, 'TOTAL DES PRODUITS DE FONCTIONNEMENT',
                                          listAnnees[0], "Valeur totale"))
    ressourcesI = int(utilitaires.getValeur(ville, "TOTAL DES RESSOURCES D'INVESTISSEMENT",
                                            listAnnees[0], "Valeur totale"))

    # Pour comparaison valeur par habitant / Strate des données de l'année la plus récente
    grandeursAnalyse = []
    dictCharges = \
    {
        'des ' + genLien(config, ["Charge (comptabilité)", "charges"],
                         isWikicode, verbose) + ' de personnels' :
        {
            'libellePicto' : 'Charges de personnels',
            'cle' : "dont : Charges de personnel",
            'note' : "Les « charges de personnel » regroupent les frais " + \
                     "de [[rémunération]] des employés par la commune.",
            'noteHtml' : "7",
            'nul' : 'aucune ' + genLien(config, ["Charge (comptabilité)", "charges"],
                                        isWikicode, verbose) + ' de personnel'
        },
        'des ' + genLien(config, ["achats"], isWikicode, verbose) + \
        ' et charges externes' :
        {
            'libellePicto' : 'Achats et charges ext.',
            'cle' : "Achats et charges externes",
            'note' : "Le poste « achats et charges externes » regroupe " + \
                     "les achats non stockés de matières et fournitures " + \
                     "([[Eau potable|eau]], [[énergie]]...), le petit matériel, " +\
                     "les achats de [[Crédit-bail|crédits-bails]], " + \
                     "les [[location]]s, [[Prime d'assurance|primes d'assurances]]...",
            'noteHtml' : "8",
            'nul' : 'aucun ' + genLien(config, ["achats", "achat"],
                                       isWikicode, verbose) + ' ou charge externe'
        },
        'des charges financières' :
        {
            'libellePicto' : 'Charges financières',
            'cle' : "Charges financières",
            'note' : "Les « charges financières » correspondent à la rémunération " + \
                         "des ressources d'[[Emprunt (finance)|emprunt]].",
            'noteHtml' : "9",
            'nul' : 'aucune charge financière'
        },
        'des ' + genLien(config, ["subventions"], isWikicode, verbose) + \
        ' versées' :
        {
            'libellePicto' : 'Subventions versées',
            'cle' : "Subventions versées",
            'note' : "Les « subventions versées » rassemblent l'ensemble " + \
                     "des [[subvention]]s à des associations votées par le " + \
                     "[[Conseil municipal (France)|conseil municipal]].",
            'noteHtml' : "10",
            'nul' : 'aucune ' + genLien(config, ["subvention"],
                                        isWikicode, verbose) + ' versée'
        },
        'des contingents' :
        {
            'libellePicto' : 'Contingents',
            'cle' : "Contingents",
            'note' : "Les « contingents » représentent des participations " + \
                     "obligatoires d'une commune au financement de services " + \
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
            'cle' : 'Encours de la dette au 31/12/N',
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
            'libellePicto' : 'Annuité de la dette',
            'cle' : "Annuité de la dette",
            'note' : "",
            'noteHtml' : '',
            'nul' : 'aucune annuité pour la dette'
        }
    }
    grandeursAnalyse.append([dictAnnuiteDette, 0, "ANNUITE_DETTE", couleurDettesCAF])

    #Recettes
    dictRecettes = \
    {
        'des ' + genLien(config, ["Impôts locaux en France", "impôts locaux"],
                         isWikicode, verbose) :
        {
            'libellePicto' : 'Impôts locaux',
            'cle' : "dont : Impôts Locaux",
            'note' : "Les « [[Impôts locaux en France|impôts locaux]] » " +\
                    "désignent les [[impôt]]s prélevés par les " + \
                    "[[Collectivité territoriale|collectivités territoriales]] " + \
                    "comme les communes pour alimenter leur budget. Ils regroupent " + \
                    "les [[Taxe foncière|impôts fonciers]], la [[taxe d'habitation]] " + \
                    "ou encore, pour les [[entreprise]]s, les " + \
                    "[[Cotisation foncière des entreprises|cotisations foncières]] ou " + \
                    "sur la [[valeur ajoutée]].",
            'noteHtml' : "12",
            'nul' : 'aucun ' + genLien(config, ["Impôts locaux en France", "impôt local"],
                                       isWikicode, verbose)
        },
        "de la " + genLien(config, ["dotation globale de fonctionnement"],
                           isWikicode, verbose) + " (DGF)" :
        {
            'libellePicto' : 'Dotation globale de fonctionnement',
            'cle' : 'Dotation globale de fonctionnement',
            'note' : "Les « [[Finances locales en France#Dotations et subventions de " + \
                     "l'État|dotations globales de fonctionnement]] » désignent, en " + \
                     "[[France]], des concours financiers de l'[[État]] au [[budget]] " + \
                     "des [[Collectivité territoriale|collectivités territoriales]].",
            'noteHtml' : "13",
            'nul' : 'aucune somme au titre de la [[dotation globale de fonctionnement]]'
        },
        'des ' + genLien(config, ["Impôts locaux en France", "autres impôts"],
                         isWikicode, verbose) :
        {
            'libellePicto' : 'Autres impôts',
            'cle' : "Autres impôts et taxes",
            'note' : "Les « autres impôts » couvrent certains impôts et [[taxe]]s " + \
                     "autres que les [[Impôts locaux en France|impôts locaux]].",
            'noteHtml' : "14",
            'nul' : 'aucun ' + genLien(config, ["Impôts locaux en France", "autre impôt"],
                                       isWikicode, verbose)
        }
    }
    grandeursAnalyse.append([dictRecettes, produitsF, "RECETTE", couleurRecettes])

    dictSoldeF = \
    {
        'Solde de la section de fonctionnement' :
        {
            'libellePicto' : 'Résultat comptable',
            'cle' : "RESULTAT COMPTABLE",
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
            'cle' : "dont : Dépenses d'équipement",
            'note' : "Les « dépenses d’équipement » servent à financer des projets " + \
                     "d’envergure ayant pour objet d’augmenter la valeur du " + \
                     "[[Patrimoine (finance)|patrimoine]] de la commune et d’améliorer " + \
                     "la qualité des équipements municipaux, voire d’en créer de nouveaux.",
            'noteHtml' : "16",
            'nul' : "aucune dépense d'équipement"
        },
        "des " + genLien(config, ["Plan de remboursement", "remboursements"],
                         isWikicode, verbose) + " d'emprunts" :
        {
            'libellePicto' : "Remboursements d'emprunts",
            'cle' : "Remboursement d'emprunts et dettes assimilées",
            'note' : "Les « [[Plan de remboursement|remboursement]]s d'emprunts » " + \
                     "représentent les sommes affectées par la commune au " + \
                     "remboursement du capital de la dette.",
            'noteHtml' : "17",
            'nul' : "aucun " + genLien(config, ["Plan de remboursement", "remboursement"],
                                       isWikicode, verbose) + " d'emprunt"
        }
    }
    grandeursAnalyse.append([dictEmploiInvest, emploisI,
                             "EMPLOI_INVEST", couleurEmploisInvest])

    dictRessourcesInvest = \
    {
        genLien(config, ["Emprunt (finance)", "nouvelles dettes"],
                isWikicode, verbose) :
        {
            'libellePicto' : 'Nouvelles dettes',
            'cle' : "dont : Emprunts bancaires et dettes assimilées",
            'note' : "",
            'noteHtml' : '',
            'nul' : "aucune " + genLien(config, ["Emprunt (finance)", "nouvelles dettes"],
                                        isWikicode, verbose)
        },
        genLien(config, ["subventions"], isWikicode, verbose) + " reçues" :
        {
            'libellePicto' : 'Subventions reçues',
            'cle' : "Subventions reçues",
            'note' : "",
            'noteHtml' : '',
            'nul' : "aucune " + genLien(config, ["subventions", "subvention"],
                                        isWikicode, verbose) + " reçue"
        },
        genLien(config, ["fonds de Compensation pour la TVA"], isWikicode, verbose) :
        {
            'libellePicto' : 'FCTVA',
            'cle' : "FCTVA",
            'note' : "",
            'noteHtml' : '',
            'nul' : "aucune somme au titre des " + \
                    genLien(config, ["fonds de Compensation pour la TVA"],
                            isWikicode, verbose)
        }
    }
    grandeursAnalyse.append([dictRessourcesInvest, ressourcesI,
                             "RESSOURCES_INVEST", couleurRessourcesInvest])

    dictCAF = \
    {
        "la " + genLien(config, ["capacité d'autofinancement"], isWikicode, verbose) + \
        " (CAF)" :
        {
            'libellePicto' : "Capacité d'autofinancement",
            'cle' : "Capacité d'autofinancement = CAF",
            'note' : "",
            'noteHtml' : '',
            'nul' : "aucune " + genLien(config, ["capacité d'autofinancement"],
                                        isWikicode, verbose)
        }
    }
    grandeursAnalyse.append([dictCAF, 0, "CAF", couleurCAF])

    # V1.0.0 : Generation des lignes des tableaux picto pour tous les dico définis plus haut
    # Les mots cles générés sont expansés par la suite
    for grandeurs in grandeursAnalyse:
        nbLignes = len(grandeurs[0])
        if not isComplet:
            nbLignes = min(nbLignes,
                           int(config.get('GenWIkiCode',
                                          'gen.nbLignesTableauxPictoNonComplet')))
        lignes = genlignesTableauPicto(grandeurs[2], nbLignes, grandeurs[3], "euro",
                                       isWikicode, verbose)
        textSection = textSection.replace("<GEN_LIGNES_TABLEAU_PICTO_" + grandeurs[2] + ">",
                                          "".join(lignes))

    # Recherche des valeurs, calcul des ratio et remplacement des mots clés
    for grandeurs in grandeursAnalyse:
        nbAnneesTendance = int(config.get('GenWIkiCode', 'gen.nbAnneesTendance'))
        listeAnneesTendance = sorted(listAnnees[:nbAnneesTendance])
        getValeursDict(listeAnneesTendance, ville, listAnnees[0], grandeurs[0], verbose)
        cleTriee = triPourCent(config, grandeurs[1], grandeurs[0], True, isWikicode, verbose)
        for numValeur in range(len(cleTriee)):
            text = cleTriee[numValeur]
            textSection = textSection.replace("<LIBELLE_" + grandeurs[2] + str(numValeur+1) + ">",
                                              text)
            textSection = textSection.replace("<VALEUR_" + grandeurs[2] + str(numValeur+1) +">",
                                              str(grandeurs[0][text]["Valeur totale"]))
            textSection = textSection.replace("<VALEUR_" + grandeurs[2] + "_PC" + \
                                              str(numValeur+1) +">",
                                              grandeurs[0][text]['ratioValeurStr'])
            textSection = textSection.replace("<VALEUR_" + grandeurs[2] + "_PAR_HABITANT" + \
                                              str(numValeur+1) +">",
                                              str(grandeurs[0][text]["Par habitant"]))

            # v1.0.0 : précision tendances
            textSection = textSection.replace("<VALEUR_" + grandeurs[2] + "_TENDANCE" + \
                                              str(numValeur+1) +">",
                                              grandeurs[0][text]['ratioStrateStr'])
            textSection = textSection.replace("<VALEUR_" + grandeurs[2] + "_TENDANCE_SERIE" + \
                                              str(numValeur+1) +">",
                                              grandeurs[0][text]['ratioTendanceStr'])

            textSection = textSection.replace("<VALEUR_" + grandeurs[2] + "_STRATE" + \
                                              str(numValeur+1) +">",
                                              str(grandeurs[0][text]["En moyenne pour la strate"]))
            if isWikicode:
                note = grandeurs[0][text]["note"]
            else:
                note = '<sup><a href="../../notice.html#Note_' + \
                       grandeurs[0][text]["noteHtml"] + \
                       '">Note ' + grandeurs[0][text]["noteHtml"] + '</a></sup>'
            textSection = textSection.replace("<NOTE_" + grandeurs[2] + str(numValeur+1) + ">",
                                              note)
            textSection = textSection.replace("<PICTO_" + grandeurs[2] + str(numValeur+1) + ">",
                                              grandeurs[0][text]['ratioStratePicto'])
            # V1.0.2 : Accessibilité : texte alternatif
            textSection = textSection.replace("<PICTO_ALT_" + grandeurs[2] + str(numValeur+1) + ">",
                                              grandeurs[0][text]['ratioStratePictoAlt'])
            textSection = textSection.replace("<LIBELLE_PICTO_" + grandeurs[2] + \
                                              str(numValeur+1) + ">",
                                              grandeurs[0][text]['libellePicto'])
            # V1.2.1 : Phrase complête pour éviter les problèmes en cas de valeur nulle
            if grandeurs[0][text]["Valeur totale"] == 0:
                phrase = grandeurs[0][text]["nul"]
            else:
                phrase = text
            if isWikicode and len(grandeurs[0][text]["note"].strip()) != 0:
                phrase += '<ref group="Note">' + grandeurs[0][text]["note"] + '</ref>'
            if not isWikicode and len(grandeurs[0][text]["noteHtml"].strip()) != 0:
                phrase += '<sup><a href="../../notice.html#Note_' + \
                          grandeurs[0][text]["noteHtml"] + \
                          '">Note ' + grandeurs[0][text]["noteHtml"] + '</a></sup>'
            if grandeurs[0][text]["Valeur totale"] != 0:
                phrase += " pour " + random.choice(["un montant de", "une somme de", "",
                                                    "une valeur totale de",
                                                    "une valeur de"]) + " " + \
                           utilitaires.modeleEuro(str(grandeurs[0][text]["Valeur totale"]),
                                                  isWikicode)

                # Si la somme total des valeurs du groupe est valide, on affiche le pourcentage
                if grandeurs[1] > 0:
                    phrase += " (" +  grandeurs[0][text]['ratioValeurStr'] + ")"
                if grandeurs[0][text]["Par habitant"] > 0:
                    phrase += ", soit " + \
                              utilitaires.modeleEuro(str(grandeurs[0][text]["Par habitant"]),
                                                     isWikicode)
                    phrase += " par habitant, ratio "
                else:
                    phrase += ", négligeable compte tenu du nombre d’habitants de la commune et "
                phrase += grandeurs[0][text]['ratioStrateStr']
            textSection = textSection.replace("<PHRASE_" + grandeurs[2] + str(numValeur+1) +">",
                                              phrase)

    # V1.0.0 : Generation des lignes des tableaux picto pour les taux des taxes
    # Les mots cles générés sont expansés par la suite
    listeDictTaxes = \
    [
        {
            "libelle" : "Taxe d'habitation",
            "tag" : "TAUX_TAXE_HABITATION",
            "cle" : "Taux Taxe d'habitation"
        },
        {
            "libelle" : "Taxe foncière sur le bâti",
            "tag" : "TAUX_FONCIER_BATI",
            "cle" : "Taux Taxe foncière bâti"
        },
        {
            "libelle" : "Taxe foncière sur le non bâti",
            "tag" : "FONCIER_NON_BATI",
            "cle" : "Taux Taxe foncière non bâti"
        }
    ]

    lignes = ""
    for dictTaxe in listeDictTaxes:
        lignes += genlignesTableauPicto(dictTaxe["tag"], 1, couleurTaxes, '%',
                                        isWikicode, verbose)[0]
    textSection = textSection.replace("<GEN_LIGNES_TABLEAU_PICTO_TAXES>",
                                      "".join(lignes))

    # Remplacement des mot clés produits au dessus
    # Libelles des taxes
    for dictTaxe in listeDictTaxes:
        cle = dictTaxe["cle"]
        tag = dictTaxe["tag"]
        textSection = textSection.replace("<LIBELLE_PICTO_" + tag + "1>",
                                          dictTaxe["libelle"])
        tauxTaxeVille = utilitaires.getValeurFloat(ville, cle, listAnnees[0], "Taux")
        textSection = textSection.replace("<VALEUR_" + tag + "_PAR_HABITANT1>",
                                          tauxTaxeVille)
        tauxTaxeVilleNM1 = utilitaires.getValeurFloat(ville, cle, listAnnees[1],
                                                      "Taux")
        # V1.0.4 :pas d'utilisation du modèle unité avec les pourcentages
        textSection = textSection.replace("<VALEUR_" + tag + "_PAR_HABITANT1_NM1>",
                                          tauxTaxeVilleNM1.replace('.', ','))
        tauxTaxeStrate = utilitaires.getValeurFloat(ville, cle, listAnnees[0],
                                                    "Taux moyen pour la strate")
        textSection = textSection.replace("<VALEUR_" + tag + "_STRATE1>",
                                          tauxTaxeStrate)
        ratioTaxe = utilitaires.calculAugmentation(config,
                                                   float(tauxTaxeVille),
                                                   float(tauxTaxeStrate))
        picto, alt = utilitaires.choixPicto(config, ratioTaxe, isWikicode)
        textSection = textSection.replace("<PICTO_" + tag + "1>", picto)
        textSection = textSection.replace("<PICTO_ALT_" + tag + "1>", alt)

        # Tendance annee N-1
        augmentation = utilitaires.calculeTendance(config,
                                                   float(tauxTaxeVille),
                                                   float(tauxTaxeVilleNM1))
        textSection = textSection.replace("<TENDANCE_" + tag + "_PAR_HABITANT1>",
                                          augmentation)

    legende = genLegendePicto(config, isWikicode, verbose)
    textSection = textSection.replace("<LEGENDE_ECART_TABLEAU_PICTO>", legende)

    if verbose:
        print("Sortie de genWikiCodeTableauxPicto")
    return textSection.strip()

def getValeursDict(listeAnneesTendance, ville, annee, dictValeurs, verbose):
    """ V0.8 : Recuperation groupe de valeurs pour certaines années """
    if verbose:
        print("\nEntrée dans getValeursDict")
    # Recupération des valeurs pour les clés
    for defValeur in list(dictValeurs.keys()):
        for sousCle in ["Valeur totale", "Par habitant", "En moyenne pour la strate"]:
            dictValeurs[defValeur][sousCle] = \
                int(utilitaires.getValeur(ville, dictValeurs[defValeur]['cle'],
                                          annee, sousCle))

        # V1.0.0 : Preparation données pour calcul tendance
        dictAneeesValeur = dict()
        for annee in listeAnneesTendance:
            dictAneeesValeur[str(annee)] = \
                int(utilitaires.getValeur(ville, dictValeurs[defValeur]['cle'],
                                          annee, "Par habitant"))
        dictValeurs[defValeur]['dictAneeesValeur'] = dictAneeesValeur
    if verbose:
        print("dictAneeesValeur =", dictAneeesValeur)
        print("\nSortie de getValeursDict")

# V0.8 : Classemement de grandeurs et stat
def triPourCent(config, sommeValeurTotal, dictValeurs, avecTendance, isWikicode, verbose):
    """
    Classemement de grandeurs et stat
    Entree :  valeur totale, dictionnaire des valeurs à compléter
    Sortie : Liste ordonnée par valeur décroissante des cles du dictionnaire
    """
    if verbose:
        print("\nEntrée dans triPourCent")

    seuilValeurPourCentDifferente = \
        float(config.get('GenCode', 'gen.seuilValeurPourCentDifferente'))

    # Par convention si sommeValeurTotal <= 0, on prend 1 pour éviter div0
    if sommeValeurTotal <= 0:
        sommeValeurTotal = 1

    # Calcul des ratios Valeur / sommeValeurTotal
    # Calcul des ratio comparatifs par rapport aux strates
    if isWikicode:
        espacePc = ' '
    else:
        espacePc = '&nbsp;'

    for defValeur in list(dictValeurs.keys()):
        dictValeurs[defValeur]['ratioValeur'] = \
            (float(dictValeurs[defValeur]["Valeur totale"]) * 100.0) / \
             float(sommeValeurTotal)
        if dictValeurs[defValeur]['ratioValeur'] < 1.0:
            faibleStr = random.choice(["inférieures à 1"+ espacePc + "%",
                                       " plus faibles", "négligeables"])
            dictValeurs[defValeur]['ratioValeurStr'] = "des sommes " + faibleStr
        else:
            dictValeurs[defValeur]['ratioValeurStr'] = \
                "%1.f"%dictValeurs[defValeur]['ratioValeur'] + espacePc + "%"

        # Ratio strates
        moyStrate = float(dictValeurs[defValeur]["En moyenne pour la strate"])
        ratioStrate = \
            utilitaires.calculAugmentation(config,
                                           float(dictValeurs[defValeur]["Par habitant"]),
                                           moyStrate)
        dictValeurs[defValeur]['ratioStrate'] = ratioStrate
        if abs(ratioStrate) <= seuilValeurPourCentDifferente:
            dictValeurs[defValeur]['ratioStrateStr'] = \
                "voisin de la valeur moyenne de la strate"
        else:
            if ratioStrate < seuilValeurPourCentDifferente:
                dictValeurs[defValeur]['ratioStrateStr'] = "inférieur"
            else:
                dictValeurs[defValeur]['ratioStrateStr'] = "supérieur"
            if dictValeurs[defValeur]["Par habitant"] != 0: # Si 0 pourcentage sans signification
                dictValeurs[defValeur]['ratioStrateStr'] += \
                    " de %1.f %%"%abs(dictValeurs[defValeur]['ratioStrate'])
            dictValeurs[defValeur]['ratioStrateStr'] += \
                " à la valeur moyenne pour les communes de la même strate (" + \
                utilitaires.modeleEuro(str(dictValeurs[defValeur]["En moyenne pour la strate"]),
                                       isWikicode)
            dictValeurs[defValeur]['ratioStrateStr'] += " par habitant)"

        # v1.0.0 : tendance des séries sur les derniéres années
        if avecTendance:
            dictAneeesValeur = dictValeurs[defValeur]['dictAneeesValeur']
            dictValeurs[defValeur]['ratioTendanceStr'] = \
                utilitaires.calculeTendanceSerieStr('ce ratio', dictAneeesValeur,
                                                    'par habitant',
                                                    isWikicode, verbose)

        picto, alt = utilitaires.choixPicto(config, ratioStrate, isWikicode)
        dictValeurs[defValeur]['ratioStratePicto'] = picto
        dictValeurs[defValeur]['ratioStratePictoAlt'] = alt

    # tri des cles par importance decroissante
    dictCleValeur = dict()
    for defValeur in list(dictValeurs.keys()):
        dictCleValeur[defValeur] = dictValeurs[defValeur]["Valeur totale"]
    cleTriee = [e[0] for e in sorted(list(dictCleValeur.items()),
                                     key=operator.itemgetter(1), reverse=True)]

    if verbose:
        print("cleTriee=", cleTriee)
        print("dictValeurs=", dictValeurs)
        print("\nSortie de triPourCent")
    return cleTriee

# V1.0.0 : Le modèle table est remplacé par la syntaxe de base des tableaux Wiki
# car il ne gère pas l'alignement à droite des nombres à l'intérieur des cellules
def genlignesTableauPicto(motCle, nbLignes, couleur, unite,
                          isWikicode, verbose):
    """ Genere nbLignes du tableau des pictogrammes avec mot-clés à expanser plus tard """
    if verbose:
        print("\nEntrée dans genlignesTableauPicto")
        print("motCle=", motCle)
        print("nbLignes=", nbLignes)
        print("couleur=", couleur)

    lignes = list()
    for numLigne in range(1, nbLignes+1):
        if isWikicode:
            ligne = ' |----\n'
            ligne += ' ! scope="row" style="background-color: ' + couleur + '" | ' + \
                     '<LIBELLE_PICTO_' + motCle + str(numLigne) + '>\n'
        else:
            ligne = '    <tr>\n'
            ligne += '      <td align="left" bgcolor="' + couleur + '">' + \
                     '<LIBELLE_PICTO_' + motCle + str(numLigne) +'></td>\n'

        for champ in ['_PAR_HABITANT', '_STRATE']:
            valeur = '<VALEUR_' + motCle + champ + str(numLigne) + '>'
            if isWikicode:
                ligne += ' | style="text-align:right;background-color: ' + couleur + '"' + ' | '
            else:
                ligne += '      <td align="right" bgcolor="' + couleur + '">'
            if isWikicode and unite == "%":
                ligne += '{{unité|' + valeur + '}}'
            elif not isWikicode and unite == "%":
                ligne += valeur
            else:
                ligne += utilitaires.modeleEuro(valeur, isWikicode)
            if not isWikicode:
                ligne += '</td>'
            ligne += '\n'

        if isWikicode:
            # V1.0.2 : Accessibilité : texte alternatif
            ligne += ' | style="text-align:right;background-color:' + couleur + \
                     ' " | [[fichier:<PICTO_' + motCle + str(numLigne) + '>|10px|alt=' + \
                     '<PICTO_ALT_' + motCle + str(numLigne) + '>|link=]]\n'
        else:
            ligne += '      <td align="right" bgcolor="' + couleur + '">' + \
                     '<img alt="<PICTO_ALT_' + motCle + str(numLigne) + '>"' + \
                     ' src="<PICTO_' + motCle + str(numLigne) + '>">\n'

        if not isWikicode:
            ligne += '    </tr>\n'

        lignes.append(ligne)
        numLigne += 1

    if verbose:
        print("Sortie de genlignesTableauPicto")
        print("lignes", lignes)
    return lignes

def genLegendePicto(config, isWikicode, verbose):
    """
    V1.0.0 : Generation de la légende du tableau (Wikicode)
    V1.0.2 : Accessibilité : texte alternatif
    V2.1.0 : Légende en HTML
    """
    if verbose:
        print("\nEntrée dans genLegendePicto")

    seuilValeurPourCentDifferente = config.get('GenCode', 'gen.seuilValeurPourCentDifferente')
    seuilValeurPourCentgrande = config.get('GenCode', 'gen.seuilValeurPourCentgrande')
    seuilMoyen = (float(seuilValeurPourCentgrande) + float(seuilValeurPourCentDifferente)) / 2.0
    seuilFort = float(seuilValeurPourCentgrande) * 2.0
    ecartNul, ecartNulAlt = utilitaires.choixPicto(config, 0.0, isWikicode)
    ecartMoyen, ecartMoyenAlt = utilitaires.choixPicto(config, seuilMoyen, isWikicode)
    ecartFort, ecartFortAlt = utilitaires.choixPicto(config, seuilFort, isWikicode)

    if isWikicode:
        legende = "[[fichier:" + ecartNul + "|10px|alt=" + \
                    ecartNulAlt + "|link=]] "
        legende += "de 0 à " + seuilValeurPourCentDifferente + \
               " % ; "
        legende += "[[fichier:" + ecartMoyen + "|10px|alt=" + \
                ecartMoyenAlt + "|link=]] de "
        legende += seuilValeurPourCentDifferente + \
               " à " + seuilValeurPourCentgrande + " % ; "
        legende += "[[fichier:" + ecartFort + "|10px|alt=" + \
                ecartFortAlt + "|link=]] "
        legende += "supérieur à " + seuilValeurPourCentgrande + \
                   " %"
    else:
        legende = '<tr><td align="center" colspan="4">'
        legende += 'Êcart : <img alt="' + ecartNulAlt + '" src="' + ecartNul + '">'
        legende += ' de 0 à ' + seuilValeurPourCentDifferente + ' % ; '
        legende += '<img alt="' + ecartMoyenAlt + '" src="' + ecartMoyen + '">'
        legende += ' de ' + seuilValeurPourCentDifferente
        legende += ' à ' + seuilValeurPourCentgrande + ' % ; '
        legende += '<img alt="' + ecartFortAlt + '" src="' + ecartFort + '">'
        legende += ' supérieur à ' + seuilValeurPourCentgrande + ' %'
        legende += '</td></tr>'

    if verbose:
        print("legende=", legende)
        print("\nSortie de genLegendePicto")
    return legende
