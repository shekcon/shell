#!/usr/bin/env python3
import os
from subprocess import Popen, PIPE
from sys import exit as exit_program


def builtins_cd(directory=''):  # implement cd
    if directory:
        try:
            os.environ['OLDPWD'] = os.getcwd()
            os.chdir(directory)  # change working directory
            os.environ['PWD'] = os.getcwd()
            output = ''
        except FileNotFoundError:
            output = ('intek-sh: cd: %s: No such file or directory\n'
                      % (directory))
    else:  # if variable directory is empty, change working dir into homepath
        if 'HOME' not in os.environ:
            output = 'intek-sh: cd: HOME not set'
        else:
            os.environ['OLDPWD'] = os.getcwd()
            homepath = os.environ['HOME']
            os.chdir(homepath)
            os.environ['PWD'] = os.getcwd()
            output = ''
    return output


def builtins_printenv(variables=''):  # implement printenv
    output_lines = []
    if variables:
        for variable in variables.split():
            if variable in os.environ:
                output_lines.append(os.environ[variable])
    else:  # if variable is empty, print all envs
        for key, value in os.environ.items():
            output_lines.append(key + '=' + value)
    return '\n'.join(output_lines)


def check_name(name):
    # check if name is a valid identifier or not
    if not name or name[0].isdigit():
        return False
    for char in name:
        if not (char.isalnum() or char is '_'):
            return False
    return True


def builtins_export(variables=''):  # implement export
    if variables:
        errors = []
        for variable in variables.split():
            if '=' in variable:
                name, value = variable.split('=', 1)
            else:  # if variable stands alone, set its value as ''
                name = variable
                value = ''
            if check_name(name):
                os.environ[name] = value
            else:
                errors.append('intek-sh: export: `%s\': '
                              'not a valid identifier\n' % variable)
        output = '\n'.join(errors)
    else:
        env = builtins_printenv()[1].split('\n')
        result = []
        for line in env:
            result.append('declare -x ' + line.replace('=', '=\"', 1) + '\"')
        output = '\n'.join(result)
    return output


def builtins_unset(variables=''):  # implement unset
    errors = []
    for variable in variables.split():
        if not check_name(variable):
            errors.append('intek-sh: unset: `%s\': not a valid identifier\n'
                          % variable)
        elif variable in os.environ:
            os.environ.pop(variable)
    return '\n'.join(errors)


def builtins_exit(exit_code):  # implement exit
    exit_value = 0
    print('exit')
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
        output.append('intek-sh: %s: Permission denied\n' % command)
    except FileNotFoundError:
        output.append('intek-sh: %s: command not found\n' % command)
    return '\n'.join(output)


def run_command(command, args=[]):
    if command == 'cd':
        return builtins_cd(' '.join(args))
    elif command == 'printenv':
        return builtins_printenv(''.join(args))
    elif command == 'export':
        return builtins_export(''.join(args))
    elif command == 'unset':
        return builtins_unset(''.join(args))
    elif '/' in command:
        return run_executions(command, args)
    elif 'PATH' in os.environ:
        paths = os.environ['PATH'].split(':')
        for path in paths:
            realpath = path + '/' + command
            if os.path.exists(realpath):
                return run_executions(realpath, args)
    return 'intek-sh: %s: command not found\n' % command


def main():
    while True:
        try:
            input_user = input('intek-sh$ ')
            command = input_user.split()[0]
            args = input_user[len(command):].split()
            if command == 'exit':
                break
            print(run_command(command, args), end='')
        except IndexError:
            pass
        except EOFError:
            break
    builtins_exit(' '.join(args))


if __name__ == '__main__':
    main()
