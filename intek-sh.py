#!/usr/bin/env python3
from signal import SIG_IGN, SIGINT, SIGQUIT, SIGTERM, signal
from subprocess import PIPE, Popen
from sys import exit as exit_program

from globbing import multi_glob
from logical_operators import *
from parse_command_shell import Token
from path_expansions import check_name, path_expansions
from process_keys import Shell, curses, process_input
from quoting import Quote
from redirections import run_redirections


def handle_logic_op(string, operator=None):
    '''
    Tasks:
    - First get step need to do from parse command operator
    - Run command and if exit status isn't 0 and operator is 'and' then skip
    - Else exit status is 0 and operator is 'or' then skip
    - After handle command substitution then run exit status of command
    '''
    global terminate
    steps_exec = parse_command_operator(Token(string).split_token())
    output = []
    for command, next_op in steps_exec:
        if is_skip_command(operator) and is_boolean_command(command[0]):
            if check_subshell(command[0]):
                handle_subshell(command)
            else:
                command = handle_com_substitution(command)
                result = handle_exit_status(command)
                output.append(result)
        operator = next_op
        if terminate:
            return
    return output


def handle_com_substitution(arguments):
    '''
    Tasks:
    - Checking is command substitution return string between backquote else return origin argument passed
    - If string isn't empty then run handle logical operator to get result of that command
    - If string is empty not need do anthing
    '''
    global terminate, com_sub
    new_command = []
    for arg in arguments:
        result = check_command_sub(arg)
        if result and result != arg:
            if check_syntax_shell(result):
                com_sub = True
                valids = [arg for arg in handle_logic_op(result) if arg]
                new_command += [e for arg in valids for e in arg.split('\n')]
                com_sub = False
        elif result:
            new_command.append(arg)
        if terminate:
            return
    return new_command


def handle_subshell(command):
    try:
        pid = os.fork()
    except OSError:
        pass
    if pid == 0:
        handle_logic_op(command[0][1:-1])
        exit_program(int(os.environ['?']))
    exit_code = os.wait()[1]
    os.environ['?'] = str(exit_code)


def check_command_sub(arg):
    if arg.startswith('`') and arg.endswith('`'):
        return arg[1:-1:].strip()
    return arg


def check_subshell(command):
    return command.startswith("(") and command.endswith(")")


def builtins_cd(directory):  # implement cd
    if directory:
        try:
            os.environ['OLDPWD'] = os.getcwd()
            os.chdir(directory)  # change working directory
            os.environ['PWD'] = os.getcwd()
            exit_value = 0
        except FileNotFoundError:
            exit_value, message = 1, 'intek-sh: cd: %s: No ' \
                'such file or directory\n' % directory
    else:  # if variable directory is empty, change working dir into homepath
        if 'HOME' not in os.environ:
            exit_value, message = 1, 'intek-sh: cd: HOME not set'
        else:
            os.environ['OLDPWD'] = os.getcwd()
            homepath = os.environ['HOME']
            os.chdir(homepath)
            os.environ['PWD'] = os.getcwd()
            exit_value = 0
    if exit_value:
        show_error(message)
    return exit_value, ''


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


def builtins_export(variables=[]):  # implement export
    exit_value = 0
    output = []
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
                Shell.printf('intek-sh: export: `%s\': '
                             'not a valid identifier\n' % variable)
    else:
        env = builtins_printenv()[1].split('\n')
        result = []
        for line in env:
            result.append('declare -x ' + line.replace('=', '=\"', 1) + '\"')
        output = '\n'.join(result)
    return exit_value, '\n'.join(output)


def builtins_unset(variables=[]):  # implement unset
    exit_value = 0
    for variable in variables:
        if not check_name(variable):
            exit_value = 1
            Shell.printf('intek-sh: unset: `%s\': not a valid identifier\n'
                         % variable)
        elif variable in os.environ:
            os.environ.pop(variable)
    return exit_value, ''


def builtins_exit(exit_code='0'):  # implement exit
    Shell.save_history()
    Shell.printf('exit')
    exit_value = 0
    if exit_code:
        if exit_code.isdigit():
            exit_value = int(exit_code)
        else:
            Shell.printf('intek-sh: exit: ' + exit_code)
    curses.endwin()
    exit_program(exit_value)


def run_execution(command, args, inp=PIPE, out=PIPE):
    global process
    output = []
    try:
        process = Popen([command]+args, stdin=inp, stdout=out, stderr=PIPE)
        if out == PIPE and inp == PIPE:
            line = process.stdout.readline().decode()
            while line:
                if not com_sub and not in_pipes:
                    Shell.printf(line.strip())
                output.append(line)
                line = process.stdout.readline().decode()
        elif out == PIPE:
            content = process.stdout.read().decode()
            if not com_sub and not in_pipes:
                Shell.printf(content)
            output.append(content)
        for line in process.stderr:
            if line.decode() not in ['', '\n']:
                Shell.printf(line.decode())
        process.wait()
        exit_value = process.returncode
    except PermissionError:
        exit_value = 126
        Shell.printf('intek-sh: %s: Permission denied' % command)
    except FileNotFoundError:
        exit_value = 127
        Shell.printf('intek-sh: %s: command not found' % command)
    except Exception as e:
        exit_value = 1
        Shell.printf(str(e))
    return exit_value, ''.join(output)


