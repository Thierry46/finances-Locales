# -*- coding: utf-8 -*-
"""
************************************************************************************
Programme  : Database
Author : Thierry Maillard (TMD)
Date  : 19/6/2019 - 12/4/2020

Role : Gestion de la base des données de Finances Locale.

Licence : GPLv3
Copyright (c) 2020 - Thierry Maillard

This file is part of FinancesLocales project.

CalcAl project is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

CalcAl project is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with CalcAl project.  If not, see <http://www.gnu.org/licenses/>.
************************************************************************************
"""
import os.path
import sys
import sqlite3

def createDatabase(config, databasePath, verbose):
    """
    Initialise la structure de la base de données si elle n'existe pas
    Ouvre la base de données
    config : fichier de configuration du projet
    databasePath : chemin de la base de données (utile pour les test)
    Retourne un connecteur à la base de données
    """
    if verbose:
        print("Entree dans createDatabase")
        print("databasePath =", databasePath)

    # Test if directory containing database exists
    databasePathDir = os.path.dirname(databasePath)
    if not os.path.isdir(databasePathDir):
        print("Création du répertoire :", databasePathDir)
        os.makedirs(databasePathDir)

    if verbose:
        if os.path.isfile(databasePath):
            print("La base de données", databasePath, "existe déjà")
        else:
            print("Création de la base de données", databasePath)

    # Mets à jour une base existante avec les éléments des properties
    connDB = sqlite3.connect(databasePath)
    createMinFiTables(connDB, verbose)

    if verbose:
        print("Initialisation des départements à partir des properties")
    listeDepartements = initDepartements(config, verbose)
    connDB.executemany("""
            INSERT INTO departements(numDepartement, nomDepartement, article)
            VALUES (?, ?, ?)
            """, listeDepartements)

    if verbose:
        print("Initialisation des clés d'extraction MinFi",
              "à partir des properties (communes V et groupement GC)")
    for typeEntite in ("V", "GC"):
        listCles = initClesMinFi(config, typeEntite, verbose)
        # Enregistre les clés dans la table
        connDB.executemany("""
            INSERT INTO clesMinFi(codeCle, typeEntite, nomCle, typeCle, unite)
            VALUES (?, ?, ?, ?, ?)
            """, listCles)

    # Validation des modifications dans la base
    connDB.commit()

    if verbose:
        print("Sortie de createDatabase")
    return connDB

def closeDatabase(connDB, verbose):
    """ Close database """
    if verbose:
        print("Entree dans closeDatabase")

    if connDB:
        connDB.commit()
        connDB.close()
        if verbose:
            print("Commit + Base de données fermée")
    elif verbose:
        print("Base de données déjà fermée")

    if verbose:
        print("Sortie de closeDatabase")

def createMinFiTables(connDB, verbose):
    """ Crée les tables si nécessaire """
    if verbose:
        print("Entree dans createMinFiTables")
        print("Crée les tables")

    # Controls how strings are encoded and stored in the database
    connDB.execute('PRAGMA encoding = "UTF-8"')

    # V4.0 Supprime la table clesMinFi car recréée à partir des properties
    connDB.execute("DROP TABLE IF EXISTS departements")
    connDB.execute("""
        CREATE TABLE departements(
            numDepartement TEXT,
            nomDepartement TEXT,
            article TEXT
            )""")

    connDB.execute("""
        CREATE TABLE IF NOT EXISTS villes(
            codeCommune TEXT PRIMARY KEY UNIQUE,
            nomWkpFr TEXT,
            nomMinFi TEXT,
            nom TEXT,
            icom TEXT,
            score INTEGER,
            numDepartement TEXT,
            nomStrate TEXT,
            population TEXT,
            typeGroupement TEXT
            )""")

    # V4.0 Supprime la table clesMinFi car recréée à partir des properties
    connDB.execute("DROP TABLE IF EXISTS clesMinFi")
    # La cree à nouveau avec la bonne structure
    connDB.execute("""
        CREATE TABLE clesMinFi(
            codeCle TEXT,
            typeEntite TEXT,
            nomCle TEXT,
            typeCle TEXT,
            unite TEXT
            )""")

    connDB.execute("""
        CREATE TABLE IF NOT EXISTS dataFi(
            codeCommune TEXT,
            annee INTEGER,
            codeCle TEXT,
            valeur TEXT
            )""")

    # V4.0 : Add column sirenGroupement to existing villes table
    cursor = connDB.cursor()
    try:
        cursor.execute("ALTER TABLE villes ADD COLUMN sirenGroupement TEXT")
    except sqlite3.OperationalError:
        pass

    # V4.0 : Add column ancienneCommune to existing villes table
    #        Valeurs : 0 : commune actuelle, 1 : ancienne commune
    try:
        cursor.execute("ALTER TABLE villes ADD COLUMN ancienneCommune INTEGER")
        # Init champ ancienneCommune à 0
        cursor.execute("UPDATE villes SET ancienneCommune=0")
    except sqlite3.OperationalError:
        pass

    # V4.0 : Create table groupementCommunes : infos générales Wikipedia
    connDB.execute("""
        CREATE TABLE IF NOT EXISTS groupementCommunes(
            sirenGroupement TEXT PRIMARY KEY UNIQUE,
            nomArticleCC TEXT,
            nom TEXT,
            logo TEXT,
            région TEXT,
            département TEXT,
            forme TEXT,
            siège TEXT,
            siteWeb TEXT
            )""")

    # V4.0 : Create table dataFiGroupement : valeurs financières
    connDB.execute("""
        CREATE TABLE IF NOT EXISTS dataFiGroupement(
            sirenGroupement TEXT,
            annee INTEGER,
            codeCle TEXT,
            valeur TEXT
            )""")

    cursor.close()
    connDB.commit()

    if verbose:
        print("Sortie de createMinFiTables")

