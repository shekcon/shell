class Token():
    '''
    Tasks:
    - Parse text input from user into list of arguments
    - Command substitution still one argument
    - Also help now user is missing anything
    '''

    def __init__(self, string):
        self.str = string + " "
        self.len = len(self.str)
        self.i = 0
        self.tokens = ["'", '"', "`", "|", "&", ">", "<", "(", ")"]
        self.param = ''
        self.args = []
        self.key = ''
        self.stack = []
        self.escape = True

    def _check_stack(self):
        if len(self.param) > 2 and self.param[-2:] == "${" and not (
                len(self.param) > 3 and self.param[-3:] == "\\${"):
            self.stack.append("}")
        elif self.key != "`" and ((self.param and self.param[-1:] == "`") and
                                  not (self.stack and self.stack[-1] == '`') and
                                  not (len(self.param) > 2 and self.param[-2:] == "\\`")):
            self.stack.append("`")
        elif self.param and self.stack and\
                self.param[-1] == self.stack[-1]:
            self.stack.pop()

    def _is_subshell(self):
        return self.key == '(' and self.str[self.i] != ")"

    def _is_single_quote(self):
        return self.key == "'" and self.str[self.i] != "'"

    def _is_double_quote(self):
        return self.key == '"' and (self.str[self.i] != '"' or
                                    (self._is_back_slash() and self.str[self.i] == "\""))

    def _is_back_slash(self):
        return self.i - 1 >= 0 and self.str[self.i - 1] == '\\' and self.escape

    def _is_back_quote(self):
        return self.key == "`" and (self.str[self.i] != "`" or
                                    (self._is_back_slash() and self.str[self.i] == "`"))

    def _is_start_param(self):
        return not self.key and self.str[self.i] != " "

    def _is_element_param(self):
        return bool(self.key) and (self._is_single_param()
                                   or self._is_element_token()
                                   or self._is_element_op())

    def _is_single_param(self):
        return self.str[self.i] != " " and self.key not in self.tokens

    def _is_element_token(self):
        return self._is_single_quote() or\
            self._is_double_quote() or\
            self._is_back_quote() or\
            self._is_subshell()

    def _is_element_op(self):
        return self._is_operator_or() or self._is_operator_and()

    def _is_operator_or(self):
        return self.key == '|' and self.str[self.i] != "|"

    def _is_operator_and(self):
        return self.key == '&' and self.str[self.i] != "&"

    def _add_argument(self):
        if self.key in self.tokens and\
                (self.str[self.i] == self.key or self.str[self.i] == ")"):
            self.param += self.str[self.i]
        if self.key in ['"']:
            self.param = self.param.replace('\\"', '"')
        self.args.append(self.param)
        if self._change_param():
            self.i -= 1

    def _check_escape_chr(self):
        if self.str[self.i] == '\\':
            if (self.key not in self.tokens and
                self.i + 1 < self.len and
                self.str[self.i + 1] not in ["'", "`", "|", "&", ">", "<", "(", ")", "~", '$', '{']) or\
                (self.key in self.tokens and
                 self.i + 1 < self.len and self.str[self.i + 1] in ["\"", "\\"]):
                self.escape = False
                self.i += 1

    def _add_content_param(self):
        self.escape = True
        self._check_escape_chr()
        self.param += self.str[self.i]
        self._check_stack()

    def _clear_param_key(self):
        self.param = ''
        self.key = ''

    def _set_param_key(self):
        self.key = self.str[self.i]
        self._check_escape_chr()
        self.param = self.str[self.i]

    def _change_param(self):
        return self.param and not self._is_back_slash() and\
            (self.str[self.i] in self.tokens and self.key not in self.tokens) or\
            (self.key in ['>', "<", "|"]
             and self.str[self.i] != self.key)

    def split_token(self):
        while self.i < self.len:
            # find index start param of user
            if self._is_start_param():
                self._set_param_key()

            # add element of param into variable
            elif (self._is_element_param() and not self._change_param()) or\
                    self.stack:
                self._add_content_param()

            # store param if param not empty
            elif self.param:
                self._add_argument()
                self._clear_param_key()
            self.i += 1

        return self.args


if __name__ == "__main__":
    while True:
        input_user = input("intek-sh$ ")
        args = Token(input_user)
        print(args.split_token())
        if input_user == 'exit':
            break