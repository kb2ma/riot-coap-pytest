# Copyright (c) 2018 Ken Bannister. All rights reserved.
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.

"""
Tests CoAP retry capability.

Sends a GET request from gcoap to a server that ignores the request for a
configurable timeout.

Requires:
   - RIOTBASE env variable for RIOT root directory

   - Network with ULA fd00:bbbb::1/64
"""

import pytest
import os
import time

from conftest import ExpectHost

#
# fixtures and utility functions
#

@pytest.fixture
def time_server():
    """Runs a time server as an ExpectHost."""
    cmd = './con_retry_server.py -d 5'

    host = ExpectHost(None, cmd)
    term = host.connect()
    yield host

    # teardown
    host.disconnect()

#
# tests
#

def test_get_time(time_server, gcoap_example):
    client = gcoap_example

    # expect response like 'Nov 04 11:21:58'
    client.send_recv('coap get -c fd00:bbbb::1 5683 /time',
                     '\d+-\d+-\d+ \d+:\d')