def initClesMinFi(config, typeEntite, verbose):
    """
        Remplit la table des cles d'extraction des CSV du ministère des finances
        à partir des properties
        v4.0 : ajout paramètre typeEntite
        typeEntite : "V" pour les communes, "GC" pour les groupements de communes
    """
    if verbose:
        print("Entree dans initClesMinFi")
        print("Initialise la table clesMinFi à partir des properties")
        print("typeEntite=", typeEntite)

    assert typeEntite in ("V", "GC")

    listCles = []
    # Génère les clés à 3 valeurs uniquement pour les communes
    if typeEntite == "V":
        for key in config['cleFi3Valeurs']:
            nomCle = key.replace("clefi.", "")
            listCles.append([config['cleFi3Valeurs'][key], typeEntite, nomCle,
                             "Valeur totale", "En milliers d'Euros"])
            listCles.append(["f" + config['cleFi3Valeurs'][key], typeEntite,
                             nomCle + " par habitant",
                             "Par habitant", "Euros par habitant"])
            listCles.append(["m" + config['cleFi3Valeurs'][key], typeEntite,
                             nomCle + " moyen",
                             "En moyenne pour la strate", "En milliers d'Euros"])

    # Génère les clés à 2 valeurs pour les communes
    if typeEntite == "V":
        for key in config['cleFi2Valeurs']:
            nomCle = key.replace("cletaxe.", "")
            listCles.append([config['cleFi2Valeurs'][key], typeEntite, nomCle,
                             "Taux", "taux voté (%)"])
            listCles.append([config['cleFi2Valeurs'][key].replace("t", "tm", 1),
                             typeEntite, nomCle + " moyen",
                             "taux moyen pour la strate",
                             "taux moyen de la strate (%)"])

    # Génère les clés à 2 valeurs pour les groupements de communes
    if typeEntite == "GC":
        for key in config['cleFi2ValeursGC']:
            if key.startswith("clefi."):
                nomCle = key.replace("clefi.", "")
                listCles.append([config['cleFi2ValeursGC'][key], typeEntite, nomCle,
                                 "Valeur totale", "En milliers d'Euros"])
                listCles.append([config['cleFi2ValeursGC'][key]+"hab", typeEntite,
                                 nomCle + " par habitant",
                                 "Par habitant", "Euros par habitant"])

            if key.startswith("cletaxe."):
                nomCle = key.replace("cletaxe.", "")
                listCles.append([config['cleFi2ValeursGC'][key], typeEntite, nomCle,
                                 "Valeur totale", "En milliers d'Euros"])
                listCles.append(["f"+config['cleFi2ValeursGC'][key], typeEntite,
                                 nomCle + " par habitant",
                                 "Par habitant", "Euros par habitant"])


    # Génère les clés à 1 valeur pour les communes
    if typeEntite == "V":
        for key in config['cleFi1Valeur']:
            nomCle = key.replace("clefi.", "")
            listCles.append([config['cleFi1Valeur'][key], typeEntite, nomCle,
                             "Valeur simple", ""])

    # Génère les clés à 1 valeur pour les groupements de communes
    if typeEntite == "GC":
        for key in config['cleFi1ValeurGC']:
            nomCle = key.replace("clefi.", "")
            if nomCle.startswith("cletaxe.taux"):
                nomCle = nomCle.replace("cletaxe.", "")
                listCles.append([config['cleFi1ValeurGC'][key],
                                 typeEntite, nomCle,
                                 "Taux", "taux voté (%)"])
            else:
                listCles.append([config['cleFi1ValeurGC'][key],
                                 typeEntite, nomCle,
                                 "Valeur simple", ""])

    if verbose:
        print("Sortie de initClesMinFi :", typeEntite, ":",
              len(listCles), "clés")
        print("listCles=", listCles)

    return listCles

