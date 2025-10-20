Varsnap Python
==============

[![Build Status](https://drone.albertyw.com/api/badges/albertyw/varsnap-python/status.svg)](https://drone.albertyw.com/albertyw/varsnap-python)

[Python Varsnap Client](https://www.varsnap.com/)

Installation
------------

Install from PyPI - `pip install varsnap`

Requirements
------------

The client depends on three environment variables to be set:

 - `VARSNAP` - Should be either `true` or `false`.  Varsnap will be disabled if the variable is anything other than `true`.
 - `ENV` - If set to `development`, the client will receive events from production.  If set to `production`, the client will emit events.
 - `VARSNAP_PRODUCER_TOKEN` - Only clients with this token may emit production snapshots.  Copied from https://www.varsnap.com/user/
 - `VARSNAP_CONSUMER_TOKEN` - Only clients with this token may emit development snapshots.  Copied from https://www.varsnap.com/user/

Usage
-----

Add the varsnap decorator in front of any function you'd like to make better:

```python
from varsnap import varsnap


@varsnap
def example(args, **kwargs):
    return 'output'
```

Testing
-------

With the proper environment variables set, in a test file, add:

```python
import unittest
from varsnap import test

class TestIntegration(unittest.TestCase):
    def test_varsnap(self):
        matches, logs = test()
        if matches is None:
            raise unittest.case.SkipTest('No Snaps found')
        self.assertTrue(matches, logs)
```

If you're testing a Flask application, set up a
[test request context](https://flask.palletsprojects.com/en/1.1.x/api/#flask.Flask.test_request_context) when testing:

```python
# app = Flask()
with app.test_request_context():
    matches, logs = test()
```

Troubleshooting
---------------

**Decorators changing function names**

Using decorators may change the name of functions.  In order to not confuse
varsnap, set the decorated function's `__qualname__` and `__signature__` to
match the original function:

```python
import inspect


def decorator(func):
    def decorated(*args, **kwargs):
        func(*args, **kwargs)
    decorated.__qualname__ = func.__qualname__
    wrapper.__signature__ = inspect.signature(func)
    return decorated
```

Publishing
----------

```bash
pip install build twine
python -m build
twine upload dist/*
```
