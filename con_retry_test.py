# Copyright (c) 2018-2019 Ken Bannister. All rights reserved.
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.

"""
Tests CoAP confirmable message retry capability.

Sends a GET request from gcoap to a libcoap server that ignores a configurable
number of requests.

Requires:
   - RIOTBASE env variable for RIOT root directory

   - Network with ULA fd00:bbbb::1/64
"""

import pytest
import pexpect
import logging

from conftest import proto_params

logging.basicConfig(level=logging.INFO)

#
# fixtures and utility functions
#

def send_recv(client):
    client.send_recv('coap get -c fd00:bbbb::1 {0} /time'.format(proto_params['port']),
                     r'\w+ \w+ \d+:\d+:')

#
# tests
#

@pytest.mark.parametrize('libcoap_ignore_count', [2])
def test_recover(libcoap_server, gcoap_example):
    """Recover from 2 ignored requests and receive time value."""

    send_recv(gcoap_example)

@pytest.mark.parametrize('libcoap_ignore_count', [5])
def test_timeout(libcoap_server, gcoap_example):
    """Times out from 5 ignored requests."""
    gcoap_example.timeout = 100

    with pytest.raises(pexpect.TIMEOUT):
        send_recv(gcoap_example)
