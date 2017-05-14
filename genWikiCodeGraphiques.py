# -*- coding: utf-8 -*-
"""
*********************************************************
Module : genWikiCodeGraphiques.py
Auteur : Thierry Maillard (TMD)
Date : 24/5/2015 - 22/7/2015

Role : Transforme les donnees traitées par extractionMinFi.py
        en wikicode pour les partie graphiques.
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
import sys
import math

import utilitaires

def genWikiCodeGraphiques(config, textSection, ville,
                          listAnnees, isComplet, verbose):
    """ Génere le Wikicode pour tous les graphiques d'une ville """
    if verbose:
        print("Entree dans genWikiCodeGraphiques")

    # Définition des couleurs format : [couleur picto, couleur EasyTimeline]
    # La couleur EasyTimeline pour les courbes doit correspondre
    # à la couleur des pictos de la légende.
    # Reference
    # https://www.mediawiki.org/wiki/Extension:EasyTimeline/syntax#Predefined_colors
    # https://fr.wikipedia.org/wiki/Aide:Couleurs
    # https://fr.wikipedia.org/wiki/Wikip%C3%A9dia:Atelier_accessibilit%C3%A9
    noir = [config.get('Graphiques', 'graph.pointNoir'),
            config.get('Graphiques', 'graph.courbeNoir'),
            config.get('Graphiques', 'graph.altNoir')]
    vertFonce = [config.get('Graphiques', 'graph.pointVertFonce'),
                 config.get('Graphiques', 'graph.courbeVertFonce'),
                 config.get('Graphiques', 'graph.altVertFonce')]
    bleuFonce = [config.get('Graphiques', 'graph.pointBleuFonce'),
                 config.get('Graphiques', 'graph.courbeBleuFonce'),
                 config.get('Graphiques', 'graph.altBleuFonce')]
    rougeFonce = [config.get('Graphiques', 'graph.pointRougeFonce'),
                  config.get('Graphiques', 'graph.courbeRougeFonce'),
                  config.get('Graphiques', 'graph.altRougeFonce')]

    listeGraphiques = list()

    # V1.0.5 : Précision investissement : ajout 1 courbe  et séparation tableau
    courbesProduitsChargesFonctionnement = \
        {
            'nomGraphique' : "RECETTES_CHARGES_FONCTIONNEMENT",
            'unite' : 'euros',
            'largeur' : 'graph.largeurPage',
            'courbes' :
                [
                    {
                        'cle' : 'TOTAL DES PRODUITS DE FONCTIONNEMENT',
                        'sousCle' : "Valeur totale",
                        'libelle' : 'Produits',
                        'couleur' : bleuFonce
                    },
                    {
                        'cle' : 'TOTAL DES CHARGES DE FONCTIONNEMENT',
                        'sousCle' : "Valeur totale",
                        'libelle' : 'Charges',
                        'couleur' : rougeFonce
                    }
                ]
        }
    listeGraphiques.append(courbesProduitsChargesFonctionnement)

    courbesEmploisRessourcesFonctionnement = \
        {
            'nomGraphique' : "EMPLOIS_RESSOURCES_INVESTISSEMENT",
            'unite' : 'euros',
            'largeur' : 'graph.largeurPage',
            'courbes' :
                [
                    {
                        'cle' : "TOTAL DES EMPLOIS D'INVESTISSEMENT",
                        'sousCle' : "Valeur totale",
                        'libelle' : "Emplois",
                        'couleur' : vertFonce
                    },
                    {
                        'cle' : "TOTAL DES RESSOURCES D'INVESTISSEMENT",
                        'sousCle' : "Valeur totale",
                        'libelle' : "Ressources",
                        'couleur' : noir
                    }

                ]
        }
    listeGraphiques.append(courbesEmploisRessourcesFonctionnement)

    courbesProduits = \
        {
            'nomGraphique' : "PRODUITS",
            'largeur' : 'graph.largeurPage',
            'unite' : 'euros',
            'courbes' :
                [
                    {
                        'cle' : "dont : Impôts Locaux",
                        'sousCle' : "Valeur totale",
                        'libelle' : 'Impôts Locaux',
                        'couleur' : bleuFonce
                    },
                    {
                        'cle' : "Autres impôts et taxes",
                        'sousCle' : "Valeur totale",
                        'libelle' : 'Autres impôts et taxes',
                        'couleur' : rougeFonce
                    },
                    {
                        'cle' : "Dotation globale de fonctionnement",
                        'sousCle' : "Valeur totale",
                        'libelle' : 'Dotation globale de fonctionnement',
                        'couleur' : noir
                    }
                ]
        }
    listeGraphiques.append(courbesProduits)
    courbesChargesPersonnelsExternes = \
        {
            'nomGraphique' : "CHARGES_PERSONNELS_EXTERNES",
            'largeur' : 'graph.largeurPage',
            'unite' : 'euros',
            'courbes' :
                [
                    {
                        'cle' : "dont : Charges de personnel",
                        'sousCle' : "Valeur totale",
                        'libelle' : "Charges de personnel",
                        'couleur' : bleuFonce
                    },
                    {
                        'cle' : "Achats et charges externes",
                        'sousCle' : "Valeur totale",
                        'libelle' : "Achats et charges externes<br />",
                        'couleur' : rougeFonce
                    },
                ]
        }
    listeGraphiques.append(courbesChargesPersonnelsExternes)
    courbesChargesPersonnelsExternes = \
        {
            'nomGraphique' : "CHARGES_FINANCIERES_SUBVENTIONS_VERSEES",
            'largeur' : 'graph.largeurPage',
            'unite' : 'euros',
            'courbes' :
                [
                    {
                        'cle' : "Charges financières",
                        'sousCle' : "Valeur totale",
                        'libelle' : "Charges financières",
                        'couleur' : vertFonce
                    },
                    {
                        'cle' : "Subventions versées",
                        'sousCle' : "Valeur totale",
                        'libelle' : "Subventions versées",
                        'couleur' : noir
                    }
                ]
        }
    listeGraphiques.append(courbesChargesPersonnelsExternes)

    courbesDetteCAF = \
        {
            'nomGraphique' : "DETTE_CAF",
            'largeur' : 'graph.largeurPage',
            'unite' : 'euros',
            'courbes' :
                [
                    {
                        'cle' : "Capacité d'autofinancement = CAF",
                        'sousCle' : "Par habitant",
                        'libelle' : 'CAF',
                        'couleur' : bleuFonce
                    },
                    {
                        'cle' : 'Encours de la dette au 31/12/N',
                        'sousCle' : "Par habitant",
                        'libelle' : 'Encours total de la dette',
                        'couleur' : rougeFonce
                    }
                ]
            }
    if isComplet:
        courbesDetteCAF['courbes'].extend(
            [
                {
                    'cle' : "Capacité d'autofinancement = CAF",
                    'sousCle' : "En moyenne pour la strate",
                    'libelle' : 'CAF',
                    'couleur' : vertFonce
                },
                {
                    'cle' : 'Encours de la dette au 31/12/N',
                    'sousCle' : "En moyenne pour la strate",
                    'libelle' : 'Encours total de la dette',
                    'couleur' : noir
                }
            ])
    listeGraphiques.append(courbesDetteCAF)

    courbesDGF = \
        {
            'nomGraphique' : "DGF",
            'largeur' : 'graph.largeurPage',
            'unite' : 'euros',
            'courbes' :
                [
                    {
                        'cle' : "Dotation globale de fonctionnement",
                        'sousCle' : "Par habitant",
                        'libelle' : 'DGF',
                        'couleur' : bleuFonce
                    }
                ]
        }
    if isComplet:
        courbesDGF['courbes'].extend(
            [
                {
                    'cle' : "Dotation globale de fonctionnement",
                    'sousCle' : "En moyenne pour la strate",
                    'libelle' : 'DGF',
                    'couleur' : vertFonce
                }
            ])
    listeGraphiques.append(courbesDGF)

    # V1.0.2 : Ajout courbes investissement
    # V1.0.5 : Précisions : séparation emploi et ressources d'investissement
    courbesEmploisInvest = \
        {
            'nomGraphique' : "EMPLOIS_INVEST",
            'largeur' : 'graph.largeurPage',
            'unite' : 'euros',
            'courbes' :
                [
                    {
                        'cle' : "dont : Dépenses d'équipement",
                        'sousCle' : "Valeur totale",
                        'libelle' : "[[Dépenses publiques|Dépenses]] d'équipement",
                        'couleur' : bleuFonce
                    },
                    {
                        'cle' : "Remboursement d'emprunts et dettes assimilées",
                        'sousCle' : "Valeur totale",
                        'libelle' : "[[Plan de remboursement|Remboursement]]s " + \
                                    "[[Emprunt (finance)|emprunt]]s",
                        'couleur' : vertFonce
                    }
                ]
        }
    listeGraphiques.append(courbesEmploisInvest)
    courbesRessourcesInvest = \
        {
            'nomGraphique' : "RESSOURCES_INVEST",
            'largeur' : 'graph.largeurPage',
            'unite' : 'euros',
            'courbes' :
                [
                    {
                        'cle' : "dont : Emprunts bancaires et dettes assimilées",
                        'sousCle' : "Valeur totale",
                        'libelle' : 'Nouvelles [[Emprunt (finance)|dette]]s',
                        'couleur' : rougeFonce
                    },
                    {
                        'cle' : "Subventions reçues",
                        'sousCle' : "Valeur totale",
                        'libelle' : '[[Subventions]] reçues',
                        'couleur' : bleuFonce
                    },
                    {
                        'cle' : "FCTVA",
                        'sousCle' : "Valeur totale",
                        'libelle' : '[[Fonds de Compensation pour la TVA|FCTVA]]',
                        'couleur' : vertFonce
                    }
                ]
        }
    listeGraphiques.append(courbesRessourcesInvest)

    # Generation graphique Ratio Encours de la dette / CAF
    courbeRatioDetteCAF = \
        {
            'nomGraphique' : "RATIO",
            'largeur' : 'graph.largeurPage',
            'unite' : 'années',
            'courbes' :
                [
                    {
                        'cle' : 'ratioCAFDette',
                        'sousCle' : "",
                        'libelle' : 'Ratio = Encours de la dette / CAF',
                        'couleur' : bleuFonce
                    }
                ]
        }
    listeGraphiques.append(courbeRatioDetteCAF)

    courbesTaxes = \
        {
            'nomGraphique' : "TAXES",
            'largeur' : 'graph.largeurPage',
            'unite' : '%',
            'courbes' :
                [
                    {
                        'cle' : "Taux Taxe d'habitation",
                        'sousCle' : "Taux",
                        'libelle' : "Taux taxe d'habitation",
                        'couleur' : bleuFonce
                    },
                    {
                        'cle' : 'Taux Taxe foncière bâti',
                        'sousCle' : "Taux",
                        'libelle' : 'Taux foncier bâti',
                        'couleur' : rougeFonce
                    }
                ]
        }
    if isComplet:
        courbesTaxes['courbes'].extend(
            [
                {
                    'cle' : "Taux Taxe d'habitation",
                    'sousCle' : "Taux moyen pour la strate",
                    'libelle' : "Taux taxe d'habitation",
                    'couleur' : vertFonce
                },
                {
                    'cle' : 'Taux Taxe foncière bâti',
                    'sousCle' : "Taux moyen pour la strate",
                    'libelle' : 'Taux foncier bâti',
                    'couleur' : noir
                }
            ])
    listeGraphiques.append(courbesTaxes)

    courbesTaxesNB = \
        {
            'nomGraphique' : "TAXES_NB",
            'largeur' : 'graph.largeurPage',
            'unite' : '%',
            'courbes' :
                [
                    {
                        'cle' : "Taux Taxe foncière non bâti",
                        'sousCle' : "Taux",
                        'libelle' : 'Taux foncier non bâti',
                        'couleur' : rougeFonce
                    }
                ]
        }
    if isComplet:
        courbesTaxesNB['courbes'].extend(
            [
                {
                    'cle' : "Taux Taxe foncière non bâti",
                    'sousCle' : "Taux moyen pour la strate",
                    'libelle' : 'Taux foncier non bâti',
                    'couleur' : noir
                }
            ])
    listeGraphiques.append(courbesTaxesNB)

    # Generation des graphiques et remplacement des mot-clés
    for graphique in listeGraphiques:
        if verbose:
            print("\n************************************")
            print("Graphe :", graphique['nomGraphique'])
            print("************************************")
        graphiqueWiki, legendeVille, legendeStrate = \
            genGraphique(config,
                         ville, listAnnees, graphique['courbes'],
                         graphique['unite'], graphique['largeur'], verbose)
        textSection = textSection.replace("<GRAPHIQUE_" + graphique['nomGraphique'] + ">",
                                          graphiqueWiki)
        textSection = textSection.replace("<LEGENDE_" + graphique['nomGraphique'] + ">",
                                          legendeVille)
        textSection = textSection.replace("<LEGENDE_STRATE_" + graphique['nomGraphique'] + ">",
                                          legendeStrate)

    if verbose:
        print("Sortie de genWikiCodeGraphiques")

    return textSection