def initDepartements(config, verbose):
    """
        Remplit la table des départements à partir des properties
    """
    if verbose:
        print("Entree dans initDepartements")
        print("Initialise la table clesMinFi à partir des properties")

    listDepartements = []
    for numDep in config['départements']:
        ligneDep = config['départements'][numDep].split(";")
        numDep3 = numDep
        if len(numDep3) < 3:
            numDep3 = "0" + numDep3
        numDep3 = numDep3.upper()
        listDepartements.append((numDep3, ligneDep[0], ligneDep[1]))

    if verbose:
        print("Sortie de initDepartements : ", len("listeDepartements"), "départements")
        print("listDepartements=", listDepartements)

    return listDepartements

def getListCodeClesMiniFi(connDB, typeEntite, verbose):
    """
    Retourne la liste des codes clés de la table clesMinFi
    V4.0 : Pour l'entité définie (V ou GC)
    """
    if verbose:
        print("Entree dans getListCodeClesMiniFi")
        print("typeEntite =", typeEntite)

    assert typeEntite in ('V', 'GC')

    cursor = connDB.cursor()
    cursor.execute("""SELECT codeCle FROM clesMinFi
                      WHERE typeEntite=?""",
                   (typeEntite,))
    listCodeCle = [codeCle[0] for codeCle in cursor.fetchall()]
    cursor.close()

    if verbose:
        print("listCodeCle =", listCodeCle)
        print("Sortie de getListCodeClesMiniFi")
    return listCodeCle

