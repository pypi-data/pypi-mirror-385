# Onionprobe usage

Simply ask Onionprobe to try an Onion Service site:

    onionprobe -e http://2gzyxa5ihm7nsggfxnu52rck2vv4rvmdlkiu3zzui5du4xyclen53wid.onion

It's possible to supply multiple addresses:

    onionprobe -e <onion-address1> <onionaddress2> ...

Onionprobe also accepts a configuration file with a list of .onion endpoints
and options. A [detailed sample config][] is provided and can
be invoked with:

    onionprobe -c configs/tor.yaml

By default, Onionprobe starts it's own Tor daemon instance, so the `tor` binary
must be available in the system.

See the [manual page](man/README.md) for the complete list of options and
available metrics.

[detailed sample config]: https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/blob/main/configs/tor.yaml
