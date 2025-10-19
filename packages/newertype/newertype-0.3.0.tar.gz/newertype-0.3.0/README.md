# newertype

An Implementation of the NewType Pattern for Python that works in dynamic contexts.

  [![PyPI version](https://img.shields.io/pypi/v/newertype.svg)](https://pypi.org/project/newertype/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Python Versions](https://img.shields.io/pypi/pyversions/newertype.svg)](https://pypi.org/project/newertype/)
  [![Downloads](https://pepy.tech/badge/newertype)](https://pepy.tech/project/newertype)
  [![Python package](https://github.com/evanjpw/newertype/actions/workflows/python-package.yml/badge.svg)](https://github.com/evanjpw/newertype/actions/workflows/python-package.yml)

## What is it?

`NewerType` is a package that provides a semi-transparent wrapper to an existing type that allows it to be used
mostly as if it's just the wrapped type, but which allows type checking as if it's a distinct type at runtime.

With the addition to Python of [PEP 483](https://peps.python.org/pep-0483/),
[PEP 484](https://peps.python.org/pep-0484/), & the
[typing](https://docs.python.org/3/library/typing.html#module-typing) package, Python added support for type
hints. That included an implementation of the Haskell [`newtype`](https://wiki.haskell.org/Newtype) which was
cleverly called `NewType`.
As explained in [the documentation](https://docs.python.org/3/library/typing.html#typing.NewType),
Python's `NewType` is, like most of the
typing library, meant for use by static type checkers. This means that, when the code is running, the _Newness_ of
the type is erased, leaving just the wrapped type & no way to tell that there was ever a `Newtype`, either by
the code or by Python itself.

`NewerType` provides the same kind of wrapper as `NewType`, but allows (& enforces) type checking at runtime.
this means, for example, that if you wrap an `int` in a `NewerType`, you can do all of the arithmetic &
comparison operations on an instance of that type that you could with a normal `int` with either different
instances of that type, or `int`s. But you will not be able to mix _different_ `NewerType`s, even if they
all wrap `int`s.

This allows you to never have to worry if you are adding `Miles` to `Kilometers`, or mixing up a `UserName`
with a `Password`.

### Main Features

* A wrapper that allows dynamic type checking while mostly not getting in the way
* Carries type information with the object so you can always use `isinstace()` or `type()` to know what it is
* Forwards the magic methods from the wrapped object so things like arithmetic or indexing work
* Allows you to customize what methods are forwarded
* No dependencies!

## Installation

Current stable version:
```shell
pip install newertype
```

Newest thing on GitHub:
```shell
pip install git+https://github.com/evanjpw/newertype.git
```

## Usage

Basic usage:

```python
from newertype import NewerType

AType = NewerType("AType", int)  # `AType` is a new type that wraps an int
a_type = AType(14)  # Make an instance of this new type
isinstance(a_type, AType)  # `a_type` is an `AType`
# Returns: True
isinstance(a_type, int)  # `a_type` is _NOT_ an `int`
# Returns: False
str(a_type.__class__.__name__) == "AType"
# Returns: True
```

You can use the new type as if it's the wrapped type:

```python
AType = NewerType("AType", int)  # Let's make some types!
a_type_1 = AType(7)
a_type_2 = AType(7)  # Two different instances with the same class
a_type_1 == a_type_2  # You can compare them as if they were just `int`s
# Returns: True

EType = NewerType("EType", int)
e_type_1 = EType(7)
e_type_2 = EType(14)
e_type_2 > e_type_1  # All of the `int` operations work
# Returns: True
a_type_1 == e_type_1  # But different types are not equal, even if the wrapped value is
Returns: False

IType = NewerType("IType", int)
JType = NewerType("JType", int)
i_type_1 = IType(7)
i_type_2 = IType(14)
i_type_1 + i_type_2  # Arithmetic works!
# Returns: 21

j_type_1 = JType(7)
i_type_1 + j_type_1  # But not if you try to mix `NewerType`s
# "TypeError: unsupported operand type(s) for +: 'IType' and 'JType'"
int(i_type_1) < int(i_type_2)  # Conversions that work for the inner type work also
# Returns: True
```

Accessing the wrapped data directly:

```python
a_type = AType(14)
a_type.inner  # the `inner` property gets the contained value
# Returns: 14
a_type.inner = 27  # `inner` can also be used to modify the value
a_type.inner
# Returns: 27
```

The "truthiness" & string representations are sensible:

```python
SType = NewerType("SType", float)
s_type = SType(2.71828182845904523536028747135266249775724709369995)
str(s_type)
# Returns: "SType(2.718281828459045)"
repr(s_type)
# Returns: "SType(2.718281828459045)"
bool(s_type)
# Returns: True
bytes(s_type)  # `bytes()` only works if it works with the wrapped type
# "TypeError: cannot convert 'float' object to bytes"

s_type.inner = 0.0
bool(s_type)
# Returns: False
```

What about forwarding your own methods on your own classes? NewerType can handle that:

```python
# First, define a class. It can have the standard indexing methods, but also some unique ones:
class Forwardable(UserDict):
    def forwarded(self, value):
        return value

    def also_forwarded(self, key):
        return self[key]

    def __getitem__(self, item):
        return super().__getitem__(item)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)

# The normal behavior is for NewerType to forward the standard methods but ignore the custom ones:
FO1Type = NewerType("FO1Type", Forwardable)
fo1_type_1 = FO1Type(Forwardable())
fo1_type_1["a"] = 5  # `__setitem__` is a standard method, so it's forwarded
fo1_type_1["a"]  # So is `__getitem__`
# Returns: 5
fo1_type_1.forwarded(5)  # But unique methods are not forwarded
# "AttributeError: FO1Type' object has no attribute 'forwarded'"

# We can use "extra_forwards" to specify the additional methods we'd like to forward:
FO2Type = NewerType(
    "FO2Type", Forwardable, extra_forwards=["forwarded", "also_forwarded"]
)
fo2_type_1 = FO2Type(Forwardable())
fo2_type_1["e"] = 7  # This continues to work
fo2_type_1["e"]  # As does this
# Returns: 7
fo2_type_1.also_forwarded("e")  # But now this works also!
# Returns: 7

# But what if we _don't_ want to forward the standard methods? Use "no_def_forwards":
FO3Type = NewerType(
    "FO3Type", Forwardable, extra_forwards=["also_forwarded"], no_def_forwards=True
)
fo3_type_1 = FO3Type(Forwardable())
fo3_type_1.inner["g"] = 8
fo3_type_1.also_forwarded("g")  # The extra methods continue to work
# Returns: 8
fo3_type_1["g"]  # But the standard ones don't (unless we specifically mention them in "extra_forwards")
# "TypeError: 'FO3Type' object is not subscriptable"
```

## TBD

* The `bytes()` built-in currently just forces all wrapped `str` objects to "utf-8" as an encoding.
 If you need a *different* encoding, use `bytes()` of `.inner`.
* There are a *bunch* more methods that should be in the whitelist for forwarding. That's a work in progress.

## Project Resources

* Documentation - TBD
* [Issue tracker](https://github.com/evanjpw/newertype/issues)
* [Source code](https://github.com/evanjpw/newertype)
* [Change log](https://github.com/evanjpw/newertype/blob/main/CHANGELOG.md)

## License

Licensed under the [MIT LICENSE](https://www.mit.edu/~amini/LICENSE.md)
