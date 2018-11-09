# Copyright (c) 2018 Ken Bannister. All rights reserved.
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.

"""
Simple client tests to a libcoap server.

Requires:
   - RIOTBASE env variable for RIOT root directory

   - LIBCOAP_BASE env variable for libcoap root directory, or coap-server example
  executable on PATH.

   - Network with ULA fd00:bbbb::1/64
"""

import pytest
import os
import signal

from conftest import ExpectHost

#
# fixtures and utility functions
#

@pytest.fixture
def gcoap_example(request):
    """Runs a gcoap example process, and provides a pexpect spawn object to
       interact with it."""
    folder = os.environ.get('RIOTBASE', None)

    host = ExpectHost(os.path.join(folder, 'examples/gcoap'), 'make term')
    term = host.connect()
    # accepts either gcoap example app or riot-gcoap-test app
    term.expect('gcoap .* app')

    # set ULA
    host.send_recv('ifconfig 6 add unicast fd00:bbbb::2/64',
                   'success:')
    yield host

    # teardown
    host.disconnect()

@pytest.fixture
def libcoap_server(request):
    """Runs a libcoap example server process, and provides a pexpect spawn
       object to interact with it."""
    folder = os.environ.get('LIBCOAP_BASE', None)
    if folder:
        cmd = os.path.join('examples/coap-server')
    else:
        cmd = 'coap-server'

    host = ExpectHost(folder, cmd)
    term = host.connect()
    yield host

    # teardown
    host.disconnect()

#
# tests
#

def test_client_get(libcoap_server, gcoap_example):
    client = gcoap_example

    # expect like 'Nov 04 11:21:58'
    client.send_recv('coap get fd00:bbbb::1 5683 /time',
                     '\w+ \w+ \d+:\d+:')

