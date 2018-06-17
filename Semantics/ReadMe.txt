Projet Optimisation de code 
MARSOT Mathieu

Le but de mon travail est d'éliminer les instructions assembleur inutile par étude des dépendances entre les variables dans le code.

Approche du problème : 
    Premièrement je découpe tout d'abord le code en BasicBlocks
    Une fois ces blocs obtenus je crée un graphe de dépendances pour chacun d'eux
    Ensuite je supprime les lignes de code inutiles en étudiant les dépendances


Tests et limites : 
    Lancer le fichier Optimisation.py pour obtenir le résultat de l'optimisation de code sur le fichier test.assembleur
    Pour effectuer un test complémentaire, changer le fichier test.asm par out.asm pour voir que sur un code plus complexe déja optimisé de slignes ne sont pas effacées
    
    Les faiblesses du programme sont surtout liées au parsing du texte .asm car cette partie était je pense moins intéressante par rapport au cours. 
    Les instructions du fichier .asm doivent donc toutes être en position 0 de la ligne (pas de tabulations ou d'espaces avant)
    et il ne doit pas y avoir de commentaires sur la même ligne qu'une instruction
    Seules les instructions mov, add, sub, xor, inc, push et pop sont prises en compte pour le calcul des dépendances

    J'ai aussi ajouté une petite amélioration qui supprime les instructions de type "add x, 0" et "sub x, 0"

    Je pense sinon que mon programme ne supprimera jamais une ligne utile au code d'origine 

Details des classes (voir commentaires dans le fichier pour plus de détails): 

    -BasicBlock est tout simplement un bloc de code sans sortie (jmp, ret, call...)

    -AsmCodeLine est un pre traitement applique à chaque ligne du fichier pour rendre la generation du graphe des dépendances plus facile

    -DependancyNode est un noeud (une variable) du graphe des dependances, chaque variable connait les variables dont elle dépend

    -DependancyGraph contient la liste des variables modifiées dans un bloc donné et permet d'optimiser le code d'un bloc

    -ControlFlowGraph porte mal son nom et permet en fait seulement de découper le code en BasicBlock avant de l'optimiser 