import getpass
import time
import sys
from lexer.lexer import Lexer
from repl import repl
from tokens import tokens
from parser.parser import *
from parser.LL1 import *

sys.path.append("..")


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
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(content)
                l = Lexer(character_stream=content)
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
                print(f"Total runtime is {round(end_time - start_time, 8)}\n")

            except FileNotFoundError:
                print("Error: File not found.")
        elif command in ["show_tokens", "st"]:
            try:
                if l.tokens:
                    for i in l.tokens:
                        print(i, end='\n\n')
                else:
                    print("You have no tokens!\n")
            except UnboundLocalError:
                print("You need to scan some Monke first!\n")
        elif command in ["parse_tokens", "pt"]:
            try:
                # Create a parser and start parsing
                p = Parser(l.tokens)  # Pass the tokens deque to the parser
                ast = p.parse()  # Call the parser's parse method
                print(f'\nHERE IS THE AST\n{ast}\n')  # Print the AST for debugging
            except (UnboundLocalError, ReferenceError) as e:
                print(
                    f"\n{e}\nScan your source code to generate some tokens first. "
                    f"Use 'keywords' command to find out how\n")
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
- scan_file: Read code from a file and tokenize it.
- show_tokens: Show the tokens generated from the Lexical Analysis.
- parse_tokens: Create an Abstract Syntax Tree from the tokens.
- eval: Directly interact with your compiler output at any stage.\n'l' commands are for Lexer.\n'p' commands are for Parser.
- keywords: List the reserved keywords in the Monke language.
- about: Display information about the MonkePaw compiler.
- exit: Exit the Monke compiler.
""")
        elif command == "exit":
            print("Bye!")
            break
        else:
            print("Invalid command. Enter 'help' for options.")


if __name__ == "__main__":
    main()
