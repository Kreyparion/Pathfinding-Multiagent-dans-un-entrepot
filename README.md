# Pathfinding multiagent dans un entrepot

### Attribution des commandes

- Clustering selon la proximité des articles des commandes
- Répartition des commandes petits à petit aux robots à la récupération des étagères
    
    -> Amélioration potentielle : Attribution de nouvelles commandes passant par des opérqteurs non surchargés

### Pathfinding sans collision - version 5

- Check des robots coincés / qui attendent sur une case pour les éviter
- Pathfinding avec dijkstra vers le carton/point de dépot le plus proche en prenant en compte le déplacement des autres robots

## Stratégies
### Strategie 1 - Détachement si opérateur trop loin

Calcul de la distance de la prochaine étagère disponible et comparaison à la distance de l'opérateur à l'étagère. Détachement si l'opérateur est trop loin.

-> En régime permanent / t assez grand, la plupart des robots sont bloqués car une étagère est au niveau du dernier colis à récupérer. Tout se bloque -> Besoin de la strategie 2

### Strategie 2 - Détachement si bloquée

Détachement de l'étagère si le robot se retrouve bloqué et ne peut pas atteindre son objectif

-> Problème de vas-et-viens des robots qui se détachent et reviennent car ils pensent que l'étagère qu'ils viennent de laisser doit être traitée. -> Besoin de strategie 3

### Strategie 3 - Liste des étagères en attente sans les étagères bloquées

Listage des étagères en attentes : prêtes à être récupérées par un robot selon ces critères :
- Etagère n'est pas déjà connectée / l'objectif d'un autre robot
- Etagère a été / va bientôt être traitée par un opérateur
- **Etagère non bloquée**

### Strategie 4 - Les robots coincées se déplace au plus proche de leur objectif
Un robot coincé va s'arreter et géner toute la circulation.
Il se coince le plus souvent au moment d'aller chercher son dernier article. On a intéret à qu'il s'arrête proche de cet article et pas dans l'avenue principale

-> Prend la priorité sur la strategie 2 mais compatible

### Strategie 5 - Better Pathfinding
Les robots prennent maintenant en compte les déplacement des autres robots et peuvent donc se suivre dans un couloir.
Ce principe marche avec du marquage au sol du prochain déplacement, selon les notations de "tableau_entrepot.md". L'algo de plus court chemin prend donc ces marquages en compte.

-> Optimise même quand les étagères sont fixées.

[Rendu](robot_demo.gif)