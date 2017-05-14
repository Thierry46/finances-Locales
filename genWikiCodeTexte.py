# -*- coding: utf-8 -*-
"""
*********************************************************
Module : genWikiCodeTexte.py
Auteur : Thierry Maillard (TMD)
Date : 24/5/2015 - 3/6/2015

Role : Transforme les donnees traitées par extractionMinFi.py
        en wikicode pour les partie textuelles.
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
import urllib.parse
import time
import re

import utilitaires

def genWikiCodeTexte(config, modele, textSection, ville,
                     listAnnees, nomProg, verbose):
    """ Génère tout le wikicode des parties texte pour une ville """

    if verbose:
        print("Entree dans genWikiCodeTexte")
        print('ville=', ville['nom'])
        print("modele :", modele)

    textSection = textSection.replace("<ANNEE>", str(listAnnees[0]))
    textSection = textSection.replace("<ANNEE-1>", str(listAnnees[0]-1))
    textSection = textSection.replace("<ANNEE0>", str(listAnnees[-1]))
    textSection = textSection.replace("<NB_ANNEE_TOTAL>", str(len(listAnnees)))

    # Commentaire de traçabilité
    outilNom = config.get('Version', 'version.appName')
    textSection = textSection.replace("<OUTIL_NOM>", outilNom)
    textSection = textSection.replace("<NOM_PROG>", nomProg)
    version = config.get('Version', 'version.number') + " : " + \
              config.get('Version', 'version.nom')
    textSection = textSection.replace("<VERSION>", version)
    versionPicto = config.get('Version', 'version.picto')
    textSection = textSection.replace("<VERSION_PICTO>", versionPicto)
    versionDate = config.get('Version', 'version.date')
    textSection = textSection.replace("<VERSION_DATE>", versionDate)
    textSection = textSection.replace("<OPTIONS>",
                                      config.get('Modele', 'modele.type'))
    textSection = textSection.replace("<NOM_MODELE>", modele)

    # Tags pour la ville
    articleVille = "de "
    if ville['nom'][0] in "AEIOUYH":
        articleVille = "d'"
    textSection = textSection.replace("<ARTICLE_VILLE>", articleVille)
    textSection = textSection.replace("<VILLE>", ville['nom'])
    textSection = textSection.replace("<VILLE_LIEN>", ville['nomWkpFr'])
    nomArticleDetail = config.get('GenWIkiCode', 'gen.prefixePagedetail') + \
                       " " + articleVille + ville['nom']
    textSection = textSection.replace("<NOM_ARTICLE_DETAIL>", nomArticleDetail)
    categorieArticle = config.get('GenWIkiCode', 'gen.prefixeCategorieArticle') + \
                       " " + ville['nomDepStr']
    textSection = textSection.replace("<CATEGORIE_ARTICLE>", categorieArticle)

    # Budget général
    chargesF = utilitaires.getValeurIntTotale(ville,
                                              'TOTAL DES CHARGES DE FONCTIONNEMENT',
                                              listAnnees[0])
    emploisI = utilitaires.getValeurIntTotale(ville,
                                              "TOTAL DES EMPLOIS D'INVESTISSEMENT",
                                              listAnnees[0])
    depensesTotal = chargesF + emploisI
    textSection = textSection.replace("<DEPENSES_TOTAL>", str(depensesTotal))
    textSection = textSection.replace("<CHARGES_FONCTIONNEMENT>", str(chargesF))
    textSection = textSection.replace("<EMPLOIS_INVEST>", str(emploisI))

    produitsF = utilitaires.getValeurIntTotale(ville,
                                               'TOTAL DES PRODUITS DE FONCTIONNEMENT',
                                               listAnnees[0])
    ressourcesI = utilitaires.getValeurIntTotale(ville,
                                                 "TOTAL DES RESSOURCES D'INVESTISSEMENT",
                                                 listAnnees[0])
    recettesTotal = produitsF + ressourcesI
    textSection = textSection.replace("<RECETTES_TOTAL>", str(recettesTotal))
    textSection = textSection.replace("<PRODUITS_FONCTIONNEMENT>", str(produitsF))
    textSection = textSection.replace("<RESSOURCES_INVEST>", str(ressourcesI))

    # Fonctionnement
    textSection = textSection.replace("<RESULTAT_COMPTABLE>",
                                      utilitaires.getValeur(ville, 'RESULTAT COMPTABLE',
                                                            listAnnees[0], "Valeur totale"))
    textSection = textSection.replace("<RESULTAT_COMPTABLE_PAR_HAB>",
                                      utilitaires.getValeur(ville, 'RESULTAT COMPTABLE',
                                                            listAnnees[0], "Par habitant"))
    textSection = \
        textSection.replace("<CHARGES_FONCTIONNEMENT_PAR_HAB>",
                            utilitaires.getValeur(ville,
                                                  'TOTAL DES CHARGES DE FONCTIONNEMENT',
                                                  listAnnees[0], "Par habitant"))
    textSection = \
        textSection.replace("<PRODUITS_FONCTIONNEMENT_PAR_HAB>",
                            utilitaires.getValeur(ville,
                                                  'TOTAL DES PRODUITS DE FONCTIONNEMENT',
                                                  listAnnees[0], "Par habitant"))

    # Variation DGF
    dgf = float(utilitaires.getValeur(ville, 'Dotation globale de fonctionnement',
                                      listAnnees[0], "Valeur totale"))
    dgfm1 = float(utilitaires.getValeur(ville, 'Dotation globale de fonctionnement',
                                        listAnnees[0]-1, "Valeur totale"))
    tendanceDGFstr = utilitaires.calculeTendance(config, dgf, dgfm1)
    textSection = textSection.replace("<TENDANCE_DGF>", tendanceDGFstr)

    # ratio Dette / CAF
    ratioCAFDette = ville['data']['ratioCAFDette'][str(listAnnees[0])]
    textSection = textSection.replace("<RATIO_N>",
                                      utilitaires.presentRatioDettesCAF(config,
                                                                        ratioCAFDette,
                                                                        verbose))
    textSection = textSection.replace("<TENDANCE_RATIO_DETTE_CAF>",
                                      ville['data']['tendanceRatio'])

    # Réferences
    urlMinFi = config.get('Extraction', 'extraction.urlMinFi')
    textSection = textSection.replace("<URL_BASE>",
                                      "[" + config.get('GenWIkiCode', 'gen.siteAlize2') + \
                                      " " + urllib.parse.urlparse(urlMinFi).netloc + "]")
    nbPages = len(listAnnees) * 7
    textSection = textSection.replace("<NB_PAGES_MINFI>", str(nbPages))
    for numtTab in list(ville['ref'].keys()):
        textSection = textSection.replace("<REF_NAME"+str(numtTab)+">",
                                          ville['ref'][numtTab]['refName'])
        textSection = textSection.replace("<URL_TAB"+str(numtTab)+">",
                                          ville['ref'][numtTab]['url'])
        textSection = textSection.replace("<URL_NOMPAGE"+str(numtTab)+">",
                                          ville['ref'][numtTab]['nomPage'].lower())
    textSection = textSection.replace("<REF_NAME_DETAIL>", ville['refDetail']['refName'])
    textSection = textSection.replace("<URL_TAB_DETAIL>", ville['refDetail']['url'])
    textSection = textSection.replace("<URL_NOMPAGE_DETAIL>",
                                      ville['refDetail']['nomPage'].lower())
    textSection = textSection.replace("<DATE>", time.strftime("%d %B %G"))

    # Commentaire definition strate
    defStrate = ville['defStrate'].replace('Strate :', 'La strate regroupe les')
    strateWikif = wikifieStrate(defStrate, verbose)
    textSection = textSection.replace("<DEF_STRATE>", strateWikif)

    if verbose:
        print("Sortie de genWikiCodeTexte")

    return textSection

def wikifieStrate(defStrate, verbose):
    """
    V1.0.1 : Wikification description strate suite
             remarque récurrente d'AntonyB
    """
    if verbose:
        print("Entree dans wikifieStrate")
        print("defStrate=", defStrate)

    # Si on ne trouve rien, on renvoie la chaine
    strateWikif = defStrate.replace("(4 taxes)", "({{nobr|4 taxes}})")

    #Recherche des formulation possibles
    if strateWikif.find("moins de 250 habitants") != -1:
        strateWikif = strateWikif.replace("moins de 250 habitants",
                                          "moins de {{unité|250|habitants}}")
    elif strateWikif.find("plus de 100 000 habitants") != -1:
        strateWikif = strateWikif.replace("plus de 100 000 habitants",
                                          "plus de {{unité|100000|habitants}}")
    else:
        # Récupère les deux nombres autour de la lettre à
        # Ces nombres sont composés de chiffres et de blanc
        posA = strateWikif.find(" à ")
        if posA != -1:
            strateWikif2 = strateWikif.split(" à ")
            listNb1 = re.findall(r'\d{1,3}', strateWikif2[0])
            startNb1 = strateWikif.find(listNb1[0])
            nb1 = "".join(listNb1)
            listNb2 = re.findall(r'\d{1,3}', strateWikif2[1])
            endNb2 = strateWikif.find("habitants") + len("habitants")
            nb2 = "".join(listNb2)
            strateWikif = strateWikif[:startNb1] + \
                          "{{unité/2|"+nb1+"|à="+nb2 +"|habitants}}" + \
                          strateWikif[endNb2:]

    # Suppresion abbréviation (FPU)
    strateWikif = strateWikif.replace(" (FPU)", "")

    if verbose:
        print("strateWikif=", strateWikif)
        print("Sortie de wikifieStrate")
    return strateWikif

