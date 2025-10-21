#!/usr/bin/env python3
"""
abstract_ocr.pdf_utils.pdf_tools
--------------------------------
Standalone utilities for PDF page extraction, image conversion, and text preprocessing.

Dependencies:
    - PyPDF2
    - pdf2image
    - PIL (Pillow)
    - abstract_utilities (for write_to_file, get_file_parts)
    - abstract_ocr.ocr_utils (for convert_image_to_text, preprocess_image, clean_text)
"""

from .imports import *


# ------------------------------------------------------
#  IMAGE → PDF
# ------------------------------------------------------
def images_to_pdf(image_paths: List[str], output_pdf: Optional[str] = None) -> str:
    """Combine multiple images into a single PDF file."""
    if not image_paths:
        raise ValueError("❌ No image files provided for conversion.")

    first_image_path = str(image_paths[0])
    dirname = os.path.dirname(first_image_path)
    processed_pdf_path = os.path.join(dirname, "processed_pdf.pdf")
    output_pdf = output_pdf or processed_pdf_path

    # Prepare first image
    first_image = Image.open(first_image_path)
    if first_image.mode in ("RGBA", "P"):
        first_image = first_image.convert("RGB")

    # Process rest
    image_list = []
    for img_path in image_paths[1:]:
        img = Image.open(img_path)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        image_list.append(img)

    os.makedirs(os.path.dirname(output_pdf), exist_ok=True)
    first_image.save(output_pdf, "PDF", resolution=100.0, save_all=True, append_images=image_list)
    logger.info(f"📘 PDF saved as: {output_pdf}")
    return output_pdf


# ------------------------------------------------------
#  PDF → MULTI-PAGE PROCESSOR
# ------------------------------------------------------
def process_pdf(main_pdf_path: str, pdf_output_dir: Optional[str] = None) -> None:
    """
    Full pipeline:
      1. Split PDF into single-page PDFs.
      2. Convert each to PNG.
      3. Extract, clean, preprocess, and save text variants.

    Outputs a folder structure like:
      processed_pdf/
      ├── pdf_pages/
      ├── images/
      ├── text/
      │   └── cleaned/
      ├── preprocessed_images/
      └── preprocessed_text/
          └── cleaned/
    """
    file_parts = get_file_parts(main_pdf_path)
    pdf_name = file_parts.get("filename")
    dirname = file_parts.get("dirname")
    processed_pdf_dir = os.path.join(dirname, f"{pdf_name}_processed")
    pdf_output_dir = pdf_output_dir or processed_pdf_dir

    # Directory structure
    subdirs = {
        "pages": os.path.join(pdf_output_dir, "pdf_pages"),
        "images": os.path.join(pdf_output_dir, "images"),
        "text": os.path.join(pdf_output_dir, "text"),
        "cleaned": os.path.join(pdf_output_dir, "text", "cleaned"),
        "pre_img": os.path.join(pdf_output_dir, "preprocessed_images"),
        "pre_txt": os.path.join(pdf_output_dir, "preprocessed_text"),
        "pre_cln": os.path.join(pdf_output_dir, "preprocessed_text", "cleaned"),
    }
    for path in subdirs.values():
        os.makedirs(path, exist_ok=True)

    pdf_reader = PyPDF2.PdfReader(main_pdf_path)
    num_pages = len(pdf_reader.pages)
    logger.info(f"📄 Processing {pdf_name} with {num_pages} pages...")

    for i, page in enumerate(pdf_reader.pages, start=1):
        try:
            base = f"{pdf_name}_page_{i}"
            basename_pdf = f"{base}.pdf"
            basename_png = f"{base}.png"
            pre_png = f"preprocessed_{basename_png}"
            basename_txt = f"{base}.txt"

            # Save single-page PDF
            page_path = os.path.join(subdirs["pages"], basename_pdf)
            with open(page_path, "wb") as f:
                writer = PyPDF2.PdfWriter()
                writer.add_page(page)
                writer.write(f)

            # Convert to image
            images = convert_from_path(page_path)
            if not images:
                logger.warning(f"⚠️ No image rendered for page {i}")
                continue
            img_path = os.path.join(subdirs["images"], basename_png)
            images[0].save(img_path, "PNG")

            # OCR (raw)
            text = convert_image_to_text(img_path)
            write_to_file(os.path.join(subdirs["text"], basename_txt), text)

            # Cleaned OCR
            cleaned_text = clean_text(text)
            write_to_file(os.path.join(subdirs["cleaned"], basename_txt), cleaned_text)

            # Preprocess + OCR again
            pre_img_path = os.path.join(subdirs["pre_img"], pre_png)
            preprocess_image(img_path, pre_img_path)

            pre_text = convert_image_to_text(pre_img_path)
            write_to_file(os.path.join(subdirs["pre_txt"], basename_txt), pre_text)

            pre_clean_text = clean_text(pre_text)
            write_to_file(os.path.join(subdirs["pre_cln"], basename_txt), pre_clean_text)

            logger.info(f"✅ Processed page {i} of {pdf_name}")

        except Exception as e:
            logger.error(f"❌ Error processing page {i} of {pdf_name}: {e}")
            continue
