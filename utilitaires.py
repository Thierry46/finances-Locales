#! /usr/bin/env python
# coding: utf8
"""
*********************************************************
Programme : utilitaires.py
Auteur : Thierry Maillard (TMD)
Date : 24/5/2015 - 2/7/2020
Role : Fonctions communes
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
import os
import os.path
import math
import random
import time
import platform
import sys
import unicodedata
import urllib.request
import re


__TPREC__ = 0.0

def merge2Dict(dict1, dict2, verbose):
    """
        Fusionne deux dictionnaires (année : valeur) sur leurs années commune
        les liste d'entrée doivent être triées de façon indentique.
        Retourne un dictionnaire {année : [valeurListe1, valeurListe2]}
    """
    if verbose:
        print("Entree dans merge2Dict")
        print("dict1 =", dict1)
        print("dict2 =", dict2)

    # Fusionne les 2 dictionnaires sur leurs années communes
    anneesCafEtDette = set(dict1.keys()) & set(dict2.keys())
    if verbose:
        print("anneesCafEtDette =", anneesCafEtDette)

    dictDetteCaf = {cle : [dict1[cle], dict2[cle]] for cle in anneesCafEtDette}

    if verbose:
        print("dictDetteCaf=", dictDetteCaf)
        print("Sortie de merge2Dict")

    return dictDetteCaf

def lectureFiltreModele(modele, isComplet, verbose):
    """ Lecture du fichier modèle
        et adaptation du modèle en fonction du type de sortie souhaitée """

    if verbose:
        print("Entree dans lectureFiltreModele")
        print("modele =", modele)
        print("isComplet =", isComplet)

    with open(modele, 'r', encoding='utf-8') as modelefile:
        htmlPage = ""
        ecrit = True
        for ligne in modelefile.read().splitlines():
            if ligne.startswith("<STOP_COMPLET>"):
                ecrit = True
            elif ligne.startswith("<COMPLET>"):
                ecrit = False
            elif isComplet or ecrit:
                htmlPage += ligne + '\n'

    if verbose:
        print("Sortie de lectureFiltreModele")

    return htmlPage

def construitNomFic(repertoire, nomArticle, indicateur, extFic):
    """ Construit le nom d'un fichier de sortie """
    nomVille = nomArticle
    for char in "()":
        nomVille = nomVille.replace(char, '_')
    ficVilleIndicateur = nomVille
    if len(indicateur) > 0:
        ficVilleIndicateur += '_' + indicateur
    ficVilleIndicateur += extFic
    if repertoire is not None:
        ficVilleIndicateur = os.path.join(repertoire, ficVilleIndicateur)
    pathficNomVille = os.path.normcase(ficVilleIndicateur)
    return pathficNomVille

def calculAugmentation(config, valeurArrivee, valeurDepart):
    """Renvoie l'augmentation ou diminution en pourcentage entre 2 valeurs"""
    # Pour éviter les divisions par 0
    procheZero = float(config.get('Math', 'math.procheZero'))
    if abs(valeurDepart) < procheZero:
        valeurDepart = math.copysign(procheZero, valeurDepart)
    if abs(valeurArrivee) < procheZero:
        valeurArrivee = math.copysign(procheZero, valeurArrivee)
    return ((valeurArrivee - valeurDepart) / valeurDepart) * 100.

# V1.0.0 : Suppression couleurs = jugement de valeur
# V1.0.2 : Accessibilité : texte alternatif
def choixPicto(config, ratio, isWikicode):
    """Choix d'un pictogramme en fonction d'un ratio"""
    if isWikicode:
        prefix = 'picto'
    else:
        prefix = 'pictoHtml'
    if abs(ratio) < float(config.get('GenCode', 'gen.seuilValeurPourCentDifferente')):
        picto = config.get('Picto', prefix + '.ecartNul')
        alt = config.get('Picto', 'picto.ecartNulAlt')
    elif abs(ratio) < config.getfloat('GenCode', 'gen.seuilValeurPourCentgrande'):
        picto = config.get('Picto', prefix + '.ecartMoyen')
        alt = config.get('Picto', 'picto.ecartMoyenAlt')
    else:
        picto = config.get('Picto', prefix + '.ecartFort')
        alt = config.get('Picto', 'picto.ecartFortAlt')
    return picto, alt

