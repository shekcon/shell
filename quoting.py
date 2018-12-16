class Quote:

    def __init__(self, string):
        self.i = 0
        if (string.startswith('"') and string.startswith('"')) or\
                (string.startswith("'") and string.startswith("'")):
            self.str = string[1:-1:]
        else:
            self.str = string
        self.new_str = ''

    def _check_escape_chr(self):
        if self.str[self.i] == '\\':
            self.i += 1

    def remove_quote(self):
        while self.i < len(self.str):
            self._check_escape_chr()
            self.new_str += self.str[self.i]
            self.i += 1
        return self.new_str
