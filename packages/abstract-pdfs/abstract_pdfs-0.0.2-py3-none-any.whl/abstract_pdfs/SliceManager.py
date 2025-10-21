from abstract_ocr import *
class SliceManager:
    """
    Modular manager for PDF column-aware OCR and text cleaning.
    Runs separate OCR passes for Tesseract, EasyOCR, and PaddleOCR.
    Each engine gets its own output tree and collated results.
    """

    def __init__(self, pdf_path: str, out_root: str,engines='paddle',engine_directory=False,visualize=False):
        self.pdf_path = pdf_path
        self.out_root = out_root
        self.file_parts = get_file_parts(self.pdf_path)
        self.filename = self.file_parts.get("filename")
        self.base = os.path.join(self.out_root, self.filename)
        self.visualize=visualize
        self.engine_directory = engine_directory
        # Engines to run
        self.engines = make_list(engines or Config.OCR_ENGINES)
        if len(self.engines) >1:
            self.engine_directory=True
        # Create global directories
        self.pages = make_dir(self.base, "pages")
        self.images = make_dir(self.base, "images")
        self.cols = make_dir(self.base, "columns")

        # Create separate per-engine trees
        self.engine_dirs = {}
        for engine in self.engines:
            root = make_dir(self.base)
            if self.engine_directory:
                root = make_dir(self.base, engine)
            dirs = {
                "root": root,
                "raw_tx": make_dir(root, "text"),
                "clean_tx": make_dir(root, "text", "cleaned"),
                "pre_img": make_dir(root, "preprocessed_images"),
                "pre_txt": make_dir(root, "preprocessed_text"),
                "pre_cln": make_dir(root, "preprocessed_text", "cleaned"),
                "final_raw": os.path.join(root, f"{self.filename}_{engine}_FULL.txt"),
                "final_clean": os.path.join(root, f"{self.filename}_{engine}_FULL_cleaned.txt"),
            }
            self.engine_dirs[engine] = dirs

    # ---------------------------------------------------------

    def extract_page_image(self, page, i: int) -> Optional[str]:
        """Convert a single PDF page to PNG."""
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
        """Perform OCR + cleaning on one image for a given engine."""
        dirs = self.engine_dirs[engine]
        side_suffix = f"_{side_label}" if side_label else ""
        png_filename = f"page_{i}{side_suffix}.png"
        txt_filename = f"page_{i}{side_suffix}.txt"

        proc_img = os.path.join(dirs["pre_img"], png_filename)
        preprocess_image(img_path, proc_img)

        image_array = cv2.imread(str(proc_img))
        df = layered_ocr_img(image_array, engine=engine)
        txt = "\n".join(df["text"].tolist())
        cln = clean_text(txt)

        # Save engine-specific variants
        write_to_file(contents=txt, file_path=os.path.join(dirs["raw_tx"], txt_filename))
        write_to_file(contents=cln, file_path=os.path.join(dirs["clean_tx"], txt_filename))
        write_to_file(contents=txt, file_path=os.path.join(dirs["pre_txt"], txt_filename))
        write_to_file(contents=cln, file_path=os.path.join(dirs["pre_cln"], txt_filename))

        logger.info(f"✅ [{engine}] OCR complete for page {i}{side_suffix}")
        return txt, cln

    # ---------------------------------------------------------

    def process_page(self, page, i: int, engine: str) -> Tuple[str, str]:
        """Process one PDF page for a single OCR engine."""
        try:
            img_path = self.extract_page_image(page, i)
            if not img_path:
                return "", ""

            div, _ = detect_columns(img_path)
            two = validate_reading_order(img_path, div,visualize=self.visualize)
            if two:
                logger.info(f"📗 [{engine}] Page {i}: Split detected — processing left/right halves.")
                left, right = slice_columns(img_path, div, self.cols, f"page_{i}")

                left_txt, left_cln = self.process_single_column(left, i, engine, "left")
                right_txt, right_cln = self.process_single_column(right, i, engine, "right")

                merged_txt = f"{left_txt}\n{right_txt}"
                merged_cln = f"{left_cln}\n{right_cln}"
            else:
                merged_txt, merged_cln = self.process_single_column(img_path, i, engine)

            return merged_txt, merged_cln

        except Exception as e:
            logger.error(f"❌ [{engine}] Error processing page {i}: {e}")
            traceback.print_exc()
            return "", ""

    # ---------------------------------------------------------

    def process_pdf_for_engine(self, engine: str):
        """Run full pipeline for a specific OCR engine."""
        logger.info(f"📘 [{engine}] Starting SliceManager for {self.filename}")
        reader = PyPDF2.PdfReader(self.pdf_path)
        all_txt, all_cln = [], []

        for i, page in enumerate(reader.pages, start=1):
            txt, cln = self.process_page(page, i, engine)
            if txt.strip():
                all_txt.append(txt)
            if cln.strip():
                all_cln.append(cln)

        final_txt = "\n\n".join(all_txt)
        final_cln = "\n\n".join(all_cln)

        dirs = self.engine_dirs[engine]
        write_to_file(contents=final_txt, file_path=dirs["final_raw"])
        write_to_file(contents=final_cln, file_path=dirs["final_clean"])

        logger.info(f"✅ [{engine}] Completed and collated: {dirs['final_raw']}")

    # ---------------------------------------------------------

    def process_pdf(self):
        """Run the entire PDF through all configured OCR engines."""
        logger.info(f"📕 Starting multi-engine OCR for {self.filename}")
        for engine in self.engines:
            self.process_pdf_for_engine(engine)
        logger.info(f"🏁 Finished all engines for {self.filename}")
