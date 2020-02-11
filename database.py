# -*- coding: utf-8 -*-
"""
************************************************************************************
Programme  : Database
Author : Thierry Maillard (TMD)
Date  : 19/6/2019 - 10/2/2020

Role : Gestion de la base des données de Finances Locale.

Licence : GPLv3
Copyright (c) 2019 - Thierry Maillard

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

    existDB = os.path.isfile(databasePath)
    if verbose:
        if existDB:
            print("La base de données", databasePath, "existe déjà")
        else:
            print("Création de la base de données", databasePath)

    # Crée ou complete eventuellement une base existante
    connDB = sqlite3.connect(databasePath)
    createMinFiTables(connDB, verbose)

    if not existDB:
        print("Initialisation des départements à partir des properties")
        listeDepartements = initDepartements(config, verbose)
        connDB.executemany("""
            INSERT INTO departements(numDepartement, nomDepartement, article)
            VALUES (?, ?, ?)
            """, listeDepartements)

        print("Initialisation des clés d'extraction MinFi à partir des properties")
        listCles = initClesMinFi(config, verbose)
        # Enregistre les clés dans la table
        connDB.executemany("""
            INSERT INTO clesMinFi(codeCle, nomCle, typeCle, unite)
            VALUES (?, ?, ?, ?)
            """, listCles)
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

    connDB.execute("""
        CREATE TABLE IF NOT EXISTS departements(
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

    connDB.execute("""
        CREATE TABLE IF NOT EXISTS clesMinFi(
            codeCle TEXT PRIMARY KEY UNIQUE,
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

    connDB.commit()

    if verbose:
        print("Sortie de createMinFiTables")

def initClesMinFi(config, verbose):
    """
        Remplit la table des cles d'extraction des CSV du ministère des finances
        à partir des properties
    """
    if verbose:
        print("Entree dans initClesMinFi")
        print("Initialise la table clesMinFi à partir des properties")

    listCles = []
    # Génère les clés à 3 valeurs
    for key in config['cleFi3Valeurs']:
        nomCle = key.replace("clefi.", "")
        listCles.append([config['cleFi3Valeurs'][key], nomCle,
                         "Valeur totale", "En milliers d'Euros"])
        listCles.append(["f" + config['cleFi3Valeurs'][key],
                         nomCle + " par habitant",
                         "Par habitant", "Euros par habitant"])
        listCles.append(["m" + config['cleFi3Valeurs'][key],
                         nomCle + " moyen",
                         "En moyenne pour la strate", "En milliers d'Euros"])

    # Génère les clés à 2 valeurs
    for key in config['cleFi2Valeurs']:
        nomCle = key.replace("cletaxe.", "")
        listCles.append([config['cleFi2Valeurs'][key], nomCle,
                         "Taux", "taux voté (%)"])
        listCles.append([config['cleFi2Valeurs'][key].replace("t", "tm", 1),
                         nomCle + " moyen",
                         "taux moyen pour la strate",
                         "taux moyen de la strate (%)"])

    # Génère les clés à 1 valeur
    for key in config['cleFi1Valeur']:
        nomCle = key.replace("clefi.", "")
        listCles.append([config['cleFi1Valeur'][key], nomCle, "Valeur simple", ""])

    if verbose:
        print("Sortie de initClesMinFi : ", len(listCles), "clés")
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

def getListCodeClesMiniFi(connDB, verbose):
    """ Retourne la liste des codes clés de la table clesMinFi """
    if verbose:
        print("Entree dans getListCodeClesMiniFi")

    cursor = connDB.cursor()
    cursor.execute("SELECT codeCle FROM clesMinFi")
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
                                                                       False,
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

def getListeCodeCommuneNomWkp(connDB, isFast, verbose):
    """
        Retourne la liste des villes présentes dans la base
        et leur nom Wikipedia.
        si isFast est Vrai, seule les communes avec un score NULL
        est récupéré.
        Retourne une liste de tupples (codeCommune, nomWkpFr)
    """
    if verbose:
        print("Entree dans getListeCodeCommuneNomWkp")
        print("isFast=", isFast)

    cursor = connDB.cursor()
    listCodeCommuneNomWkp = {}

    # Insertion de toutes les villes de la base dans les clés du dictionnaire sans annees
    if isFast:
        cursor.execute("""SELECT codeCommune, nomWkpFr
                            FROM villes
                            WHERE score is NULL
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


def getAllValeurs4Ville(connDB, codeCommune, verbose=False):
    """
    Lit toutes les valeurs pour une ville en une seule requête SQL
    Retourne toutes les valeurs dans un dictionnaire :
    dict[typeGrandeur][NomGrandeur][annee]
    Les valeurs autres que valeurs simples sont converties
    en float et sont en unités des données originales du MinFi
    """
    if verbose:
        print("Entree dans getAllValeurs4Ville")
        print("codeCommune =", codeCommune)

    # Récupère toutes les données dans la base
    cursor = connDB.cursor()
    cursor.execute("""SELECT annee, valeur, typeCle, nomCle
                        FROM dataFi
                        NATURAL JOIN clesMinFi
                        WHERE codeCommune = ?
                   """, (codeCommune,))
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
                print("Ignore commune=", codeCommune, grandeur)
                continue
        if grandeur[2] not in dictAllGrandeur:
            dictAllGrandeur[grandeur[2]] = dict()
        if grandeur[3] not in dictAllGrandeur[grandeur[2]]:
            dictAllGrandeur[grandeur[2]][grandeur[3]] = dict()
        dictAllGrandeur[grandeur[2]][grandeur[3]][grandeur[0]] = \
             valeur

    if verbose:
        print("dictAllGrandeur=", dictAllGrandeur)
        print("Sortie de getAllValeurs4Ville")

    return dictAllGrandeur

def getListeAnnees4Ville(connDB, codeCommune, verbose):
    """
    Retourne la liste de toutes les années connues pour les données
    d'une ville.
    """
    if verbose:
        print("Entree dans getListeAnnees4Ville")
        print("codeCommune =", codeCommune)

    cursor = connDB.cursor()
    cursor.execute("""SELECT DISTINCT annee
                        FROM dataFi
                        WHERE codeCommune = ?
                        ORDER BY annee DESC
                   """, (codeCommune,))
    listeAnnee = [annee[0] for annee in cursor.fetchall()]
    cursor.close()

    if verbose:
        print("listeAnnee=", listeAnnee)
        print("Sortie de getListeAnnees4Ville")

    return listeAnnee
