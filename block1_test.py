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

pwd = os.getcwd()

#
# fixtures and utility functions
#

@pytest.fixture(scope='module', params=[16, 32, 64])
def block_size(request):
    """Provides the size of the block to test."""
    return request.param


@pytest.fixture
def struct_block_server():
    """
    Provides a block server that uses struct-based functions to build the
    response. Used for development testing until merged into RIOT mainline.
    """
    base_folder = os.environ.get('RIOTAPPSBASE', None)
    board       = os.environ.get('BOARD', 'native')

    term_cmd = 'make term'
    term_resp = 'gcoap block handler'
        
    host = ExpectHost(os.path.join(base_folder, 'gcoap-block'), term_cmd)
    term = host.connect()
    term.expect(term_resp)

    # set ULA
    host.send_recv('ifconfig 6 add unicast fd00:bbbb::2/64','success:')

    yield host

    # teardown
    host.disconnect()

#
# tests
#

def run_block1(server_addr, block_size):
    """Runs block1 test"""
    signature = b'C496DF5946783990BEC5EFDC2999530EEB9175B83094BAE66170FF2431FC896E'

    cmd = './block1_client.py -r [{0}] -b {1}'
    host = ExpectHost(pwd, cmd.format(server_addr, block_size))

    output = host.run()
    assert re.search(b'2.04 Changed', output)
    assert re.search(signature, output)

def test_block1_buf(nanocoap_server, block_size):
    """Handle block1 request for buffer-based server."""
    address = os.environ.get('TAP_LLADDR_SUT', None)
    run_block1(address, block_size)

def test_block1_struct(struct_block_server, block_size):
    """Handle block1 request for struct-based server."""
    server_addr = 'fd00:bbbb::2'
    run_block1(server_addr, block_size)
