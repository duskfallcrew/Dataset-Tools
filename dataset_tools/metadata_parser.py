
from png import Reader as pngReader
import zlib
import re
import json
from dataset_tools import logger
from collections import defaultdict
import ast

def open_jpg_header(file_path_named: str):
    """
    Open jpg format files\n
    :param file_path_named: `str` The path and file name of the jpg file
    :return: `Generator[bytes]` Generator element containing header tags
    """
    from PIL import Image, ExifTags
    from PIL.ExifTags import TAGS

    pil_img = Image.open(file_path_named)
    exif_info = pil_img._getexif()
    exif = {TAGS.get(k, k): v for k, v in exif_info.items()}
    return exif

def open_png_header(file_path_named: str) -> bytes:
    """
    Open png format files\n
    :param file_path_named: `str` The path and file name of the png file
    :return: `Generator[bytes]` Generator element containing header bytes
    """
    try:
        with open(file_path_named, "rb") as f:
            png_data = f.read()
            reader = pngReader(bytes=png_data)
            header_chunks = reader.chunks()
    except Exception as error_log:
        logger.info(f"Error reading png file: {file_path_named} {error_log}")
        logger.debug(f"{file_path_named} {error_log}")
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

def clean_string_with_json(formatted_text:str) -> dict:
    """"
    Convert data into a clean dictionary\n
    :param pre_cleaned_text: `str` Unstructured utf-8 formatted string
    :return: `dict` Dictionary formatted data
    """
    if next(iter(formatted_text)) != "{":
        formatted_text = restructure_metadata(formatted_text)
        formatted_text = str(formatted_text).replace("\'","\"").replace('\n', '').strip()
    try:
        print(formatted_text)
        json_structured_text = json.loads(formatted_text)
    except Exception as e:
        print("Error parsing json directly", e)
    else:
        return json_structured_text

def format_chunk(text_chunk: bytes) -> dict:
    """
    Turn raw bytes into utf8 formatted text\n
    :param text_chunk: `bytes` Data from a file header
    :return: `dict` text data in a dict structure
    """
    try:
        formatted_text = text_chunk.decode('utf-8', errors='ignore')
    except Exception as error_log:
        logger.info("Error decoding: ", error_log)
        logger.debug(f"",error_log, exc_info=True)
    else:
        json_structured_text = clean_string_with_json(formatted_text)
        logger.debug(f"Decoded Text: {json_structured_text}")
        return json_structured_text

def restructure_metadata(formatted_text: str) -> dict:
    """
    Reconstruct metadata header format into a dict\n
    :param formatted_text: `str` Unstructured utf-8 formatted text
    :return: `dict` The text formatted into a valid dictionary structure
    """
    pre_cleaned_text = defaultdict(dict)

    start_idx = formatted_text.find("POS\"") + 1
    end_idx = formatted_text.find("\"", start_idx)
    positive_string = formatted_text[start_idx:end_idx].strip()

    start_idx = formatted_text.find("Neg") + 1
    end_idx = formatted_text.find("\"", start_idx)
    negative_string = formatted_text[start_idx:end_idx].strip()

    start_idx = formatted_text.find("Hashes") + len("Hashes:")
    end_idx = formatted_text.find("\"", start_idx)
    hash_string = formatted_text[start_idx:end_idx].strip()

    positive = positive_string.replace("\'","\"").replace('\n', '').strip()
    negative = negative_string.replace("\'","\"").replace('\n', '').strip()
    text_split = formatted_text.strip().split('\n')

    for strip in text_split:
        mapped_metadata = {}
        for key, value in re.findall(r'(\w+):\s*(\d+(?:\.\d+)?)', strip):
            mapped_metadata.setdefault(key.replace("\'","\"").replace('\n', '').strip(), value.replace("\'","\"").replace('\n', '').strip())
        pre_cleaned_text = mapped_metadata | {"Hashes": hash_string, "Positive prompt": positive_string, "Negative prompt": negative_string }
    return pre_cleaned_text


def parse_metadata(file_path_named: str) -> dict:
    """
    Extract the metadata from the header of an image file\n
    :param file_path_named: `str` The file to open
    :return: `dict` The metadata from the header of the file
    """
    header_chunks = open_png_header(file_path_named)
    if header_chunks is not None:
        text_chunk = extract_metadata_chunks(header_chunks)
        json_structured_text = format_chunk(text_chunk)
        return json_structured_text
