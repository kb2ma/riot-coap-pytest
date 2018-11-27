# Copyright (c) 2018 Ken Bannister. All rights reserved.
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.

"""
Tests GETting a large payload from nanocoap via block2.
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

def test_block2(nanocoap_server, block_size):
    """Verify response from block2_client."""
    address = os.environ.get('TAP_LLADDR_SUT', None)
    response = b'This is RIOT \\(Version'

    host = ExpectHost(pwd, './block2_client.py -r [{0}] -b {1}'.format(address, block_size))

    output = host.run()
    assert re.search(b'2.05 Content', output)
    assert re.search(response, output)
