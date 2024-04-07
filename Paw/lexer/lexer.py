from tokens import tokens

class Lexer:
    def __init__(self, character_stream):
        self.character_stream = character_stream
        self.position = 0
        self.read_position = 0
        self.ch = ''

    # Initialize the lexer
    def read_char(self):
        if self.read_position >= len(self.character_stream):
            self.ch = '\0'  # ASCII code for "NULL" character
        else:
            self.ch = self.character_stream[self.read_position]
        self.position = self.read_position
        self.read_position += 1

    # Skip whitespace in the character_stream
    def skip_whitespace(self):
        while self.ch in ' \t\n\r':
            self.read_char()

    # Peek at the next character without advancing the lexer
    def peek_char(self):
        if self.read_position >= len(self.character_stream):
            return '\0'
        else:
            return self.character_stream[self.read_position]

    # Read an identifier from the character_stream
    def read_identifier(self):
        start_position = self.position
        while self.ch.isalpha():
            self.read_char()
        return self.character_stream[start_position:self.position]

    # Read a number from the character_stream
    def read_number(self):
        start_position = self.position
        while self.ch.isdigit():
            self.read_char()
        return self.character_stream[start_position:self.position]

    # Get the next token from the character_stream
    def next_token(self):
        self.skip_whitespace()
        if self.ch == '=':
            if self.peek_char() == '=':
                ch = self.ch
                self.read_char()
                tok = tokens.Token(tokens.EQ, ch + self.ch)
            else:
                tok = self.new_token(tokens.ASSIGN, self.ch)
        elif self.ch == ";":
            tok = tokens.Token(tokens.SEMICOLON, self.ch)
        
        self.read_char()
        return tok

    # Helper method to create a new token
    def new_token(self, token_type, ch):
        return tokens.Token(token_type, ch)

# Check if a character is a letter
def is_letter(ch):
    return ch.isalpha() or ch == '_'
