# Copyright (c) 2018 Ken Bannister. All rights reserved.
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.

"""Tests registration to a CORE Resource Directory server."""

import pytest
import logging
import os
import re
import time

from conftest import ExpectHost

#
# fixtures and utility functions
#

@pytest.fixture
def cord_cli():
    """Runs the RIOT cord_ep example process as an ExpectHost."""
    base_folder = os.environ.get('RIOTBASE', None)

    host = ExpectHost(os.path.join(base_folder, 'examples/cord_ep'), 'make term')
    term = host.connect()
    term.expect('CoRE RD client example!')

    # set ULA
    host.send_recv('ifconfig 7 add unicast fd00:bbbb::2/64',
                   'success:')
    yield host

    # teardown
    host.disconnect()


@pytest.fixture
def rd_server():
    """Runs an aiocoap Resource Directory server as an ExpectHost."""
    folder = os.environ.get('LIBCOAP_BASE', None)

    cmd = '{0}coap-rd'.format('examples/' if folder else '')
    host = ExpectHost(folder, cmd)
    term = host.connect()
    # allow a couple of seconds for initialization
    time.sleep(2)
    yield host

    # teardown
    host.disconnect()

#
# tests
#

def test_discover(rd_server, cord_cli):
    cord_cli.send_recv('cord_ep discover [fd00:bbbb::1]',
                       'registration interface is')

def test_register(rd_server, cord_cli):
    cord_cli.send_recv('cord_ep register [fd00:bbbb::1]',
                       'registration successful')

    # verify automatic re-registration
    cord_cli.term.expect('successfully updated client registration', 60)

    # cancel
    cord_cli.send_recv('cord_ep remove',
                       'dropped client registration')

def test_update(rd_server, cord_cli):
    cord_cli.send_recv('cord_ep register [fd00:bbbb::1]',
                       'registration successful')

    time.sleep(10)
    # update
    cord_cli.send_recv('cord_ep update',
                       'RD update successful')

    # cancel
    cord_cli.send_recv('cord_ep remove',
                       'dropped client registration')

@pytest.mark.parametrize('request_path', ['/sense/temp', '/node/info'])
def test_server(cord_cli, libcoap_client, request_path):
    """Test expected output from cord_cli resources"""
    # allow a couple of seconds for cord_cli to initialize
    time.sleep(2)

    output = libcoap_client.run()
    logging.info('output {0}'.format(output))

    if request_path == '/sense/temp':
        assert re.search(b'23', output) is not None
    elif request_path == '/node/info':
        assert re.search(b'INFORMATION', output) is not None
    else:
        pytest.fail('unknown request_path')
