import time
from lexer.lexer import Lexer
from tokens import tokens

PROMPT = "(Lexer) >>"

def start():
    while True:
        line = input(PROMPT)
        line+='\n'
        if line == ":quit":
            return
        l = Lexer(line)
        start_time = time.time()
        while True:
            tok = l.next_token()
            try:
                if tok.type == tokens.EOF:
                    break
                print(f'{tok}\n')
            except AttributeError:
                continue
                
        end_time = time.time()
        print(f"Total runtime is {round(end_time-start_time,8)}\n")
