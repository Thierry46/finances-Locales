# -*- coding: utf-8 -*-
"""
*********************************************************
Module : genCodeGraphiques.py
Auteur : Thierry Maillard (TMD)
Date : 24/5/2015 - 21/6/2019

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

def genCodeGraphiques(config, repVille, dictAllGrandeur,
                      textSection, nomEntite,
                      listAnnees, isComplet,
                      isWikicode, isMatplotlibOk,
                      verbose):
    """
    Génere le Wikicode pour tous les graphiques d'une ville
    ou d'un groupementde communes.
    """
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
                        'cle' : 'total des produits de fonctionnement',
                        'sousCle' : "Valeur totale",
                        'libelle' : 'Produits',
                        'couleur' : bleuFonce,
                        'couleurMPL' : 'turquoise'
                    },
                    {
                        'cle' : 'total des charges de fonctionnement',
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
                        'cle' : "total des emplois investissement",
                        'sousCle' : "Valeur totale",
                        'libelle' : "Emplois",
                        'couleur' : vertFonce,
                        'couleurMPL' : 'chartreuse'
                    },
                    {
                        'cle' : "total des ressources d'investissement",
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
                        'cle' : "dont impôts locaux",
                        'sousCle' : "Valeur totale",
                        'libelle' : 'Impôts Locaux',
                        'couleur' : bleuFonce,
                        'couleurMPL' : 'turquoise'
                    },
                    {
                        'cle' : "autres impôts et taxes",
                        'sousCle' : "Valeur totale",
                        'libelle' : 'autres impôts et taxes',
                        'couleur' : rougeFonce,
                        'couleurMPL' : 'salmon'
                    },
                    {
                        'cle' : "dotation globale de fonctionnement",
                        'sousCle' : "Valeur totale",
                        'libelle' : 'dotation globale de fonctionnement',
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
                        'cle' : "dont charges de personnel",
                        'sousCle' : "Valeur totale",
                        'libelle' : "Charges de personnel",
                        'couleur' : bleuFonce,
                        'couleurMPL' : 'turquoise'
                    },
                    {
                        'cle' : "achats et charges externes",
                        'sousCle' : "Valeur totale",
                        'libelle' : "achats et charges externes",
                        'couleur' : rougeFonce,
                        'couleurMPL' : 'salmon'
                    },
                ]
        }
    listeGraphiques.append(courbesChargesPersonnelsExternes)
    courbesChargesPersonnelsExternes = \
        {
            'nomGraphique' : "CHARGES_FINANCIERES_SUBVENTIONS_VERSEES",
            'titreGrahique' : "G1b2 - charges financières et des subventions versées",
            'largeur' : 'graph.largeurPage',
            'unite' : 'euros',
            'courbes' :
                [
                    {
                        'cle' : "charges financières",
                        'sousCle' : "Valeur totale",
                        'libelle' : "charges financières",
                        'couleur' : vertFonce,
                        'couleurMPL' : 'chartreuse'
                    },
                    {
                        'cle' : "subventions versées",
                        'sousCle' : "Valeur totale",
                        'libelle' : "subventions versées",
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
                        'cle' : "capacité autofinancement caf par habitant",
                        'sousCle' : "Par habitant",
                        'libelle' : 'CAF',
                        'couleur' : bleuFonce,
                        'couleurMPL' : 'turquoise'
                    },
                    {
                        'cle' : 'encours de la dette au 31 12 n par habitant',
                        'sousCle' : "Par habitant",
                        'libelle' : 'Encours total de la dette',
                        'couleur' : rougeFonce,
                        'couleurMPL' : 'salmon'
                    }
                ]
            }
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
                        'cle' : "dont dépenses équipement",
                        'sousCle' : "Valeur totale",
                        'libelle' : "Dépenses d'équipement",
                        'couleur' : bleuFonce,
                        'couleurMPL' : 'turquoise'
                    },
                    {
                        'cle' : "remboursement emprunts et dettes assimilées",
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
                        'cle' : "dont emprunts bancaires et dettes assimilées",
                        'sousCle' : "Valeur totale",
                        'libelle' : 'Nouvelles dettes',
                        'couleur' : rougeFonce,
                        'couleurMPL' : 'salmon'
                    },
                    {
                        'cle' : "subventions reçues",
                        'sousCle' : "Valeur totale",
                        'libelle' : 'subventions reçues',
                        'couleur' : bleuFonce,
                        'couleurMPL' : 'turquoise'
                    },
                    {
                        'cle' : "fctva",
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
                        'cle' : 'ratio dette / caf',
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
                        'cle' : "taux taxe habitation",
                        'sousCle' : "Taux",
                        'libelle' : "taux taxe habitation",
                        'couleur' : bleuFonce,
                        'couleurMPL' : 'turquoise'
                    },
                    {
                        'cle' : 'taux taxe foncière bâti',
                        'sousCle' : "Taux",
                        'libelle' : 'taux foncier bâti',
                        'couleur' : rougeFonce,
                        'couleurMPL' : 'salmon'
                    }
                ]
        }
    if isComplet:
        courbesTaxes['courbes'].extend(
            [
                {
                    'cle' : "taux taxe habitation moyen",
                    'sousCle' : "taux moyen pour la strate",
                    'libelle' : "taux taxe habitation",
                    'couleur' : vertFonce,
                    'couleurMPL' : 'chartreuse'
                },
                {
                    'cle' : 'taux taxe foncière bâti moyen',
                    'sousCle' : "taux moyen pour la strate",
                    'libelle' : 'taux foncier bâti',
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
                        'cle' : "taux taxe foncière non bâti",
                        'sousCle' : "Taux",
                        'libelle' : 'taux foncier non bâti',
                        'couleur' : rougeFonce,
                        'couleurMPL' : 'salmon'
                    }
                ]
        }
    if isComplet:
        courbesTaxesNB['courbes'].extend(
            [
                {
                    'cle' : "taux taxe foncière non bâti moyen",
                    'sousCle' : "taux moyen pour la strate",
                    'libelle' : 'taux foncier non bâti',
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

        controleSousCle(graphique, verbose)

        # Elimination des courbes vides et
        # des années non présentes dans toutes les autres
        try:
            anneesOK = controleSeries(dictAllGrandeur, graphique['courbes'],
                                      listAnnees, verbose)
            # Détermination de l'arrondi à utiliser et à afficher
            listeCles = [courbe['cle']
                         for courbe in graphique['courbes']
                         if courbe['sousCle'] == "Valeur totale"]
            if listeCles:
                arrondi, arrondiStr, arrondiStrAffiche = \
                    utilitaires.setArrondi(dictAllGrandeur["Valeur totale"], anneesOK,
                                           1000.0, listeCles, verbose)
            else:
                arrondi = 1.0
                arrondiStr = graphique['unite']
                arrondiStrAffiche = arrondiStr

            # Generation des graphiques
            if isWikicode:
                graphiqueWiki, legendeVille, legendeStrate = \
                genWikiCodeGraphiques.genGraphique(config, dictAllGrandeur,
                                                   nomEntite, anneesOK,
                                                   graphique['courbes'],
                                                   graphique['largeur'],
                                                   arrondi,
                                                   arrondiStrAffiche,
                                                   verbose)
                textSection = textSection.replace("<GRAPHIQUE_" + graphique['nomGraphique'] + ">",
                                                  graphiqueWiki)
                textSection = textSection.replace("<LEGENDE_" + graphique['nomGraphique'] + ">",
                                                  legendeVille)
                tag = "<LEGENDE_STRATE_" + graphique['nomGraphique'] + ">"
                textSection = textSection.replace(tag, legendeStrate)
            elif isMatplotlibOk:
                textLien = genHTMLCodeGraphiques.genGraphique(repVille, dictAllGrandeur,
                                                              graphique['nomGraphique'],
                                                              graphique['titreGrahique'],
                                                              nomEntite, anneesOK,
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
        except ValueError as exc:
            print(str(exc) + "\n pour la ville ou le groupement " + nomEntite +
                  " et graphique " + graphique['nomGraphique'])
            textSection = textSection.replace("<GRAPHIQUE_" + graphique['nomGraphique'] + ">",
                                              "Graphique non disponible, " + \
                                              " problème de données !<br/>")

    if verbose:
        print("Sortie de genCodeGraphiques")

    return textSection


def controleSeries(dictAllGrandeur, courbes, listAnnees, verbose):
    """
    Contrôle des series pour eliminer les series vides
    et ne tracer que les séries restantes qui ont des annees communes
    """
    if verbose:
        print("\nEntree dans controleSeries")
        print('dictAllGrandeur=', dictAllGrandeur)
        print('courbes=', courbes)
        print("Nombre de courbes :", len(courbes))
        print("listAnnees :", listAnnees)

    assert courbes, "Erreur appel controleSeries() : Aucune courbe à controler !"

    # Recupération liste des années valides pour chaque clé
    # et conservation des seules clés qui ont au moins une année valide
    anneesOKParCle = dict()
    setCles = {courbe['sousCle'] + ":" + courbe['cle'] for courbe in courbes}
    for cleAll in setCles:
        sousCle, cle = cleAll.split(":")
        # Pour le ratio dette/caf, la sous-clé n'est pas définie
        if sousCle != '':
            anneesOK1serie = set(annee for annee in listAnnees
                                 if sousCle in dictAllGrandeur and
                                 cle in dictAllGrandeur[sousCle] and
                                 annee in dictAllGrandeur[sousCle][cle])
        else:
            anneesOK1serie = set(annee
                                 for annee in listAnnees
                                 if cle in dictAllGrandeur and
                                 annee in dictAllGrandeur[cle])

        if len(anneesOK1serie) > 0:
            anneesOKParCle[cle] = anneesOK1serie

    # Détermination des annees communes aux clés restantes
    anneesOK = set(listAnnees)
    for cle in anneesOKParCle:
        anneesOK &= anneesOKParCle[cle]

    # Conservation des seules series (courbes) qui ont des annees communes
    # By assigning to the slice courbes[:], we mutate the existing list
    # to contain only the correct items:
    # This approach is needed because there are other references to courbes
    # that need to reflect the changes
    # Ref : stackoverflow.com/questions/1207406/how-to-remove-items-from-a-list-while-iterating
    courbes[:] = [courbe for courbe in courbes
                  if courbe['cle'] in anneesOKParCle]

    # Un graphique sans courbe doit être considéré comme une erreur
    if not courbes:
        raise ValueError("Erreur : pas de courbe pour le graphique")

    if verbose:
        print("Sortie de controleSeries")
        print("Nombre de courbes :", len(courbes))
        print("listeCle OK =", [courbe['cle'] for courbe in courbes])
        print("anneeOK =", anneesOK)

    # Le tri des chaines de caractere est ici acceptable pour des annees sur 4 chiffres
    return sorted(list(anneesOK))

def controleSousCle(graphique, verbose):
    """
    Les sous-clés des courbes du graphique doivent être compatibles :
    les taux et valeurs par habitant ne doivent pas être mélangé dans
    une même courbe avec d'autres sous-clé
    """

    if verbose:
        print("\nEntree dans controleSousCle")
        print('graphique=', graphique)
        print("Nombre de courbes du graphique :", len(graphique))

    sousCleUnique = list({courbe['sousCle'] for courbe in graphique['courbes']})
    if not sousCleUnique:
        raise ValueError("Aucune sous clé pour la courbe " +
                         graphique['nomGraphique'])
    nbSousCleTaux = 0
    nbSousCleAutre = 0
    for sousCle in sousCleUnique:
        if sousCle.lower().startswith("taux"):
            nbSousCleTaux += 1
        else:
            nbSousCleAutre += 1
    if nbSousCleTaux != 0 and nbSousCleAutre != 0:
        raise ValueError("Les sous clé commençant par taux ne doivent " +
                         "pas être combinées à d'autres dans la courbe " +
                         graphique['nomGraphique'])

    nbSousCleParHabitant = 0
    for sousCle in sousCleUnique:
        if sousCle == "Par habitant":
            nbSousCleParHabitant += 1
    if nbSousCleParHabitant != 0 and len(sousCleUnique) != 1:
        raise ValueError("Les sous clé Par habitant " +
                         "pas être combinées à d'autres dans la courbe " +
                         graphique['nomGraphique'])

    if verbose:
        print("Sortie de controleSousCle : OK")
