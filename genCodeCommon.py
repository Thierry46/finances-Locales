# -*- coding: utf-8 -*-
"""
*********************************************************
Module : genCodeCommon.py
Auteur : Thierry Maillard (TMD)
Date : 12/4/2020 - 22/6/2020

Role : Fonctions communes à genCode* et
        à genCodeGroupement*.

-----------------------------------------------------------
Licence : GPLv3 (en français dans le fichier gpl-3.0.fr.txt)
Copyright (c) 2020 - Thierry Maillard
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
import shutil
import operator
import random

import ratioTendance
import utilitaires

def createResultDir(config, resultatsPath):
    """ Création répertoire resultat """

    if not os.path.isdir(resultatsPath):
        print("Creation repertoire résultats :", resultatsPath)
        os.makedirs(resultatsPath)
        # Copie du répertoire des images dans les résultats
        RepSrcFicAux = config.get('EntreesSorties', 'io.RepSrcFicAux')
        shutil.copytree(RepSrcFicAux, os.path.join(resultatsPath, RepSrcFicAux))
        nomNoticeTermes = config.get('EntreesSorties', 'io.nomNoticeTermes')
        shutil.copy(nomNoticeTermes, resultatsPath)

def calculeGrandeur(config, dictAllGrandeur, listAnnees, isWikicode, verbose):
    """ Aglomère certaines grandeurs et complète dictAllGrandeur """

    if verbose:
        print("Entree calculeGrandeur")
    dictAllGrandeur["tendance ratio"], dictAllGrandeur["ratio dette / caf"] = \
            ratioTendance.getTendanceRatioDetteCAF(config, dictAllGrandeur,
                                                   isWikicode, verbose)
    ratioCAFDetteN = dictAllGrandeur["ratio dette / caf"][listAnnees[0]]
    dictAllGrandeur["ratio n"] = \
                           ratioTendance.presentRatioDettesCAF(config,
                                                               ratioCAFDetteN,
                                                               isWikicode,
                                                               verbose)

    # Calcule la valeur manquante pour la clé
    # "besoin ou capacité de financement de la section investissement"
    # Qui n'est pas dans les données du MinFi pour les groupements
    # = total des emplois investissement - total des ressources d'investissement
    # Pas de strate pour un groupement de communes
    cleManquante = "besoin ou capacité de financement de la section investissement"
    cleManquanteHab = "besoin ou capacité de financement de la section investissement par habitant"
    cleEmploiInv = "total des emplois investissement"
    cleEmploiInvHab = "total des emplois investissement par habitant"
    cleRessourceInv = "total des ressources d'investissement"
    cleRessourceInvHab = "total des ressources d'investissement par habitant"
    if cleManquante not in dictAllGrandeur['Valeur totale']:
        dictValeurAnnee = dict()
        for annee in listAnnees:
            dictValeurAnnee[annee] = \
                dictAllGrandeur['Valeur totale'][cleEmploiInv][annee] - \
                dictAllGrandeur['Valeur totale'][cleRessourceInv][annee]
            dictAllGrandeur['Valeur totale'][cleManquante] = dictValeurAnnee

    if cleManquanteHab not in dictAllGrandeur['Par habitant']:
        dictValeurAnnee = dict()
        for annee in listAnnees:
            dictValeurAnnee[annee] = \
                dictAllGrandeur['Par habitant'][cleEmploiInvHab][annee] - \
                dictAllGrandeur['Par habitant'][cleRessourceInvHab][annee]
            dictAllGrandeur['Par habitant'][cleManquanteHab] = dictValeurAnnee

    if verbose:
        for grandeur in ["tendance ratio", "ratio dette / caf", "ratio n"]:
            print(grandeur, "=", dictAllGrandeur[grandeur])
        print("Sortie de calculeGrandeur")

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
        lien = '<a href="' + config.get('Extraction', 'wikipediaFr.baseUrl') + \
               defLien[0] + '" target="_blank">' + alias + '</a>'

    if verbose:
        print("Lien : ", lien)
        print("Sortie de genLien")
    return lien

def triPourCent(config, sommeValeurTotal, dictValeurs,
                avecTendance, isWikicode, avecStrate,
                verbose):
    """
    V0.8 : Classemement de grandeurs et stat
    Entree :  valeur totale, dictionnaire des valeurs à compléter
    Sortie : Liste ordonnée par valeur décroissante des cles du dictionnaire
    avecStrate : tient compte des valeurs de la strate
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

    for defValeur in dictValeurs:
        dictValeurs[defValeur]['ratioValeur'] = \
            (float(dictValeurs[defValeur]["Valeur totale"]*1e3) * 100.0) / \
             float(sommeValeurTotal)
        if dictValeurs[defValeur]['ratioValeur'] < 1.0:
            faibleStr = random.choice(["inférieures à 1"+ espacePc + "%",
                                       " plus faibles", "négligeables"])
            dictValeurs[defValeur]['ratioValeurStr'] = "des sommes " + faibleStr
        else:
            dictValeurs[defValeur]['ratioValeurStr'] = \
                "%1.f"%dictValeurs[defValeur]['ratioValeur'] + espacePc + "%"

        if avecStrate:
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

                # Si 0 pourcentage sans signification
                if dictValeurs[defValeur]["Par habitant"] != 0:
                    dictValeurs[defValeur]['ratioStrateStr'] += \
                        " de %1.f %%"%abs(dictValeurs[defValeur]['ratioStrate'])
                dictValeurs[defValeur]['ratioStrateStr'] += \
                    " à la valeur moyenne pour les communes de la même strate (" + \
                    utilitaires.modeleEuro(str(dictValeurs[defValeur]["En moyenne pour la strate"]),
                                           isWikicode)
                dictValeurs[defValeur]['ratioStrateStr'] += " par habitant)"

        # v1.0.0 : tendance des séries sur les derniéres années
        if avecTendance:
            dictAnneesValeur = dictValeurs[defValeur]['dictAnneesValeur']
            dictValeurs[defValeur]['ratioTendanceStr'] = \
                utilitaires.calculeTendanceSerieStr('ce ratio', dictAnneesValeur,
                                                    'par habitant',
                                                    isWikicode, verbose)

        if avecStrate:
            picto, alt = utilitaires.choixPicto(config, ratioStrate, isWikicode)
            dictValeurs[defValeur]['ratioStratePicto'] = picto
            dictValeurs[defValeur]['ratioStratePictoAlt'] = alt

    # tri des cles par importance decroissante
    dictCleValeur = dict()
    for defValeur in dictValeurs:
        dictCleValeur[defValeur] = dictValeurs[defValeur]["Valeur totale"]*1e3
    cleTriee = [e[0] for e in sorted(list(dictCleValeur.items()),
                                     key=operator.itemgetter(1), reverse=True)]

    if verbose:
        print("cleTriee=", cleTriee)
        print("dictValeurs=", dictValeurs)
        print("\nSortie de triPourCent")
    return cleTriee

