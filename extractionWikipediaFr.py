# -*- coding: utf-8 -*-
"""
*********************************************************
Module : extractionWikipediaFr.py
Auteur : Thierry Maillard (TMD)
Date : 24/5/2015 - 3/6/2015

Role : Récupère des informations sur les villes dans Wikipédia fr.
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
import urllib.request, urllib.error, urllib.parse
import re
import sys

def recupVilles(config, nomArticle, verbose):
    """
    Récupère les code Insee et departement des villes d'un département
    dans une page de liste de Wikipedia fr
    Paramètre : nomArticle : nom de l'article qui contient la liste des villes
    """
    if verbose:
        print("Entrée dans recupVilles")
        print("\tnomArticle =", nomArticle)

    listeVilleDict = []
    nomArticleUrl = urllib.request.pathname2url(nomArticle)
    page = getPageWikipediaFr(config, nomArticleUrl, verbose)

    # V1.0.5 : 18/7/2015 : support de 2 formats pour le tableau de liste des villes
    # Remarque : le programme accepte un mix des deux formats.
    # Support num. dep. corse 2A et 2B

    # Syntaxe des expressions régulières utilisées :
    # [ ]* : 0 ou n espace
    # \d{n} : n chiffre
    # [\|]{2} : 2 | ; idem pour [\[]{2} : 2 [
    # [\]\|] : un ] ou un | sont attendus
    # .*? : N'importe quel caractère, n'importe quel car jusqu'à atteindre le ] ou le | :
    #       ? -> non-greedy or minimal fashion
    # ^ : Début de ligne
    # $ : fin de ligne obligatoire

    # Extract Code Insee, lien ville sur une même ligne : schéma 1
    # Ligne du type :   | Code Insee || Code Postal || [[Lien commune]]
    #                   | 46324 || 46310 || [[Uzech]]
    selectFmt1 = r'^[ ]*\|[ ]*(?P<Insee>\d[0-9AB]\d{3})[ ]*\|[ ]*\|[ ]*\d{5}[,0-9 ]*?' +\
                 r'[\|]{2}[ ]*[\[]{2}(?P<Lien>.*?)[\]\|]'
    regexpFmt1 = re.compile(selectFmt1)

    # Extract Code Insee et lien ville sur deux lignes successives : schéma 2
    # Ligne du type :   | Code Insee || Code Postal
    #                   | [[Lien commune]]
    #                   | 97401 || 97425
    #                   | [[Les Avirons]]
    selectFmt2a = r'^[ ]*\|[ ]*(?P<Insee>\d[0-9AB]\d{3})[ ]*\|[ ]*\|[ ]*\d{5}[ ]*$'
    regexpFmt2a = re.compile(selectFmt2a)
    selectFmt2b = r'^[ ]*\|[ ]*[\[]{2}(?P<Lien>.*?)[\]\|]'
    regexpFmt2b = re.compile(selectFmt2b)

    toutsur1ligne = True
    numLigne = 0
    for line in page.splitlines():
        numLigne += 1
        if toutsur1ligne:
            m = regexpFmt1.search(line)
            if m: # si les infos sont trouvées dans une même ligne : schéma 1
                ville = dict()
                ville['nomWkpFr'] = m.group('Lien')
                setArticleLiens(ville, verbose)
                setInseeDep(ville, m.group('Insee'), verbose)
                listeVilleDict.append(dict(ville)) # dict() to avoid the copy of the reference only
            else: # On tente le schéma 2 : le code Insee suivi du code postal (ignoré)
                m = regexpFmt2a.search(line)
                if m: # si le code Insee est suivi du code postal
                    toutsur1ligne = False
                    ville = dict()
                    setInseeDep(ville, m.group('Insee'), verbose)
            # Sinon la ligne est ignorée en silence
        else: # Schéma 2 : on recherche un lien de ville dans cette ligne
            m = regexpFmt2b.search(line)
            if m: # si le lien de ville est trouvé sur cette ligne
                toutsur1ligne = True # Pour retenté le schéma 1 ur la prochaine ligne
                ville['nomWkpFr'] = m.group('Lien')
                setArticleLiens(ville, verbose)
                listeVilleDict.append(dict(ville)) # dict() to avoid the copy of the reference only
            else: # C'est la loose totale : on attendait une deuxième ligne qui n'est pas arrivée.
                msg = "Problème d'analyse de la page " + nomArticle + " en ligne " + \
                    str(numLigne) + " :\n" + \
                    "Code insee trouvé sur ligne précédente (" + ville['icom'] + ") , " + \
                    "mais nom de commune non trouvé ici !"
                raise ValueError(msg)

    if verbose:
        print("listeVilleDict[:5] : ")
        for ville in listeVilleDict[:5]:
            print(ville)
        print("Sortie de recupVilles")

    return listeVilleDict

def recup1Ville(config, nomArticle, verbose):
    """
    Récupère une ville dans Wikipedia fr
    Paramètre : nomArticle : nom de l'article de la ville
    """
    if verbose:
        print("Entrée dans recup1Ville")
        print("\tnomArticle =", nomArticle)

    listeVilleDict = []
    ville = dict()
    ville['nomWkpFr'] = nomArticle.strip()
    setArticleLiens(ville, verbose)
    page = getPageWikipediaFr(config, ville['lien'], verbose)

    # Ligne du type : | insee = 46254
    # \d : un chiffre
    select = r'^[ ]*\|[ ]*insee[ ]*=[ ]*(?P<Insee>\d{5})'
    regexp = re.compile(select)
    # Extract Code Insee
    for line in page.splitlines():
        m = regexp.search(line)
        if m: # si l'expression régulière s'applique à la ligne
            setInseeDep(ville, m.group('Insee'), verbose)
            break

    # Ajout de la ville à la liste
    listeVilleDict.append(ville)

    if verbose:
        print("listeVilleDict : ", listeVilleDict)
        print("Sortie de recup1Ville")

    return listeVilleDict

def recupNomDepStr(config, nomArticleUrl, verbose):
    """
    Recuperation du nom du département en chaine de caractere dans
    l'article Wikipedia de la ville passée en paramètre
    """
    if verbose:
        print("Entrée dans recupNomDepStr")
        print("pour nomArticleUrl=", nomArticleUrl)

    nomDepStr = ""
    page = getPageWikipediaFr(config, nomArticleUrl, verbose)

    # Ligne du type : [Catégorie:Commune du Lot]
    # .*? : n'importe quel car jusqu'à atteindre le ] : ? -> non-greedy or minimal fashion
    select = r'^[ ]*[\[]{2}Catégorie:Commune (?P<NomDepStr>d[eu\'].*?)[\]\|]'
    regexp = re.compile(select)
    # Extract Code Insee
    for line in page.splitlines():
        m = regexp.search(line)
        if m: # si l'expression régulière s'applique à la ligne
            nomDepStr = m.group('NomDepStr')
            msg = 'Nom de departement invalide : ' + nomDepStr +\
                  " dans l'article  " +  nomArticleUrl
            assert len(nomDepStr) > 4, msg
            break
    msg = "recupNomDepStr() nom de département vide dans article : " +  nomArticleUrl
    assert len(nomDepStr) > 0, msg

    if verbose:
        print("nomDepStr : ", nomDepStr)
        print("Sortie de recupNomDepStr")
    return nomDepStr

def recupScoreDataVilles(config, listeVilleDict, verbose):
    """
    Récupération dans les PDD de chaque ville des données pour calculer leur score
    """

    if verbose:
        print("Entrée dans recupScoreDataVilles")

    # Récupération pondération de chaque label et
    # conversion en minuscule pour éviter pb casse
    dicoPoids = {
        '?' : config.getint('Score', 'poids.Indetermine'),
        'ébauche' : config.getint('Score', 'poids.Ebauche'),
        'BD' : config.getint('Score', 'poids.BD'),
        'B' : config.getint('Score', 'poids.B'),
        'A' : config.getint('Score', 'poids.A'),
        'BA' : config.getint('Score', 'poids.BA'),
        'AdQ' : config.getint('Score', 'poids.AdQ'),
        'faible' : config.getint('Score', 'poids.Faible'),
        'moyenne' : config.getint('Score', 'poids.Moyenne'),
        'élevée' : config.getint('Score', 'poids.Elevee'),
        'maximum' : config.getint('Score', 'poids.Maximum'),
        'avancement' : config.getint('Score', 'coef.avancement'),
        'importanceCDF' : config.getint('Score', 'coef.importanceCDF'),
        'importanceVDM' : config.getint('Score', 'coef.importanceVDM'),
        'popularite' : config.getint('Score', 'coef.popularite')
        }

    for ville in listeVilleDict:
        print('.', end='')
        sys.stdout.flush()

        # Construction du nom de la page de discussion pour cette ville
        nomArticlePDD = config.get('Extraction', 'extraction.discussion') + ville['lien']

        # Lecture de la page de discussion
        page = getPageWikipediaFr(config, nomArticlePDD, verbose)
        listeCriteres = recupScoreData1Ville(config, page, verbose)
        for critere in listeCriteres:
            ville[critere['cle']] = critere['valeur']

        # Calcule le score pour cette ville
        try:
            ville['Score'] = dicoPoids['avancement'] * dicoPoids[ville['avancement']] + \
                         dicoPoids['importanceCDF'] * dicoPoids[ville['importanceCDF']] + \
                         dicoPoids['importanceVDM'] * dicoPoids[ville['importanceVDM']] + \
                         dicoPoids['popularite'] * dicoPoids[ville['popularite']]
        except ValueError:
            print(("Problème dans PDD de " + ville['nom']))
            raise
    print(" OK")

    if verbose:
        print("Sortie de recupScoreDataVilles")

def recupScoreData1Ville(config, page, verbose):
    """
    Récupération dans page de texte des données de score
    """
    if verbose:
        print("Entrée dans recupScoreData1Ville")

    # V1.0.5 : Précision labels acceptés et paramétrage
    avancementsOk = config.get('Score', 'label.avancementsOk').split('|')
    importancesOk = config.get('Score', 'label.importancesOk').split('|')

    # Définition des éléments déterminant le score
    # Ligne du type : | Communes de France | faible ou  | avancement = AdQ
    listeCriteres = list()
    critereimportanceCDF = {
        'cle' : 'importanceCDF',
        'nomLabel' : config.get('Score', 'nom.importanceCDF'),
        'select' : r'^[ ]*\|[ ]*' + config.get('Score', 'nom.importanceCDF') +\
                   r'[ ]*\|[ ]*(?P<importanceCDF>[A-Za-zé?]+)',
        'accept' : importancesOk
        }
    listeCriteres.append(critereimportanceCDF)
    critereavancement = {
        'cle' : 'avancement',
        'nomLabel' : config.get('Score', 'nom.avancement'),
        'select' : r'^[ ]*\|[ ]*' + config.get('Score', 'nom.avancement') +\
                   r'[ ]*=[ ]*(?P<avancement>[A-Za-zé?]+)',
        'accept' : avancementsOk
    }
    listeCriteres.append(critereavancement)
    critereimportanceVDM = {
        'cle' : 'importanceVDM',
        'nomLabel' : config.get('Score', 'nom.importanceVDM'),
        'select' : r'^[ ]*\|[ ]*' + config.get('Score', 'nom.importanceVDM') +\
                   r'[ ]*\|[ ]*(?P<importanceVDM>[A-Za-zé?]+)',
        'accept' : importancesOk
    }
    listeCriteres.append(critereimportanceVDM)
    criterepopularite = {
        'cle' : 'popularite',
        'nomLabel' : config.get('Score', 'nom.popularite'),
        'select' : r'^[ ]*\|[ ]*' + config.get('Score', 'nom.popularite') +\
                   r'[ ]*\|[ ]*(?P<popularite>[A-Za-zé?]+)',
        'accept' : importancesOk
    }
    listeCriteres.append(criterepopularite)

    # Init et compilation des expressions régulières
    for critere in listeCriteres:
        critere['valeur'] = "?"
        critere['regexp'] = re.compile(critere['select'])

    # Recherche et extraction des éléments déterminant le score
    # et conversion en minuscule pour éviter les pb de casse
    for line in page.splitlines():
        for critere in listeCriteres:
            m = critere['regexp'].search(line)
            if m: # si l'expression régulière s'applique à la ligne
                valeur = m.group(critere['cle'])
                # V1.0.5 : Précision labels acceptés et paramétrage
                trouve = False
                for labelOk in critere['accept']:
                    if labelOk == valeur:
                        trouve = True
                        critere['valeur'] = valeur
                if not trouve:
                    msg = "Problème d'analyse du modèle Wikiprojet dans cette PDD : " + \
                            "valeur " + valeur + " non autorisé pour le label " + \
                            critere['nomLabel'] + "!"
                    raise ValueError(msg)

    if verbose:
        print("Sortie de recupScoreData1Ville")
    return listeCriteres

def getPageWikipediaFr(config, nomArticleUrl, verbose):
    """
    Ouvre une page de Wikipedia et retourne le texte brut de la page
    """
    if verbose:
        print("Entrée dans getPageWikipediaFr")
        print("Recuperation de l'article :", nomArticleUrl)

    # Pour ressembler à un navigateur Mozilla/5.0
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]

    # Construction URL à partir de la config et du nom d'article
    baseWkpFrUrl = config.get('Extraction', 'extraction.wikipediafrBaseUrl')
    actionTodo = config.get('Extraction', 'extraction.wikipediafrActionRow')
    urltoGet = baseWkpFrUrl + nomArticleUrl + actionTodo
    if verbose:
        print("urltoGet =", urltoGet)

    # Envoi requete, lecture de la page et decodage vers Unicode
    infile = opener.open(urltoGet)
    page = infile.read().decode('utf8')

    if verbose:
        print("Sortie de getPageWikipediaFr")
        print("Nombre de caracteres lus :", len(page))
    return page

def setArticleLiens(ville, verbose):
    """
    A partir de son champ 'nomWkpFr' : nom d'article affiché dans Wikipédia
    Complete une ville avec son nom court et son lien pour bâtir des URL
    """
    if verbose:
        print("Entrée dans setArticleLiens")
        print(("Construction des liens pour : " + ville['nomWkpFr']))

    nomWkpFr = ville['nomWkpFr']
    ville['nom'] = nomWkpFr
    posDept = nomWkpFr.rfind(' (')
    if posDept != -1:
        ville['nom'] = nomWkpFr[:posDept]
    ville['lien'] = urllib.request.pathname2url(nomWkpFr)

    if verbose:
        print(("nom court : " + ville['nom']))
        print(("lien pour URL : " + ville['lien']))
        print("Sortie de setArticleLiens")

def setInseeDep(ville, codeInsee, verbose):
    """
    Analyse le parametre codeInsee pour en sortir un numéro de département préfixé par 0
    et le numéro Insee de la commune dans le département.
    Met à jour la structure ville passée en paramètre.
    """
    if verbose:
        print("Entrée dans setInseeDep")
        print(("Analyse du code Insee : " + codeInsee))

    msg = 'Code Insee de invalide : < 5 chiffres : ' + codeInsee
    assert len(codeInsee) == 5, msg
    ville['icom'] = codeInsee[-3:]
    ville['dep'] = '0' + codeInsee[:2]

    if verbose:
        print(("Code insee ville icom : " + ville['icom']))
        print(("Code département : " + ville['dep']))
        print("Sortie de setArticleLiens")
