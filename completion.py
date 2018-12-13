import os


def get_all_commands():
    '''
    Task: + Get all command from path environment
    '''
    commands = []
    for path in os.environ['PATH'].split(':'):
        if os.path.exists(path):
            commands += os.listdir(path)
    return commands


def get_all_files(path):
    '''
    Task: + Get all file or directory at head of path passed
    '''
    head, _ = os.path.split(path)
    if head:
        return [os.path.join(head, p)  for p in os.listdir(head)]
    return os.listdir('.')


def get_suggest(txt, mode):
    '''
    Task: + Find all suggest from text passed at the mode
          + One is command
          + Two is file or directory at that directory
    '''
    if mode == 'command':
        valids = get_all_commands()
    else:
        valids = get_all_files(txt)
    if not txt:
        return valids
    return [i for i in valids if i.startswith(txt)]


def is_possible_completion(suggests, text):
    '''
    Task: + That is any suggest same text passed
    Return: Boolean
    '''
    return min(suggests, key=lambda o: len(o)) != text


def find_common_suggest(suggests, txt):
    '''
    Task: + Let max length command is key
          + Increase index from length of text passed
          + If some suggest not same then return right away
    '''
    index = len(txt)
    max_command = max(suggests).lower()
    while index < len(max_command):
        for e in suggests:
            if not e.lower().startswith(max_command[:index + 1]):
                return max_command[: index]
        index += 1
    return txt


def handle_completion(text, mode):
    '''
    Tasks: + Find all suggest from text passed at that mode
           + Find common from that list of suggest
           + Then return it
    '''
    list_suggest = get_suggest(text, mode=mode)
    if len(list_suggest) == 1:
        return list_suggest[0]
    elif list_suggest and is_possible_completion(list_suggest, text):
        return find_common_suggest(list_suggest, text)
    return text


if __name__ == '__main__':
    print(get_suggest('cat', mode='file'))