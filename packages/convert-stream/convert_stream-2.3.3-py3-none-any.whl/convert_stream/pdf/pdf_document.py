#!/usr/bin/env python3
#
"""
    Módulo para trabalhar com imagens
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from io import BytesIO
from typing import Union
import pandas as pd
from soup_files import File, Directory, LibraryDocs, InputFiles, ProgressBarAdapter, JsonConvert
from convert_stream.mod_types import get_void_metadata, get_hash_from_bytes
from convert_stream.mod_types.table_types import (
    ListItems, ListString, create_map_from_values, concat_maps, create_void_map, ColumnBody
)
from convert_stream.mod_types.enums import LibPDF, ColumnsTable
from convert_stream.mod_types.modules import (
    DEFAULT_LIB_PDF, ModDocPdf, PdfWriter, PdfReader, PageObject, fitz,
)
from convert_stream.pdf.pdf_page import PageDocumentPdf
from convert_stream.text import print_line, show_warning, FindText
from convert_stream.sheets.save import save_data


class SearchableTextPdf(object):
    """
        Esta classe serve para armazenar textos filtrados em documentos PDF
    guardando o texto buscado e outros elementos como a página em que o texto foi
    encontrado, linha e o nome do respetivo arquivo.
    """
    def __init__(self, silent: bool = False):
        self.silent = silent
        # Cada elemento encontrado na busca de texto, será guardado nesse objeto para
        # posterior consulta (self.elements), cada chave aqui deve ter uma lista de
        # tamanho igual.
        self.elements: dict[str, list[str]] = {
            ColumnsTable.NUM_PAGE.value: [],
            ColumnsTable.NUM_LINE.value: [],
            ColumnsTable.TEXT.value: [],
            ColumnsTable.FILE_PATH.value: [],
        }

    def __repr__(self):
        return f'SearchableTextPdf: {self.elements}'

    def is_empty(self) -> bool:
        return len(self.elements[ColumnsTable.TEXT.value]) == 0

    @property
    def first(self) -> dict[str, str]:
        if self.is_empty():
            return {}
        return {
            ColumnsTable.NUM_PAGE.value: self.elements[ColumnsTable.NUM_PAGE.value][0],
            ColumnsTable.NUM_LINE.value: self.elements[ColumnsTable.NUM_LINE.value][0],
            ColumnsTable.TEXT.value: self.elements[ColumnsTable.TEXT.value][0],
            ColumnsTable.FILE_PATH.value: self.elements[ColumnsTable.FILE_PATH.value][0],
        }

    @property
    def last(self) -> dict[str, str]:
        if self.is_empty():
            return {}
        return {
            ColumnsTable.NUM_PAGE.value: self.elements[ColumnsTable.NUM_PAGE.value][-1],
            ColumnsTable.NUM_LINE.value: self.elements[ColumnsTable.NUM_LINE.value][-1],
            ColumnsTable.TEXT.value: self.elements[ColumnsTable.TEXT.value][-1],
            ColumnsTable.FILE_PATH.value: self.elements[ColumnsTable.FILE_PATH.value][-1],
        }

    @property
    def length(self) -> int:
        return len(self.elements[ColumnsTable.TEXT.value])

    def get_item(self, idx: int) -> dict[str, str]:
        try:
            return {
                ColumnsTable.NUM_PAGE.value: self.elements[ColumnsTable.NUM_PAGE.value][idx],
                ColumnsTable.NUM_LINE.value: self.elements[ColumnsTable.NUM_LINE.value][idx],
                ColumnsTable.TEXT.value: self.elements[ColumnsTable.TEXT.value][idx],
                ColumnsTable.FILE_PATH.value: self.elements[ColumnsTable.FILE_PATH.value][idx],
            }
        except Exception as err:
            if not self.silent:
                print(err)
            return {}

    def add_line(self, text, *, num_page: str, num_line: str, file: str) -> None:
        if not self.silent:
            print_line()
            print(f'{file} => {text}')
        self.elements[ColumnsTable.NUM_PAGE.value].append(num_page)
        self.elements[ColumnsTable.NUM_LINE.value].append(num_line)
        self.elements[ColumnsTable.TEXT.value].append(text)
        self.elements[ColumnsTable.FILE_PATH.value].append(file)

    def clear(self) -> None:
        for _k in self.elements.keys():
            self.elements[_k].clear()

    def to_string(self) -> str:
        """
            Retorna o texto da coluna TEXT em formato de string
        ou 'nas' em caso de erro nas = Not a String
        """
        try:
            return ' '.join(self.elements[ColumnsTable.TEXT.value])
        except Exception as e:
            print(e)
            return 'nas'

    def to_data_frame(self) -> pd.DataFrame:
        return pd.DataFrame.from_dict(self.elements)

    def to_file_json(self, file: File):
        """Exporta os dados da busca para um arquivo .JSON"""
        dt = JsonConvert.from_dict(self.elements).to_json_data()
        dt.to_file(file)

    def to_file_excel(self, file: File):
        """Exporta os dados da busca para um arquivo .XLSX"""
        save_data(self.to_data_frame(), file=file)


class ABCDocument(ABC):
    """
        Classe molde para gerir os documentos, para operações como:
    - leitura e escrita de arquivos pdf
    - exportar páginas ou arquivos pdf
    - permitir a leitura de arquivos ou bytes de pdf.
    """
    def __init__(self, mod_doc_pdf: ModDocPdf):
        self.mod_doc_pdf: ModDocPdf = mod_doc_pdf
        self.lib_pdf: LibPDF = DEFAULT_LIB_PDF
        self.metadata: dict[str, str | None] = get_void_metadata()

    @property
    def name(self) -> str | None:
        return self.metadata['name']

    @abstractmethod
    def lenght(self) -> int:
        pass

    @abstractmethod
    def get_first_page(self) -> PageDocumentPdf:
        pass

    @abstractmethod
    def get_last_page(self) -> PageDocumentPdf:
        pass

    @abstractmethod
    def get_page(self, idx: int) -> PageDocumentPdf | None:
        pass

    @abstractmethod
    def add_page(self, page: PageDocumentPdf):
        pass

    @abstractmethod
    def add_pages(self, pages: list[PageDocumentPdf]):
        pass

    @abstractmethod
    def to_file(self, file: File):
        pass

    @abstractmethod
    def to_bytes(self) -> BytesIO:
        pass

    @abstractmethod
    def to_pages(self) -> list[PageDocumentPdf]:
        pass

    @classmethod
    def create_from_file(cls, file: File) -> ABCDocument:
        pass

    @classmethod
    def create_from_bytes(cls, bt: BytesIO) -> ABCDocument:
        pass


class ImplementDocumentFitz(ABCDocument):
    """
        Implementação usando a biblioteca fitz.
    """
    def __init__(self, mod_doc_pdf: ModDocPdf):
        super().__init__(mod_doc_pdf)
        self.mod_doc_pdf: ModDocPdf = mod_doc_pdf
        self.lib_pdf: LibPDF = LibPDF.FITZ

    def lenght(self) -> int:
        return self.mod_doc_pdf.page_count

    def get_first_page(self) -> PageDocumentPdf:
        return self.get_page(0)

    def get_last_page(self) -> PageDocumentPdf:
        last_idx = self.mod_doc_pdf.page_count - 1
        return self.get_page(last_idx)

    def get_page(self, idx: int) -> PageDocumentPdf | None:
        _page_pdf = None
        if 0 <= idx < self.mod_doc_pdf.page_count:
            pg: fitz.Page = self.mod_doc_pdf.load_page(idx)  # retorna fitz.Page
            if pg is not None:
                _page_pdf = PageDocumentPdf.create_from_page_fitz(pg, pg.number + 1)
        return _page_pdf

    def add_page(self, page: PageDocumentPdf):
        # Assume que page.mod_page é fitz.Page
        self.mod_doc_pdf.insert_pdf(
            page.implement_page_pdf.mod_page.parent,
            from_page=page.implement_page_pdf.mod_page.number,
            to_page=page.implement_page_pdf.mod_page.number
        )

    def add_pages(self, pages: list[PageDocumentPdf]):
        for page in pages:
            self.add_page(page)

    def to_file(self, file: File):
        try:
            self.mod_doc_pdf.save(file.path)
        except Exception as e:
            show_warning(f'{e}')

    def to_bytes(self) -> BytesIO:
        buf = BytesIO()
        self.mod_doc_pdf.save(buf)
        buf.seek(0)
        return buf

    def to_pages(self) -> list[PageDocumentPdf]:
        pages = []
        for num, pg in enumerate(self.mod_doc_pdf):
            page_pdf = PageDocumentPdf.create_from_page_fitz(pg, num + 1)
            pages.append(page_pdf)
        return pages

    @classmethod
    def create_from_bytes(cls, bt: BytesIO) -> ImplementDocumentFitz:
        # Cria documento a partir de BytesIO
        doc: ModDocPdf = fitz.open(stream=bt.getvalue(), filetype="pdf")
        name = get_hash_from_bytes(bt)
        _obj_doc = cls(doc)
        _obj_doc.metadata['name'] = name
        _obj_doc.metadata['md5'] = name
        return _obj_doc

    @classmethod
    def create_from_file(cls, file: File) -> ImplementDocumentFitz:
        # Cria documento a partir de caminho no disco
        doc = fitz.open(file.path)
        _obj_doc = cls(doc)
        _obj_doc.metadata['file_path'] = file.absolute()
        _obj_doc.metadata['dir_path'] = file.dirname()
        _obj_doc.metadata['size'] = file.size()
        _obj_doc.metadata['name'] = file.absolute()
        _obj_doc.metadata['md5'] = file.md5()
        return _obj_doc

    @classmethod
    def create_from_pages(cls, pages: list[PageDocumentPdf]) -> ImplementDocumentFitz:
        # Criar documento PDF.
        pdf_document = fitz.Document()
        for page in pages:
            # Verifica se a página é do tipo fitz.Page
            if not isinstance(page.implement_page_pdf.mod_page, fitz.Page):
                raise TypeError(f"Todas as páginas devem ser do tipo [fitz.Page]")
            # Insere as páginas no novo documento
            pdf_document.insert_pdf(
                page.implement_page_pdf.mod_page.parent,
                from_page=page.implement_page_pdf.mod_page.number,
                to_page=page.implement_page_pdf.mod_page.number
            )
        bt = BytesIO(pdf_document.write())
        return cls.create_from_bytes(bt)


class ImplementDocumentPyPdf(ABCDocument):
    """
        Implementação usando a biblioteca pypdf
    """

    def __init__(self, mod_doc_pdf: PdfWriter):
        super().__init__(mod_doc_pdf)
        self.mod_doc_pdf: PdfWriter = mod_doc_pdf  # ou PdfReader
        self.lib_pdf: LibPDF = LibPDF.PYPDF

    def lenght(self) -> int:
        return len(self.mod_doc_pdf.pages)

    def get_first_page(self) -> PageDocumentPdf:
        """
        Retorna a primeira página do documento.
        """
        # O índice da primeira página em PyPDF2 é 0.
        return self.get_page(0)

    def get_last_page(self) -> PageDocumentPdf:
        """
        Retorna a última página do documento.
        """
        # O índice da última página é o número total de páginas menos um.
        last_page_idx = len(self.mod_doc_pdf.pages) - 1
        return self.get_page(last_page_idx)

    def get_page(self, idx: int) -> PageDocumentPdf | None:
        """
        Retorna uma página específica pelo seu índice.
        Se o índice for inválido, retorna None.
        """
        if 0 <= idx < len(self.mod_doc_pdf.pages):
            # Acessa a página pela lista self.mod_doc_pdf.pages
            pg = self.mod_doc_pdf.pages[idx]
            # O número da página é idx + 1
            return PageDocumentPdf.create_from_page_pypdf(pg, idx + 1)
        return None

    def add_page(self, page: PageDocumentPdf):
        self.mod_doc_pdf.add_page(page.implement_page_pdf.mod_page)

    def add_pages(self, pages: list[PageDocumentPdf]):
        for page in pages:
            self.add_page(page)

    def to_file(self, file: File):
        with open(file.path, 'wb') as f:
            self.mod_doc_pdf.write(f)

    def to_bytes(self) -> BytesIO:
        buf = BytesIO()
        self.mod_doc_pdf.write(buf)
        buf.seek(0)
        return buf

    def to_pages(self) -> list[PageDocumentPdf]:
        pages_pdf: list[PageDocumentPdf] = []
        for num, page in enumerate(self.mod_doc_pdf.pages):
            pg = PageDocumentPdf.create_from_page_pypdf(page, num + 1)
            pages_pdf.append(pg)
        return pages_pdf

    @classmethod
    def create_from_bytes(cls, bt: BytesIO) -> ImplementDocumentPyPdf:
        # Usa PdfReader diretamente de BytesIO
        bt.seek(0)
        reader = PdfReader(bt)
        bt.seek(0)
        name = get_hash_from_bytes(bt)
        pdf_writer = PdfWriter()
        for page in reader.pages:
            pdf_writer.add_page(page)
        bt.close()
        del bt
        del reader
        _obj_doc = cls(pdf_writer)
        _obj_doc.metadata['name'] = name
        _obj_doc.metadata['md5'] = name
        return _obj_doc

    @classmethod
    def create_from_file(cls, file: File) -> ImplementDocumentPyPdf:
        # Usa PdfReader diretamente de arquivo
        reader = PdfReader(file.absolute())
        pdf_writer = PdfWriter()
        for p in reader.pages:
            pdf_writer.add_page(p)
        del reader
        _obj_doc = cls(pdf_writer)
        _obj_doc.metadata['file_path'] = file.absolute()
        _obj_doc.metadata['dir_path'] = file.dirname()
        _obj_doc.metadata['size'] = file.size()
        _obj_doc.metadata['name'] = file.absolute()
        _obj_doc.metadata['md5'] = file.md5()
        _obj_doc.metadata['extension'] = file.extension()
        return _obj_doc

    @classmethod
    def create_from_pages(cls, pages: list[PageDocumentPdf]) -> ImplementDocumentPyPdf:
        pdf_writer = PdfWriter()
        for page_obj in pages:
            # Obtém o objeto de página da implementação da lib
            pdf_writer.add_page(page_obj.implement_page_pdf.mod_page)
        output_bytes = BytesIO()
        pdf_writer.write(output_bytes)
        pdf_bytes = output_bytes
        return cls.create_from_bytes(pdf_bytes)


class DocumentPdf(object):
    """
        Gerir um documento PDF com uma implementação de fitz ou pypdf.
    As operações são feitas pela classe encapsulada aqui.
    """
    def __init__(
                self,
                document: Union[
                    str, File, PdfWriter, fitz.Document, BytesIO,
                    ImplementDocumentFitz, ImplementDocumentPyPdf,
                ],
                *,
                lib_pdf: LibPDF = LibPDF.FITZ
            ):
        self.doc_pdf: ABCDocument = None
        self.lib_pdf: LibPDF = lib_pdf
        if isinstance(document, str):
            if lib_pdf == LibPDF.PYPDF:
                self.doc_pdf = ImplementDocumentPyPdf.create_from_file(File(document))
            elif lib_pdf == LibPDF.FITZ:
                self.doc_pdf = ImplementDocumentFitz.create_from_file(File(document))
        elif isinstance(document, File):
            if lib_pdf == LibPDF.PYPDF:
                self.doc_pdf = ImplementDocumentPyPdf.create_from_file(document)
            elif lib_pdf == LibPDF.FITZ:
                self.doc_pdf = ImplementDocumentFitz.create_from_file(document)
        elif isinstance(document, PdfWriter):
            _tmp_bytes = BytesIO()
            document.write(_tmp_bytes)
            _tmp_bytes.seek(0)
            if lib_pdf == LibPDF.PYPDF:
                name = get_hash_from_bytes(_tmp_bytes)
                self.doc_pdf = ImplementDocumentPyPdf(document)
                self.doc_pdf.metadata['name'] = name
                self.doc_pdf.metadata['md5'] = name
                del _tmp_bytes
            elif lib_pdf == LibPDF.FITZ:
                self.doc_pdf = ImplementDocumentFitz.create_from_bytes(_tmp_bytes)
        elif isinstance(document, fitz.Document):
            _tmp_bytes = BytesIO(document.tobytes())
            _tmp_bytes.seek(0)
            if lib_pdf == LibPDF.PYPDF:
                self.doc_pdf = ImplementDocumentPyPdf.create_from_bytes(_tmp_bytes)
            elif lib_pdf == LibPDF.FITZ:
                name = get_hash_from_bytes(_tmp_bytes)
                self.doc_pdf = ImplementDocumentFitz(document)
                self.doc_pdf.metadata['name'] = name
                self.doc_pdf.metadata['md5'] = name
                del _tmp_bytes
        elif isinstance(document, BytesIO):
            if lib_pdf == LibPDF.PYPDF:
                self.doc_pdf = ImplementDocumentPyPdf.create_from_bytes(document)
            elif lib_pdf == LibPDF.FITZ:
                self.doc_pdf = ImplementDocumentFitz.create_from_bytes(document)
        elif isinstance(document, ImplementDocumentFitz):
            self.doc_pdf = document
        elif isinstance(document, ImplementDocumentPyPdf):
            self.doc_pdf = document

        if self.doc_pdf is None:
            raise ValueError(
                f'Use: str, File, PdfWriter, fitz.Document ou BytesIO não => {type(document)}'
            )

    @property
    def name(self) -> str | None:
        return self.doc_pdf.name

    @property
    def metadata(self) -> dict[str, str | None]:
        return self.doc_pdf.metadata

    @property
    def lenght(self) -> int:
        return self.doc_pdf.lenght()

    def get_real_document(self) -> fitz.Document | PdfWriter:
        return self.doc_pdf.mod_doc_pdf

    def get_first_page(self) -> PageDocumentPdf:
        """
        Retorna a primeira página do documento.
        """
        return self.doc_pdf.get_first_page()

    def get_last_page(self) -> PageDocumentPdf:
        """
        Retorna a última página do documento.
        """
        return self.doc_pdf.get_last_page()

    def get_page(self, idx: int) -> PageDocumentPdf | None:
        """
        Retorna uma página específica pelo seu índice.
        Se o índice for inválido, retorna None.
        """
        return self.doc_pdf.get_page(idx)

    def add_page(self, page: PageDocumentPdf):
        self.doc_pdf.add_page(page)

    def add_pages(self, pages: list[PageDocumentPdf]):
        self.doc_pdf.add_pages(pages)

    def to_file(self, file: File):
        self.doc_pdf.to_file(file)

    def to_bytes(self) -> BytesIO:
        return self.doc_pdf.to_bytes()

    def to_pages(self) -> list[PageDocumentPdf]:
        return self.doc_pdf.to_pages()

    def to_list(self, separator: str = '\n') -> list[str]:
        _pages = self.to_pages()
        _values = []
        for page in _pages:
            try:
                _values.extend(page.to_string().split(separator))
            except Exception as e:
                show_warning(f'{e}')
        return _values

    def _create_map(self, page: PageDocumentPdf, *, separator: str = '\n') -> dict[str, ColumnBody]:
        """
        @rtype: pd.DataFrame
        """
        txt_page = page.to_string()
        if (txt_page is None) or (txt_page == '') or (txt_page == 'nas'):
            _values = ['nan']
        else:
            _values = txt_page.split(separator)

        if self.metadata['file_path'] is None:
            return create_map_from_values(
                _values, page_num=f'{page.number_page}', file_type='.pdf',
            )
        else:
            return create_map_from_values(
                _values,
                page_num=f'{page.number_page}',
                file_type='.pdf',
                file_path=self.metadata['file_path'],
                dir_path=self.metadata['dir_path'],
            )

    def to_dict(self, separator: str = '\n') -> dict[str, ColumnBody]:
        list_data: list[dict[str, ColumnBody]] = []
        pages: list[PageDocumentPdf] = self.to_pages()

        for page_pdf in pages:
            _mp: dict[str, ColumnBody] = self._create_map(page_pdf, separator=separator)
            list_data.append(_mp)
        if len(list_data) == 0:
            return create_void_map()
        return concat_maps(list_data)

    def to_data(self, separator: str = '\n') -> pd.DataFrame:
        return pd.DataFrame.from_dict(self.to_dict(separator=separator))

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
        pages_pdf = self.to_pages()
        for page_pdf in pages_pdf:
            text_str_in_page = page_pdf.to_string()
            if (text_str_in_page == 'nas') or (text_str_in_page is None):
                continue
            try:
                fd = FindText(text_str_in_page, separator=separator)
                idx = fd.find_index(text, iqual=iqual, case=case)
                if idx is None:
                    continue
                math_text = fd.get_index(idx)
            except Exception as e:
                print(f'{__class__.__name__} {e}')
            else:
                _searchable.add_line(
                    math_text,
                    num_page=str(page_pdf.number_page),
                    num_line=str(idx + 1),
                    file=self.name,
                )
                return _searchable
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
        _pages_pdf = self.to_pages()
        for page_pdf in _pages_pdf:
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
                                    file=self.name,
                                )
                        else:
                            if text in item:
                                _searchable.add_line(
                                    item,
                                    num_page=str(page_pdf.number_page),
                                    num_line=str(num + 1),
                                    file=self.name,
                                )
                    else:
                        if iqual:
                            if text.lower() == item.lower():
                                _searchable.add_line(
                                    item,
                                    num_page=str(page_pdf.number_page),
                                    num_line=str(num + 1),
                                    file=self.name,
                                )
                        else:
                            if text.lower() in item.lower():
                                _searchable.add_line(
                                    item,
                                    num_page=str(page_pdf.number_page),
                                    num_line=str(num + 1),
                                    file=self.name,
                                )
            except Exception as e:
                show_warning(f'{__class__.__name__} {e}')
        return _searchable

    @classmethod
    def create_from_bytes(cls, bt: BytesIO, *, lib_pdf: LibPDF = LibPDF.FITZ) -> DocumentPdf:
        return cls(bt, lib_pdf=lib_pdf)

    @classmethod
    def create_from_file(cls, file: File, *, lib_pdf: LibPDF = DEFAULT_LIB_PDF) -> DocumentPdf:
        return cls(file, lib_pdf=lib_pdf)

    @classmethod
    def create_from_pages(
                cls,
                pages: list[PageDocumentPdf], *,
                lib_pdf: LibPDF = DEFAULT_LIB_PDF
            ) -> DocumentPdf:
        if lib_pdf == LibPDF.FITZ:
            mod_pdf = ImplementDocumentFitz.create_from_pages(pages)
            return cls(mod_pdf, lib_pdf=lib_pdf)
        elif lib_pdf == LibPDF.PYPDF:
            mod_pdf = ImplementDocumentPyPdf.create_from_pages(pages)
            return cls(mod_pdf, lib_pdf=lib_pdf)
        else:
            raise NotImplementedError(f'Módulo PDF não implementado: {lib_pdf}')


class CollectionPagePdf(ListItems):
    """
        Gerir uma coleção de páginas PDF.
    """
    def __init__(self, pages: list[PageDocumentPdf]) -> None:
        super().__init__(pages)
        self.pbar: ProgressBarAdapter = ProgressBarAdapter()

    @property
    def name(self) -> str | None:
        if self.is_empty:
            return None
        return self[0].__hash__()

    def set_pbar(self, p: ProgressBarAdapter):
        self.pbar = p

    def set_land_scape(self):
        for page in self:
            page.set_land_scape()

    def set_rotation(self, rotation: int) -> None:
        for page in self:
            page.set_rotation(rotation)

    def add_page(self, page: PageDocumentPdf) -> None:
        page.number_page = self.length + 1
        self.pbar.update_text(f'Adicionando página PDF {page.number_page}')
        self.append(page)

    def add_pages(self, pages: list[PageDocumentPdf]) -> None:
        _counter = len(pages)
        for n, pg in enumerate(pages):
            _counter += 1
            pg.number_page = _counter
            self.append(pg)

    def add_file_pdf(self, file: File, *, lib_pdf: LibPDF = DEFAULT_LIB_PDF) -> None:
        self.pbar.update_text(f'Adicionando arquivo PDF {file.basename()}')
        doc_pdf = DocumentPdf(file, lib_pdf=lib_pdf)
        self.add_pages(doc_pdf.to_pages())

    def add_files_pdf(self, files: list[File], lib_pdf: LibPDF = DEFAULT_LIB_PDF) -> None:
        max_num: int = len(files)
        for num, f in enumerate(files):
            self.pbar.update(
                ((num + 1) / max_num) * 100,
                f'Adicionando arquivo: [{num+1} de {max_num}] {f.basename()}'
            )
            _doc_pdf = DocumentPdf(f, lib_pdf=lib_pdf)
            self.add_pages(_doc_pdf.to_pages())
            del _doc_pdf

    def add_document(self, doc: DocumentPdf) -> None:
        self.add_pages(doc.to_pages())

    def add_directory_pdf(self, d: Directory, *, max_files: int = 4000):
        input_files = InputFiles(d, maxFiles=max_files)
        self.add_files_pdf(input_files.get_files(file_type=LibraryDocs.PDF))

    def to_document(self, lib_pdf: LibPDF = DEFAULT_LIB_PDF) -> DocumentPdf:
        return DocumentPdf.create_from_pages(self, lib_pdf=lib_pdf)

    def to_file_pdf(self, file: File, *, replace: bool = False) -> None:
        if not replace:
            if file.exists():
                print(f'[PULANDO]: o arquivo já existe {file.absolute()}')
                return
        _doc = DocumentPdf.create_from_pages(self)
        _doc.to_file(file)
        del _doc

    def to_files_pdf(
                self,
                output_dir: Directory, *,
                replace: bool = False,
                prefix: str = None,
            ) -> None:
        max_num = self.length
        self.pbar.start()
        print()
        for n, page in enumerate(self):
            _doc_pdf = DocumentPdf.create_from_pages([page])
            if prefix is None:
                file_path = output_dir.join_file(f'{page.number_page}-{_doc_pdf.name}.pdf')
            else:
                file_path = output_dir.join_file(f'{prefix}-{page.number_page}.pdf')

            if (not replace) and (file_path.exists()):
                continue
            self.pbar.update(
                ((n+1) / max_num) * 100,
                f'Exportando: [{n+1} de {max_num}] {file_path.basename()}'
            )
            try:
                _doc_pdf.to_file(file_path)
            except Exception as e:
                self.pbar.update_text(f'{e}')
            del _doc_pdf
        print()
        self.pbar.stop()
