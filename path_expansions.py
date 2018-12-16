#!/usr/bin/env python3

import os
from os import getenv, path


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


def tilde_expansions(args):
    for i, arg in enumerate(args):
        if '~' in arg:
            if arg.startswith('\\'):
                # args[i] = arg[1:]
                continue
            elif arg[0] in ('\'', '\"'):
                # args[i] = arg[1:-1]
                continue
            if '=' in arg:
                key, new_args = arg.split('=', 1)
                if check_name(key):
                    args[i] = key + '=' + ':'.join([expand_tilde(x) for
                                                    x in new_args.split(':')])
            else:
                args[i] = expand_tilde(arg)
    return args


def parameter_expansions(args):
    exit_value = 0
    for i, arg in enumerate(args):
        if not arg:
            continue
        if arg == '$' or '$' not in arg:
            continue
        if arg[0] in ('"', "'", '`', '(') and arg[-1] in ('"', "'", '`', ')'):
            args[i] = arg[1:-1]
            continue
        # if arg.startswith('\"'):
        #     arg = arg[1:-1]
        if arg.startswith('\\'):
            args[i] = arg[1:]
            continue
        arg = path.expandvars(arg)
        if '$?' in arg:
            arg = arg.replace('$?', os.environ['?'])
        while '$' in arg:
            if '${' in arg:
                name = arg[arg.find('${')+2:arg.find('}')]
                if check_name(name):
                    arg[i] = arg[:arg.find('${')] + arg[arg.find('}')+1:]
                    continue
                else:
                    return 1, 'intek-sh: ${' + name + '}: bad substitution'
            if '$' in arg:
                j = arg.index('$') + 1
                while j < len(arg) and (arg[j].isalnum() or arg[j] == '_'):
                    j += 1
                arg = arg[:arg.index('$')] + arg[j:]
        args[i] = arg
    return exit_value, args


def path_expansions(args):
    args = tilde_expansions(args)
    exit_value, args = parameter_expansions(args)
    return exit_value, args
