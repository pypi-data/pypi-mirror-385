# pyrunnable

Lightweight convenience wrapper around `threading.Thread` with lifecycle hooks.

[![PyPI](https://img.shields.io/pypi/v/pyrunnable.svg)](https://pypi.org/project/pyrunnable/)
[![Python Versions](https://img.shields.io/pypi/pyversions/pyrunnable.svg)](https://pypi.org/project/pyrunnable/)
[![License: MIT](https://img.shields.io/pypi/l/pyrunnable.svg)](./LICENSE)

## Features

- Simple subclass of `threading.Thread`
- Lifecycle hooks you can override:
  - `on_start()` — called right after `start()`
  - `work()` — called repeatedly while running
  - `on_stop()` — called once after stopping
- Convenient `stop(join: bool = True)` helper

## Installation

- With pip:

```bash
pip install pyrunnable
```

- With uv (recommended):

```bash
uv add pyrunnable
```

## Quick start

```python
from time import sleep
from pyrunnable import Runnable

class Worker(Runnable):
    def on_start(self):
        print("starting")

    def work(self):
        print("working")
        sleep(0.2)

    def on_stop(self):
        print("stopping")

if __name__ == "__main__":
    w = Worker()
    try:
        w.start()
        w.join()  # Runnable inherits from threading.Thread
    except KeyboardInterrupt:
        w.stop()
```

## Compatibility

- Python: >= 3.6
- OS: Any platform supporting Python threads

## Development

This project uses [uv](https://github.com/astral-sh/uv) for building and packaging.

- Build distributions:

```bash
uv build
```

## Links

- Homepage/Repo: https://github.com/nbdy/pyrunnable
- Issues: https://github.com/nbdy/pyrunnable/issues
