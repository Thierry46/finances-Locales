"""
Name : test_genCodeGraphiques.py
Author : Thierry Maillard (TMD)
Date : 23/10/2019 - 1/11/2019
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
import genCode
import genCodeCommon
import updateDataMinFi
import database
import utilitaires

@pytest.mark.parametrize("courbesTest",
    [
        [
            {
                'cle' : "capacité autofinancement caf par habitant",
                'sousCle' : "Par habitant",
             },
             {
                 'cle' : 'encours de la dette au 31 12 n par habitant',
                 'sousCle' : "Par habitant",
             },
        ],
        [
            {
                'cle' : "dont charges de personnel",
                'sousCle' : "Valeur totale",
             },
             {
                 'cle' : "achats et charges externes",
                 'sousCle' : "Valeur totale",
             },
        ],
        [
            {
                 'cle' : 'taux taxe habitation',
                 'sousCle' : "Taux",
             },
             {
                 'cle' : "taux taxe foncière bâti",
                 'sousCle' : "Taux",
             },
        ],
        [
            {
                 'cle' : 'ratio dette / caf',
                 'sousCle' : "",
             },
        ]
    ])
def test_controleSeriesOK(courbesTest):
    """
        teste selection des courbes : valeurs OK
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
    dictAllGrandeur = database.getAllValeursDataMinFi4Entite(connDB, 'V', ville[0], False)
    listAnnees = database.getListeAnneesDataMinFi4Entite(connDB, 'V',
                                                         ville[0], False)
    assert len(listAnnees) == 3

    # Grandeurs calculées
    genCodeCommon.calculeGrandeur(config, dictAllGrandeur,
                            listAnnees, True, False)

    # Test calcul des valeurs
    nbCourbeOrig = len(courbesTest)
    anneesOK = genCodeGraphiques.controleSeries(dictAllGrandeur, courbesTest,
                                                listAnnees, True)
    assert anneesOK == sorted(listAnnees)
    assert nbCourbeOrig == len(courbesTest)

    # Fermeture base
    database.closeDatabase(connDB, True)
    
def test_controleSeriesSuppr():
    """
        teste selection des courbes : suppression de courbe sans valeur
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
    dictAllGrandeur = database.getAllValeursDataMinFi4Entite(connDB, 'V', ville[0], False)
    listAnnees = database.getListeAnneesDataMinFi4Entite(connDB, 'V',
                                                         ville[0], False)
    assert len(listAnnees) == 3

    # La courbe de clé "inconnue" devra être supprimee
    courbesTest = [
            {
                'cle' : "inconnue",
                'sousCle' : "Valeur totale",
             },
             {
                 'cle' : "achats et charges externes",
                 'sousCle' : "Valeur totale",
             },
        ]

    # Test calcul des valeurs
    anneesOK = genCodeGraphiques.controleSeries(dictAllGrandeur, courbesTest,
                                                listAnnees, True)
    assert anneesOK == sorted(listAnnees)
    assert len(courbesTest) == 1
    assert courbesTest[0]['cle'] == "achats et charges externes"

    # Fermeture base
    database.closeDatabase(connDB, True)
    
def test_controleSeriesSupprAll():
    """
        teste selection des courbes :
        suppression de toutes les courbes d'un graphique :
        doit lever une exception ValueError
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
    dictAllGrandeur = database.getAllValeursDataMinFi4Entite(connDB, 'V', ville[0], False)
    listAnnees = database.getListeAnneesDataMinFi4Entite(connDB, 'V',
                                                         ville[0], False)
    assert len(listAnnees) == 3

    # Les courbee de clé "inconnue*" devront être supprimees
    # et une exception levee
    courbesTest = [
            {
                'cle' : "inconnue1",
                'sousCle' : "Valeur totale",
             },
             {
                 'cle' : "inconnue2",
                 'sousCle' : "Valeur totale",
             },
        ]

    # Test calcul des valeurs
    with pytest.raises(ValueError,
                       match=r'.*pas de courbe pour le graphique.*'):
        genCodeGraphiques.controleSeries(dictAllGrandeur, courbesTest,
                                                listAnnees, True)

    # Fermeture base
    database.closeDatabase(connDB, True)

@pytest.mark.parametrize( "isComplet, isWikicode",
                          [[False, True],
                           [False, False],
                           [True, True],
                           [True, False]])