def genGraphique(config, ville, listAnnees, courbes, unite, largeur, verbose):
    """ Génère le Wikicode pour un graphique """
    if verbose:
        print("\n**********************")
        print("Entree dans genGraphique")
        print('ville=', ville['nom'])
        print("Nombre de courbes :", len(courbes))
        print("clé =", [courbe['cle'] for courbe in courbes])
        print("listAnnees :", listAnnees)

    # Elimination des courbes vides et des années non présentes dans toutes les autres
    anneesOK = controleSeries(ville, courbes, listAnnees, verbose)
    nbSeries = len(courbes)
    nbSeriesVille = len([courbe for courbe in courbes
                         if 'strate' not in courbe['sousCle']])
    if verbose:
        print("\nApres elimination des series vide et")
        print("\tselection des seules annees contenant des valeurs")
        print("\tpour les series conserves")
        print("nbSeries Ville=", nbSeriesVille)
        print("nbSeries Ville + Strate =", nbSeries)
        print("anneesOK =", anneesOK)

    ligne = "| {{Graphique polygonal\n"
    ligne += " | coul_fond = white\n"
    # ! Si largeur trop petite, problème de tracé :
    # Les rectangles représentants les points "bavent"
    # par un trait oblique qui les relie au bas du graphique
    ligne += " | largeur = " + config.get('Graphiques', largeur)
    ligne += " | hauteur = " + config.get('Graphiques', 'graph.hauteur')
    ligne += "\n"

    # V0.8 : margeg = 50 pour corriger pb libellé ordonnées tronquées
    #           si grand nombre et une des série proche 0
    ligne += " | marge_g = " + config.get('Graphiques', 'graph.marge_g')
    ligne += " | marge_d = " + config.get('Graphiques', 'graph.marge_d')
    ligne += " | marge_h = " + config.get('Graphiques', 'graph.marge_h')
    ligne += " | marge_b = " + config.get('Graphiques', 'graph.marge_b')
    ligne += "\n"

    ligne += " | nb_series = " + str(nbSeries) + "\n"
    nbAbscisses = len(anneesOK)
    ligne += " | nb_abscisses = " + str(nbAbscisses) + "\n"

    # Generation dates abscisses
    # V1.0.5 : Correction bug si annee manquante
    for indice in range(len(anneesOK)):
        ligne += " | lb_x" + str(indice+1) + " = " + str(anneesOK[indice])
    ligne += "\n"

    # Détermination de l'arrondi à utiliser :
    # Arrondi en million sauf si une des valeurs à afficher est < 1000000
    # V0.5 : TMD : 7/6/2015 :seuils des arrondis relevés relevé à 2ME et 2kE
    if verbose:
        print("Determination de l'arrondi...")
    arrondi = 0
    arrondiStr = ""
    arrondiStrAffiche = ""
    if not courbes[0]['cle'].startswith('Taux'):
        arrondi = 2
        arrondiStr = 'M€'
        arrondiStrAffiche = "millions d'"
        for annee in anneesOK:
            for courbe in courbes:
                if courbe['sousCle'] == "":
                    valeurData = int(ville['data'][courbe['cle']][str(annee)])
                else:
                    valeurData = int(utilitaires.getValeur(ville, courbe['cle'],
                                                           annee, courbe['sousCle']))
                if valeurData < 2000000 and arrondi > 1:
                    arrondi = 1
                    arrondiStr = 'k€'
                    arrondiStrAffiche = "milliers d'"
                # V0.8 : Contournement pb multiple pour valeur de grande amplitude avec 0 inclu :
                # arrondi mini = 1 : on ne descend pas au dessous du kEuro
                #   si sous-clé = "Valeur totale"
                # Pas de perte d'info par arrondi car en kEuros dans base MinFi
                if valeurData < 2000 and arrondi > 0 and \
                   courbe['sousCle'] != "Valeur totale":
                    arrondi = 0
                    arrondiStr = '€'
                    arrondiStrAffiche = ""
    arrondiStrAffiche += unite

    if verbose:
        print("arrondi =", arrondi, ", arrondiStr = ", arrondiStr)
        print("arrondiStrAffiche = ", arrondiStrAffiche)

    # Détermination min, max des valeurs
    maxVal = -sys.maxsize - 1
    minVal = sys.maxsize
    for annee in anneesOK:
        for courbe in courbes:
            if courbe['cle'].startswith('Taux'):
                valeurData = \
                    int(ville['data'][courbe['cle']][str(annee)][courbe['sousCle']])
            elif courbe['sousCle'] == "":
                valeurData = int(ville['data'][courbe['cle']][str(annee)])
            else:
                valeurData = int(utilitaires.getValeur(ville, courbe['cle'],
                                                       annee, courbe['sousCle'], arrondi))
            maxVal = max(maxVal, valeurData)
            minVal = min(minVal, valeurData)
    if verbose:
        print("minVal =", minVal, ", maxVal = ", maxVal)

    # Calcul des caractéristiques des graduations de l'axe Y :
    # y_max, y_min, pas des graduations majeures et mineures
    yMin, yMax, pasSec, pasPrinc = myticks(minVal, maxVal, True, True, verbose)
    if verbose:
        print("yMin=", yMin)
        print("yMax=", yMax)
        print("pasSec=", pasSec)
        print("pasPrinc=", pasPrinc)

    ligne += " | y_max =" + str(yMax) + " | y_min = " + str(yMin) + "\n"
    ligne += " | pas_grille_principale = " + str(pasPrinc)
    ligne += " | pas_grille_secondaire = " + str(pasSec) + "\n"
    ligne += " | grille = oui\n"

    numSerie = 0
    for courbe in courbes:
        ligne += " | epaisseur_serie" + str(numSerie+1) + " = 0.9 "
        ligne += " | coul_serie_" + str(numSerie+1) + " = " + \
                 courbe['couleur'][1] + "\n"
        numSerie += 1

    # Data series
    numValeur = 1
    for annee in anneesOK:
        valeur = '%02d'%numValeur
        numSerie = 1
        for courbe in courbes:
            serie = '%02d'%numSerie
            if courbe['cle'].startswith('Taux'):
                valeurData = utilitaires.getValeurFloat(ville, courbe['cle'],
                                                        annee, courbe['sousCle'])
            elif courbe['sousCle'] == "":
                valeurData = str(ville['data'][courbe['cle']][str(annee)])
            else:
                valeurData = utilitaires.getValeur(ville, courbe['cle'],
                                                   annee, courbe['sousCle'], arrondi)
            ligne += " | S" + serie + "V" + valeur + " = " + valeurData + " "
            numSerie += 1
        ligne += "\n"
        numValeur += 1

    ligne += " | points = oui}}"

    # Légende
    # V1.0.2 : Accessibilité, remplacement des caractères Unicode
    #          par des images + chaine alt
    legendeVille = "Valeurs en " + arrondiStrAffiche + "<br />"
    legendeStrate = ""
    ecritLegendeVille = True
    ecritLegendeStrate = True

    for courbe in courbes:
        if 'strate' not in courbe['sousCle']:
            if ecritLegendeVille:
                legendeVille += (ville["nom"] + ', ' + courbe['sousCle'].lower() + ' : ')
                ecritLegendeVille = False
            legendeVille += "[[fichier:" + courbe['couleur'][0] + "|10px|alt=" + \
                            courbe['couleur'][2] + "|link=]] " + \
                            courbe['libelle'] + " "
        if 'strate' in courbe['sousCle']:
            if ecritLegendeStrate:
                legendeStrate += '<br />' + courbe['sousCle'] + ' : '
                ecritLegendeStrate = False
            legendeStrate += "[[fichier:" + courbe['couleur'][0] + "|10px|alt=" + \
                             courbe['couleur'][2] + "|link=]] " + \
                             courbe['libelle'] + " "

    if verbose:
        print("legendeVille=", legendeVille)
        print("legendeStrate =", legendeStrate)
        print("Sortie de genGraphique")

    return ligne, legendeVille, legendeStrate