def enregistreLigneVilleMinFi(config, dictValues, connDB, verbose):
    """
    Enregistre dans la base de données les valeurs de dictValues lues dans
    les fichiers .CSV du ministere des finances.
    Retourne une exception ValueError si les données de l'année existent
    déjà dans le table dataFi.
    """
    if verbose:
        print("Entree dans enregistreLigneVilleMinFi")

    # Enregistrement des caractéristiques de la ville
    # Recherche si le code Insee existe déjà
    cursor = connDB.cursor()

    cursor.execute("""SELECT nomMinFi, numDepartement
                      FROM villes WHERE codeCommune=?""",
                   (dictValues['codeCommune'],))
    nomsVille = cursor.fetchone()

    if nomsVille is not None:
        # Test si des champs stables sont modifiés
        if nomsVille[0] and \
           nomsVille[0] != dictValues[config.get('cleFi1Valeur', 'clefi.nomMinFi')]:
            print("Attention nomMinFi pour commune", dictValues['codeCommune'],
                  ":", nomsVille[0], "!=",
                  dictValues[config.get('cleFi1Valeur', 'clefi.nomMinFi')],
                  file=sys.stderr)
        if nomsVille[1] and \
           nomsVille[1] != dictValues[config.get('cleFi1Valeur', 'clefi.departement')]:
            print("Attention departement pour commune", dictValues['codeCommune'],
                  ":", nomsVille[1], "!=",
                  dictValues[config.get('cleFi1Valeur', 'clefi.departement')],
                  file=sys.stderr)

        # Mise à jour de la base
        cursor.execute("""
                       UPDATE villes
                       SET nomMinFi=?, numDepartement=?,
                           nomStrate=?, population=?, typeGroupement=?
                       WHERE codeCommune=?
                       """,
                       (dictValues[config.get('cleFi1Valeur', 'clefi.nomMinFi')],
                        dictValues[config.get('cleFi1Valeur', 'clefi.departement')],
                        dictValues[config.get('cleFi1Valeur', 'clefi.nomStrate')],
                        dictValues[config.get('cleFi1Valeur', 'clefi.population1_1')],
                        dictValues[config.get('cleFi1Valeur', 'clefi.typeGroupement')],
                        dictValues['codeCommune']))
    else:
        if verbose:
            print(dictValues['codeCommune'], " introuvable dans table ville -> création")
        cursor.execute("""
                        INSERT INTO villes(codeCommune, nomMinFi, numDepartement,
                                           nomStrate, population, typeGroupement)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                       (dictValues['codeCommune'],
                        dictValues[config.get('cleFi1Valeur', 'clefi.nomMinFi')],
                        dictValues[config.get('cleFi1Valeur', 'clefi.departement')],
                        dictValues[config.get('cleFi1Valeur', 'clefi.nomStrate')],
                        dictValues[config.get('cleFi1Valeur', 'clefi.population1_1')],
                        dictValues[config.get('cleFi1Valeur', 'clefi.typeGroupement')])
                       )

    # Erreur si insertion valeur déjà existante pour cette année et pour cette ville
    # dans la table dataFi
    annee = dictValues[config.get('cleFi1Valeur', 'clefi.annee')]
    cursor.execute("""
                    SELECT codeCommune FROM dataFi
                    WHERE codeCommune=? AND annee=?
                   """, (dictValues['codeCommune'], annee))
    codeCommuneList = cursor.fetchone()
    if codeCommuneList is not None:
        cursor.close()
        connDB.rollback()
        raise ValueError("Erreur : Annee " + str(annee) + " déjà présente pour " +
                         codeCommuneList[0])

    # Enregistrement des autres donnees annuelles
    listDataMinFi = [(dictValues['codeCommune'], annee, key, dictValues[key])
                     for key in dictValues
                     if key not in config['cleFi1Valeur']]
    connDB.executemany("""
            INSERT INTO dataFi(codeCommune, annee, codeCle, valeur)
            VALUES (?, ?, ?, ?)
            """, listDataMinFi)

    # Rendre les information visibles
    cursor.close()
    connDB.commit()

    if verbose:
        print("Sortie de enregistreLigneVilleMinFi")

def enregistreVilleWKP(config, databasePath, listeVilles4Bd, verbose):
    """
    Enregistre dans la base de données les villes lues dans une liste.
    Produit une exception sqlite3.IntegrityError si la liste contient
    des doublons sur les codes commune.
    """
    if verbose:
        print("Entree dans enregistreVilleWKP")

    if len(listeVilles4Bd) == 0:
        print("Warning : enregistreVilleWKP : rien à enregistrer")

    # Crée la base de données si elle n'existe pas et l'ouvre
    connDB = createDatabase(config, databasePath, verbose)

    # Récupère la liste des codes communes des villes existantes
    listeCodeCommuneExistBD = [villes[0]
                               for villes in getListeCodeCommuneNomWkp(connDB,
                                                                       False, "",
                                                                       verbose)]
    if verbose:
        print("listeCodeCommuneExistBD=", listeCodeCommuneExistBD)

    # Insère la liste des nouvelles commune dans la base
    listeVille2Insert = [(ville['codeCommune'], ville['numDepartement'],
                          ville['icom'], ville['nomWkpFr'], ville['nom'])
                         for ville in listeVilles4Bd
                         if ville['codeCommune'] not in listeCodeCommuneExistBD]
    if verbose:
        print("listeVille2Insert=", listeVille2Insert)
    connDB.executemany("""
                        INSERT INTO villes(codeCommune, numDepartement, icom, nomWkpFr, nom)
                        VALUES (?, ?, ?, ?, ?)
                        """, listeVille2Insert)

    # Met à jour les communes existantes
    listeVille2Update = [(ville['numDepartement'], ville['icom'],
                          ville['nomWkpFr'], ville['nom'],
                          ville['codeCommune'])
                         for ville in listeVilles4Bd
                         if ville['codeCommune'] in listeCodeCommuneExistBD]
    if verbose:
        print("listeVille2Update=", listeVille2Update)
    connDB.executemany("""
                        UPDATE villes SET numDepartement=?, icom=?, nomWkpFr=?, nom=?
                        WHERE codeCommune=?
                        """,
                       listeVille2Update)

    connDB.commit()
    closeDatabase(connDB, verbose)

    print(len(listeVille2Insert), "villes insérées dans la base.")
    print(len(listeVille2Update), "villes mises à jour dans la base.")

    if verbose:
        print("Sortie de enregistreVilleWKP")

def getDictCodeCommuneAnnees(connDB, verbose):
    """
        Retourne la liste des villes et des années présentes dans la base.
    """
    if verbose:
        print("Entree dans getDictCodeCommuneAnnees")

    cursor = connDB.cursor()
    dictCodeCommuneAnnees = {}

    # Selection de toutes les villes de la base
    cursor.execute("SELECT codeCommune FROM villes ORDER BY codeCommune")
    for codeCommune in cursor.fetchall():
        dictCodeCommuneAnnees[codeCommune[0]] = []

    # Ajout des annees dans le dico
    # Jointure naturelle sur champ commun codeCommune
    cursor.execute("""
                    SELECT DISTINCT codeCommune, annee
                    FROM villes
                    NATURAL JOIN dataFi
                    ORDER BY codeCommune, annee
                   """)
    for codeannee in cursor.fetchall():
        dictCodeCommuneAnnees[codeannee[0]].append(codeannee[1])

    cursor.close()
    if verbose:
        print("Sortie de getDictCodeCommuneAnnees")
        print("dictCodeCommuneAnnees =", dictCodeCommuneAnnees)
    return dictCodeCommuneAnnees

def getListeCodeCommuneNomWkp(connDB, isFast, field, verbose):
    """
        Retourne la liste des villes présentes dans la base
        et leur nom Wikipedia.
        si isFast est Vrai, Traitement rapide.
        field : Si isFast, champ a tester pour limiter à ses valeurs nulles
        Si isFast, ignore les anciennes communes
        Retourne une liste de tupples (codeCommune, nomWkpFr)
    """
    if verbose:
        print("Entree dans getListeCodeCommuneNomWkp")
        print("isFast=", isFast, 'field=', field)
    assert not isFast or (isFast and field), "parametre isFast et field NULL"

    cursor = connDB.cursor()
    listCodeCommuneNomWkp = {}

    # Insertion de toutes les villes de la base dans les clés du dictionnaire
    if isFast:
        cursor.execute("""SELECT codeCommune, nomWkpFr
                            FROM villes
                            WHERE """ + field + """ is NULL AND ancienneCommune != 1
                            ORDER BY codeCommune""")
    else:
        cursor.execute("""SELECT codeCommune, nomWkpFr
                            FROM villes
                            ORDER BY codeCommune""")
    listCodeCommuneNomWkp = cursor.fetchall()
    cursor.close()
    if verbose:
        print("listCodeCommuneNomWkp =", listCodeCommuneNomWkp)
        print("Sortie de getListeCodeCommuneNomWkp")
    return listCodeCommuneNomWkp

def updateScoresVille(connDB, scoresVille, verbose):
    """
        Met à jour les scores des villes de la base
        fournies par le dictionnaire scoresVille
    """
    if verbose:
        print("Entree dans updateScoresVille")
        print("scoresVille=", scoresVille)

    listscore = [(scoresVille[key], key) for key in scoresVille]
    connDB.executemany("UPDATE villes SET score=? WHERE codeCommune=?", listscore)
    connDB.commit()

    if verbose:
        print("Sortie de updateScoresVille")

def getListeDepartement(connDB, verbose):
    """
        Retourne la liste des numéro et nom de département
        présents dans la base
    """
    if verbose:
        print("Entree dans getListeDepartement")

    cursor = connDB.cursor()
    # Sélection des département de la base
    cursor.execute("""SELECT numDepartement, article, nomDepartement
                        FROM departements
                        ORDER BY numDepartement""")
    listeDepartement = cursor.fetchall()
    cursor.close()
    if verbose:
        print("listeDepartement =", listeDepartement[:2])
        print("Sortie de getListeDepartement")

    return listeDepartement

def getListeVilles4Departement(connDB, numDepartement, verbose):
    """
        Retourne la liste des villes de ce département
        présents dans la base
    """
    if verbose:
        print("Entree dans getListeVilles4Departement")

    cursor = connDB.cursor()
    # Sans DISTINCT, les résultats sont en double ???
    cursor.execute("""SELECT DISTINCT codeCommune, nom, nomWkpFr,
                             article, nomDepartement,
                             typeGroupement, nomStrate,
                             score, population, numDepartement
                        FROM villes
                        NATURAL JOIN departements
                        WHERE numDepartement = ?
                        ORDER BY codeCommune
                   """, (numDepartement,))
    listeVille = cursor.fetchall()
    cursor.close()

    if verbose:
        print("Liste des villes du département", numDepartement, ":",
              listeVille[:2], "...")
        print("Sortie de getListeVilles4Departement")

    return listeVille


def getListeVilleGroupement(connDB, codeCommune, verbose):
    """
        Retourne une liste d'info sur le groupement
        d'appartenance d'une commune
        dont le codeCommune est passé en pramètre
        Peut être une liste vide si
        leur chanp de jointure sirenGroupement est vide.
    """
    if verbose:
        print("\nEntree dans getListeVilleGroupement pour commune :",
              codeCommune)

    cursor = connDB.cursor()
    cursor.execute("""SELECT DISTINCT Vi.sirenGroupement,
                                      Gc.nomArticleCC, Gc.nom
                        FROM villes Vi
                        INNER JOIN groupementCommunes Gc USING(sirenGroupement)
                        WHERE Vi.codeCommune = ?
                    """, (codeCommune,))
    resuInfosGroupement = cursor.fetchall()
    infosGroupement = []
    if resuInfosGroupement:
        infosGroupement = resuInfosGroupement[0]
    cursor.close()

    if verbose:
        print("infosGroupement =", infosGroupement)
        print("Sortie de getListeVilleGroupement")

    return infosGroupement

def getValeurs4VilleCle(connDB, codeCommune, codeCle, verbose=False):
    """
    Retourne une liste de (annee, valeur MinFi)
    pour une commune et un codeCle du Ministère des Finances
    triée par années (décroissantes) de la plus récente à la plus ancienne.
    Pour des raisons de performances, aucun contrôle n'est fait sur les codeCle
    La liste résultats peut donc être vide
    """
    if verbose:
        print("Entree dans getValeurs4VilleCle")
        print("codeCommune =", codeCommune, ", codeCle=", codeCle)

    cursor = connDB.cursor()
    cursor.execute("""SELECT annee, valeur
                        FROM dataFi
                        WHERE codeCommune = ? AND codeCle = ?
                        ORDER BY annee DESC
                   """, (codeCommune, codeCle))
    listeAnneeValeur = cursor.fetchall()
    cursor.close()

    if verbose:
        print("listeAnneeValeur=", listeAnneeValeur)
        print("Sortie de getValeurs4VilleCle")

    return listeAnneeValeur

def updateInfosGroupement(connDB, listeSirenCodeCommune,
                          dictSirenInfoCC, verbose):
    """
    Met à jour les numéros de siren des groupements de communes,
    fournis dans listeSirenCodeCommune, dans la table villes.
    listeSirenCodeCommune liste [sirenGroupement, ancienneCommune, codeCommune]
    pour mise à jour rapide en une seule requete SQL

    Met à jour les infos des groupements de communes,
    fournis dans dictSirenInfoCC, dans la table groupementCommunes.
    dictSirenInfoCC dict {sirenGroupement, dictInfos1CC}
    """

    if verbose:
        print("Entree dans updateInfosGroupement")
    cursor = connDB.cursor()

    if verbose:
        print("Mets à jour les numéros de siren dans la table villes")
    cursor.executemany("""UPDATE villes SET sirenGroupement=?,
                                            ancienneCommune=?
                           WHERE codeCommune=?""",
                       listeSirenCodeCommune)

    if verbose:
        print("Préparation des infos des groupements de communes")

     # Récupère les numéro de Siren existants dans la table groupementCommunes
    cursor.execute("""SELECT sirenGroupement FROM groupementCommunes""")
    setSirenExistant = set(sirenGroupement[0]
                           for sirenGroupement
                           in cursor.fetchall())

    # Sépare les code siren existant dans la base pour mise à jour des infos
    # des nouveaux pour insertion des infos.
    setSirenInfos4Update = set(dictSirenInfoCC.keys()).intersection(setSirenExistant)
    setSirenInfos4Insert = set(dictSirenInfoCC.keys()).difference(setSirenInfos4Update)

    # Préparation des données pour mise à jour
    # Valeur par défaut si champ non trouvé dans Wikipédia : None
    listeChamps = ["nomArticleCC", "nom", "région", "département", "forme", "siège",
                   "logo", "siteWeb", "sirenGroupement"]
    listeInfosGroupement4Update = list()
    for codeSiren in list(setSirenInfos4Update):
        listInfosChamp = [dictSirenInfoCC[codeSiren].get(champ, None)
                          for champ in listeChamps]
        listeInfosGroupement4Update.append(listInfosChamp)
    listeInfosGroupement4Insert = list()
    for codeSiren in list(setSirenInfos4Insert):
        listInfosChamp = [dictSirenInfoCC[codeSiren].get(champ, None)
                          for champ in listeChamps]
        listeInfosGroupement4Insert.append(listInfosChamp)

    if verbose:
        print("Insere ou met à jour dans la base les infos des groupements de communes")

    # Mise à jour de la table groupementCommunes de la base de données
    if listeInfosGroupement4Update:
        cursor.executemany("""UPDATE groupementCommunes
                              SET nomArticleCC=?, nom=?, Région=?, département=?,
                                  forme=?, siège=?, logo=?, siteWeb=?
                              WHERE sirenGroupement=?""",
                           listeInfosGroupement4Update)
        print(f"\n{len(listeInfosGroupement4Update)} villes mises à jour dans la base.")
    else:
        print("\nAucune ville à mettre à jour dans la base !")

    # Insertion dans la table groupementCommunes de la base de données
    if listeInfosGroupement4Insert:
        connDB.executemany("""
                INSERT INTO groupementCommunes(nomArticleCC, nom, Région, département,
                                               forme, siège, logo, siteWeb,
                                               sirenGroupement)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, listeInfosGroupement4Insert)
        print(f"\n{len(listeInfosGroupement4Insert)} villes insérées dans la base.")
    else:
        print("\nAucune ville à insérer dans la base !")

    # Rendre les informations visibles
    cursor.close()
    connDB.commit()

    if verbose:
        print("Sortie de updateInfosGroupement")

