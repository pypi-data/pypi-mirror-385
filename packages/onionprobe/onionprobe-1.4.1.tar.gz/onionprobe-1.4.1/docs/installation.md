# Onionprobe installation

## Debian package

A package for Onionprobe should be available on [Debian][]-like systems.

    sudo apt install onionprobe

This will also install the [Tor daemon][] and other needed dependencies.

[Debian]: https://www.debian.org
[Tor daemon]: https://gitlab.torproject.org/tpo/core/tor

## Arch Linux package

An Arch Linux package is [available on AUR][][^arch-linux-package]:

    pacman -S onionprobe-git

[available on AUR]: https://aur.archlinux.org/packages/onionprobe-git
[tpo/onion-services/onionprobe#16]: https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/issues/16

[^arch-linux-package]: Check also issue [tpo/onion-services/onionprobe#16][].

## Python package

Onionprobe is available as a [Python][] package [through PyPI][pypi] and can be
installed in a number of ways.

The [Python][] package installation procedure will handle all the Python
dependencies, but won't install the [Tor daemon][] package, which should be
installed separately, preferentially through your operating system package
manager. Example: in a [Debian][]-like system, run

    sudo apt install -y tor

[Python]: https://python.org
[pypi]: https://pypi.org/project/onionprobe

Once the [Tor daemon][] is installed, proceed installing the [Python][] package.
Some options are detailed below.

### Using pipx

The recommended way to install the Onionprobe from the [Python][] package is
via [pipx][]:

    pipx install onionprobe

[pipx]: https://pipx.pypa.io/stable/

### Using pip and a virtualenv

Another installation option is to use [pip][] with a [virtualenv][]:

    mkdir onionprobe
    cd onionprobe
    python3 -m venv venv
    source venv/bin/activate
    pip install onionprobe

The `onionprobe` folder will store the [virtualenv][], and can also be
used to host Onionprobe configuration and data.

!!! note "Environment activation"

    The [virtualenv][] should be activated in order to run Onionprobe.

    This means that that a command like `source venv/bin/activate`
    should be user before running Oniobalance, like after system
    reboots, fresh command line shells or inside scripts.

[pip]: https://pypi.org/project/pip/
[virtualenv]: https://virtualenv.pypa.io/

### Using pip without a virtualenv

!!! warning "Conflict with system-wide packages"

    The following procedure might create conflict with system-wide Python
    software installed through the operating system package manager,
    and therefore is not recommended except if you know what you're doing.

If you prefer, Onionprobe can also be installed directly using [pip][]
without a [virtualenv][], but **this might conflict with system-wide installed
[Python][] packages**, and therefore is not usually recommended:

    pip install onionprobe --break-system-packages

### Python package installation from source

!!! warning "Conflict with system-wide packages"

    The following procedure might create conflict with system-wide Python
    software installed through the operating system package manager,
    and therefore is not recommended except if you know what you're doing.

To install the [Python][] package from source, first get the code and
install it using [pip][]:

    sudo apt install -y python3-pip
    git clone https://gitlab.torproject.org/tpo/onion-services/onionbalance
    cd onionprobe
    python3 -m pip install . --break-system-packages

The Onionprobe executable will be available usually at your `$HOME/.local/bin`
folder.

System-wide installation from source is also possible. The simpler way
is to invoke the last command above with `sudo`.

    sudo python3 -m pip install . --break-system-packages

For system-wide installations, the Onionprobe executable should be available in
a path like `/usr/local/bin/onionprobe`.

## Ansible role

[Ansible][] users can use the [Onionprobe Ansible Role][], which supports
running Onionprobe in a number of ways, including the [standalone
mode](standalone.md).

[Ansible]: https://ansible.com
[Onionprobe Ansible Role]: https://gitlab.torproject.org/tpo/onion-services/ansible/onionprobe-role

## Running from source

It's also possible to run it directly from the [Git repository][], useful if
you want to run the [standalone mode](standalone.md), hack on it or prefer a
local installation:

    git clone https://gitlab.torproject.org/tpo/onion-services/onionprobe
    cd onionprobe

[Git repository]: https://gitlab.torproject.org/tpo/onion-services/onionprobe

There are a number of ways to run from sources after the repository is cloned.

### Local installation from source using Debian packages

When in a [Debian][]-based system, Onionprobe dependencies can be installed
with:

    sudo apt install -y python3-prometheus-client python3-stem \
                        python3-cryptography python3-yaml      \
                        python3-requests python3-socks tor

The Onionprobe can then run directly from the working copy:

    ./onionprobe

A [convenience script][debian-script] is provided, which also installs
the official `tor` package:

    ./scripts/provision-onionprobe

[debian-script]: https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/blob/main/scripts/provision-onionprobe

### Local installation from source using Python packages

Onionprobe's [Python][] dependencies can be installed directly from
[PyPI][pypi], by setting up a [virtualenv][]:

The recommended way is to clone setup a [virtualenv][]:

    sudo apt install -y python3-pip tor
    python3 -m venv venv
    source venv/bin/activate
    pip3 install .

The Onionprobe can then run directly from the working copy:

    ./onionprobe

[Git repository]: https://gitlab.torproject.org/tpo/onion-services/onionprobe

!!! note "Environment activation"

    The [virtualenv][] should be activated in order to run Onionprobe.

    This means that that a command like `source venv/bin/activate`
    should be user before running Oniobalance, like after system
    reboots, fresh command line shells or inside scripts.
