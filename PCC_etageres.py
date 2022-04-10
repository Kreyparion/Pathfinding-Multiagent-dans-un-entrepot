import pygame
import time
import random
import math
from copy import deepcopy
from Attribution_zones import generation_commandes,new_commande

# les Stratégies
strategie1 = True          # Les robots se détachent des étagères si le temps d'attente d'un opérateur est trop important
strategie2 = True         # Les robots se détachent des étagères si ils sont coincés
        # Problème commun 1 -> Les étagères qui cherchent leur dernier carton qui est déjà coincé par une autre étagère
        # Problème commun 2 -> Les étagères sont coincées entre 2 autres étagères
        # Comment déclarer cette étagère ? Libre, coincée ?
strategie3 = True          # lent // dans waiting shelves, selectionne que celles non coincées
                            # Problème : détecte une étagère comme coincée même si obstruée par le robot allant la chercher
strategie4 = False          # Les robots coincés se rapprochent de leur objectif
strategie5 = True          # Les robots peuvent se suivre /!\ à garder à true si on utilise V5

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
    """
    Spawn robots so that there is no superposition
    ---
    Only add to the variables : robots - destination_robots - distance_to_destination_robots
    """
    global robots,destination_robots, distance_to_destination_robots
    robots = robots + [(x, y, -1) for (x, y) in depot]
    destination_robots = destination_robots + [(x, y) for (x, y) in depot]
    distance_to_destination_robots = distance_to_destination_robots + [10000 for _ in depot]


def init(nb_robot,nb_etagères):
    """
    Initialisation de la fenêtre et des différentes variables

    """
    global robots, pos_obstacles, tab_carton, myfont, tab_lab, miniFont, destination_shelves, strategie, connected, cluster_restant, worker_zone, pos_worker_zone, workers, shelves, destination_robots, distance_to_destination_robots,status_shelves
    tab_carton = []
    points = []
    tab_carton = [[0]*(nbtuileshaut+1) for _ in range(nbtuileslong+1)]
    points = generation_commandes(nb_commandes, 5, tab_carton, nbtuileslong, nbtuileshaut)
    cluster_restant = deepcopy(points)
    #robots = [(1,1,[0,0,0,0]),(12,1,[0,0,0,0]),(24,1,[0,0,0,0])]
    robots = [(x, y, -1) for (x, y) in depot]+[(x, y, -1) for (x, y) in depot] + [(x, y, -1) for (x, y) in depot] +[(x, y, -1) for (x, y) in depot] + [(x, y, -1) for (x, y) in depot] + [(x, y, -1) for (x, y) in depot]+ [(x, y, -1) for (x, y) in depot] + [(x, y, -1) for (x, y) in depot]
    robots = robots[0:nb_robot]
    shelves = [(x+1, y, [0, 0, 0, 0])for (x, y) in depot]+[(x-1, y, [0, 0, 0, 0])for (x, y) in depot]+[(x+2, y, [0, 0, 0, 0])for (x, y) in depot] + \
        [(x-2, y, [0, 0, 0, 0])for (x, y) in depot]+[(x+1, y, [0, 0, 0, 0]) for (x, y) in depot]+[(x-1, y, [0, 0, 0, 0])for (x, y) in depot]+[(x+2, y, [0, 0, 0, 0]) for (x, y) in depot]+[(x-2, y, [0, 0, 0, 0])for (x, y) in depot]+[(x+1, y, [0, 0, 0, 0]) for (x, y) in depot]+[(x-1, y, [0, 0, 0, 0])for (x, y) in depot]+[(x+2, y, [0, 0, 0, 0]) for (x, y) in depot]+[(x-2, y, [0, 0, 0, 0])for (x, y) in depot]+[(x+1, y, [0, 0, 0, 0]) for (x, y) in depot]+[(x-1, y, [0, 0, 0, 0])for (x, y) in depot]
    shelves = shelves[0:nb_etagères]
    workers = [(1, 1, []), (13, 1, []), (28, 1, []),
               (1, 13, []), (13, 13, []), (28, 13, [])]
    # initialisation des destinations des robots
    destination_shelves = [(i, j) for (i, j, k) in shelves]
    status_shelves = [-1 for _ in range(len(shelves))]
    destination_robots = [(i, j) for (i, j, k) in robots]
    distance_to_destination_robots = [10000 for _ in robots]
    strategie = [[] for _ in shelves]
    if display:
        pygame.font.init()
        # Définit la police + taille de police des cartons sur les obstacles
        myfont = pygame.font.SysFont('Comic Sans MS', 23) # Sur Windows 10
        # Définit la police + taille de police des cartons sur les robots
        miniFont = pygame.font.SysFont('Comic Sans MS', 12) # Sur Windows 5

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



def enumerate_in_order(liste):
    res = []
    new_liste = liste[:]
    for i in range(len(liste)):
        mini_id = new_liste.index(min(new_liste))
        res.append(mini_id)
        new_liste[mini_id] = 100000
    return res