def calculeTendance(config, valeurN, valeurNM1):
    """
    Qualifie une variation sur une grandeur :
    Retourne une chaine de caractères
    """
    tendance = calculAugmentation(config, valeurN, valeurNM1)
    tendancestr = ""
    ecartAbs = abs(tendance)
    if ecartAbs >= float(config.get('GenCode', 'gen.seuilValeurPourCentgrande')):
        tendancestr = "très "
    if ecartAbs < float(config.get('GenCode', 'gen.seuilValeurPourCentDifferente')):
        egal = "égale"
        if ecartAbs < float(config.get('Math', 'math.procheZero')):
            tendancestr = egal
        else:
            tendancestr = "quasiment " + egal
    elif tendance > 0.0:
        tendancestr += "supérieure (%1.0f %%)"%tendance
    else:
        tendancestr += "inférieure (%1.0f %%)"%tendance

    return tendancestr

def calculeTendanceSerie(nomValeur, dictAneeesValeur, verbose):
    """ Retourne des indicateurs qui qualifient la variation d'une grandeur """

    if verbose:
        print("\nEntrée dans tendanceValeur")
        print("nomValeur =", nomValeur)
        print("dictAneeesValeur =", dictAneeesValeur)

    assert len(dictAneeesValeur) > 0, "calculeTendanceSerie() : la serie a traiter est vide !"
    # Reverse car l'année de ref est la plus récete par laquel tout traitement doit commencer
    listeAnneesStr = sorted(list(dictAneeesValeur.keys()), reverse=True)
    if verbose:
        print("listeAnneesStr=", listeAnneesStr)

    # Determine l'annee du max et du min
    minAnnee = maxAnnee = listeAnneesStr[0]
    for annee in listeAnneesStr:
        if dictAneeesValeur[annee] > dictAneeesValeur[maxAnnee]:
            maxAnnee = annee
        if dictAneeesValeur[annee] < dictAneeesValeur[minAnnee]:
            minAnnee = annee

    if verbose:
        print("minAnnee=", minAnnee,
              ", dictAneeesValeur[minAnnee] =", dictAneeesValeur[minAnnee])
        print("maxAnnee=", maxAnnee,
              ", dictAneeesValeur[maxAnnee] =", dictAneeesValeur[maxAnnee])

    # Determine si la série est croissante, décroissante ou constante
    # V1.0.5 : Correction bug si manque une année
    croissante = decroissante = constante = False
    if int(maxAnnee) == int(minAnnee):
        constante = True
    elif int(maxAnnee) > int(minAnnee):
        croissante = True
        for indice in range(len(listeAnneesStr)-1):
            if dictAneeesValeur[listeAnneesStr[indice]] < \
               dictAneeesValeur[listeAnneesStr[indice+1]]:
                croissante = False
                break
    else:
        decroissante = True
        for indice in range(len(listeAnneesStr)-1):
            if dictAneeesValeur[listeAnneesStr[indice]] > \
               dictAneeesValeur[listeAnneesStr[indice+1]]:
                decroissante = False
                break

    if verbose:
        print("croissante=", croissante, ", decroissante =", decroissante,
              ", constante =", constante)
        print("\nSortie de tendanceValeur")
    return minAnnee, maxAnnee, croissante, decroissante, constante

