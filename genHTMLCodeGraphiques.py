# -*- coding: utf-8 -*-
"""
*********************************************************
Module : genHTMLCodeGraphiques.py
Auteur : Thierry Maillard (TMD)
Date : 10/10/2015 - 22/10/2015

Role : Génère les graphiques SVG pour les données traitées
        par extractionMinFi.py.
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
# Le rendu des graphiques est très lent avec le backend MacOSX
# La fenetre X11 s'affiche.
# Affichage backend courant : matplotlib.get_backend()
# Affichage tous les backends :
#   import matplotlib.rcsetup as rc
#   print (rc.all_backends)
# Perf (time) bacends pour produire les graphiques de 2 villes : 2*10 png
# MacOSX : 12.12 (raster png)
# agg : 11,52s (raster png)
# Choisi : svg : 9.906s (vectoriel)

import matplotlib
# Changement de backend : svg : rapide et vectoriel
matplotlib.use('svg')
import matplotlib.pyplot as plt
import utilitaires
import os
import os.path

def genGraphique(repVille, nomGraphique, titreGrahique, ville,
                 anneesOK, courbes,
                 arrondi, arrondiStrAffiche,
                 verbose):
    """ Génere un graphique vectoriel SVG et retourne un lien HTML dessus """
    if verbose:
        print("Entree dans genGraphique (HTML)")

    # Génération du lien HTML
    nomImage = nomGraphique + '.svg'
    textLien = '<img alt="' + titreGrahique + '" src="' + nomImage + '">'
    #  width="100%"
    cheminImage = os.path.join(repVille, nomImage)

    nbSeries = len(courbes)
    largeurBarre = 1./(float(nbSeries) + 1.)

    fig, ax = plt.subplots(facecolor='white')
    ax.set_title(ville["nom"] + ' - ' + titreGrahique)

    # Graduation en années de l'axe des abscisses
    positionsAbsisses = [float(x + float(nbSeries) * largeurBarre / 2.0)
                         for x in range(len(anneesOK))]
    xlabels = [str(anneesOK[indice]) for indice in range(len(anneesOK))]
    plt.xticks(positionsAbsisses, xlabels, rotation='vertical')

    # Si valeur totale -> une seule série : on peut qualifier l'axe des Y
    # Sinon, par habitant [+ strate]
    yAxisLabel = 'Valeurs'
    if courbes[0]['sousCle'] == 'Valeur totale':
        yAxisLabel += " totales"
    elif courbes[0]['sousCle'] == 'Par habitant':
        yAxisLabel += " par habitant"
    elif "Taux" in courbes[0]['libelle']:
        yAxisLabel += " des taux"
    yAxisLabel += ' en ' + arrondiStrAffiche
    ax.set_ylabel(yAxisLabel)

    # Test si des donnéees de la srates sont à tracer
    # Si non -> pas de nom de ville dans les libellés
    isStrateInCourbes = False
    for courbe in courbes:
        if 'strate' in courbe['sousCle']:
            isStrateInCourbes = True

    # Valeurs des barres
    numCourbe = 0
    for courbe in courbes:
        valeurs = []
        for annee in anneesOK:
            if courbe['cle'].startswith('Taux'):
                valeurData = float(utilitaires.getValeurFloat(ville, courbe['cle'],
                                                              annee, courbe['sousCle']))
            elif courbe['sousCle'] == "":
                valeurData = ville['data'][courbe['cle']][str(annee)]
            else:
                valeurData = int(utilitaires.getValeur(ville, courbe['cle'],
                                                       annee, courbe['sousCle'],
                                                       arrondi))
            valeurs.append(valeurData)
        positionsAbsisses = [float(x + (float(numCourbe) * largeurBarre))
                             for x in range(len(anneesOK))]

        # v2.1.0 : clarification legende des courbes
        labelSerie = ""
        if courbe['sousCle'] != 'Valeur totale':
            if 'strate' in courbe['sousCle']:
                labelSerie += 'strate : '
            elif isStrateInCourbes:
                labelSerie += ville["nom"] + ' : '
        labelSerie += courbe['libelle']
        labelSerie = labelSerie.replace("Taux", "")
        ax.bar(positionsAbsisses, valeurs, largeurBarre,
               color=courbe['couleurMPL'],
               label=labelSerie)
        numCourbe += 1

    plt.legend(loc='best', prop={'size':10})
    plt.grid()

    print("Ecriture de", cheminImage)
    fig.savefig(cheminImage)
    plt.close() # sinon rien n'est généré

    if verbose:
        print("textLien=", textLien)
        print("Sortie de genGraphique (HTML)")

    return textLien