def getSirenInfosGroupementsAnnees(connDB, verbose):
    """
    Récupère les numéros de SIREN des groupements déjà présents dans la base
    ainsi que leurs noms et années des infos financières déjà enregistrées.
    table groupementCommunes.
    Retour : dictSirenInfos dict {sirenGroupement :
                                    {nomArticleCC, nom, [listeAnnées]}}
    """

    if verbose:
        print("Entree dans getSirenInfosGroupementsAnnees")

    dictSirenInfos = dict()
    cursor = connDB.cursor()

    # Récupère les informations des groupements des villes de la base
    cursor.execute("""SELECT DISTINCT villes.sirenGroupement, groupementCommunes.nom,
                                      nomArticleCC
                        FROM villes, groupementCommunes
                        WHERE villes.sirenGroupement = groupementCommunes.sirenGroupement""")
    dictSirenInfos = {sirenNoms[0]:(sirenNoms[1], sirenNoms[2], [])
                      for sirenNoms in cursor.fetchall()}

    # Récupère les années enregistréees dans la base pour les groupements
    # de communes précédents
    cursor.execute("""SELECT DISTINCT villes.sirenGroupement, dataFiGroupement.annee
                        FROM villes, dataFiGroupement
                        WHERE villes.sirenGroupement = dataFiGroupement.sirenGroupement
                        ORDER BY villes.sirenGroupement, dataFiGroupement.annee
                        """)
    for sirenAnnee in cursor.fetchall():
        if sirenAnnee[0] in dictSirenInfos:
            dictSirenInfos[sirenAnnee[0]][2].append(sirenAnnee[1])

    cursor.close()

    if verbose:
        print("Sortie de getSirenInfosGroupementsAnnees")
        print(len(dictSirenInfos), "groupements de communes avec des",
              "données financières enregistrées dans la base")
    return dictSirenInfos

