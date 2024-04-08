import getpass
from repl import repl

def main():
    username = getpass.getuser()
    print(f"Hello {username}! This is the Monke programming language!")
    print("Type in any commands to see generated tokens")
    repl.start()

if __name__ == "__main__":
    main()
