#!/usr/bin/env python3
import os
from subprocess import Popen, PIPE
from sys import exit as exit_program
from parse_command_shell import Token



def handle_logic_op(string, operator=None):
    '''
    Tasks:
    - First get step need to do from parse command operator
    - Run command and if exit status isn't 0 and operator is 'and' then skip
    - Else exit status is 0 and operator is 'or' then skip
    - After handle command substituition then run exit status of command
    '''
    steps_exec = parse_command_operator(Token(string).split_token())
    output = []
    # printf(str(steps_exec))
    for command, next_op in steps_exec:
        if is_skip_command(operator) and is_boolean_command(command[0]):
            result = run_command(command.pop(0), command)
            output.append(result)
        operator = next_op
    return output


def is_boolean_command(command):
    if command == 'false':
        os.environ['?'] = '1'
    elif command == 'true':
        os.environ['?'] = '0'
    else:
        return True
    return False


def is_skip_command(operator):
    if not operator:
        return True
    if operator == '&&':
        return os.environ['?'] == '0'
    return os.environ['?'] != '0'


def parse_command_operator(args):
    '''
    Tasks:
    - Split command and logical operator into list of tuple
    - Inside tuple is command + args and next logical operators after command
    - Return list of step need to do logical operators
    '''
    steps = []
    commands = args + [" "]
    start = 0
    for i, com in enumerate(commands):
        if com == '||' or com == "&&" or com == ' ':
            steps.append((commands[start: i], commands[i]))
            start = i + 1
    return steps


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


def run_command(command, whatever=[]):
    output = []
    builtins = ('cd', 'printenv', 'export', 'unset')
    if command in builtins:
        if command == 'cd':
            return builtins_cd(' '.join(whatever))
        elif command == 'printenv':
            return builtins_printenv(' '.join(whatever))
        elif command == 'export':
            return builtins_export(' '.join(whatever))
        elif command == 'unset':
            return builtins_unset(' '.join(whatever))
    if '/' in command:
        try:
            process = Popen([command]+whatever, stdout=PIPE, stderr=PIPE)
            out, err = process.communicate()  # byte
            process.wait()
            if err:
                output.append(err.decode())
            if out:
                output.append(out.decode())
        except PermissionError:
            output.append('intek-sh: %s: Permission denied\n' % command)
        except FileNotFoundError:
            output.append('intek-sh: %s: command not found\n' % command)
    elif 'PATH' in os.environ:
        paths = os.environ['PATH'].split(':')
        not_found = True
        for path in paths:
            realpath = path + '/' + command
            if os.path.exists(realpath):
                not_found = False
                process = Popen([realpath]+whatever, stdout=PIPE, stderr=PIPE)
                out, err = process.communicate()  # byte
                process.wait()
                if err:
                    output.append(err.decode())
                if out:
                    output.append(out.decode())
                break
        if not_found:
            output.append('intek-sh: %s: command not found\n' % command)
    else:
        output.append('intek-sh: %s: command not found\n' % command)
    return '\n'.join(output)


def main():
    while True:
        try:
            input_user = input('intek-sh$ ')
            command = input_user.split()[0]
            args = input_user[len(command):].split()
            if command == 'exit':
                break
            print(handle_logic_op(command, args), end='')
        except IndexError:
            pass
        except EOFError:
            break
    builtins_exit(' '.join(args))


if __name__ == '__main__':
    main()
