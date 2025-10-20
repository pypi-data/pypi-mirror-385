# Slightly Better Dicts

A Python library that provides some classes and functions that add quality of life improvements to the standard library's `dict`.

This is a library that I end up re-writing in some form or another every time I work on a new Python project. I decided that it was long past time I threw together a module.

---

Before and after:

```python
my_data = {
    "id": 123,
    "profile": {
        "name": "Mr. Cool Guy",
        "email": "cool.guy@matthewhale.xyz",
        "address": {
            "street": "123 Baller Ave",
            "city": "Coolsville",
            "state": "HI",
            "zip": 55555,
        },
    },
    "preferences": {
        "notifications": {
            "messages": True,
            "promotions": False,
        },
    },
}

my_data.get("profile").get("address").get("zip")
# 55555

my_data.get("preferences").get("oops").get("frobnicate")
# AttributeError: 'NoneType' object has no attribute 'get'

my_data.get("preferences", {}).get("clunky, huh?", {}).get("frobnicate", "default")
# 'default'


from slightly_better_dicts import BetterDict

my_better_data = BetterDict(my_data)

my_better_data.get_in(["profile", "address", "zip"])
# 55555

my_better_data.get_in(["preferences", "oops", "frobnicate"], "default")
# 'default'

if state := my_better_data.get_in(["profile", "address", "state"]) == "HI":
    print("Hi, HI!")
# Hi, HI!
```

## Installation

It's on PyPI. `pip install slightly_better_dicts`, `poetry add slightly_better_dicts`, `uv add slightly_better_dicts` and so on and so forth and what have you.

## Usage

Functionality is provided via two interfaces: subclasses of `dict`, and a collection of pure functions. All of the methods found in the `dict` subclasses are also available as regular functions that accept a mapping as their first argument.

For example:

```python
from slightly_better_dicts import BetterDict, get_in

data = {
    "a": {
        "b": {
            "c": True,
        },
    },
}
better_data = BetterDict(data)

better_data.get_in(["a", "b", "c"])
# True

get_in(data, ["a", "b", "c"])
# True
```
