import getpass
import time
import sys
from lexer.lexer import Lexer
from repl import repl
from tokens import tokens
from parser.parser import *
from parser.LL1 import *

sys.path.append("..")


def scan(source: str | None = None, filename: str | None = None):
    if filename:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                print(content)
                source = content
        except FileNotFoundError:
            print("Error: File not found.")

    lexer = Lexer(character_stream=source)
    start_time = time.time()

    while True:
        tok = lexer.next_token()
        try:
            if tok.type == tokens.EOF:
                break
            print(f'token found-> {tok}\n'
                  f'\ntokens -> {lexer.tokens}\n')
        except AttributeError:
            continue

    end_time = time.time()
    print(f"Total runtime is {round(end_time - start_time, 8)}\n")
    return lexer

def main():
    username = getpass.getuser()

    import os
    os.system('cls' if os.name == 'nt' else 'clear')

    monke_logo = ("\n"
                  "  /\\/\\   \n"
                  " /-  -\\ \n"
                  "| |__| |\n"
                  " \\_||_/\n"
                  " / /\\ \\  \n"
                  "|/ /  \\ \\n"
                  "\\ \\   / /\n"
                  " \\_\\_/_/\n"
                  " ")

    print(monke_logo)
    print(f"Hello, {username}! Welcome to the Monke compiler!")
    print("Type in commands to get started (or 'help' for options):")

    while True:
        command = input("(MonkePaw)> ").lower()
        if command == "start":
            repl.start()
            break  # Exit after starting the REPL
        elif command in ["scan_file", "sf"]:
            filename = input("Enter the full path of the file: ")
            l = scan(filename=filename)
        elif command in ["show_tokens", "st"]:
            try:
                if l.tokens:
                    for i in l.tokens:
                        print(i, end='\n\n')
                else:
                    print("You have no tokens!\n")
            except UnboundLocalError:
                print("You need to scan some Monke first!\n")
        elif command in ["parser", "prs"]:
            while True:
                parser_command = input("(Parser)> ").lower()
                if parser_command in ["parse_directly", "pd"]:
                    statement = input("Enter your statement: ")
                    parser_lexer = scan(source=statement)
                    print(f'TOKENS - {parser_lexer.tokens}')
                    p = Parser(parser_lexer.tokens)
                    pst = p.parse()
                    print(f'\nHERE IS THE PST STATEMENTS: \n{pst}\n')
                elif parser_command in ["parse_file", "pf"]:
                    filename = input("Enter the full path of the file: ")
                    parser_lexer = scan(filename=filename)
                    p = Parser(parser_lexer.tokens)
                    pst = p.parse()
                    print(f'\nHERE IS THE PST STATEMENTS: \n{pst}\n')
                elif parser_command in ["show_ast", "sa"]:
                    try:
                        print(f'\nHERE IS THE Parse Tree\n')
                        p.show_ast()
                    except UnboundLocalError:
                        print("\nPlease parse tokens before displaying Concrete Syntax Tree")
                elif parser_command in ["show_symbol_table", "sst"]:
                    try:
                        print(p.symbol_table)
                    except UnboundLocalError:
                        print("\nPlease parse tokens before displaying Symbol Table")
                elif parser_command == "exit":
                    break
                else:
                    print("Invalid command. Enter 'help' for options.")
        elif command in ["eval_tokens", "et"]:
            while True:
                inp = (input("(Token Evaluator) Enter position> "))
                if inp == 'q':
                    break
                try:
                    print(eval(f'\nl.tokens[{inp}]'))
                    continue
                except (IndexError, NameError):
                    print("Out of bounds of token stream")

        elif command in ["eval_ast", "ea"]:
            while True:
                inp = (input("(AST Evaluator) Enter position> "))
                try:
                    print(eval(f'\np.ast[{inp}]'))
                except (IndexError, NameError):
                    print("Out of bounds of AST")
                if inp != 'q':
                    break
        elif command in ["show symbol table", "sst"]:
            try:
                print(p.symbol_table)
            except UnboundLocalError:
                print("\nPlease parse tokens before displaying Symbol Table")
        elif command == "keywords":
            print("Reserved Keywords:")
            for keyword in tokens.keywords.keys():
                print(f"- {keyword}")
        elif command == "about":
            print("""
MonkePaw Compiler

A compiler written in Go (frontend) and Python (backend) to
translate Monke, a custom language inspired by Robert Nystrom's Lox,
into Python code.

This is a work in progress, but it aims to provide a user-friendly
and interactive environment for learning and experimenting with language
compilation. This Python workspace also hosts a Monke lexer.
""")
        elif command == "help":
            print("""
Available Commands:

- start: Start the interactive REPL for tokenizing code.
- scan_file or sf: Read code from a file and tokenize it.
- show_tokens or st: Show the tokens generated from the Lexical Analysis.
- parser or prs: Enter the parser submenu.
- keywords: List the reserved keywords in the Monke language.
- about: Display information about the MonkePaw compiler.
- exit: Exit the Monke compiler.

Parser Submenu Commands:

- parse_directly or pd: Parse statements directly from the user.
- parse_file or pf: Parse a source file.
- show_ast or sa: Show the Abstract Syntax Tree.
- show_symbol_table or sst: Show the symbol table.
- exit: Exit the parser submenu.

""")
        elif command == "exit":
            print("Bye!")
            break
        else:
            print("Invalid command. Enter 'help' for options.")


if __name__ == "__main__":
    main()
