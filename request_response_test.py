# Copyright (c) 2018 Ken Bannister. All rights reserved.
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.

"""
Simple request and response tests to gcoap and nanocoap.
"""

import pytest
import logging
import os
import re
import signal
import time

from collections import Counter
from conftest import ExpectHost
from conftest import proto_params

pwd = os.getcwd()
logging.basicConfig(level=logging.INFO)

#
# fixtures and utility functions
#

@pytest.fixture
def aiocoap_client():
    """Runs an aiocoap client to query gcoap_example as a server."""
    # server handles same quantity of messages as client sends
    cmdText = './repeat_send_client.py -r [fd00:bbbb::2] -p /cli/stats -q {0} {1}'
    cmd = cmdText.format(10, '-c dtls-credentials.json' if proto_params['is_dtls'] else '')

    host = ExpectHost(pwd, cmd)
    term = host.connect()
    # allow a couple of seconds for initialization
    time.sleep(2)
    yield host

    # teardown
    host.disconnect()

@pytest.fixture
def qty_repeat(request):
    """Provides the number of times to repeat the request"""
    return int(request.config.getini('request_response_repeat'))

def send_recv(client, is_confirm):
    """
    GET time from server.

    :param ExpectHost client: Host that sends request
    :param boolean is_confirm: True if confirmable message
    """
    # expect like 'Nov 04 11:21:58'
    cmdText = 'coap get {0} fd00:bbbb::1 {1} /time'.format('-c' if is_confirm else '',
                                                            proto_params['port'])
    client.send_recv(cmdText, r'\w+ \w+ \d+:\d+:')

def send_recv_nano(client, server_addr):
    """
    nanocoap client specific implementation; does not support non-confirmable

    :param ExpectHost client: Host that sends request
    :param string server_addr: server address
    """
    # expect like 'Nov 04 11:21:58'
    client.send_recv('client get {0} 5683 /time'.format(server_addr),
                     r'\w+ \w+ \d+:\d+:')

#
# tests
#

def test_client_get(libcoap_server, gcoap_example):
    """Single, simple GET request, non-confirmable and confirmable"""
    send_recv(gcoap_example, False)
    send_recv(gcoap_example, True)

@pytest.mark.parametrize('request_path', ['/xyz'])
def test_server_no_resource(gcoap_example, libcoap_client, request_path):
    """Verify response when no matching resource.

       This test is more about resources rather than request/response, but
       putting it here as a first step."""
    output = libcoap_client.run()
    assert re.search(b'4.04', output) is not None

def test_client_get_nano(libcoap_server, nanocoap_cli):
    """Single, simple GET request, confirmable only. nanocoap_cli does not
       support non-confirmable requests."""
    board = os.environ.get('BOARD', 'native')
    addr  = None

    if board == 'native':
        addr = os.environ.get('TAP_LLADDR_REMOTE', None)
    else:
        return

    send_recv_nano(nanocoap_cli, addr)


def test_client_get_repeat(libcoap_server, gcoap_example, qty_repeat):
    """Repeats simple non-confirmable request. See qty_repeat in INI file."""
    for i in range(qty_repeat):
        send_recv(gcoap_example, False)
        time.sleep(1)

def test_client_server(libcoap_server, gcoap_example, qty_repeat, aiocoap_client):
    """
    Tests gcoap concurrently sending and receiving messages.

    Client: repeats simple non-confirmable request from gcoap
    Server: repeats simple confirmable request to gcoap
    """
    # gcoap client
    for i in range(qty_repeat):
        send_recv(gcoap_example, False)
        time.sleep(1)

    # wait for server to finish
    while aiocoap_client.term.isalive():
        time.sleep(2)

    # validate gcoap server from count of responses received by aiocoap_client
    qty = 0
    with open(r'repeat_send_client.log') as log:
        for line in log:
            qty += (1 if re.search('2.05 Content', line) else 0)

    assert qty == qty_repeat
