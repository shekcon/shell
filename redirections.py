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


def output_redirection(args):
    stdout_file = ''
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
                Shell.printf('bash: ' + stdout_file + ': Permission denied')
                return PIPE, [], 126
        elif args[i] in ('>'):
            stdout_file = args[i+1]
            try:
                open(stdout_file, 'w+').close()
                mode = 'w+'
            except PermissionError:
                Shell.printf('bash: ' + stdout_file + ': Permission denied')
                return PIPE, [], 126
        else:
            other_args.append(args[i])
            i -= 1
        i += 2

    if mode:
        return open(stdout_file, mode), other_args, 0
    else:
        return PIPE, other_args, 0


def input_redirection(args):
    stdin_file = ''
    other_args = []
    exit_value = 0
    i = 0
    while i < len(args):
        if args[i] in ('<'):
            stdin_file = args[i+1]
            if not path.isfile(stdin_file):
                Shell.printf('bash: ' + stdin_file +
                             ': No such file or directory')
                # return PIPE, [], 1
                exit_value = 1
            try:
                open(stdin_file, 'r').close()
            except PermissionError:
                Shell.printf('bash: ' + stdin_file + ': Permission denied')
                # return PIPE, [], 126
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


def run_redirections(args):
    _stdout, args, exit_value = output_redirection(args)
    _stdin, args, exit_value = input_redirection(args)
    return _stdin, _stdout, args, exit_value

