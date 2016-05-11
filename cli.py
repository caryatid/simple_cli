#!/usr/bin/python
import sys
import os
from itertools import zip_longest, product, repeat, chain
from collections import defaultdict
        
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
    [new.add(x) for x in args if not _match(possible, x)]
    [current.update(_match(possible, x)) for x in args]
    return (new, current)

def _make_parameters(products):
    params = []
    for arg, group, possible, maker in products:
        if arg and arg[0] == '+':
            arg = arg[1:]
            n, c = matching(_stdin_list(), arg)
        elif arg and arg[0] == '.':
            arg = arg[1:]
            n, c = matching(files_comps(), arg)
        elif arg and arg[0] == ',':
            arg = arg[1:]
            n = set(arg.split(','))
            c = n
        else:
            n, c = matching(possible(params), arg)
        if 'current' in group:
            pos = c
        elif 'new' in group:
            pos = n
        else:
            pos = n | c
        if '1' in group:
            if not arg:
                pos = set()
            else:
                pos = sorted(pos, key=len)[:1]
        params.append([y for y in [maker(x) for x in pos] if y])
    return [x for x in params if x]

def _expand_arguments(args, arg_h):
    procs = map(lambda y: (y[0], y[1][0], y[1][1], y[1][2]),
                zip_longest(args, arg_h, fillvalue=''))
    prod, app, split = (list(), list(), False)
    for x in procs:
        if x[1][0] == '|':
            split = True
            continue
        if split:
            app.append(x)
        else:
            prod.append(x)
    a = product(*_make_parameters(prod))
    b = zip(a, repeat(sorted(_make_parameters(app), key=len)))
    return map(lambda x: list(chain(*x)), b)


def handle(commands, args=None):
    a = args.pop(0) if args else ''
    dry = False
    if a and a.startswith('_'):
        a = a[1:]
        dry = True
    _, cmds = matching(commands.keys(), a)
    if len(cmds) == 0:
        args = []
        if 'help' not in commands:
            commands.update({'help': (lambda : 'available commands:\n' +
                                      '\n'.join(commands.keys()), [])})
        cmds = set(['help'])
    com_name = sorted(cmds, key=lambda x: len(x))[0]
    if dry:
        cmd = lambda *x: list(map(str, x))
    else:
        cmd = commands[com_name][0]
    arg_h = commands[com_name][1]
    for variation in _expand_arguments(args, arg_h):
        yield cmd(*variation)

def t_to_d(ts):
    ts = list(ts)
    if not ts or not isinstance(ts[0], list):
        return {'return': ts}
    # takes list of tuples all of same length.
    # returns dictionary
    # determine if mappend or assign final value
    l = ['.'.join(map(str, x[:-1])) for x in ts]
    s = set(l)
    assign = True
    if len(l) > len(s):
        assign = False
    d = {}
    for t in ts:
        _d = d
        k = t.pop(0)
        while t:
            _k = t.pop(0)
            if not t:
                if assign:
                    _d[k] = _k
                else:
                    _d.setdefault(k, list())
                    _d[k].append(_k)
            else:
                _d.setdefault(k, {})
                _d = _d[k]
                k = _k
    return d
            
def _file_list(top=None):
    top = '.' if not top else top
    for p, _, fs in os.walk(top):
        for f in fs:
            yield os.path.join(p, f)
        

def _stdin_list():
    return [x.strip() for x in sys.stdin.readlines()]

def none_or_one(s):
    if len(s) >= 1:
        return sorted(s, key=len)[:1]
    else:
        return [None]

files_p = lambda: set(_file_list())
stind_p = lambda: set(_stdin_list())
raw_p = ('both', lambda: set(['']), lambda x: x)

if __name__ == '__main__':
    # example
    import yaml
    data_1 = set('this old man he played dumb he played tic tac'.split())
    data_2 = set('we all have time for our friends but we spend it instead'.split())
    data_3 = set('lastly for another time and place'.split())
    sys.argv.pop(0)
    cmds = {'one': (lambda a, b, c: [a, b, c], [('current', lambda x: data_1, lambda x: x.upper()),
                                                ('current', lambda x: data_3, lambda x: x.upper()),
                                                ('|', None, None),
                                                ('both', lambda x: data_2, lambda x: x.upper())])}
    print(list(handle(cmds, sys.argv)))
