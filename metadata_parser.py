import png
import zlib
import json
import re
def parse_metadata(file_path):
    metadata = {}
    formatted_text = ""
    try:
        with open(file_path, "rb") as f:
            png_data = f.read()
        reader = png.Reader(bytes=png_data)
        chunks = reader.chunks()
        
        text_chunk = b""
        for chunk_name, chunk_data in chunks:
            if chunk_name == b"tEXt" or chunk_name == b"iTXt":
                try:
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
                    if key == b"parameters":
                      text_chunk = value
                      break # stop when you find it
                except Exception as e:
                    print("Error reading chunk: ", e)

        if text_chunk:
          try:
            # Try to decode the value, it may contain utf8 or other encodings
            text = text_chunk.decode('utf-8', errors='ignore')
            print(f"Decoded text: {text}")
          except Exception as e:
            print("Error decoding: ", e)
            return formatted_text
          try:
            # Regex to find the prompt and the json string:
            m = re.search(r"^(.*?)?(?:Negative prompt: (.*?))?(?:\nSteps: (.*?))?(?:\nSampler: (.*?))?(?:\nSchedule type: (.*?))?(?:\nCFG scale: (.*?))?(?:\nSeed: (.*?))?(?:\nSize: (.*?))?(?:\nModel hash: (.*?))?(?:\nModel: (.*?))?(?:\nVAE hash: (.*?))?(?:\nVAE: (.*?))?(?:\nDenoising strength: (.*?))?(?:\nClip skip: (.*?))?(?:\nHashes: (.*?))?(?:\n.*)?$", text, re.MULTILINE)
            if m is not None:
              
              formatted_text = ""
              if m.group(1):
                formatted_text += f"prompt: {m.group(1).strip()}\n"
              if m.group(2):
                  formatted_text += f"negative_prompt: {m.group(2).strip()}\n"
              if m.group(3):
                  formatted_text += f"steps: {m.group(3).strip()}\n"
              if m.group(4):
                  formatted_text += f"sampler: {m.group(4).strip()}\n"
              if m.group(5):
                 formatted_text += f"schedule_type: {m.group(5).strip()}\n"
              if m.group(6):
                  formatted_text += f"cfg_scale: {m.group(6).strip()}\n"
              if m.group(7):
                  formatted_text += f"seed: {m.group(7).strip()}\n"
              if m.group(8):
                formatted_text += f"size: {m.group(8).strip()}\n"
              if m.group(9):
                  formatted_text += f"model_hash: {m.group(9).strip()}\n"
              if m.group(10):
                  formatted_text += f"model: {m.group(10).strip()}\n"
              if m.group(11):
                  formatted_text += f"vae_hash: {m.group(11).strip()}\n"
              if m.group(12):
                  formatted_text += f"vae: {m.group(12).strip()}\n"
              if m.group(13):
                  formatted_text += f"denoising_strength: {m.group(13).strip()}\n"
              if m.group(14):
                  formatted_text += f"clip_skip: {m.group(14).strip()}\n"
              if m.group(15):
                formatted_text += f"hashes: {m.group(15).strip()}"
              return formatted_text
          except Exception as e:
            print("Error parsing text", e)
          try:
            # try to load as json
            metadata = json.loads(text)
            formatted_text = ""
            for key, value in metadata.items():
                formatted_text += f"{key}: {value}\n"
            return formatted_text

          except Exception as e:
              print("Error parsing json directly", e)
    except Exception as e:
       print("Error reading png file: ", e)
    return formatted_text