__all__ = ['require']

import builtins
from importlib import import_module

from .config import config

def require(name, *args, **kwargs):
    if kwargs.get('function'):
        path = list(map(lambda a: a.replace('-', '_'), name.split('.')))
        if len(path) == 1:
            path.extend(('cli', 'main'))
        path[0] = toplevel(path[0])
        try:
            last = path.pop()
            module = import_module('.'.join(path))
            fn = getattr(module, last)
            if hasattr(fn, 'main'):
                fn = getattr(fn, 'main')
        except:
            path.append(last)
            module = import_module('.'.join(path))
            try:
                fn = getattr(module, 'main')
            except:
                fn = getattr(module, last)
        return fn
    else:
        if name == 'config': return config
        if '-' in name:
            name = name.replace('-', '_')
        if '.' in name:
            name, *args = name.split('.')
        d = import_module(toplevel(name))
        if len(args) > 1:
            return map(lambda a: getattr(d, a), args)
        elif len(args) == 1:
            return getattr(d, args[0])
        else:
            return d

def toplevel(name):
    if cfg := config('inceptum'):
        m = cfg.get('module')
        if m and name in m:
            return m[name]
        if 'prefix' in cfg:
            return cfg['prefix'] + name
    return name

builtins.require = require

# DEPRECATED
builtins.I = require
builtins.leptonix = require
