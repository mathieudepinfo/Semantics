section .text

;dans ce premier bloc les deux premieres lignes sont inutiles et sont enlevees lors de l'optimisation
mov [rax], 3
mov [y], [rax]
mov [rax], 5
mov [y],2 

ret

;ici rien n'est enleve car y n'est pas ecrase donc la premiere ligne reste aussi
mov [rax], 3
mov [y], [rax]
mov [rax], 5

ret

;ici on devrait enlever la  troisieme ligne mais ce n'est pas fait 
;car je suppose qu'il y a une dependance entre "pop y" et y (rsp se deplace d'un nombre de bits dependant de y?)
;facilement modifiable en commentant les deux lignes dans le constructeur de AsmCodeLine
mov x, 3
push x
mov y, x
pop y
mov x, 4

ret

;ici on supprime les lignes 2 et 4 qui sont inutiles

mov a, 5
add a, 0
mov b, 4 
sub b, 0

ret

;vous pouvez aussi testez de changer "test.asm" par "out.asm" dans le main de optimisation.py pour voir qu'il n'y a pas de modifications 