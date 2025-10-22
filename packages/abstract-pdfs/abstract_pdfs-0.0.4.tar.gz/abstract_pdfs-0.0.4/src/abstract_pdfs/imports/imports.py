from typing import *
from PIL import Image
from pathlib import Path
from abstract_ocr import *
from pdf2image import convert_from_path
import os, shutil, hashlib, re, logging, PyPDF2
from abstract_utilities import get_file_parts, write_to_file, get_logFile
from abstract_utilities.path_utils import is_file, mkdirs, get_directory, get_base_name, get_ext, get_file_name
logger = get_logFile("abstract_pdf")