def getValeursDict(dictAllGrandeur,
                   listeAnneesTendance, annee,
                   dictValeurs, avecStrate,
                   verbose):
    """
    V0.8 : Recuperation groupe de valeurs pour certaines années
    Résultats placés dans dictValeurs
    avecStrate si vrai : récupère aussi les valeurs pour la strate (ville)
    les groupements n'ont pas de strate.
    """
    if verbose:
        print("\nEntrée dans getValeursDict")
        print("avecStrate=", avecStrate)
        print("dictValeurs=", dictValeurs)

    # Recupération des valeurs pour les clés
    for defValeur in dictValeurs:
        cle = dictValeurs[defValeur]['cle']
        listeSousCle = ["Valeur totale", "Par habitant"]
        if avecStrate:
            listeSousCle.append("En moyenne pour la strate")
        for sousCle in listeSousCle:
            if sousCle == "Par habitant":
                cle = dictValeurs[defValeur]['cle'] + " par habitant"
            if sousCle == "En moyenne pour la strate":
                cle = dictValeurs[defValeur]['cle'] + " moyen"
            dictValeurs[defValeur][sousCle] = \
                    round(dictAllGrandeur[sousCle][cle][annee])

        # V1.0.0 : Preparation données pour calcul tendance
        cle = dictValeurs[defValeur]['cle'] + " par habitant"
        dictAnneesValeur = dict()
        for anneeTendance in listeAnneesTendance:
            dictAnneesValeur[anneeTendance] = \
                    dictAllGrandeur["Par habitant"][cle][anneeTendance]
        dictValeurs[defValeur]['dictAnneesValeur'] = dictAnneesValeur

    if verbose:
        print("dictValeurs =", dictValeurs)
        print("\nSortie de getValeursDict")

