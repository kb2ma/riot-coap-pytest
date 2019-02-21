# Copyright (c) 2018 Ken Bannister. All rights reserved.
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.

"""
Tests POSTing a large payload to gcoap via block1.
"""

import pytest
import os
import re

from conftest import ExpectHost

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
                      env={'PORT':'tap1'})
    term = host.connect()
    term.expect(term_resp)

    # set ULA
    host.send_recv('ifconfig 6 add unicast fd00:bbbb::1/64','success:')

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


@pytest.fixture
def gcoap_block_client():
    """
    Provides an ExpectHost that runs the nanocoap block client app.
    """
    base_folder = os.environ.get('RIOTAPPSBASE', None)

    host = ExpectHost(os.path.join(base_folder, 'gcoap-block-client'), 'make term')
    term = host.connect()
    term.expect('gcoap block client')

    # set ULA
    host.send_recv('ifconfig 6 add unicast fd00:bbbb::2/64','success:')

    yield host

    # teardown
    host.disconnect()

#
# tests
#

def test_block1_buf(nano_block_client, block_server, block_size):
    """Handle block2 server response for Packet API based client."""
    signature = 'C496DF5946783990BEC5EFDC2999530EEB9175B83094BAE66170FF2431FC896E'

    nano_block_client.send_recv('post fd00:bbbb::1 5683', signature)

def test_block1_pkt(gcoap_block_client, block_server, block_size):
    """Handle block2 server response for Packet API based client."""
    signature = 'C496DF5946783990BEC5EFDC2999530EEB9175B83094BAE66170FF2431FC896E'

    gcoap_block_client.send_recv('coap post fd00:bbbb::1 5683', signature)
