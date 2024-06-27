import unittest
from unittest.mock import patch, mock_open, MagicMock
from publi_cast.repositories.audacity_repository import NamedPipe

class TestNamedPipe(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists", return_value=True)
    def test_open(self, exists_mock, open_mock):
        named_pipe = NamedPipe("\\\\.\\pipe\\ToSrvPipe", "\\\\.\\pipe\\FromSrvPipe")
        named_pipe.open()
        open_mock.assert_any_call("\\\\.\\pipe\\ToSrvPipe", 'w')
        open_mock.assert_any_call("\\\\.\\pipe\\FromSrvPipe", 'r')

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists", return_value=True)
    def test_write(self, exists_mock, open_mock):
        named_pipe = NamedPipe("\\\\.\\pipe\\ToSrvPipe", "\\\\.\\pipe\\FromSrvPipe")
        named_pipe.open()
        message = "Test Message"
        named_pipe.write(message)
        handle = open_mock()
        handle.write.assert_called_once_with(message + '\n')
        handle.flush.assert_called_once()

    @patch("builtins.open", new_callable=mock_open, read_data="Line1\nLine2\nEnd of Script\n")
    @patch("os.path.exists", return_value=True)
    def test_read(self, exists_mock, open_mock):
        named_pipe = NamedPipe("\\\\.\\pipe\\ToSrvPipe", "\\\\.\\pipe\\FromSrvPipe")
        named_pipe.open()
        response = named_pipe.read()
        self.assertEqual(response, "Line1\nLine2")

if __name__ == '__main__':
    unittest.main()
