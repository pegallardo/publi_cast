import unittest
from unittest.mock import Mock, patch
from repositories.audacity_repository import NamedPipe

class TestNamedPipe(unittest.TestCase):
    def setUp(self):
        self.mock_logger = Mock()
        self.pipe = NamedPipe(self.mock_logger)

    @patch('os.path.exists')
    @patch('win32file.CreateFile')
    def test_open_pipe_success(self, mock_create_file, mock_exists):
        mock_exists.return_value = True
        mock_create_file.return_value = Mock()
        
        self.pipe.open()
        
        self.assertEqual(mock_create_file.call_count, 2)
        self.mock_logger.info.assert_called()

    @patch('win32file.CloseHandle')
    def test_close_pipe_success(self, mock_close):
        self.pipe.pipe_in = Mock()
        self.pipe.pipe_out = Mock()
        
        self.pipe.close()
        
        self.assertEqual(mock_close.call_count, 2)
