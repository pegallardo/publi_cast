import unittest
from unittest.mock import Mock, patch
from publi_cast.controllers.import_controller import select_audio_file

class TestAudioDialog(unittest.TestCase):
    @patch('tkinter.filedialog.askopenfilename')
    def test_select_audio_file_success(self, mock_filedialog):
        mock_logger = Mock()
        mock_filedialog.return_value = "/path/to/audio.mp3"
        
        result = select_audio_file(mock_logger)
        
        self.assertIn("audio.mp3", result)
        mock_logger.info.assert_called()

    @patch('tkinter.filedialog.askopenfilename')
    def test_select_audio_file_cancelled(self, mock_filedialog):
        mock_logger = Mock()
        mock_filedialog.return_value = ""
        
        result = select_audio_file(mock_logger)
        
        self.assertIsNone(result)
        mock_logger.warning.assert_called()
