#!/usr/bin/env python3
from __future__ import annotations
from convert_stream.mod_types.table_types import ArrayString


class FindText(object):
    """
        Filtrar palavras/strings em textos longos
    """
    def __init__(self, text_value: str, separator: str = ' '):
        """

        :param text_value: texto bruto a ser filtrado
        :param separator: separador de texto a ser usado durante o filtro
        :type  text_value: str
        :type  separator: str
        :return: None
        """
        self.array: ArrayString = ArrayString(text_value.split(separator))
        self.separator: str = separator

    @property
    def is_null(self) -> bool:
        return self.array.is_empty

    def contains(self, text: str, *, iqual: bool = False, case: bool = True) -> bool:
        return self.array.contains(text, iqual=iqual, case=case)

    def find_index(self, text: str, *, iqual: bool = False, case: bool = True) -> int | None:
        return self.array.find_index(text, iqual=iqual, case=case)

    def get_index(self, num: int) -> str | None:
        return self.array.get(num)

    def to_array(self) -> ArrayString:
        return ArrayString(self.array)

    def find(self, text: str, *, iqual: bool = False, case: bool = False) -> str | None:
        if text is None:
            raise ValueError(f'{__class__.__name__}: text is None')
        return self.array.find(text, iqual=iqual, case=case)

    def find_all(self, text: str, *, iqual: bool = False, case: bool = True) -> list[str]:
        if text is None:
            raise ValueError(f'{__class__.__name__}: text is None')
        return self.array.find_all(text, iqual=iqual, case=case)




