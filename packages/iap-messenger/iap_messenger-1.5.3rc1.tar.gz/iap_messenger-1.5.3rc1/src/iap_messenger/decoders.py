"""
IA Parc Inference decoders
"""
import logging
from dataclasses import dataclass
from typing import Any
from struct import unpack
from PIL.Image import Image
from io import BytesIO
import msgpack
import msgpack_numpy as m
import lz4.frame as lz4
import re


Error = ValueError | None

@dataclass
class MultipartField:
    """Represents a field in multipart data"""
    filename: str | None
    data: bytes
    size: int

# Configure the logger for this module
LOGGER = logging.getLogger("Decoders")
LOGGER.propagate = True
## Data decoders


def decode(data: bytes, decoder: str) -> tuple[Any, Error]:
    """
    Decode data
    Arguments:
    data: bytes
    decoder: str
    """
    use_lz4 = False
    if "lz4(" in decoder:
        use_lz4 = True
        decoder = decoder.replace("lz4(", "").replace(")", "")
    if decoder == "float":
        return decode_float(data)
    if decoder == "int" or decoder == "integer":
        return decode_int(data)
    if decoder == "bool":
        return decode_bool(data)
    if decoder == "file":
        return decode_file(data, use_lz4)
    elif decoder == "image":
        return decode_image(data, use_lz4)
    elif decoder == "text" or decoder == "str" or decoder == "string":
        return decode_text(data, use_lz4)
    elif decoder == "json":
        return decode_json(data, use_lz4)
    elif decoder == "msgpack":
        return decode_msgpack(data, use_lz4)
    elif decoder == "numpy":
        return decode_numpy(data, use_lz4)
    elif decoder == "multipart" or decoder == "multimodal":
        res, err = decode_multipart(data, "", use_lz4)
        return res, err
    elif decoder == "audio":
        return decode_audio(data, use_lz4)
    elif decoder == "video":
        return decode_video(data, use_lz4)

    
    return None, ValueError(f"Decoder {decoder} is not supported")

def decode_float(data: bytes) -> tuple[float, Error]:
    """
    Read float - robust implementation that handles various formats
    Arguments:
    data: bytes
    """
    if data is None:
        return 0.0, ValueError("No data to read")
    if not isinstance(data, bytes):
        return 0.0, ValueError("Data is not bytes")
    if not data:
        return 0.0, ValueError("Empty data")
    
    try:
        # First try to parse as string representation (most flexible)
        try:
            # Try UTF-8 first, then latin-1 as fallback
            try:
                text = data.decode('utf-8').strip()
            except UnicodeDecodeError:
                text = data.decode('latin-1').strip()
            
            # Handle common string representations
            if text:
                # Support hex, binary, and octal formats by converting to int first, then float
                if text.startswith('0x') or text.startswith('0X'):
                    return float(int(text, 16)), None  # Hexadecimal
                elif text.startswith('0b') or text.startswith('0B'):
                    return float(int(text, 2)), None   # Binary
                elif text.startswith('0o') or text.startswith('0O'):
                    return float(int(text, 8)), None   # Octal
                else:
                    return float(text), None           # Decimal or scientific notation
        except (ValueError, UnicodeDecodeError):
            pass
        
        # Try to interpret as integer bytes first (more likely to be intended as numbers)
        if len(data) <= 8:
            try:
                int_val = int.from_bytes(data, byteorder='little', signed=True)
                # Check if this looks like a reasonable integer (not too large for float precision)
                if abs(int_val) < 2**53:  # 53 bits is float64 precision limit
                    return float(int_val), None
            except Exception:
                pass
            
            try:
                int_val = int.from_bytes(data, byteorder='big', signed=True)
                if abs(int_val) < 2**53:
                    return float(int_val), None
            except Exception:
                pass
        
        # Try struct unpack for binary float data (when int interpretation doesn't make sense)
        if len(data) == 4:
            try:
                value = unpack('f', data)[0]  # 32-bit float
                return value, None
            except Exception:
                try:
                    value = unpack('!f', data)[0]  # Big-endian 32-bit float
                    return value, None
                except Exception:
                    pass
        elif len(data) == 8:
            try:
                value = unpack('d', data)[0]  # 64-bit double
                return value, None
            except Exception:
                try:
                    value = unpack('!d', data)[0]  # Big-endian 64-bit double
                    return value, None
                except Exception:
                    pass
        
        # Final fallback for remaining cases
        if len(data) <= 8:
            try:
                int_val = int.from_bytes(data, byteorder='little', signed=False)
                return float(int_val), None
            except Exception:
                try:
                    int_val = int.from_bytes(data, byteorder='big', signed=False)
                    return float(int_val), None
                except Exception:
                    pass
        
    except Exception as e:
        return 0.0, ValueError(f"Error reading float: {e}")
    
    return 0.0, ValueError(f"Could not decode {len(data)} bytes as float")

