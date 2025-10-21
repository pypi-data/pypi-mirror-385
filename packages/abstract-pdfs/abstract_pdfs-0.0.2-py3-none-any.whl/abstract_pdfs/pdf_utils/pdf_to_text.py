
from .imports import *

# -----------------------------------------------------
# Core Utilities
# -----------------------------------------------------
def get_file_hash(file_path: str, hash_algorithm: str = "sha256", chunk_size: int = 8192) -> str:
    """Calculate the hash of a file's contents."""
    hash_obj = hashlib.new(hash_algorithm)
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def is_pdf_file(file_path: str) -> bool:
    """Check if a file is a PDF based on its extension."""
    return file_path.lower().endswith(".pdf")


def get_preferred_filename(filenames: List[str]) -> str:
    """Return the best name among duplicates (lowest numbered or unsuffixed)."""
    name_info = []
    for fname in filenames:
        base_name, ext = os.path.splitext(fname)
        match = re.match(r"^(.*?)(?:_(\d+))?$", base_name)
        if match:
            core_name, suffix = match.groups()
            suffix = int(suffix) if suffix else None
            name_info.append((core_name, suffix, ext, fname))
    name_info.sort(key=lambda x: (x[1] is not None, x[1] or 0))
    return name_info[0][3]


def get_pdf_obj(pdf_obj: Union[str, PyPDF2.PdfReader]) -> Optional[PyPDF2.PdfReader]:
    """Return a PyPDF2 PdfReader from path or object."""
    if is_str(pdf_obj) and is_pdf_file(pdf_obj):
        try:
            return PyPDF2.PdfReader(pdf_obj)
        except Exception as e:
            logger.error(f"Failed to read PDF {pdf_obj}: {e}")
            return None
    return pdf_obj


def get_pdf_pages(pdf_file: Union[str, PyPDF2.PdfReader]) -> int:
    """Get the number of pages in a PDF."""
    pdf_obj = get_pdf_obj(pdf_file)
    return len(pdf_obj.pages) if pdf_obj else 0


def save_pdf(output_file_path: str, pdf_writer: PyPDF2.PdfWriter):
    """Write a PyPDF2 writer object to disk."""
    with open(output_file_path, "wb") as f:
        pdf_writer.write(f)


# -----------------------------------------------------
# Page & Text Extraction
# -----------------------------------------------------
def split_pdf(input_path: str, pdf_pages_dir: str, file_name: Optional[str] = None) -> List[str]:
    """Split a PDF into one file per page."""
    pdf_pages = []
    file_name = get_file_name(input_path) if not file_name else file_name
    mkdirs(pdf_pages_dir)

    try:
        with open(input_path, "rb") as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for i, page in enumerate(pdf_reader.pages, start=1):
                writer = PyPDF2.PdfWriter()
                writer.add_page(page)
                out_path = os.path.join(pdf_pages_dir, f"{file_name}_page_{i}.pdf")
                save_pdf(out_path, writer)
                pdf_pages.append(out_path)
    except Exception as e:
        logger.warning(f"Skipping {input_path} due to error: {e}")
    return pdf_pages


# -----------------------------------------------------
# PDF → IMAGE → TEXT Conversion
# -----------------------------------------------------
def pdf_to_text_in_folders(src_dir: str, dest_base_dir: str):
    """
    Copy unique PDFs to individual folders under `dest_base_dir`,
    split into pages, convert to images, extract text, and save results.
    """
    src = Path(src_dir)
    dest_base = Path(dest_base_dir)
    dest_base.mkdir(parents=True, exist_ok=True)

    hash_registry = {}
    copied_count = skipped_count = 0

    # Phase 1: Identify unique PDFs
    for fname in os.listdir(src):
        if not is_pdf_file(fname):
            continue
        src_file = src / fname
        file_hash = get_file_hash(src_file)
        entry = hash_registry.setdefault(file_hash, {"filename": fname, "duplicates": []})
        entry["duplicates"].append(str(src_file))

    # Phase 2: Process each unique
    for file_hash, info in hash_registry.items():
        duplicates = info["duplicates"]
        preferred_name = get_preferred_filename([Path(f).name for f in duplicates])
        src_file = Path(duplicates[0])

        base_name = Path(preferred_name).stem
        pdf_dir = dest_base / base_name
        for sub in ["pdf_pages", "images", "text"]:
            mkdirs(pdf_dir / sub)

        # Copy main file
        dest_file = pdf_dir / preferred_name
        try:
            shutil.copy2(src_file, dest_file)
            copied_count += 1
            logger.info(f"Copied: {src_file} -> {dest_file}")
        except Exception as e:
            logger.error(f"Failed copy: {src_file}: {e}")
            continue

        # Split into pages
        pdf_pages = split_pdf(dest_file, pdf_dir / "pdf_pages")
        if not pdf_pages:
            continue

        # Convert and OCR
        for page_path in pdf_pages:
            try:
                images = convert_from_path(page_path)
                if not images:
                    continue
                img_path = pdf_dir / "images" / (Path(page_path).stem + ".png")
                txt_path = pdf_dir / "text" / (Path(page_path).stem + ".txt")
                images[0].save(img_path, "PNG")
                text = image_to_text(img_path)
                write_to_file(file_path=txt_path, contents=text)
                logger.info(f"Converted: {page_path} → {img_path} → {txt_path}")
            except Exception as e:
                logger.error(f"Error converting {page_path}: {e}")

        # Duplicate info
        if len(duplicates) > 1:
            skipped_count += len(duplicates) - 1
            logger.info(f"Skipped duplicates: {', '.join(duplicates[1:])}")

    logger.info(f"✅ PDFs processed: {copied_count} | Skipped: {skipped_count}")


# -----------------------------------------------------
# Recursive Conversion
# -----------------------------------------------------
def convert_pdf_tree(pdf_dir: str):
    """Process a single PDF directory recursively."""
    pdf_dir = Path(pdf_dir)
    out_root = pdf_dir / "pdf_convert" / pdf_dir.name
    mkdirs(out_root)

    dirs = [p for p in pdf_dir.iterdir() if p.is_dir()] + [pdf_dir]
    for d in dirs:
        dest = out_root / d.name
        mkdirs(dest)
        pdf_to_text_in_folders(str(d), str(dest))



