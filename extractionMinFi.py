# -*- coding: utf-8 -*-
"""
*********************************************************
Module : extractionMinFi.py
Auteur : Thierry Maillard (TMD)
Date : 24/5/2015 - 3/6/2015

Role : Récupère des informations sur les villes sur le
        site du minitère des finances.
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
import urllib.request, urllib.parse
import time
import sys

import utilitaires

def recupDataMinFi(config, listeVilleDict, cleFi, urlMinFi,
                   cleFiDetail, urlMinFiDetail,
                   nomsTableaux, verbose):
    """
    Récupère les données du ministère des Finances
    et les range dans listeVilleDict
    """
    if verbose:
        print("Entrée dans recupDataMinFi")

    msg = "recupDataMinFi : Aucune ville à traiter !"
    assert len(listeVilleDict) > 0, msg

    # Pour ressembler à un navigateur Mozilla/5.0
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]

    listAnnee = getAnneesMinFi(config, urlMinFi, listeVilleDict[0]['icom'],
                               listeVilleDict[0]['dep'], 0,
                               opener, verbose)
    msg = "Erreur : nombre d'année inférieur à 10 : " + str(len(listAnnee))
    assert len(listAnnee) > 10, msg

    # Traitement des villes
    for ville in listeVilleDict:
        if not utilitaires.isCommuneDejaExtraite(config, ville, verbose):
            msg = "\nTraitement de " + ville['nom'] + " (Score=" + str(ville['Score']) + ")"
            print(msg)

            # enregisterent des references pour cette ville
            ville['ref'] = setReferences(urlMinFi, ville['icom'], ville['dep'],
                                         listAnnee[0], nomsTableaux, cleFi, verbose)
            # v0.7 : Tableaux detail
            ville['refDetail'] = setReferencesDetail(urlMinFiDetail,
                                                     ville['icom'], ville['dep'],
                                                     listAnnee[0], "Fiche détaillée",
                                                     verbose)

            msg = 'Récupération des pages sur le site ' + \
                  urllib.parse.urlparse(urlMinFi).netloc
            print(msg)
            dictPagesWeb = dict()
            for annee in listAnnee:
                dictPages = dict()

                # Pages de synthèse
                for numTab in {cle[0] for cle in cleFi}:
                    # V1.0.5 : Délai entre deux requêtes au MinFi
                    utilitaires.wait2requete(config, verbose)
                    print('.', end='')
                    sys.stdout.flush()
                    url = construitUrlMinFi(urlMinFi, ville['icom'], ville['dep'],
                                            numTab, str(annee), verbose)
                    infile = opener.open(url)
                    dictPages[numTab] = infile.read()

                # v0.7 : pages de detail
                # V1.0.5 : Délai entre deux requêtes au MinFi
                utilitaires.wait2requete(config, verbose)
                print('.', end='')
                sys.stdout.flush()
                url = construitUrlMinFi(urlMinFiDetail, ville['icom'], ville['dep'],
                                        "0", str(annee), verbose)
                infile = opener.open(url)
                dictPages["Detail"] = infile.read()

                # Raccrochement au dico des annees
                dictPagesWeb[str(annee)] = dictPages
            print(" OK")

            # Récupère les clés dans les pages WEB
            dictCle = dict()

            # Pages de synthèse
            for cle in cleFi:
                dictAnnee = dict()
                for annee in listAnnee:
                    dictAnnee[str(annee)] =\
                        extractDonneesLigneTableau(dictPagesWeb[str(annee)][cle[0]],
                                                   cle[1], verbose)
                dictCle[cle[1]] = dictAnnee

            # v0.7 : pages de detail
            for cle in cleFiDetail:
                dictAnnee = dict()
                for annee in listAnnee:
                    dictAnnee[str(annee)] =\
                        extractDonneesLigneTableauDetail(dictPagesWeb[str(annee)]["Detail"],
                                                         cle["titres"], cle["libelles"],
                                                         verbose)
                dictCle[cle["alias"]] = dictAnnee

            # Raccrochement au dico des valeurs des clés
            ville['data'] = dictCle

            # Recup libelle complet strate
            cle = cleFi[0]
            defStrate =\
                extractDonneesCell(dictPagesWeb[str(listAnnee[0])][cle[0]],
                                   "Strate : ", verbose)
            ville['defStrate'] = defStrate.replace("Strate : ", "").replace("hab ", "habitants ")

            # Pour toutes les clés, les années max et max-1 doivent exister
            for cle in list(ville['data'].keys()):
                for annee in [listAnnee[0], listAnnee[0]-1]:
                    if ville['data'][cle][str(annee)] is None:
                        msg = "Erreur : la cle " +\
                            cle + " n'est pas definie dans la BD Alize2 pour l'année" +\
                            str(annee) +\
                            " : corrigez la liste cleFi dans le programme" +\
                            " pour ne plus demander cette cle"
                        raise ValueError(msg)

            # Ecrit dans un fichier local les donnees pour la ville
            utilitaires.ecritVilleDict(config, ville, verbose)
        else:
            msg = "\n" + ville['nom'] + " ignorée car déjà extraite."
            print(msg)

    if verbose:
        print("Sortie de recupDataMinFi")

def extractDonneesLigneTableau(page, key, verbose):
    """
    Récupère les valeurs des 3 éléments de tableau
    immédiatement à droite de cell contenant la clé key
    """
    if verbose:
        print("Entrée dans extractDonneesLigneTableau")
        print('key=', key)

    import lxml.html as lxmlHtml
    doc = lxmlHtml.document_fromstring(page)
    values = []
    for elt in doc.iter('td'):
        text = elt.text_content().lstrip()
        if text.startswith(key):
            values = [text.strip('\xa0')
                      for node in elt.itersiblings('td')
                      for subnode in node.iter()
                      for text in textTail(subnode)
                      if text and text != '\xa0' and text.lstrip().rstrip() != '']
            break

    if len(values) == 3:
        dictValue = dict()
        dictValue["Valeur totale"] = getInt(values[0]) * 1000
        dictValue["Par habitant"] = getInt(values[1])
        dictValue["En moyenne pour la strate"] = getInt(values[2])
    else:
        # Je ne sais pas quelle valeur manque,
        # je considère donc les données comme non valides.
        dictValue = None

    if verbose:
        print("Sortie de extractDonneesLigneTableau")
        print("Valeurs lues :", dictValue)

    return dictValue

def getInt(valeurStr):
    """ Extrait un entier d'une chaine contenant des caractères bizarres en fin """
    chiffres = [char for char in valeurStr if char.isdigit() or char == '-']
    valeurInt = int("".join(chiffres))
    return valeurInt