def calculeTendanceSerieStr(nomValeur, dictAneeesValeur, unite,
                            isWikicode, verbose):
    """
    Calcule une tendance refletant la variation d'une grandeur
    et l'exprime dans une phrase
    """

    # Calcule des tendances
    minAnnee, maxAnnee, croissante, decroissante, constante = \
        calculeTendanceSerie(nomValeur, dictAneeesValeur, verbose)

    if verbose:
        print("\nEntrée dans calculeTendanceSerieStr")

    # Construit la phrase de tendance
    # V1.0.2 : années affichées pour la période
    annee0 = int(time.strftime("%Y"))
    anneeM = 0
    for annee in dictAneeesValeur.keys():
        if int(annee) < annee0:
            annee0 = int(annee)
        if int(annee) > anneeM:
            anneeM = int(annee)

    # v1.2.1 : random.choice() pour éviter les répétitions
    vp1 = "Sur la période " + str(annee0) + " - "  + str(anneeM)
    vp2 = "Sur les " + str(anneeM  - annee0 + 1) + " dernières années"
    vp3 = "Depuis " + str(anneeM  - annee0 + 1) + " ans"
    vp4 = "En partant de " + str(annee0) + " et jusqu'à " + str(anneeM)
    vp5 = "Pour la période allant de " + str(annee0) + " à " + str(anneeM)
    strTendance = random.choice([vp1, vp2, vp3, vp4, vp5]) + ", "  + nomValeur + " "
    if constante:
        if isWikicode:
            strTendance += "est constant et proche de " + \
                           modeleEuro(str(int(dictAneeesValeur[minAnnee])), isWikicode) + \
                           " " + unite
    elif croissante:
        strTendance += "augmente de façon continue de "+ \
                       modeleEuro(str(int(dictAneeesValeur[minAnnee])), isWikicode) + \
                       " à " + modeleEuro(str(int(dictAneeesValeur[maxAnnee])), isWikicode) + \
                       " " + unite
    elif decroissante:
        strTendance += "diminue de façon continue de " + \
                       modeleEuro(str(int(dictAneeesValeur[maxAnnee])), isWikicode) + \
                       " à " +  modeleEuro(str(int(dictAneeesValeur[minAnnee])), isWikicode) + \
                       " " + unite
    else:
        strTendance += "fluctue et présente un minimum de "+ \
                       modeleEuro(str(int(dictAneeesValeur[minAnnee])), isWikicode) + \
                       " " + unite + \
                       " en " + str(minAnnee) + " et un maximum de " + \
                       modeleEuro(str(int(dictAneeesValeur[maxAnnee])), isWikicode) + \
                       " " + unite + " en " + str(maxAnnee)

    if verbose:
        print("strTendance=", strTendance)
        print("Sortie de calculeTendanceSerieStr")
    return strTendance

# V1.0.5 : Délai entre deux requêtes au MinFi
def wait2requete(config, verbose):
    """ Met le programme en sommeil si  le temps entre 2 appels est trop court """
    if verbose:
        print("\nEntrée dans wait2requete")
    delaiEntre2Requetes = config.getfloat('Extraction', 'extraction.delaiEntre2Requetes')
    global __TPREC__

    if verbose:
        print("delaiEntre2Requetes =", delaiEntre2Requetes)
        print("__TPREC__ =", __TPREC__)

    deltaT = time.time() - __TPREC__
    if deltaT < delaiEntre2Requetes:
        print('Z', end='', flush=True)
        time.sleep(delaiEntre2Requetes - deltaT)

    __TPREC__ = time.time()
    if verbose:
        print("__TPREC__ =", __TPREC__)
        print("Sortie de wait2requete")

def getVersion(config):
    """ Renvoie une chaine de caractère correspondant à la version du code """
    appName = config.get('Version', 'version.appName')
    versionNumber = config.get('Version', 'version.number')
    versionDate = config.get('Version', 'version.date')
    return appName + " " + versionNumber + " du " + versionDate

def checkPythonVersion(config, verbose):
    """ Vérifie la version de python requise """
    if verbose:
        print("\nEntrée dans checkPythonVersion")

    pythonVersionReq = config.get('Env', 'env.pythonVersionReq')
    if verbose:
        print("Version requise :", pythonVersionReq)
    pythonVersionReqTest = pythonVersionReq.replace('x', '')
    versionPython = platform.python_version()
    if not versionPython.startswith(pythonVersionReqTest):
        print("Version de python incompatible :", versionPython)
        print("requis :", pythonVersionReq)
        sys.exit(1)
    else:
        print("Version Python OK :", versionPython)

    if verbose:
        print("\nSortie de checkPythonVersion")

def checkMatplolibOK():
    """ Vérifie que le module matplotlib est installé """
    try:
        import matplotlib
        print("Module matplotlib : trouvé")
        isMatplotlibOk = True
    except ModuleNotFoundError as exc:
        print("Warning : module matplotlib non disponible !")
        print(str(exc))
        print("Pour générer des graphiques, téléchargez et installez le module :")
        print("matplotlib : http://matplotlib.org")
        isMatplotlibOk = False
    return isMatplotlibOk


