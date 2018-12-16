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
        self.escape = False

    def _check_stack(self):
        flag = False
        if self.key not in ["'", '"'] and not (self.stack and self.stack[-1] in ["'", '"']):
            if len(self.param) > 1 and self.param[-2:] == "${" and\
                    not (len(self.param) > 2 and self.param[-3:] == "\\${"):
                self.stack.append("}")
                flag = True
            elif (self.param and self.param[-1:] in ["'", '"']) and\
                not self.escape and\
                not (self.stack and self.param[-1] in ['`'] and self.stack[-1] in ['`']):
                self.stack.append(self.param[-1])
                flag = True
        if not flag and self.param and self.stack and\
                self.param[-1] == self.stack[-1] and not self.escape:
            self.stack.pop()

    def _is_subshell(self):
        return self.key == '(' and self.str[self.i] != ")"

    def _is_single_quote(self):
        return self.key == "'" and self.str[self.i] != "'"

    def _is_double_quote(self):
        return self.key == '"' and (self.str[self.i] != '"' or
                                    (self.escape and self.str[self.i] == "\""))

    def _is_back_quote(self):
        return self.key == "`" and (self.str[self.i] != "`" or
                                    (self.escape and self.str[self.i] == "`"))

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
        self.args.append(self.param)
        if self._change_param():
            self.i -= 1

    def _check_escape_chr(self):
        if self.str[self.i] == '\\':
            if self.key not in self.tokens and\
                    (self.i + 1 < self.len and self.str[self.i + 1] == " "):
                self.i += 1

    def _is_has_escape(self):
        if self.param[-1] == '\\':
            if self.previous == '\\':
                self.escape = not self.escape
            else:
                self.escape = True
        else:
            self.escape = False
        self.previous = self.param[-1]

    def _add_content_param(self):
        self._check_escape_chr()
        self.param += self.str[self.i]
        self._check_stack()
        self._is_has_escape()

    def _clear_param_key(self):
        self.param = ''
        self.key = ''
        self.escape = False
        self.previous = ''

    def _set_param_key(self):
        self.key = self.str[self.i]
        self._check_escape_chr()
        self.param = self.str[self.i]
        self._is_has_escape()

    def _change_param(self):
        return self.param and not self.escape and\
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

    def check_syntax(self):
        if self.key or self.stack:
            if self.stack:
                return 'intek-sh: parse token error `%s\'' % self.stack[-1]
            return 'intek-sh: parse token error `%s\'' % self.key
        previous = ''
        for i, arg in enumerate(self.args):
            if arg in ['&', '(', ')', '"', "'"] or\
                (arg and (arg == previous or
                          (arg in ['|', "||", '>>', '<', '>', '>>'] and
                           previous in ['|', "||", '>>', '<', '>', '>>']) or
                          (arg in ['|', '&&', '||'] and previous in ['&&', '||', '|']) or
                          (arg in ['&&', '||', '|'] and previous in ['>>', '<', '>', '>>']))):
                return 'intek-sh: syntax error near unexpected token `%s\'' % arg
            elif i != 0 and previous not in ['&&', '||'] and\
                ((arg.endswith(")") and not arg.endswith("\\)")) or
                    arg.startswith("(")):
                if arg.startswith("("):
                    return 'intek-sh: syntax error near unexpected token `(\''
                else:
                    return 'intek-sh: syntax error near unexpected token `)\''
            if arg in ['&&', '||', '|', "<", '<<', '>', '>>']:
                previous = arg
            else:
                previous = ''
        if self.args[-1] in ['&&', '||', '|', '>>', '<', '>', '>>']:
            return 'intek-sh: parse token error "%s"' % self.args[-1]
        elif self.args[0] in ['&&', '||', '|']:
            return 'intek-sh: parse token error "%s"' % self.args[0]
        return None


if __name__ == "__main__":
    while True:
        input_user = input("intek-sh$ ")
        args = Token(input_user)
        print(args.split_token())
        print(args.stack, args.key)
        if input_user == 'exit':
            break
