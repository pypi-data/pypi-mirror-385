"""
IA Parc Inference encoders
"""
from typing import Any
from PIL.Image import Image
from io import BytesIO
import msgpack
import msgpack_numpy as m
import lz4.frame as lz4

Error = ValueError | None


def encode(data: Any, encoder: str) -> (tuple[bytes, str, Error]):
    """
    Encode data
    Arguments:
    data: Any
    encoder: str
    """
    use_lz4 = False
    if "lz4(" in encoder:
        use_lz4 = True
        encoder = encoder.replace("lz4(", "").replace(")", "")
    if encoder == "file":
        if not isinstance(data, BytesIO):
            return ''.encode(), "application/octet-stream", ValueError("Data is not a file")
        bdata, err = encode_file(data, use_lz4)
        return bdata, "application/octet-stream", err
    elif encoder == "image":
        if not isinstance(data, Image):
            return ''.encode(), "image/*", ValueError("Data is not an image")
        bdata, err = encode_image(data, use_lz4)
        return bdata, "image/*", err
    elif encoder == "text":
        if not isinstance(data, str):
            return ''.encode(), "text/plain", ValueError("Data is not a string")
        bdata, err = encode_text(data, use_lz4)
        return bdata, "text/plain", err
    elif encoder == "json":
        if not isinstance(data, dict):
            return ''.encode(), "application/json", ValueError("Data is not a dictionary")
        bdata, err = encode_json(data, use_lz4)
        return bdata, "application/json", err
    elif encoder == "msgpack":
        if not isinstance(data, dict):
            return ''.encode(), "application/octet-stream", ValueError("Data is not a dictionary")
        bdata, err = encode_msgpack(data, use_lz4)
        return bdata, "application/octet-stream", err
    elif encoder == "numpy":
        if not isinstance(data, dict):
            return ''.encode(), "application/octet-stream", ValueError("Data is not a dictionary")
        bdata, err = encode_numpy(data, use_lz4)
        return bdata, "application/octet-stream", err
    elif encoder == "multipart":
        if not isinstance(data, dict):
            return ''.encode(), "", ValueError("Data is not a dictionary")
        return encode_multipart(data, use_lz4)
    
    return ''.encode(), "", ValueError(f"Encoder {encoder} is not supported")

## Data encoders
def encode_file(file: BytesIO, use_lz4: bool=False) -> tuple[bytes, Error]:
    """
    Encode file to bytes
    Arguments:
    file: BytesIO
    """
    if not file:
        return ''.encode(), ValueError("No data to encode")
    if not isinstance(file, BytesIO):
        return ''.encode(), ValueError("Data is not a file")
    try:
        data = file.read()
    except Exception as e:
        return ''.encode(), ValueError(f"Error encoding file: {e}")
    if use_lz4:
        try:
            data = lz4.compress(data)
        except Exception as e:
            return ''.encode(), ValueError(f"Error compressing file with lz4: {e}")
    return data, None

def encode_image(img: Image, use_lz4: bool=False) -> tuple[bytes, Error]:
    """
    Encode image to bytes
    Arguments:
    img: PIL Image
    """
    data = ''.encode()
    if img is None:
        return data, ValueError("No data to encode")
    try:
        buf = BytesIO()
        if img.format == "" or img.format is None:
            img = img.convert("RGB")
            img.format = "JPEG"
        img.save(buf, format=img.format)
        data = buf.getvalue()
    except Exception as e:
        return data, ValueError(f"Error encoding image: {e}")
    if use_lz4:
        try:
            data = lz4.compress(data)
        except Exception as e:
            return ''.encode(), ValueError(f"Error compressing file with lz4: {e}")
    return data, None

def encode_text(text: str, use_lz4: bool=False) -> tuple[bytes, Error]:
    """
    Encode text to bytes
    Arguments:
    text: str
    """
    data = ''.encode()
    if not isinstance(text, str):
        return data, ValueError("Data is not a string")
    try:
        data = text.encode("utf-8")
    except Exception as e:
        return data, ValueError(f"Error encoding text: {e}")
    if use_lz4:
        try:
            data = lz4.compress(data)
        except Exception as e:
            return ''.encode(), ValueError(f"Error compressing file with lz4: {e}")
    return data, None

def encode_json(in_data: dict, use_lz4: bool=False) -> tuple[bytes, Error]:
    """
    Encode json to bytes
    Arguments:
    in_data: dict
    """
    data = ''.encode()
    from json_tricks import dumps
    if in_data is None:
        return data, ValueError("No data to encode")
    try:
        s_data = dumps(in_data)
        data = str(s_data).encode("utf-8")
    except Exception as e:
        return data, ValueError(f"Error encoding json: {e}")
    if use_lz4:
        try:
            data = lz4.compress(data)
        except Exception as e:
            return ''.encode(), ValueError(f"Error compressing file with lz4: {e}")
    return data, None

def encode_msgpack(in_data: dict, use_lz4: bool=False) -> tuple[bytes, Error]:
    """
    Encode msgpack to bytes
    Arguments:
    in_data: dict
    """
    data = ''.encode()
    if in_data is None:
        return data, ValueError("No data to encode")
    try:
        data = msgpack.packb(in_data, default=m.encode)
    except Exception as e:
        return data, ValueError(f"Error encoding msgpack: {e}")
    if not isinstance(data, bytes):
        return b'', ValueError("Encoded data is not bytes")
    if use_lz4:
        try:
            data = lz4.compress(data)
        except Exception as e:
            return ''.encode(), ValueError(f"Error compressing file with lz4: {e}")
    return data, None

def encode_numpy(in_data: dict, use_lz4: bool=False) -> tuple[bytes, Error]:
    """
    Encode numpy to bytes
    Arguments:
    in_data: dict
    """
    return encode_msgpack(in_data, use_lz4)

def encode_multipart(data: dict, use_lz4: bool=False) -> tuple[bytes, str, Error]:
    """
    Encode multi-part data to bytes
    Arguments:
    data: dict
    """
    body = ''.encode()
    if data is None:
        return body, "", ValueError("No data to encode")
    try:
        from urllib3 import encode_multipart_formdata
        body, header = encode_multipart_formdata(data)
    except Exception as e:
        return body, "", ValueError(f"Error encoding multi-part data: {e}")
    if use_lz4:
        try:
            data = lz4.compress(data)
        except Exception as e:
            return body, "", ValueError(f"Error encoding multi-part data: {e}")
    return body, header, None