def traiteOptionStd(config, option, nomProg, docProgramme, usageListe):
    """ Traite les options communes des modules """
    verbose = False
    sortiePgm = False

    if option in ("-h", "--help"):
        print(docProgramme, "\n", getVersion(config), file=sys.stderr)
        sortiePgm = True

    if option in ("-u", "--usage"):
        msg = "Usage :\n"
        for usage in usageListe:
            msg += nomProg + " " + usage + "\n"
        print(msg, file=sys.stderr)
        sortiePgm = True

    if option in ("-v", "--verbose"):
        verbose = True
        print("Parametres :\n--verbose : mode bavard activé (debug)")

    if option in ("-V", "--version"):
        print(getVersion(config), file=sys.stderr)
        sortiePgm = True

    return verbose, sortiePgm

# V1.3.0 : Wikicode + HTML
def modeleEuro(valeur, isWikicode):
    """ Formate une valeur en Euros selon le type de code à produire"""
    chResult = ""
    if isWikicode:
        chResult += "{{euro|"
    chResult += valeur
    if isWikicode:
        chResult += "}}"
    else:
        chResult += "&nbsp;€"
    return chResult

def convertLettresAccents(ligne):
    """ # V2.4.0 : Conversion caractères accentués ou interdits dans un nom de fichier """
    accents = {'a': ['à', 'ã', 'á', 'â'],
               'A': ['À', 'Ã', 'Á', 'Â'],
               'e': ['é', 'è', 'ê', 'ë'],
               'E': ['É', 'È', 'Ê', 'Ë'],
               'i': ['î', 'ï'],
               'I': ['Î', 'Ï'],
               'u': ['ù', 'ü', 'û'],
               'U': ['Ù', 'Ü', 'Û'],
               'o': ['ô', 'ö'],
               'O': ['Ô', 'Ö'],
               'oe': ['œ'],
               'OE': ['Œ'],
               'ae': ['æ'],
               'AE': ['Æ'],
               'c': ['ç'],
               'C': ['Ç'],
               '_': ['(', ')', ' ', '/']} # 32/7/2020 = Ajout /

    for char, listCharsAccent in accents.items():
        for char2Replace in listCharsAccent:
            ligne = ligne.replace(char2Replace, char)
    return ligne

def setArrondi(dictAllGrandeurAnneeValeur, listAnneesOK,
               seuilkEuros, listeCles,
               verbose=False):
    """
    Détermination de l'arrondi à utiliser :
    Les valeurs sont prises pour les années définies par listAnneesOK
    Les sommes du MinFi sont en kEuros
    pour toutes les grandeurs si listeCles=None, sinon pour les clés de listeCles
    Si toutes les valeurs sont supérieures à seuilkEuros,
    demande l'affichage de milions
    Arrondi en kEuros si au moins une des valeurs à afficher est < seuilkEuros
    """

    if verbose:
        print("Entrée dans setArrondi")
        print('dictAllGrandeurAnneeValeur=', dictAllGrandeurAnneeValeur)
        print("seuilkEuros=", seuilkEuros)
        print("listeCles=", listeCles)

    if not dictAllGrandeurAnneeValeur:
        raise ValueError("Erreur : arrondi impossible car pas de valeurs à arrondir")

    if not listAnneesOK:
        raise ValueError("Erreur : arrondi impossible car aucune année de sélection des données")

    arrondi = 1e-3
    arrondiStr = 'M€'
    arrondiStrAffiche = "million d'euros (M€)"

    if not listeCles:
        listeCles = dictAllGrandeurAnneeValeur.keys()

    for grandeur in listeCles:
        for annee in listAnneesOK:
            try:
                if dictAllGrandeurAnneeValeur[grandeur][annee] < seuilkEuros:
                    arrondi = 1.0
                    arrondiStr = 'k€'
                    arrondiStrAffiche = "millier d'euros (k€)"
            except TypeError as exc:
                msg = ("Erreur : Impossible d'arrondir : " +
                                 "grandeur=" + grandeur + ", annee=" + str(annee) +
                                 ", valeur=" +
                                 str(dictAllGrandeurAnneeValeur[grandeur][annee]))
                raise ValueError(msg) from exc

    if verbose:
        print("arrondi =", arrondi, ", arrondiStr = ", arrondiStr,
              ", arrondiStrAffiche = ", arrondiStrAffiche)
        print("Sortie de setArrondi")

    return arrondi, arrondiStr, arrondiStrAffiche

