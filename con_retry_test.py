# Copyright (c) 2018 Ken Bannister. All rights reserved.
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.

"""
Tests CoAP confirmable message retry capability.

Sends a GET request to a server that ignores a configurable number of requests.
Tests both the gcoap example and a nanocoap client.

Requires:
   - RIOTBASE env variable for RIOT root directory

   - Network with ULA fd00:bbbb::1/64 for gcoap

   - Remote with TAP_LLADDR_REMOTE on native for nanocoap
"""

import pytest
import os
import pexpect
import time
import logging

from conftest import ExpectHost

logging.basicConfig(level=logging.INFO)

pwd = os.getcwd()

#
# fixtures and utility functions
#

@pytest.fixture
def retry_server(ignores):
    """Runs a server that ignores requests as an ExpectHost."""

    cmd = './con_ignore_server.py -i {0}'.format(ignores)

    host = ExpectHost(pwd, cmd)
    term = host.connect()
    # allow a couple of seconds for initialization
    time.sleep(2)
    yield host

    # teardown
    host.disconnect()


@pytest.fixture
def ignores():
    """Count of requests to ignore."""
    return 0

def send_recv(client):
    # expects time value formatted like '2018-11-04 17:20'
    client.send_recv('coap get -c fd00:bbbb::1 5683 /time',
                     r'\d+-\d+-\d+ \d+:\d')

def send_recv_nano(client, server_addr):
    """
    nanocoap client specific implementation; no '-c' switch, always
    confirmable
    """
    # expects time value formatted like '2018-11-04 17:20'
    client.send_recv('client get {0} 5683 /time'.format(server_addr),
                     r'\d+-\d+-\d+ \d+:\d')

#
# tests
#

@pytest.mark.parametrize('ignores', [2])
def test_recover(retry_server, gcoap_example, ignores):
    """Recover from 2 ignored requests and receive time value."""
    send_recv(gcoap_example)

@pytest.mark.parametrize('ignores', [2])
def test_recover_nano(retry_server, nanocoap_cli, ignores):
    """
    Recover from 2 ignored requests and receive time value. nanocoap client
    specific implementation. Only runs on native due to address limitation
    with nanocoap_cli app.
    """
    board = os.environ.get('BOARD', 'native')
    addr  = None
    
    if board == 'native':
        addr = os.environ.get('TAP_LLADDR_REMOTE', None)
    else:
        return

    send_recv_nano(nanocoap_cli, addr)


@pytest.mark.parametrize('ignores', [5])
def test_timeout(retry_server, gcoap_example, ignores):
    """Times out from 5 ignored requests."""
    gcoap_example.timeout = 100

    with pytest.raises(pexpect.TIMEOUT):
        send_recv(gcoap_example)


@pytest.mark.parametrize('ignores', [5])
def test_timeout_nano(retry_server, nanocoap_cli, ignores):
    """Times out from 5 ignored requests. nanocoap client specific
    implementation. Only runs on native due to address limitation
    with nanocoap_cli app.
    """
    board = os.environ.get('BOARD', 'native')
    addr  = None

    if board == 'native':
        addr = os.environ.get('TAP_LLADDR_REMOTE', None)
    else:
        return

    nanocoap_cli.timeout = 100

    with pytest.raises(pexpect.TIMEOUT):
        send_recv_nano(nanocoap_cli, addr)
