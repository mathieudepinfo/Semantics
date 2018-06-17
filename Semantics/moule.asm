global main
extern printf, atoi
section .data
hello: db "return %d", 10, 0

VAR_DECLS

section .text
main:
sub rsp, 16
mov [rsp+8], rdi
mov [rsp], rsi

VAR_INIT


BODY

RET_EXPR
mov rsi, rax
mov rdi, hello
xor rax, rax
call printf

add rsp, 16
ret