def getNomsVille(config, nomVille, repertoireDepBase, verbose):
    """
    Retourne les noms des fichiers et répertoire qui stockeront les
    données de la ville.
    """

    if verbose:
        print("Entrée dans getNomsVille")
        print('nomVille=', nomVille)

    dictNomsVille = {}
    dictNomsVille['nom'] = nomVille
    dictNomsVille['villeNomDisque'] = convertLettresAccents(
        unicodedata.normalize('NFC', nomVille))
    dictNomsVille['nomRelatifIndexVille'] = \
                os.path.join(dictNomsVille['villeNomDisque'],
                             dictNomsVille['villeNomDisque'])
    indicateur = config.get('GenCode', 'gen.idFicDetail')
    dictNomsVille['villeWikicode'] = dictNomsVille['nomRelatifIndexVille'] + \
                                     '_' +  indicateur + '.html'
    dictNomsVille['villeHtml'] = dictNomsVille['nomRelatifIndexVille'] + '.html'
    dictNomsVille['repVille'] = os.path.join(repertoireDepBase,
                                             dictNomsVille['villeNomDisque'])

    if verbose:
        print("dictNomsVille=", dictNomsVille)
        print("Sortie de getNomsVille")

    return dictNomsVille

def getPageWikipediaFr(config, nomArticleUrl, verbose):
    """
    Ouvre une page de Wikipedia et en retourne le texte brut
    Affiche un point sur stdout sans newline.

    if problem urllib ssl.SSLError :
    Launch "Install Certificates.command" located in Python installation directory :
    sudo '/Applications/Python 3.6/Install Certificates.command'

    Exception urllib.error.HTTPError : si page Wikipedia inexistante

    V 4.0 : Respecte un délai entre 2 requetes Wikipedia
            pour ne pas faire croire à une attaque DOS
    """
    if verbose:
        print("Entrée dans getPageWikipediaFr")
        print("Recuperation de l'article :", nomArticleUrl)

    # Délai entre 2 requetes
    wait2requete(config, verbose)
    print('.', end='', flush=True)

    # Pour ressembler à un navigateur Mozilla/5.0
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]

    # Construction URL à partir de la config et du nom d'article
    baseWkpFrUrl = config.get('Extraction', 'wikipediaFr.baseUrl')
    actionTodo = config.get('Extraction', 'wikipediaFr.actionRow')
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

#REDIRECTION[[lienCC]]
#REDIRECTION [[lienCC]]
#REDIRECT[[lienCC]]
#REDIRECT [[lienCC]]
regExpPageRedirection = re.compile(r'^[ ]*#REDIRECT(ION)*[ ]*' +
                                   r'[\[]{2}(?P<lienCC>.*?)[\]]{2}')
def jumpRedirGetPageWikipediaFr(config, nomArticle, verbose):
    """
    Elimine les redirections de pages Wikipedia et lit la page finale
    Affiche un R sur stdout sans newline, pour chaque redirection.

    retourne :
    nomArticle : nom de la page Wikipedia au bout des redirections
    page : le texte de la page demandée
    Exception ValueError : si page Wikipedia inexistante
    """
    if verbose:
        print("Entrée dans jumpRedirGetPageWikipediaFr")
        print("Recuperation de l'article :", nomArticle)

    URLNomArticle = urllib.request.pathname2url(nomArticle)
    page = None
    try:
        # Elimination des pages de redirections Wikipedia
        findRedir = True
        countRedir = 0
        while findRedir:
            page = getPageWikipediaFr(config, URLNomArticle, verbose)
            line = page.splitlines()[0]
            m = regExpPageRedirection.search(line)
            if m:
                print('R', end='', flush=True)
                URLNomArticle = urllib.request.pathname2url(m.group("lienCC"))
                countRedir += 1
            else:
                findRedir = False

        if countRedir > 1:
            print("\nWarning Wikipedia page :", nomArticle,
                  ", Trop de redirection (>1) :", countRedir,
                  file=sys.stderr)
    except (urllib.error.HTTPError) as exc:
        raise ValueError("Problème page Wikipedia :" +
                         urllib.request.url2pathname(URLNomArticle) +
                         ":" + str(exc)) from exc

    nomArticle = urllib.request.url2pathname(URLNomArticle)
    if verbose:
        print("Sortie de jumpRedirGetPageWikipediaFr")
        print("nom de l'article linal =", nomArticle)

    return nomArticle, page

