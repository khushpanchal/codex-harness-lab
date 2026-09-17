import errno
import os
import unittest
from unittest.mock import ANY, call, NonCallableMagicMock, patch

from test_utils import MockSock, MockFile, MockException, ZEN, SuperMock

from paasio import MeteredFile, MeteredSocket


class PaasioTest(unittest.TestCase):
    def test_meteredsocket_context_manager(self):
        wrapped = MockSock()
        mock = NonCallableMagicMock(wraps=wrapped, autospec=True)
        mock.__exit__.side_effect = wrapped.__exit__
        with MeteredSocket(mock) as socket:
            self.assertFalse(mock.__enter__.called)
            socket.recv(30)
        self.assertFalse(mock.__enter__.called)
        mock.__exit__.assert_called_once_with(None, None, None)
        self.assertEqual(2, len(mock.mock_calls))
        with self.assertRaisesRegex(OSError, os.strerror(errno.EBADF)):
            socket.recv(30)
        with self.assertRaisesRegex(OSError, os.strerror(errno.EBADF)):
            socket.send(b"")
