def test_genCodeGraphiques_OK(isComplet, isWikicode):
    """ Test la génération de tous les graphiques """
    
    config = configparser.RawConfigParser()
    config.read('FinancesLocales.properties')

    # Création répertoire de sortie des graphiques
    repOutGraphique = config.get('Test', 'genHTMLCodeGraphiques.pathOutputTest')
    if not os.path.isdir(repOutGraphique):
        os.mkdir(repOutGraphique)

    # récup données de test
    pathDatabaseMini = config.get('Test', 'genCode.pathDatabaseMini')
    pathCSVMini = config.get('Test', 'genCode.pathCSVMini')
    if os.path.isfile(pathDatabaseMini):
        print("Destruction de la base de test :", pathDatabaseMini)
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
    dictAllGrandeur = database.getAllValeursDataMinFi4Entite(connDB, 'V', ville[0], False)
    listAnnees = database.getListeAnneesDataMinFi4Entite(connDB, 'V',
                                                         ville[0], False)
    assert len(listAnnees) == 3
    
    # Agglomère certaines grandeurs et complète dictAllGrandeur
    genCodeCommon.calculeGrandeur(config, dictAllGrandeur,
                            listAnnees, True, False)

    # Lecture du modèle
    nomBaseModele = config.get('Modele', 'modele.nomBaseModele')
    typeSortie = config.get('GenCode', 'gen.idFicDetail')
    modele = nomBaseModele + '_' + typeSortie + '.txt'
    textSection = utilitaires.lectureFiltreModele(modele, isComplet, False)

    # Generation des graphiques pour une ville
    textSection = genCodeGraphiques.genCodeGraphiques(
                      config, repOutGraphique, dictAllGrandeur,
                      textSection, ville[1],
                      listAnnees, isComplet,
                      isWikicode, True, True)

    # Test des valeurs générées
    if isWikicode:
        assert "Graphique polygonal" in textSection
    else:
        assert ".svg" in textSection

@pytest.mark.parametrize("courbes",
                [
                    {
                        'nomGraphique' : "VALEUR_TOTALE_TEST",
                        'courbes' : [
                            {'sousCle' : "Valeur totale"},
                            {'sousCle' : "Valeur totale"},
                            {'sousCle' : "En moyenne pour la strate"}]
                    },
                    {
                        'nomGraphique' : "TAUX_TEST",
                        'courbes' : [
                            {'sousCle' : "taux"},
                            {'sousCle' : "taux moyen"},
                            {'sousCle' : "taux"}]
                    },
                    {
                        'nomGraphique' : "PAR_HABITANT_TEST",
                        'courbes' : [
                            {'sousCle' : "Par habitant"},
                            {'sousCle' : "Par habitant"}]
                    },
                    {
                        'nomGraphique' : "RATIO_TEST",
                        'courbes' : [{'sousCle' : ""}]
                    }
                ])
def test_controleSousCle_OK(courbes):
    """ test controle sous clés OK """
    genCodeGraphiques.controleSousCle(courbes, True)

@pytest.mark.parametrize("courbes, messageOK",
                [
                    [
                        {
                        'nomGraphique' : "VALEUR_TOTALE_PB",
                        'courbes' : [
                            {'sousCle' : "Valeur totale"},
                            {'sousCle' : "Par habitant"},
                            {'sousCle' : "En moyenne pour la strate"}]
                        },
                        r'.*Par habitant.*VALEUR_TOTALE_PB'
                    ],
                    [
                        {
                        'nomGraphique' : "TAUX_TEST_PB",
                        'courbes' : [
                            {'sousCle' : "taux"},
                            {'sousCle' : "taux moyen"},
                            {'sousCle' : "Par habitant"}]
                        },
                        r'.*commençant par taux.*TAUX_TEST_PB'
                    ],
                    [
                        {
                        'nomGraphique' : "NO_COURBE_TEST",
                        'courbes' : []
                        },
                        r'Aucune sous clé pour la courbe '
                    ]
                ])
def test_controleSousCle_PB(courbes, messageOK):
    """ test controle sous clés incompatibles """
    with pytest.raises(ValueError, match=messageOK):
        genCodeGraphiques.controleSousCle(courbes, True)

