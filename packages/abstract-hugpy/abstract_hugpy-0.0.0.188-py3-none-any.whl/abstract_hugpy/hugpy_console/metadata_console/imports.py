from ..imports import *
from .constant import *
from abstract_utilities import *
import fitz  # PyMuPDF
from pdf2image import convert_from_path
from PIL import Image
import pytesseract, cv2, os, tempfile, json
from pathlib import Path
from typing import Dict, List
import hashlib