def textTail(node):
    """ Renvoie des nodes de type text """
    yield node.text

def extractDonneesCell(page, key, verbose):
    """ Récupère les données d'une cellule de tableau HTML """
    if verbose:
        print("Entrée dans extractDonneesCell")
        print('key=', key)

    import lxml.html as lxmlHtml
    stringValue = ""
    doc = lxmlHtml.document_fromstring(page)
    for elt in doc.iter('td'):
        text = elt.text_content().lstrip().rstrip()
        if text.startswith(key):
            stringValue = text
            break

    if verbose:
        print("Sortie de extractDonneesCell")
        print("Valeurs lues :", stringValue)

    return stringValue

def construitUrlMinFi(urlMinFi, icom, dep, numTab, annee, verbose):
    """
    Construit une URL pour accès au site du Ministère des Finances
    les chiffres manquants en tête de icom et dep sont remplacé par des 0
    Paramètres :
    urlMinFi : base de l'url
    icom : numero Insee de la commune (3 chiffres)
    dep : numero de département (3 chiffres)
    numTab : numero du tableau demandé
    annee : numéro de l'annee sur 4 chiffres
    """
    if verbose:
        print("Entrée dans construitUrlMinFi")
        print("urlMinFi :", urlMinFi)
        print("icom :", icom)
        print("dep :", dep)
        print("numTab :", numTab)
        print("annee :", annee)

    # Définit les paramètres fixes de l'url
    urlParam = dict()
    urlParam['icom'] = icom
    urlParam['dep'] = dep
    urlParam['type'] = 'BPS'
    urlParam['exercice'] = annee
    urlParam['param'] = numTab
    urlParamsEncode = urllib.parse.urlencode(urlParam)
    url = urlMinFi + '?' + urlParamsEncode

    if verbose:
        print("url :", url)
        print("Sortie de construitUrlMinFi")
    return url

