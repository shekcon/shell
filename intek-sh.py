#!/usr/bin/env python3
from subprocess import Popen, PIPE
from sys import exit as exit_program
from parse_command_shell import Token
from logical_operators import *


def handle_logic_op(string, operator=None):
    '''
    Tasks:
    - First get step need to do from parse command operator
    - Run command and if exit status isn't 0 and operator is 'and' then skip
    - Else exit status is 0 and operator is 'or' then skip
    - After handle command substitution then run exit status of command
    '''
    steps_exec = parse_command_operator(Token(string).split_token())
    output = []
    for command, next_op in steps_exec:
        if is_skip_command(operator) and is_boolean_command(command[0]):
            result = handle_exit_status(command.pop(0), command)
            output.append(result)
        operator = next_op
    return output


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
                print('intek-sh: export: `%s\': '
                      'not a valid identifier\n' % variable)
    else:
        env = builtins_printenv()[1].split('\n')
        result = []
        for line in env:
            result.append('declare -x ' + line.replace('=', '=\"', 1) + '\"')
        output = '\n'.join(result)
    return exit_value, output


def builtins_unset(variables=[]):  # implement unset
    exit_value = 0
    for variable in variables:
        if not check_name(variable):
            exit_value = 1
            print('intek-sh: unset: `%s\': not a valid identifier\n'
                  % variable)
        elif variable in os.environ:
            os.environ.pop(variable)
    return exit_value, ''


def builtins_exit(exit_code):  # implement exit
    print('exit')
    exit_value = 0
    if exit_code:
        if exit_code.isdigit():
            exit_value = int(exit_code)
        else:
            print('intek-sh: exit: ' + exit_code)
    exit_program(exit_value)


def run_execution(command, args):
    global com_sub
    output = []
    try:
        process = Popen([command]+args, stdout=PIPE, stderr=PIPE)
        out, err = process.communicate()  # byte
        process.wait()
        exit_value = process.returncode
        if exit_value:
            message = err.decode()
        if out:
            output.append(out.decode())
            if not com_sub:
                print(out.decode(), end='')
    except PermissionError:
        exit_value = 126
        message = 'intek-sh: %s: Permission denied' % command
    except FileNotFoundError:
        exit_value = 127
        message = 'intek-sh: %s: command not found' % command
    except Exception as e:
        exit_value = 1
        message = str(e)
    if exit_value:
        show_error(message)
    return exit_value, ''.join(output)


def run_builtins(command, args):
    if command == 'cd':
        return builtins_cd(' '.join(args))
    elif command == 'printenv':
        return builtins_printenv(args)
    elif command == 'export':
        return builtins_export(args)
    elif command == 'unset':
        return builtins_unset(args)
    else:
        return builtins_exit(' '.join(args))


def run_utility(command, args):
    paths = os.environ['PATH'].split(':')
    for path in paths:
        realpath = path + '/' + command
        if os.path.exists(realpath):
            return run_execution(realpath, args)
    show_error('intek-sh: %s: command not found' % command)
    return 127, ''


def run_command(command, args=[]):
    global com_sub
    built_ins = ('cd', 'printenv', 'export', 'unset', 'exit')
    if command in built_ins:
        exit_code, output = run_builtins(command, args)
        if not com_sub:
            print(output)
        return exit_code, output
    elif '/' in command:
        return run_execution(command, args)
    elif 'PATH' in os.environ:
        return run_utility(command, args)
    show_error('intek-sh: %s: command not found' % command)
    return 127, ''


def handle_exit_status(command, args):
    exit_value, output = run_command(command, args)
    os.environ['?'] = str(exit_value)
    return output


def show_error(error):
    print(error)


def main():
    global com_sub
    com_sub = False
    os.environ['?'] = '0'
    while True:
        try:
            input_user = input('intek-sh$ ')
            command = input_user.split()[0]
            args = input_user[len(command):].split()
            if command == 'exit':
                break
            handle_logic_op(input_user)
        except IndexError:
            pass
        except EOFError:
            break
    builtins_exit(' '.join(args))


if __name__ == '__main__':
    main()
