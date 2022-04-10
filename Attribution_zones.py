import random
from Clustering_constrained import cluster, cluster2
import matplotlib.pyplot as plt
import numpy as np

# coord_to_zone prend en entrée les coordonnées d'un point de collecte
# et renvoie le numéro de la zone correpondante


def coord_to_zone(coord):
    xpos, ypos = coord
    if xpos <= 10:
        if ypos <= 13:
            return 1
        else:
            return 2
    elif xpos <= 19:
        if ypos <= 13:
            return 3
        else:
            return 4
    elif xpos <= 28:
        if ypos <= 13:
            return 5
        else:
            return 6
    else:
        if ypos <= 13:
            return 7
        else:
            return 8


# colis_to_vect prend en entrée la liste des coordonnées des articles qui composent
# un colis et renvoie en sortie le vecteur qui représente le nombre d'articles du colis
# dans chaque zone


def colis_to_vect(colis):
    vect = [0 for i in range(8)]
    for article in colis:
        # print(coord_to_zone(article))
        vect[coord_to_zone(article) - 1] += 1
    return vect


# génération d'une liste aléatoire de 10 commandes (ici commande = colis) contenant
# chacune entre 1 et 5 articles

nbtuileslong = 38
nbtuileshaut = 29
tab_carton = [[0] * (nbtuileshaut + 1) for _ in range(nbtuileslong + 1)]
nums_cartons = []
dict_cmds = {}
art_pos = {}


def gen_commandes(nb_commandes, nb_articles, tab_carton, nbtuileslong, nbtuileshaut):
    cmd_list = []
    for n in range(1, nb_commandes + 1):
        nb_cartons_posés = 0
        nb_cartons = random.randint(1, nb_articles)
        cart_list = []
        while nb_cartons_posés < nb_cartons:
            num_carton = random.randint(1, 999)
            if num_carton in art_pos:
                i, j = art_pos[num_carton]
                # print("article {} dans plusieurs commandes".format(num_carton))
                nb_cartons_posés += 1
                cart_list.append((i, j))
            else:
                i, j = (
                    random.randint(1, nbtuileslong - 1),
                    random.randint(1, nbtuileshaut - 1),
                )
                if (i % 3 == 2 or i % 3 == 0) and j % 6 != 1 and j < nbtuileshaut - 3:
                    if tab_carton[i][j] == 0:
                        tab_carton[i][j] = num_carton
                        art_pos[num_carton] = (i, j)
                        nb_cartons_posés += 1
                        cart_list.append((i, j))
        cle = str(colis_to_vect(cart_list))
        cmd_list.append(colis_to_vect(cart_list))
        if cle not in dict_cmds:
            dict_cmds[cle] = [cart_list]
        else:
            dict_cmds[cle].append(cart_list)

    # print(dict_cmds)
    return cmd_list


# liste_cmds = gen_commandes(40, 5, tab_carton, nums_cartons, nbtuileslong, nbtuileshaut)

# print(liste_cmds)

# clust = cluster(liste_cmds)
# print(clust)


def vect_to_coord(liste_cmd):
    L = []
    for cluster in liste_cmd:
        clust_coord = []
        for commande in cluster:
            cmd_coord = dict_cmds[str(commande)].pop()
            clust_coord.append(cmd_coord)
        L.append(clust_coord)
    return L


def afficher2(L):
    for cluster in L:
        fig = plt.figure()
        for commande in cluster:
            x = []
            y = []
            for colis in commande:
                x.append(colis[0])
                y.append(colis[1])
            plt.scatter(x, y)
        plt.xlabel("x")
        plt.xlim(0, 40)
        plt.ylabel("y")
        plt.ylim(0, 30)
        plt.title("Répartition des colis par clusters d'au plus 4 éléments")
        plt.show()


# points = vect_to_coord(clust)
# print(points)
# afficher2(points)


def verif_problemes(pts, points):
    # print(len(points))
    mat_cluster2 = []
    k = 0
    while k < len(pts):
        if len(pts[k]) > 4:
            # print("on réajuste la taille du cluster {}, qui est au départ {}".format(k, len(points[k])))
            probleme = pts.pop(k)
            if len(probleme) % 4 == 1:
                # plutôt que de laisser des commandes isolées
                mat_cluster2.append(probleme.pop())
                # on rapplique l'algorithme de clustering à celles-ci

            points2 = [probleme[x : x + 4] for x in range(0, len(probleme), 4)]

            # print(points2)
            points += points2

        else:
            k += 1
    # print(len(points))
    return mat_cluster2


def generation_commandes(
    nb_commandes, nb_articles, tab_carton, nbtuileslong, nbtuileshaut
):
    liste_cmds = gen_commandes(
        nb_commandes, nb_articles, tab_carton, nbtuileslong, nbtuileshaut
    )
    points = vect_to_coord(cluster(liste_cmds))
    mat_cluster = verif_problemes(points, points)
    while len(mat_cluster) > 0:
        # print("on résout les problèmes")
        mat_to_vect2 = []

        for commande in mat_cluster:
            cle = str(colis_to_vect(commande))
            mat_to_vect2.append(colis_to_vect(commande))
            if cle not in dict_cmds:
                dict_cmds[cle] = [commande]
            else:
                dict_cmds[cle].append(commande)
        # print("test", len(mat_to_vect2))
        clust2 = cluster2(mat_to_vect2)
        points_2 = vect_to_coord(clust2)
        # print(points_2)
        points += points_2
        mat_cluster = verif_problemes(points, points)

    # retirer les listes vides
    # print("on retire les listes vides")

    i = 0
    while i < len(points):
        n = len(points[i])
        if n == 0:
            points.pop(i)
        elif n > 4:
            print("error cluster size")
        else:
            i += 1
    return points


# generation_commandes(1000, 5, tab_carton, nbtuileslong, nbtuileshaut)


def new_commande(strategie, cluster_restant):
    # print("début")
    # print(strategie[6])
    # print(colis_to_vect(strategie[6]))
    """a_agreger = []
    for item in strategie:
        print(item)
        a_agreger += [colis_to_vect(item[i]) for i in range(len(item))]
        print(a_agreger)"""
    a_agreger = [
        colis_to_vect(item[commande])
        for item in strategie
        for commande in range(len(item))
    ]

    congestion = [sum(x) for x in zip(*a_agreger)]
    if congestion == []:
        congestion = [0 for i in range(8)]

    # print("congestion", congestion)

    tau = (10000.0, 0, [0 for i in range(8)])
    for i in range(len(cluster_restant)):
        cluster = cluster_restant[i]
        clust_agreg = [colis_to_vect(commande) for commande in cluster]
        clust_agreg += [congestion]
        test_congestion = [sum(x) for x in zip(*clust_agreg)]
        tau_test = np.std(test_congestion)
        if tau_test < tau[0]:
            tau = (tau_test, i, test_congestion)
    # print("commande_choisie", cluster_restant[tau[1]])
    # print("nouvelle congestion", tau[2])
    # print("fin", "\n")

    return tau[1]