def run_builtins(command, args):
    if command == 'cd':
        return builtins_cd(args[0] if args else '')
    elif command == 'printenv':
        return builtins_printenv(args)
    elif command == 'export':
        return builtins_export(args)
    elif command == 'unset':
        return builtins_unset(args)
    elif command == 'history':
        return Shell.display_history()
    elif command == 'clear':
        return Shell.clear()
    else:
        return builtins_exit(args[0] if args else '')


def run_utility(command, args, inp=PIPE, out=PIPE):
    paths = os.environ['PATH'].split(':')
    for path in paths:
        realpath = path + '/' + command
        if os.path.exists(realpath):
            return run_execution(realpath, args, inp=inp, out=out)
    Shell.printf('intek-sh: %s: command not found' % command)
    return 127, ''


def run_command(command, args=[], inp=PIPE, out=PIPE):
    global com_sub
    built_ins = ('cd', 'printenv', 'export', 'unset', 'exit', 'history', 'clear')
    if command in built_ins:
        exit_code, output = run_builtins(command, args)
        if not com_sub and output and not exit_code and not in_pipes:
            Shell.printf(output)
        return exit_code, output
    elif '/' in command:
        return run_execution(command, args, inp=inp, out=out)
    elif 'PATH' in os.environ:
        return run_utility(command, args, inp=inp, out=out)
    Shell.printf('intek-sh: %s: command not found' % command)
    return 127, ''


def parse_pipes(args):
    pipes = []
    while '|' in args:
        index = args.index('|')
        pipes.append(args[:index])
        args = args[index+1:]
    pipes.append(args)
    return pipes


def run_pipes(args):
    global in_pipes
    output = ''
    exit_value = 0
    pipes = parse_pipes(args)
    for pipe in pipes:
        if pipe is not pipes[-1]:
            in_pipes = True
        else:
            in_pipes = False
        inp, out, others, exit_value = run_redirections(pipe, in_pipes)
        if inp == PIPE and os.path.exists('.output_last_pipe'):
            inp = open('.output_last_pipe', 'r')
        handle_quotes(args)
        command = others.pop(0)
        exit_value, output = run_command(command, others, inp, out)
        if output:
            with open('.output_last_pipe', 'w+') as f:
                f.write(output)
                f.close()
        elif output and os.path.exists('.output_last_pipe'):
            os.remove('.output_last_pipe')
    return output, exit_value


def handle_exit_status(args):
    global terminate, in_pipes
    if terminate and args:
        return

    # path expansions
    exit_value, args = path_expansions(args)
    if exit_value:
        os.environ['?'] = str(exit_value)
        Shell.printf(args)
        terminate = True
        return ''

    # globbing
    args = multi_glob(args)

    # run pipes and redirections
    if '|' in args:
        run_redirections(args, in_pipes)
        output, exit_value = run_pipes(args)
    else:
        # redirections
        inp, out, args, exit_value = run_redirections(args, in_pipes)
        handle_quotes(args)
        command = args.pop(0)
        exit_value, output = run_command(command, args, inp=inp, out=out)

    in_pipes = False
    # exit status
    os.environ['?'] = str(exit_value)
    return output


def handle_quotes(args):
    for i in range(len(args)):
        args[i] = Quote(args[i]).remove_quote()


def check_syntax_shell(string):
    parse = Token(string)
    parse.split_token()
    message = parse.check_syntax()
    if message:
        show_error(message)
        os.environ['?'] = '1'
        return False
    return True


def handle_signal(sig, frame):
    global process, terminate
    Shell.printf("^C")
    terminate = False
    if process:
        try:
            os.kill(process.pid, sig)
            terminate = True
        except ProcessLookupError:
            pass
    os.environ['?'] = '130'


def show_error(error):
    if error:
        Shell.printf(error)


def setup_terminal():
    global terminate
    terminate = False
    os.environ['?'] = '0'
    reset_terminal()
    signal(SIGINT, handle_signal)
    signal(SIGTERM, SIG_IGN)
    signal(SIGQUIT, SIG_IGN)
    Shell()


def reset_terminal():
    global process, terminate, com_sub, in_pipes
    if terminate:
        os.environ['?'] = '130'
    in_pipes = False
    com_sub = False
    process = None
    terminate = False


def main():
    setup_terminal()
    while True:
        try:
            input_user = process_input()
            if check_syntax_shell(input_user):
                handle_logic_op(input_user)
        except IndexError:
            pass
        except EOFError:
            break
        except TypeError:
            # when terminate is True
            pass
        except ValueError:
            # outrange chr()
            pass
        except Exception as e:
            Shell.printf(str(e))
        reset_terminal()
    builtins_exit()


if __name__ == '__main__':
    main()
