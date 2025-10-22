#!/usr/bin/env python3
#
from __future__ import annotations
from hashlib import md5 as md5_hash
from io import BytesIO
from .table_types import (
    TextTable, ColumnsTable, ListString, ArrayString, HeadCell, HeadValues,
    ColumnBody, create_void_map, create_map_from_values, create_void_table,
    create_map_from_file_values, concat_maps, contains, get_text_from_file
)


def get_hash_from_bytes(bt: BytesIO | bytes) -> str:
    if isinstance(bt, BytesIO):
        return md5_hash(bt.getvalue()).hexdigest().upper()
    elif isinstance(bt, bytes):
        return md5_hash(bt).hexdigest().upper()
    else:
        raise TypeError(f"Unsupported type {type(bt)}")


def get_void_metadata() -> dict[str, str | None]:
    """
        Salvar os metadados básico de documentos/imagens lidas em disco.
    """
    return {
        'file_path': None,
        'dir_path': None,
        'name': None,
        'md5': None,
        'size': None,
        'extension': None,
        'origin_src': None,
    }


__all__ = [
    'get_hash_from_bytes', 'get_void_metadata', 'get_void_metadata', 'contains',
    'concat_maps', 'create_map_from_file_values', 'create_map_from_values',
    'create_void_table', 'create_void_map', 'ColumnBody', 'ColumnsTable',
    'ListString', 'HeadCell', 'HeadValues', 'TextTable',
]