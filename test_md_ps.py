import unittest
from unittest.mock import patch, mock_open, Mock
import io
import zlib

from metadata_parser import parse_metadata, interpret_metadata_chunk

class TestParseMetadata(unittest.TestCase):
    @patch('builtins.open', new_callable=mock_open, read_data=b'\x89PNG\r\n\x1a\n')
    def test_parse_metadata_success(self, mock_file):
        chunks = parse_metadata("test_image.png")
        self.assertTrue(chunks)  # Check not empty

    @patch('builtins.open', side_effect=IOError)
    def test_parse_metadata_failure(self, mock_file):
        self.assertIsNone(parse_metadata("nonexistent.png"))



class TestInterpretMetadataChunk(unittest.TestCase):
    @patch('zlib.decompress', side_effect=zlib.decompress)
    def test_successful_Чтение_tEXt(self, mock_decompress):
        chunks = [(b"tEXt", b"parameters\x00Test Value")]
        self.assertEqual(interpret_metadata_chunk(chunks), b"Test Value")

    @patch('zlib.decompress', return_value=b'Decompressed Value')
    def test_successful_Чтение_iTXt(self, mock_decompress):
        chunks = [(b"iTXt", b"parameters\x00\x00\x00\x00SomeData")]
        self.assertEqual(interpret_metadata_chunk(chunks), b'Decompressed Value')

    @patch('zlib.decompress', side_effect=zlib.error)
    def test_failed_decompression(self, mock_decompress):
        chunks = [(b"iTXt", b"parameters\x00\x00\x00\x00SomeData")]
        self.assertIsNone(interpret_metadata_chunk(chunks))  # Test failure case

    @patch('zlib.decompress', return_value=b'Decompressed Value')
    def test_ignore_other_keys(self, mock_decompress):
        chunks = [(b"tEXt", b"other\x00Test"),
                  (b"iTXt", b"parameters\x00\x00\x00\x00SomeData")]
        self.assertEqual(interpret_metadata_chunk(chunks), b'Decompressed Value')

    def test_empty_chunks(self):
        chunks = []
        self.assertIsNone(interpret_metadata_chunk(chunks))

if __name__ == '__main__':
    unittest.main()
