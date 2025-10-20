#!/usr/bin/env python3

from __future__ import annotations
from abc import ABC, abstractmethod
from soup_files import (
    File, Directory, ProgressBarAdapter, CreatePbar, InputFiles, LibraryDocs
)
from convert_stream.mod_types.table_types import (
    ListItems, create_void_table, create_map_from_file_values, get_text_from_file
)
from convert_stream.text.string import FindText
from convert_stream.pdf.pdf_document import SearchableTextPdf, DocumentPdf


class PdfFinder(object):
    """
        Classe para Filtrar texto em documentos PDF,
    """

    def __init__(self):
        self.docs_collection: dict[File, DocumentPdf] = {}

    def is_empty(self) -> bool:
        return len(self.docs_collection) == 0

    def clear(self) -> None:
        self.docs_collection.clear()

    def add_file_pdf(self, file: File) -> None:
        if file.is_pdf():
            self.docs_collection[file] = DocumentPdf.create_from_file(file)

    def add_files_pdf(self, files: list[File]) -> None:
        for f in files:
            self.add_file_pdf(f)

    def add_directory_pdf(self, dir_pdf: Directory) -> None:
        files = InputFiles(dir_pdf).get_files(file_type=LibraryDocs.PDF)
        if len(files) > 0:
            self.add_files_pdf(files)

    def find(
            self, text: str,
            separator: str = '\n',
            iqual: bool = False,
            case: bool = False,
            silent: bool = False,
            ) -> SearchableTextPdf:
        """
            Filtrar texto retornando a primeira ocorrência do Documento PDF.
        """
        _searchable = SearchableTextPdf(silent)
        if self.is_empty():
            return _searchable

        for file_key in self.docs_collection.keys():
            current_doc: DocumentPdf = self.docs_collection[file_key]
            for page_pdf in current_doc.to_pages():
                text_str_in_page = page_pdf.to_string()
                if (text_str_in_page == 'nas') or (text_str_in_page is None):
                    continue
                try:
                    fd = FindText(text_str_in_page, separator=separator)
                    idx = fd.find_index(text, iqual=iqual, case=case)
                    if idx is None:
                        continue
                    math_text = fd.get_index(idx)
                except Exception as err:
                    print(f'{__class__.__name__} {err}')
                else:
                    _searchable.add_line(
                        math_text,
                        num_page=str(page_pdf.number_page),
                        num_line=str(idx + 1),
                        file=file_key.absolute(),
                    )
                    return _searchable
            del current_doc
        return _searchable

    def find_all(
                self, text: str,
                separator: str = '\n',
                iqual: bool = False,
                case: bool = False,
                silent: bool = False,
            ) -> SearchableTextPdf:
        """
            Filtrar texto em documento PDF e retorna todas as ocorrências do texto
        encontradas no documento, incluindo o número da linha, página e nome do arquivo
        em cada ocorrência.
        """
        _searchable = SearchableTextPdf(silent)
        if self.is_empty():
            return _searchable

        for file_key in self.docs_collection.keys():
            current_doc: DocumentPdf = self.docs_collection[file_key]
            for page_pdf in current_doc.to_pages():
                text_str_in_page = page_pdf.to_string()
                if (text_str_in_page == 'nas') or (text_str_in_page is None):
                    continue
                try:
                    _values = text_str_in_page.split(separator)
                    for num, item in enumerate(_values):
                        if case:
                            if iqual:
                                if text == item:
                                    _searchable.add_line(
                                        item,
                                        num_page=str(page_pdf.number_page),
                                        num_line=str(num + 1),
                                        file=file_key.absolute(),
                                    )
                            else:
                                if text in item:
                                    _searchable.add_line(
                                        item,
                                        num_page=str(page_pdf.number_page),
                                        num_line=str(num + 1),
                                        file=file_key.absolute(),
                                    )
                        else:
                            if iqual:
                                if text.lower() == item.lower():
                                    _searchable.add_line(
                                        item,
                                        num_page=str(page_pdf.number_page),
                                        num_line=str(num + 1),
                                        file=file_key.absolute(),
                                    )
                            else:
                                if text.lower() in item.lower():
                                    _searchable.add_line(
                                        item,
                                        num_page=str(page_pdf.number_page),
                                        num_line=str(num + 1),
                                        file=file_key.absolute(),
                                    )
                except Exception as e:
                    print(f'{__class__.__name__} {e}')
        return _searchable