def enregistreLigneGroupementMinFi(dictValues, connDB, verbose):
    """
    Enregistre dans la base de données les valeurs de dictValues lues dans
    les fichiers .CSV du ministere des finances pour les groupements
    de communes.
    Retourne une exception ValueError si les données de l'année existent
    déjà dans le table dataFi.
    """
    if verbose:
        print("Entree dans enregistreLigneGroupementMinFi")

    # Enregistrement des donnees dans dataFiGroupement
    listDataMinFi = [(dictValues['siren'], int(dictValues['exer']), key, dictValues[key])
                     for key in dictValues
                     if key not in ('siren', 'exer')]
    connDB.executemany("""
            INSERT INTO dataFiGroupement(sirenGroupement, annee, codeCle, valeur)
            VALUES (?, ?, ?, ?)
            """, listDataMinFi)

    # Rendre les information visibles
    connDB.commit()

    if verbose:
        print("Sortie de enregistreLigneGroupementMinFi")

def getListeGroupements(connDB, verbose):
    """
        Retourne la liste des groupements de communes
        présents dans la base
    """
    if verbose:
        print("Entree dans getListeGroupements")

    cursor = connDB.cursor()
    cursor.execute("""SELECT sirenGroupement, nomArticleCC, nom,
                            région, département, forme, siège,
                            logo, siteWeb
                        FROM groupementCommunes
                        ORDER BY nom""")
    listeGroupements = cursor.fetchall()
    cursor.close()

    if verbose:
        print("Liste des groupements de communes",
              listeGroupements[:2], "...")
        print("Sortie de getListeGroupements")

    return listeGroupements

