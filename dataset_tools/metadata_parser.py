import png  # assuming an imported library for example
import zlib
import re
from dataset_tools import logger

def open_png_header(file_path_named: str) -> bytes:
    """
    Open png format files\n
    :param file_path_named: `str` The path and file name of the png file
    :return: `Generator[bytes]` Generator element containing header bytes
    """
    try:
        with open(file_path_named, "rb") as f:
            png_data = f.read()
            reader = png.Reader(bytes=png_data)
            header_chunks = reader.chunks()
    except Exception as error_log:
        logger.info("Error reading png file: ", error_log)
        logger.debug(f"",error_log, exc_info=True)
        return None
    else:
        return header_chunks


def extract_metadata_chunks(header_chunks: bytes,
                            text_prefix: tuple = (b"tEXt", b"iTXt"),
                            search_key: tuple = (b"parameters", b"prompt")
                            ) -> bytes:
    """
    Scan metadata chunks, then extract relevant data\n
    :param header_chunks: `Generator[bytes]` Data header from relevant file
    :param text_prefix: `tuple` Values that precede text bytes
    :param search_key: `tuple` Values that precede text we are looking for
    :return: `bytes` Byte string from the header of relevant data
    """
    for chunk_name, chunk_data in header_chunks:
        if chunk_name in text_prefix:
            parts = chunk_data.split(b"\x00", 3)
            key, *_, text_chunk = parts
            if chunk_name == b"iTXt" and parts[1] == b'\x00':
                try:
                    text_chunk = zlib.decompress(text_chunk)
                except Exception as error_log:
                    logger.info(f"Error decompressing: ", error_log)
                    logger.debug(f"",error_log, exc_info=True)
                    continue

            if key in search_key:
                return text_chunk

def format_chunk(text_chunk: bytes) -> dict:
    """
    Turn raw bytes into utf8 formatted text\n
    :param text_chunk: `bytes` Data from a file header
    :return: `dict` text data in a dict structure
    """
    try:
        text = text_chunk.decode('utf-8', errors='ignore')
    except Exception as error_log:
        logger.info("Error decoding: ", error_log)
        logger.debug(f"",error_log, exc_info=True)
    else:
        if not next(iter(text)) == "{":
            formatted_text = parse_text(text)
        logger.debug(f"Decoded Text: {formatted_text}")
        return formatted_text

def parse_text(formatted_text: str) -> dict:
    """
    Reconstruct metadata header format into a dict\n
    :param formatted_text: `str` Unstructured utf-8 formatted text
    :return: `dict` The text formatted into a valid dictionary structure
    """

    text_strip_spaces = formatted_text.strip()
    text_prefix = text_strip_spaces.split('\n')
    text_pos_prompt = text_prefix[0].split('POS')[1]
    text_neg_prompt = text_prefix[1].split('Neg')[1]
    hash_values = text_prefix[2]
    regex_filter = dict(re.findall(r'(\w+):\s*(\d+(?:\.\d+)?)', str(text_prefix)))
    formatted_text = str({
                        "positive": text_pos_prompt,
                        "negative": text_neg_prompt,
                        "parameters": regex_filter,
                        "hash": hash_values}
                        )

    return formatted_text

def parse_metadata(file_path_named: str) -> dict:
    """
    Extract the metadata from the header of an image file\n
    :param file_path_named: `str` The file to open
    :return: `dict` The metadata from the header of the file
    """
    header_chunks = open_png_header(file_path_named)
    text_chunk = extract_metadata_chunks(header_chunks)
    formatted_text = format_chunk(text_chunk)
    return formatted_text
