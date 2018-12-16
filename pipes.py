#!/usr/bin/env python3
def parse_pipes(args):
    pipes = []

    while '|' in args:
        index = args.index('|')
        pipes.append(args[:index])
        args = args[index+1:]

    return pipes