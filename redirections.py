#!/usr/bin/env python3
from os import path
from subprocess import PIPE

from process_keys import *


'''
> : Directs the output of a command into a file.
>> : Does the same as >, except that if the target file exists, the new data are appended.
< : Gives input to a command.
<< : A here document. It is often used to print multi-line strings.
'''


def output_redirection(args, in_pipes):
    stdout_file = ''
    exit_value = 0
    # stderr_file = None
    other_args = []
    i = 0
    mode = ''
    while i < len(args):
        if args[i] == '>>':
            stdout_file = args[i+1]
            try:
                open(stdout_file, 'a+').close()
                mode = 'a+'
            except PermissionError:
                if not in_pipes:
                    Shell.printf('intek-sh: ' + stdout_file +
                                 ': Permission denied')
                exit_value = 126
                stdout_file = ''
        elif args[i] == '>':
            stdout_file = args[i+1]
            try:
                open(stdout_file, 'w+').close()
                mode = 'w+'
            except PermissionError:
                if not in_pipes:
                    Shell.printf('intek-sh: ' + stdout_file +
                                 ': Permission denied')
                exit_value = 126
                stdout_file = ''
        else:
            other_args.append(args[i])
            i -= 1
        i += 2

    if mode:
        return open(stdout_file, mode), other_args, exit_value
    else:
        return PIPE, other_args, exit_value


def input_redirection(args, in_pipes):
    stdin_file = ''
    other_args = []
    exit_value = 0
    i = 0
    while i < len(args):
        if args[i] == '<':
            stdin_file = args[i+1]
            if not path.isfile(stdin_file):
                if not in_pipes:
                    Shell.printf('intek-sh: ' + stdin_file +
                                 ': No such file or directory')
                exit_value = 1
                stdin_file = ''
            else:
                try:
                    open(stdin_file, 'r').close()
                except PermissionError:
                    if not in_pipes:
                        Shell.printf('intek-sh: ' + stdin_file +
                                     ': Permission denied')
                    exit_value = 126
            i += 1
        elif args[i] == '<<':
            # every content between args[i+1] and args[-1] is content of
            # a document which is stdin_file
            with open('.stdin_file', 'w+') as f:
                f.write('\n'.join(args[i+2:-2]))
                f.close()
            stdin_file = '.stdin_file'
            i = len(args) - 1
        else:
            other_args.append(args[i])
        i += 1
    if stdin_file:
        return open(stdin_file, 'r'), other_args, exit_value
    else:
        return PIPE, other_args, exit_value


def run_redirections(args, in_pipes):
    _stdout, args, exit_value = output_redirection(args, in_pipes)
    _stdin, args, exit_value = input_redirection(args, in_pipes)
    return _stdin, _stdout, args, exit_value