def decode_int(data: bytes) -> tuple[int, Error]:
    """
    Read int - robust implementation using int.from_bytes and string parsing
    Arguments:
    data: bytes
    """
    if data is None:
        return 0, ValueError("No data to read")
    if not isinstance(data, bytes):
        return 0, ValueError("Data is not bytes")
    if not data:
        return 0, ValueError("Empty data")
    
    try:
        LOGGER.debug(f"Decoding int from {len(data)} bytes")
        
        # First try to parse as string representation (most flexible)
        try:
            # Try UTF-8 first, then latin-1 as fallback
            try:
                text = data.decode('utf-8').strip()
            except UnicodeDecodeError:
                text = data.decode('latin-1').strip()
            
            # Handle common string representations
            if text:
                # Support different bases (decimal, hex, binary)
                if text.startswith('0x') or text.startswith('0X'):
                    return int(text, 16), None  # Hexadecimal
                elif text.startswith('0b') or text.startswith('0B'):
                    return int(text, 2), None   # Binary
                elif text.startswith('0o') or text.startswith('0O'):
                    return int(text, 8), None   # Octal
                else:
                    return int(text), None      # Decimal
        except (ValueError, UnicodeDecodeError):
            pass
        
        # Use int.from_bytes for binary data (most robust for various byte lengths)
        if len(data) <= 8:  # Support up to 64-bit integers
            try:
                # Try little-endian first (most common)
                value = int.from_bytes(data, byteorder='little', signed=True)
                return value, None
            except Exception:
                try:
                    # Try big-endian
                    value = int.from_bytes(data, byteorder='big', signed=True)
                    return value, None
                except Exception:
                    try:
                        # Try unsigned little-endian
                        value = int.from_bytes(data, byteorder='little', signed=False)
                        return value, None
                    except Exception:
                        try:
                            # Try unsigned big-endian
                            value = int.from_bytes(data, byteorder='big', signed=False)
                            return value, None
                        except Exception:
                            pass
        
        # Fallback to struct unpack for compatibility with existing code
        if len(data) == 4:
            try:
                value = unpack('i', data)[0]  # 32-bit signed int
                return value, None
            except Exception:
                try:
                    value = unpack('!i', data)[0]  # Big-endian 32-bit signed int
                    return value, None
                except Exception:
                    pass
        elif len(data) == 8:
            try:
                value = unpack('q', data)[0]  # 64-bit signed int
                return value, None
            except Exception:
                try:
                    value = unpack('!q', data)[0]  # Big-endian 64-bit signed int
                    return value, None
                except Exception:
                    pass
        
    except Exception as e:
        return 0, ValueError(f"Error reading int: {e}")
    
    return 0, ValueError(f"Could not decode {len(data)} bytes as int")

def decode_bool(data: bytes) -> tuple[bool, Error]:
    """
    Read bool - robust implementation that handles various boolean representations
    Arguments:
    data: bytes
    """
    if data is None:
        return False, ValueError("No data to read")
    if not isinstance(data, bytes):
        return False, ValueError("Data is not bytes")
    if not data:
        return False, ValueError("Empty data")
    
    try:
        # First try to parse as string representation (most flexible)
        try:
            # Try UTF-8 first, then latin-1 as fallback
            try:
                text = data.decode('utf-8').strip().lower()
            except UnicodeDecodeError:
                text = data.decode('latin-1').strip().lower()
            
            # Handle common string representations
            if text in ('true', '1', 'yes', 'on', 't', 'y'):
                return True, None
            elif text in ('false', '0', 'no', 'off', 'f', 'n', ''):
                return False, None
            else:
                # Try to parse as number and check if non-zero
                try:
                    num_val = float(text)
                    return bool(num_val), None
                except ValueError:
                    pass
        except (ValueError, UnicodeDecodeError):
            pass
        
        # Try struct unpack for single byte boolean
        if len(data) == 1:
            try:
                value = unpack('?', data)[0]
                return value, None
            except Exception:
                # Interpret single byte as boolean (0 = False, non-zero = True)
                return bool(data[0]), None
        
        # For multi-byte data, use int.from_bytes and check if non-zero
        if len(data) <= 8:
            try:
                # Try little-endian
                int_val = int.from_bytes(data, byteorder='little', signed=False)
                return bool(int_val), None
            except Exception:
                try:
                    # Try big-endian
                    int_val = int.from_bytes(data, byteorder='big', signed=False)
                    return bool(int_val), None
                except Exception:
                    pass
        
        # Fallback: any non-empty, non-zero byte sequence is True
        return any(b != 0 for b in data), None
        
    except Exception as e:
        return False, ValueError(f"Error reading bool: {e}")
    
    return False, ValueError(f"Could not decode {len(data)} bytes as bool")

