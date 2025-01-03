
import unittest
from unittest.mock import patch, mock_open, Mock
import zlib

from metadata_parser import open_png_header, extract_metadata_chunks

class TestParseMetadata(unittest.TestCase):

    @patch('metadata_parser.open_png_header.png.Reader', 'chunks', return_value=[(b'tEXt', b'data')])
    def test_parse_metadata_success(self, chunks):
        mock_file = mock_open(read_data=b'\x89PNG\r\n\x1a\nIHDR...')
        with patch('builtins.open', mock_file, create=True):
            chunks = open_png_header("mock_path")
            self.assertIsNotNone(chunks)
            self.assertTrue(list(chunks))  # Confirm it's not empty

if __name__ == '__main__':
    @patch('builtins.open', side_effect=IOError)
    def test_parse_metadata_failure(self, mock_file):
        self.assertIsNone(open_png_header("nonexistent.png"))

    def mock_header_chunks(self, data):
        # Mock generator
        return ((b"tEXt", b"parameters\x00example"), (b"iTXt", b"prompt\x00\x00\x00CompVal"))

    def test_extract_metadata(self):
        compressed_val = zlib.compress(b'Test Value')
        mock_data = [(b"tEXt", b"parameters\x00metadata"),
                    (b"iTXt", b"prompt\x00\x00\x00\0"+compressed_val)]
        assert extract_metadata_chunks(iter(mock_data)) == compressed_val


if __name__ == '__main__':
    unittest.main()
