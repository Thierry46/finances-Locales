# -*- coding: utf-8 -*-
"""
*********************************************************
Module : genCodeGraphiques.py
Auteur : Thierry Maillard (TMD)
Date : 24/5/2015 - 7/10/2015

Role : Transforme les donnees traitées par extractionMinFi.py
        en wikicode ou en png pour les parties graphiques.
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
import genWikiCodeGraphiques
import genHTMLCodeGraphiques
import utilitaires

def genCodeGraphiques(config, repVille, textSection, ville,
                      listAnnees, isComplet,
                      isWikicode, isMatplotlibOk,
                      verbose):
    """ Génere le Wikicode pour tous les graphiques d'une ville """
    if verbose:
        print("Entree dans genCodeGraphiques")

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

    # Les couleurs matplotlib couleurMPL sont définies dans :
    # http://matplotlib.org/examples/color/named_colors.html

    listeGraphiques = list()

    # V1.0.5 : Précision investissement : ajout 1 courbe  et séparation tableau
    courbesProduitsChargesFonctionnement = \
        {
            'nomGraphique' : "RECETTES_CHARGES_FONCTIONNEMENT",
            'titreGrahique' : "G0a - Section fonctionnement",
            'unite' : 'euros',
            'largeur' : 'graph.largeurPage',
            'courbes' :
                [
                    {
                        'cle' : 'TOTAL DES PRODUITS DE FONCTIONNEMENT',
                        'sousCle' : "Valeur totale",
                        'libelle' : 'Produits',
                        'couleur' : bleuFonce,
                        'couleurMPL' : 'turquoise'
                    },
                    {
                        'cle' : 'TOTAL DES CHARGES DE FONCTIONNEMENT',
                        'sousCle' : "Valeur totale",
                        'libelle' : 'Charges',
                        'couleur' : rougeFonce,
                        'couleurMPL' : 'salmon'
                    }
                ]
        }
    listeGraphiques.append(courbesProduitsChargesFonctionnement)

    courbesEmploisRessourcesFonctionnement = \
        {
            'nomGraphique' : "EMPLOIS_RESSOURCES_INVESTISSEMENT",
            'titreGrahique' : "G0b - Section investissement",
            'unite' : 'euros',
            'largeur' : 'graph.largeurPage',
            'courbes' :
                [
                    {
                        'cle' : "TOTAL DES EMPLOIS D'INVESTISSEMENT",
                        'sousCle' : "Valeur totale",
                        'libelle' : "Emplois",
                        'couleur' : vertFonce,
                        'couleurMPL' : 'chartreuse'
                    },
                    {
                        'cle' : "TOTAL DES RESSOURCES D'INVESTISSEMENT",
                        'sousCle' : "Valeur totale",
                        'libelle' : "Ressources",
                        'couleur' : noir,
                        'couleurMPL' : 'dimgray'
                    }

                ]
        }
    listeGraphiques.append(courbesEmploisRessourcesFonctionnement)

    courbesProduits = \
        {
            'nomGraphique' : "PRODUITS",
            'titreGrahique' : "G1a - Produits de fonctionnement",
            'largeur' : 'graph.largeurPage',
            'unite' : 'euros',
            'courbes' :
                [
                    {
                        'cle' : "dont : Impôts Locaux",
                        'sousCle' : "Valeur totale",
                        'libelle' : 'Impôts Locaux',
                        'couleur' : bleuFonce,
                        'couleurMPL' : 'turquoise'
                    },
                    {
                        'cle' : "Autres impôts et taxes",
                        'sousCle' : "Valeur totale",
                        'libelle' : 'Autres impôts et taxes',
                        'couleur' : rougeFonce,
                        'couleurMPL' : 'salmon'
                    },
                    {
                        'cle' : "Dotation globale de fonctionnement",
                        'sousCle' : "Valeur totale",
                        'libelle' : 'Dotation globale de fonctionnement',
                        'couleur' : noir,
                        'couleurMPL' : 'dimgray'
                    }
                ]
        }
    listeGraphiques.append(courbesProduits)
    courbesChargesPersonnelsExternes = \
        {
            'nomGraphique' : "CHARGES_PERSONNELS_EXTERNES",
            'titreGrahique' : "G1b1 - Charges de personnel et externes",
            'largeur' : 'graph.largeurPage',
            'unite' : 'euros',
            'courbes' :
                [
                    {
                        'cle' : "dont : Charges de personnel",
                        'sousCle' : "Valeur totale",
                        'libelle' : "Charges de personnel",
                        'couleur' : bleuFonce,
                        'couleurMPL' : 'turquoise'
                    },
                    {
                        'cle' : "Achats et charges externes",
                        'sousCle' : "Valeur totale",
                        'libelle' : "Achats et charges externes",
                        'couleur' : rougeFonce,
                        'couleurMPL' : 'salmon'
                    },
                ]
        }
    listeGraphiques.append(courbesChargesPersonnelsExternes)
    courbesChargesPersonnelsExternes = \
        {
            'nomGraphique' : "CHARGES_FINANCIERES_SUBVENTIONS_VERSEES",
            'titreGrahique' : "G1b2 - Charges financières et des subventions versées",
            'largeur' : 'graph.largeurPage',
            'unite' : 'euros',
            'courbes' :
                [
                    {
                        'cle' : "Charges financières",
                        'sousCle' : "Valeur totale",
                        'libelle' : "Charges financières",
                        'couleur' : vertFonce,
                        'couleurMPL' : 'chartreuse'
                    },
                    {
                        'cle' : "Subventions versées",
                        'sousCle' : "Valeur totale",
                        'libelle' : "Subventions versées",
                        'couleur' : noir,
                        'couleurMPL' : 'dimgray'
                    }
                ]
        }
    listeGraphiques.append(courbesChargesPersonnelsExternes)

    courbesDetteCAF = \
        {
            'nomGraphique' : "DETTE_CAF",
            'titreGrahique' : "G4a - Capacité d'autofinancement et dette",
            'largeur' : 'graph.largeurPage',
            'unite' : 'euros',
            'courbes' :
                [
                    {
                        'cle' : "Capacité d'autofinancement = CAF",
                        'sousCle' : "Par habitant",
                        'libelle' : 'CAF',
                        'couleur' : bleuFonce,
                        'couleurMPL' : 'turquoise'
                    },
                    {
                        'cle' : 'Encours de la dette au 31/12/N',
                        'sousCle' : "Par habitant",
                        'libelle' : 'Encours total de la dette',
                        'couleur' : rougeFonce,
                        'couleurMPL' : 'salmon'
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
                    'couleur' : vertFonce,
                    'couleurMPL' : 'chartreuse'
                },
                {
                    'cle' : 'Encours de la dette au 31/12/N',
                    'sousCle' : "En moyenne pour la strate",
                    'libelle' : 'Encours total de la dette',
                    'couleur' : noir,
                    'couleurMPL' : 'dimgray'
                }
            ])
    listeGraphiques.append(courbesDetteCAF)

    # V1.0.2 : Ajout courbes investissement
    # V1.0.5 : Précisions : séparation emploi et ressources d'investissement
    courbesEmploisInvest = \
        {
            'nomGraphique' : "EMPLOIS_INVEST",
            'titreGrahique' : "G3a - Emplois d'investissement",
            'largeur' : 'graph.largeurPage',
            'unite' : 'euros',
            'courbes' :
                [
                    {
                        'cle' : "dont : Dépenses d'équipement",
                        'sousCle' : "Valeur totale",
                        'libelle' : "Dépenses d'équipement",
                        'couleur' : bleuFonce,
                        'couleurMPL' : 'turquoise'
                    },
                    {
                        'cle' : "Remboursement d'emprunts et dettes assimilées",
                        'sousCle' : "Valeur totale",
                        'libelle' : "Remboursements d'emprunts",
                        'couleur' : vertFonce,
                        'couleurMPL' : 'chartreuse'
                    }
                ]
        }
    listeGraphiques.append(courbesEmploisInvest)
    courbesRessourcesInvest = \
        {
            'nomGraphique' : "RESSOURCES_INVEST",
            'titreGrahique' : "G3b - Ressources d'investissement",
            'largeur' : 'graph.largeurPage',
            'unite' : 'euros',
            'courbes' :
                [
                    {
                        'cle' : "dont : Emprunts bancaires et dettes assimilées",
                        'sousCle' : "Valeur totale",
                        'libelle' : 'Nouvelles dettes',
                        'couleur' : rougeFonce,
                        'couleurMPL' : 'salmon'
                    },
                    {
                        'cle' : "Subventions reçues",
                        'sousCle' : "Valeur totale",
                        'libelle' : 'Subventions reçues',
                        'couleur' : bleuFonce,
                        'couleurMPL' : 'turquoise'
                    },
                    {
                        'cle' : "FCTVA",
                        'sousCle' : "Valeur totale",
                        'libelle' : 'Fonds de compensation pour la TVA',
                        'couleur' : vertFonce,
                        'couleurMPL' : 'chartreuse'
                    }
                ]
        }
    listeGraphiques.append(courbesRessourcesInvest)

    # Generation graphique Ratio Encours de la dette / CAF
    courbeRatioDetteCAF = \
        {
            'nomGraphique' : "RATIO",
            'titreGrahique' : "G4b - Nombre d'années d'endettement",
            'largeur' : 'graph.largeurPage',
            'unite' : 'années',
            'courbes' :
                [
                    {
                        'cle' : 'ratioCAFDette',
                        'sousCle' : "",
                        'libelle' : 'Ratio = Encours de la dette / CAF',
                        'couleur' : bleuFonce,
                        'couleurMPL' : 'turquoise'
                    }
                ]
        }
    listeGraphiques.append(courbeRatioDetteCAF)

    courbesTaxes = \
        {
            'nomGraphique' : "TAXES",
            'titreGrahique' : "G2a - Taxes d'habitation et foncière sur le bâti",
            'largeur' : 'graph.largeurPage',
            'unite' : '%',
            'courbes' :
                [
                    {
                        'cle' : "Taux Taxe d'habitation",
                        'sousCle' : "Taux",
                        'libelle' : "Taux taxe d'habitation",
                        'couleur' : bleuFonce,
                        'couleurMPL' : 'turquoise'
                    },
                    {
                        'cle' : 'Taux Taxe foncière bâti',
                        'sousCle' : "Taux",
                        'libelle' : 'Taux foncier bâti',
                        'couleur' : rougeFonce,
                        'couleurMPL' : 'salmon'
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
                    'couleur' : vertFonce,
                    'couleurMPL' : 'chartreuse'
                },
                {
                    'cle' : 'Taux Taxe foncière bâti',
                    'sousCle' : "Taux moyen pour la strate",
                    'libelle' : 'Taux foncier bâti',
                    'couleur' : noir,
                    'couleurMPL' : 'dimgray'
                }
            ])
    listeGraphiques.append(courbesTaxes)

    courbesTaxesNB = \
        {
            'nomGraphique' : "TAXES_NB",
            'titreGrahique' : "G2b - Taxe foncière sur le non bâti",
            'largeur' : 'graph.largeurPage',
            'unite' : '%',
            'courbes' :
                [
                    {
                        'cle' : "Taux Taxe foncière non bâti",
                        'sousCle' : "Taux",
                        'libelle' : 'Taux foncier non bâti',
                        'couleur' : rougeFonce,
                        'couleurMPL' : 'salmon'
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
                    'couleur' : noir,
                    'couleurMPL' : 'dimgray'
                }
            ])
    listeGraphiques.append(courbesTaxesNB)

    # Generation des graphiques et remplacement des mot-clés
    for graphique in listeGraphiques:
        if verbose:
            print("\n************************************")
            print("Graphe :", graphique['nomGraphique'])
            print("************************************")

        # Elimination des courbes vides et des années non présentes dans toutes les autres
        anneesOK = controleSeries(ville, graphique['courbes'],
                                  listAnnees, verbose)
        arrondi, arrondiStrAffiche = \
            setArrondi(ville, anneesOK, graphique['courbes'],
                       graphique['unite'], verbose)

        if isWikicode:
            graphiqueWiki, legendeVille, legendeStrate = \
            genWikiCodeGraphiques.genGraphique(config,
                                               ville, anneesOK,
                                               graphique['courbes'],
                                               graphique['largeur'],
                                               arrondi,
                                               arrondiStrAffiche,
                                               verbose)
            textSection = textSection.replace("<GRAPHIQUE_" + graphique['nomGraphique'] + ">",
                                              graphiqueWiki)
            textSection = textSection.replace("<LEGENDE_" + graphique['nomGraphique'] + ">",
                                              legendeVille)
            textSection = textSection.replace("<LEGENDE_STRATE_" + graphique['nomGraphique'] + ">",
                                              legendeStrate)
        elif isMatplotlibOk:
            textLien = genHTMLCodeGraphiques.genGraphique(repVille,
                                                          graphique['nomGraphique'],
                                                          graphique['titreGrahique'],
                                                          ville, anneesOK,
                                                          graphique['courbes'],
                                                          arrondi,
                                                          arrondiStrAffiche,
                                                          verbose)
            textSection = textSection.replace("<GRAPHIQUE_" + graphique['nomGraphique'] + ">",
                                              textLien)
        else:
            textSection = textSection.replace("<GRAPHIQUE_" + graphique['nomGraphique'] + ">",
                                              "Graphique non disponible, " +\
                                              " installez matplotlib !<br/>")

    if verbose:
        print("Sortie de genCodeGraphiques")

    return textSection


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

def setArrondi(ville, anneesOK, courbes, unite, verbose):
    """
    Détermination de l'arrondi à utiliser :
    Arrondi en million sauf si une des valeurs à afficher est < 1000000
    V0.5 : TMD : 7/6/2015 :seuils des arrondis relevés relevé à 2ME et 2kE
    """
    if verbose:
        print("setArrondi : Determination de l'arrondi...")
    arrondi = 0
    arrondiStrAffiche = ""
    if not courbes[0]['cle'].startswith('Taux'):
        arrondi = 2
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
                    arrondiStrAffiche = "milliers d'"
                # V0.8 : Contournement pb multiple pour valeur de grande amplitude avec 0 inclu :
                # arrondi mini = 1 : on ne descend pas au dessous du kEuro
                #   si sous-clé = "Valeur totale"
                # Pas de perte d'info par arrondi car en kEuros dans base MinFi
                if valeurData < 2000 and arrondi > 0 and \
                   courbe['sousCle'] != "Valeur totale":
                    arrondi = 0
                    arrondiStrAffiche = ""
    arrondiStrAffiche += unite

    if verbose:
        print("arrondi =", arrondi,)
        print("arrondiStrAffiche = ", arrondiStrAffiche)
    return arrondi, arrondiStrAffiche
