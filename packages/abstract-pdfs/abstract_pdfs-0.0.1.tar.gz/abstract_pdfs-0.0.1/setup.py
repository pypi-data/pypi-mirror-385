from time import time
import setuptools
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setuptools.setup(
    name='abstract_pdfs',
    version='0.0.1',
    author='putkoff',
    author_email='partners@abstractendeavors.com',
    description='A modular OCR and PDF-processing toolkit for automated text extraction, deduplication, and multi-engine column-aware OCR using Tesseract, EasyOCR, and PaddleOCR',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/AbstractEndeavors/abstract_pdfs',
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.11',
    ],
    install_requires=[
        'abstract_ocr',
        'abstract_utilities',
        ]
,
   package_dir={"": "src"},
   packages=setuptools.find_packages(where="src"),
   python_requires=">=3.6",
  

)
