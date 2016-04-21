#!/usr/bin/python
import sys
import os
from itertools import zip_longest, product
        
def _match(possible, m=None):
    acts = set() if m else possible
    return acts | set(a for a in possible if m in a)

def matching(possible, m=None):
    new, current = set(), set()
    if m:
        args = m.split('^')
    else:
        args = []
        current.update(possible)
    [(new.add(x[1:]), args.remove(x)) for x in args if x[0] == '_']
    [new.add(x) for x in args if not _match(possible, x)]
    [current.update(_match(possible, x)) for x in args]
    print(new, current)
    return (new, current)

def handle(commands, args=None):
    a = args.pop(0) if args else []
    stdin = None
    if a[0] == '_':
        stdin = sys.stdin.read()
        a = a[1:]
    n_cmds, cmds = matching(commands.keys(), a)
    for com in cmds:
        process = zip_longest(args, commands[com][1], fillvalue='')
        process = map(lambda x: (x[0], x[1][0], x[1][1], x[1][2]), process)
        params = []
        for arg, group, possible, maker in process:
            n, c = matching(possible(), arg)
            if group == 'both':
                pos = n | c
            elif group == 'new':
                pos = n
            elif group == 'current':
                pos = c
            params.append([maker(x) for x in pos])
        for variation in product(*params):
            yield commands[com][0](*variation)

def _file_list(top=None):
    top = '.' if not top else top
    for p, _, fs in os.walk(top):
        for f in fs:
            yield os.path.join(p, f)
        
files = (lambda x: x, [('current', lambda: [x for x in _file_list()], lambda x: x)])
if __name__ == '__main__':
    # example
    data_1 = set('this old man he played dumb he played tic tac'.split())
    data_2 = set('we all have time for our friends but we spend it instead'.split())
    sys.argv.pop(0)
    cmds = {'one': (lambda a, b: (a, b), [('both', lambda: data_1, lambda x: x.upper()),
                                          ('current', lambda: data_2, lambda x: x.upper())]),
            'files': files}
    list(handle(cmds, sys.argv))