def controleSeries(ville, courbes, listAnnees, verbose):
    """
    Contrôle des series pour eliminer les series vides
    et ne tracer que les séries restantes qui ont des annees communes
    """
    if verbose:
        print("\nEntree dans controleSeries")
        print('ville=', ville['nom'])
        print("Nombre de courbes :", len(courbes))
        print("listAnnees :", listAnnees)

    setCle = {courbe['cle'] for courbe in courbes}

    # Recupération liste des années valides pour chaque clé
    # et conservation des seules clés qui ont au moins une année valide
    anneesOKParCle = dict()
    for cle in setCle:
        anneesOK1serie = set(annee for annee in listAnnees
                             if ville['data'][cle][str(annee)] is not None)
        if len(anneesOK1serie) > 0:
            anneesOKParCle[cle] = anneesOK1serie

    # Détermination des annees communes aux clés restantes
    anneesOK = set(listAnnees)
    for cle in list(anneesOKParCle.keys()):
        anneesOK &= anneesOKParCle[cle]

    # Conservation des seules series qui ont des annees communes
    for courbe in courbes:
        if courbe['cle'] not in list(anneesOKParCle.keys()):
            courbes.remove(courbe)

    if verbose:
        print("Sortie de controleSeries")
        print("Nombre de courbes :", len(courbes))
        print("listeCle OK =", [courbe['cle'] for courbe in courbes])
        print("anneeOK =", anneesOK)

    # Le tri des chaines de caractere est ici acceptable pour des annees sur 4 chiffres
    return sorted(list(anneesOK))

