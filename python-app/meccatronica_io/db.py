from __future__ import annotations

import sqlite3
from typing import Iterable

from meccatronica_io.schema import Signal


def connect(db_path: str) -> sqlite3.Connection:
    con = sqlite3.connect(db_path)
    con.execute("PRAGMA foreign_keys = ON;")
    _init_schema(con)
    return con


def _init_schema(con: sqlite3.Connection) -> None:
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS signals (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          tag TEXT NOT NULL,
          descrizione TEXT NOT NULL,
          tipo TEXT NOT NULL,
          indirizzo TEXT NOT NULL,
          dispositivo TEXT NOT NULL DEFAULT '',
          modulo TEXT NOT NULL DEFAULT '',
          morsetto TEXT NOT NULL DEFAULT '',
          unita TEXT NOT NULL DEFAULT '',
          note TEXT NOT NULL DEFAULT ''
        );
        """
    )
    con.execute("CREATE INDEX IF NOT EXISTS idx_signals_tag ON signals(tag);")
    con.commit()


def clear_signals(con: sqlite3.Connection) -> None:
    con.execute("DELETE FROM signals;")
    con.commit()


def insert_signals(con: sqlite3.Connection, signals: Iterable[Signal]) -> int:
    rows = [
        (
            s.tag,
            s.descrizione,
            s.tipo,
            s.indirizzo,
            s.dispositivo,
            s.modulo,
            s.morsetto,
            s.unita,
            s.note,
        )
        for s in signals
    ]
    con.executemany(
        """
        INSERT INTO signals(tag, descrizione, tipo, indirizzo, dispositivo, modulo, morsetto, unita, note)
        VALUES(?,?,?,?,?,?,?,?,?);
        """,
        rows,
    )
    con.commit()
    return len(rows)


def list_signals(con: sqlite3.Connection) -> list[Signal]:
    cur = con.execute(
        """
        SELECT tag, descrizione, tipo, indirizzo, dispositivo, modulo, morsetto, unita, note
        FROM signals
        ORDER BY tag;
        """
    )
    return [Signal(*row) for row in cur.fetchall()]


def count_signals(con: sqlite3.Connection) -> int:
    cur = con.execute("SELECT COUNT(1) FROM signals;")
    return int(cur.fetchone()[0])

