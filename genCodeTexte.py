# -*- coding: utf-8 -*-
"""
*********************************************************
Module : genCodeTexte.py
Auteur : Thierry Maillard (TMD)
Date : 24/5/2015 - 8/12/2019

Role : Transforme les donnees traitées par extractionMinFi.py
        en wikicode pour les partie textuelles.
------------------------------------------------------------
Licence : GPLv3 (en français dans le fichier gpl-3.0.fr.txt)
Copyright (c) 2015 - 2019 - Thierry Maillard
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
import time
import re

import utilitaires
import genCodeCommon

def genTexte(config, dictAllGrandeur, infosGroupement,
             modele, textSection, ville,
             listAnnees, nomProg, isWikicode, verbose):
    """
        Expanse les tags concernant du txte simple pour une ville donnée,
        les mots clés de type textuels du modèle.
        dictAllGrandeur contient toutes les données financières pour cette ville
        infosGroupement contient les infos relatives au groupement de commune
        de rattachement,
        Le texte du modèle en entrée est fourni dans la chaine textSection.
        Le type de sortie peut être du Wikicode ou du HTML.
        Le texte résultat est retourné à l'appelant.
    """

    if verbose:
        print("Entree dans genTexte")
        print('ville=', ville)
        print("modele :", modele)
        print("isWikicode =", isWikicode)

    textSection = textSection.replace("<ANNEE>", str(listAnnees[0]))
    textSection = textSection.replace("<ANNEE-1>", str(listAnnees[1]))
    textSection = textSection.replace("<ANNEE0>", str(listAnnees[-1]))

    # Commentaire de traçabilité
    outilNom = config.get('Version', 'version.appName')
    textSection = textSection.replace("<OUTIL_NOM>", outilNom)
    textSection = textSection.replace("<NOM_PROG>", nomProg)
    version = config.get('Version', 'version.number') + " : " + \
              config.get('Version', 'version.nom')
    textSection = textSection.replace("<VERSION>", version)

    if isWikicode:
        versionPicto = config.get('Version', 'version.picto')
    else:
        versionPicto = config.get('Version', 'version.pictoHTML')
    textSection = textSection.replace("<VERSION_PICTO>", versionPicto)
    versionDate = config.get('Version', 'version.date')
    textSection = textSection.replace("<VERSION_DATE>", versionDate)
    textSection = textSection.replace("<OPTIONS>",
                                      config.get('Modele', 'modele.type'))
    textSection = textSection.replace("<NOM_MODELE>", modele)

    # Tags pour la ville
    articleVille = "de "
    if ville[1][0] in "AEIOUYH":
        articleVille = "d'"
    textSection = textSection.replace("<ARTICLE_VILLE>", articleVille)
    textSection = textSection.replace("<VILLE>", ville[1])
    textSection = textSection.replace("<VILLE_LIEN>", ville[2])
    nomArticleDetail = config.get('GenCode', 'gen.prefixePagedetail') + \
                       " " + articleVille + ville[1]
    textSection = textSection.replace("<NOM_ARTICLE_DETAIL>", nomArticleDetail)
    # Construction du nom de département avec article
    article = ville[3]
    if not article.endswith("'"):
        article += " "
    nomDepartement = ville[4]
    categorieArticle = config.get('GenCode', 'gen.prefixeCategorieArticle') + \
                       " " + article + nomDepartement
    textSection = textSection.replace("<CATEGORIE_ARTICLE>", categorieArticle)

    # Info du groupement d'appartenance
    lienGroupement = "aucun groupement d'appartenance"
    print("infosGroupement=", infosGroupement)
    if infosGroupement:
        print("infosGroupement[1:2]=", infosGroupement[1:2])
        lienGroupement = genCodeCommon.genLien(config, infosGroupement[1:2],
                                               isWikicode, verbose)
    textSection = textSection.replace("<LIEN_GROUPEMENT>", lienGroupement)

    # Budget général
    codeCle = "total des charges de fonctionnement"
    chargesF = dictAllGrandeur["Valeur totale"][codeCle][listAnnees[0]] * 1e3
    codeCle = "total des emplois investissement"
    emploisI = dictAllGrandeur["Valeur totale"][codeCle][listAnnees[0]] * 1e3
    depensesTotal = chargesF + emploisI
    textSection = textSection.replace("<DEPENSES_TOTAL>", f"{depensesTotal:.0f}")
    textSection = textSection.replace("<CHARGES_FONCTIONNEMENT>", f"{chargesF:.0f}")
    textSection = textSection.replace("<EMPLOIS_INVEST>", f"{emploisI:.0f}")

    codeCle = "total des produits de fonctionnement"
    produitsF = dictAllGrandeur["Valeur totale"][codeCle][listAnnees[0]] * 1e3
    codeCle = "total des ressources d'investissement"
    ressourcesI = dictAllGrandeur["Valeur totale"][codeCle][listAnnees[0]] * 1e3
    recettesTotal = produitsF + ressourcesI
    textSection = textSection.replace("<RECETTES_TOTAL>", f"{recettesTotal:.0f}")
    textSection = textSection.replace("<PRODUITS_FONCTIONNEMENT>", f"{produitsF:.0f}")
    textSection = textSection.replace("<RESSOURCES_INVEST>", f"{ressourcesI:.0f}")

    # Fonctionnement
    codeCle = "resultat comptable"
    resultatC = dictAllGrandeur["Valeur totale"][codeCle][listAnnees[0]] * 1e3
    textSection = textSection.replace("<RESULTAT_COMPTABLE>", f"{resultatC:.0f}")
    codeCle = "resultat comptable par habitant"
    resultatCpH = dictAllGrandeur["Par habitant"][codeCle][listAnnees[0]]
    textSection = textSection.replace("<RESULTAT_COMPTABLE_PAR_HAB>", f"{resultatCpH:.0f}")
    codeCle = "total des charges de fonctionnement par habitant"
    ChargesFpH = dictAllGrandeur["Par habitant"][codeCle][listAnnees[0]]
    textSection = textSection.replace("<CHARGES_FONCTIONNEMENT_PAR_HAB>", f"{ChargesFpH:.0f}")
    codeCle = "total des produits de fonctionnement par habitant"
    ProduitsFpH = dictAllGrandeur["Par habitant"][codeCle][listAnnees[0]]
    textSection = textSection.replace("<PRODUITS_FONCTIONNEMENT_PAR_HAB>", f"{ProduitsFpH:.0f}")

    # Variation DGF
    codeCle = "dotation globale de fonctionnement"
    dgf = dictAllGrandeur["Valeur totale"][codeCle][listAnnees[0]] * 1e3
    dgfm1 = dictAllGrandeur["Valeur totale"][codeCle][listAnnees[1]] * 1e3
    tendanceDGFstr = utilitaires.calculeTendance(config, dgf, dgfm1)
    textSection = textSection.replace("<TENDANCE_DGF>", tendanceDGFstr)

    # ratio Dette / CAF
    textSection = textSection.replace("<RATIO_N>", dictAllGrandeur["ratio n"])
    textSection = textSection.replace("<TENDANCE_RATIO_DETTE_CAF>",
                                      dictAllGrandeur["tendance ratio"])

    # Réferences
    urlMinFi = config.get('Extraction', 'dataGouvFr.Comptes')
    textSection = textSection.replace("<URL_BASE>", urlMinFi)
    textSection = textSection.replace("<DATE>", time.strftime("%d %B %G"))

    # Commentaire definition strate
    defStrate = ville[5] + ' ' + ville[6]
    defStrate = defStrate.replace('Strate :', 'La strate regroupe les')
    if isWikicode:
        strateWikif = wikifieStrate(defStrate, verbose)
    else:
        strateWikif = defStrate
    textSection = textSection.replace("<DEF_STRATE>", strateWikif)

    if verbose:
        print("textSection resultat =\n", textSection)
        print("Sortie de genTexte")

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
