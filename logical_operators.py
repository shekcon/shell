import os


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