# -*- coding: utf-8 -*-
"""
*********************************************************
Programme : genereCode1Groupement.py
Auteur : Thierry Maillard (TMD)
Date : 13/5/2020 - 2/7/2020

Role : Genere le wikicode et le HTML pour un groupement de communes.

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

import os
import os.path

import utilitaires
import database
import genCodeCommon
import genCodeGroupementTexte
import genCodeGroupementTableaux
import genCodeGraphiques
import genCodeTableaux
import genHTML

def traite1Groupement(config, groupement,
                      repertoireGroupements,
                      connDB, nomProg,
                      isMatplotlibOk,
                      verbose):
    """
    Traite un groupement de commune :
    Genere le Wikicode et le HTML
    """
    if verbose:
        print("Sortie de traite1Groupement")

    auMoins1GroupementGenere = False

    dictNomsGroupement = utilitaires.getNomsGroupement(groupement[2],
                                                       repertoireGroupements,
                                                       verbose)
    print(dictNomsGroupement['nom'], 'sur disque',
          dictNomsGroupement['repGroupement'], '...')

    # on ne génère pas un groupement dont le répertoire existe
    if os.path.isdir(dictNomsGroupement['repGroupement']):
        print(groupement[3], "Siren:", groupement[1],
              "ignoréée car le répertoire",
              dictNomsGroupement['repGroupement'], "existe.")
    else:
        auMoins1GroupementGenere = True
        if verbose:
            print("Creation répertoire du groupement :",
                  dictNomsGroupement['repGroupement'])

        os.makedirs(dictNomsGroupement['repGroupement'])

        for typeCode in ["wikicode", "HTML"]:
            textSection = genereCode1Groupement(config, connDB,
                                                dictNomsGroupement['repGroupement'],
                                                groupement, nomProg, typeCode,
                                                isMatplotlibOk, verbose)

            if typeCode == "wikicode":
                extensionFic = '.txt'
            elif typeCode == "HTML":
                extensionFic = '.html'

            # Ecriture du fichier du Wikicode et du fichier html
            # Inclusion des fichiers Wikicode dans des fichiers HTML pour
            # éviter problèmes d'encodage et travaller uniquement dans un navigateur Web.
            nomFic = utilitaires.construitNomFic(dictNomsGroupement['repGroupement'],
                                                 dictNomsGroupement['groupementNomDisque'],
                                                 typeCode, extensionFic)
            if verbose:
                print("Ecriture du code dans :", nomFic)
            with open(nomFic, 'w') as ficGroupement:
                ficGroupement.write(textSection)

            if typeCode == "wikiArticle":
                genHTML.convertWikicode2Html(config, nomFic, verbose)

    if verbose:
        print("Sortie de traite1Groupement")
        print("auMoins1GroupementGenere=", auMoins1GroupementGenere)
    return auMoins1GroupementGenere

def genereCode1Groupement(config, connDB, repGroupement, groupement,
                          nomProg, typeCode, isMatplotlibOk, verbose):
    """ Génère le Wikicode pour un groupement """
    if verbose:
        print("Entree dans genereWikicode1Groupement")
        print("repGroupement=", repGroupement)
        print("typeCode=", typeCode)
        print('groupement =', groupement)
        print('isMatplotlibOk', isMatplotlibOk)

    isWikicode = True if typeCode == "wikicode" else False
    modele = 'modele_groupement_' + typeCode + '.txt'
    isComplet = False
    isGroupement = True

    # Lecture du fichier modèle
    with open(modele, 'r') as modelefile:
        textSection = modelefile.read()

        # Récupère toutes les données concernant ce groupement
        dictAllGrandeur = database.getAllValeursDataMinFi4Entite(connDB, "GC",
                                                                 groupement[0],
                                                                 verbose)

        # On ne génère pas les communauté de communes sans donnée MinFi
        if "Valeur totale" in dictAllGrandeur:
            listAnnees = database.getListeAnneesDataMinFi4Entite(connDB, 'GC',
                                                                 groupement[0],
                                                                 verbose)

            # Agglomère certaines grandeurs et complète dictAllGrandeur
            genCodeCommon.calculeGrandeur(config, dictAllGrandeur,
                                          listAnnees, isWikicode,
                                          verbose)

            # Modification des valeurs simples
            textSection = genCodeGroupementTexte.genTexte(config, dictAllGrandeur,
                                                          modele, textSection,
                                                          groupement, listAnnees, nomProg,
                                                          isWikicode, verbose)

            # Définit le contenu des tableaux picto
            grandeursAnalyse = genCodeGroupementTableaux.defTableauxGroupementPicto(config,
                                                                                    dictAllGrandeur,
                                                                                    listAnnees,
                                                                                    isWikicode,
                                                                                    verbose)

            # Génération des tableaux pictogrammes
            textSection = genCodeCommon.genCodeTableauxPicto(config,
                                                             dictAllGrandeur,
                                                             grandeursAnalyse,
                                                             textSection,
                                                             listAnnees,
                                                             isComplet,
                                                             isWikicode,
                                                             False,
                                                             isGroupement,
                                                             verbose)
             # Génération des tableaux
            textSection = genCodeTableaux.genCodeTableaux(config, dictAllGrandeur,
                                                          textSection,
                                                          listAnnees, False,
                                                          isWikicode,
                                                          verbose)

            # Generation des graphiques
            textSection = genCodeGraphiques.genCodeGraphiques(config,
                                                              repGroupement,
                                                              dictAllGrandeur,
                                                              textSection,
                                                              groupement[2],
                                                              listAnnees,
                                                              False,
                                                              isWikicode,
                                                              isMatplotlibOk,
                                                              verbose)

    if verbose:
        print("Sortie de genereCode1Groupement")

    return textSection
