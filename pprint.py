
def pformat(content, width):
    """ return string fit pretty printing style """
    ls = content.split('\n')
    max_len = len(max(ls, key=lambda s: len(s)))
    ncols = width // max_len
    nrows = len(ls) // ncols
    block_width = width // ncols + 1
    string = ''
    for i in range(len(ls)):
        if not (i+1) % ncols:
            if not ls[i].endswith('\n'):
                string += ls[i] + '\n'
        else:
            string += ls[i] + (block_width-len(ls[i])) * ' '
    return string