def myticks(MinP, MaxP, fitMin, fitMax, verbose):
    '''
    Role : Generate intelligent axis scaling
    Author : David Ascher da@ski.org
    Source : https://mail.python.org/pipermail/matrix-sig/1999-March/002668.html
    Date : Thu, 18 Mar 1999

    Usage : python ticks.py MinData MaxData
    Parameters
        -MinP, MaxP : Minimum and maximum values (int) of the dataset to plot
    Return :
        - gridMin, gridMax : min and max ticks position
        - smallTicksSpace : spacing between minor ticks
        - bigTicksSpace : spacing between major ticks
        - (may be return) r and l : minor and major ticks position.

    Modifed by Thierry Maillard (TMD) on 29/5/2015
        - Suppress log supports
        - Replace calls to NumPy with standard library calls : rand, pow
        - Add test and trick if two import numbers are too close
        - Output grid ticks spaces instead of ticks position
    '''
    if verbose:
        print("\nEntree dans myticks")
        print("MinP=", MinP, "MaxP=", MaxP)

    # TMD : if values are too close, enlarge the gap
    Max = float(MaxP)
    Min = float(MinP)
    d = abs(MaxP - MinP)
    if d < 10:
        Max = Max + 5
        Min = Min - 5
        d = abs(Max - Min)

    epsilon = 1e-10
    s = math.pow(10, math.floor(math.log10(d)) - 1)
    if fitMin:
        startat = Min - (Min % (s * 10))
    else:
        startat = Min
    overmax = Max + (s * 10)
    if fitMax:
        endat = overmax - (overmax % (s * 10))
    else:
        endat = Max
    if d / (10*s) > 5.2:  # magic!
                     # small tickmarks at unit factors
        s = s * 10   # we need to upshift the scale
        maj_mod = 10 # major tick marks at factors of 10
        int_mod = 2  # intermediate tick marks at factors of 2
    else:
        maj_mod = 10 # major tick marks at factors of 10
        int_mod = 5  # minors at factors of 5
                     # smalls at factors of 1
    r = []
    l = []
    nummajors = 0 # for debugging
    numints = 0
    for x in range(int(round(startat)), int(round(endat+epsilon)), int(round(s))):
        x = int(round(x))
        r.append(x)
        if abs((x / s) % maj_mod) < epsilon:
            l.append(x)
            nummajors = nummajors + 1
        elif abs((x / s) % int_mod) < epsilon:
            l.append(x)
            numints = numints + 1

    gridMin = int(startat)
    gridMax = int(endat)
    smallTicksSpace = int(abs(r[0] - r[1]))
    bigTicksSpace = int(abs(l[0] - l[1]))

    if verbose:
        print("gridMin=", gridMin, "gridMax=", gridMax)
        print("smallTicksSpace=", smallTicksSpace, "bigTicksSpace=", bigTicksSpace)
        print("\nSortie de myticks")
    return gridMin, gridMax, smallTicksSpace, bigTicksSpace
