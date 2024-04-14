import getpass, time
from repl import repl
from lexer.lexer import Lexer
from tokens import tokens

def main():
    username = getpass.getuser()

    import os
    os.system('cls' if os.name == 'nt' else 'clear') 

    monke_logo = """
  /\/\  
 /-  -\ 
| |__| |
 \_||_/
 / /\ \  
|/ /  \ \
\ \   / /
 \_\_/_/
    """

    print(monke_logo)
    print(f"Hello, {username}! Welcome to the Monke compiler!")
    print("Type in commands to get started (or 'help' for options):")

    while True:
        command = input("> ").lower()
        if command == "start":
            repl.start()
            break  # Exit after starting the REPL
        elif command in ["read_file", "rf"]:
            filename = input("Enter the full path of the file: ")
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(content)
                l = Lexer(character_stream=content)
                start_time = time.time()
                tok = l.next_token()
                while tok.type != tokens.EOF:
                    print(f'{tok}\n')
                    tok = l.next_token()
                end_time = time.time()
                print(f"Total runtime is {round(end_time-start_time,8)}\n")
            except FileNotFoundError:
                print("Error: File not found.")
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
- read_file: Read code from a file and tokenize it.
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
