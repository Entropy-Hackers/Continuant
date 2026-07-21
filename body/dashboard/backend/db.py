# Copyright Entropy Hackers. Licensed under the Apache License, Version 2.0.
"""The dashboard's own small SQLite store — state that belongs to the
dashboard as an admin tool, not to the instance's observed activity
(that's `audit/events.jsonl`, owned by tools/audit-tap) and not to live
config (that's `openclaw.json`/`control/phase.json`).

Currently just one table: every phase change, with who and when — because
`control/phase.json` only holds the *current* status, and "wann wurde sie
für mündig erklärt, von wem" is exactly the kind of decision the Exposé
(A.9) says should leave a trace.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS phase_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    phase TEXT NOT NULL,
    notes TEXT NOT NULL,
    changed_by TEXT NOT NULL
);
"""


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA)


@contextmanager
def connect(db_path: Path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def record_phase_change(db_path: Path, ts: str, phase: str, notes: str, changed_by: str) -> None:
    with connect(db_path) as conn:
        conn.execute(
            "INSERT INTO phase_history (ts, phase, notes, changed_by) VALUES (?, ?, ?, ?)",
            (ts, phase, notes, changed_by),
        )


def recent_phase_history(db_path: Path, limit: int = 20) -> list[dict]:
    with connect(db_path) as conn:
        rows = conn.execute(
            "SELECT ts, phase, notes, changed_by FROM phase_history ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]
