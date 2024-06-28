# Carte interactive des IPS de de la Métropole de Rouen Normandie

## Qu'est ce qu'un IPS ?

L'IPS (Indice de Position Sociale) est un indicateur permettant de mesurer la situation sociale des élèves face aux apprentissages dans les établissements scolaires français. 

Plus l'IPS est élevé, plus l'élève se situe dans un environnement favorable aux apprentissages.

Cet indice est calculé à partir des catégories socio-professionnelles des parents.

## Comment cette carte a-t-elle été réalisée ?

J'ai d'abord récupéré les données géographiques de tous les établissements scolaires français, les données géographiques de la Métropole Rouen Normandie, et celles des communes, sur data.gouv.fr. J'ai extrait, avec Qgis, à partir des contours de la Métropole, les établissements uniquement de la métropole, et uniquement les communes de la métropole. 

J'ai aussi importé une base de données des IPS de tous les établissements scolaires ; j'ai lié ces données aux données géographiques en les connectant par code UAI.

J'ai ensuite importé toutes ces données dans une base de données PostgreSQL. J'ai réalisé un petit script SQL qui m'a permit d'obtenir, pour chaque ville, le nombre d'établissements scolaires, ainsi que la moyenne des IPS de ces établissements.

Ces informations acquises, j'ai pû réaliser une carte avec QGis. 

J'ai ensuite réalisé une première carte interactive en 2D avec Dash Leaflet et Dash Bootstrap pour la modale. 
Pour obtenir les images des établissements, j'ai écrit un script de pré-process, qui stocke la première image trouvée sur Google de l'établissement (récupérée avec ICrawler), et la renomme en fonction du numéro UAI. 

Enfin, j'ai fait une deuxième carte interactive avec Dash Deck, cette fois-ci en 3D. 
J'ai récuperé les informations de la BDTopo - couche bâtiments -, que j'ai filtrés par type de bâtiment, pour ne garder que les établissements scolaires ; cela m'a permit d'avoir un JSON reliant les établissements scolaires et la hauteur de leur bâtiment.


## Remerciements

Merci à Thomas Escrihuela et à toute l'équipe du CEREMA pour leur aide ;)