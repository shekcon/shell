from pprint import pformat
import re
from completion import (complete_double_tab, complete_tab, get_suggest,
                        handle_completion)
from vitural_terminal import *


def process_history(arg):
    if arg == '!!':
        return Shell.HISTORY_STACK[-1]
    else:
        return Shell.HISTORY_STACK[int(arg[1:])]


def process_KEY_UP(input, curs_pos):
    try:
        if len(Shell.HISTORY_STACK) == 0:
            return input
        if input not in [Shell.HISTORY_STACK[Shell.STACK_CURRENT_INDEX], '\n', '']:
            Shell.HISTORY_STACK.append(input)
            Shell.STACK_CURRENT_INDEX -= 1
        if abs(Shell.STACK_CURRENT_INDEX) != len(Shell.HISTORY_STACK):  # Not meet the start
            Shell.del_nlines(Shell.count_lines(
                Shell.HISTORY_STACK[Shell.STACK_CURRENT_INDEX]), curs_pos[0], False)
            window.addstr(curs_pos[0], 0, Shell.PROMPT +
                          Shell.HISTORY_STACK[Shell.STACK_CURRENT_INDEX-1])
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
            try:
                Shell.HISTORY_STACK[Shell.STACK_CURRENT_INDEX+1]
            except IndexError:
                return input
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
    if Shell.step(pos[0], pos[1]) < Shell.step(input_pos[0], input_pos[1]) + len(input):
        Shell.move(step // Shell.WIDTH, step % Shell.WIDTH)


def process_KEY_BACKSPACE(input, input_pos):
    pos = Shell.cursor_pos()
    del_loc = Shell.step(pos[0], pos[1]) - \
        Shell.step(input_pos[0], input_pos[1])
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
    string = input
    if Shell.last_key in ['TAB', 'TAB2']:  # second TAB
        data = complete_double_tab(input)
        if len(data) and data != input:
            Shell.printf('\n'+pformat(data, Shell.WIDTH))
            Shell.last_key = 'TAB2'
            Shell.can_break = True
            Shell.restore = True
            return input
    else:
        pos = Shell.cursor_pos()
        insert_pos = Shell.step(pos[0], pos[1]) - \
            Shell.step(input_pos[0], input_pos[1])
        string = input[:insert_pos]
        if string != complete_tab(input[:insert_pos]):
            string = complete_tab(input[:insert_pos])
            input = string + input[insert_pos:]
            Shell.write_log(new=input[insert_pos:], end='', mode='a')
        Shell.last_key = 'TAB'
    Shell.add_str(input_pos[0], 10, input)
    step = Shell.step(input_pos[0], input_pos[1]) + len(string)
    Shell.move(step//Shell.WIDTH, step % Shell.WIDTH)
    return input


def process_KEY_DELETE(input, input_pos):
    pos = Shell.cursor_pos()
    del_loc = Shell.step(pos[0], pos[1]) - \
        Shell.step(input_pos[0], input_pos[1]) + 1
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
    Shell.add_str(0, 0, data)
    Shell.HEIGHT, Shell.WIDTH = window.getmaxyx()
    pos = Shell.cursor_pos()
    # Recalculate input position
    loc_step = Shell.step(pos[0], pos[1]) - len(input)
    input_pos = loc_step//Shell.WIDTH, loc_step % Shell.WIDTH
    Shell.move(pos[0], pos[1])
    return input, input_pos


def process_insert_mode(input, input_pos, char, last_data):
    pos = Shell.cursor_pos()
    insert_loc = Shell.step(pos[0], pos[1]) - \
        Shell.step(input_pos[0], input_pos[1])
    if Shell.step(input_pos[0], input_pos[1]) + len(input) == Shell.WIDTH * Shell.HEIGHT:
        insert_loc += Shell.WIDTH

    input = input[:insert_loc] + char + input[insert_loc:]
    if Shell.step(input_pos[0], input_pos[1]) + len(input) > Shell.WIDTH * Shell.HEIGHT:
        input_pos = input_pos[0] - 1, input_pos[1]
    window.addstr(input_pos[0], input_pos[1], input)
    Shell.move(pos[0], pos[1]+1)
    return input, input_pos


def process_input():
    input = ""
    Shell.restore_window()
    last_key = Shell.last_key

    if Shell.restore:
        try:
            input = Shell.HISTORY_STACK[-1]
            char = Shell.getch(Shell.PROMPT, restore=input)
            Shell.restore = False
            input_pos = Shell.cursor_pos()[0], len(Shell.PROMPT)
        except IndexError:
            char = Shell.getch(Shell.PROMPT)
            input_pos = Shell.cursor_pos()

    else:
        char = Shell.getch(Shell.PROMPT)
        input_pos = Shell.cursor_pos()

    last_data = Shell.read_log()
    if last_key == 'TAB2':
        last_data = last_data[:last_data.rfind(Shell.PROMPT)+len(Shell.PROMPT)]
    Shell.can_break = False
    while char not in ['\n']:
        ######################### KEY process ####################################
        """
            This block's purposes are handling special KEYS
        """
        if char == chr(curses.KEY_RESIZE):
            input, input_pos = process_KEY_RESIZE(input, input_pos)
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
        elif char == chr(curses.KEY_END):
            Shell.last_key = char
            Shell.move_relative(input_pos, len(input))
            char = ''

        elif char == chr(curses.KEY_HOME):
            Shell.last_key = char
            Shell.move_relative(input_pos, 0)
            char = ''

        elif char == chr(curses.KEY_BACKSPACE) or ord(char) == 127:  # curses.BACKSPACE
            Shell.last_key = char
            input = process_KEY_BACKSPACE(input, input_pos)
            char = ''

        elif ord(char) == 9:  # curses.TAB
            input = process_KEY_TAB(input, input_pos)
            if Shell.can_break:
                break
            char = ''

        elif char == chr(curses.KEY_DC):
            Shell.last_key = char
            input = process_KEY_DELETE(input, input_pos)
            char = ''

        ##############################################################################################
        # Insert mode
        if char != '':
            Shell.last_key = char
            input, input_pos = process_insert_mode(
                input, input_pos, char, last_data)

        Shell.write_log(last_data, input)
        Shell.restore = False
        char = chr(window.getch())

    _input = input
    if _input not in ['\n', ''] or Shell.can_break is True:
        try:
            if Shell.HISTORY_STACK[-1] != _input:
                Shell.HISTORY_STACK.append(_input)
            Shell.STACK_CURRENT_INDEX = 0
        except IndexError:
            Shell.HISTORY_STACK.append(_input)
            Shell.STACK_CURRENT_INDEX = 0
    ################### retrieve history command ############
    if input.startswith('!'):
        Shell.HISTORY_STACK.pop()
    ls_re = re.split('(!!|!-?\d*)', input)

    if input.startswith('!'):
        Shell.printf('\n'+process_history(input), end='')
    for c in ls_re:
        if '!' in c:
            input = input.replace(c, process_history(c))
    #########################################################
    if Shell.last_key not in['TAB2']:
        step = input_pos[0]*Shell.WIDTH + input_pos[1] + len(input)
        Shell.move(step // Shell.WIDTH, step % Shell.WIDTH)
        Shell.write_log(new='\n', mode='a')

    if not Shell.can_break:
        Shell.last_key = '\n'

    if Shell.last_key in ['TAB2']:
        Shell.printf(Shell.PROMPT, end='', write_log=False)
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
        elif input == 'history':
            Shell.display_history()
        elif input == 'clear':
            Shell.clear()
            pass
    curses.endwin()
