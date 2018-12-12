#!/usr/bin/env python3
from subprocess import Popen, PIPE
from sys import exit as exit_program
from globbing import glob_string
from parse_command_shell import Token
from logical_operators import *
from signal import signal
from signal import SIG_IGN, SIGINT, SIGQUIT, SIGTSTP, signal


def handle_logic_op(string, operator=None):
    '''
    Tasks:
    - First get step need to do from parse command operator
    - Run command and if exit status isn't 0 and operator is 'and' then skip
    - Else exit status is 0 and operator is 'or' then skip
    - After handle command substituition then run exit status of command
    '''
    global sig_now
    steps_exec = parse_command_operator(Token(string, keep_quote=False).split_token())
    output = []
    for command, next_op in steps_exec:
        if is_skip_command(operator) and is_boolean_command(command[0]):
            command = handle_com_substitution(command)
            result = handle_exit_status(command)
            output.append(result)
        operator = next_op
        if sig_now is not None:
            break
    return output


def handle_com_substitution(arguments):
    '''
    Tasks:
    - Checking is command substitution return string between backquote else return origin argument passed
    - If string isn't empty then run handle logical operator to get result of that command
    - If string is empty not need do anthing
    '''
    global sig_now, com_sub
    new_command = []
    for arg in arguments:
        result = check_command_sub(arg)
        if result and result != arg:
            com_sub = True
            valids = [arg for arg in handle_logic_op(result) if arg]
            new_command += [e for arg in valids for e in arg.split('\n')]
            com_sub = False
        elif result:
            new_command.append(arg)
        if sig_now is not None:
            break
    return new_command


def check_command_sub(arg):
    if arg.startswith('`') and arg.endswith('`'):
        return arg[1:-1:].strip()
    if arg.startswith('\\`') and arg.endswith('\\`'):
        return arg[2:-2:].strip()
    return arg


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
                print('intek-sh: export: `%s\': '
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


def run_execution(command, args):
    global process, sig_now, com_sub
    output = []
    try:
        process = Popen([command]+args, stdout=PIPE, stderr=PIPE)
        line = process.stdout.readline().decode()
        while line and sig_now is None:
            if not com_sub:
                print(line.strip())
            output.append(line)
            line = process.stdout.readline().decode()
        if sig_now is None:
            process.wait()
        exit_value = process.returncode
        if exit_value:
            message = process.stderr.read().decode()
    except PermissionError:
        exit_value = 126
        message = 'intek-sh: %s: Permission denied' % command
    except FileNotFoundError:
        exit_value = 127
        message = 'intek-sh: %s: command not found' % command
    except Exception as e:
        message = str(e)
        exit_value = 1
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


def handle_exit_status(args):
    global sig_now
    if sig_now is not None:
        return
    for i, arg in enumerate(args):
        if '*' in arg or '?' in arg:
            args[i] = glob_string(arg)
    command = args.pop(0)
    exit_value, output = run_command(command, args)
    os.environ['?'] = str(exit_value)
    return output

def handle_child_process(sig):
    global process, sig_now
    if process:
        try:
            sig_now = sig
            os.kill(process.pid, sig)
        except ProcessLookupError:
            # printf("error finding process")
            sig_now = None
            return None
        if sig == SIGQUIT:
            return 131
        return 148
    return None


def handle_signal(sig, frame):
    global process
    if sig == SIGINT:
        handle_child_process(sig)
        exit_code = 130
    elif sig == SIGQUIT:
        exit_code = handle_child_process(sig)
    else:
        exit_code = handle_child_process(sig)
    if exit_code is not None:
        os.environ['?'] = str(exit_code)

def show_error(error):
    print(error)


def setup_terminal():
    global process, sig_now, com_sub
    com_sub = False
    process = None
    sig_now = None
    signal(SIGINT, handle_signal)
    signal(SIGTSTP, handle_signal)
    signal(SIGQUIT, handle_signal)

def main():
    global process, sig_now
    setup_terminal()
    while True:
        try:
            input_user = input('intek-sh$ ')
            handle_logic_op(input_user)
            process = None
            sig_now = None
        except IndexError:
            pass
        except EOFError:
            break


if __name__ == '__main__':
    main()
