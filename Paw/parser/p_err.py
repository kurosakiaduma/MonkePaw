class ParseError():
    pass

class AssignmentError(ParseError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class DeclarationError(ParseError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
