import curses
import os
#from completion import handle_completion, get_suggest

global window
window = curses.initscr()


def write_file(content):
    with open('debug', 'w') as f:
        f.write(str(content))


class Shell:

    PROMPT = 'intek-sh$ '
    HISTORY_STACK = []
    STACK_CURRENT_INDEX = 0
    WIDTH, HEIGHT = (0, 0)
    CURSES_KEYS = [curses.KEY_LEFT, curses.KEY_RESIZE, curses.KEY_RIGHT,
                   curses.KEY_BACKSPACE, curses.KEY_DC, curses.KEY_UP, curses.KEY_DOWN]

    def __init__(self):
        self._set_up_curses()
        self._set_up_window()
        self._set_up_vars()
        self._update_winsize()

    def _set_up_window(self):
        window.keypad(True)
        window.scrollok(True)

    def _set_up_curses(self):
        #global window
        #window = curses.initscr()
        curses.noecho()

    def _set_up_vars(self):
        """
        - winlog : store the content is displayed on the window
        - mrk_end: mark the endline
        - last_key: store the last single input key
        - input : store the current input line 
        """
        Shell.windowlog = 'windowlog'
        open(Shell.windowlog, 'w').close()
        Shell.historylog = 'history'
        open(Shell.historylog, 'w').close()
        Shell.newline_mark = '@'
        Shell.last_key = ''
        Shell.input = ''
        Shell.go_to_end = False
        Shell.go_to_home = False
        Shell.can_break = False
        Shell.restore = False

    def _update_winsize(self):
        Shell.HEIGHT, Shell.WIDTH = window.getmaxyx()

    ##########################################################################
    @classmethod
    def read_log(Shell):
        return open(Shell.windowlog, 'r').read().replace(Shell.newline_mark, '')

    @classmethod
    def write_log(Shell, overwrite_last_data=False, new='', end='', mode='w'):
        pos = Shell.cursor_pos()
        last_data = ""
        if overwrite_last_data:
            last_data = overwrite_last_data
        if mode == 'w':
            open(Shell.windowlog, mode).write(last_data+new+end)
        else:
            open(Shell.windowlog, mode).write(new+end)
        Shell.move(pos[0], pos[1])

    @classmethod
    def cursor_pos(Shell):
        pos = curses.getsyx()
        return pos[0], pos[1]

    @classmethod
    def getch(Shell, append_log=False, prompt=True, restore=False):
        """ get a character from input """
        pos = Shell.cursor_pos()
        if prompt:
            if not restore:
                Shell.add_str(pos[0], 0, Shell.PROMPT)
            else:
                Shell.add_str(pos[0], 0, Shell.PROMPT + restore)
                window.refresh()
        if append_log:
            Shell.write_log(Shell.PROMPT, end='', mode='a')

        return chr(window.getch())

    @classmethod
    def add_str(Shell, y, x, string):
        """ add string with refresh window """
        window.addstr(y, x, string)
        window.refresh()

    @classmethod
    def printf(Shell, string="", end='\n'):
        """ interpreted python print function to work with curses """
        pos = Shell.cursor_pos()
        if string.endswith('\n'):
            Shell.add_str(pos[0], pos[1], string)
            # Shell.write_log(new='@'+string, mode='a')
        else:
            Shell.add_str(pos[0], pos[1], string+end)
            # Shell.write_log(new='@'+string+end, mode='a')

    @classmethod
    def move(Shell, y, x, refresh=True):
        window.refresh()
        if x < Shell.WIDTH and x >= 0:
            window.move(y, x)
        else:
            if x > 0:
                if y+1 < Shell.HEIGHT:
                    window.move(y+1, 0)
                else:
                    window.move(y, 0)
            else:
                window.move(y-1, Shell.WIDTH-1)

    @classmethod
    def count_lines(Shell, string):
        """ return number of line the string can takk place based on window width """
        return (len(string) + len(Shell.PROMPT)) // Shell.WIDTH + 1

    @classmethod
    def del_nlines(Shell, n=1, startl=False, revese=True):
        """
        - Delete n lines in curses
        - if "startl" not given: base on current curs position
        - "reverse" to delete upward (bottom to top) and so on
        """
        pos = curses.getsyx()
        if not startl:
            window.move(pos[0], Shell.WIDTH-1)
        else:
            window.move(startl, Shell.WIDTH-1)

        for i in range(n):
            window.deleteln()
            if i != n-1:
                pos = curses.getsyx()
                if revese:
                    Shell.move(pos[0]-1, Shell.WIDTH-1)
                else:
                    Shell.move(pos[0]+1, Shell.WIDTH-1)

    @classmethod
    def read_nlines(Shell, startl, n=1, reverse=False):
        pos = Shell.cursor_pos()
        content = ''
        if not reverse:
            for col in range(startl, startl+n):
                content += window.instr(col, 0).decode().strip()
        else:
            for col in range(startl-n+1, startl+1):
                content += window.instr(col, 0).decode().strip()
        Shell.move(pos[0], pos[1])
        return content

    @classmethod
    def move_relative(Shell, start_pos, offset=0):
        step = start_pos[0]*Shell.WIDTH + start_pos[1] + offset
        Shell.move(step // Shell.WIDTH, step % Shell.WIDTH)

    @classmethod
    def step(Shell, y, x, yStart=0, xStart=0):
        """ return int step from (yStart, xStart) to (y, x) """
        return y*Shell.WIDTH + x - yStart*Shell.WIDTH - xStart
