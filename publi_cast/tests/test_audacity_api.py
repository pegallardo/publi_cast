import unittest
from unittest.mock import Mock, patch
from services.audacity_service import AudacityAPI

class TestAudacityAPI(unittest.TestCase):
    def setUp(self):
        self.mock_logger = Mock()
        self.mock_pipe = Mock()
        self.api = AudacityAPI(self.mock_pipe, self.mock_logger)

    @patch('subprocess.Popen')
    def test_start_audacity_success(self, mock_popen):
        mock_process = Mock()
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process
        
        result = self.api.start_audacity()
        
        self.assertEqual(result, mock_process)
        self.mock_logger.info.assert_called_with("Audacity started successfully")

    @patch('subprocess.Popen')
    def test_start_audacity_retry_success(self, mock_popen):
        mock_process = Mock()
        mock_process.poll.side_effect = [1, None]
        mock_popen.return_value = mock_process
        
        result = self.api.start_audacity(retry_attempts=2)
        
        self.assertEqual(result, mock_process)
        self.assertEqual(mock_popen.call_count, 2)

    def test_run_command_success(self):
        self.api.pipe = self.mock_pipe
        self.mock_pipe.write.return_value = None
        self.mock_pipe.read.return_value = "OK"
        
        response = self.api.run_command("TestCommand")
        
        self.assertEqual(response, "OK")
