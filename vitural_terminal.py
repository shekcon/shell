import curses
from os.path import expanduser

global window
window = curses.initscr()


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
        self._init_history()

    def _set_up_window(self):
        window.keypad(True)
        window.scrollok(True)

    def _set_up_curses(self):
        curses.noecho()

    def _set_up_vars(self):
        """
        - winlog : store the content is displayed on the window
        - mrk_end: mark the endline
        - last_key: store the last single input key
        - input : store the current input line 
        """
        Shell.windowlog = '/'.join([expanduser('~'), 'windowlog'])
        open(Shell.windowlog, 'w').close()
        Shell.historylog = '/'.join([expanduser('~'), 'history'])
        open(Shell.historylog, 'a+').close()
        Shell.newline_mark = '@'
        Shell.last_key = ''
        Shell.input = ''
        Shell.can_break = False
        Shell.restore = False

    def _update_winsize(self):
        Shell.HEIGHT, Shell.WIDTH = window.getmaxyx()

    def _init_history(self):
        with open(Shell.historylog, 'r') as f:
            for line in f:
                Shell.HISTORY_STACK.append(line.strip())
        return

    ##########################################################################

    @classmethod
    def read_log(Shell):
        data = []
        with open(Shell.windowlog, 'r') as f:
            for line in f:
                data.append(line)
        if len(data) > Shell.HEIGHT:
            data = data[-Shell.HEIGHT:]
            with open(Shell.windowlog, 'w') as f:
                f.write(''.join(data).replace(Shell.newline_mark, ''))
        return ''.join(data).replace(Shell.newline_mark, '')

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

    @classmethod
    def cursor_pos(Shell):
        pos = curses.getsyx()
        return pos[0], pos[1]

    @classmethod
    def getch(Shell, append_log=True, prompt=True, restore=False):
        """ get a character from input """
        pos = Shell.cursor_pos()
        data = Shell.PROMPT
        if restore:
            data = Shell.PROMPT + restore
        if prompt:
            Shell.add_str(pos[0], 0, data)

        if append_log:
            Shell.write_log(new=data, end='', mode='a')

        return chr(window.getch())

    @classmethod
    def add_str(Shell, y, x, string):
        """ add string with refresh window """
        window.addstr(y, x, string)
        window.refresh()

    @classmethod
    def printf(Shell, string="", end='\n', pretty=False, write_log=True):
        """ interpreted python print function to work with curses """
        pos = Shell.cursor_pos()
        if string.endswith('\n'):
            Shell.add_str(pos[0], pos[1], string)
            if write_log:
                Shell.write_log(new='@'+string, mode='a')
        else:
            Shell.add_str(pos[0], pos[1], string+end)
            if write_log:
                Shell.write_log(new='@'+string+end, mode='a')

    @classmethod
    def move(Shell, y, x, refresh=True):
        window.refresh()
        if x < Shell.WIDTH and x >= 0:
            curses.setsyx(y, x)
        else:
            if x > 0:
                if y+1 < Shell.HEIGHT:
                    curses.setsyx(y+1, 0)
                else:
                    curses.setsyx(y, 0)
            else:
                curses.setsyx(y-1, Shell.WIDTH-1)
        curses.doupdate()

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
        """ read number of lines from current window """
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

    @classmethod
    def display_history(Shell, index=False):
        if not index:
            for i in range(len(Shell.HISTORY_STACK)):
                Shell.printf("{:3d}".format(i)+'  ' +
                             str(Shell.HISTORY_STACK[i]))
        else:
            Shell.HISTORY_STACK.pop()
            Shell.STACK_CURRENT_INDEX = 0
            Shell.printf(Shell.HISTORY_STACK[index])
            return 0, Shell.HISTORY_STACK[index]

    @classmethod
    def save_history(Shell):
        with open(Shell.historylog, 'a') as f:
            f.write('\n'.join(Shell.HISTORY_STACK))
        return

    @classmethod
    def clear(Shell):
        window.clear()
        window.refresh()
        open(Shell.windowlog, 'w').close()

    @classmethod
    def restore_window(Shell):
        window.clear()
        data = Shell.read_log()
        Shell.add_str(0, 0, data)

    @classmethod
    def get_history(Shell, input_user):
        try:
            if input_user[1] == '!':
                Shell.HISTORY_STACK.pop()
                Shell.printf(Shell.HISTORY_STACK[-1])
                return Shell.HISTORY_STACK[-1]
            else:
                Shell.HISTORY_STACK.pop()
                Shell.printf(Shell.HISTORY_STACK[input_user[1]])
                return Shell.HISTORY_STACK[input_user[1]]
        except IndexError:
            return input_user