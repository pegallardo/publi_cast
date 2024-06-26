import unittest
from unittest.mock import MagicMock
from publi_cast.audacity.service import AudacityAPI
from publi_cast.audacity.repository import Pipe

class TestAudacityAPI(unittest.TestCase):
    def setUp(self):
        self.pipe_mock = MagicMock(spec=Pipe)
        self.api = AudacityAPI()
        self.api.set_pipe(self.pipe_mock)

    def test_send_command(self):
        command = "GenerateTone:Frequency=440 Duration=1"
        self.api.send_command(command)
        self.pipe_mock.write.assert_called_once_with(command + '\n')

    def test_get_response(self):
        expected_response = "Response"
        self.pipe_mock.read.return_value = expected_response
        response = self.api.get_response()
        self.assertEqual(response, expected_response)

    def test_run_command(self):
        command = "GenerateTone:Frequency=440 Duration=1"
        expected_response = "Response"
        self.pipe_mock.read.return_value = expected_response
        response = self.api.run_command(command)
        self.pipe_mock.write.assert_called_once_with(command + '\n')
        self.assertEqual(response, expected_response)

if __name__ == '__main__':
    unittest.main()
