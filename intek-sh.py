#!/usr/bin/env python3
import os
from subprocess import Popen, PIPE
from sys import exit as exit_program
from globbing import glob_string


def builtins_cd(directory=''):  # implement cd
    if directory:
        try:
            os.environ['OLDPWD'] = os.getcwd()
            os.chdir(directory)  # change working directory
            os.environ['PWD'] = os.getcwd()
            exit_value, output = 0, ''
        except FileNotFoundError:
            exit_value, output = 1, 'intek-sh: cd: %s: No ' \
                'such file or directory\n' % directory
    else:  # if variable directory is empty, change working dir into homepath
        if 'HOME' not in os.environ:
            exit_value, output = 1, 'intek-sh: cd: HOME not set'
        else:
            os.environ['OLDPWD'] = os.getcwd()
            homepath = os.environ['HOME']
            os.chdir(homepath)
            os.environ['PWD'] = os.getcwd()
            exit_value, output = 0, ''
    return exit_value, output


def builtins_printenv(variables=[]):  # implement printenv
    exit_value = 0
    output_lines = []
    if variables:
        for variable in variables:
            if variable in os.environ:
                output_lines.append(os.environ[variable])
            else:
                exit_value = 1
    else:  # if variable is empty, print all envs
        for key, value in os.environ.items():
            output_lines.append(key + '=' + value)
    return exit_value, '\n'.join(output_lines)


def check_name(name):
    # check if name is a valid identifier or not
    if not name or name[0].isdigit():
        return False
    for char in name:
        if not (char.isalnum() or char is '_'):
            return False
    return True


def builtins_export(variables=[]):  # implement export
    exit_value = 0
    if variables:
        errors = []
        for variable in variables:
            if '=' in variable:
                name, value = variable.split('=', 1)
            else:  # if variable stands alone, set its value as ''
                name = variable
                value = ''
            if check_name(name):
                os.environ[name] = value
            else:
                exit_value = 1
                errors.append('intek-sh: export: `%s\': '
                              'not a valid identifier\n' % variable)
        output = '\n'.join(errors)
    else:
        env = builtins_printenv()[1].split('\n')
        result = []
        for line in env:
            result.append('declare -x ' + line.replace('=', '=\"', 1) + '\"')
        output = '\n'.join(result)
    return exit_value, output


def builtins_unset(variables=[]):  # implement unset
    exit_value = 0
    errors = []
    for variable in variables:
        if not check_name(variable):
            exit_value = 1
            errors.append('intek-sh: unset: `%s\': not a valid identifier\n'
                          % variable)
        elif variable in os.environ:
            os.environ.pop(variable)
    return exit_value, '\n'.join(errors)


def builtins_exit(exit_code):  # implement exit
    print('exit')
    exit_value = 0
    if exit_code:
        if exit_code.isdigit():
            exit_value = int(exit_code)
        else:
            print('intek-sh: exit: ' + exit_code)
    exit_program(exit_value)


def run_executions(command, args):
    output = []
    try:
        process = Popen([command]+args, stdout=PIPE, stderr=PIPE)
        out, err = process.communicate()  # byte
        process.wait()
        exit_value = process.returncode
        if err:
            output.append(err.decode())
        if out:
            output.append(out.decode())
    except PermissionError:
        exit_value = 126
        output.append('intek-sh: %s: Permission denied\n' % command)
    except FileNotFoundError:
        exit_value = 127
        output.append('intek-sh: %s: command not found\n' % command)
    except OSError:
        exit_value = 127
        output.append("intek-sh: %s: cannot execute binary file\n" % command)
    return exit_value, '\n'.join(output)


def run_command(command, args=[]):
    if command == 'cd':
        return builtins_cd(' '.join(args))
    elif command == 'printenv':
        return builtins_printenv(args)
    elif command == 'export':
        return builtins_export(args)
    elif command == 'unset':
        return builtins_unset(args)
    elif command == 'exit':
        return builtins_exit(' '.join(args))
    elif '/' in command:
        return run_executions(command, args)
    elif 'PATH' in os.environ:
        paths = os.environ['PATH'].split(':')
        for path in paths:
            realpath = path + '/' + command
            if os.path.exists(realpath):
                return run_executions(realpath, args)
    return 127, 'intek-sh: %s: command not found\n' % command


def handle_exit_status(string):
    if '*' in string or '?' in string:
        string = glob_string(string)
    command = string.split()[0]
    args = string[len(command):].split()
    exit_value, output = run_command(command, args)
    os.environ['?'] = str(exit_value)
    return output


def main():
    while True:
        try:
            input_user = input('intek-sh$ ')
            print(handle_exit_status(input_user), end='')
        except IndexError:
            pass
        except EOFError:
            break


if __name__ == '__main__':
    main()
