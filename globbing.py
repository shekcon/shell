#!/usr/bin/env python3
from fnmatch import fnmatch
from glob import glob
from os import path, listdir

def globbing(pathname):
    dir_name, base_name = path.split(pathname)
    if base_name.startswith("."):
        return handle_superhidden(pathname, dir_name)
    return glob(pathname)


def handle_superhidden(pathname, dir_name):
    match = []
    for f in get_ll_dir(dir_name):
        if fnmatch(path.join(dir_name, f), pathname):
            match.append(path.join(dir_name, f))
    return match


def get_ll_dir(directory):
    if directory:
        return ['.', '..'] + listdir(directory)
    return ['.', '..'] + listdir('.')


def glob_string(string):
    tokens = string.split()
    for i, token in enumerate(tokens):
        if '*' in token or '?' in token:
            tokens[i] = ' '.join(globbing(token))
    return ' '.join(tokens)

# print(globbing('../.*/'))
# print(glob_string('echo *'))