def getAllValeursDataMinFi4Entite(connDB, typeEntite,
                                  cleEntite, verbose=False):
    """
    Lit toutes les valeurs financières de la table dataFi ou dataFiGroupement
    pour une entité de clé cleEntite
    en une seule requête SQL
    Retourne toutes les valeurs dans un dictionnaire :
    dict[typeGrandeur][NomGrandeur][annee]
    Les valeurs autres que valeurs simples sont converties
    en float et sont en unités des données originales du MinFi
    typeEntite  doit valoir "V" ou "GC"
    """
    if verbose:
        print("Entree dans getAllValeursDataMinFi4Entite")
        print("typeEntite =", typeEntite)
        print("cleEntite =", cleEntite)
    assert typeEntite in ("V", "GC")

    # Création de la requete en fonction du typeEntite
    requete = """SELECT annee, valeur, typeCle, nomCle FROM dataFi, clesMinFi
                 WHERE dataFi.codeCle = clesMinFi.codeCle
                     AND clesMinFi.typeEntite = ?
                     AND codeCommune = ?"""

    # Modif de la requete pour les groupements de communes
    if typeEntite == "GC":
        requete = requete.replace("dataFi", "dataFiGroupement")
        requete = requete.replace("codeCommune", "sirenGroupement")

    # Récupère toutes les données dans la base
    cursor = connDB.cursor()
    cursor.execute(requete, (typeEntite, cleEntite,))
    listeClesValeur = cursor.fetchall()
    cursor.close()

    # Fabrique le dictionnaire résultat
    dictAllGrandeur = dict()
    for grandeur in listeClesValeur:
        valeur = grandeur[1]
        if grandeur[2] != "Valeur simple":
            try:
                valeur = float(grandeur[1])
                if valeur > 1e8:
                    raise ValueError()
            except ValueError:
                print("Ignore entité=", cleEntite, grandeur)
                continue
        if grandeur[2] not in dictAllGrandeur:
            dictAllGrandeur[grandeur[2]] = dict()
        if grandeur[3] not in dictAllGrandeur[grandeur[2]]:
            dictAllGrandeur[grandeur[2]][grandeur[3]] = dict()
        dictAllGrandeur[grandeur[2]][grandeur[3]][grandeur[0]] = \
             valeur

    if verbose:
        print("dictAllGrandeur=", dictAllGrandeur)
        print("Sortie de getAllValeursDataMinFi4Entite")

    return dictAllGrandeur

