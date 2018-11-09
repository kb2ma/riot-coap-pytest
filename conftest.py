# Copyright (c) 2018 Ken Bannister. All rights reserved.
#
# This file is subject to the terms and conditions of the GNU Lesser
# General Public License v2.1. See the file LICENSE in the top level
# directory for more details.

"""
Utilities for tests
"""

import pytest
import pexpect
import os
import signal

class ExpectHost():
    """
    A networking host wrapped in a pexpect spawn.

    The pexpect spawn object itself is available as the 'term' attribute.
    """

    def __init__(self, folder, term_cmd):
        self.folder = folder
        self.term = None
        self.term_cmd = term_cmd

    def connect(self):
        """
        Starts OS host process.

        :return: pexpect spawn object; the 'term' attribute for ExpectHost
        """
        if self.folder:
            os.chdir(self.folder)
        self.term = pexpect.spawn(self.term_cmd, codec_errors='replace',
                                  timeout=10)
        return self.term

    def disconnect(self):
        """Kill OS host process"""
        try:
            os.killpg(os.getpgid(self.term.pid), signal.SIGKILL)
        except ProcessLookupError:
            print("Process already stopped")

    def send_recv(self, out_text, in_text):
        """Sends the given text to the host, and expects the given text
           response."""
        self.term.sendline(out_text)

        result = False
        try:
            self.term.expect(in_text)
            result = True
        except pexpect.TIMEOUT:
            pytest.fail("TIMEOUT")

        return result
