# Onionprobe requirements

Onionprobe requires the following software:

* [Python 3](https://www.python.org)
* [Stem Tor Control library](https://stem.torproject.org)
* [Prometheus Python client](https://github.com/prometheus/client_python)
* [PyYAML](https://pyyaml.org)
* [Requests](https://docs.python-requests.org)
* [PySocks](https://github.com/Anorov/PySocks)
* [Tor daemon](https://gitlab.torproject.org/tpo/core/tor)

On [Debian](https://debian.org), they can be installed using

    sudo apt install python3 python3-prometheus-client \
                     python3-stem python3-cryptography \
                     python3-yaml python3-requests     \
                     python3-socks tor
