# -*- coding: utf-8 -*-
"""
*********************************************************
Module : extractionWikipediaFr.py
Auteur : Thierry Maillard (TMD)
Date : 24/5/2015 -  7/11/2015

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
    Paramètres :
    - nomArticle : nom de l'article qui contient la liste des villes
    Le format des listes de communes varient beaucoup et sont difficiles à analyser
    Certain utilisent des modèles.
    Pour cette raisons, la lecture de liste de commune générées par l'outil genListeDep.py
    est préferable
    """
    if verbose:
        print("Entrée dans recupVilles")
        print("\tnomArticle =", nomArticle)

    listeVilleDict = []
    nomArticleUrl = urllib.request.pathname2url(nomArticle)
    page = getPageWikipediaFr(config, nomArticleUrl, verbose)

    listeRegexp = dict()
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
    # \s : caractère espace
    # $ : fin de ligne obligatoire

    # Extract Code Insee, lien ville sur une même ligne : schéma 1
    # Ligne du type :   | Code Insee || Code Postal || [[Lien commune]]
    #                   | 46324 || 46310 || [[Uzech]]
    listeRegexp['1'] = \
        re.compile(r'^[ ]*\|[ ]*(?P<Insee>\d[0-9AB]\d{3})[ ]*\|[ ]*\|[ ]*\d{5}[,0-9 ]*?' +\
                   r"[\|]{2}[ ']*[\[]{2}(?P<Lien>.*?)[\]\|]")

    # Extract Code Insee et lien ville sur deux lignes successives : schéma 2
    # Ligne du type :   | Code Insee || Code Postal
    #                   | [[Lien commune]]
    #                   | 97401 || 97425
    #                   | [[Les Avirons]]
    listeRegexp['2a'] = \
        re.compile(r'^[ ]*\|[ ]*(?P<Insee>\d[0-9AB]\d{3})[ ]*\|[ ]*\|[ ]*\d{5}[ ]*$')
    listeRegexp['2b'] = re.compile(r'^[ ]*\|[ ]*[\[]{2}(?P<Lien>.*?)[\]\|]')

    #  V2.3.0 : 31/10/2015 :
    # Lecture ligne du type Val-de-Marne : ! scope=row | [[Alfortville]]
    listeRegexp['b0'] = \
    re.compile(r'^[ ]*![ ]*scope=row[ ]*\|[ ]*[\[]{2}(?P<Lien>.*?)[\]\|]')

    # V2.2.0, V2.3.0 : 26/10/2015 - 28/10/2015 :
    # Lecture ligne du type Gironde : | | [[Lien commune]] || Code Insee || Code Postal
    listeRegexp['b1'] = \
        re.compile(r'^[ ]*\|[ ]*\|[ ]*[\[]{2}(?P<Lien>.*?)[\]\|]' + \
                   r'[^\d]*\d{5}[,0-9<br />]*?\|[ ]*\|.*?\|')
    # Lecture ligne du type Essonne : | style="text-align: left" | [[Abbéville-la-Rivière]] || 91
    listeRegexp['b2'] = \
        re.compile(r'^[ ]*\|[ ]*style=.*?\|[ ]*[\[]{2}(?P<Lien>.*?)[\]\|]')

    #  V2.3.0 : 29/10/2015 :
    # Lecture ligne du type Vendée : | {{tri|Aiguillon-sur-Vie|[[L'Aiguillon-sur-Vie|L’Aiguillon-sur-Vie]]}}
    listeRegexp['b3'] = \
        re.compile(r'^[ ]*\|[ ]*{{tri\|.*?\|[ ]*[\[]{2}(?P<Lien>.*?)[\]\|]')

    #  V2.3.0 : 29/10/2015 :
    # Lecture ligne du type Var : | [[Les Adrets-de-l'Estérel]] || 83001 || 83600 ||
    listeRegexp['b4'] = \
        re.compile(r'^\|[ ]*[\[]{2}(?P<Lien>.*?)[\]\|].*?' +
                   r'[\|]{2}[ ]*\d{5}[ ]*[\|]{2}[ ]*\d{5}[ ]*[\|]{2}')

    # V2.2.0 : 26/10/2015 :
    # Lecture ligne du type Aveyron : modèle {{Tableau Liste commune de France}}
    listeRegexp['4'] = re.compile(r'^[ ]*\|[ ]*commune [0-9]+[ ]*=[ ]*(?P<Lien>.*?)[\s]*$')

    #  V2.3.0 : 29/10/2015 :
    # Lecture ligne du type Côte d'Or : | {{tri1|agencourt}} [[Agencourt]] || 21001 || 21700 ||
    listeRegexp['5'] = \
        re.compile(r'^[ ]*\|[ ]*{{tri1\|.*?}}[ ]*[\[]{2}(?P<Lien>.*?)[\]\|].*?' +
                   r'[\|]{2}[ ]*(?P<Insee>\d{5})[ ]*[\|]{2}[ ]*\d{5}[ ]*[\|]{2}')

    # Lecture ligne du type Aisne : | align="left" | [[Abbécourt]] || 02001 || 02300 ||
    listeRegexp['6'] = \
        re.compile(r'^[ ]*\|[ ]*align="left"[ ]*\|[ ]*[\[]{2}(?P<Lien>.*?)[\]\|].*?' +
                   r'[\|]{2}[ ]*(?P<Insee>\d{5})[ ]*[\|]{2}[ ]*\d{5}[ ]*[\|]{2}')

    #  V2.3.0 : 1/11/2015 :
    # Lecture ligne du type Guadeloupe :
    # |97102||<small>219711025</small>||align="left"|[[Anse-Bertrand]]||97121
    listeRegexp['7'] = \
        re.compile(r'^[ ]*\|[ ]*(?P<Insee>971\d{2})[ ]*[\|]{2}[ ]*' +
                   r'<small>\d{9}</small>[ ]*\|{2}.*?\|' +
                   r"[ ']*[\[]{2}(?P<Lien>.*?)[\]\|]")
    attente1ereLigne = True
    numLigne = 0
    ville = None
    fmtPrev = None
    for line in page.splitlines():
        # V2.3.0 : Si changement de section après avoir trouvé des communes : arrêt
        if fmtPrev is not None and "==" in line:
            break

        numLigne += 1

        # Vérif quelle expression s'applique à la ligne
        match = None
        if attente1ereLigne:
            for fmt in ['1', '2a', 'b0', 'b1', 'b2', 'b3', 'b4', '4', '5', '6', '7']:
                match = listeRegexp[fmt].search(line)
                if match:
                    ville = dict()
                    # V2.3.0 : le format de la liste des communes doit être homogène.
                    if fmtPrev is None:
                        fmtPrev = fmt
                    elif fmt != fmtPrev:
                        break
                    if fmt in ['1', '5', '6', '7']:
                        ville['nomWkpFr'] = match.group('Lien')
                        setArticleLiens(ville, verbose)
                        setInseeDep(ville, match.group('Insee'), verbose)
                        listeVilleDict.append(dict(ville)) # dict() to avoid the copy of the reference only
                    elif fmt == '4' or fmt.startswith('b'):
                        ville['nomWkpFr'] = match.group('Lien')
                        if 'Aire urbaine' not in ville['nomWkpFr'] and \
                           'ommunauté' not in ville['nomWkpFr'] and \
                           'circonscription' not in ville['nomWkpFr'] and \
                           'Arrondissement' not in ville['nomWkpFr'] and \
                           'gglo' not in ville['nomWkpFr'] and \
                           'Atlantique' not in ville['nomWkpFr'] and \
                           'Canton' not in ville['nomWkpFr'] and \
                           'urbaine' not in ville['nomWkpFr']:
                            setArticleLiens(ville, verbose)
                            # Recup Code Insee dans page wikipedia de la commune
                            liste1ville = recup1Ville(config, ville['nomWkpFr'], verbose)
                            ville['icom'] = liste1ville[0]['icom']
                            ville['dep'] = liste1ville[0]['dep']
                            listeVilleDict.append(dict(ville)) # dict() to avoid the copy of the reference only
                    elif fmt == '2a': # cette ligne ne contient que le code Insee
                        attente1ereLigne = False
                        setInseeDep(ville, match.group('Insee'), verbose)
                    break
        else: # Ligne suivante au format 2b obligatoire (suite ligne 2a)
            match = listeRegexp['2b'].search(line)
            if match:
                attente1ereLigne = True # Pour retenter le schéma 1 sur la prochaine ligne
                ville['nomWkpFr'] = match.group('Lien')
                setArticleLiens(ville, verbose)
                listeVilleDict.append(dict(ville)) # dict() to avoid the copy of the reference only
            else: # C'est la loose totale : on attendait une deuxième ligne qui n'est pas arrivée.
                msg = "Problème d'analyse de la page " + nomArticle + " en ligne " + \
                    str(numLigne) + " :\n" + \
                    "Code insee=" + ville['icom'] + " , " + \
                    "departement=" + ville['dep'] +" trouvés sur ligne précédente\n" + \
                    "mais nom de commune non trouvé sur ligne suivante !"
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

    assert nomArticle.strip() != "", "Erreur paramètre : nomArticle vide !"

    listeVilleDict = []
    ville = dict()
    ville['nomWkpFr'] = nomArticle.strip()
    setArticleLiens(ville, verbose)
    page = getPageWikipediaFr(config, ville['lien'], verbose)

    # Ligne du type : | insee = 46254
    # V2.1.1 ou : | insee          = 2A041
    # \d : un chiffre
    select = r'^[ ]*\|[ ]*insee[ ]*=[ ]*(?P<Insee>\d[AB0-9]\d{3})'
    regexp = re.compile(select)
    # Extract Code Insee
    trouveCodeInsee = False
    for line in page.splitlines():
        m = regexp.search(line)
        if m: # si l'expression régulière s'applique à la ligne
            setInseeDep(ville, m.group('Insee'), verbose)
            trouveCodeInsee = True
            break

    assert trouveCodeInsee, '| insee = CODE introuvable dans article ' + nomArticle
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
            # V2.1.1 : Un nom de département ne doit pas contenir commun
            # Pb Achenheim (67) : [[Catégorie:Commune de la communauté de communes les Châteaux]]
            if len(nomDepStr) > 4 and "commun" not in nomDepStr and "canton"  not in nomDepStr:
                break
    msg = "recupNomDepStr() nom de département vide dans article : " +  nomArticleUrl + \
          ", verifiez si cette commune n'a pas été fusionnée."
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
        'Faible' : config.getint('Score', 'poids.Faible'),
        'moyenne' : config.getint('Score', 'poids.Moyenne'),
        'Moyenne' : config.getint('Score', 'poids.Moyenne'),
        'élevée' : config.getint('Score', 'poids.Elevee'),
        'maximum' : config.getint('Score', 'poids.Maximum'),
        'avancement' : config.getint('Score', 'coef.avancement'),
        'importanceCDF' : config.getint('Score', 'coef.importanceCDF'),
        'importanceVDM' : config.getint('Score', 'coef.importanceVDM'),
        'popularite' : config.getint('Score', 'coef.popularite')
        }

    for ville in listeVilleDict:
        sys.stdout.flush()

        # Construction du nom de la page de discussion pour cette ville
        nomArticlePDD = config.get('Extraction', 'extraction.discussion') + ville['lien']

        # Lecture de la page de discussion
        page = getPageWikipediaFr(config, nomArticlePDD, verbose)
        listeCriteres = recupScoreData1Ville(config, page, nomArticlePDD, verbose)
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
    print("OK")

    if verbose:
        print("Sortie de recupScoreDataVilles")

def recupScoreData1Ville(config, page, nomArticlePDD, verbose):
    """
    Récupération dans page de texte des données de score
    """
    if verbose:
        print("Entrée dans recupScoreData1Ville")
        print("nomArticlePDD", nomArticlePDD)

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
                          nomArticlePDD + ", valeur " + valeur + \
                          " non autorisé pour le label " + \
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
    print(nomArticleUrl) # Facilite debug

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
