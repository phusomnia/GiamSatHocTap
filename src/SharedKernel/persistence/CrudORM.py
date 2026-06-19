from __future__ import annotations

import sqlite3
from dataclasses import fields, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Generic, List, Optional, Tuple, TypeVar, Union

T = TypeVar("T")


class CrudORM(Generic[T]):
    TABLE_NAME: str = ""
    PK: str = "id"

    _TYPE_MAP = {
        int: "INTEGER",
        float: "REAL",
        str: "TEXT",
        bool: "INTEGER",
        bytes: "BLOB",
    }

    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_table()

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _model_class(self):
        raise NotImplementedError

    def _fields(self):
        return fields(self._model_class())

    def _resolve_type(self, f):
        raw = f.type
        origin = getattr(raw, "__origin__", None)
        if origin is Union:
            for arg in raw.__args__:
                if arg is not type(None):
                    return arg
        return raw

    def _init_table(self) -> None:
        cols = []
        for f in self._fields():
            if f.name == self.PK:
                cols.append(f"{f.name} INTEGER PRIMARY KEY AUTOINCREMENT")
                continue
            py_type = self._resolve_type(f)
            sql_type = self._TYPE_MAP.get(py_type, "TEXT")
            cols.append(f"{f.name} {sql_type}")
        ddl = (
            f"CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} "
            f"({', '.join(cols)})"
        )
        with self._get_connection() as conn:
            conn.execute(ddl)

    def insert(self, obj) -> int:
        col_names, values = [], []
        for f in self._fields():
            val = getattr(obj, f.name)
            if f.name == self.PK and val is None:
                continue
            col_names.append(f.name)
            values.append(self._serialize(val))
        placeholders = ",".join("?" for _ in col_names)
        sql = (
            f"INSERT INTO {self.TABLE_NAME} "
            f"({','.join(col_names)}) VALUES ({placeholders})"
        )
        with self._get_connection() as conn:
            cur = conn.execute(sql, values)
            return cur.lastrowid

    def get(self, id_val: Any) -> Optional[T]:
        with self._get_connection() as conn:
            row = conn.execute(
                f"SELECT * FROM {self.TABLE_NAME} WHERE {self.PK}=?",
                (id_val,),
            ).fetchone()
            return self._row_to_model(row) if row else None

    def get_all(self, order_by: str = "") -> List[T]:
        sql = f"SELECT * FROM {self.TABLE_NAME}"
        if order_by:
            sql += f" ORDER BY {order_by}"
        with self._get_connection() as conn:
            return [self._row_to_model(r) for r in conn.execute(sql).fetchall()]

    def update(self, obj) -> None:
        sets, values = [], []
        pk_val = None
        for f in self._fields():
            val = getattr(obj, f.name)
            if f.name == self.PK:
                pk_val = val
                continue
            sets.append(f"{f.name}=?")
            values.append(self._serialize(val))
        values.append(pk_val)
        sql = (
            f"UPDATE {self.TABLE_NAME} "
            f"SET {','.join(sets)} WHERE {self.PK}=?"
        )
        with self._get_connection() as conn:
            conn.execute(sql, values)

    def delete(self, id_val: Any) -> None:
        with self._get_connection() as conn:
            conn.execute(
                f"DELETE FROM {self.TABLE_NAME} WHERE {self.PK}=?",
                (id_val,),
            )

    def _serialize(self, val: Any) -> Any:
        if isinstance(val, datetime):
            return val.isoformat()
        return val

    def _row_to_model(self, row: Tuple) -> T:
        model_cls = self._model_class()
        col_names = [f.name for f in self._fields()]
        kwargs = {}
        for i, col in enumerate(col_names):
            raw = row[i]
            f = self._fields()[i]
            kwargs[col] = self._deserialize(raw, f)
        return model_cls(**kwargs)

    def _deserialize(self, raw: Any, f) -> Any:
        if raw is None:
            return None
        py_type = self._resolve_type(f)
        if py_type is datetime:
            return datetime.fromisoformat(raw) if raw else None
        return raw