def decode_file(data: bytes, use_lz4: bool=False) -> tuple[BytesIO, Error]:
    """
    Read file
    Arguments:
    data: bytes
    """
    if not data:
        return BytesIO(), ValueError("No data to read")
    if not isinstance(data, bytes):
        return BytesIO(), ValueError("Data is not bytes")
    try:
        if use_lz4:
            data = lz4.decompress(data)
        file = BytesIO(data)
    except Exception as e:
        return BytesIO(), ValueError(f"Error reading file: {e}")
    return file, None

def decode_image(data: bytes, use_lz4: bool=False) -> tuple[Image|None, Error]:
    """
    Read image
    Arguments:
    data: bytes
    """
    if not data:
        return None, ValueError("No data to read")
    if not isinstance(data, bytes):
        return None, ValueError("Data is not bytes")
    try:
        from PIL import Image
        if use_lz4:
            data = lz4.decompress(data)
        image = Image.open(BytesIO(data))
    except Exception as e:
        return None, ValueError(f"Error reading image: {e}")
    return image, None

def decode_text(data: bytes, use_lz4: bool=False) -> tuple[str, Error]:
    """
    Read text
    Arguments:
    data: bytes
    """
    if not data:
        return "", ValueError("No data to read")
    if not isinstance(data, bytes):
        return "", ValueError("Data is not bytes")
    try:
        if use_lz4:
            data = lz4.decompress(data)
        
        # Try UTF-8 decoding first (most common case)
        try:
            text = data.decode("utf-8")
            return text, None
        except UnicodeDecodeError:
            # Fallback to latin-1 which can decode any byte sequence
            try:
                text = data.decode("latin-1")
                return text, None
            except UnicodeDecodeError:
                # Final fallback: decode only ASCII characters
                try:
                    text = data.decode("ascii", errors="ignore")
                    return text, None
                except Exception:
                    # If all decoding attempts fail, return error
                    pass
        
    except Exception as e:
        return "", ValueError(f"Error reading text: {e}")
    
    return "", ValueError("Could not decode text data with any supported encoding")

def decode_json(data: bytes, use_lz4: bool=False) -> tuple[dict, Error]:
    """
    Read json
    Arguments:
    data: bytes
    """
    if not data:
        return {}, ValueError("No data to read")
    if not isinstance(data, bytes):
        return {}, ValueError("Data is not bytes")
    try:
        from json_tricks import loads
        if use_lz4:
            data = lz4.decompress(data)
        json_data = loads(data.decode("utf-8"))
    except Exception as e:
        return {}, ValueError(f"Error reading json: {e}")
    return json_data, None

def decode_msgpack(data: bytes, use_lz4: bool=False) -> tuple[dict, Error]:
    """
    Read msgpack
    Arguments:
    data: bytes
    """
    if not data:
        return {}, ValueError("No data to read")
    if not isinstance(data, bytes):
        return {}, ValueError("Data is not bytes")
    try:
        if use_lz4:
            data = lz4.decompress(data)
        json_data = msgpack.unpackb(data, object_hook=m.decode)
    except Exception as e:
        return {}, ValueError(f"Error reading msgpack: {e}")
    return json_data, None

def decode_numpy(data: bytes, use_lz4: bool=False) -> tuple[dict, Error]:
    """
    Read numpy
    Arguments:
    data: bytes
    """
    return decode_msgpack(data, use_lz4)

