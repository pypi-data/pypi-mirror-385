# This file is placed in the Public Domain.


"json serializer"


from json import JSONEncoder
from json import dumps as jdumps
from json import loads as jloads


class Encoder(JSONEncoder):

    def default(self, o):
        if isinstance(o, dict):
            return o.items()
        if isinstance(o, list):
            return iter(o)
        try:
            return JSONEncoder.default(self, o)
        except TypeError:
            try:
                return vars(o)
            except TypeError:
                return repr(o)


def dumps(obj, *args, **kw):
    ""
    kw["cls"] = Encoder
    return jdumps(obj, *args, **kw)


def loads(*args, **kw):
    ""
    return jloads(*args, **kw)
    

def __dir__():
    return (
        'dumps',
        'loads'
    )


__all__ = __dir__()
