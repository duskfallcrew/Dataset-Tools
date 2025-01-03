
import png
import zlib
import json
import re
import sys


def open_png_header(file_path):
    try:
        with open(file_path, "rb") as f:
            png_data = f.read()
            reader = png.Reader(bytes=png_data)
            chunks = reader.chunks()
    except Exception as e:
       print("Error reading png file: ", e)
    else:
        return chunks

def interpret_metadata_chunk(chunks):
        text_chunk = b""
        for chunk_name, chunk_data in chunks:
            if chunk_name == b"tEXt" or chunk_name == b"iTXt":
                if chunk_name == b"tEXt":
                    key, value = chunk_data.split(b"\x00", 1)
                elif chunk_name == b"iTXt":
                    key, compression_method, _, value = chunk_data.split(b"\x00", 3)
                    if compression_method == b'\x00':
                        # Try zlib decompression only if needed
                        try:
                            value = zlib.decompress(value)
                        except Exception as e:
                            print("Error decompressing: ", e)
                            continue; # skip the rest of this loop iteration, and try the next one
                if key == b"parameters" or key == b"prompt":
                    return value

def format_chunk(text_chunk):
    """Try to decode the value, it may contain utf8 or other encodings"""
    try:
        text = text_chunk.decode('utf-8', errors='ignore')
    except Exception as e:
        print("Error decoding: ", e)
    else:
        if next(iter(text)) == "{":
            formatted_text = text
            json_text = load_as_json(formatted_text)
        else:
            json_text = parse_text(text)
            #json_text = load_as_json(str(formatted_text))
       # print(f"Decoded text: {json_text}")
        return json_text

def parse_text(text):
    """Regex to find the prompt and the json string:"""

    text_strip = text.strip()
    text_prefix = text_strip.split('\n')
    text_pos_prompt = text_prefix[0].split('POS')[1]
    text_neg_prompt = text_prefix[1].split('Neg')[1]
    hash_values = text_prefix[2]
    regex_filter = dict(re.findall(r'(\w+):\s*(\d+(?:\.\d+)?)', str(text_prefix)))
    return str({"positive": text_pos_prompt, "negative": text_neg_prompt, "parameters": regex_filter, "hash": hash_values})

    # try:
    #     metadata_values = re.search(
    #         r"^(.*?)?(?:Negative prompt: (.*?))?(?:\nSteps: (.*?))?"
    #         r"(?:\nSampler: (.*?))?(?:\nSchedule type: (.*?))?"
    #         r"(?:\nCFG scale: (.*?))?(?:\nSeed: (.*?))?"
    #         r"(?:\nSize: (.*?))?(?:\nModel hash: (.*?))?"
    #         r"(?:\nModel: (.*?))?(?:\nVAE hash: (.*?))?"
    #         r"(?:\nVAE: (.*?))?(?:\nDenoising strength: (.*?))?"
    #         r"(?:\nClip skip: (.*?))?(?:\nHashes: (.*?))?",
    #         text,
    #         re.MULTILINE
    #     )
    # except Exception as e:
    #     print("Error parsing text:", e)
    #     return None

    # if metadata_values is not None:
    #     fields = [
    #         ("prompt", 1),
    #         ("negative_prompt", 2),
    #         ("steps", 3),
    #         ("sampler", 4),
    #         ("schedule_type", 5),
    #         ("cfg_scale", 6),
    #         ("seed", 7),
    #         ("size", 8),
    #         ("model_hash", 9),
    #         ("model", 10),
    #         ("vae_hash", 11),
    #         ("vae", 12),
    #         ("denoising_strength", 13),
    #         ("clip_skip", 14),
    #         ("hashes", 15)
    #     ]
    #     formatted_text = "\n".join(
    #         f"{field[0]}: {metadata_values.group(group).strip()}" for field, group in fields if metadata_values.group(group)
    #         )
    #     return formatted_text
    # else:
    #     return "No match found."

def load_as_json(formatted_text):
    """try to load as json"""
    try:
        metadata = json.loads(formatted_text)

        for key, value in metadata.items():
            formatted_text += f"{key}: {value}\n"
    except Exception as e:
        print("Error parsing json directly", e)
    else:
        return formatted_text

def parse_metadata(file_name):
    chunks = open_png_header(file_name)
    text_chunk = interpret_metadata_chunk(chunks)
    json_text = format_chunk(text_chunk)
    #formatted_text = parse_text(text)
    return json_text
