# Onionprobe development

Onionprobe development guidelines and workflow are listed here.

## Release procedure

Release cycle workflow.

### Version update

Set the version number:

    ONIONPROBE_VERSION=1.4.1

Update the version in some files, like:

    dch -i # debian/changelog
    $EDITOR packages/onionprobe/config.py
    $EDITOR docker-compose.yaml
    $EDITOR setup.cfg

### Regenerate the manpages

Build updated manual pages:

    make manpages

Check:

    man -l docs/man/onionprobe.1

### Register the changes

Update the ChangeLog:

    $EDITOR ChangeLog

Commit and tag:

    git diff # review
    git commit -a -m "Feat: Onionprobe $ONIONPROBE_VERSION"
    git tag -s $ONIONPROBE_VERSION -m "Onionprobe $ONIONPROBE_VERSION"

Push changes and tags. Example:

    git push origin        && git push upstream
    git push origin --tags && git push upstream --tags

Once a tag is pushed, a [GitLab release][] is created.

[GitLab release]: https://docs.gitlab.com/ee/user/project/releases/

### Build packages

Build the Python package:

    make build-python-package

Install this package in a fresh virtual machine. Example:

    sudo apt-get install -y python3-pip tor
    pip install --break-system-packages \
      dist/onionprobe-$ONIONPROBE_VERSION-*.whl

Then test it:

    $HOME/.local/bin/onionprobe --version
    $HOME/.local/bin/onionprobe -e \
      http://2gzyxa5ihm7nsggfxnu52rck2vv4rvmdlkiu3zzui5du4xyclen53wid.onion
    $HOME/.local/bin/onionprobe -e \
      https://v236xhqtyullodhf26szyjepvkbv6iitrhjgrqj4avaoukebkk6n6syd.onion

If the package worked, upload it to the [Test PyPI][] instance:

    make upload-python-test-package

Install again the test package, by fetching it from [Test PyPI][], and in
another fresh virtual machine:

    sudo apt-get install -y python3-pip tor
    pip install -i https://pypi.org/simple/ \
                --extra-index-url https://test.pypi.org/simple \
                --break-system-packages \
                onionprobe==$ONIONPROBE_VERSION

Do the tests again in this new installation.
If the the package works as expected, upload it to PyPI:

    make upload-python-package

Finally, install the package one more time, but now fetching it from [PyPI][],
and in yet another fresh virtual machine:

    sudo apt-get install -y python3-pip tor
    pip install --break-system-packages \
      onionprobe==$ONIONPROBE_VERSION

Do the tests once more, in this new installation.

[Test PyPI]: https://test.pypi.org
[PyPI]: https://pypi.org

### Announcement

Announce the new release:

* Post a message to the [Tor Forum][], using the [onion-services-announce tag][].
* Send a message to the [tor-announce][] mailing list ONLY in special cases,
  like important security issues (severity `HIGH` or `CRITICAL`).

Template:

```
Subject: [RELEASE] Onionprobe [security] release $ONIONPROBE_VERSION

Greetings,

We just released [Onionprobe][] $ONIONPROBE_VERSION, a tool for testing and
monitoring the status of Onion Services.

[This release fixes a security issue. Please upgrade as soon as possible!]

[This release [also] requires a database migration for those using the monitoring node:]
[https://onionservices.torproject.org/apps/web/onionprobe/upgrading/]

[Onionprobe]: https://onionservices.torproject.org/apps/web/onionprobe

# ChangeLog

$CHANGELOG
```

[tor-announce]: https://lists.torproject.org/cgi-bin/mailman/listinfo/tor-announce
[Tor Forum]: https://forum.torproject.org
[onion-services-announce tag]: https://forum.torproject.org/tag/onion-services-announce

## Testing

### Writing and trying alerts and unit tests for Prometheus

The [Prometheus][] alerts shipped by Onionprobe are tested by the `promtool` [CI job][].
The configuration is available under the [configs/prometheus][] folder.

#### Workflow

A quick workflow to try tests before pushing to CI can be set with the
[standalone][] node:

    ./onionprobe-monitor up
    ./onionprobe-monitor shell prometheus
    promtool test rules /etc/prometheus/prometheus-tests.yml

[Prometheus]: https://prometheus.io/
[CI job]: https://docs.gitlab.com/ee/ci
[configs/prometheus]: https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/tree/main/configs/prometheus
[standalone]: standalone.md

Once the new alerts and corresponding unit tests are updated, don't forget to
also update the [troubleshooting docs](troubleshooting.md).

#### References

References for understanding and writing unit tests for [Prometheus][]:

* [Unit Testing for Rules | Prometheus](https://prometheus.io/docs/prometheus/latest/configuration/unit_testing_rules/)
* [Sleep Soundly: Reliable Alerting with Unit Testing in Prometheus | by Rubén Cougil Grande | Medium](https://medium.com/@rcougil/sleep-soundly-realiable-alerting-with-unit-testing-in-prometheus-260c652a3f9)
* [A Guide to Unit Testing Prometheus Alerts - Aviator Blog](https://www.aviator.co/blog/a-guide-to-unit-testing-prometheus-alerts/#)
* [Testing alerts - prometheus · Wiki · The Tor Project / TPA / TPA team · GitLab](https://gitlab.torproject.org/tpo/tpa/team/-/wikis/service/prometheus#testing-alerts)
