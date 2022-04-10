# pip install k-means-constrained
from k_means_constrained import KMeansConstrained
import numpy as np
from math import *
import matplotlib.pyplot as plt
import random


# Affichage de la répartition initiale des colis
def afficher(L):
    x = []
    y = []
    for elm in L:
        x.append(elm[0])
        y.append(elm[1])
    fig = plt.figure()
    plt.scatter(x, y)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title("Emplacement des colis")
    plt.show()


# Affichage des clusters


def afficher2(L):
    fig = plt.figure()
    for i in range(len(L)):
        x = []
        y = []
        for elm in L[i]:
            x.append(elm[0])
            y.append(elm[1])
        plt.scatter(x, y)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title("Répartition des colis par clusters d'au plus 4 éléments")
    plt.show()


# Liste aléatoire des coordonnées des colis
L = []
for i in range(50):
    x = random.randint(1, 100)
    y = random.randint(1, 100)
    L.append([x, y])
L = np.array(L)


def cluster(L):
    """ 
    K-Means clustering avec comme contraintes le nombre minimal et maximal d'éléments par cluster

    Paramètres
    ----------
    L : int ndarray de longueur le nombre de colis à aller chercher
        Coordonnées [x,y] de tous les points correspondant à l'emplacement d'un colis

    Return
    ------
    liste_cluster : Liste de longueur le nombre de cluster crées
                    Liste des différents clusters
                    Un cluster contient les coordonnées [x,y] des points qu'il contient

    """

    # nombre de cluster à créer
    n_clusters = ceil(len(L) / 4)

    # KMeans clustering
    cluster = KMeansConstrained(n_clusters, size_min=3, size_max=4).fit(L)
    idx = cluster.labels_

    # transforme les arrays en une liste de points
    Liste_points = [list(point) for point in list(L)]

    # Liste des différents clusters crées
    liste_cluster = []
    for i in range(n_clusters):
        # regroupe les points d'un même cluster
        liste_cluster.append(
            [x for x in Liste_points if idx[Liste_points.index(x)] == i]
        )

    # print("l", liste_cluster)
    return liste_cluster


def cluster2(L):
    """ 
    K-Means clustering avec comme contraintes le nombre minimal et maximal d'éléments par cluster

    Paramètres
    ----------
    L : int ndarray de longueur le nombre de colis à aller chercher
        Coordonnées [x,y] de tous les points correspondant à l'emplacement d'un colis

    Return
    ------
    liste_cluster : Liste de longueur le nombre de cluster crées
                    Liste des différents clusters
                    Un cluster contient les coordonnées [x,y] des points qu'il contient

    """

    if len(L) < 4:
        print([L])
        return [L]
    else:
        # nombre de cluster à créer
        n_clusters = ceil(len(L) / 4)

        # KMeans clustering
        cluster = KMeansConstrained(n_clusters, size_max=4).fit(L)
        idx = cluster.labels_

        # transforme les arrays en une liste de points
        Liste_points = [list(point) for point in list(L)]

        # Liste des différents clusters crées
        liste_cluster = []
        for i in range(n_clusters):
            # regroupe les points d'un même cluster
            liste_cluster.append(
                [x for x in Liste_points if idx[Liste_points.index(x)] == i]
            )
        return liste_cluster


# afficher(L)
# liste_cluster = cluster(L)
# afficher2(liste_cluster)
