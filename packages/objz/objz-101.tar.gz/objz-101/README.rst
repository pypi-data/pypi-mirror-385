OBJz
====


**NAME**


|
| ``objz`` - a clean namespace
|


**SYNOPSIS**

::

    >>> from objz.objects import Object
    >>> from objz.serials import dumps, loads
    >>> o = Object()
    >>> o.a = "b"
    >>> print(loads(dumps(o)))
    {'a': 'b'}


**DESCRIPTION**


``objz`` contains python3 code to program objz in a functional
way. it provides an “clean namespace” Object class that only has
dunder methods, so the namespace is not cluttered with method names.

This makes reading to/from json possible.


**INSTALL**


installation is done with pip

|
| ``$ pip install objz``
|

**AUTHOR**

|
| Bart Thate <``bthate@dds.nl``>
|

**COPYRIGHT**

|
| ``objz`` is Public Domain.
|
