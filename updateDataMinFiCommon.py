# -*- coding: utf-8 -*-
"""
*********************************************************
Module : updateDataMinFiCommon.py
Auteur : Thierry Maillard (TMD)
Date : 7/4/2020

Role : Fonctions communes à updateDataMinFi et
        à updateGroupementsCommunes.

-----------------------------------------------------------
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

import os
import os.path

import database

def getColumnPosition(header, typeEntite, connDB, verbose):
    """
        Contrôle que tous les codes clés de la table clesMinFi
        soient présents dans la ligne d'entête header
        passée en paramètre
        v4.0 : ajout paramètre typeEntite
        typeEntite : "V" pour les communes, "GC" pour les groupements de communes
        Retourne :
        - un dictionnaire (moclé : position (0:n))
        - la liste des clés manquantes
    """
    if verbose:
        print("Entrée dans getColumnPosition")
        print("header =", header)

    listMissingKeys = []

    # Récupère la liste des codes clés de la table clesMinFi pour les communes
    listCodeCle = database.getListCodeClesMiniFi(connDB, typeEntite, verbose)
    if verbose:
        print("listCodeCle=", listCodeCle)

    headerList = header.replace(' ', '').split(";")
    dictPositionColumns = dict()
    for motCle in listCodeCle:
        try:
            dictPositionColumns[motCle] = headerList.index(motCle)
        except ValueError:
            listMissingKeys.append(motCle)

    if len(dictPositionColumns) == 0:
        raise ValueError("Entete CSV non valide (aucun mot-clé trouvé) " + header)

    if verbose:
        print("dictPositionColumns :", dictPositionColumns)
        print("Mots clés manquant :", listMissingKeys)
        print("Sortie de getColumnPosition")
    return dictPositionColumns, listMissingKeys
