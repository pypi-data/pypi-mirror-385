#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Onionprobe test/monitor tool.
#
# Copyright (C) 2023 Silvio Rhatto <rhatto@torproject.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import ssl

from datetime import datetime, timezone

from cryptography.x509              import load_pem_x509_certificate, oid, DNSName
from cryptography.hazmat.primitives import hashes

class OnionprobeCertificate:
    """
    Onionprobe class with X.509 Certificate methods.
    """

    def get_dns_alt_names_from_cert(self, cert, format='tuple'):
        """
        Get the DNS names from a X.509 certificate's SubjectAltName extension.

        :type  cert: cryptography.x509.Certificate
        :param cert: The X.509 Certificate object.

        :type  format: str
        :param format: The output format, either 'list' or 'tuple' in the
                       same format returned by SSLSocket.getpeercert and
                       accepted by ssl.match_hostname.

        :rtype: list or tuple
        :return: The list or tuple with the certificate's DNS Subject
                 Alternative Names.

        """

        dns_alt_names = cert.extensions.get_extension_for_oid(
                oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME
                ).value.get_values_for_type(DNSName)

        if format == 'tuple':
            dns_alt_names = tuple(('DNS', item) for item in dns_alt_names)

        return dns_alt_names

    def get_cert_rdns(self, cert, field = 'issuer', format = 'tuple'):
        """
        Get the Relative Distinguished Names (RDNs) from a given X.509
        certificate field like issuer or subject.

        :type field: str
        :param field: The name of the X.509 certificate field
                      ('issuer' or 'subject').

        :type  format: str
        :param format: The output format, either 'list' or 'tuple' in the
                       same format returned by SSLSocket.getpeercert and
                       accepted by ssl.match_hostname.

        :rtype: dict or tuple
        :return: The dict or tuple with the certificate's DNS Subject
                 Alternative Names.

        :type  cert: cryptography.x509.Certificate
        :param cert: The X.509 Certificate object.

        """

        items = {}

        for item in getattr(cert, field):
            name = item.oid._name

            if name not in items:
                items[name] = []

            items[name].append(item.value)

        if format == 'dict':
            return items

        result = []

        for name in items:
            result.append(tuple((name, item) for item in items[name]))

        return tuple(result)

    def get_cert_validity_interval(self, cert, timestamp=False):
        """
        Handle deprecation transition on certificate validity.

        cryptography.x509.Certificate.not_valid_before and
        cryptography.x509.Certificate.not_valid_after deprecated in favor of
        cryptography.x509.Certificate.not_valid_before_utc and
        cryptography.x509.Certificate.not_valid_after_utc

        Details:

        https://gitlab.torproject.org/tpo/onion-services/onionprobe/-/issues/92
        https://cryptography.io/en/44.0.2/x509/reference/#cryptography.x509.Certificate.not_valid_before
        https://cryptography.io/en/44.0.2/x509/reference/#cryptography.x509.Certificate.not_valid_before_utc
        https://cryptography.io/en/44.0.2/x509/reference/#cryptography.x509.Certificate.not_valid_after
        https://cryptography.io/en/44.0.2/x509/reference/#cryptography.x509.Certificate.not_valid_after_utc

        :type  cert: cryptography.x509.Certificate
        :param cert: The X.509 Certificate object.

        :type  timestamp: bol
        :param timestamp: Whether the return values should be converted to a timestamp.
                          Defaults to False.

        :rtype: typle
        :return: Pair of certificate not valid before and not valid after timestamps.

        """

        if 'not_valid_before_utc' in dir(cert):
            not_valid_before = cert.not_valid_before_utc
            not_valid_after  = cert.not_valid_after_utc
        else:
            not_valid_before = cert.not_valid_before
            not_valid_after  = cert.not_valid_after

        if timestamp:
            return (not_valid_before.timestamp(), not_valid_after.timestamp())

        return (not_valid_before, not_valid_after)

    def get_cert_info(self, cert, format = 'tree'):
        """
        Get basic information from a X.509 certificate.

        This method is compatible with SSLSocket.geetpeercert, with the
        advantage that it does not require a valid certificate in order
        to process it's data.

        :type  cert: cryptography.x509.Certificate
        :param cert: The X.509 Certificate object.

        :type  format: str
        :param format: The output format, either 'tree' or 'flat'.
                       The 'tree' format is the same as returned
                       returned by SSLSocket.getpeercert and
                       accepted by ssl.match_hostname. The 'flat' format
                       uses just one level of key-value pairs, and all
                       values are strings, and is accepted by Prometheus
                       info metrics.

        :rtype: dict
        :return: Dictionary with basic certificate information in the same
                 format returned by SSLSocket.getpeercert and accepted by
                 ssl.match_hostname, additionally with certificate
                 fingerprints.

        """

        # Date format is the same from ssl.cert_time_to_seconds
        date_format = '%b %d %H:%M:%S %Y %Z'

        (not_valid_before, not_valid_after) = self.get_cert_validity_interval(cert)

        # The info dictionary
        info = {
                'issuer'           : self.get_cert_rdns(cert, 'issuer'),
                'subject'          : self.get_cert_rdns(cert, 'subject'),
                'subjectAltName'   : self.get_dns_alt_names_from_cert(cert),

                # Convert to aware datetime formats since
                # cryptography.x509.Certificate uses naive objects by default
                'notAfter'         : not_valid_after.replace(
                    tzinfo=timezone.utc).strftime(date_format),
                'notBefore'        : not_valid_before.replace(
                    tzinfo=timezone.utc).strftime(date_format),

                'serialNumber'     : str(cert.serial_number),
                'version'          : int(str(cert.version).replace('Version.v', '')),

                'fingerprintSHA1'  : cert.fingerprint(hashes.SHA1()).hex(':').upper(),
                'fingerprintSHA256': cert.fingerprint(hashes.SHA256()).hex(':').upper(),
        }

        if format == 'flat':
            info['version']        = str(info['version'])
            info['issuer']         = cert.issuer.rfc4514_string()
            info['subject']        = cert.subject.rfc4514_string()
            info['subjectAltName'] = ' '.join(self.get_dns_alt_names_from_cert(cert, 'list'))

        return info

    def get_certificate_expiration(self, cert):
        """
        Get the number of seconds remaining before a X.509 certificate expires,
        or the number of seconds passed since it's expiration.

        :type  cert: cryptography.x509.Certificate
        :param cert: The X.509 Certificate object.

        :rtype: int
        :return: Number of seconding remaining before the certificate
                 expiration (if positive) or the number of seconds passed since the
                 expiration (if negative).

        """

        (not_valid_before, not_valid_after) = self.get_cert_validity_interval(cert)

        not_valid_after = not_valid_after.replace(tzinfo=timezone.utc).timestamp()
        now             = datetime.now(timezone.utc).timestamp()

        return int(not_valid_after - now)

    def match_certificate_hostname(self, info, address):
        """
        Since Python 3.12, ssl.match_hostname is not available anymore.

        Details at

          https://docs.python.org/3.12/library/ssl.html
          https://docs.python.org/3.12/whatsnew/changelog.html#id202
          https://github.com/python/cpython/issues/94199#issuecomment-1165682234
          https://github.com/python/cpython/pull/94224
          https://bugs.python.org/issue43880

        We cannot just ignore this check, since we're using the following
        on tls.py:

          context.check_hostname = False
          context.verify_mode    = ssl.CERT_NONE

        We could try to detect existing implementations, in older systems.

        And we could ship the old Python 3.11 implementation for newer
        systems (by copying/adapting match_hostname() and _dnsname_match()
        from ssl.py: https://github.com/python/cpython/blob/3.11/Lib/ssl.py

        But that would require to redistribute around 100 lines of code
        under a different license, which could be complicated.

        Also, we don't need the full hostname matching logic as defined
        by RFC 2818, RFC 5280 and RFC 6125. We can use something stricter
        than that, for the case of .onion addresses (RFC 7686).

        Therefore we roll or own implementation, inspired by the original
        ssl.match_hostname().

        :type  info: dict
        :param info: Certificate information as returned by get_cert_info().

        :type  address: str
        :param address: An Onion Service address.

        :rtype: str
        :return: The matching hostname in the certificate
                 Raises ssl.CertificateError otherwise.

        """

        # Unused approach: try to use the old deprecated ssl.match_hostname(),
        # or go with a copied/adapted version shipped in Onionprobe's codebase.
        #if 'match_hostname' in dir(ssl):
        #    # Still available
        #    # https://docs.python.org/3.11/library/ssl.html#ssl.match_hostname
        #    ssl_match_hostname = ssl.match_hostname
        #else:
        #    # Use a built-in replacement for ssl.match_hostname, based on
        #    # the implementation from Python 3.11.
        #    #
        #    # Check also
        #    # https://github.com/brandon-rhodes/backports.ssl_match_hostname
        #    from .ssl import match_hostname as match_hostname

        # Helper function
        #
        # Check if a DNS value matches a given address.
        # Returns the value on success, and False otherwise.
        def match_hostname(value, address):
            # Use lowercase matching
            value   = value.lower()
            address = address.lower()

            if value == address:
                return value

            # Wildcard handling
            if value[0:2] == '*.':
                address_parts = address.partition('.')
                value_parts   = value.partition('.')

                if value_parts[2] == address_parts[2]:
                    return value

            return False

        # Start by checking the Common Name
        if 'subject' in info:
            for item in info['subject']:
                (field, value) = item[0]

                if field == 'commonName':
                    match = match_hostname(value, address)

                    if match:
                        return match

        # Then check the subjectAltName (SAN)
        if 'subjectAltName' in info:
            for alt in info['subjectAltName']:
                (field, value) = alt

                if field == 'DNS':
                    match = match_hostname(value, address)

                    if match:
                        return match

        raise ssl.CertificateError

    def get_certificate(self, endpoint, config, tls):
        """
        Get the certificate information from a TLS connection.

        :type  endpoint: str
        :param endpoint: The endpoint name from the 'endpoints' instance config.

        :type  config: dict
        :param config: Endpoint configuration

        :type  tls: ssl.SSLSocket
        :param tls: The TLS socket connection to the endpoint.

        :rtype: cryptography.x509.Certificate or False
        :return: The X.509 certificate object on success.
                 False on error.

        """

        try:
            # We can't rely on ssl.getpeercert() if the certificate wasn't validated
            #cert_info = tls.getpeercert()

            self.log('Retrieving certificate information for {} on port {}'.format(
                    config['address'], config['port']))

            der_cert         = tls.getpeercert(binary_form=True)
            pem_cert         = ssl.DER_cert_to_PEM_cert(der_cert)
            cert             = load_pem_x509_certificate(bytes(pem_cert, 'utf-8'))
            result           = cert

            (not_valid_before, not_valid_after) = self.get_cert_validity_interval(cert, timestamp=True)

            info             = self.get_cert_info(cert)
            expiry           = self.get_certificate_expiration(cert)
            match_hostname   = 1
            labels           = {
                    'name'    : endpoint,
                    'address' : config['address'],
                    'port'    : config['port'],
                    }

            try:
                match = self.match_certificate_hostname(info, config['address'])

                self.log('Found a matching hostname {} for {} in the certificate'.format(
                    match,
                    config['address']), 'debug')

            except ssl.CertificateError as e:
                match_hostname = 0

                self.log('No hostnames in the certificate matches {}'.format(
                    config['address']), 'debug')

            self.info_metric('onion_service_certificate', self.get_cert_info(cert, 'flat'), labels)

            self.set_metric('onion_service_certificate_not_valid_before_timestamp_seconds',
                    not_valid_before, labels)
            self.set_metric('onion_service_certificate_not_valid_after_timestamp_seconds',
                    not_valid_after, labels)
            self.set_metric('onion_service_certificate_expiry_seconds', expiry,         labels)
            self.set_metric('onion_service_certificate_match_hostname', match_hostname, labels)

            message = 'Certificate for {address} on {port} has subject: {subject}; ' + \
                      'issuer: {issuer}; serial number: {serial_number}; version: {version}; ' + \
                      'notBefore: {not_before}; notAfter: {not_after}; SHA256 fingerprint: ' + \
                      '{fingerprint}'

            self.log(message.format(
                address       = config['address'],
                port          = config['port'],
                subject       = cert.subject.rfc4514_string(),
                issuer        = cert.issuer.rfc4514_string(),
                serial_number = info['serialNumber'],
                version       = str(info['version']),
                not_before    = info['notBefore'],
                not_after     = info['notAfter'],
                fingerprint   = info['fingerprintSHA256'],
                ))

            if expiry <= 0:
                self.log('The certificate for {address} on port {port} expired {days} days ago'.format(
                    address = config['address'],
                    port    = config['port'],
                    days    = str(int(-1 * expiry / 86400)),
                    ), 'error')

        except Exception as e:
            result    = False
            exception = 'generic_error'

            self.log(e, 'error')

        finally:
            return result
