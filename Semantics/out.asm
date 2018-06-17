global main
extern printf, atoi
section .data
hello: db "return %d", 10, 0

y: dq 0
x: dq 0


section .text
main:
sub rsp, 16
mov [rsp+8], rdi
mov [rsp], rsi


mov rdx, [rsp]
mov rdi, [rdx+8]
call atoi
mov [x], rax

mov rdx, [rsp]
mov rdi, [rdx+16]
call atoi
mov [y], rax



debut1: 
mov rax, [x]

cmp rax, 0
je fin1
mov rax, 1

push rax
mov rax, [x]

pop rbx
sub rax, rbx

mov [x], rax

mov rax, 1

push rax
mov rax, [y]

pop rbx
add rax, rbx

mov [y], rax


jmp debut1
fin1:


mov rax, [y]

mov rsi, rax
mov rdi, hello
xor rax, rax
call printf

add rsp, 16
ret
