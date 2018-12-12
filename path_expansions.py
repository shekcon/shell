#!/usr/bin/env python3

from os import path, getenv
import os


def check_name(name):
    # check if name is a valid identifier or not
    if not name or name[0].isdigit():
        return False
    for char in name:
        if not (char.isalnum() or char is '_'):
            return False
    return True


def expand_tilde(arg):
    cur_path = getenv('PWD')
    old_path = getenv('OLDPWD')
    arg = path.expanduser(arg)
    if (arg == '~+' or arg.startswith('~+/')) and cur_path:
        arg = arg.replace('~+', cur_path, 1)
    if (arg == '~-' or arg.startswith('~-/')) and old_path:
        arg = arg.replace('~-', old_path, 1)
    return arg


def tilde_expansions(string):
    args = string.split()
    for i, arg in enumerate(args):
        if '~' in arg:
            if '=' in arg:
                key, new_args = arg.split('=', 1)
                if check_name(key):
                    args[i] = key + '=' + ':'.join([expand_tilde(x) for
                                                    x in new_args.split(':')])
            else:
                args[i] = expand_tilde(arg)
    return ' '.join(args)


def parameter_expansions(string):
    exit_value = 0
    string = path.expandvars(string)
    if '$?' in string:
        string = string.replace('$?', str(os.environ['?']))
    while '$' in string:
        if '${' in string:
            name = string[string.find('${'):string.find('}')+1]
            if check_name(name[3:-1]):
                string = string[:string.find('${')] + \
                         string[string.find('}')+1:]
                continue
            else:
                exit_value = 1
                string = 'bash: %s: bad substitution' % name
                return exit_value, string
        j = string.index('$') + 1
        while j < len(string) and string[j] and \
                (string[j].isalnum() or string[j] == '_'):
            j += 1
        string = string[:string.index('$')] + string[j:]
    return exit_value, string


def path_expansions(string):
    exit_value = 0
    if '~' in string:
        string = tilde_expansions(string)
    if '$' in string:
        if ' $ ' in string:
            ministrings = string.split(' $ ')
            for i, ministring in enumerate(ministrings):
                exit_value, s = parameter_expansions(ministring)
                if exit_value:
                    return exit_value, s
                else:
                    ministrings[i] = s
            string = ' $ '.join(ministrings)
        else:
            exit_value, string = parameter_expansions(string)
    return exit_value, string


# if __name__ == "__main__":
#     print(path_expansions("echo +${dawdawd}"))
    # print(path_expansions("echo +$ {PATH } _adwad${PATH}"))
