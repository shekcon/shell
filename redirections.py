#!/usr/bin/env python3
import os
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
                return PIPE, []
        elif args[i] in ('>', '1>'):
            stdout_file = args[i+1]
            try:
                open(stdout_file, 'w+').close()
                mode = 'w+'
            except PermissionError:
                Shell.printf('bash: ' + stdout_file + ': Permission denied')
                return PIPE, []
        # elif args[i] in ('2>>'):
        #     stderr_file = args[i+1]
        #     open(stderr_file, 'a+').close()
        # elif args[i] in ('2>'):
        #     stderr_file = args[i+1]
        #     open(stderr_file, 'w+').close()
        else:
            other_args.append(args[i])
            i -= 1
        i += 2

    if mode:
        return open(stdout_file, mode), other_args
    else:
        return PIPE, other_args


def input_redirection(args):
    stdin_file = ''
    other_args = []
    i = 0
    while i < len(args):
        if args[i] in ('<'):
            stdin_file = args[i+1]
            if not path.isfile(stdin_file):
                Shell.printf('bash: ' + stdin_file +
                             ': No such file or directory')
                os.environ['?'] = '1'
                return PIPE, []
            try:
                open(stdin_file, 'r').close()
            except PermissionError:
                Shell.printf('bash: ' + stdin_file + ': Permission denied')
                return PIPE, []
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
        return open(stdin_file, 'r'), other_args
    else:
        return PIPE, other_args


def run_redirections(args):
    _stdout, args = output_redirection(args)
    _stdin, args = input_redirection(args)
    return _stdin, _stdout, args

