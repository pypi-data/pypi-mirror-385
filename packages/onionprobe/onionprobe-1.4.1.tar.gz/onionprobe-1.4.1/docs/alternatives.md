# Alternatives to Onionprobe

* [OnionScan](https://onionscan.org/)
* [Webmon](https://webmon.dev.akito.ooo/) has support for Onion Services
  monitoring if used along with [Orbot](https://guardianproject.info/apps/org.torproject.android/).
* [BrassHornCommunications/OnionWatch: A GoLang daemon for notifying Tor Relay and Hidden Service admins of status changes](https://github.com/BrassHornCommunications/OnionWatch)
* [systemli/prometheus-onion-service-exporter: Prometheus Exporter for Tor Onion Services](https://github.com/systemli/prometheus-onion-service-exporter)
* [prometheus/blackbox_exporter: Blackbox prober
  exporter](https://github.com/prometheus/blackbox_exporter), which could be
  configured using `proxy_url` pointing to a [Privoxy](http://www.privoxy.org/)
  instance relaying traffic to `tor` daemon. See [this
  issue](https://github.com/prometheus/blackbox_exporter/issues/264) for details.
