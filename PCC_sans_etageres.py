import pygame
import time
import random
import math
from copy import deepcopy
from Attribution_zones import generation_commandes

# les Stratégies
strategie1 = False          # Les robots se détachent des étagères si le temps d'attente d'un opérateur est trop important
strategie2 = False         # Les robots se détachent des étagères si ils sont coincés
        # Problème commun 1 -> Les étagères qui cherchent leur dernier carton qui est déjà coincé par une autre étagère
        # Problème commun 2 -> Les étagères sont coincées entre 2 autres étagères
        # Comment déclarer cette étagère ? Libre, coincée ?
strategie3 = False          # non opti // dans waiting shelves, selectionne que celles non coincées
strategie4 = False          # Les robots coincés se rapprochent de leur objectif
strategie5 = True          # Les robots peuvent se suivre

# facteur gérant la taille d'une case sur l'interface graphique ( à mettre à 2 sous windows)
c = 3
d = 0  # facteur de décalage par rapport à l'affichage (reste à 0)

nbtuileslong = 38  # un de moins
nbtuileshaut = 27  # un de moins
nb_cartons = 35
depot = [(3*3+1, (nbtuileshaut-1)), (3*6+1, (nbtuileshaut-1)), (3*9+1,(nbtuileshaut-1))]  # Les coordonnés des différents points de dépot
robots = []
nb_workers = 6
display = True

robot_etagere_obst = [-2, -1, 1, 2, 3, 4, 5]
robot_seul_obst = [-1, 1, 2, 3, 4, 5]
worker_obst = [-1]
priority_robot_etagere_obst = [-2,-1, 5]
priority_robot_seul_obst = [-1, 5]
display_obst_on_screen = []          #test de pos
nb_commandes = 400

def spawn_robots():
    global robots,destination_robots, distance_to_destination_robots
    robots = robots + [(x, y, -1) for (x, y) in depot]
    destination_robots = destination_robots + [(x, y) for (x, y) in depot]
    distance_to_destination_robots = distance_to_destination_robots + [10000 for _ in depot]

def init(nb_robot):
    """
    Initialisation de la fenêtre et des différentes variables

    """
    global robots, pos_obstacles, tab_carton, myfont, tab_lab, miniFont, destination_shelves, strategie, connected, cluster_restant, worker_zone, pos_worker_zone, workers, shelves, destination_robots, distance_to_destination_robots
    tab_carton = []
    points = []
    tab_carton = [[0]*(nbtuileshaut+1) for _ in range(nbtuileslong+1)]
    points = generation_commandes(nb_commandes, 5, tab_carton, nbtuileslong, nbtuileshaut)
    cluster_restant = deepcopy(points)
    #robots = [(1,1,[0,0,0,0]),(12,1,[0,0,0,0]),(24,1,[0,0,0,0])]
    robots = [(x, y, -1) for (x, y) in depot]+[(x, y, -1) for (x, y) in depot] + [(x, y, -1) for (x, y) in depot] +[(x, y, -1) for (x, y) in depot] + [(x, y, -1) for (x, y) in depot] + [(x, y, -1) for (x, y) in depot]+ [(x, y, -1) for (x, y) in depot] + [(x, y, -1) for (x, y) in depot]
    robots = robots[0:nb_robot]
    shelves = [(x+1, y, [0, 0, 0, 0])for (x, y) in depot]+[(x-1, y, [0, 0, 0, 0])for (x, y) in depot]+[(x+2, y, [0, 0, 0, 0])for (x, y) in depot] + \
        [(x-2, y, [0, 0, 0, 0])for (x, y) in depot]+[(x+1, y, [0, 0, 0, 0]) for (x, y) in depot]+[(x-1, y, [0, 0, 0, 0])for (x, y) in depot]+[(x+2, y, [0, 0, 0, 0]) for (x, y) in depot]+[(x-2, y, [0, 0, 0, 0])for (x, y) in depot]+[(x+1, y, [0, 0, 0, 0]) for (x, y) in depot]+[(x-1, y, [0, 0, 0, 0])for (x, y) in depot]
    workers = [(1, 1, []), (13, 1, []), (28, 1, []),
               (1, 13, []), (13, 13, []), (28, 13, [])]
    # initialisation des destinations des robots
    destination_shelves = [(i, j) for (i, j, k) in shelves]
    destination_robots = [(i, j) for (i, j, k) in robots]
    distance_to_destination_robots = [10000 for _ in robots]
    strategie = [[] for _ in shelves]
    connected = [0 for _ in shelves]
    if display:
        pygame.font.init()
        # Définit la police + taille de police des cartons sur les obstacles
        myfont = pygame.font.SysFont('Comic Sans MS', 23)
        # Définit la police + taille de police des cartons sur les robots
        miniFont = pygame.font.SysFont('Comic Sans MS', 12)

# Définition des coordonnés des obstacles pour former l'entrepot

    tab_lab = [[0]*(nbtuileshaut+1) for _ in range(nbtuileslong+1)]

    for i in range(len(tab_lab)):
        for j in range(len(tab_lab[0])):
            if i == 0 or j == 0 or i == nbtuileslong or j == nbtuileshaut:
                tab_lab[i][j] = -1

    for i in range(len(tab_lab)):
        for j in range(len(tab_lab[0])):
            if (i % 3 == 2 or i % 3 == 0) and j % 6 != 1 and j != len(tab_lab[0])-2:
                tab_lab[i][j] = -1