def decode_multipart(data: bytes, content_type: str, use_lz4: bool=False) -> tuple[dict[str, MultipartField], Error]:
    """
    Read multi-part data
    Arguments:
    data: bytes
    content_type: str - content type string
    use_lz4: bool - whether to decompress with lz4
    
    Returns:
    dict containing decoded multipart data with field names as keys,
    where each value is a MultipartField dataclass instance
    """
    if not data:
        return {}, ValueError("No data to read")
    if not isinstance(data, bytes):
        return {}, ValueError("Data is not bytes")
    
    try:
        if use_lz4:
            data = lz4.decompress(data)
        
        results = {}
        
        # Extract boundary from content_type or data
        boundary = None
        if content_type and "boundary=" in content_type:
            # Extract boundary from content-type header
            boundary_match = re.search(r'boundary=([^;]+)', content_type)
            if boundary_match:
                boundary = boundary_match.group(1).strip('"')
        
        # If no boundary in content_type, try to extract from data
        if not boundary:
            boundary = _get_boundary(data)
        
        if not boundary:
            return {}, ValueError("Could not find multipart boundary")
        
        # Split data by boundary
        boundary_bytes = f"--{boundary}".encode('utf-8')
        parts = data.split(boundary_bytes)
        
        # Remove first (empty) and last (closing) parts
        parts = parts[1:-1] if len(parts) > 2 else parts[1:] if len(parts) > 1 else []
        
        for part in parts:
            if not part.strip():
                continue
            
            # Split headers from body
            if b'\r\n\r\n' in part:
                headers_bytes, body = part.split(b'\r\n\r\n', 1)
            elif b'\n\n' in part:
                headers_bytes, body = part.split(b'\n\n', 1)
            else:
                continue  # Invalid part
            
            # Parse headers
            headers = {}
            try:
                headers_text = headers_bytes.decode('utf-8').strip()
                for line in headers_text.split('\n'):
                    line = line.strip()
                    if ':' in line:
                        key, value = line.split(':', 1)
                        headers[key.strip().lower()] = value.strip()
            except UnicodeDecodeError:
                continue  # Skip parts with invalid headers
            
            # Extract field name and filename from Content-Disposition
            field_name = None
            filename = None
            
            if 'content-disposition' in headers:
                cd_header = headers['content-disposition']
                
                # Extract name
                name_match = re.search(r'name="([^"]*)"', cd_header)
                if name_match:
                    field_name = name_match.group(1)
                
                # Extract filename
                filename_match = re.search(r'filename="([^"]*)"', cd_header)
                if filename_match:
                    filename = filename_match.group(1)
            
            # Use default field name if not found
            if not field_name:
                field_name = f"field_{len(results)}"
            
            # Remove trailing \r\n from body data
            clean_body = body.rstrip(b'\r\n')
            
            results[field_name] = MultipartField(
                filename=filename,
                data=clean_body,
                size=len(clean_body)
            )
            
        return results, None
        
    except Exception as e:
        LOGGER.error(f"Error decoding multipart data: {e}")
        return {}, ValueError(f"Error decoding multipart data: {e}")

def decode_audio(data: bytes, use_lz4: bool=False) -> tuple[BytesIO, Error]:
    """
    Read audio data - supports various audio formats
    Arguments:
    data: bytes
    use_lz4: bool - whether to decompress with lz4
    
    Returns a BytesIO object containing the audio data that can be used with
    audio libraries like pydub, librosa, or soundfile.
    """
    if not data:
        return BytesIO(), ValueError("No data to read")
    if not isinstance(data, bytes):
        return BytesIO(), ValueError("Data is not bytes")
    
    try:
        if use_lz4:
            data = lz4.decompress(data)
        
        # Create BytesIO object with the audio data
        audio_stream = BytesIO(data)
        
        # Try to detect and validate audio format by checking magic bytes
        audio_stream.seek(0)
        header = audio_stream.read(12)  # Read first 12 bytes for format detection
        audio_stream.seek(0)  # Reset position
        
        if len(header) >= 4:
            # Check for common audio format signatures
            if header[:4] == b'RIFF' and header[8:12] == b'WAVE':
                # WAV format detected
                LOGGER.debug("Detected WAV audio format")
            elif header[:3] == b'ID3' or header[:2] == b'\xff\xfb' or header[:2] == b'\xff\xf3':
                # MP3 format detected (ID3 tag or MP3 sync word)
                LOGGER.debug("Detected MP3 audio format")
            elif header[:4] == b'OggS':
                # OGG format detected
                LOGGER.debug("Detected OGG audio format")
            elif header[:4] == b'fLaC':
                # FLAC format detected
                LOGGER.debug("Detected FLAC audio format")
            elif header[:4] == b'FORM' and header[8:12] == b'AIFF':
                # AIFF format detected
                LOGGER.debug("Detected AIFF audio format")
            elif header[:8] == b'ftypM4A ' or header[:4] == b'M4A ':
                # M4A/AAC format detected
                LOGGER.debug("Detected M4A/AAC audio format")
            else:
                # Unknown format, but still return the data
                LOGGER.debug(f"Unknown audio format, header: {header[:8].hex()}")
        
        return audio_stream, None
        
    except Exception as e:
        LOGGER.error(f"Error reading audio data: {e}")
        return BytesIO(), ValueError(f"Error reading audio: {e}")


