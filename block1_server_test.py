# Copyright (c) 2018 Ken Bannister. All rights reserved.
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.

"""
Tests POSTing a large payload to a RIOT CoAP server via block1.
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

@pytest.fixture(scope='module', params=[16, 32, 64])
def block_size(request):
    """Provides the size of the block to test."""
    return request.param


@pytest.fixture
def pkt_block_server():
    """
    Provides a block server that uses Packet API functions to build the
    response.
    """
    base_folder = os.environ.get('RIOTAPPSBASE', None)
    board       = os.environ.get('BOARD', 'native')

    term_cmd = 'make term'
    term_resp = 'gcoap block handler'
        
    host = ExpectHost(os.path.join(base_folder, 'gcoap-block-server'), term_cmd)
    term = host.connect()
    term.expect(term_resp)

    # set ULA
    pid = '5' if proto_params['is_dtls'] else '6'
    cmd = 'ifconfig {0} add unicast fd00:bbbb::2/64'.format(pid)
    host.send_recv(cmd, 'success:')

    yield host

    # teardown
    host.disconnect()

#
# tests
#

def run_block1(server_addr, block_size):
    """Runs block1 test"""
    signature = b'C496DF5946783990BEC5EFDC2999530EEB9175B83094BAE66170FF2431FC896E'

    cmd = './block1_client.py -r [{0}] -b {1} {2}'
    host = ExpectHost(pwd, cmd.format(server_addr, block_size,
                                      '-c dtls-credentials.json' if proto_params['is_dtls'] else ''))

    output = host.run()
    assert re.search(b'2.04 Changed', output)
    assert re.search(signature, output)

def test_block1_buf(nanocoap_server, block_size):
    """Handle block1 request for Buffer API based server."""
    address = os.environ.get('TAP_LLADDR_SUT', None)
    run_block1(address, block_size)

def test_block1_pkt(pkt_block_server, block_size):
    """Handle block1 request for Packet API based server."""
    server_addr = 'fd00:bbbb::2'
    run_block1(server_addr, block_size)
