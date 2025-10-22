#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Onionprobe test/monitor tool.
#
# Copyright (C) 2022 The Tor Project, Inc.
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

# Dependencies
import logging
import datetime
import base64
import re

try:
    import stem
except ImportError:
    print("Please install stem library first!")
    raise ImportError

class OnionprobeDescriptor:
    """
    Onionprobe class with Tor descriptor-related methods.
    """

    def get_pubkey_from_address(self, address):
        """
        Extract .onion pubkey from the address

        Leaves out the .onion domain suffix and any existing subdomains.

        :type  address: str
        :param address: Onion Service address

        :rtype: str
        :return: Onion Service public key
        """

        # Extract
        pubkey = address[0:-6].split('.')[-1]

        return pubkey

    def get_endpoint_by_pubkey(self, pubkey):
        """
        Get an endpoint configuration given an Onion Service pubkey.

        :type  pubkey: str
        :param pubkey: Onion Service pubkey

        :rtype: tuple or False
        :return: Endpoint name and configuration if a match is found.
                 False otherwise.
        """

        endpoints = self.get_config('endpoints')

        for name in endpoints:
            if self.get_pubkey_from_address(endpoints[name]['address']) == pubkey:
                return (name, endpoints[name])

        return False

    def parse_pow_params(self, inner_text, labels):
        """
        Parse the Proof of Work (PoW) parameters from a descriptor.

        :type  inner_text: str
        :param inner_text: The decrypted raw inner descriptor layer plaintext for the endpoint.

        :type  labels: dict
        :param labels: Metrics labels

        :rtype:  None
        :return: This method does not return any special value.
        """

        pow_params    = re.compile(r"^pow-params .*$", re.MULTILINE)
        pow_params_v1 = re.compile(
                r"^pow-params v1 (?P<seed>[^ ]*) (?P<effort>[0-9]*) (?P<expiration>[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2})$",
                re.MULTILINE)

        pow_parsed    = pow_params.search(inner_text)
        pow_parsed_v1 = pow_params_v1.search(inner_text)

        if pow_parsed:
            self.log("Proof of Work (PoW) params found in the descriptor")
            self.set_metric('onion_service_pow_enabled', 1, labels)
        else:
            self.log("Proof of Work (PoW) params not found in the descriptor")
            self.set_metric('onion_service_pow_enabled', 0, labels)

        if pow_parsed_v1:
            pow_data_v1 = pow_parsed_v1.groupdict()
            expiration  = int(datetime.datetime.fromisoformat(pow_data_v1['expiration']).timestamp())

            # For the purposes of this proposal, all cryptographic algorithms
            # are assumed to produce and consume byte strings, even if
            # internally they operate on some other data type like 64-bit
            # words. This is conventionally little endian order for Blake2b,
            # which contrasts with Tor's typical use of big endian.
            #
            # -- https://spec.torproject.org/hspow-spec/v1-equix.html
            effort = int.from_bytes(base64.b64decode(pow_data_v1['seed']), 'little')

            self.log('PoW v1 set with effort {}, expiration {} and seed {}'.format(
                pow_data_v1['effort'],
                pow_data_v1['expiration'],
                pow_data_v1['seed'],
                ))

            self.set_metric('onion_service_pow_v1_seed',               effort,                     labels)
            self.set_metric('onion_service_pow_v1_effort',             int(pow_data_v1['effort']), labels)
            self.set_metric('onion_service_pow_v1_expiration_seconds', int(expiration),            labels)

    def get_descriptor(self, endpoint, config, attempt = 1):
        """
        Get Onion Service descriptor from a given endpoint

        :type  endpoint: str
        :param endpoint: The endpoint name from the 'endpoints' instance config.

        :type  config: dict
        :param config: Endpoint configuration

        :rtype: stem.descriptor.hidden_service.InnerLayer or False
        :return: The Onion Service descriptor inner layer on success.
                 False on error.
        """

        self.log('Trying to get descriptor for {} (attempt {})...'.format(config['address'], attempt))

        pubkey    = self.get_pubkey_from_address(config['address'])
        init_time = self.now()
        timeout   = self.get_config('descriptor_timeout')
        reachable = 1

        # Metrics labels
        labels = {
                'name'   : endpoint,
                'address': config['address'],
                }

        # Get the descriptor
        try:
            # Increment the total number of descriptor fetch attempts
            self.inc_metric('onion_service_descriptor_fetch_requests_total', 1, labels)

            # Try to get the descriptor
            descriptor = self.controller.get_hidden_service_descriptor(pubkey, timeout=timeout)

        except (stem.DescriptorUnavailable, stem.Timeout, stem.ControllerError, ValueError) as e:
            reachable = 0
            inner     = False
            retries   = self.get_config('descriptor_max_retries')

            # Try again until max retries is reached
            if attempt <= retries:
                return self.get_descriptor(endpoint, config, attempt + 1)

        else:
            # Calculate the elapsed time
            elapsed = self.elapsed(init_time, True, "descriptor fetch")

            self.set_metric('onion_service_descriptor_latency_seconds',
                            elapsed, labels)

            # Update the HSDir latency metric
            if self.get_pubkey_from_address(config['address']) in self.hsdirs:
                # Register HSDir latency
                [ hsdir_id, hsdir_name ] = str(
                        self.hsdirs[self.get_pubkey_from_address(
                            config['address'])]).split('~')

                #self.log('HSDir ID: {}, HSDir name: {}'.format(hsdir_id, hsdir_name))
                self.set_metric('hsdir_latency_seconds',
                                elapsed, {
                                    'name': hsdir_name,
                                    'id'  : hsdir_id,
                                    })

            # Debuging the outer layer
            self.log("Outer wrapper descriptor layer contents (decrypted):\n" + str(descriptor), 'debug')

            self.set_metric('onion_service_descriptor_outer_wrapper_size_bytes',
                    len(str(descriptor).encode('utf-8')), labels)

            # Ensure it's converted to the v3 format
            #
            # See https://github.com/torproject/stem/issues/96
            #     https://stem.torproject.org/api/control.html#stem.control.Controller.get_hidden_service_descriptor
            #     https://gitlab.torproject.org/legacy/trac/-/issues/25417
            from stem.descriptor.hidden_service import HiddenServiceDescriptorV3
            descriptor = HiddenServiceDescriptorV3.from_str(str(descriptor))

            # Decrypt the inner layer
            inner = descriptor.decrypt(pubkey)

            self.set_metric('onion_service_descriptor_second_layer_size_bytes',
                    len(str(inner._raw_contents).encode('utf-8')), labels)

            if descriptor.lifetime:
                self.log("Descriptor lifetime: " + str(descriptor.lifetime))
                self.set_metric('onion_service_descriptor_lifetime_seconds',
                                descriptor.lifetime * 60, labels)

            if descriptor.revision_counter:
                self.log("Descriptor revision counter: " + str(descriptor.revision_counter))
                self.set_metric('onion_service_descriptor_revision_counter',
                                descriptor.revision_counter, labels)

            self.log("Single service mode is set to " + str(inner.is_single_service))
            self.set_metric('onion_service_is_single', inner.is_single_service, labels)

            # Debuging the inner layer
            self.log("Second layer of encryption descriptor contents (decrypted):\n" + inner._raw_contents, 'debug')

            # Get introduction points
            # See https://stem.torproject.org/api/descriptor/hidden_service.html#stem.descriptor.hidden_service.IntroductionPointV3
            #for introduction_point in inner.introduction_points:
            #    self.log(introduction_point.link_specifiers, 'debug')

            if 'introduction_points' in dir(inner):
                self.log("Number of introduction points: " + str(len(inner.introduction_points)))
                self.set_metric('onion_service_introduction_points_number',
                                len(inner.introduction_points), labels)

            # Parse PoW parameters
            self.parse_pow_params(inner._raw_contents, labels)

        finally:
            if inner is False:
                self.inc_metric('onion_service_descriptor_fetch_error_total', 1, labels)
            #else:
            #    # Increment the total number of sucessful descriptor fetch attempts
            #    self.inc_metric('onion_service_descriptor_fetch_success_total', 1, labels)

            labels['reachable'] = reachable

            # Register the number of fetch attempts in the current probing round
            self.set_metric('onion_service_descriptor_fetch_attempts',
                            attempt, labels)

            # Return the inner layer or False
            return inner

    def hsdesc_event(
            self,
            event,
            ):
        """
        Process HS_DESC events.

        Sets the onion_service_descriptor_reachable metric.

        See https://spec.torproject.org/control-spec/replies.html#HS_DESC
            https://spec.torproject.org/control-spec/replies.html#HS_DESC_CONTENT

        :type  event : stem.response.events.HSDescEvent
        :param stream: HS_DESC event
        """

        if event.action not in [ 'RECEIVED', 'FAILED' ]:
            return

        # Get the endpoint configuration
        (name, endpoint) = self.get_endpoint_by_pubkey(event.address)

        # Metrics labels
        labels = {
                'name'   : name,
                'address': event.address + '.onion',
                }

        if event.action == 'RECEIVED':
            reason = event.action

            self.set_metric('onion_service_descriptor_reachable', 1, labels)

        elif event.action == 'FAILED':
            # See control-spec.txt section "4.1.25. HiddenService descriptors"
            # FAILED action is split into it's reasons
            reason = event.reason

            self.set_metric('onion_service_descriptor_reachable', 0, labels)

        # Descriptor reachability
        self.log("Descriptor reachability: " + str(reason))

        # Log the HSDir
        self.log("HSDir used: " + str(event.directory))

        self.info_metric('onion_service_descriptor', {
            'hsdir': event.directory,
            'state': reason,
            },
            labels)

        # Initialize the HSDirs object if needed
        if 'hsdirs' not in dir(self):
            self.hsdirs = {}

        # Register the HSDir where the descriptor was fetched
        self.hsdirs[event.address] = str(event.directory).split('$')[1]
