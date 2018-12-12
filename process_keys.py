from vitural_terminal import *
#from completion import handle_completion, get_suggest


def process_KEY_UP(input, curs_pos):
    try:
        if len(Shell.HISTORY_STACK) == 0:
            return input
        if input not in [Shell.HISTORY_STACK[Shell.STACK_CURRENT_INDEX], '\n', '']:
            Shell.HISTORY_STACK.append(input)
            Shell.STACK_CURRENT_INDEX -= 1
        if abs(Shell.STACK_CURRENT_INDEX) != len(Shell.HISTORY_STACK):  # Not meet the start
            Shell.del_nlines(Shell.count_lines(Shell.HISTORY_STACK[Shell.STACK_CURRENT_INDEX]), curs_pos[0], False)
            window.addstr(curs_pos[0], 0, Shell.PROMPT + Shell.HISTORY_STACK[Shell.STACK_CURRENT_INDEX-1])
            input = Shell.HISTORY_STACK[Shell.STACK_CURRENT_INDEX-1]
            Shell.STACK_CURRENT_INDEX -= 1
        else:
            if input is not Shell.HISTORY_STACK[0]:  # EndOfStack
                Shell.del_nlines(Shell.count_lines(Shell.HISTORY_STACK[0]))
                window.addstr(
                    curs_pos[0], 0, Shell.PROMPT + Shell.HISTORY_STACK[0])
                input = Shell.HISTORY_STACK[0]
        return input
    except IndexError:
        pass


def process_KEY_DOWN(input, curs_pos):
        try:
            if len(Shell.HISTORY_STACK) == 0:
                return input
            if input not in [Shell.HISTORY_STACK[Shell.STACK_CURRENT_INDEX], '\n', '']:
                Shell.HISTORY_STACK.append(input)
                Shell.STACK_CURRENT_INDEX += 1
            if Shell.STACK_CURRENT_INDEX != -1:  # Not meet the end of stack
                Shell.del_nlines(Shell.count_lines(
                    Shell.HISTORY_STACK[Shell.STACK_CURRENT_INDEX]))
                # print the previous
                window.addstr(
                    curs_pos[0], 0, Shell.PROMPT + Shell.HISTORY_STACK[Shell.STACK_CURRENT_INDEX+1])
                input = Shell.HISTORY_STACK[Shell.STACK_CURRENT_INDEX+1]
                Shell.STACK_CURRENT_INDEX += 1
            else:
                if input is not Shell.HISTORY_STACK[-1]:  # EndOfStack
                    Shell.del_nlines(
                        Shell.count_lines(Shell.HISTORY_STACK[-1]))
                    window.addstr(
                        curs_pos[0], 0, Shell.PROMPT + Shell.HISTORY_STACK[-1])
                    input = Shell.HISTORY_STACK[-1]
            return input
        except IndexError:
            pass


def process_KEY_LEFT(input, input_pos):
    pos = Shell.cursor_pos()
    if pos[1] > 10 or pos[0] != input_pos[0]:
        if pos[1] - 1 < 0:
            pos = (pos[0] - 1, Shell.WIDTH)
        Shell.move(pos[0], pos[1]-1)
    elif pos[1] == 10:
        Shell.move(pos[0], pos[1])


