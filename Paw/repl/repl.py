import time
from lexer.lexer import Lexer
from tokens import tokens

PROMPT = ">>"

def start():
    while True:
        line = input(PROMPT)
        l = Lexer(line)
        start_time = time.time()
        tok = l.next_token()
        while tok.type != tokens.EOF:
            print(f'{tok}\n')
            tok = l.next_token()
        end_time = time.time()
        print(f"Total runtime is {round(end_time-start_time,8 )}\n")
