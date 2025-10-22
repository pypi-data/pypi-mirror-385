#!/usr/bin/env python3
#
from __future__ import annotations
from convert_stream.mod_types.enums import ColumnsTable
import os.path
import pandas as pd
from soup_files import File, ProgressBarAdapter, CreatePbar


def contains(text: str, values: list[str], *, case: bool = True, iqual: bool = False) -> bool:
    """
        Verificar se um texto existe em lista de strings.
    """
    if case:
        if iqual:
            for x in values:
                if text == x:
                    return True
        else:
            for x in values:
                if text in x:
                    return True
    else:
        if iqual:
            for x in values:
                if text.upper() == x.upper():
                    return True
        else:
            for x in values:
                if text.upper() in x.upper():
                    return True
    return False


class ListItems(list):

    def __init__(self, items: list):
        super().__init__(items)

    @property
    def length(self) -> int:
        return len(self)

    @property
    def is_empty(self) -> bool:
        return self.length == 0

    def get(self, idx: int):
        return self[idx]


class ListString(ListItems):

    def __init__(self, items: list[str]):
        super().__init__(items)

    def contains(self, item: str, *, case: bool = True, iqual: bool = False) -> bool:
        return contains(item, self, case=case, iqual=iqual)

    def get(self, idx: int) -> str:
        return self[idx]

    def add_item(self, i: str):
        if isinstance(i, str):
            self.append(i)

    def add_items(self, items: list[str]):
        for item in items:
            self.add_item(item)


class ArrayString(ListString):
    """
        Classe para filtrar e manipular lista de strings.
    """

    def __init__(self, items: list[str]):
        super().__init__(items)

    def get_next(self, text: str, *, iqual: bool = False, case: bool = False) -> str | None:
        """
        Ao encontrar o texto 'text' na lista retorna a próxima string se existir, se não retorna None.
        """
        _idx: int | None = self.get_back_index(text, iqual=iqual, case=case)
        if _idx is None:
            return None
        if _idx < 0:
            return None
        if _idx >= self.length - 1:
            return None
        return self[_idx+1]

    def get_next_all(self, text: str, iqual: bool = False, case: bool = False) -> ListString:
        _idx: int | None = self.get_back_index(text, iqual=iqual, case=case)
        if _idx is None:
            return ListString([])
        if _idx < 0:
            return ListString([])
        if _idx >= self.length - 1:
            return ListString([])
        return ListString(self[(_idx + 1):])

    def get_next_index(self, text: str, *, iqual: bool = False, case: bool = False) -> int | None:
        """
            Ao encontrar o texto 'text' na lista retorna o índice da string anterior
        se existir, se não retorna None.
        """
        _idx: int | None = self.get_back_index(text, iqual=iqual, case=case)
        if _idx is None:
            return None
        if _idx < 0:
            return None
        if _idx >= self.length - 1:
            return None
        return _idx + 1

    def get_back_index(self, text: str, *, iqual: bool = False, case: bool = False) -> int | None:
        """
            Ao encontrar o texto 'text' na lista retorna o índice da string anterior
        se existir, se não retorna None.
        """
        _final_idx: int | None = self.find_index(text, iqual=iqual, case=case)
        if _final_idx is None:
            return None
        if _final_idx <= 0:
            return None
        return _final_idx - 1

    def get_back(self, text: str, iqual: bool = False, case: bool = False) -> str | None:
        """
        Ao encontrar o texto 'text' na lista retorna a string anterior se existir, se não retorna None.
        """
        _idx = self.get_back_index(text, iqual=iqual, case=case)
        return None if _idx is None else self[_idx]

    def get_back_all(self, text: str, iqual: bool = False, case: bool = False) -> ListString:
        _idx = self.get_back_index(text, iqual=iqual, case=case)
        return ListString([]) if _idx is None else ListString(self[:_idx])

    def find_index(self, text: str, *, iqual: bool = False, case: bool = True) -> int | None:
        num_idx = None
        if iqual:
            for idx, i in enumerate(self):
                if case:
                    if i == text:
                        num_idx = idx
                        break
                else:
                    if text.lower() == i.lower():
                        num_idx = idx
                        break
        else:
            for idx, i in enumerate(self):
                if case:
                    if text in i:
                        num_idx = idx
                        break
                else:
                    if text.lower() in i.lower():
                        num_idx = idx
                        break
        return num_idx

    def get(self, idx: int) -> str:
        return self[idx]

    def find(self, text: str, *, iqual: bool = False, case: bool = False) -> str | None:
        if text is None:
            raise ValueError(f'{__class__.__name__}: text is None')

        element = None
        if iqual:
            for i in self:
                if case:
                    if text == i:
                        element = i
                        break
                else:
                    if text.lower() == i.lower():
                        element = i
                        break
        else:
            for i in self:
                if case:
                    if text in i:
                        element = i
                        break
                else:
                    if text.lower() in i.lower():
                        element = i
                        break
        return element

    def find_all(self, text: str, *, iqual: bool = False, case: bool = True) -> list[str]:
        items = []
        if iqual:
            for i in self:
                if case:
                    if i == text:
                        items.append(i)
                else:
                    if text.lower() == i.lower():
                        items.append(i)
        else:
            for i in self:
                if case:
                    if text in i:
                        items.append(i)
                else:
                    if text.lower() in i.lower():
                        items.append(i)
        return items

    def count(self, text: str, *, iqual: bool = False, case: bool = True) -> int:
        count: int = 0
        if iqual:
            for i in self:
                if case:
                    if i == text:
                        count += 1
                else:
                    if text.lower() == i.lower():
                        count += 1
        else:
            for i in self:
                if case:
                    if text in i:
                        count += 1
                else:
                    if text.lower() in i.lower():
                        count += 1
        return count