def decode_video(data: bytes, use_lz4: bool=False) -> tuple[BytesIO, Error]:
    """
    Read video data - supports various video formats
    Arguments:
    data: bytes
    use_lz4: bool - whether to decompress with lz4
    
    Returns a BytesIO object containing the video data that can be used with
    video libraries like opencv-python, moviepy, or ffmpeg-python.
    """
    if not data:
        return BytesIO(), ValueError("No data to read")
    if not isinstance(data, bytes):
        return BytesIO(), ValueError("Data is not bytes")
    
    try:
        if use_lz4:
            data = lz4.decompress(data)
        
        # Create BytesIO object with the video data
        video_stream = BytesIO(data)
        
        # Try to detect and validate video format by checking magic bytes
        video_stream.seek(0)
        header = video_stream.read(20)  # Read first 20 bytes for format detection
        video_stream.seek(0)  # Reset position
        
        if len(header) >= 8:
            # Check for common video format signatures
            if (header[4:8] == b'ftyp' and
                (header[8:12] in [b'mp41', b'mp42', b'isom', b'avc1', b'qt  '])):
                # MP4/MOV format detected
                LOGGER.debug("Detected MP4/MOV video format")
            elif header[:4] == b'RIFF' and header[8:12] == b'AVI ':
                # AVI format detected
                LOGGER.debug("Detected AVI video format")
            elif header[:3] == b'FLV':
                # FLV format detected
                LOGGER.debug("Detected FLV video format")
            elif header[:4] == b'\x1a\x45\xdf\xa3':  # EBML header for WebM/MKV
                # WebM/MKV format detected
                LOGGER.debug("Detected WebM/MKV video format")
            elif header[:4] == b'OggS':
                # Could be OGV (Ogg Video)
                LOGGER.debug("Detected OGG video format")
            elif header[:2] == b'\x00\x00' and header[4:8] == b'ftyp':
                # Another variant of MP4
                LOGGER.debug("Detected MP4 video format (variant)")
            elif header[:4] == b'\x30\x26\xb2\x75':  # WMV signature
                # WMV format detected
                LOGGER.debug("Detected WMV video format")
            elif (header[:4] == b'RIFF' and
                  len(header) >= 12 and header[8:12] in [b'WEBP', b'VP8 ', b'VP80']):
                # WebP or VP8 format
                LOGGER.debug("Detected WebP/VP8 format")
            else:
                # Unknown format, but still return the data
                LOGGER.debug(f"Unknown video format, header: {header[:12].hex()}")
        
        # Additional validation: check if data looks like video content
        if len(data) < 100:
            LOGGER.warning(f"Video data seems too small ({len(data)} bytes), might be invalid")
        
        return video_stream, None
        
    except Exception as e:
        LOGGER.error(f"Error reading video data: {e}")
        return BytesIO(), ValueError(f"Error reading video: {e}")


def _get_boundary(data: bytes) -> str | None:
    """
    Get boundary from multipart data
    Arguments:
    data: bytes
    """
    splitted = data.split(b"\r\n")
    if len(splitted) < 2:
        return None
    boundary = splitted[0]
    if len(boundary) < 2:
        return None
    
    # Extract boundary after the '--' prefix
    boundary_bytes = boundary[2:]
    
    # RFC 2046 specifies boundaries should be ASCII, but we'll handle edge cases
    try:
        # First try UTF-8 decoding (most common case)
        return boundary_bytes.decode("utf-8")
    except UnicodeDecodeError:
        try:
            # Try latin-1 which can decode any byte sequence
            decoded = boundary_bytes.decode("latin-1")
            
            # For better safety, if the decoded boundary contains non-printable
            # or unusual characters, extract only printable ASCII part
            if any(ord(c) < 32 or ord(c) > 126 for c in decoded):
                # Extract only ASCII printable characters
                ascii_chars = ''.join(c for c in decoded if 32 <= ord(c) <= 126)
                if len(ascii_chars) >= 3:  # Minimum reasonable boundary length
                    return ascii_chars
                # If too short after filtering, return the original latin-1 decoded string
                # The multipart parser will handle validation
            return decoded
        except UnicodeDecodeError:
            # Should never happen with latin-1, but just in case
            # Extract only ASCII printable bytes
            ascii_bytes = bytes([b for b in boundary_bytes if 32 <= b <= 126])
            if len(ascii_bytes) >= 3:
                try:
                    return ascii_bytes.decode("ascii")
                except UnicodeDecodeError:
                    pass
            return None