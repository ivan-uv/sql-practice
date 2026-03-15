#!/usr/bin/env python3
"""Schema Browser — interactive database explorer for SQL Practice.

Usage:
    uv run browse.py

Keybindings:
    Tab         Switch focus between sidebar and main panel
    Ctrl+Q      Quit
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Label,
    Select,
    Static,
    Tree,
)

# ── Database discovery ────────────────────────────────────────────────────────

ROOT = Path(__file__).parent

DB_FILES: list[dict] = []


def _discover_databases() -> None:
    """Find all SQLite databases referenced by questions.py modules."""
    DB_FILES.clear()
    for qfile in sorted(ROOT.glob("*/questions.py")):
        folder = qfile.parent
        # Look for .db or .sqlite files in the folder
        for ext in ("*.db", "*.sqlite"):
            for db in folder.glob(ext):
                DB_FILES.append({"name": folder.name, "path": db})


# ── Schema introspection ─────────────────────────────────────────────────────


def _get_tables(db_path: Path) -> list[str]:
    conn = sqlite3.connect(db_path)
    tables = [
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
    ]
    conn.close()
    return tables


def _get_columns(db_path: Path, table: str) -> list[dict]:
    conn = sqlite3.connect(db_path)
    rows = conn.execute(f'PRAGMA table_info("{table}")').fetchall()
    conn.close()
    # cid, name, type, notnull, dflt_value, pk
    return [
        {
            "name": r[1],
            "type": r[2] or "TEXT",
            "notnull": bool(r[3]),
            "default": r[4],
            "pk": bool(r[5]),
        }
        for r in rows
    ]


def _get_foreign_keys(db_path: Path, table: str) -> list[dict]:
    conn = sqlite3.connect(db_path)
    rows = conn.execute(f'PRAGMA foreign_key_list("{table}")').fetchall()
    conn.close()
    # id, seq, table, from, to, on_update, on_delete, match
    return [
        {"from": r[3], "to_table": r[2], "to_column": r[4]}
        for r in rows
    ]


def _get_sample_rows(
    db_path: Path, table: str, limit: int = 10
) -> tuple[list[str], list[tuple]]:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM "{table}" LIMIT {limit}')
    cols = [d[0] for d in cur.description] if cur.description else []
    rows = cur.fetchall()
    conn.close()
    return cols, rows


def _get_row_count(db_path: Path, table: str) -> int:
    conn = sqlite3.connect(db_path)
    count = conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
    conn.close()
    return count


# ── CSS ───────────────────────────────────────────────────────────────────────

APP_CSS = """
Screen { background: $surface; }

#sidebar {
    width: 36;
    background: $panel;
    border-right: solid $primary-background;
    padding: 0 1;
}
#sidebar-heading {
    text-style: bold;
    color: $accent;
    height: 2;
    padding: 1 0 0 0;
}
#db-select { margin-bottom: 1; }
#table-tree { height: 1fr; }

#main { padding: 1 2; height: 1fr; overflow-y: auto; }

#table-header {
    text-style: bold;
    height: 2;
    color: $text;
    margin-bottom: 0;
}
#table-info {
    color: $text-muted;
    height: 2;
    margin-bottom: 1;
}

.section-label {
    color: $accent;
    text-style: bold;
    height: 1;
    margin-top: 1;
}

#columns-table { height: auto; max-height: 16; margin-bottom: 1; }
#fk-section { height: auto; }
#fk-table { height: auto; max-height: 8; margin-bottom: 1; }

