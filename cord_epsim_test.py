# Copyright (c) 2018 Ken Bannister. All rights reserved.
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.

"""
Tests simple registration to a CORE Resource Directory server.

Requires cord_epsim example is compiled with unicast address of RD server
(RD_ADDR). By default the example uses the link local all nodes multicast
address (ff02::1).
"""

import pytest
import logging
import os
import pexpect
import re
import time

from conftest import ExpectHost

logging.basicConfig(level=logging.INFO)

#
# fixtures and utility functions
#

@pytest.fixture
def cord_cli():
    """Runs the RIOT cord_epsim example process as an ExpectHost."""
    base_folder = os.environ.get('RIOTBASE', None)

    host = ExpectHost(os.path.join(base_folder, 'examples/cord_epsim'), 'make term')
    term = host.connect()
    term.expect('Simplified CoRE RD registration example')
    yield host

    # teardown
    host.disconnect()


@pytest.fixture
def rd_server():
    """Runs an aiocoap Resource Directory server as an ExpectHost."""
    folder = os.environ.get('AIOCOAP_BASE', None)

    host = ExpectHost(folder, './aiocoap-rd')
    term = host.connect()
    # allow a couple of seconds for initialization
    time.sleep(2)
    yield host

    # teardown
    host.disconnect()


@pytest.fixture
def libcoap_client(request_path):
    """Runs a libcoap example client as an ExpectHost to retrieve a response."""
    folder = os.environ.get('LIBCOAP_BASE', None)
    cmd_folder = folder + '/examples/' if folder else ''
    addr   = os.environ.get('TAP_LLADDR_SUT', None)

    cmd = '{0}coap-client -N -m get -T 5a -U coap://[{1}]{2}'
    cmd_text = cmd.format(cmd_folder, addr, request_path)

    host = ExpectHost(folder, cmd_text)
    yield host


@pytest.fixture
def request_path():
    """Provides the URI to request on the cord_epsim server"""
    return '/.well-known/core'

#
# tests
#

def test_run(rd_server, cord_cli):
    """Test expected output after connection to rd server"""
    # must read to end of output from startup
    cord_cli.term.expect('RD address:.*$')

    # attempting to re-register
    cord_cli.term.expect('updating registration with RD.*$', 60)

    # not expecting warning, which indicates failed to contact server
    with pytest.raises(pexpect.TIMEOUT):
        cord_cli.term.expect('warning: registration already in progress', 60)

def test_no_server(cord_cli):
    """Test expected failure when no rd server"""
    # must read to end of output from startup
    cord_cli.term.expect('RD address:.*$')

    cord_cli.term.expect('warning: registration already in progress', 60)

@pytest.mark.parametrize('request_path', ['/riot/foo', '/riot/info'])
def test_server(cord_cli, libcoap_client, request_path):
    """Test expected output from cord_cli resources"""
    # allow a couple of seconds for cord_cli to initialize
    time.sleep(2)

    output = libcoap_client.run()
    logging.info('output {0}'.format(output))

    if request_path == '/riot/foo':
        assert re.search(b'bar', output) is not None
    elif request_path == '/riot/info':
        assert re.search(b'{"ep":.*,"lt":', output) is not None
    else:
        pytest.fail('unknown request_path')