class HeadCell(str):

    def __init__(self, text: str):
        super().__init__()
        self.text: str = text


class HeadValues(ListString):

    def __init__(self, head_items: list[HeadCell]):
        super().__init__(head_items)

    def contains(self, item: HeadCell | str, *, case: bool = True, iqual: bool = False) -> bool:
        return contains(item, self, case=case, iqual=iqual)

    def get(self, idx: int) -> HeadCell:
        return self[idx]

    def add_item(self, i: HeadCell | str):
        if isinstance(i, str):
            self.append(HeadCell(i))
        else:
            self.append(i)


class ColumnBody(ListString):
    """
        Lista de strings nomeada para representar os dados da coluna de uma tabela.
    """

    def __init__(self, col_name: HeadCell | str, col_body: list[str]):
        super().__init__(col_body)
        if isinstance(col_name, str):
            col_name = HeadCell(col_name)
        self.col_name: HeadCell = col_name

    def __repr__(self):
        return f'{__class__.__name__} {self.col_name} {super().__repr__()}'


class TextTable(dict):

    def __init__(self, body_list: list[ColumnBody]):
        local_args = {}
        self.header: HeadValues = HeadValues([])
        if len(body_list) == 0:
            super().__init__(local_args)
        else:
            max_num: int = len(body_list[0])
            col: ColumnBody
            for col in body_list:
                if len(col) != max_num:
                    raise ValueError(f'Todas as colunas devem ter o mesmo tamanho: {max_num}')
                local_args[col.col_name.text] = col
                self.header.add_item(col.col_name)
            super().__init__(local_args)

    @property
    def length(self) -> int:
        if self.header.length == 0:
            return 0
        return len(self[self.header[0]])

    def add_column(self, col: ColumnBody):
        if col.length != self.length:
            raise ValueError(f'Todas as colunas devem ter o mesmo tamanho: {self.length}')
        self[col.col_name] = col