#sample-label { margin-top: 1; }
#sample-table { height: auto; max-height: 14; margin-bottom: 1; }
"""


# ── App ───────────────────────────────────────────────────────────────────────


class SchemaBrowser(App):
    """Interactive database schema browser."""

    CSS = APP_CSS
    TITLE = "Schema Browser"

    BINDINGS = [
        Binding("tab", "focus_next", "Focus next", show=False),
        Binding("ctrl+q", "quit", "Quit", show=True),
    ]

    _db_idx: int
    _current_table: str | None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="layout"):
            with Vertical(id="sidebar"):
                yield Label("Database", id="sidebar-heading")
                yield Select(
                    [(d["name"], i) for i, d in enumerate(DB_FILES)],
                    value=0,
                    id="db-select",
                )
                yield Tree("Tables", id="table-tree")
            with Vertical(id="main"):
                yield Static("Select a table from the sidebar.", id="table-header")
                yield Static("", id="table-info")

                yield Label("Columns", classes="section-label")
                yield DataTable(id="columns-table", zebra_stripes=True)

                with Vertical(id="fk-section"):
                    yield Label("Foreign Keys", classes="section-label")
                    yield DataTable(id="fk-table", zebra_stripes=True)

                yield Label("Sample Data (first 10 rows)", id="sample-label", classes="section-label")
                yield DataTable(id="sample-table", zebra_stripes=True)
        yield Footer()

    def on_mount(self) -> None:
        self._db_idx = 0
        self._current_table = None
        self._build_tree()

    # ── Tree / sidebar ────────────────────────────────────────────────────────

    def _build_tree(self) -> None:
        tree = self.query_one("#table-tree", Tree)
        tree.clear()
        tree.show_root = False
        db = DB_FILES[self._db_idx]
        tables = _get_tables(db["path"])
        for tbl in tables:
            cols = _get_columns(db["path"], tbl)
            node = tree.root.add(f"  {tbl}", data=tbl)
            for col in cols:
                pk = " PK" if col["pk"] else ""
                nn = " NOT NULL" if col["notnull"] else ""
                node.add_leaf(f"  {col['name']}  [{col['type']}{pk}{nn}]")
        tree.root.expand_all()

        # Auto-select first table
        if tables:
            self._show_table(tables[0])

    @on(Select.Changed, "#db-select")
    def _on_db_select(self, event: Select.Changed) -> None:
        if event.value is not Select.BLANK:
            idx = int(event.value)
            if idx != self._db_idx:
                self._db_idx = idx
                self._build_tree()

    @on(Tree.NodeHighlighted, "#table-tree")
    def _on_tree_highlight(self, event: Tree.NodeHighlighted) -> None:
        node = event.node
        # Walk up to find the table-level node (has data set)
        while node.parent and node.data is None:
            node = node.parent
        if node.data and node.data != self._current_table:
            self._show_table(node.data)

    # ── Table detail ──────────────────────────────────────────────────────────

    def _show_table(self, table: str) -> None:
        self._current_table = table
        db = DB_FILES[self._db_idx]
        db_path = db["path"]

        # Header
        row_count = _get_row_count(db_path, table)
        self.query_one("#table-header", Static).update(f"  {table}")
        self.query_one("#table-info", Static).update(
            f"  {row_count:,} rows  |  {db['name']}/{db_path.name}"
        )

        # Columns table
        cols = _get_columns(db_path, table)
        ct = self.query_one("#columns-table", DataTable)
        ct.clear(columns=True)
        ct.add_columns("Column", "Type", "PK", "Nullable", "Default")
        for c in cols:
            ct.add_row(
                c["name"],
                c["type"],
                "yes" if c["pk"] else "",
                "no" if c["notnull"] else "yes",
                str(c["default"]) if c["default"] is not None else "",
            )

        # Foreign keys table
        fks = _get_foreign_keys(db_path, table)
        ft = self.query_one("#fk-table", DataTable)
        ft.clear(columns=True)
        fk_section = self.query_one("#fk-section", Vertical)
        if fks:
            fk_section.display = True
            ft.add_columns("Column", "References", "Foreign Column")
            for fk in fks:
                ft.add_row(fk["from"], fk["to_table"], fk["to_column"])
        else:
            fk_section.display = False

        # Sample data
        sample_cols, sample_rows = _get_sample_rows(db_path, table)
        st = self.query_one("#sample-table", DataTable)
        st.clear(columns=True)
        if sample_cols:
            st.add_columns(*sample_cols)
            for row in sample_rows:
                st.add_row(*[("NULL" if v is None else str(v)) for v in row])


# ── Entry point ───────────────────────────────────────────────────────────────


def main() -> None:
    _discover_databases()
    if not DB_FILES:
        print(
            "No databases found!\n\n"
            "Download them first:\n"
            "  bash chinook/setup.sh\n"
            "  bash northwind/setup.sh\n"
            "  bash sakila/setup.sh\n\n"
            "Then run:  uv run browse.py"
        )
        raise SystemExit(1)
    SchemaBrowser().run()


if __name__ == "__main__":
    main()
