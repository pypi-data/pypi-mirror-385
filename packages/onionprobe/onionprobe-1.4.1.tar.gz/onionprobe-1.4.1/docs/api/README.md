# API

This section documents the Onionprobe API.

## Basic usage

Onionprobe can be easily run as a library.

If you [installed it](../installation.md) as a package, you can just import it
directly on your code like any other installed Python package:

```python
from onionprobe.app import run_from_cmdline

if __name__ == "__main__":
    run_from_cmdline()
```

It's also possible to import it directly from the source code, like when it's
vendorized as a Git submodule in a folder such as `vendors/onionprobe` relative
to the top-level of your main project:


```python
from vendors.onionprobe.packages.onionprobe.app import run_from_cmdline

if __name__ == "__main__":
    run_from_cmdline()
```

The [package API page](onionprobe.md) details all the available
modules and functionality for developing with Onionprobe.
