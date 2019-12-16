# Copyright (c) 2018 Ken Bannister. All rights reserved.
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.

"""
Tests GETting a large payload from gcoap via block2.
"""

import pytest
import os
import re

from conftest import ExpectHost
from conftest import proto_params

pwd = os.getcwd()

#
# fixtures and utility functions
#

@pytest.fixture(scope='module', params=[16])
def block_size(request):
    """Provides the size of the block to test."""
    return request.param

@pytest.fixture(scope='module', params=[True, False])
def is_confirm(request):
    """Selects for a confirmable or non-confirmable request ."""
    return request.param


@pytest.fixture
def block_server():
    """
    Provides a block server that uses Packet API functions to build the
    response.
    """
    base_folder = os.environ.get('RIOTAPPSBASE', None)
    board       = os.environ.get('BOARD', 'native')

    term_cmd = 'make term'
    term_resp = 'gcoap block handler'
        
    host = ExpectHost(os.path.join(base_folder, 'gcoap-block-server'), term_cmd,
                      putenv={'PORT':'tap1'})
    term = host.connect()
    term.expect(term_resp)

    # set ULA
    pid = '5' if proto_params['is_dtls'] else '6'
    cmd = 'ifconfig {0} add unicast fd00:bbbb::1/64'.format(pid)
    host.send_recv(cmd, 'success:')

    yield host

    # teardown
    host.disconnect()


@pytest.fixture
def nano_block_client():
    """
    Provides an ExpectHost that runs the nanocoap block client app.
    """
    base_folder = os.environ.get('RIOTAPPSBASE', None)

    host = ExpectHost(os.path.join(base_folder, 'nano-block-client'), 'make term')
    term = host.connect()
    term.expect('nanocoap block client app')

    # set ULA
    host.send_recv('ifconfig 5 add unicast fd00:bbbb::2/64','success:')

    yield host

    # teardown
    host.disconnect()

#
# tests
#

def test_block2_pkt(gcoap_example, block_server, block_size, is_confirm):
    """Handle block2 server response for Packet API based client. Tests
    confirmable and non-confirmable request.
    """
    cmd_text = 'coap get {0} fd00:bbbb::1 {1} /riot/ver'.format('-c' if is_confirm else '',
                                                                proto_params['port'])
    gcoap_example.send_recv(cmd_text, r'This is RIOT \(Ve.*blockwise complete')

def test_block2_buf(nano_block_client, block_server, block_size):
    """Handle block2 server response for Packet API based client."""
    nano_block_client.send_recv('get fd00:bbbb::1 5683',
                                r'This is RIOT \(Ve.*native MCU.')