# V1.0.0 : Le modèle table est remplacé par la syntaxe de base des tableaux Wiki
# car il ne gère pas l'alignement à droite des nombres à l'intérieur des cellules
def genlignesTableauPicto(motCle, nbLignes, couleur, unite,
                          isWikicode, avecStrate, isGroupement,
                          verbose):
    """
    Genere nbLignes du tableau des pictogrammes avec mot-clés à expanser plus tard
    avecStrate : si Vrai, ajout de colonne pour les valeurs de la strate et
        une pour le pictogramme de couleur indiquant la tendance
        et une ligne en fin de tableau indiquant les valeurs des seuils en fin de tableau.
    """
    if verbose:
        print("\nEntrée dans genlignesTableauPicto")
        print("motCle=", motCle)
        print("nbLignes=", nbLignes)
        print("couleur=", couleur)
        print("avecStrate=", avecStrate)

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

        listeSousCle = ['_PAR_HABITANT',]
        if avecStrate and not isGroupement:
            listeSousCle.append('_STRATE')
        for champ in listeSousCle:
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

        if avecStrate and not isGroupement:
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

def genCodeTableauxPicto(config, dictAllGrandeur, grandeursAnalyse,
                         textSection, listAnnees,
                         isComplet, isWikicode,
                         avecStrate, isGroupement,
                         verbose):

    """
    Génère le Wikicode pour un tableau de pictogramme de comparaison
    année N et N-1
    """
    if verbose:
        print("Entrée dans genCodeTableauxPicto")
        print("dictAllGrandeur=", dictAllGrandeur)
        print("avecStrate=", avecStrate)

    # V1.0.0 : Generation des lignes des tableaux picto pour tous les dico définis plus haut
    # Les mots cles générés sont expansés par la suite
    for grandeurs in grandeursAnalyse:
        nbLignes = len(grandeurs[0])
        if not isComplet:
            nbLignes = min(nbLignes,
                           config.getint('GenWIkiCode',
                                         'gen.nbLignesTableauxPictoNonComplet'))
        lignes = genlignesTableauPicto(grandeurs[2], nbLignes,
                                       grandeurs[3], "euro",
                                       isWikicode, True,
                                       isGroupement, verbose)
        textSection = textSection.replace("<GEN_LIGNES_TABLEAU_PICTO_" + grandeurs[2] + ">",
                                          "".join(lignes))

    # Recherche des valeurs, calcul des ratios et remplacement des mots clés
    nbAnneesTendance = int(config.get('GenWIkiCode', 'gen.nbAnneesTendance'))
    listeAnneesTendance = sorted(listAnnees[:nbAnneesTendance])

    # Extraction des valeurs de la base
    listeNomsgrandeurs = [grandeurs[0][key]['cle']
                          for grandeurs in grandeursAnalyse
                          for key in grandeurs[0]]

    if verbose:
        print("listeNomsgrandeurs=", listeNomsgrandeurs)

    for grandeurs in grandeursAnalyse:
        getValeursDict(dictAllGrandeur,
                       listeAnneesTendance,
                       listAnnees[0], grandeurs[0],
                       avecStrate, verbose)
        cleTriee = triPourCent(config, grandeurs[1], grandeurs[0],
                               True, isWikicode, avecStrate,
                               verbose)
        for numValeur, text in enumerate(cleTriee, start=1):
            textSection = textSection.replace("<LIBELLE_" + grandeurs[2] + str(numValeur) + ">",
                                              text)
            textSection = textSection.replace("<VALEUR_" + grandeurs[2] + str(numValeur) +">",
                                              str(int(grandeurs[0][text]["Valeur totale"]*1e3)))
            textSection = textSection.replace("<VALEUR_" + grandeurs[2] + "_PC" + \
                                              str(numValeur) +">",
                                              grandeurs[0][text]['ratioValeurStr'])
            textSection = textSection.replace("<VALEUR_" + grandeurs[2] + "_PAR_HABITANT" + \
                                              str(numValeur) +">",
                                              str(grandeurs[0][text]["Par habitant"]))

            if avecStrate and not isGroupement:
                # v1.0.0 : précision tendances
                textSection = textSection.replace("<VALEUR_" + grandeurs[2] + "_TENDANCE" + \
                                                  str(numValeur) +">",
                                                  grandeurs[0][text]['ratioStrateStr'])
                textSection = textSection.replace("<VALEUR_" + grandeurs[2] + "_TENDANCE_SERIE" + \
                                                  str(numValeur) +">",
                                                  grandeurs[0][text]['ratioTendanceStr'])

                valStrate = grandeurs[0][text]["En moyenne pour la strate"]
                textSection = textSection.replace("<VALEUR_" + grandeurs[2] + "_STRATE" + \
                                                  str(numValeur) +">", str(valStrate))

            if isWikicode:
                note = grandeurs[0][text]["note"]
            else:
                note = '<sup><a href="../../notice.html#Note_' + \
                       grandeurs[0][text]["noteHtml"] + \
                       '">Note ' + grandeurs[0][text]["noteHtml"] + '</a></sup>'
            textSection = textSection.replace("<NOTE_" + grandeurs[2] + str(numValeur) + ">",
                                              note)

            if avecStrate and not isGroupement:
                textSection = textSection.replace("<PICTO_" + grandeurs[2] + str(numValeur) + ">",
                                                  grandeurs[0][text]['ratioStratePicto'])

                # V1.0.2 : Accessibilité : texte alternatif
                idPictoAlt = "<PICTO_ALT_" + grandeurs[2] + str(numValeur) + ">"
                textSection = textSection.replace(idPictoAlt,
                                                  grandeurs[0][text]['ratioStratePictoAlt'])
            textSection = textSection.replace("<LIBELLE_PICTO_" + grandeurs[2] + \
                                              str(numValeur) + ">",
                                              grandeurs[0][text]['libellePicto'])
            # V1.2.1 : Phrase complête pour éviter les problèmes en cas de valeur nulle
            if grandeurs[0][text]["Valeur totale"] <= 0.0:
                phrase = grandeurs[0][text]["nul"]
            else:
                phrase = text
            if isWikicode and len(grandeurs[0][text]["note"].strip()) != 0:
                phrase += '<ref group="Note">' + grandeurs[0][text]["note"] + '</ref>'
            if not isWikicode and len(grandeurs[0][text]["noteHtml"].strip()) != 0:
                phrase += '<sup><a href="../../notice.html#Note_' + \
                          grandeurs[0][text]["noteHtml"] + \
                          '">Note ' + grandeurs[0][text]["noteHtml"] + '</a></sup>'
            if grandeurs[0][text]["Valeur totale"] > 0.0:
                phrase += " pour " + random.choice(["un montant de", "une somme de", "",
                                                    "une valeur totale de",
                                                    "une valeur de"]) + " " + \
                           utilitaires.modeleEuro(str(int(grandeurs[0][text]["Valeur totale"]*1e3)),
                                                  isWikicode)

                # Si la somme total des valeurs du groupe est valide, on affiche le pourcentage
                if grandeurs[1] > 0:
                    phrase += " (" +  grandeurs[0][text]['ratioValeurStr'] + ")"
                if grandeurs[0][text]["Par habitant"] > 0:
                    phrase += ", soit " + \
                              utilitaires.modeleEuro(str(int(grandeurs[0][text]["Par habitant"])),
                                                     isWikicode)
                    phrase += " par habitant, ratio "
                else:
                    phrase += ", négligeable compte tenu du nombre d’habitants de l'entité et "
                if avecStrate:
                    phrase += grandeurs[0][text]['ratioStrateStr']
            textSection = textSection.replace("<PHRASE_" + grandeurs[2] + str(numValeur) +">",
                                              phrase)

    # V1.0.0 : Generation des lignes des tableaux picto pour les taux des taxes
    # Les mots cles générés sont expansés par la suite
    listeDictTaxes = \
    [
        {
            "libelle" : "Taxe d'habitation",
            "tag" : "TAUX_TAXE_HABITATION",
            "cle" : "taux taxe habitation"
        },
        {
            "libelle" : "Taxe foncière sur le bâti",
            "tag" : "TAUX_FONCIER_BATI",
            "cle" : "taux taxe foncière bâti"
        },
        {
            "libelle" : "Taxe foncière sur le non bâti",
            "tag" : "FONCIER_NON_BATI",
            "cle" : "taux taxe foncière non bâti"
        }
    ]

    couleurTaxes = config.get('Tableaux', 'tableaux.couleurTaxes')
    lignes = ""
    for dictTaxe in listeDictTaxes:
        lignes += genlignesTableauPicto(dictTaxe["tag"], 1,
                                        couleurTaxes, '%',
                                        isWikicode, avecStrate, isGroupement,
                                        verbose)[0]
    textSection = textSection.replace("<GEN_LIGNES_TABLEAU_PICTO_TAXES>",
                                      "".join(lignes))

    # Remplacement des mot clés produits au dessus
    # Libelles des taxes
    for dictTaxe in listeDictTaxes:
        cle = dictTaxe["cle"]
        tag = dictTaxe["tag"]
        textSection = textSection.replace("<LIBELLE_PICTO_" + tag + "1>",
                                          dictTaxe["libelle"])
        tauxTaxeVille = dictAllGrandeur["Taux"][cle][listAnnees[0]]
        textSection = textSection.replace("<VALEUR_" + tag + "_PAR_HABITANT1>",
                                          f'{tauxTaxeVille:2.2f}')
        if len(listAnnees) > 1:
            tauxTaxeVilleNM1 = dictAllGrandeur["Taux"][cle][listAnnees[1]]
            # V1.0.4 :pas d'utilisation du modèle unité avec les pourcentages
            textSection = textSection.replace("<VALEUR_" + tag + "_PAR_HABITANT1_NM1>",
                                              f'{tauxTaxeVilleNM1:2.2f}'.replace('.', ','))
        else:
            textSection = textSection.replace("<VALEUR_" + tag + "_PAR_HABITANT1_NM1>",
                                              '?')
        if avecStrate and not isGroupement:
            tauxTaxeStrate = dictAllGrandeur["taux moyen pour la strate"]\
                                            [cle + " moyen"][listAnnees[0]]
            textSection = textSection.replace("<VALEUR_" + tag + "_STRATE1>",
                                              f'{tauxTaxeStrate:2.2f}')
            ratioTaxe = utilitaires.calculAugmentation(config,
                                                       float(tauxTaxeVille),
                                                       float(tauxTaxeStrate))
            picto, alt = utilitaires.choixPicto(config, ratioTaxe, isWikicode)
            textSection = textSection.replace("<PICTO_" + tag + "1>", picto)
            textSection = textSection.replace("<PICTO_ALT_" + tag + "1>", alt)

        # Tendance annee N-1
        if len(listAnnees) > 1:
            augmentation = utilitaires.calculeTendance(config,
                                                       float(tauxTaxeVille),
                                                       float(tauxTaxeVilleNM1))
            textSection = textSection.replace("<TENDANCE_" + tag + "_PAR_HABITANT1>",
                                              augmentation)

            # V4.0.1 : Insertion légende tableau picto
            legende = genLegendePicto(config, isWikicode, verbose)
            textSection = textSection.replace("<LEGENDE_ECART_TABLEAU_PICTO>",
                                              legende)
        else:
            textSection = textSection.replace("<TENDANCE_" + tag + "_PAR_HABITANT1>",
                                              '?')

    if verbose:
        print("Sortie de genCodeTableauxPicto")
    return textSection.strip()


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
