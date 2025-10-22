#!/usr/bin/env python3
from __future__ import annotations
from io import BytesIO
from typing import Union
from soup_files import File

from ._version import (
    __module_name__, __author__, __license__, __modify_date__, __version__
)
from .image import ImageObject, CollectionImages
from .pdf import DocumentPdf, PageDocumentPdf, CollectionPagePdf
from .doc_stream import PdfStream


def __create_stream() -> PdfStream:
    st = PdfStream()
    st.clear()
    return st


def read_pdf(file: Union[str, File, bytes, BytesIO]) -> PdfStream:
    _pdf_stream = __create_stream()

    if isinstance(file, File):
        _pdf_stream.add_file_pdf(file)
    elif isinstance(file, str):
        _pdf_stream.add_file_pdf(File(file))
    elif isinstance(file, bytes):
        _pdf_stream.add_document(DocumentPdf(BytesIO(file)))
    elif isinstance(file, BytesIO):
        _pdf_stream.add_document(DocumentPdf(file))
    else:
        raise ValueError()
    return _pdf_stream


def read_files_pdf(files: Union[list[str], list[File]]) -> PdfStream:
    _pdf_stream = __create_stream()
    if len(files) == 0:
        return _pdf_stream

    if isinstance(files[0], str):
        for f in files:
            _pdf_stream.add_file_pdf(File(f))
    elif isinstance(files[0], File):
        _pdf_stream.add_files_pdf(files)
    else:
        raise ValueError()
    return _pdf_stream


def read_image(img: Union[str, File, bytes, BytesIO]) -> PdfStream:
    _pdf_stream = __create_stream()
    if isinstance(img, str):
        _pdf_stream.add_file_image(File(img))
    elif isinstance(img, File):
        _pdf_stream.add_image(ImageObject.create_from_file(img))
    elif isinstance(img, bytes):
        _pdf_stream.add_image(ImageObject.create_from_bytes(img))
    elif isinstance(img, BytesIO):
        img.seek(0)
        _pdf_stream.add_image(ImageObject.create_from_bytes(img.getvalue()))
    else:
        raise ValueError()
    return _pdf_stream


__all__ = [
    '__modify_date__', '__author__', '__license__', '__module_name__', '__version__',
    'PdfStream', 'DocumentPdf', 'PageDocumentPdf', 'CollectionPagePdf', 'CollectionImages',
    'read_pdf', 'read_files_pdf', 'read_image',
]

