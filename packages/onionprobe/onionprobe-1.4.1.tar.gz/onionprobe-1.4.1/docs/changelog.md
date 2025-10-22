# Onionprobe ChangeLog

## v1.4.1 - 2025-10-21

### Fixes

* Generating the manual page during development time
  ([tpo/onion-services/onionprobe#93][]).

* Support for Python 3.14 ([tpo/onion-services/onionprobe#116][]).

[tpo/onion-services/onionprobe#93]: https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/issues/93
[tpo/onion-services/onionprobe#116]: https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/issues/116

## v1.4.0 - 2025-04-08

### Features

* Prometheus alerting improvements ([tpo/onion-services/onionprobe#102][]):
    * Tests for Prometheus alerting rules.
    * New alert "Onionprobe not responding", detecting issues with the
      Onionprobe operation itself.

* Documentation:
    * [Troubleshooting page](troubleshooting.md).
    * [Development](development.md): new section about Prometheus alerts
      development and testing.

* Test Onionprobe on CI ([tpo/onion-services/onionprobe!107][],
  [tpo/onion-services/onionprobe!108][]).

* Upgraded Grafana image to 11.6.0.

[tpo/onion-services/onionprobe#102]: https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/issues/102
[tpo/onion-services/onionprobe!107]: https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/merge_requests/107
[tpo/onion-services/onionprobe!108]: https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/merge_requests/108

### Fixes

* Filter out `SocketClosed` log messages from Stem ([tpo/onion-services/onionprobe!111][]).

* Handle `ssl.match_hostname()` deprecation ([tpo/onion-services/onionprobe#107][]).

* Fix `CryptographyDeprecationWarning` on TLS certificate handling
  ([tpo/onion-services/onionprobe#92][]).

[tpo/onion-services/onionprobe!111]: https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/merge_requests/111
[tpo/onion-services/onionprobe#107]: https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/issues/107
[tpo/onion-services/onionprobe#92]: https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/issues/92

## v1.3.0 - 2025-03-12

### Features

* [Standalone monitoring node](standalone.md):
  * Grafana dashboard got a new time series: number of missing Onion Service
    descriptors in HSDirs.

* Added tests for the Prometheus configuration
  ([tpo/onion-services/onionprobe!90][]).

[tpo/onion-services/onionprobe!90]: https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/merge_requests/90

### Fixes

* [Standalone monitoring node](standalone.md):
  * *SECURITY*: use an internal network by default:
    * By default, Prometheus, Alertmanager, Grafana and the Onionprobe exporter are accessible
      only from localhost or through Onion Services.
    * This prevents exposing these services to the internet in systems that aren't firewalled.
    * This can be customized via the `ONIONPROBE_LISTEN_ADDR` environment variable used by
      the [Compose][] configuration.
    * Thanks to [@gus][] for spotting the issue.

  * The `start` action in the `onionprobe-monitor` script now pulls and builds
    images.

  * Failure rate was erroneously being reported at 1% when all services
    were working, when the excepted would be a reported value of 0%.
    This is now fixed.

[Compose]: https://docs.docker.com/reference/compose-file/
[@gus]: https://gitlab.torproject.org/gus

## v1.2.1 - 2024-11-27

### Features

* The [installation page](installation.md) updated to include a reference to
  the new [Onionprobe Ansible Role][].

* [Standalone monitoring node](standalone.md):
    * Added support for [Podman][] and [Podman Compose][] ([tpo/onion-services/onionprobe#97][]).
      It can be enable by setting `CONTAINER_RUNTIME=podman` in the `.env` file.
      For backwards compatibility,
      [Docker][] is still the default container runtime.

    * New `onionprobe-monitor` script acting as a wrapper for interacting with
      the container runtime ([tpo/onion-services/onionprobe#97][]).
      Given that [Podman][] and [Docker][] have a few differences, it made sense
      to create a thin wrapper around them, to handle things like [Podman not
      honoring some Compose variables in .env files][podman-env].

[Onionprobe Ansible Role]: https://gitlab.torproject.org/tpo/onion-services/ansible/onionprobe-role
[Docker]: https://docker.com
[Podman]: https://podman.io
[Podman Compose]: https://github.com/containers/podman-compose
[podman-env]: https://github.com/containers/podman-compose/issues/475
[tpo/onion-services/onionprobe#97]: https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/issues/97

### Fixes

* Updated the sample systemd service unit ([tpo/onion-services/onionprobe!72][]).

* Upgraded Prometheus image to [3.0.0][prometheus-3.0.0].

* PostgreSQL:
    * Upgraded image to version 17.
      Please run the [needed upgrading steps](upgrading.md#major-upgrades).

    * Minor fixes at `upgrade-postgresql-database`.

* Updated [development procedure](development.md).

* Improved verbosity for the Tor initialization log message.

[tpo/onion-services/onionprobe!72]: https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/merge_requests/72
[prometheus-3.0.0]: https://prometheus.io/blog/2024/11/14/prometheus-3-0/

## v1.2.0 - 2024-04-24

### Features

* New metrics ([tpo/onion-services/onionprobe#78][]):
    * From the outer descriptor wrapper:
        * `descriptor-lifetime`.
        * `revision-counter`.
    * From the second layer of encryption:
        * `single-onion-service`.
        * `pow-params`.
    * HSDir latency when fetching descriptors.

* Enhanced Grafana Dashboard ([tpo/onion-services/onionprobe#80][]) with the
  following new visualizations:
    * Overview:
        * Current failure rate of onionsites.
        * Total expiring certificates in the next 7 days.
        * List of certificate expirations up to the next 180 days.
        * List of unreachable instances.
        * Graph with the total unreachable instances.
        * List of invalid HTTPS certificates.
        * List of services with HTTPS errors.
    * Performance:
        * Total of minimum, average and maximum service connection latency.
        * Total of minimum, average and maximum descriptor fetch latency.
        * Chart of minimum, average and maximum service connection latency.
        * Chart of minimum, average and maximum descriptor fetch latency.
        * Rate of services using the single hop mode, relative to the total services monitored.
        * List of slow services.
    * Descriptors:
        * List of services missing a published descriptor.
        * Chart of the minimum, average and maximum descriptor sizes (decrypted outer layer).
        * Chart of the minimum, average and maximum descriptor sizes (decrypted second layer).
    * Introduction points:
        * Chart of minimum, average and maximum number of introduction points per service.
        * List of services and it's number of introduction points.
    * HSDir:
        * Total number of HSDirs tested.
        * Chart of minimum, average and maximum HSDir latency for fetching descriptors.
        * List of HSDirs sorted by descriptor fetch latency.
    * Proof of Work (PoW):
        * Ratio of services with PoW enabled, relative to the total services monitored.
        * Total number of services with PoW enabled.
        * Chart of minimum, average and maximum PoW v1 effort seem.
        * List of services with PoW enabled.
        * List of services with PoW enabled with effort greater than zero.

* Improved log message for elapsed time.

* New log messages for:
    * Number of introduction points.
    * HS_DESC events:
        * Descriptor reachability.
        * HSDir used.

* Create a GitLab release at every new tag (experimental)
  ([tpo/onion-services/onionprobe#82][]).

* Running lintian on CI to check the generated Debian package.

[tpo/onion-services/onionprobe#78]: https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/issues/78
[tpo/onion-services/onionprobe#80]: https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/issues/80
[tpo/onion-services/onionprobe#82]: https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/issues/82

### Fixes

* Manpage generation is now compatible with the Onion Services
  Ecosystem Portal ([tpo/onion-services/ecosystem#1][]).

* Use the correct copyright line in source files.

* Support for a wider range of [pyca/cryptography][] versions at `setup.cfg`.

* Display Tor bootstrap messages only for the debug log level.

* Disable stem logging if log level is below debug ([tpo/onion-services/onionprobe#63][]).

* Exit codes now reflects reality ([tpo/onion-services/onionprobe#64][]).

* Calculate the elapsed time for descriptors right after fetching.

* Updated the [SecureDrop list][].

* Upgraded Grafana image to 10.4.2.

* Upgraded Alertmanager image to 0.27.0.

* Upgraded Prometheus image to 2.51.2.

* Upgraded PostgreSQL image to 16.
  Please run the [needed upgrading steps](upgrading.md#major-upgrades).

* Upgraded CI and container images to Debian bookworm.

* Upgraded `vendors/onion-mkdocs`.

[tpo/onion-services/ecosystem#1]: https://gitlab.torproject.org/tpo/onion-services/ecosystem/-/issues/1
[pyca/cryptography]: https://cryptography.io
[tpo/onion-services/onionprobe#63]: https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/issues/63
[tpo/onion-services/onionprobe#64]: https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/issues/64
[SecureDrop list]: https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/blob/main/configs/securedrop.yaml

## v1.1.2 - 2023-09-28

### Features

* Debug outer and inner layer descriptor contents.

* Decrease Prometheus certificate expiration alerts to 7 days in advance.

### Fixes

* Make the tor process quiet when generating hashed passwords (reported by
  @anarcat): https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/issues/81

* CI/CD: use rsync to copy slide artifacts, preserving the folder structure.

* Minor documentation improvements.

## v1.1.1 - 2023-04-04

### Fixes

* Grafana dashboard:
  * Apply workaround for "Invalid dashboard UID in the request error on custom
    home dashboard": https://github.com/grafana/grafana/issues/54574

* Docker:
  * Stick to specific upstream image versions to avoid unexpected upgrade issues.

  * Change the `onionprobe` image version scheme to match semantic versioning.

* PostgreSQL upgrade script (`upgrade-postgresql-database`):
  * Misc fixes.

## v1.1.0 - 2023-04-03

### Features

* Support for Tor metrics Prometheus exporter via `MetricsPort` and `MetricsPortPolicy`
  settings, available respectively as `metrics_port` and `metrics_port_policy`
  configuration or command line parameters.

  These settings are disabled by default. If you plan to use this with the
  standalone monitoring node, you may also want to edit `configs/prometheus/prometheys.yml`
  and uncomment Tor's Prometheus configuration so this data becomes available at
  Prometheus, Alertmanager and Grafana.

  WARNING: Before enabling this, it is important to understand that exposing
  tor metrics publicly is dangerous to the Tor network users. Please take extra
  precaution and care when opening this port. Set a very strict access policy
  with `MetricsPortPolicy` and consider using your operating systems firewall
  features for defense in depth.

  We recommend, for the prometheus format, that the only address that can
  access this port should be the Prometheus server itself. Remember that the
  connection is unencrypted (HTTP) hence consider using a tool like stunnel to
  secure the link from this port to the server.

  Check the [standalone monitoring node docs](standalone.md) for
  detailed instructions in how to enable this additional metric collection.

* TLS certificate verification:
  * Added a global `tls_verify` flag to check certificates during HTTP tests.
    Set it to `false` to ignore TLS certificate verification.
    By default all TLS certificates are checked.

  * Added a per-endpoint `tls_verify` flag to check certificates in HTTP tests,
    overriding the global setting for the endpoint context.

  * Changed the `onion_service_valid_certificate` metric to also inform
    when a certificate wasn't tested by setting a value of `2` on that
    case. This isn't a breaking change since the TLS certificate is enabled
    by default, so unless verification is disabled the metric will only
    vary between `0` (invalid cert) and `1` (valid cert).

* TLS and X.509 certificate test:
  * Added a new test to check the conditions of the underlying TLS connection
    and to get detailed certificate information.

  * This test currently only happens for endpoints with the `https` protocol,
    and only if the `test_tls_connection` configuration is set to true in the
    global scope or in the endpoint configuration.

  * Certificates are retrieved and analyzed _even_ if they're not valid,
    in order to also collect data on self-signed, expired or otherwise invalid
    certificates.

  * A number of new metrics is included both for the TLS connection and for the
    server certificate:
    * `onion_service_certificate_not_valid_before_timestamp_seconds`: Register
      the beginning of the validity period of the certificate in UTC. This does
      not mean necessarily that the certificate is CA-validated. Value is
      represented as a POSIX timestamp,

    * `onion_service_certificate_not_valid_after_timestamp_seconds`: Register
      the end of the validity period of the certificate in UTC. This does not
      mean necessarily that the certificate is CA-validated. Value is
      represented as a POSIX timestamp.

    * `onion_service_certificate_expiry_seconds`: Register how many seconds are
      left before the certificate expire. Negative values indicate how many
      seconds passed after the certificate already expired.

    * `onion_service_certificate_match_hostname`: Register whether a provided
      server certificate matches the server hostname in a TLS connection: value
      is 1 for matched hostname and 0 otherwise. Check is done both on the
      commonName and subjectAltName fields. A value of 1 does not mean necessarily
      that the certificate is CA-validated.

    * `onion_service_certificate_info`: Register miscellaneous TLS certificate
      information for a given Onion Service such as version and fingerprints.

    * `onion_service_tls_security_level`: Tracks the SSL security level in use.
      Needs Python 3.10+ to work. See SSL_CTX_get_security_level(3) manpage for details:
      https://www.openssl.org/docs/manmaster/man3/SSL_CTX_get_security_level.html

    * `onion_service_tls_info`: Register miscellaneous TLS information for a
      given Onion Service such as version and ciphers.

  * Prometheus rules for the standalone monitoring node were updated to include
    an alert for certificates about to expire (defaults to 30 days in advance).

  * Details at https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/issues/49

* Added the `onion_service_generic_error_total` metric to track probing errors
  not covered by other metrics.

* Added script to handle PostgreSQL version upgrades at the service container:
  https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/issues/70

* Using Onion Mkdocs for the documentation, now hosted at
  https://tpo.pages.torproject.net/onion-services/onionprobe/

  See https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/issues/19

* Expected HTTP status codes:
  * Per-endpoint configuration specifying a list of expected HTTP status
    codes, useful when it's expected that an endpoint returns a status other
    than 200.
  * Custom metric indicating if the status code is expected or not.

* CI/CD: added jobs to test building debian and python packages, as well as
  configurations and slides.

### Fixes

* Stick to a PostgreSQL docker image:
  See https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/issues/70

* Command-line URL parsing:
  https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/merge_requests/17

* Display default values for most options on `onionprobe --help`.

## v1.0.0 - 2022-05-31

### Breaking changes

* Changed Prometheus exporter metric names to adhere to the
  [Best practices](https://prometheus.io/docs/practices/naming/) and to
  [other recommendations when writing an exporter](https://prometheus.io/docs/instrumenting/writing_exporters/#naming).
  Prometheus admins might want to rename their old metrics to the new
  ones to keep time series continuity, drop the old ones or keep both
  during a transition phase. The following metrics were renamed:
  * From `onionprobe_wait` to `onionprobe_wait_seconds`.
  * From `onion_service_latency` to `onion_service_latency_seconds`.
  * From `onion_service_descriptor_latency` to `onion_service_descriptor_latency_seconds`.
  * From `onion_service_fetch_error_counter` to `onion_service_fetch_error_total`.
  * From `onion_service_descriptor_fetch_error_counter` to
         `onion_service_descriptor_fetch_error_total`.
  * From `onion_service_request_exception` to `onion_service_request_exception_total`.
  * From `onion_service_connection_error` to `onion_service_connection_error_total`.
  * From `onion_service_http_error` to `onion_service_http_error_total`.
  * From `onion_service_too_many_redirects` to `onion_service_too_many_redirects_total`.
  * From `onion_service_connection_timeout` to `onion_service_connection_timeout_total`.
  * From `onion_service_read_timeout` to `onion_service_read_timeout_total`.
  * From `onion_service_timeout` to `onion_service_timeout_total`.
  * From `onion_service_certificate_error` to `onion_service_certificate_error_total`.

* Removed the `updated_at` label from all metrics, which was creating a new
  data series for every measurement on Prometheus.

* Removed the `hsdir` label from `onion_service_descriptor_reachable` metric,
  which was creating a new data series for every measurement on Prometheus.

### Features

* Monitoring node setup using Docker Compose and Prometheus, Alertmanager
  and Grafana dashboards served via Onion Services.

* Config generation improvements.

* New metrics:
  * `onion_service_fetch_requests_total`.
  * `onion_service_descriptor_fetch_requests_total`.
  * `onion_service_descriptor`, with Onion Service descriptor information.
  * `onion_service_probe_status`, with timestamp from the last test.

* Default Grafana Dashboard with basic metrics.

## v0.3.4 - 2022-05-11

### Fixes

* [x] Onionprobe's exporter port allocation conflict with the push gateway
      https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/issues/45

## v0.3.3 - 2022-05-11

### Fixes

* [x] Stem is unable to find cryptography module when running from the pip package
      https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/issues/43

## v0.3.2 - 2022-05-11

Main issue: https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/issues/42

### Features

* [x] Enhanced config generators: switch all three config generators currently
      supporter (Real-World Onion Sites, SecureDrop and TPO) to rely on argparse
      for command line arguments.

## v0.3.1 - 2022-05-10

Main issue: https://gitlab.torproject.org/tpo/tpa/team/-/issues/40717

### Features

* [x] Adds `packages/tpo.py` to generate an Onionprobe config with Tor
      Project's .onions.
      Details at https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/merge_requests/4

* [x] Other minor fixes and enhancements.

## v0.3.0 - 2022-04-19

Main issue: https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/issues/4

### Features

* [x] Debian package.
* [x] Better logging.
* [x] Additional command line options.
* [x] Handling of SIGTERM and other signals.

### Documentation

* [x] Manpage.
* [x] Auto-generate command line docs from CLI invocation.
* [x] Auto-generate manpage from `argparse`.

## v0.2.2 - 2022-04-06

### Fixes

* [x] Print usage when no arguments are supplied.

## v0.2.1 - 2022-04-06

### Fixes

* [x] Python package fixes.

## v0.2.0 - 2022-04-06

Main issue: https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/issues/3

### Features

* [x] Python packaging: https://pypi.org/project/onionprobe.
* [x] Support for `--endpoints` command line argument.
* [x] Display available metrics at command line usage.
* [x] Adds `OnionprobeConfigCompiler` to help compile custom configuration.

## v0.1.0 - 2022-03-31

Main issue: https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/issues/2

### Meta

* [x] Move the repository to the [Onion Services Gitlab group](https://gitlab.torproject.org/tpo/onion-services).
* [x] Docstrings.
* [x] Environment variable controlling the configuration file to use.

### Probing

* [x] Set timeout at `get_hidden_service_descriptor()`.
* [x] Set timeout at `Requests`.
* [x] Set `CircuitStreamTimeout` in the built-in Tor daemon.
* [x] HTTPS certificate validation check/exception.
* [x] Max retries before throwing an error when getting descriptors.
      This could help answering the following questions:
    * [When an onion service lookup has failed at the first k HSDirs we tried, what are the chances it will still succeed?](https://gitlab.torproject.org/tpo/network-health/analysis/-/issues/28)
    * [What's the average number of hsdir fetches before we get the hsdesc?](https://gitlab.torproject.org/tpo/core/tor/-/issues/13208)
* [x] Max retries before throwing an error when querying the endpoint.

### Metrics

* [x] Status: sleeping, probing, starting or stopping.
* [x] Match found / not found.
* [x] Metric units in the description.
* [x] Number of introduction points.
* [x] Timestamp label.
* [x] Register HSDir used to fetch the descriptor.
      Check the [control-spec](https://gitlab.torproject.org/tpo/core/torspec/-/blob/main/control-spec.txt)
      for `HSFETCH` command and the `HS_DESC` event ([using SETEVENTS](https://stem.torproject.org/tutorials/down_the_rabbit_hole.html)).
      Relevant issues:

### Enhancements

* [x] Refactor into smaller modules.
* [x] Better exception handling.

### Bonus

* [x] Script that compiles configuration from the
      [real-world-onion-sites](https://github.com/alecmuffett/real-world-onion-sites) repository.
* [x] Script that compiles configuration from the
      [the SecureDrop API](https://securedrop.org/api/v1/directory/).

## v0.0.1 - 2022-03-23

Main issue: https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/issues/1

### Basic

* [x] Take a list of onions to check and make sure that you can always fetch
      descriptors rather than just using cached descriptors etc.
* [x] Randomisation of timing to avoid systemic errors getting lucky and not
      detected.
* [x] Looping support: goes through the list of onions in a loop, testing one
      at a time continuously.
* [x] Flush descriptor caches so testing happens like if a fresh client.
* [x] Support for HTTP status codes.
* [x] Page load latency.
* [x] Ability to fetch a set of paths from each onion.
      Customisable by test path: not all our sites have content at the root,
      but do not bootstrap every time if that can be avoided.
* [x] Need to know about "does the site have useful content?"
      Regex for content inside the page: allow configuring a regex per path for
      what should be found in the returned content/headers.
* [x] Documentation.

### Meta

* [x] Dockerfile (and optionally a Docker Compose).

### Prometheus

* [x] Exports Prometheus metrics for the connection to the onion service, and
      extra metrics per path on the status code for each path returned by the server.
      If using the prometheus exporter with python, consider to just use request and
      beautiful soup to check that the page is returning what one expects.
* [x] Add in additional metrics wherever appropriate.
* [x] To get the timings right, the tool should take care of the test frequency and
      just expose the metrics rather than having Prometheus scraping individual
      targets on Prometheus' schedule.

### Bonus

* [x] Optionally launch it's [own Tor process](https://stem.torproject.org/api/process.html)
      like in [this example](https://stem.torproject.org/tutorials/to_russia_with_love.html#using-pycurl).
