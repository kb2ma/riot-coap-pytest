# Copyright (c) 2018 Ken Bannister. All rights reserved.
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.

"""
Tests POSTing a large payload via block1 to nanocoap.
"""

import pytest
import os
import re

from conftest import ExpectHost

pwd = os.getcwd()

#
# fixtures and utility functions
#

@pytest.fixture(scope='module', params=[16, 64])
def block_size(request):
    """Provides the size of the block to test."""
    return request.param

#
# tests
#

def test_block1(nanocoap_server, block_size):
    """Verify signature for payload in block1_client."""
    address = 'fe80::200:bbff:febb:2%tap0'
    signature = b'BEF6D998FB07110712EC8DC5AF83EE399EAC875F7FE44423348A0E0D8254C8AA'

    host = ExpectHost(pwd, './block1_client.py -r [{0}] -b {1}'.format(address, block_size))

    output = host.run()
    assert re.search(b'2.04 Changed', output)
    assert re.search(signature, output)