def process_KEY_RIGHT(input, input_pos):
    pos = Shell.cursor_pos()
    step = pos[0]*Shell.WIDTH + pos[1] + 1
    if step <= input_pos[0]*Shell.WIDTH + input_pos[1] + len(input):
        Shell.move(step // Shell.WIDTH, step % Shell.WIDTH)


def process_KEY_BACKSPACE(input, input_pos):
    pos = Shell.cursor_pos()
    del_loc = pos[0]*Shell.WIDTH + pos[1] - \
        (input_pos[0]*Shell.WIDTH + input_pos[1])
    if del_loc > 0:
        input = input[:del_loc-1] + input[del_loc:]
    Shell.del_nlines(Shell.count_lines(
        input), input_pos[0], revese=False)
    window.addstr(input_pos[0], 0, Shell.PROMPT + input)
    if pos[1] > 10 or pos[0] != input_pos[0]:
        Shell.move(pos[0], pos[1]-1)
    elif pos[1] == 10:
        Shell.move(pos[0], pos[1])
    return input

def process_KEY_TAB(input, input_pos):
    """
    if Shell.last_key in ['TAB', 'TAB2']:  # second TAB
        data = ''
        if input.endswith(' '):
            data = "\n".join(get_suggest("", 'file'))
        else:
            data = "\n".join(get_suggest(input.strip(), 'command'))
        if len(data):
            Shell.printf('\n'+data)
            Shell.last_key = 'TAB2'
    else:
        if input != handle_completion(input, 'command'):
            input = handle_completion(input, 'command')
        Shell.last_key = 'TAB'
    """
    window.addstr(input_pos[0], 10, input)
    window.refresh()


def process_KEY_DELETE(input, input_pos):
    pos = Shell.cursor_pos()
    del_loc = pos[0]*Shell.WIDTH + pos[1] - \
        (input_pos[0]*Shell.WIDTH + input_pos[1]) + 1
    if del_loc > 0:
        input = input[:del_loc-1] + input[del_loc:]
    Shell.del_nlines(Shell.count_lines(
        input), input_pos[0], revese=False)
    window.addstr(input_pos[0], 0, Shell.PROMPT + input)
    Shell.move(pos[0], pos[1])
    return input



def process_KEY_RESIZE(input, input_pos):
    window.clear()
    window.refresh()
    data = Shell.read_log()
    window.addstr(0, 0, data)
    window.refresh()
    Shell.HEIGHT, Shell.WIDTH = window.getmaxyx()
    pos = Shell.read_log()
    step = pos[0]*Shell.WIDTH + pos[1]
    loc_step = step - len(input)
    input_pos = loc_step//Shell.WIDTH, loc_step % Shell.WIDTH
    #window.move(input_pos[0] + lens//self.width, (step + lens) % self.width)


def process_insert_mode(input, input_pos, char):
    pos = Shell.cursor_pos()
    insert_loc = pos[0]*Shell.WIDTH + pos[1] - \
        (input_pos[0]*Shell.WIDTH + input_pos[1])
    input = input[:insert_loc] + char + input[insert_loc:]
    window.addstr(input_pos[0], 10, input)
    #Shell.move(pos[0], pos[1]+1)
    curses.setsyx(pos[0], pos[1]+1)
    curses.doupdate()
    return input


def process_input():
    char = Shell.getch(Shell.PROMPT)
    input = ""  # inittial input

    input_pos = Shell.cursor_pos()
    last_data = Shell.read_log()
    while char not in ['\n']:
        ######################### KEY process ####################################
        """
            This block's purposes are handling special KEYS
            Add feature on this block
        """
        if ord(char) == curses.KEY_RESIZE:
            process_KEY_RESIZE(input, input_pos)
            char = ''

        elif char == chr(curses.KEY_UP):
            Shell.last_key = char
            input = process_KEY_UP(input, input_pos)
            char = ''

        elif char == chr(curses.KEY_DOWN):
            Shell.last_key = char
            input = process_KEY_DOWN(input, input_pos)
            char = ''

        elif char == chr(curses.KEY_LEFT):
            Shell.last_key = char
            process_KEY_LEFT(input, input_pos)
            char = ''

        elif char == chr(curses.KEY_RIGHT):
            Shell.last_key = char
            process_KEY_RIGHT(input, input_pos)
            char = ''

        elif char == chr(curses.KEY_BACKSPACE):  # curses.BACKSPACE
            Shell.last_key = ''
            input = process_KEY_BACKSPACE(input, input_pos)
            char = ''

        elif ord(char) == 9:  # curses.TAB
            process_KEY_TAB(input, input_pos)
            char = ''

        elif char == chr(curses.KEY_DC):
            input = process_KEY_DELETE(input, input_pos)
            char = ''

        ##############################################################################################
        # Insert mode
        if char != '':
            input = process_insert_mode(input, input_pos, char)


        Shell.write_log(overwrite_last_data=last_data, new=Shell.read_nlines(startl=input_pos[0], n = Shell.count_lines(input)), end='', mode='w')
        char = chr(window.getch())

    if Shell.last_key not in['TAB2']:
        step = input_pos[0]*Shell.WIDTH + input_pos[1] + len(input)
        window.move(step // Shell.WIDTH, step % Shell.WIDTH)
        #Shell.write_log(new='\n',mode='a')

    if input not in ['\n', '']:
        Shell.HISTORY_STACK.append(input)
        Shell.STACK_CURRENT_INDEX = 0

    if Shell.last_key in ['TAB2']:
        char = Shell.getch(Shell.PROMPT)
        input = ""
    else:
        window.addstr("\n")
    window.refresh()
    return input


if __name__ == '__main__':
    shell = Shell()
    while True:
        input = process_input()
        if input == 'exit':
            break
    curses.endwin()
