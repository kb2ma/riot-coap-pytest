# Copyright (c) 2018 Ken Bannister. All rights reserved.
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.

"""
Tests simple registration to a CORE Resource Directory server.

Requires cord_epsim example is compiled with unicast address of RD server
(RD_ADDR). By default the example uses TAP_LLADDR_EXT defined in setup_env.sh.
"""

import pytest
import os
import pexpect
import time

from conftest import ExpectHost

#
# fixtures and utility functions
#

@pytest.fixture
def cord_cli():
    """Runs the RIOT cord_ep example process as an ExpectHost."""
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

#
# tests
#

def test_run(rd_server, cord_cli):
    # ensure compiled with RD server address
    with pytest.raises(pexpect.TIMEOUT):
        cord_cli.term.expect(r'\[::1\]')

    # initial response
    cord_cli.term.expect(r'lt:.*s\r\n')
    cord_cli.term.expect(r'updating registration with RD \[fe80::.*5683\r\n')

    # verify re-registration
    cord_cli.term.expect(r'updating registration with RD \[fe80::.*5683\r\n', 60)

    # verify no error, likely caused by overflowing PDU resend buffer if no
    # ACK from server
    with pytest.raises(pexpect.TIMEOUT):
        cord_cli.term.expect(r'(error|warning)', 120)