regExpBR = re.compile(r'[\s]*\<br[\s]*/>[\s]*')
regExpNobr = re.compile(r'[\{]{2}nobr\|(?P<Texte>.*)[\}]{2}')
regExpGras = re.compile(r"[']{3}(?P<Texte>.*)[']{3}")
regExpItalic = re.compile(r"[']{2}(?P<Texte>.*)[']{2}")
regExpHTMLComment = re.compile(r'\<!--.*--\>')
regExpLienAliasWKP = re.compile(r'[\[]{2}(?P<Texte>[^\]]*?)\|.*?[\]]{2}')
regExpLienWKP = re.compile(r'[\[]{2}(?P<Texte>.*?)[\]]{2}')
regExpAliasPipeLien = re.compile(r'.*\|[\s]*(?P<Texte>.*)')
regExpDrapeauModele = re.compile(r'[\{]{2}[\s]*[Dd]rapeau[\s]*\|.*[\}]{2}[\s]*')
regExpLienFile = re.compile(r'[\[]{2}[\s]*File\:.*?[\]]{2}[\s]*')
regExpLienWEBAlias = re.compile(r'\[[\s]*(?P<Texte>http[s]?\://.*?)/[\s]+.*\]')
regExpLienWEBSimple = re.compile(r'\[[\s]*(?P<Texte>http[s]?\://.*?)[\s]*\]')
regExpHTMLTag = re.compile(r'\<.*?\>')
def removeFormatWikipedia(valeurStr):
    """
    Retire les formattages Wikipedia définis dans les expressions
    régulières au dessus
    """
    valeurStr = regExpHTMLComment.sub("", valeurStr)
    valeurStr = regExpBR.sub(" ", valeurStr)
    valeurStr = regExpDrapeauModele.sub("", valeurStr)
    valeurStr = regExpLienFile.sub("", valeurStr)
    valeurStr = regExpLienWEBAlias.sub(r'\g<Texte>', valeurStr)
    valeurStr = regExpLienWEBSimple.sub(r'\g<Texte>', valeurStr)
    valeurStr = regExpLienAliasWKP.sub(r'\g<Texte>', valeurStr)
    valeurStr = regExpLienWKP.sub(r'\g<Texte>', valeurStr)
    valeurStr = regExpNobr.sub(r'\g<Texte>', valeurStr)
    valeurStr = regExpGras.sub(r'\g<Texte>', valeurStr)
    valeurStr = regExpItalic.sub(r'\g<Texte>', valeurStr)
    valeurStr = regExpAliasPipeLien.sub(r'\g<Texte>', valeurStr)
    valeurStr = regExpHTMLTag.sub("", valeurStr)
    valeurStr = valeurStr.replace('&nbsp;', ' ')
    return valeurStr

def getNomsGroupement(nomGroupement, repertoireGroupements, verbose):
    """
    Retourne les noms des fichiers et répertoire qui stockeront les
    données de ce groupement de communes.
    nomGroupement : nom usuel du groupement de communes (Wikipedia)
    """

    if verbose:
        print("Entrée dans getNomsGroupement")
        print('nomGroupement=', nomGroupement)

    dictNomsGroupement = {}
    dictNomsGroupement['nom'] = nomGroupement
    dictNomsGroupement['groupementNomDisque'] =\
            convertLettresAccents(unicodedata.normalize('NFC', nomGroupement))
    dictNomsGroupement['nomRelatifIndexGroupement'] = \
                os.path.join(dictNomsGroupement['groupementNomDisque'],
                             dictNomsGroupement['groupementNomDisque'])
    dictNomsGroupement['groupementWikicode'] = (
                dictNomsGroupement['nomRelatifIndexGroupement'] +
                "_wikicode.html")
    dictNomsGroupement['groupementHtml'] = \
                dictNomsGroupement['nomRelatifIndexGroupement'] + '.html'
    dictNomsGroupement['repGroupement'] = \
                os.path.join(repertoireGroupements,
                             dictNomsGroupement['groupementNomDisque'])

    if verbose:
        print("dictNomsGroupement=", dictNomsGroupement)
        print("Sortie de getNomsGroupement")

    return dictNomsGroupement