def create_void_map() -> dict[str, ColumnBody]:

    return {
            ColumnsTable.KEY.value: ColumnBody(ColumnsTable.KEY.value, ListString([])),
            ColumnsTable.NUM_PAGE.value: ColumnBody(ColumnsTable.NUM_PAGE.value, ListString([])),
            ColumnsTable.NUM_LINE.value: ColumnBody(ColumnsTable.NUM_LINE.value, ListString([])),
            ColumnsTable.TEXT.value: ColumnBody(ColumnsTable.TEXT.value, ListString([])),
            ColumnsTable.FILE_NAME.value: ColumnBody(ColumnsTable.FILE_NAME.value, ListString([])),
            ColumnsTable.FILETYPE.value: ColumnBody(ColumnsTable.FILETYPE.value, ListString([])),
            ColumnsTable.FILE_PATH.value: ColumnBody(ColumnsTable.FILE_PATH.value, ListString([])),
            ColumnsTable.DIR.value: ColumnBody(ColumnsTable.DIR.value, ListString([])),
        }


def create_void_table() -> pd.DataFrame:
    """
        Retorna um DataFrame() vazio, apenas com as colunas formatadas
    para tabela de arquivos.
    @rtype: pd.DataFrame
    """
    return pd.DataFrame.from_dict(create_void_map())


def create_map_from_values(
            values: list[str], *,
            page_num: str = 'nan',
            file_path: str = 'nan',
            dir_path: str = 'nan',
            file_type: str = 'nan',
        ) -> dict[str, ColumnBody]:
    """
    Criar um DataFrame() a partir do mapa de um texto list[str]
    :param values: texto list[str]
    :param page_num: numero da página PDF caso o texto seja de uma página PDF.
    :param file_path: path do arquivo.
    :param dir_path: diretório pai do arquivo.
    :param file_type: tipo do arquivo.
    :return: DataFrame
    @rtype: pd.DataFrame
    """
    max_num = len(values)
    if max_num < 1:
        return create_void_map()

    _map: dict[str, ColumnBody] = create_void_map()
    _map[ColumnsTable.KEY.value].extend([f'{x}' for x in range(0, max_num)])
    _map[ColumnsTable.NUM_PAGE.value].extend([page_num] * max_num)
    _map[ColumnsTable.NUM_LINE.value].extend([f'{x+1}' for x in range(0, max_num)])
    _map[ColumnsTable.TEXT.value].extend(values)
    _map[ColumnsTable.FILE_NAME.value].extend([os.path.basename(file_path)] * max_num)
    _map[ColumnsTable.FILETYPE.value].extend([file_type] * max_num)
    _map[ColumnsTable.FILE_PATH.value].extend([file_path] * max_num)
    _map[ColumnsTable.DIR.value].extend([dir_path] * max_num)
    return _map


def create_map_from_file_values(
            file: File, values: list[str], *,
            page_num: str = 'nan'
        ) -> dict[str, ColumnBody]:
    """
    Criar um DataFrame() a partir do mapa de um texto list[str]
    :param file: arquivo no disco do qual o texto (list[str]) foi extraído
    :param values: texto list[str]
    :param page_num: numero da página PDF caso o texto seja de uma página PDF.

    """
    max_num = len(values)
    if max_num < 1:
        return create_void_map()
    return create_map_from_values(
        values, page_num=page_num, file_path=file.absolute(), dir_path=file.dirname(), file_type=file.extension()
    )


def get_text_from_file(file: str) -> ListString:
    """
        Retorna o texto de um arquivo .txt em formato de lista
    """
    try:
        with open(file, 'rt') as f:
            lines = ListString(f.readlines())
    except Exception as e:
        print(e)
        return ListString([])
    else:
        return lines


def concat_maps(list_map: list[dict[str, ColumnBody]]) -> dict[str, ColumnBody]:
    if len(list_map) == 0:
        return {}
    columns: list[str] = list(list_map[0].keys())
    final_dict: dict[str, ColumnBody] = {}
    for col in columns:
        final_dict[col] = ColumnBody(col, [])
    for current_map in list_map:
        for c in columns:
            final_dict[c].extend(current_map[c])
    return final_dict





