import sys
from lexer.lexer import Lexer
from tokens import tokens

PROMPT = ">>"

def start():
    while True:
        line = input(PROMPT)
        l = Lexer(line)
        tok = l.next_token()
        while tok.type != tokens.EOF:
            print(f'{tok}\n')
            tok = l.next_token()