def getListeAnneesDataMinFi4Entite(connDB, typeEntite,
                                   cleEntite, verbose):
    """
    Retourne la liste de toutes les années connues pour les données
    d'une entite (ville ou groupement de commune) définie par cleEntite
    de la table dataFi ou dataFiGroupement.
    typeEntite  doit valoir "V" ou "GC"
    """
    if verbose:
        print("Entree dans getListeAnneesDataMinFi4Entite")
        print("typeEntite =", typeEntite)
        print("cleEntite =", cleEntite)
    assert typeEntite in ("V", "GC")

    requete = """SELECT DISTINCT annee
                 FROM dataFi
                 WHERE codeCommune = ?
                 ORDER BY annee DESC"""

    # Modif de la requete pour les groupements de communes
    if typeEntite == "GC":
        requete = requete.replace("dataFi", "dataFiGroupement")
        requete = requete.replace("codeCommune", "sirenGroupement")

    # Récupère toutes les données dans la base
    cursor = connDB.cursor()
    cursor.execute(requete, (cleEntite,))
    listeAnnee = [annee[0] for annee in cursor.fetchall()]
    cursor.close()

    if verbose:
        print("listeAnnee=", listeAnnee)
        print("Sortie de getListeAnneesDataMinFi4Entite")

    return listeAnnee
