class ParseError(SystemExit):
    def __init__(self, message, code=2):
        super().__init__(code)
        self.message = message
