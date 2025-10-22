from .imports import *
def get_pdf_path(pdf_path):
    pdf_path = str(pdf_path)
    if os.path.isdir(pdf_path):
        dirlist = os.listdir(pdf_path)
        pdfs = [os.path.join(pdf_path,item) for item in dirlist if item and item.endswith('.pdf') and '_page_' not in item ]
        if pdfs and len(pdfs)>0:
            pdf_path = pdfs[0]
    if pdf_path and os.path.isfile(pdf_path) and pdf_path.endswith('.pdf'):
        return pdf_path
def get_pdf_dir(pdf_dir):
    pdf_dir = str(pdf_dir)
    if os.path.isdir(pdf_dir):
        dirlist = os.listdir(pdf_dir)
        pdfs = [os.path.join(pdf_dir,item) for item in dirlist if item and item.endswith('.pdf') and '_page_' not in item ]
        if pdfs and len(pdfs)>0:
            return pdf_dir
    if pdf_dir and os.path.isfile(pdf_dir) and pdf_dir.endswith('.pdf'):
        return os.path.dirname(pdf_dir)
    if pdf_dir and os.path.isfile(pdf_dir) and (pdf_dir.endswith('.txt') or pdf_dir.endswith('.png')):
        file_parts = get_file_parts(pdf_dir)
        return file_parts.get('parent_dirname')

def get_pdf_dir_or_path(path: str):
    """
    Normalize input path to a proper PDF directory or PDF file.
    If directory: finds closest valid PDF (no '_page_' in name).
      - Prefers one matching the directory's base name.
      - If found PDF name differs, creates new subdir named after PDF
        and moves the PDF inside it.
    Returns absolute path to the PDF file or directory.
    """
    path = str(path)
    path = os.path.abspath(path)

    # If it's a directory, find valid PDF inside
    if os.path.isdir(path):
        dir_name = os.path.basename(path)
        dir_items = os.listdir(path)
        pdfs = [
            os.path.join(path, f)
            for f in dir_items
            if f.lower().endswith('.pdf') and '_page_' not in f
        ]

        if pdfs:
            # Prefer PDF that matches directory name
            for pdf in pdfs:
                base = os.path.splitext(os.path.basename(pdf))[0]
                if base.lower() == dir_name.lower():
                    return pdf

            # Otherwise take the first
            pdf = pdfs[0]
            pdf_base = os.path.splitext(os.path.basename(pdf))[0]
            
            # Create new subdirectory if needed
            new_dir = os.path.join(path, pdf_base)
            if not os.path.samefile(path, new_dir):
                os.makedirs(new_dir, exist_ok=True)
                new_pdf_path = os.path.join(new_dir, os.path.basename(pdf))
                shutil.move(pdf, new_pdf_path)
                return new_pdf_path

            return pdf

        # If directory but no PDFs
        return path

    # If it's a file
    if os.path.isfile(path):
        if path.lower().endswith('.pdf'):
            return os.path.dirname(path)
        if path.lower().endswith(('.png', '.txt')):
            file_parts = get_file_parts(path)
            return file_parts.get('parent_dirname')

    return None
def get_manifest_path(pdf_dir):
    pdf_dir = str(pdf_dir)
    pdf_dir = get_pdf_dir(pdf_dir)
    manifest_path = os.path.join(str(pdf_dir),MANIFEST_NAME)
    return manifest_path
def load_manifest(pdf_dir=None,manifest_path=None):
    pdf_dir = str(pdf_dir) if pdf_dir else pdf_dir
    manifest_path = str(manifest_path) if manifest_path else manifest_path
    if pdf_dir==None and manifest_path==None:
        return {}
    manifest_path = manifest_path or get_manifest_path(pdf_dir)
    if not os.path.isfile(manifest_path):
        safe_dump_to_json(data={},file_path=manifest_path)
    manifest = safe_load_json(manifest_path)
    return manifest
def save_manifest_data(data=None,pdf_dir=None,override=False):
    pdf_dir = str(pdf_dir) if pdf_dir else pdf_dir
    manifest_path = get_manifest_path(pdf_dir)
    if data in [None,{}] and override == True:
        data = load_manifest(pdf_dir,manifest_path=manifest_path)
    else:
        data = {}
    safe_dump_to_json(data=data,file_path=manifest_path)
