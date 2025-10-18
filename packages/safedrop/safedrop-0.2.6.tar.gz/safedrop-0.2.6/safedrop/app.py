import ctypes
import sys
import os
from PIL import Image


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Determine library file name based on platform
if sys.platform.startswith("linux"):
    lib_file = os.path.join(BASE_DIR, "lib", "fileops.so")
elif sys.platform == "darwin":
    lib_file = os.path.join(BASE_DIR, "lib", "fileops.dylib")
elif sys.platform == "win32":
    lib_file = os.path.join(BASE_DIR, "lib", "fileops.dll")
else:
    raise RuntimeError(f"Unsupported OS: {sys.platform}")

# Check if library exists
if not os.path.exists(lib_file):
    raise FileNotFoundError(f"Shared library not found: {lib_file}")

# Load the shared library
lib = ctypes.CDLL(lib_file)

# Define encodeFiles function signature
lib.encodeFiles.argtypes = [
    ctypes.c_char_p,                  # const char* username
    ctypes.POINTER(ctypes.c_char_p),  # const char** file_paths
    ctypes.c_int,                     # int num_files
    ctypes.c_char_p,                  # const char* input_image_path
    ctypes.c_char_p                   # const char* output_image_path
]
# Use ctypes.c_bool if the function returns a bool
lib.encodeFiles.restype = ctypes.c_int

from pathlib import Path

class UnknownImageTypeError(Exception):
    pass

def detect_image_type(image_path: Path) -> str:
    """
    Detect the type of an image by reading its content (magic numbers).
    
    Supports: PNG, JPG/JPEG
    
    Args:
        image_path (Path or str): Path to the image file.
    
    Returns:
        str: Image type ("PNG" or "JPEG")
    
    Raises:
        UnknownImageTypeError: If the file type is not recognized.
        FileNotFoundError: If the file does not exist.
    """
    image_path = Path(image_path)
    
    if not image_path.is_file():
        raise FileNotFoundError(f"File not found: {image_path}")
    
    with image_path.open("rb") as f:
        header = f.read(8)  # 8 bytes is enough for PNG, JPEG
    
    # PNG signature: 89 50 4E 47 0D 0A 1A 0A
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "PNG"
    
    # JPEG signature: FF D8 FF
    if header.startswith(b"\xff\xd8\xff"):
        return "JPEG"
    
    raise UnknownImageTypeError(f"Unrecognized image type: {image_path}")


def convert_jpeg_to_png(input_path: Path, output_path: Path = None) -> Path:
    """
    Convert a JPG/JPEG image to PNG format.
    
    Args:
        input_path (Path or str): Path to the input JPEG image.
        output_path (Path or str, optional): Path to save the PNG image. 
            If None, saves in the same folder with .png extension.
    
    Returns:
        Path: Path to the saved PNG image.
    
    Raises:
        FileNotFoundError: If the input file does not exist.
        ValueError: If input file is not JPEG/JPG.
    """
    input_path = Path(input_path)
    
    if not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Default output path
    if output_path is None:
        output_path = input_path.with_suffix(".png")
    else:
        output_path = Path(output_path)
    
    # Open the JPEG image and save as PNG
    with Image.open(input_path) as img:
        img.save(output_path, format="PNG")
    
    return output_path
import locale 
encoding = locale.getpreferredencoding(False)

def safedrop(username: str, folder: str, image: str, output_image: str = None):
    """
    Encode all files under `folder` into a PNG image.

    Args:
        folder: Path to a folder containing files to encode.
        image: Path to the input PNG (must NOT be inside `folder`).
        output_image: Path to save the output PNG. If None, will default to *_sd.png
    Returns:
        Path to the encoded PNG with '_sd' suffix.
    """
    # Validate paths
    folder = os.path.abspath(folder)
    image = os.path.abspath(image)

    if not os.path.isdir(folder):
        raise ValueError(f"❌ Folder not found: {folder}")

    if not os.path.isfile(image):
        raise ValueError(f"❌ Input image not found: {image}")

    # Ensure image is not inside the folder
    if os.path.commonpath([folder]) == os.path.commonpath([folder, image]):
        raise ValueError("❌ Input image cannot be inside the source folder.")

    imgtype = detect_image_type(image)
    if imgtype in ['JPEG']:
        image = convert_jpeg_to_png(image)
        image = str(image)

    # Gather all files in folder (recursive)
    file_paths = []
    for root, _, files in os.walk(folder):
        for f in files:
            full_path = os.path.join(root, f)
            file_paths.append(full_path.encode(encoding))

    if not file_paths:
        raise ValueError(f"⚠️ No files found under folder: {folder}")

    # Prepare ctypes array
    FileArray = ctypes.c_char_p * len(file_paths)
    file_array = FileArray(*file_paths)

    # Prepare input/output PNG
    input_png = image.encode(encoding)
    output_png = output_image or os.path.splitext(image)[0] + "_sd.png"
    output_png_b = output_png.encode(encoding)

    print(f"🧩 Safedropping {len(file_paths)} files from {folder}")
    print(f"Input image: {image}")
    print(f"Output image: {output_png}")

    res = lib.encodeFiles(username.encode('utf8'), file_array, len(file_paths), input_png, output_png_b)
    if res == 1:
        raise Exception(
            "Failed to encode files: the provided content exceeds the capacity of the image. "
            "Consider using a larger image, splitting the content across multiple images, "
            "or reducing the number of files to encode."
        )

    print(f"✅ Your files are safely stored in image: {output_png}.")
    return output_png