def findclosest(coord, liste_obj, list_obstacles):
    """
    Par un algorithme de Djikstra, détermine le carton
    le plus proche du robots situé en 'coord' parmi ceux de 'liste_obj', et renvoie
    la position du point de collecte et la position à t+1 où aller pour se rendre au point de collecte
    
    Paramètres
    ------
    coord : tuple of int - les coordonnées de départ du parcours de graph
    liste_obj : array of coord - la liste des objectif parmi lesquels il faut déterminer le plus proche
    list_obstacles : array of int - le type d'obstacle qui peuvent bloquer l'objet qui se déplace (répertoriés dans tableau_entrepot.md)
    
    Global variable use
    ------
    tab_lab : array of array of int tableau de l'entrepot avec les types d'obstacles

    Return
    ------
    (index_closer,newpos) : tuple of tuple of int
    index_close : tuple of int - les coordonnés de l'objectif, coord si non trouvé ou si sur l'objectif
    newpos : tuple of int - les coordonnés du prochain déplacement, coord si non trouvé ou si sur l'objectif

    """
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
                            return ((i+1, j), (i+1, j))
                    else:
                        return ((i+1, j), (i0, j0))
        if not laby[i+1][j] in list_obstacles:
            if (i0, j0) == (-1, -1):
                listepriorite.append((i+1, j, i+1, j))
            else:
                listepriorite.append((i+1, j, i0, j0))
        elif not laby[i+1][j] in list_obstacles_reduite and strategie5:
            if laby[i+1][j] != 3:
                if (i0, j0) == (-1, -1):
                    if laby[i+1][j] == 4:
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
                    if laby[i-1][j] == 3:
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
                    if laby[i][j+1] == 1:
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
                    if laby[i][j-1] == 2:
                        listepriorite.append((i, j-1, i, j-1))
                else:
                    listepriorite.append((i, j-1, i0, j0))
    return ((posx, posy), (posx, posy))


def nextstep(coord, destination, list_obstacles):
    (posx, posy) = coord
    _, res = findclosest((posx, posy), [destination], list_obstacles)
    return res


def strat_sur_couloir(bot_strategie):
    """
    Designé pour transformer la variable strategie d'une étagère en modifiant les coordonnés pour qu'ils soient sur le couloir au lieu d'être sur les étagères de l'entrepot

    strategie : array (of length 4) of array of coord - Les articles à aller récupérer et dans quelles commandes ils vont
    return : array (of length 4) of array of coord - la même liste que strategie avec les indices décalés de 1 pour qu'ils soient sur les couloirs
    """
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


def distance(pos1, pos2):
    '''
    Renvoie la distance en nombre de blocs du chemin le plus court entre 2 positions (position d'un robot ou d'un opérateur) 
    (distance sans obstacles autre que les étagères de l'entrepot)
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
    """
    Enumère les étagères en attente d'être récupérées par un robot

    Paramètres
    -----
    shelves : les étagères
    workers : les opérateurs
    robots : les robots
    id_robot : l'indice du robot faisant la requête 

    """
    res = []
    for i, shelf in enumerate(shelves):
        add = 1
        pos_shelf = (shelf[0], shelf[1])
        for worker in workers:
            (wx, wy, requests) = worker
            if pos_shelf in requests:
                sx, sy = pos_shelf
                dist_case_robot = distance((sx, sy), (robots[id_robot][0], robots[id_robot][1]))
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
            if status_shelves[i] == -1:
                saved_pos = robots[id_robot]
                robots[id_robot] = (shelf[0], shelf[1],i)
                disapear,stuck,(newposx,newposy) = step1(0,[(shelf[0], shelf[1],i)],workers)
                robots[id_robot] = saved_pos

            else:
                stuck = status_shelves[i]
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

def clearboard():
    for i in range(len(tab_lab)):
        for j in range(len(tab_lab[0])):
            if tab_lab[i][j] != -1:
                tab_lab[i][j] = 0


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
        if stuck != 1 and strategie3:
            disappear = 1

    
    return disappear,stuck,(newposx,newposy)


def move_robotsV5(bots, operateurs, shelves):  # Deplace tous les robots
    global tab_lab,display_obst_on_screen
    new_robots = [() for _ in range(len(robots))]
    case_occupée = []
    delete_bot = []
    status_shelves = [-1 for _ in range(len(shelves))]
    lonlyshelves(shelves, bots)
    stuck_list = []
    
    liste_enumerate = enumerate_in_order(distance_to_destination_robots)
    for i in liste_enumerate:
        posx,posy,_ = bots[i]
        disappear,stuck,(newposx,newposy) = step1(i,bots,operateurs)
        if bots[i][2] != -1:
            status_shelves[bots[i][2]] = stuck
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
                if bots[i][2] != -1:
                    status_shelves[bots[i][2]] = stuck
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
    """ for testing purposes
    for i in range(len(tab_lab)):
        for j in range(len(tab_lab[0])):
            if tab_lab[i][j] == 5:
                display_obst_on_screen.append((i,j))
    """
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
                        indice = new_commande(strategie,cluster_restant)
                        new_cluster = cluster_restant.pop(indice)
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
    pygame.display.set_caption("Entrepot")
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
    robots = move_robotsV5(robots, workers, shelves)

    #""" uniquement pour du test
    coloredSurface = redSquare.copy()
    coloredSurface.fill((5,5,5))
    for i,j in display_obst_on_screen:
        (xdeb, ydeb, xfin, yfin) = (d+(i*10)*c, c*j*10+d, d+c*i*10+c*10, c*j*10+c*10+d)
        new_zone = pygame.transform.smoothscale(coloredSurface, (xfin - xdeb, yfin - ydeb) )  # affichage smooth
        screen.blit(coloredSurface, (xdeb, ydeb))
    #"""
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
        screen_width = 1200  # dimension initiales de la fenêtre 840 sur Windows
        screen_heigth = 850 # 590 sur Windows
    else:
        (screen_width, screen_heigth) = screen_size

    background_color = (255, 255, 255)  # bleu clair
    if screen == None:
        screen = pygame.display.set_mode(
            (screen_width, screen_heigth), pygame.RESIZABLE)

    screen.fill(background_color)
    pygame.display.set_caption("Entrepot")
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


if __name__ == "__main__":
    init(5,40)
    main(3)
