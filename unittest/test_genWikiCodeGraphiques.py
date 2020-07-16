"""
Name : test_genWikiCodeGraphiques.py
Author : Thierry Maillard (TMD)
Date : 23/10/2019 - 14/4/2020
Role : Tests unitaires du projet FinancesLocales avec py.test
Utilisation : python3 -m pytest [-k "nomTest"] .
options :
    -s : pour voir les sorties sur stdout
Ref : http://sametmax.com/un-gros-guide-bien-gras-sur-les-tests-unitaires-en-python-partie-3/
Ref : http://pytest.org/latest/
prerequis : pip install pytest

#Licence : GPLv3
#Copyright (c) 2015 - 2019 - Thierry Maillard

   This file is part of Finance Locales project.

   FinancesLocales project is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   FinancesLocales project is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with Finance Locales project.  If not, see <http://www.gnu.org/licenses/>.
"""
import configparser
import os.path

import pytest

import genCodeGraphiques
import genWikiCodeGraphiques
import genCode
import genCodeCommon
import updateDataMinFi
import database
import utilitaires

@pytest.mark.parametrize("courbesTest",
    [
        [
            {
                'cle' : "dont charges de personnel",
                'sousCle' : "Valeur totale",
                'libelle' : "Charges de personnel",
                'couleur' : ["Bb blue.jpg", "brightblue", "Point bleu"],
             },
             {
                 'cle' : "achats et charges externes",
                 'libelle' : "achats et charges externes",
                 'sousCle' : "Valeur totale",
                 'couleur' : ["Red rectangle.svg", "red", "Point rouge"],
             },
        ],
        [
            {
                 'cle' : 'taux taxe habitation',
                 'sousCle' : "Taux",
                 'libelle' : "taux taxe habitation",
                 'couleur' : ["Flag of Beni.svg", "teal", "Point vert"],
             },
             {
                 'cle' : "taux taxe foncière bâti",
                 'sousCle' : "Taux",
                 'libelle' : 'taux foncier bâti',
                 'couleur' : ["Black222.JPG", "black", "Point noir"],
             },
        ],
        [
            {
                 'cle' : 'ratio dette / caf',
                 'sousCle' : "",
                 'libelle' : 'Ratio = Encours de la dette / CAF',
                 'couleur' : ["Bb blue.jpg", "brightblue", "Point bleu"],
             },
        ]
    ])
def test_genGraphique(courbesTest):
    """
        teste generation de courbe
    """

    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # récup données de test
    pathDatabaseMini = config.get('Test', 'genCode.pathDatabaseMini')
    pathCSVMini = config.get('Test', 'genCode.pathCSVMini')
    if os.path.isfile(pathDatabaseMini):
        print("destruction de la base :", pathDatabaseMini)
        os.remove(pathDatabaseMini)

    # Insertion dans la table ville des villes à traiter
    # Création base
    connDB = database.createDatabase(config, pathDatabaseMini, False)
    connDB.executemany("""
        INSERT INTO villes(codeCommune, nomMinFi, nom, nomWkpFr)
        VALUES (?, ?, ?, ?)
        """, (('068376', 'WITTENHEIM', 'Wittenheim', 'Wittenheim'),)
                       )
    connDB.commit()

    # Création de la création de la base de test
    param = ['updateDataMinFi.py', pathDatabaseMini, pathCSVMini]
    updateDataMinFi.main(param)
    assert os.path.isfile(pathDatabaseMini)

    # Lit dans la base les infos concernant la ville à traiter
    listeVilleWalheim = [ville
                         for ville in database.getListeVilles4Departement(connDB, '068', False)
                         if ville[0] == '068376']
    ville = listeVilleWalheim[0]

    # Recup des annees de données fiscales por WALHEIN
    dictAllGrandeur = database.getAllValeursDataMinFi4Entite(connDB, 'V',
                                                             ville[0], False)
    listAnnees = database.getListeAnneesDataMinFi4Entite(connDB, 'V',
                                                         ville[0], False)
    assert len(listAnnees) == 3
    # Agglomère certaines grandeurs et complète dictAllGrandeur
    genCodeCommon.calculeGrandeur(config, dictAllGrandeur,
                            listAnnees, True, False)

    # Test calcul des valeurs
    nbCourbeOrig = len(courbesTest)
    anneesOK = genCodeGraphiques.controleSeries(dictAllGrandeur, courbesTest,
                                                listAnnees, False)

    # Détermination de l'arrondi à utiliser et à afficher
    listeCles = [courbe['cle']
                 for courbe in courbesTest
                 if courbe['sousCle'] == "Valeur totale"]
    if listeCles:
        arrondi, arrondiStr, arrondiStrAffiche = \
                utilitaires.setArrondi(dictAllGrandeur["Valeur totale"], anneesOK,
                                       1000.0, listeCles, False)
    else:
        arrondi = 1.0
        arrondiStr = "%"
        arrondiStrAffiche = arrondiStr

    # Generation des graphiques
    graphiqueWiki, legendeVille, legendeStrate = \
            genWikiCodeGraphiques.genGraphique(config, dictAllGrandeur,
                                               ville[1], anneesOK,
                                               courbesTest,
                                               'graph.largeurPage',
                                               arrondi,
                                               arrondiStrAffiche,
                                               True)
    for annee in anneesOK:
        assert str(annee) in graphiqueWiki
    for courbe in courbesTest:
        assert courbe['libelle'] in legendeVille

    for courbe in courbesTest:
        for annee in anneesOK:
            if courbe['cle'].startswith('Taux'):
                valeurData = \
                    round(dictAllGrandeur['Taux'][courbe['cle']][annee])
            elif courbe['sousCle'] == "":
                valeurData = round(dictAllGrandeur[courbe['cle']][annee])
            else:
                valeurData = round(dictAllGrandeur[courbe['sousCle']][courbe['cle']][annee] * arrondi)
            assert str(valeurData) in graphiqueWiki

    # Fermeture base
    database.closeDatabase(connDB, True)
