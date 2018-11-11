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
import logging

from conftest import ExpectHost

logging.basicConfig(level=logging.INFO)

pwd = os.getcwd()

#
# fixtures and utility functions
#

@pytest.fixture(scope='module', params=[2, 4])
def retry_server(request):
    """Runs a server that ignores requests as an ExpectHost."""
    cmd = './con_ignore_server.py -i {0}'.format(request.param)

    host = ExpectHost(pwd, cmd)
    term = host.connect()
    yield host

    # teardown
    host.disconnect()

#
# tests
#

def test_get_time(retry_server, gcoap_example):
    client = gcoap_example

    time.sleep(2)

    # expect response like '2018-11-04 11:21'
    client.send_recv('coap get -c fd00:bbbb::1 5683 /time',
                     r'\d+-\d+-\d+ \d+:\d')