def getAnneesMinFi(config, urlMinFi, icom, dep, numTab, opener, verbose):
    """
    Determine les annees des donnees du site
    du Ministère des Finances
    Paramètres :
    urlMinFi : base de l'url
    icom : numero Insee de la commune (3 chiffres)
    dep : numero de département (3 chiffres)
    numTab : numero du tableau demandé
    opener : URL opener
    """
    if verbose:
        print("Entrée dans getAnneesMinFi")
        print("urlMinFi :", urlMinFi)
        print("icom :", icom)
        print("dep :", dep)
        print("numTab :", numTab)

    import lxml.html as lxmlHtml
    print('Années disponibles :')

    nonDispoStr = "Données non disponibles"
    listAnnees = []
    rechercheAnneeMax = True
    anneeMiniMinFi = config.getint('Extraction', 'extraction.anneeMiniMinFi')
    for annee in range(int(time.strftime("%Y"))-1, anneeMiniMinFi-1, -1):
        nonDisponible = False

        # V1.0.5 : Délai entre deux requêtes au MinFi
        utilitaires.wait2requete(config, verbose)
        url = construitUrlMinFi(urlMinFi, icom, dep, numTab, annee, verbose)
        infile = opener.open(url)
        page = infile.read()
        doc = lxmlHtml.document_fromstring(page)
        for elt in doc.iter('h3'):
            text = elt.text_content().lstrip().rstrip()
            if text.startswith(nonDispoStr):
                nonDisponible = True
        if nonDisponible:
            if not rechercheAnneeMax:
                break
        else:
            listAnnees.extend([annee])
            print(str(annee) + ', ', end='', flush=True)

    if len(listAnnees) == 0:
        print("Aucune")
    else:
        print(" OK")

    if verbose:
        print("listAnnees :", listAnnees)
        print("Sortie de getAnneesMinFi")
    return listAnnees

def setReferences(urlMinFi, icom, dep, annee,
                  nomsTableaux, cleFi, verbose):
    """
    Contruit la liste des références à partir des clés extraites
    dans la base du ministère des Finances
    """
    if verbose:
        print("Entrée dans setReferences")

    references = dict()
    for numTableau in {cle[0] for cle in cleFi}:
        reference = dict()
        reference['nomPage'] = nomsTableaux[int(numTableau)]
        reference['refName'] = "Alize2_" + str(annee) + "_" + numTableau
        reference['url'] = construitUrlMinFi(urlMinFi, icom, dep,
                                             numTableau, annee, verbose)
        references[numTableau] = reference

    if verbose:
        print("references :", references)
        print("Sortie de setReferences")
    return references

# v0.7 : tableaux details
def setReferencesDetail(urlMinFi, icom, dep, annee,
                        nomTableau, verbose):
    """
    Contruit la référence à une page de détail
    dans la base du ministère des Finances
    """
    if verbose:
        print("Entrée dans setReferencesDetail")

    referenceDetail = dict()
    referenceDetail['nomPage'] = nomTableau
    referenceDetail['refName'] = "Alize2_" + str(annee) + "_Detail"
    referenceDetail['url'] = construitUrlMinFi(urlMinFi, icom, dep,
                                               "0", annee, verbose)

    if verbose:
        print("referenceDetail :", referenceDetail)
        print("Sortie de setReferencesDetail")
    return referenceDetail

# v0.7 : tableaux details
def extractDonneesLigneTableauDetail(page, titres, libelles, verbose):
    """ Exrait les données d'une page de détail Alize2 """
    if verbose:
        print("Entrée dans extractDonneesLigneTableauDetail")
        print('titres=', titres)
        print('libelles=', libelles)

    import lxml.html as lxmlHtml
    # Récupère les valeurs des 3 éléments de tableau
    # immédiatement à droite de cell contenant la lé key
    doc = lxmlHtml.document_fromstring(page)
    values = []
    numTitreTrouve = -1
    for elt in doc.iter('td'):
        text = elt.text_content().lstrip()
        if text.startswith(titres[0]):
            numTitreTrouve = 0
        if text.startswith(titres[1]):
            numTitreTrouve = 1
        if numTitreTrouve != -1 and text.startswith(libelles[numTitreTrouve]):
            values = [text.strip('\xa0')
                      for node in elt.itersiblings('td')
                      for subnode in node.iter()
                      for text in textTail(subnode)
                      if text and text != '\xa0' and text.lstrip().rstrip() != '']
            break

    #Analyse des valeurs reçues
    if len(values) == 2:
        dictValue = dict()
        dictValue["Taux"] = getFloat(values[0])
        dictValue["Taux moyen pour la strate"] = getFloat(values[1])
    else:
        # Je ne sais pas quelle valeur manque,
        # je considère donc les données comme non valides.
        dictValue = None

    if verbose:
        print("Sortie de extractDonneesLigneTableauDetail")
        print("Valeurs lues :", dictValue)

    return dictValue

def getFloat(valeurStr):
    """ Récupère un nombre à virgule depuis une châine de caractères"""
    chiffres = [char for char in valeurStr if char.isdigit() or char == ',']
    valeurFloat = float("".join(chiffres).replace(',', '.'))
    return valeurFloat
