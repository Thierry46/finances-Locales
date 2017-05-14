# -*- coding: utf-8 -*-
"""
*********************************************************
Module : genWikiCodeTableaux.py
Auteur : Thierry Maillard (TMD)
Date : 24/5/2015 - 3/6/2015

Role : Transforme les donnees traitées par extractionMinFi.py
        en wikicode pour les partie tableaux.
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
import operator
import random

import utilitaires

def genWikiCodeTableaux(config, textSection, ville,
                        listAnnees, isComplet, verbose):
    """ Génère le Wikicode pour les tableaux historiques sur N années """
    if verbose:
        print("Entrée dans genWikiCodeTableaux")

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
                     "[[Recettes publiques|Produits de fonctionnement]]",
                     couleurRecettes],
                    ["TOTAL DES CHARGES DE FONCTIONNEMENT",
                     "[[Dépenses publiques|Charges de fonctionnement]]",
                     couleurCharges],
                    ["RESULTAT COMPTABLE",
                     "[[Résultat fiscal en France|Solde de la section de fonctionnement]]",
                     couleurSolde],
                    ["TOTAL DES EMPLOIS D'INVESTISSEMENT",
                     "[[Investissement|Emplois d'investissement]]",
                     couleurEmploisInvest],
                    ["TOTAL DES RESSOURCES D'INVESTISSEMENT",
                     "[[Investissement|Ressources d'investissement]]",
                     couleurRessourcesInvest],
                    ["Besoin ou capacité de financement de la section d'investissement",
                     "[[Résultat fiscal en France|Solde de la section d'investissement]]",
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
                     "[[Encours]] de la [[Emprunt (finance)|dette]] au 31 décembre de l'année",
                     couleurDettesCAF],
                    ["Capacité d'autofinancement = CAF",
                     "[[Capacité d'autofinancement]] (CAF)",
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
                     "[[Dépenses publiques|Dépenses]] d'équipement",
                     couleurRecettes],
                    ["Remboursement d'emprunts et dettes assimilées",
                     "[[Plan de remboursement|Remboursement]]s [[Emprunt (finance)|emprunt]]s",
                     couleurRecettes],
                    ["dont : Emprunts bancaires et dettes assimilées",
                     'Nouvelles [[Emprunt (finance)|dette]]s',
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
        tableauWiki = GenereTableau(tableau['nomTableau'], ville, listAnnees, nbAnneesTableau,
                                    tableau['listLigne'], couleurTitres, couleurStrate,
                                    isComplet, verbose)
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
    tableauWiki = GenereTableauTaux(tableauTaxes['nomTableau'], ville, listAnnees, nbAnneesTableau,
                                    tableauTaxes['listLigne'], couleurTitres,
                                    couleurStrate, isComplet, verbose)
    textSection = textSection.replace("<TABLEAU_" + tableauTaxes['nomTableau'] + ">",
                                      tableauWiki)

    if verbose:
        print("Sortie de genWikiCodeTableaux")
    return textSection

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

def genWikiCodeTableauxPicto(config, textSection, ville, listAnnees, isComplet, verbose):
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
        'des [[Charge (comptabilité)|charge]]s de personnels' :
        {
            'libellePicto' : 'Charges de personnels',
            'cle' : "dont : Charges de personnel",
            'note' : "Les « charges de personnel » regroupent les frais " + \
                     "de [[rémunération]] des employés par la commune.",
            'nul' : 'aucune [[Charge (comptabilité)|charge]] de personnel'
        },
        'des [[achats]] et charges externes' :
        {
            'libellePicto' : 'Achats et charges ext.',
            'cle' : "Achats et charges externes",
            'note' : "Le poste « achats et charges externes » regroupe " + \
                     "les achats non stockés de matières et fournitures " + \
                     "([[Eau potable|eau]], [[énergie]]...), le petit matériel, " +\
                     "les achats de [[Crédit-bail|crédits-bails]], " + \
                     "les [[location]]s, [[Prime d'assurance|primes d'assurances]]...",
            'nul' : 'aucun [[achats|achat]] ou charge externe'
        },
        'des charges financières' :
        {
            'libellePicto' : 'Charges financières',
            'cle' : "Charges financières",
            'note' : "Les « charges financières » correspondent à la rémunération " + \
                         "des ressources d'[[Emprunt (finance)|emprunt]].",
            'nul' : 'aucune charge financière'
        },
        'des [[subvention]]s versées' :
        {
            'libellePicto' : 'Subventions versées',
            'cle' : "Subventions versées",
            'note' : " Les « subventions versées » rassemblent l'ensemble " + \
                     "des [[subvention]]s à des associations votées par le " + \
                     "[[Conseil municipal (France)|conseil municipal]].",
            'nul' : 'aucune [[subvention]] versée'
        },
        'des contingents' :
        {
            'libellePicto' : 'Contingents',
            'cle' : "Contingents",
            'note' : "Les « contingents » représentent des participations " + \
                     "obligatoires d'une commune au financement de services " + \
                     "départementaux, notamment aux [[Pompier|sapeurs-pompiers]] " + \
                     "du département.",
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
            'nul' : 'aucune annuité pour la dette'
        }
    }
    grandeursAnalyse.append([dictAnnuiteDette, 0, "ANNUITE_DETTE", couleurDettesCAF])

    #Recettes
    dictRecettes = \
    {
        'des [[Impôts locaux en France|impôts locaux]]' :
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
            'nul' : 'aucun [[Impôts locaux en France|impôt local]]'
        },
        "de la [[dotation globale de fonctionnement]] (DGF)" :
        {
            'libellePicto' : 'Dotation globale de fonctionnement',
            'cle' : 'Dotation globale de fonctionnement',
            'note' : "Les « [[Finances locales en France#Dotations et subventions de " + \
                     "l'État|dotations globales de fonctionnement]] » désignent, en " + \
                     "[[France]], des concours financiers de l'[[État]] au [[budget]] " + \
                     "des [[Collectivité territoriale|collectivités territoriales]].",
            'nul' : 'aucune somme au titre de la [[dotation globale de fonctionnement]]'
        },
        'des [[Impôts locaux en France|autres impôts]]' :
        {
            'libellePicto' : 'Autres impôts',
            'cle' : "Autres impôts et taxes",
            'note' : "Les « autres impôts » couvrent certains impôts et [[taxe]]s " + \
                     "autres que les [[Impôts locaux en France|impôts locaux]].",
            'nul' : 'aucun [[Impôts locaux en France|autre impôt]]'
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
            'nul' : "aucune dépense d'équipement"
        },
        "des [[Plan de remboursement|remboursement]]s d'emprunts" :
        {
            'libellePicto' : "Remboursements d'emprunts",
            'cle' : "Remboursement d'emprunts et dettes assimilées",
            'note' : "Les « [[Plan de remboursement|remboursement]]s d'emprunts » " + \
                     "représentent les sommes affectées par la commune au " + \
                     "remboursement du capital de la dette.",
            'nul' : "aucun [[Plan de remboursement|remboursement]] d'emprunt"
        }
    }
    grandeursAnalyse.append([dictEmploiInvest, emploisI,
                             "EMPLOI_INVEST", couleurEmploisInvest])

    dictRessourcesInvest = \
    {
        "[[Emprunt (finance)|nouvelles dettes]]" :
        {
            'libellePicto' : 'Nouvelles dettes',
            'cle' : "dont : Emprunts bancaires et dettes assimilées",
            'note' : "",
            'nul' : "aucune [[Emprunt (finance)|nouvelle dette]]"
        },
        "[[subventions]] reçues" :
        {
            'libellePicto' : 'Subventions reçues',
            'cle' : "Subventions reçues",
            'note' : "",
            'nul' : "aucune [[subventions|subvention]] reçue"
        },
        "[[fonds de Compensation pour la TVA]]" :
        {
            'libellePicto' : 'FCTVA',
            'cle' : "FCTVA",
            'note' : "",
            'nul' : "aucune somme au titre des [[fonds de Compensation pour la TVA]]"
        }
    }
    grandeursAnalyse.append([dictRessourcesInvest, ressourcesI,
                             "RESSOURCES_INVEST", couleurRessourcesInvest])

    dictCAF = \
    {
        "la [[capacité d'autofinancement]] (CAF)" :
        {
            'libellePicto' : "Capacité d'autofinancement",
            'cle' : "Capacité d'autofinancement = CAF",
            'note' : "",
            'nul' : "aucune [[capacité d'autofinancement]]"
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
        lignes = genlignesTableauPicto(grandeurs[2], nbLignes, grandeurs[3], "euro", verbose)
        textSection = textSection.replace("<GEN_LIGNES_TABLEAU_PICTO_" + grandeurs[2] + ">",
                                          "".join(lignes))

    # Recherche des valeurs, calcul des ratio et remplacement des mots clés
    for grandeurs in grandeursAnalyse:
        nbAnneesTendance = int(config.get('GenWIkiCode', 'gen.nbAnneesTendance'))
        listeAnneesTendance = sorted(listAnnees[:nbAnneesTendance])
        getValeursDict(listeAnneesTendance, ville, listAnnees[0], grandeurs[0], verbose)
        cleTriee = triPourCent(config, grandeurs[1], grandeurs[0], True, verbose)
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
            textSection = textSection.replace("<NOTE_" + grandeurs[2] + str(numValeur+1) +">",
                                              grandeurs[0][text]["note"])
            textSection = textSection.replace("<PICTO_" + grandeurs[2] + str(numValeur+1) +">",
                                              grandeurs[0][text]['ratioStratePicto'])
            # V1.0.2 : Accessibilité : texte alternatif
            textSection = textSection.replace("<PICTO_ALT_" + grandeurs[2] + str(numValeur+1) +">",
                                              grandeurs[0][text]['ratioStratePictoAlt'])
            textSection = textSection.replace("<LIBELLE_PICTO_" + grandeurs[2] + \
                                              str(numValeur+1) +">",
                                              grandeurs[0][text]['libellePicto'])
            # V1.2.1 : Phrase complête pour éviter les problèmes en cas de valeur nulle
            if grandeurs[0][text]["Valeur totale"] == 0:
                phrase = grandeurs[0][text]["nul"]
                if len(grandeurs[0][text]["note"].strip()) != 0:
                    phrase += '<ref group="Note">' + grandeurs[0][text]["note"] + "</ref>"
            else:
                phrase = text
                if len(grandeurs[0][text]["note"].strip()) != 0:
                    phrase += '<ref group="Note">' + grandeurs[0][text]["note"] + "</ref>"
                phrase += " pour " + random.choice(["un montant de", "une somme de", "",
                                                    "une valeur totale de",
                                                    "une valeur de"]) + \
                          " " + "{{euro|" + \
                          str(grandeurs[0][text]["Valeur totale"]) + "}}"
                # Si la somme total des valeurs du groupe est valide, on affiche le pourcentage
                if grandeurs[1] > 0:
                    phrase += " (" +  grandeurs[0][text]['ratioValeurStr'] + ")"
                if grandeurs[0][text]["Par habitant"] > 0:
                    phrase += ", soit {{euro|" + \
                              str(grandeurs[0][text]["Par habitant"]) + "}} par habitant, ratio "
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
        lignes += genlignesTableauPicto(dictTaxe["tag"], 1, couleurTaxes, '%', verbose)[0]
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
        picto, alt = utilitaires.choixPicto(config, ratioTaxe)
        textSection = textSection.replace("<PICTO_" + tag + "1>", picto)
        textSection = textSection.replace("<PICTO_ALT_" + tag + "1>", alt)

        # Tendance annee N-1
        augmentation = utilitaires.calculeTendance(config,
                                                   float(tauxTaxeVille),
                                                   float(tauxTaxeVilleNM1))
        textSection = textSection.replace("<TENDANCE_" + tag + "_PAR_HABITANT1>",
                                          augmentation)

    # V1.0.0 : Generation de la légende du tableau
    # V1.0.2 : Accessibilité : texte alternatif
    ecartFort = config.get('GenWIkiCode', 'gen.seuilValeurPourCentgrande')
    legende = "[[fichier:" + config.get('Picto', 'picto.ecartNul') + "|10px|alt=" + \
                config.get('Picto', 'picto.ecartNulAlt') + "|link=]] "
    legende += "de 0 à " + config.get('GenWIkiCode', 'gen.seuilValeurPourCentDifferente') + \
               " % ; "
    legende += "[[fichier:" + config.get('Picto', 'picto.ecartMoyen') + "|10px|alt=" + \
                config.get('Picto', 'picto.ecartMoyenAlt') + "|link=]] de "
    legende += config.get('GenWIkiCode', 'gen.seuilValeurPourCentDifferente') + \
               " à " + ecartFort + " % ; "
    legende += "[[fichier:" + config.get('Picto', 'picto.ecartFort') + "|10px|alt=" + \
                config.get('Picto', 'picto.ecartFortAlt') + "|link=]] "
    legende += "supérieur à " + config.get('GenWIkiCode', 'gen.seuilValeurPourCentgrande') + \
               " %"
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
def triPourCent(config, sommeValeurTotal, dictValeurs, avecTendance, verbose):
    """
    Classemement de grandeurs et stat
    Entree :  valeur totale, dictionnaire des valeurs à compléter
    Sortie : Liste ordonnée par valeur décroissante des cles du dictionnaire
    """
    if verbose:
        print("\nEntrée dans triPourCent")

    seuilValeurPourCentDifferente = \
        float(config.get('GenWIkiCode', 'gen.seuilValeurPourCentDifferente'))

    # Par convention si sommeValeurTotal <= 0, on prend 1 pour éviter div0
    if sommeValeurTotal <= 0:
        sommeValeurTotal = 1

    # Calcul des ratios Valeur / sommeValeurTotal
    # Calcul des ratio comparatifs par rapport aux strates
    for defValeur in list(dictValeurs.keys()):
        dictValeurs[defValeur]['ratioValeur'] = \
            (float(dictValeurs[defValeur]["Valeur totale"]) * 100.0) / \
             float(sommeValeurTotal)
        if dictValeurs[defValeur]['ratioValeur'] < 1.0:
            faibleStr = random.choice(["inférieures à 1 %", " plus faibles", "négligeables"])
            dictValeurs[defValeur]['ratioValeurStr'] = "des sommes " + faibleStr
        else:
            dictValeurs[defValeur]['ratioValeurStr'] = \
                "%1.f"%dictValeurs[defValeur]['ratioValeur'] + " %"

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
                " à la valeur moyenne pour les communes de la même strate ({{euro|" + \
                str(dictValeurs[defValeur]["En moyenne pour la strate"]) + \
                "}} par habitant)"

        # v1.0.0 : tendance des séries sur les derniéres années
        if avecTendance:
            dictAneeesValeur = dictValeurs[defValeur]['dictAneeesValeur']
            dictValeurs[defValeur]['ratioTendanceStr'] = \
                utilitaires.calculeTendanceSerieStr('ce ratio', dictAneeesValeur,
                                                    'par habitant', verbose)

        picto, alt = utilitaires.choixPicto(config, ratioStrate)
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
def genlignesTableauPicto(motCle, nbLignes, couleur, unite, verbose):
    """ Genere nbLignes du tableau des pictogrammes avec mot-clés à expanser plus tard """
    if verbose:
        print("\nEntrée dans genlignesTableauPicto")
        print("motCle=", motCle)
        print("nbLignes=", nbLignes)
        print("couleur=", couleur)

    lignes = list()
    for numLigne in range(1, nbLignes+1):
        uniteStrDebut = ""
        uniteStrFin = ""
        if unite == "euro":
            uniteStrDebut = "{{euro|"
            uniteStrFin = "}}"
        elif unite == "%":
            uniteStrDebut = "{{unité|"
            uniteStrFin = "}}"

        ligne = " |----\n"
        ligne += ' ! scope="row" style="background-color: ' + couleur + '" | ' + \
                 '<LIBELLE_PICTO_' + motCle + str(numLigne) + '>\n'
        for champ in ['_PAR_HABITANT', '_STRATE']:
            ligne += ' | style="text-align:right;background-color: ' + couleur + '"' + \
                     ' | ' + uniteStrDebut + '<VALEUR_' + motCle + champ + str(numLigne) + \
                     '>' + uniteStrFin + '\n'
        # V1.0.2 : Accessibilité : texte alternatif
        ligne += ' | style="text-align:right;background-color:' + couleur + \
                 ' " | [[fichier:<PICTO_' + motCle + str(numLigne) + '>|10px|alt=' + \
                 '<PICTO_ALT_' + motCle + str(numLigne) + '>|link=]]\n'
        lignes.append(ligne)
        numLigne += 1

    if verbose:
        print("Sortie de genlignesTableauPicto")
        print("lignes", lignes)
    return lignes
