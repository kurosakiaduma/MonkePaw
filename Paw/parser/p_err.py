from Paw.tokens.tokens import Token


class ParseError:
    def __init__(self,
                 token: Token,
                 message: str
                 ):
        self.error_info = f"Unexpected token {token} with lexeme '{token.lexeme}' at position {token.begin_position} " \
                          f"on line {token.line_position}."
        self.message = ''.join(info + '\n' for info in [message, self.error_info])

    def __str__(self):
        return self.error_info

    def __repr__(self):
        return self.message