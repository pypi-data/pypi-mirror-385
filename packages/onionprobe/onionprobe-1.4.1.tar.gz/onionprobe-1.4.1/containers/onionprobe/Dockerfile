#
# Dockerfile for Onionprobe.
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
#

FROM debian:bookworm
MAINTAINER Silvio Rhatto <rhatto@torproject.org>

ENV APP="onionprobe"
ENV APP_BASE="/srv/"
ENV SHELL="/bin/bash"
ENV ONIONPROBE_CONFIG="/srv/onionprobe/configs/tor.yaml"

# Set the PYTHONPATH in the container
ENV PYTHONPATH="/usr/lib/python3/dist-packages:/srv/onionprobe/packages"

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    apt-transport-https \
    ca-certificates \
    wget gnupg \
    python3-prometheus-client python3-stem python3-cryptography \
    python3-bs4 python3-yaml python3-pytest python3-requests \
    python3-socks

COPY configs/apt/tor.list /etc/apt/sources.list.d/tor.list
COPY scripts/get-tor-debian-key /usr/local/bin
RUN  /usr/local/bin/get-tor-debian-key /usr/share/keyrings/tor-archive-keyring.gpg
RUN  rm /usr/local/bin/get-tor-debian-key

# Install Tor and dependencies
RUN apt-get update && \
    apt-get install -y \
    deb.torproject.org-keyring \
    tor \
    && rm -rf /var/lib/apt/lists/*

WORKDIR ${APP_BASE}/${APP}

COPY . ${APP_BASE}/${APP}

USER debian-tor

ENTRYPOINT exec ${APP_BASE}/${APP}/onionprobe -c ${ONIONPROBE_CONFIG}