# Placement des obstacles sur l'interface graphique
    pos_obstacles = []

    for i in range(0, len(tab_lab)):
        for j in range(0, len(tab_lab[0])):
            if tab_lab[i][j] == -1:
                pos_obstacles.append(
                    (d+(i*10)*c, c*j*10+d, d+c*i*10+c*10, c*j*10+c*10+d))

    worker_zone = [[] for _ in range(nb_workers)]
    pos_worker_zone = [[] for _ in range(nb_workers)]

    for i in range(0, len(tab_lab)):
        for j in range(0, len(tab_lab[0])):
            if tab_lab[i][j] == 0 and j < len(tab_lab[0])-2 and j % 6 != 1:
                num_worker = i // ((nbtuileslong+1)//3) + \
                    (j // (nbtuileshaut//2))*3
                worker_zone[num_worker].append((i, j))
                pos_worker_zone[num_worker].append((d+(i*10)*c, c*j*10+d, d+c*i*10+c*10, c*j*10+c*10+d))


# Placement aléatoire de n cartons dans l'entrepot, numérotation entre 1 et 999
"""
    tab_carton = [[0]*(nbtuileshaut+1) for _ in range(nbtuileslong+1)]
    nums_cartons = []

    nb_cartons_posés = 0
    while nb_cartons_posés < nb_cartons:
        i, j = random.randint(
            1, nbtuileslong-1), random.randint(1, nbtuileshaut-1)
        if (i % 3 == 2 or i % 3 == 0) and j % 6 != 1 and j != len(tab_lab[0])-2:
            if tab_carton[i][j] == 0:
                num_carton = random.randint(1, 999)
                if not num_carton in nums_cartons:
                    tab_carton[i][j] = num_carton
                    nb_cartons_posés += 1
                    nums_cartons.append(num_carton)
"""


def find_cartons_pos():  # Transforme la matrice des colis en une liste de coordonnées des colis
    res = []
    for i in range(len(tab_carton)):
        for j in range(len(tab_carton[0])):
            if tab_carton[i][j] > 0:
                if tab_lab[i+1][j] == 0:
                    res.append((i+1, j))
                else:
                    res.append((i-1, j))
    return res


def lieu_recup_carton(list_carton):
    res = []
    for i in range(len(list_carton)):
        (x, y) = list_carton[i]
        if x % 3 == 0:
            res.append((x+1, y))
        elif x % 3 == 2:
            res.append((x-1, y))
    return res


def enumerate_in_order(liste):
    res = []
    new_liste = liste[:]
    for i in range(len(liste)):
        mini_id = new_liste.index(min(new_liste))
        res.append(mini_id)
        new_liste[mini_id] = 100000
    return res


# par un algorithme de Djikstra, détermine le carton
def findclosest(coord, liste_obj, list_obstacles):
    # le plus proche du robots situé en 'coord' parmi ceux de 'liste', et renvoie
    # la position du point de collecte ainsi que la durée du parcours et la position
    # à t+1 où aller pour se rendre au point de collecte
    (posx, posy) = coord
    laby = deepcopy(tab_lab)
    list_obstacles_reduite = []
    for val in list_obstacles:
        if not (1 <= val <= 4):
            list_obstacles_reduite.append(val)
    if 5 in list_obstacles:
        if laby[posx][posy] != 0:
            if laby[posx][posy] == 1:
                a_save = laby[posx][posy-1]
                laby[posx][posy-1] = 5
                a_remove = (posx, posy-1)
            if laby[posx][posy] == 2:
                a_save = laby[posx][posy+1]
                laby[posx][posy+1] = 5
                a_remove = (posx, posy+1)
            if laby[posx][posy] == 3:
                a_save = laby[posx+1][posy]
                laby[posx+1][posy] = 5
                a_remove = (posx+1, posy)
            if laby[posx][posy] == 4:
                a_save = laby[posx-1][posy]
                laby[posx-1][posy] = 5
                a_remove = (posx-1, posy)
    """
    for (i, j) in liste_obj:
        if not laby[i][j] in list_obstacles_reduite:
            laby[i][j] = -3
    """
    if (posx,posy) in liste_obj:
        return ((posx, posy), (posx, posy))
    laby[posx][posy] = -1
    listepriorite = [(posx, posy, -1, -1)]

    while listepriorite != []:
        i, j, i0, j0 = listepriorite.pop(0)
        laby[i][j] = -1
        if (i+1,j) in liste_obj:
            if not laby[i+1][j] in list_obstacles:
                if (i0, j0) == (-1, -1):
                    return ((i+1, j), (i+1, j))
                else:
                    return ((i+1, j), (i0, j0))
            elif not laby[i+1][j] in list_obstacles_reduite and strategie5:
                if laby[i+1][j] != 3:
                    if (i0, j0) == (-1, -1):
                        if laby[i+1][j] == 4:
                            listepriorite.append((i+1, j, i+1, j))
                        else:
                            pass
                    else:
                        listepriorite.append((i+1, j, i0, j0))
        if not laby[i+1][j] in list_obstacles:
            if (i0, j0) == (-1, -1):
                listepriorite.append((i+1, j, i+1, j))
            else:
                listepriorite.append((i+1, j, i0, j0))
        elif not laby[i+1][j] in list_obstacles_reduite and strategie5:
            if laby[i+1][j] != 3:
                if (i0, j0) == (-1, -1):
                    listepriorite.append((i+1, j, i+1, j))
                else:
                    listepriorite.append((i+1, j, i0, j0))
        if (i-1,j) in liste_obj:
            if not laby[i-1][j] in list_obstacles:
                if (i0, j0) == (-1, -1):
                    return ((i-1, j), (i-1, j))
                else:
                    return ((i-1, j), (i0, j0))
            elif not laby[i-1][j] in list_obstacles_reduite and strategie5:
                if laby[i-1][j] != 4:
                    if (i0, j0) == (-1, -1):
                        if laby[i-1][j] == 3:
                            return ((i-1, j), (i-1, j))
                    else:
                        return ((i-1, j), (i0, j0))
        if not laby[i-1][j] in list_obstacles:
            if (i0, j0) == (-1, -1):
                listepriorite.append((i-1, j, i-1, j))
            else:
                listepriorite.append((i-1, j, i0, j0))
        elif not laby[i-1][j] in list_obstacles_reduite and strategie5:
            if laby[i-1][j] != 4:
                if (i0, j0) == (-1, -1):
                    listepriorite.append((i-1, j, i-1, j))
                else:
                    listepriorite.append((i-1, j, i0, j0))
        if (i,j+1) in liste_obj:
            if not laby[i][j+1] in list_obstacles:
                if (i0, j0) == (-1, -1):
                    return ((i, j+1), (i, j+1))
                else:
                    return ((i, j+1), (i0, j0))
            elif not laby[i][j+1] in list_obstacles_reduite and strategie5:
                if laby[i][j+1] != 2:
                    if (i0, j0) == (-1, -1):
                        if laby[i][j+1] == 1:
                            return ((i, j+1), (i, j+1))
                    else:
                        return ((i, j+1), (i0, j0))
        if not laby[i][j+1] in list_obstacles:
            if (i0, j0) == (-1, -1):
                listepriorite.append((i, j+1, i, j+1))
            else:
                listepriorite.append((i, j+1, i0, j0))
        elif not laby[i][j+1] in list_obstacles_reduite and strategie5:
            if laby[i][j+1] != 2:
                if (i0, j0) == (-1, -1):
                    listepriorite.append((i, j+1, i, j+1))
                else:
                    listepriorite.append((i, j+1, i0, j0))
        if (i,j-1) in liste_obj:
            if not laby[i][j-1] in list_obstacles:
                if (i0, j0) == (-1, -1):
                    return ((i, j-1), (i, j-1))
                else:
                    return ((i, j-1), (i0, j0))
            elif not laby[i][j-1] in list_obstacles_reduite and strategie5:
                if laby[i][j-1] != 1:
                    if (i0, j0) == (-1, -1):
                        if laby[i][j-1] == 2:
                            return ((i, j-1), (i, j-1))
                    else:
                        return ((i, j-1), (i0, j0))
        if not laby[i][j-1] in list_obstacles:
            if (i0, j0) == (-1, -1):
                listepriorite.append((i, j-1, i, j-1))
            else:
                listepriorite.append((i, j-1, i0, j0))
        elif not laby[i][j-1] in list_obstacles_reduite and strategie5:
            if laby[i][j-1] != 1:
                if (i0, j0) == (-1, -1):
                    listepriorite.append((i, j-1, i, j-1))
                else:
                    listepriorite.append((i, j-1, i0, j0))
    return ((posx, posy), (posx, posy))


def nextstep(coord, destination, list_obstacles):
    (posx, posy) = coord
    a_remove = None
    a_save = 0
    #print((posx, posy), [destination],list_obstacles)
    """
    if 5 in list_obstacles:
        if tab_lab[posx][posy] != 0:
            if tab_lab[posx][posy] == 1:
                a_save = tab_lab[posx][posy-1]
                tab_lab[posx][posy-1] = 5
                a_remove = (posx, posy-1)
            if tab_lab[posx][posy] == 2:
                a_save = tab_lab[posx][posy+1]
                tab_lab[posx][posy+1] = 5
                a_remove = (posx, posy+1)
            if tab_lab[posx][posy] == 3:
                a_save = tab_lab[posx+1][posy]
                tab_lab[posx+1][posy] = 5
                a_remove = (posx+1, posy)
            if tab_lab[posx][posy] == 4:
                a_save = tab_lab[posx-1][posy]
                tab_lab[posx-1][posy] = 5
                a_remove = (posx-1, posy)
    """
    _, res = findclosest((posx, posy), [destination], list_obstacles)
    #if a_remove != None:
    #    tab_lab[a_remove[0]][a_remove[1]] = a_save
    return res

def strat_sur_couloir(bot_strategie):
    res = []
    for part in bot_strategie:
        part_res = []
        for (x,y) in part:
            if x % 3 == 0:
                part_res.append((x+1,y))
            elif x % 3 == 2:
                part_res.append((x-1,y))
            else:
                print("error bad box placement")
        res.append(part_res)
    return res

def trouve(elmt, liste):
    for i, part in enumerate(liste):
        if elmt in part:
            return i

    return -1


def findindice(obj, pos):
    (x, y) = pos
    for i in range(len(obj)):
        if (obj[i][0] == x) and (obj[i][1] == y):
            return i
    return -1


def colle(liste):
    res = []
    for part in liste:
        res = res + part
    return res


def liste_vide(liste):
    for part in liste:
        if part != []:
            return 0
    return 1


def request_worker(coord):
    x, y = coord
    num = trouve((x, y), worker_zone)
    if not (x,y) in workers[num][2]:
        workers[num][2].append((x, y))

def unrequest_worker(coord):
    x,y = coord
    num = trouve((x, y), worker_zone)
    if (x,y) in workers[num][2]:
        workers[num][2].pop(workers[num][2].index((x, y)))

def distance(pos1, pos2):
    '''
    Renvoie la distance en nombre de blocs du chemin le plus court entre 2 positions (position d'un robot ou d'un opérateur) 
    '''
    x1, x2, y1, y2 = pos1[0]-1, pos2[0]-1, pos1[1]-1, pos2[1]-1

    if y1//6 == y2//6:  # même ligne horizontale
        if x1 == x2:  # même étagère
            distance = abs(y1-y2)
        else:  # il faut contourner l'étagère
            distance = abs(x1-x2)+min(y1 % 6+y2 % 6, 12-(y1 % 6+y2 % 6))
    else:  # ligne horizontale différente : distance classique
        distance = abs(x1-x2)+abs(y1-y2)
    return(distance)


def waitingshelves(shelves, workers, robots, id_robot):
    res = []
    for i, shelf in enumerate(shelves):
        add = 1
        pos_shelf = (shelf[0], shelf[1])
        for worker in workers:
            (wx, wy, requests) = worker
            if pos_shelf in requests:
                sx, sy = pos_shelf
                dist_case_robot = distance(
                    (sx, sy), (robots[id_robot][0], robots[id_robot][1]))
                dist_case_operateur = distance((sx, sy), (wx, wy))
                if dist_case_robot <= dist_case_operateur:
                    add = 0
        if pos_shelf in destination_robots:
            add = 0
        for bot in robots:
            if bot[2] == i:
                add = 0
        if shelves[i][2] == [0, 0, 0, 0] and liste_vide(strategie[i]):
            if cluster_restant == []:
                add = 0
        if strategie3 == True:
            disapear,stuck,(newposx,newposy) = step1(0,[(shelf[0], shelf[1],i)],workers)
            if stuck:
                add = 0
        if add == 1:
            res.append((shelf[0], shelf[1]))

    return res


def lonlyshelves(shelves, robots):
    for i, shelf in enumerate(shelves):
        pos_shelf = (shelf[0], shelf[1])
        if findindice(robots, pos_shelf) == -1:
            tab_lab[shelf[0]][shelf[1]] = -2


def clearlonlyshelves():
    for i in range(len(tab_lab)):
        for j in range(len(tab_lab[0])):
            if tab_lab[i][j] == -2:
                tab_lab[i][j] = 0

def clearboard():
    for i in range(len(tab_lab)):
        for j in range(len(tab_lab[0])):
            if tab_lab[i][j] != -1:
                tab_lab[i][j] = 0

def finishedshelves(shelves):
    res = []
    for i,shelf in enumerate(shelves):
        if shelves[i][2] == [0, 0, 0, 0] and liste_vide(strategie[i]):
            res.append((shelf[0], shelf[1]))
    return res


def move_robotsV2(bots, operateurs, shelves):  # Deplace tous les robots
    global tab_lab,display_obst_on_screen
    new_robots = [() for _ in range(len(robots))]
    new_shelves = []
    case_occupée = []
    delete_bot = []
    lonlyshelves(shelves, bots)
    liste_enumerate = enumerate_in_order(distance_to_destination_robots)
    for i in liste_enumerate:
        posx, posy, linked = bots[i]
        newposx, newposy = posx, posy
        if linked != -1:
            # si arrivé à destination
            if (posx, posy) == destination_shelves[linked]:
                if (posx, posy) in depot:       # si sur un depot
                    shelves[linked] = (shelves[linked][0]+1,
                                       shelves[linked][1], [0, 0, 0, 0])
                    destination_shelves[linked] = (shelves[linked][0]+1, shelves[linked][1])
                    linked = -1
                    # si il ne reste rien à aller chercher
                    if cluster_restant == [] and waitingshelves(shelves, workers, robots, i) == []:
                        index_closer, _ = findclosest((posx, posy), depot, robot_seul_obst)
                        delete_bot.append(i)
                    else:
                        index_closer = (posx, posy)

                # si arrivée à un carton
                elif (posx, posy) in colle(strat_sur_couloir(strategie[linked])):
                    strategie_couloir = strat_sur_couloir(strategie[linked])
                    # si ce n'est pas le dernier
                    num = trouve((posx, posy), worker_zone)
                    if connected[linked]:    # si l'operateur est sur la même case
                        connected[linked] = 0
                        indice = trouve((posx, posy), strategie_couloir)

                        while indice != -1:        # récupère le colis si il est à droite
                            id_colis = strategie_couloir[indice].index((posx, posy))
                            (real_posx,real_posy) = strategie[linked][indice].pop(id_colis)
                            strategie_couloir[indice].pop(id_colis)
                            tab_carton[real_posx][real_posy] = 0
                            if indice >= 4:
                                print("erreur robot plein")
                            else:
                                shelves[linked][2][indice] += 1
                            indice = trouve((posx, posy), strategie_couloir)
                            #tab[indice] += 1
              

                        # si le dernier article de la commande vient d'être chargé donc vide
                        if liste_vide(strategie_couloir):
                            index_closer, _ = findclosest((posx, posy), depot, robot_etagere_obst)
                            if index_closer == (posx,posy):
                                if strategie2 == True:
                                    linked = -1
                        else:                           # va chercher article suivant
                            index_closer, _ = findclosest((posx, posy), colle(strategie_couloir), robot_etagere_obst)
                            if index_closer == (posx,posy):
                                if strategie2 == True:
                                    linked = -1
                            else:
                                """
                                xcarton, ycarton = index_closer
                                tab_carton[xcarton][ycarton] = - \
                                    tab_carton[xcarton][ycarton]
                                if xcarton % 3 == 0:
                                    index_closer = (xcarton+1, ycarton)
                                    request_worker((xcarton+1, ycarton))
                                elif xcarton % 3 == 2:
                                    index_closer = (xcarton-1, ycarton)
                                    request_worker((xcarton-1, ycarton))
                                else:
                                    print("error bad box placement")
                                    indice = trouve((xcarton, ycarton), strategie[linked])
                                    if indice != -1:
                                        strategie[linked][indice].pop(strategie[linked][indice].index((xcarton, ycarton)))
                                    else:
                                        print("phantom error")
                                        print((xcarton, ycarton),strategie[linked])
                                    index_closer = (posx,posy)
                                destination_shelves[linked] = index_closer
                                """
                                unrequest_worker(destination_shelves[linked])
                                request_worker(index_closer)
                                destination_shelves[linked] = index_closer
                        index_closer = (posx, posy)
                    else:
                        index_closer = (posx,posy)
                        unrequest_worker(destination_shelves[linked])
                        destination_shelves[linked] = index_closer
                        request_worker(index_closer)
                        
                        # stratégie de détachement si opérateur trop loin
                        if strategie1 == True:
                            possible_shelves = waitingshelves(shelves, operateurs, robots, i)
                            index_closer_shelf, _ = findclosest((posx, posy), possible_shelves, robot_seul_obst)
                            dist_to_shelf = distance((posx, posy),index_closer_shelf)
                            id_operateur = trouve((posx,posy),worker_zone)
                            dist_to_operateur = distance((posx,posy),(workers[id_operateur][0],workers[id_operateur][1]))
                            if dist_to_shelf < dist_to_operateur:
                                linked = -1
                                index_closer = (posx, posy)
                        
                else:
                    if shelves[linked][2] == [0, 0, 0, 0] and liste_vide(strategie[linked]):
                        if cluster_restant != []:
                            new_cluster = cluster_restant.pop(0)
                            strategie[linked] = new_cluster
                            strategie_couloir = strat_sur_couloir(strategie[linked])
                            index_closer, _ = findclosest((posx, posy), colle(strategie_couloir), robot_etagere_obst)
                            if index_closer == (posx,posy):
                                if strategie2 == True:
                                    linked = -1
                            else:
                                """
                                xcarton, ycarton = index_closer
                                tab_carton[xcarton][ycarton] = - \
                                    tab_carton[xcarton][ycarton]
                                if xcarton % 3 == 0:      # si carton sur la droite
                                    index_closer = (xcarton+1, ycarton)
                                    request_worker((xcarton+1, ycarton))
                                elif xcarton % 3 == 2:
                                    index_closer = (xcarton-1, ycarton)
                                    request_worker((xcarton-1, ycarton))
                                else:
                                    print("error bad box placement")
                                    indice = trouve((xcarton, ycarton), strategie[linked])
                                    if indice != -1:
                                        strategie[linked][indice].pop(strategie[linked][indice].index((xcarton, ycarton)))
                                    index_closer = (posx,posy)
                                destination_shelves[linked] = index_closer
                                """
                                unrequest_worker(destination_shelves[linked])
                                request_worker(index_closer)
                                destination_shelves[linked] = index_closer
                        else:
                            index_closer, _ = findclosest((posx, posy), depot, robot_seul_obst)
                            delete_bot.append(i)
                            linked = -1
                    # si le dernier article de la commande vient d'être chargé donc vide
                    elif liste_vide(strategie[linked]):
                        index_closer, _ = findclosest((posx, posy), depot, robot_etagere_obst)
                        destination_shelves[linked] = index_closer
                        if index_closer == (posx,posy):
                            if strategie2 == True:
                                linked = -1
                    else:
                        strategie_couloir = strat_sur_couloir(strategie[linked])
                        index_closer, _ = findclosest((posx, posy), colle(strategie_couloir), robot_etagere_obst)
                        if index_closer == (posx,posy):
                            if strategie2 == True:
                                linked = -1
                        else:
                            """
                            xcarton, ycarton = index_closer
                            tab_carton[xcarton][ycarton] = - \
                                tab_carton[xcarton][ycarton]
                            if xcarton % 3 == 0:
                                index_closer = (xcarton+1, ycarton)
                                request_worker((xcarton+1, ycarton))
                            elif xcarton % 3 == 2:
                                index_closer = (xcarton-1, ycarton)
                                request_worker((xcarton-1, ycarton))
                            else:
                                print("error bad box placement")
                                indice = trouve((xcarton, ycarton), strategie[linked])
                                if indice != -1:
                                    strategie[linked][indice].pop(strategie[linked][indice].index((xcarton, ycarton)))
                                else:
                                    print("phantom error")
                                    print((xcarton, ycarton),strategie[linked])
                                index_closer = (posx,posy)
                            destination_shelves[linked] = index_closer
                            """
                            unrequest_worker(destination_shelves[linked])
                            request_worker(index_closer)
                            destination_shelves[linked] = index_closer

            else:
                if shelves[linked][2] == [0, 0, 0, 0] and liste_vide(strategie[linked]):
                    if cluster_restant != []:
                        new_cluster = cluster_restant.pop(0)
                        strategie[linked] = new_cluster
                        strategie_couloir = strat_sur_couloir(strategie[linked])
                        index_closer, _ = findclosest((posx, posy), colle(strategie_couloir), robot_etagere_obst)
                        if index_closer == (posx,posy):
                            if strategie2 == True:
                                linked = -1
                        else:
                            unrequest_worker(destination_shelves[linked])
                            request_worker(index_closer)
                            destination_shelves[linked] = index_closer
                    else:
                        index_closer, _ = findclosest(
                            (posx, posy), depot, robot_seul_obst)
                        delete_bot.append(i)
                        linked = -1
                    # si le dernier article de la commande vient d'être chargé donc vide
                elif liste_vide(strategie[linked]):
                    index_closer, _ = findclosest((posx, posy), depot, robot_etagere_obst)
                    destination_shelves[linked] = index_closer
                    if index_closer == (posx,posy):
                        if strategie2 == True:
                            linked = -1
                else:
                    strategie_couloir = strat_sur_couloir(strategie[linked])
                    index_closer, _ = findclosest((posx, posy), colle(strategie_couloir), robot_etagere_obst)
                    if index_closer == (posx,posy):
                        if strategie2 == True:
                            linked = -1
                    else:
                        unrequest_worker(destination_shelves[linked])
                        request_worker(index_closer)
                        destination_shelves[linked] = index_closer
        else:
            possible_shelves = waitingshelves(shelves, operateurs, robots, i)
            index_closer, _ = findclosest(
                (posx, posy), possible_shelves, robot_seul_obst)
            destination_robots[i] = index_closer
            if (posx, posy) == destination_robots[i]:
                index_closer = (posx, posy)
                linked = findindice(shelves, (posx, posy))

        if linked != -1:
            newposx, newposy = nextstep(
                (posx, posy), index_closer, robot_etagere_obst)
            if i == 5:              #test de pos
                display_obst_on_screen = (1,1)
            if newposx > posx:
                tab_lab[newposx][newposy] = 4
            elif newposx < posx:
                tab_lab[newposx][newposy] = 3
            elif newposy > posy:
                tab_lab[newposx][newposy] = 1
            elif newposy < posy:
                tab_lab[newposx][newposy] = 2
            else:
                tab_lab[newposx][newposy] = 5
                if i == 5:          #test de pos
                    display_obst_on_screen = (newposx,newposy)

            if (newposx % 3 == 2 or newposx % 3 == 0) and newposy % 6 != 1 and newposy != len(tab_lab[0])-2:
                print(robots[i])
                
                print(shelves[robots[i][2]])
                print(destination_shelves[robots[i][2]])
                newposx = posx
                newposy = posy
            new_robots[i] = (newposx, newposy, linked)
            case_occupée.append((newposx, newposy))
            shelves[linked] = (newposx, newposy, shelves[linked][2])
            #print(newposx, newposy,destination_shelves[linked])

        else:
            newposx, newposy = nextstep(
                (posx, posy), index_closer, robot_seul_obst)
            if newposx > posx:
                tab_lab[newposx][newposy] = 4
            elif newposx < posx:
                tab_lab[newposx][newposy] = 3
            elif newposy > posy:
                tab_lab[newposx][newposy] = 1
            elif newposy < posy:
                tab_lab[newposx][newposy] = 2
            else:
                tab_lab[newposx][newposy] = 5
            new_robots[i] = (newposx, newposy, linked)
            case_occupée.append((newposx, newposy))
        distance_to_destination_robots[i] = distance(index_closer, (posx, posy))
    k = 0
    clearlonlyshelves()
    for i in liste_enumerate:
        destination_robots[i] = (robots[i][0], robots[i][1])

    for num in sorted(delete_bot):
        new_robots.pop(num-k)
        distance_to_destination_robots.pop(num-k)
        destination_robots.pop(num-k)
        k = k+1

    for (x, y) in case_occupée:
        tab_lab[x][y] = 0
    return new_robots

def move_robotsV3(bots, operateurs, shelves):  # Deplace tous les robots
    global tab_lab,display_obst_on_screen
    new_robots = [() for _ in range(len(robots))]
    new_shelves = []
    delete_bot = []
    lonlyshelves(shelves, bots)
    def step1(i):
        stuck = 0
        posx, posy, linked = bots[i]
        newposx, newposy = posx, posy
        if linked != -1:
            # si arrivé à destination
            if (posx, posy) == destination_shelves[linked] and ((posx, posy) in depot or (posx, posy) in colle(strat_sur_couloir(strategie[linked]))):
                if (posx, posy) in depot:       # si sur un depot
                    shelves[linked] = (shelves[linked][0]+1,
                                       shelves[linked][1], [0, 0, 0, 0])
                    destination_shelves[linked] = (
                        shelves[linked][0]+1, shelves[linked][1])
                    linked = -1
                    # si il ne reste rien à aller chercher
                    if cluster_restant == [] and waitingshelves(shelves, workers, robots, i) == []:
                        index_closer, _ = findclosest((posx, posy), depot, robot_seul_obst)
                        delete_bot.append(i)
                    else:
                        index_closer = (posx, posy)

                # si arrivée à un carton
                elif (posx, posy) in colle(strat_sur_couloir(strategie[linked])):
                    strategie_couloir = strat_sur_couloir(strategie[linked])
                    # si ce n'est pas le dernier
                    num = trouve((posx, posy), worker_zone)
                    if connected[linked]:    # si l'operateur est sur la même case
                        connected[linked] = 0
                        indice = trouve((posx, posy), strategie_couloir)

                        while indice != -1:        # récupère le colis si il est à droite
                            id_colis = strategie_couloir[indice].index((posx, posy))
                            (real_posx,real_posy) = strategie[linked][indice].pop(id_colis)
                            strategie_couloir[indice].pop(id_colis)
                            tab_carton[real_posx][real_posy] = 0
                            if indice >= 4:
                                print("erreur robot plein")
                            else:
                                shelves[linked][2][indice] += 1
                            indice = trouve((posx, posy), strategie_couloir)
                            #tab[indice] += 1
              
                        index_closer = (posx, posy)
                    else:
                        index_closer = (posx,posy)
                        unrequest_worker(destination_shelves[linked])
                        destination_shelves[linked] = index_closer
                        request_worker(index_closer)
                        
                        # stratégie de détachement si opérateur trop loin
                        if strategie1 == True:
                            possible_shelves = waitingshelves(shelves, operateurs, robots, i)
                            index_closer_shelf, _ = findclosest((posx, posy), possible_shelves, robot_seul_obst)
                            dist_to_shelf = distance((posx, posy),index_closer_shelf)
                            id_operateur = trouve((posx,posy),worker_zone)
                            dist_to_operateur = distance((posx,posy),(workers[id_operateur][0],workers[id_operateur][1]))
                            if dist_to_shelf < dist_to_operateur:
                                linked = -1
                                index_closer = (posx, posy)

            else:
                if shelves[linked][2] == [0, 0, 0, 0] and liste_vide(strategie[linked]):
                    if cluster_restant != []:
                        new_cluster = cluster_restant.pop(0)
                        strategie[linked] = new_cluster
                        strategie_couloir = strat_sur_couloir(strategie[linked])
                        index_closer, _ = findclosest((posx, posy), colle(strategie_couloir), robot_etagere_obst)
                        if index_closer == (posx,posy):
                            if strategie4:
                                perfect_index_closer, (perfect_newposx, perfect_newposy) = findclosest((posx, posy), colle(strategie_couloir), worker_obst)
                                if tab_lab[perfect_newposx][perfect_newposy] == 0:
                                    newposx,newposy = (perfect_newposx, perfect_newposy)
                                    index_closer = perfect_index_closer
                                else:
                                    stuck_list.append(i)
                                    stuck = 1
                                    if strategie2:
                                        linked = -1
                            else:
                                stuck_list.append(i)
                                stuck = 1
                                if strategie2:
                                    linked = -1
                        else:
                            unrequest_worker(destination_shelves[linked])
                            request_worker(index_closer)
                            destination_shelves[linked] = index_closer
                    else:
                        index_closer, _ = findclosest(
                            (posx, posy), depot, robot_seul_obst)
                        delete_bot.append(i)
                        linked = -1
                    # si le dernier article de la commande vient d'être chargé donc vide
                elif liste_vide(strategie[linked]):
                    index_closer, _ = findclosest((posx, posy), depot, robot_etagere_obst)
                    destination_shelves[linked] = index_closer
                    if index_closer == (posx,posy):
                        if strategie4:
                            perfect_index_closer, (perfect_newposx, perfect_newposy) = findclosest((posx, posy), depot, worker_obst)
                            if tab_lab[perfect_newposx][perfect_newposy] == 0:
                                newposx,newposy = (perfect_newposx, perfect_newposy)
                                index_closer = perfect_index_closer
                            else:
                                stuck_list.append(i)
                                stuck = 1
                                if strategie2:
                                    linked = -1
                        else:
                            stuck_list.append(i)
                            stuck = 1
                            if strategie2:
                                linked = -1
                            
                else:
                    strategie_couloir = strat_sur_couloir(strategie[linked])
                    index_closer, _ = findclosest((posx, posy), colle(strategie_couloir), robot_etagere_obst)
                    if index_closer == (posx,posy):
                        if strategie4:
                            perfect_index_closer, (perfect_newposx, perfect_newposy) = findclosest((posx, posy), colle(strategie_couloir), worker_obst)
                            if tab_lab[perfect_newposx][perfect_newposy] == 0:
                                newposx,newposy = (perfect_newposx, perfect_newposy)
                                index_closer = perfect_index_closer
                            else:
                                stuck_list.append(i)
                                stuck = 1
                                if strategie2:
                                    linked = -1
                        else:
                            stuck_list.append(i)
                            stuck = 1
                            if strategie2:
                                linked = -1

                    else:
                        unrequest_worker(destination_shelves[linked])
                        request_worker(index_closer)
                        destination_shelves[linked] = index_closer
        else:
            possible_shelves = waitingshelves(shelves, operateurs, robots, i)
            if possible_shelves != []:
                index_closer, _ = findclosest(
                    (posx, posy), possible_shelves, robot_seul_obst)
                destination_robots[i] = index_closer
                if (posx, posy) == destination_robots[i]:
                    index_closer = (posx, posy)
                    linked = findindice(shelves, (posx, posy))
            else:
                index_closer = (posx, posy)

        if linked != -1:
            newposx, newposy = nextstep(
                (posx, posy), index_closer, robot_etagere_obst)
            if not stuck:
                if newposx > posx:
                    tab_lab[newposx][newposy] = 4
                elif newposx < posx:
                    tab_lab[newposx][newposy] = 3
                elif newposy > posy:
                    tab_lab[newposx][newposy] = 1
                elif newposy < posy:
                    tab_lab[newposx][newposy] = 2
                else:
                    tab_lab[newposx][newposy] = 5


            new_robots[i] = (newposx, newposy, linked)
            shelves[linked] = (newposx, newposy, shelves[linked][2])
            #print(newposx, newposy,destination_shelves[linked])

        else:
            newposx, newposy = nextstep(
                (posx, posy), index_closer, robot_seul_obst)
            if not stuck:
                if newposx > posx:
                    tab_lab[newposx][newposy] = 4
                elif newposx < posx:
                    tab_lab[newposx][newposy] = 3
                elif newposy > posy:
                    tab_lab[newposx][newposy] = 1
                elif newposy < posy:
                    tab_lab[newposx][newposy] = 2
                else:
                    tab_lab[newposx][newposy] = 5
            new_robots[i] = (newposx, newposy, linked)
        distance_to_destination_robots[i] = distance(index_closer, (posx, posy))
    
    stuck_list = []
    liste_enumerate = enumerate_in_order(distance_to_destination_robots)
    k = 0
    for i in liste_enumerate:
        step1(i)

    while stuck_list != []:
        i = stuck_list.pop()
        x,y = robots[i][0],robots[i][1]
        if tab_lab[x][y] != 0:
            if tab_lab[x][y] == 4:
                robot_id = findindice(robots,(x-1,y))
                tab_lab[x][y] = 5
                step1(robot_id)
            elif tab_lab[x][y] == 3:
                robot_id = findindice(robots,(x+1,y))
                tab_lab[x][y] = 5
                step1(robot_id)
            elif tab_lab[x][y] == 2:
                robot_id = findindice(robots,(x,y+1))
                tab_lab[x][y] = 5
                step1(robot_id)
            elif tab_lab[x][y] == 1:
                robot_id = findindice(robots,(x,y-1))
                tab_lab[x][y] = 5
                step1(robot_id)
    display_obst_on_screen = []
    """ uniquement pour l'affichage de cases interessantes, pour debugguer // ici affichage des cases bloquantes
    for i in range(len(tab_lab)):
        for j in range(len(tab_lab[0])):
            if tab_lab[i][j] == 5:
                display_obst_on_screen.append((i,j))
    """
    clearboard()
    clearlonlyshelves()

    for i in liste_enumerate:
        destination_robots[i] = (robots[i][0], robots[i][1])

    for num in sorted(delete_bot):
        new_robots.pop(num-k)
        distance_to_destination_robots.pop(num-k)
        destination_robots.pop(num-k)
        k = k+1

    
    return new_robots


def step1(i,bots,operateurs):
    global destination_robots
    disappear = 0
    stuck = 0
    posx, posy, linked = bots[i]
    newposx, newposy = posx, posy
    if linked != -1:
        # si arrivé à destination
        if (posx, posy) == destination_shelves[linked] and ((posx, posy) in depot or (posx, posy) in colle(strat_sur_couloir(strategie[linked]))):
            index_closer = (posx, posy)
            (newposx, newposy) = (posx,posy)
            if (posx, posy) in depot:
                disappear = 1
            
        #sinon
        else:
            if shelves[linked][2] == [0, 0, 0, 0] and liste_vide(strategie[linked]):
                index_closer = (posx,posy)
                (newposx, newposy) = (posx,posy)
                disappear = 1
                # si le dernier article de la commande vient d'être chargé donc vide
            elif liste_vide(strategie[linked]):
                index_closer, (newposx, newposy) = findclosest((posx, posy), depot, robot_etagere_obst)
                if index_closer == (posx,posy):
                    if strategie4:
                        perfect_index_closer, (perfect_newposx, perfect_newposy) = findclosest((posx, posy), depot, worker_obst)
                        if (perfect_newposx, perfect_newposy) == (posx,posy):
                            stuck = 1
                        elif tab_lab[perfect_newposx][perfect_newposy] != 5 and tab_lab[perfect_newposx][perfect_newposy] != -2:
                            newposx,newposy = (perfect_newposx, perfect_newposy)
                            index_closer = perfect_index_closer
                            #print("nice",(posx,posy),(newposx,newposy),perfect_index_closer)
                        else:
                            stuck = 1
                    else:
                        stuck = 1
            else:
                strategie_couloir = strat_sur_couloir(strategie[linked])
                index_closer, (newposx, newposy) = findclosest((posx, posy), colle(strategie_couloir), robot_etagere_obst)
                if index_closer == (posx,posy):
                    if strategie4:
                        perfect_index_closer, (perfect_newposx, perfect_newposy) = findclosest((posx, posy), colle(strategie_couloir), worker_obst)
                        if (perfect_newposx, perfect_newposy) == (posx,posy):
                            stuck = 1
                        elif tab_lab[perfect_newposx][perfect_newposy] != 5 and tab_lab[perfect_newposx][perfect_newposy] != -2:
                            newposx,newposy = (perfect_newposx, perfect_newposy)
                            index_closer = perfect_index_closer
                            #print("nice",(posx,posy),(newposx,newposy),perfect_index_closer)
                        else:
                            stuck = 1
                    else:
                        stuck = 1
    else:
        possible_shelves = waitingshelves(shelves, operateurs, robots, i)
        index_closer, (newposx, newposy) = findclosest((posx, posy), possible_shelves, robot_seul_obst)

    
    return disappear,stuck,(newposx,newposy)


def move_robotsV5(bots, operateurs, shelves):  # Deplace tous les robots
    global tab_lab,display_obst_on_screen
    new_robots = [() for _ in range(len(robots))]
    new_shelves = []
    case_occupée = []
    delete_bot = []
    
    lonlyshelves(shelves, bots)
    stuck_list = []
    
    liste_enumerate = enumerate_in_order(distance_to_destination_robots)
    for i in liste_enumerate:
        posx,posy,_ = bots[i]
        disappear,stuck,(newposx,newposy) = step1(i,bots,operateurs)
        if not disappear and not stuck:
            if newposx > posx:
                tab_lab[newposx][newposy] = 4
            elif newposx < posx:
                tab_lab[newposx][newposy] = 3
            elif newposy > posy:
                tab_lab[newposx][newposy] = 1
            elif newposy < posy:
                tab_lab[newposx][newposy] = 2
            else:
                tab_lab[newposx][newposy] = 5
        if stuck:
            stuck_list.append(i)
    

    # step 1.5
    while stuck_list != []:
        i = stuck_list.pop()
        x,y = robots[i][0],robots[i][1]
        if tab_lab[x][y] != 0:
            if tab_lab[x][y] == 4:
                robot_id = findindice(robots,(x-1,y))
            elif tab_lab[x][y] == 3:
                robot_id = findindice(robots,(x+1,y))
            elif tab_lab[x][y] == 2:
                robot_id = findindice(robots,(x,y+1))
            elif tab_lab[x][y] == 1:
                robot_id = findindice(robots,(x,y-1))
            if tab_lab[x][y] != 5:
                tab_lab[x][y] = 5
                disappear,stuck,(newposx,newposy) = step1(robot_id,bots,operateurs)
                posx,posy,_ = bots[robot_id]
                if not disappear and not stuck:
                    if newposx > posx:
                        tab_lab[newposx][newposy] = 4
                    elif newposx < posx:
                        tab_lab[newposx][newposy] = 3
                    elif newposy > posy:
                        tab_lab[newposx][newposy] = 1
                    elif newposy < posy:
                        tab_lab[newposx][newposy] = 2
                    else:
                        tab_lab[newposx][newposy] = 5
                if stuck:
                    stuck_list.append(robot_id)
        tab_lab[x][y] = 5

    display_obst_on_screen = []
    for i in range(len(tab_lab)):
        for j in range(len(tab_lab[0])):
            if tab_lab[i][j] == 5:
                display_obst_on_screen.append((i,j))
    
    def step2(i):
        posx, posy, linked = bots[i]
        newposx, newposy = posx, posy
        if linked != -1:
            # si arrivé à destination
            if (posx, posy) == destination_shelves[linked] and ((posx, posy) in depot or (posx, posy) in colle(strat_sur_couloir(strategie[linked]))):
                if (posx, posy) in depot:       # si sur un depot
                    shelves[linked] = (shelves[linked][0]+1,shelves[linked][1], [0, 0, 0, 0])
                    destination_shelves[linked] = (shelves[linked][0]+1, shelves[linked][1])
                    linked = -1
                    # si il ne reste rien à aller chercher
                    if cluster_restant == [] and waitingshelves(shelves, workers, robots, i) == []:
                        index_closer, _ = findclosest((posx, posy), depot, robot_seul_obst)
                        newposx,newposy = posx,posy
                        delete_bot.append(i)
                    else:
                        index_closer = (posx, posy)
                        newposx,newposy = posx,posy

                # si arrivée à un carton
                elif (posx, posy) in colle(strat_sur_couloir(strategie[linked])):
                    strategie_couloir = strat_sur_couloir(strategie[linked])
                    # si ce n'est pas le dernier
                    num = trouve((posx, posy), worker_zone)
                    index_closer = (posx,posy)
                    newposx,newposy = posx,posy
                    '''
                    if connected[linked]:    # si l'operateur est sur la même case
                        connected[linked] = 0
                        indice = trouve((posx, posy), strategie_couloir)
                        while indice != -1:        # récupère le colis si il est à droite
                            id_colis = strategie_couloir[indice].index((posx, posy))
                            (real_posx,real_posy) = strategie[linked][indice].pop(id_colis)
                            strategie_couloir[indice].pop(id_colis)
                            tab_carton[real_posx][real_posy] = 0
                            if indice >= 4:
                                print("erreur robot plein")
                            else:
                                shelves[linked][2][indice] += 1
                            indice = trouve((posx, posy), strategie_couloir)
                            #tab[indice] += 1
              
                    else:
                    '''
                    destination_shelves[linked] = index_closer
                    request_worker(index_closer)
                    
                    # stratégie de détachement si opérateur trop loin
                    if strategie1 == True:
                        possible_shelves = waitingshelves(shelves, operateurs, robots, i)
                        index_closer_shelf, _ = findclosest((posx, posy), possible_shelves, robot_seul_obst)
                        dist_to_shelf = distance((posx, posy),index_closer_shelf)
                        id_operateur = trouve((posx,posy),worker_zone)
                        dist_to_operateur = distance((posx,posy),(workers[id_operateur][0],workers[id_operateur][1]))
                        if dist_to_shelf < dist_to_operateur:
                            linked = -1

            else:
                if shelves[linked][2] == [0, 0, 0, 0] and liste_vide(strategie[linked]):
                    if cluster_restant != []:
                        new_cluster = cluster_restant.pop(0)
                        strategie[linked] = new_cluster
                        strategie_couloir = strat_sur_couloir(strategie[linked])
                        index_closer, (newposx,newposy) = findclosest((posx, posy), colle(strategie_couloir), robot_etagere_obst)
                        destination_shelves[linked] = index_closer
                        if index_closer == (posx,posy):
                            if strategie4:
                                perfect_index_closer, (perfect_newposx, perfect_newposy) = findclosest((posx, posy), colle(strategie_couloir), worker_obst)
                                if (perfect_newposx, perfect_newposy) != (posx,posy) and tab_lab[perfect_newposx][perfect_newposy] != 5 and tab_lab[perfect_newposx][perfect_newposy] != -2:
                                    newposx,newposy = (perfect_newposx, perfect_newposy)
                                    index_closer = perfect_index_closer
                                elif strategie2:
                                    linked = -1
                            elif strategie2:
                                linked = -1
                        else:
                            request_worker(index_closer)
                            destination_shelves[linked] = index_closer
                    else:
                        index_closer, (newposx,newposy) = findclosest((posx, posy), depot, robot_seul_obst)
                        delete_bot.append(i)
                        linked = -1
                    # si le dernier article de la commande vient d'être chargé donc vide
                elif liste_vide(strategie[linked]):
                    index_closer, (newposx,newposy) = findclosest((posx, posy), depot, robot_etagere_obst)
                    destination_shelves[linked] = index_closer
                    if index_closer == (posx,posy):
                        if strategie4:
                            perfect_index_closer, (perfect_newposx, perfect_newposy) = findclosest((posx, posy), depot, worker_obst)
                            if (perfect_newposx, perfect_newposy) != (posx,posy) and tab_lab[perfect_newposx][perfect_newposy] != 5 and tab_lab[perfect_newposx][perfect_newposy] != -2:
                                newposx,newposy = (perfect_newposx, perfect_newposy)
                                index_closer = perfect_index_closer
                            elif strategie2:
                                linked = -1
                        elif strategie2:
                            linked = -1
                    else:
                        destination_shelves[linked] = index_closer
                else:
                    strategie_couloir = strat_sur_couloir(strategie[linked])
                    index_closer, (newposx,newposy) = findclosest((posx, posy), colle(strategie_couloir), robot_etagere_obst)
                    destination_shelves[linked] = index_closer
                    if index_closer == (posx,posy):
                        if strategie4:
                            perfect_index_closer, (perfect_newposx, perfect_newposy) = findclosest((posx, posy), colle(strategie_couloir), worker_obst)
                            if (perfect_newposx, perfect_newposy) != (posx,posy) and tab_lab[perfect_newposx][perfect_newposy] != 5 and tab_lab[perfect_newposx][perfect_newposy] != -2:
                                newposx,newposy = (perfect_newposx, perfect_newposy)
                                index_closer = perfect_index_closer
                            elif strategie2:
                                linked = -1
                        elif strategie2:
                            linked = -1

                    else:
                        request_worker(index_closer)
                        destination_shelves[linked] = index_closer
        else:
            possible_shelves = waitingshelves(shelves, operateurs, robots, i)
            index_closer, (newposx,newposy) = findclosest((posx, posy), possible_shelves, robot_seul_obst)
            destination_robots[i] = index_closer
            if (posx, posy) == destination_robots[i]:
                index_closer = (posx, posy)
                linked = findindice(shelves, (posx, posy))
                if linked == -1:
                    if cluster_restant == [] and waitingshelves(shelves, workers, robots, i) == []:
                        index_closer, (newposx,newposy) = findclosest((posx, posy), depot, robot_seul_obst)
                        if (posx, posy) in depot:
                            newposx,newposy = posx,posy
                            delete_bot.append(i)
                    elif strategie4:
                        perfect_index_closer, (perfect_newposx, perfect_newposy) = findclosest((posx, posy), possible_shelves, worker_obst)
                        if (perfect_newposx, perfect_newposy) != (posx,posy) and tab_lab[perfect_newposx][perfect_newposy] != 5:
                            newposx,newposy = (perfect_newposx, perfect_newposy)
                            index_closer = perfect_index_closer


        if linked != -1:
            #newposx, newposy = nextstep((posx, posy), index_closer, robot_etagere_obst)
            if newposx > posx:
                tab_lab[newposx][newposy] = 4
            elif newposx < posx:
                tab_lab[newposx][newposy] = 3
            elif newposy > posy:
                tab_lab[newposx][newposy] = 1
            elif newposy < posy:
                tab_lab[newposx][newposy] = 2
            else:
                tab_lab[newposx][newposy] = 5


            new_robots[i] = (newposx, newposy, linked)
            case_occupée.append((newposx, newposy))
            shelves[linked] = (newposx, newposy, shelves[linked][2])
            #print(newposx, newposy,destination_shelves[linked])

        else:
            #newposx, newposy = nextstep((posx, posy), index_closer, robot_seul_obst)
            if newposx > posx:
                tab_lab[newposx][newposy] = 4
            elif newposx < posx:
                tab_lab[newposx][newposy] = 3
            elif newposy > posy:
                tab_lab[newposx][newposy] = 1
            elif newposy < posy:
                tab_lab[newposx][newposy] = 2
            else:
                tab_lab[newposx][newposy] = 5
            new_robots[i] = (newposx, newposy, linked)
            case_occupée.append((newposx, newposy))
        distance_to_destination_robots[i] = distance(index_closer, (posx, posy))


    liste_enumerate = enumerate_in_order(distance_to_destination_robots)
    for i in liste_enumerate:
        step2(i)

    clearboard()
    clearlonlyshelves()
    for i in liste_enumerate:
        destination_robots[i] = (robots[i][0], robots[i][1])
    k = 0
    for num in sorted(delete_bot):
        new_robots.pop(num-k)
        distance_to_destination_robots.pop(num-k)
        destination_robots.pop(num-k)
        k = k+1

        for (x, y) in case_occupée:
            tab_lab[x][y] = 0
    return new_robots

def move_workers(operateur):
    global tab_lab, requests, shelves
    new_workers = []
    for i in range(len(operateur)):
        posx, posy, requests = operateur[i]
        newposx, newposy = posx, posy
        if requests != []:
            plus_proche = (posx, posy)
            min_dist = 1000000
            for (casex, casey) in requests:
                if (casex, casey) in destination_shelves:
                    num_shelf = destination_shelves.index((casex, casey))
                    dist_case_shelf = distance(
                        (casex, casey), (shelves[num_shelf][0], shelves[num_shelf][1]))
                    dist_case_operateur = distance((posx, posy), (casex, casey))
                    if min_dist > max(dist_case_shelf, dist_case_operateur):
                        plus_proche = (casex, casey)
                        min_dist = max(dist_case_shelf, dist_case_operateur)
                        if min_dist == 0:
                            connected[num_shelf] = 1
                            requests.pop(requests.index((posx, posy)))
                            break
                else:
                    print("error badrequest")
                    """
                    print((casex,casey))
                    rid = findindice(robots,(casex,casey))
                    print(rid)
                    print(robots[rid])
                    print(shelves[robots[rid][2]])
                    print(destination_shelves[robots[rid][2]])
                    """
                    requests.pop(requests.index((casex, casey)))
            if min_dist != 0 and (posx, posy) != plus_proche:
                (newposx, newposy) = nextstep(
                    (posx, posy), plus_proche, worker_obst)
        new_workers.append((newposx, newposy, requests))
    return new_workers

def move_workersV2(operateur):
    global tab_lab, requests, shelves
    new_workers = []
    for i in range(len(operateur)):
        posx, posy, requests = operateur[i]
        newposx, newposy = posx, posy
        if requests != []:
            plus_proche = (posx, posy)
            min_dist = 1000000
            for (casex, casey) in requests:
                if (casex, casey) in destination_shelves:
                    num_shelf = destination_shelves.index((casex, casey))
                    dist_case_shelf = distance(
                        (casex, casey), (shelves[num_shelf][0], shelves[num_shelf][1]))
                    dist_case_operateur = distance((posx, posy), (casex, casey))
                    if min_dist > max(dist_case_shelf, dist_case_operateur):
                        plus_proche = (casex, casey)
                        min_dist = max(dist_case_shelf, dist_case_operateur)
                        if min_dist == 0:
                            strategie_couloir = strat_sur_couloir(strategie[num_shelf])
                            indice = trouve((posx, posy), strategie_couloir)
                            #if indice == -1:
                            #    print((posx, posy),destination_shelves[i])
                            while indice != -1:        # récupère le colis si il est à droite
                                id_colis = strategie_couloir[indice].index((posx, posy))
                                (real_posx,real_posy) = strategie[num_shelf][indice].pop(id_colis)
                                strategie_couloir[indice].pop(id_colis)
                                tab_carton[real_posx][real_posy] = 0
                                if indice >= 4:
                                    print("erreur robot plein")
                                else:
                                    shelves[num_shelf][2][indice] += 1
                                indice = trouve((posx, posy), strategie_couloir)
                            requests.pop(requests.index((posx, posy)))
                            break
                else:
                    #print("error badrequest")
                    """
                    print((casex,casey))
                    rid = findindice(robots,(casex,casey))
                    print(rid)
                    print(robots[rid])
                    print(shelves[robots[rid][2]])
                    print(destination_shelves[robots[rid][2]])
                    """
                    requests.pop(requests.index((casex, casey)))
            if min_dist != 0 and (posx, posy) != plus_proche:
                (newposx, newposy) = nextstep(
                    (posx, posy), plus_proche, worker_obst)
        new_workers.append((newposx, newposy, requests))
    return new_workers

# affichage de tous les éléments
def afficher_labyrinthe(screen, background_color, screen_size):
    global pos_obstacles, robots, workers, shelves
    (screen_width, screen_heigth) = screen_size
    pygame.display.set_caption("Labyrinthe")
    screen.fill(background_color)
    redSquare = pygame.image.load("images/case-rouge.png")
    redSquare = pygame.transform.smoothscale(redSquare, (c*10, c*10))
    for x, y in depot:
        screen.blit(redSquare, (x*c*10, y*c*10))
    robot_img = pygame.image.load("images/robot-icon.png")
    robot_img = pygame.transform.smoothscale(robot_img, (c*10, c*10))
    worker_img = pygame.image.load("images/icon-ouvrier.png")
    worker_img = pygame.transform.smoothscale(worker_img, (c*10, c*10))
    shelf_img = pygame.image.load("images/shelf.png")
    shelf_img = pygame.transform.smoothscale(shelf_img, (c*10, c*10))
    # screen.blit(worker_img, ((nbtuileslong-1)*c*10, (nbtuileshaut-1)*c*10))
    # image pour les obstacles
    obstacle = pygame.image.load("images/obstacle_base.png")
    for (xdeb, ydeb, xfin, yfin) in pos_obstacles:  # on ennumère la liste des obstacles
        new_obstacle = pygame.transform.smoothscale(
            obstacle, (xfin - xdeb, yfin - ydeb))  # affichage smooth
        screen.blit(new_obstacle, (xdeb, ydeb))
    color = [(204, 232, 219), (190, 180, 214), (193, 212, 227),
             (248, 179, 202), (204, 151, 193), (250, 218, 226)]
    for num, zone in enumerate(pos_worker_zone):
        coloredSurface = redSquare.copy()
        coloredSurface.fill(color[num])
        for (xdeb, ydeb, xfin, yfin) in zone:  # on ennumère la liste des obstacles
            new_zone = pygame.transform.smoothscale(
                coloredSurface, (xfin - xdeb, yfin - ydeb))  # affichage smooth
            screen.blit(coloredSurface, (xdeb, ydeb))
    for i in range(len(tab_carton)):
        for j in range(len(tab_carton[0])):
            if tab_carton[i][j] != 0:
                strnum = str(abs(tab_carton[i][j]))
                textsurface = myfont.render(
                    (3-len(strnum))*'0'+strnum, False, (0, 0, 0))
                screen.blit(textsurface, (i*c*10+c, j*c*10+c*3))
    workers = move_workersV2(workers)
    """
    if t< 5:
        robots = move_robotsV3(robots, workers, shelves)
    else:
    """
    robots = move_robotsV5(robots, workers, shelves)

    """ uniquement pour du test
    coloredSurface = redSquare.copy()
    coloredSurface.fill((5,5,5))
    for i,j in display_obst_on_screen:
        (xdeb, ydeb, xfin, yfin) = (d+(i*10)*c, c*j*10+d, d+c*i*10+c*10, c*j*10+c*10+d)
        new_zone = pygame.transform.smoothscale(coloredSurface, (xfin - xdeb, yfin - ydeb) )  # affichage smooth
        screen.blit(coloredSurface, (xdeb, ydeb))
    """
    for i in range(len(robots)):
        screen.blit(robot_img, ((robots[i][0])*c*10, (robots[i][1])*c*10))

    for i in range(len(shelves)):
        screen.blit(shelf_img, ((shelves[i][0])*c*10, (shelves[i][1])*c*10))
        for j, num in enumerate(shelves[i][2]):
            strnum = str(abs(num))
            textsurface = miniFont.render(
                (3-len(strnum))*'0'+strnum, False, (0, 80, 80))
            screen.blit(textsurface, ((
                shelves[i][0])*c*10+c//2+(j % 2)*c*5, (shelves[i][1])*c*10+c//2+((j//2) % 2)*c*5))

    for i in range(len(workers)):
        screen.blit(worker_img, ((workers[i][0])*c*10, (workers[i][1])*c*10))
    pygame.display.flip()  # affichage de la page
    return len(robots) == 0


def main(nb_salve,screen=None, screen_size=None):
    global screen_width, screen_heigth, t
    if screen_size == None:
        screen_width = 1200  # dimension initiales de la fenêtre
        screen_heigth = 850
    else:
        (screen_width, screen_heigth) = screen_size

    background_color = (255, 255, 255)  # bleu clair
    if screen == None:
        screen = pygame.display.set_mode(
            (screen_width, screen_heigth), pygame.RESIZABLE)

    screen.fill(background_color)
    pygame.display.set_caption("Labyrinthe")
    pygame.display.flip()
    running = True
    t = 0
    while running:  # boucle traitant des event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # si on appuie sur la croix
                running = False
            if event.type == pygame.VIDEORESIZE:  # si on change la taille de la fenêtre
                screen_width = event.w
                screen_heigth = event.h
                screen = pygame.display.set_mode(
                    (screen_width, screen_heigth), pygame.RESIZABLE)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE] == 1:  # si on appuie sur echap
            running = False
        t += 1
        if t % 50 == 0:
            print(t,sum([len(colle(tranche)) for tranche in cluster_restant])+sum([len(colle(carton_restants)) for carton_restants in strategie]),nb_commandes-sum([len(tranche) for tranche in cluster_restant])-sum([len(carton_restants) for carton_restants in strategie]))
        # refresh à chaque tour de boucle
        stop = afficher_labyrinthe(
            screen, background_color, (screen_width, screen_heigth))
        if t<= nb_salve:
            spawn_robots()
        if stop == 1:
            running = False
            print(t)
        time.sleep(0.0002)


init(3)
main(3)
