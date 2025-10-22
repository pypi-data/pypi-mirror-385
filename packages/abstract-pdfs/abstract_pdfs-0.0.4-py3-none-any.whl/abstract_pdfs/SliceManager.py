## /src/abstract_pdfs/SliceManager.py
from .imports import *

def find_closest_pdf(directory: str) -> Optional[str]:
    directory = os.path.abspath(directory)
    target_name = os.path.basename(directory).lower().replace(' ', '_')
    closest_path, closest_depth = None, float('inf')

    for root, _, files in os.walk(directory, topdown=True):
        depth = root[len(directory):].count(os.sep)
        pdfs = [f for f in files if f.lower().endswith('.pdf')]
        if not pdfs:
            continue
        for f in pdfs:
            base = os.path.splitext(f)[0].lower().replace(' ', '_')
            if base == target_name:
                return os.path.join(root, f)
        if depth < closest_depth:
            closest_depth = depth
            closest_path = os.path.join(root, pdfs[0])
    return closest_path


def get_pdf_dir(pdf_item):
    if os.path.isdir(pdf_item):
        return find_closest_pdf(pdf_item)
    return pdf_item


class SliceManager:
    """Column-aware OCR and text cleaner using multiple engines."""

    def __init__(self, pdf_path: str, out_root: str = None,
                 engines='paddle',
                 engine_directory=False,
                 visualize=False):
        self.pdf_path = pdf_path
        self.out_root = out_root or get_pdf_dir_or_path(pdf_path)
        self.file_parts = get_file_parts(self.pdf_path)
        self.filename = self.file_parts.get("filename")
        self.base = os.path.join(self.out_root, self.filename)
        self.visualize = visualize
        self.imgs = []

        self.engines = make_list(engines or Config.OCR_ENGINES)
        self.engine_directory = engine_directory or (len(self.engines) > 1)

        # Create directories
        self.pages = make_dir(self.base, "pages")
        self.images = make_dir(self.base, "images")
        self.cols = make_dir(self.base, "columns")

        self.engine_dirs = {}
        for engine in self.engines:
            root = make_dir(self.base, engine) if self.engine_directory else make_dir(self.base)
            self.engine_dirs[engine] = {
                "root": root,
                "raw_tx": make_dir(root, "text"),
                "clean_tx": make_dir(root, "text", "cleaned"),
                "pre_img": make_dir(root, "preprocessed_images"),
                "pre_txt": make_dir(root, "preprocessed_text"),
                "pre_cln": make_dir(root, "preprocessed_text", "cleaned"),
                "final_raw": os.path.join(root, f"{self.filename}_{engine}_FULL.txt"),
                "final_clean": os.path.join(root, f"{self.filename}_{engine}_FULL_cleaned.txt"),
            }

    # ---------------------------------------------------------

    def extract_page_image(self, page, i: int) -> Optional[str]:
        try:
            pdf_filename = f"page_{i}.pdf"
            png_filename = f"page_{i}.png"
            page_pdf = os.path.join(self.pages, pdf_filename)

            writer = PyPDF2.PdfWriter()
            writer.add_page(page)
            with open(page_pdf, "wb") as f:
                writer.write(f)

            images = convert_from_path(page_pdf)
            if not images:
                logger.warning(f"No images extracted for page {i}")
                return None

            img_path = os.path.join(self.images, png_filename)
            images[0].save(img_path, "PNG")
            return img_path
        except Exception as e:
            logger.error(f"❌ extract_page_image failed on page {i}: {e}")
            return None

    # ---------------------------------------------------------

    def process_single_column(self, img_path: str, i: int, engine: str, side_label: str = "") -> Tuple[str, str]:
        """Run OCR and cleaning on one image for a given engine."""
        dirs = self.engine_dirs[engine]
        suffix = f"_{side_label}" if side_label else ""
        png_name = f"page_{i}{suffix}.png"
        txt_name = f"page_{i}{suffix}.txt"

        proc_img = os.path.join(dirs["pre_img"], png_name)
        preprocess_image(img_path, proc_img)

        image_array = cv2.imread(str(proc_img))
        df = layered_ocr_img(image_array, engine=engine)
        txt = "\n".join(df["text"].tolist())
        cln = clean_text(txt)

        write_to_file(contents=txt, file_path = os.path.join(dirs["raw_tx"], txt_name))
        write_to_file(contents=cln,file_path =  os.path.join(dirs["clean_tx"], txt_name))

        logger.info(f"✅ [{engine}] OCR complete for page {i}{suffix}")
        return txt, cln

    # ---------------------------------------------------------

    def process_page(self, page, i: int, engine: str) -> Dict[str, Dict[str, str]]:
        filename = f"page_{i}"
        columns_js = {
            "left": {"filename": None, "image": {"img": None, "path": None},
                     "processed": {"img": None, "path": None},
                     "raw": {"text": None, "path": None},
                     "clean": {"text": None, "path": None}},
            "right": {"filename": None, "image": {"img": None, "path": None},
                      "processed": {"img": None, "path": None},
                      "raw": {"text": None, "path": None},
                      "clean": {"text": None, "path": None}},
            "page": {"num": i, "filename": filename, "engine": engine,
                     "image": {"img": None, "path": None},
                     "raw": {"text": None, "path": None},
                     "clean": {"text": None, "path": None},
                     "path": None},
        }

        try:
            img_path = self.extract_page_image(page, i)
            if not img_path:
                return columns_js
            columns_js["page"]["path"] = img_path

            divider, _ = detect_columns(img_path)
            validate_reading_order(img_path, divider, visualize=self.visualize)

            column_js = slice_columns(img_path, divider, self.cols, columns_js)
            for col_name, meta in column_js.items():
                if col_name not in ("left", "right"):
                    continue
                txt, cln = self.process_single_column(meta["image"]["path"], i, engine, col_name)
                meta["raw"]["text"], meta["clean"]["text"] = txt, cln

            return columns_js
        except Exception as e:
            logger.error(f"❌ [{engine}] Error processing page {i}: {e}")
            traceback.print_exc()
            return columns_js

    # ---------------------------------------------------------

    def process_pdf_for_engine(self, engine: str):
        logger.info(f"📘 [{engine}] Starting SliceManager for {self.filename}")
        reader = PyPDF2.PdfReader(self.pdf_path)
        dirs = self.engine_dirs[engine]
        all_left, all_right = [], []

        for i, page in enumerate(reader.pages, start=1):
            columns_js = self.process_page(page, i, engine)
            if columns_js["left"]["raw"]["text"]:
                all_left.append(columns_js["left"]["raw"]["text"])
            if columns_js["right"]["raw"]["text"]:
                all_right.append(columns_js["right"]["raw"]["text"])

        write_to_file(contents="\n\n".join(all_left), file_path = os.path.join(dirs["raw_tx"], f"{self.filename}_{engine}_LEFT.txt"))
        write_to_file(contents="\n\n".join(all_right), file_path = os.path.join(dirs["raw_tx"], f"{self.filename}_{engine}_RIGHT.txt"))
        logger.info(f"✅ [{engine}] Finished column-separated OCR for {self.filename}")

    # ---------------------------------------------------------

    def process_pdf(self):
        logger.info(f"📕 Starting multi-engine OCR for {self.filename}")
        for engine in self.engines:
            self.process_pdf_for_engine(engine)
        logger.info(f"🏁 Finished all engines for {self.filename}")
