#!/usr/bin/env python3
"""SQL Practice — interactive terminal SQL learning app.

Usage:
    uv run practice.py

Keybindings:
    F2          Toggle between Practice and Schema Browser
    F5          Run query
    F6          Check answer against solution
    F7          Show hint
    F8          Load reference solution
    F9          Next question
    Ctrl+Q      Quit
"""
from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Label,
    ListItem,
    ListView,
    Select,
    Static,
    TextArea,
    Tree,
)

# ── Dataset registry ──────────────────────────────────────────────────────────

DATASETS: list[dict] = []


def load_datasets() -> None:
    """Scan for */questions.py and load each dataset module."""
    DATASETS.clear()
    root = Path(__file__).parent
    for qfile in sorted(root.glob("*/questions.py")):
        spec = importlib.util.spec_from_file_location(
            f"_{qfile.parent.name}_questions", qfile
        )
        mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        DATASETS.append(
            {
                "name": qfile.parent.name,
                "title": getattr(mod, "DB_TITLE", qfile.parent.name),
                "description": getattr(mod, "DB_DESCRIPTION", ""),
                "db_path": qfile.parent / mod.DB_NAME,
                "questions": mod.QUESTIONS,
                "setup_path": qfile.parent / "setup.sh",
            }
        )


# ── SQL helpers ───────────────────────────────────────────────────────────────

def _normalize(v: object) -> str:
    if v is None:
        return "NULL"
    if isinstance(v, float):
        return f"{v:.4f}"
    return str(v)


def _results_match(a: list, b: list) -> bool:
    """Order-independent comparison of two result sets."""
    norm = lambda rows: sorted(tuple(_normalize(c) for c in row) for row in rows)
    return norm(a) == norm(b)


def _run_sql(
    db_path: Path, sql: str
) -> tuple[list[str], list[tuple], str | None]:
    """Return (columns, rows, error_or_None)."""
    if not db_path.exists():
        return [], [], (
            f"Database not found: {db_path.name}\n"
            f"Run:  bash {db_path.parent.name}/setup.sh"
        )
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description] if cur.description else []
        conn.close()
        return cols, rows, None
    except Exception as exc:  # noqa: BLE001
        return [], [], str(exc)


# ── Schema introspection helpers ──────────────────────────────────────────────


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

/* ── Shared sidebar ─────────────────── */
#sidebar, #browse-sidebar {
    width: 36;
    background: $panel;
    border-right: solid $primary-background;
    padding: 0 1;
}
.sidebar-heading {
    text-style: bold;
    color: $accent;
    height: 2;
    padding: 1 0 0 0;
}
.db-select { margin-bottom: 1; }

/* ── Practice screen ────────────────── */
#question-list { height: 1fr; border: none; }
.diff-header { color: $warning; text-style: bold; }

#main { padding: 1 2; height: 1fr; overflow-y: auto; }

#q-header {
    text-style: bold;
    height: 2;
    color: $text;
    margin-bottom: 0;
}
#q-desc {
    color: $text-muted;
    height: 4;
    margin-bottom: 1;
}
#editor-label {
    color: $accent;
    text-style: bold;
    height: 1;
}
TextArea { height: 9; margin: 0 0 1 0; }

#btn-row { height: 3; margin-bottom: 1; }
Button { min-width: 16; margin-right: 1; }

#results-label { color: $accent; text-style: bold; height: 1; }
DataTable { height: 12; margin-bottom: 1; }

#status {
    height: 3;
    padding: 0 1;
    border: round $primary-background;
    color: $text-muted;
}

/* ── Browse screen ──────────────────── */
#table-tree { height: 1fr; }

#browse-main { padding: 1 2; height: 1fr; overflow-y: auto; }

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

DIFF_ICON = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}


# ── Practice Screen ──────────────────────────────────────────────────────────


class PracticeScreen(Screen):
    """Main practice screen with questions and SQL editor."""

    BINDINGS = [
        Binding("f5", "run_query", "Run", show=True),
        Binding("f6", "check_answer", "Check", show=True),
        Binding("f7", "show_hint", "Hint", show=True),
        Binding("f8", "show_solution", "Solution", show=True),
        Binding("f9", "next_question", "Next", show=True),
    ]

    _ds_idx: int
    _cur_question: dict | None
    _completion: dict

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="layout"):
            with Vertical(id="sidebar"):
                yield Label("Database", classes="sidebar-heading")
                yield Select(
                    [(d["title"], i) for i, d in enumerate(DATASETS)],
                    value=0,
                    id="practice-db-select",
                    classes="db-select",
                )
                yield ListView(id="question-list")
            with Vertical(id="main"):
                yield Static("Select a question from the sidebar.", id="q-header")
                yield Static("", id="q-desc")
                yield Label("SQL Editor", id="editor-label")
                yield TextArea(
                    "-- Write your SQL query here\n",
                    language="sql",
                    id="sql-editor",
                )
                with Horizontal(id="btn-row"):
                    yield Button("▶  Run  [F5]",      id="btn-run",  variant="success")
                    yield Button("✓  Check  [F6]",    id="btn-check", variant="primary")
                    yield Button("?  Hint  [F7]",     id="btn-hint",  variant="warning")
                    yield Button("📖 Solution  [F8]", id="btn-sol",   variant="default")
                    yield Button("→  Next  [F9]",     id="btn-next",  variant="default")
                yield Label("Results", id="results-label")
                yield DataTable(id="results-table", zebra_stripes=True)
                yield Static("Ready.", id="status")
        yield Footer()

    def on_mount(self) -> None:
        self._ds_idx = 0
        self._cur_question = None
        self._completion = {}
        self._switch_dataset(0)

    # ── Dataset / sidebar ─────────────────────────────────────────────────────

    def _switch_dataset(self, idx: int) -> None:
        self._ds_idx = idx
        self._cur_question = None
        self._rebuild_sidebar()

    def _rebuild_sidebar(self, keep_question: bool = False) -> None:
        ds = DATASETS[self._ds_idx]
        lv = self.query_one("#question-list", ListView)
        lv.clear()
        for diff in ("easy", "medium", "hard"):
            qs = [q for q in ds["questions"] if q["difficulty"] == diff]
            if not qs:
                continue
            lv.append(
                ListItem(
                    Label(f" ── {diff.capitalize()} ────────────────"),
                    classes="diff-header",
                )
            )
            for q in qs:
                key = f"{ds['name']}_{q['id']}"
                icon = "✓" if self._completion.get(key) else "○"
                lv.append(
                    ListItem(
                        Label(f"  {icon} {q['id']:02d}. {q['title']}"),
                        id=f"q_{q['id']}",
                    )
                )
        if not keep_question and ds["questions"]:
            self._load_question(ds["questions"][0])

    def _update_checkmark(self, question: dict) -> None:
        ds = DATASETS[self._ds_idx]
        key = f"{ds['name']}_{question['id']}"
        done = self._completion.get(key, False)
        icon = "✓" if done else "○"
        item_id = f"q_{question['id']}"
        try:
            item = self.query_one(f"#{item_id}", ListItem)
            item.query_one(Label).update(
                f"  {icon} {question['id']:02d}. {question['title']}"
            )
        except Exception:  # noqa: BLE001
            pass

    # ── Question loading ──────────────────────────────────────────────────────

    def _load_question(self, question: dict) -> None:
        self._cur_question = question
        diff = question["difficulty"]
        icon = DIFF_ICON.get(diff, "")
        self.query_one("#q-header", Static).update(
            f"{icon}  Q{question['id']}  [{diff.upper()}]  {question['title']}"
        )
        self.query_one("#q-desc", Static).update(question["description"])
        self.query_one("#sql-editor", TextArea).load_text(
            "-- Write your SQL query here\n"
        )
        self.query_one("#results-table", DataTable).clear(columns=True)
        ds = DATASETS[self._ds_idx]
        if not ds["db_path"].exists():
            self._set_status(
                f"⚠  Database not found.  Run:  bash {ds['name']}/setup.sh"
            )
        else:
            self._set_status(
                "Ready — write your SQL, then F5 to run or F6 to check."
            )

    # ── Events ────────────────────────────────────────────────────────────────

    @on(Select.Changed, "#practice-db-select")
    def _on_db_select(self, event: Select.Changed) -> None:
        if event.value is not Select.BLANK:
            idx = int(event.value)
            if idx != self._ds_idx:
                self._switch_dataset(idx)

    @on(ListView.Highlighted, "#question-list")
    def _on_q_highlight(self, event: ListView.Highlighted) -> None:
        item = event.item
        if item is None or not (item.id or "").startswith("q_"):
            return
        qid = int(item.id[2:])
        for q in DATASETS[self._ds_idx]["questions"]:
            if q["id"] == qid:
                self._load_question(q)
                return

    @on(Button.Pressed, "#btn-run")
    def _btn_run(self) -> None:
        self.action_run_query()

    @on(Button.Pressed, "#btn-check")
    def _btn_check(self) -> None:
        self.action_check_answer()

    @on(Button.Pressed, "#btn-hint")
    def _btn_hint(self) -> None:
        self.action_show_hint()

    @on(Button.Pressed, "#btn-sol")
    def _btn_sol(self) -> None:
        self.action_show_solution()

    @on(Button.Pressed, "#btn-next")
    def _btn_next(self) -> None:
        self.action_next_question()

    # ── Actions ───────────────────────────────────────────────────────────────

    def action_run_query(self) -> None:
        sql = self._get_sql()
        if sql is None:
            return
        cols, rows, err = _run_sql(DATASETS[self._ds_idx]["db_path"], sql)
        if err:
            self._set_status(f"✗  {err}")
        else:
            self._show_results(cols, rows)
            n = len(rows)
            self._set_status(f"Returned {n} row{'s' if n != 1 else ''}.")

    def action_check_answer(self) -> None:
        if not self._cur_question:
            self._set_status("⚠  Select a question first.")
            return
        sql = self._get_sql()
        if sql is None:
            return

        db = DATASETS[self._ds_idx]["db_path"]
        u_cols, u_rows, u_err = _run_sql(db, sql)
        if u_err:
            self._set_status(f"✗  {u_err}")
            return

        _, s_rows, s_err = _run_sql(db, self._cur_question["solution"])
        if s_err:
            self._set_status(f"⚠  Solution error (report a bug): {s_err}")
            return

        self.query_one("#results-table", DataTable).clear(columns=True)

        if _results_match(u_rows, s_rows):
            ds = DATASETS[self._ds_idx]
            key = f"{ds['name']}_{self._cur_question['id']}"
            self._completion[key] = True
            self._update_checkmark(self._cur_question)
            self._set_status(
                f"✓  Correct!  ({len(u_rows)} rows matched the expected output)"
            )
        elif len(u_rows) != len(s_rows):
            self._set_status(
                f"✗  Got {len(u_rows)} rows, expected {len(s_rows)}.  "
                "Check your filters or JOIN conditions."
            )
        else:
            self._set_status(
                "✗  Row count matches but values differ.  "
                "Check your column expressions."
            )

    def action_show_hint(self) -> None:
        if not self._cur_question:
            self._set_status("⚠  Select a question first.")
            return
        self._set_status(f"💡  Hint: {self._cur_question['hint']}")

    def action_show_solution(self) -> None:
        if not self._cur_question:
            self._set_status("⚠  Select a question first.")
            return
        self.query_one("#sql-editor", TextArea).load_text(
            self._cur_question["solution"]
        )
        self._set_status("Solution loaded in editor — study it, then try a variation!")

    def action_next_question(self) -> None:
        questions = DATASETS[self._ds_idx]["questions"]
        if not questions:
            return
        if self._cur_question is None:
            self._load_question(questions[0])
            return
        ids = [q["id"] for q in questions]
        cur_idx = ids.index(self._cur_question["id"]) if self._cur_question["id"] in ids else -1
        next_idx = (cur_idx + 1) % len(questions)
        next_q = questions[next_idx]
        self._load_question(next_q)
        lv = self.query_one("#question-list", ListView)
        for i, item in enumerate(lv._nodes):
            if getattr(item, "id", None) == f"q_{next_q['id']}":
                lv.index = i
                break

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _get_sql(self) -> str | None:
        raw = self.query_one("#sql-editor", TextArea).text.strip()
        if not raw or raw.startswith("--"):
            self._set_status("⚠  Write a SQL query first.")
            return None
        return raw

    def _show_results(self, cols: list[str], rows: list[tuple]) -> None:
        table = self.query_one("#results-table", DataTable)
        table.clear(columns=True)
        if cols:
            table.add_columns(*cols)
            for row in rows[:200]:
                table.add_row(*[("NULL" if v is None else str(v)) for v in row])

    def _set_status(self, msg: str) -> None:
        self.query_one("#status", Static).update(msg)


# ── Browse Screen ────────────────────────────────────────────────────────────


class BrowseScreen(Screen):
    """Interactive schema browser screen."""

    _db_idx: int
    _current_table: str | None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="browse-layout"):
            with Vertical(id="browse-sidebar"):
                yield Label("Database", classes="sidebar-heading")
                yield Select(
                    [(d["title"], i) for i, d in enumerate(DATASETS)],
                    value=0,
                    id="browse-db-select",
                    classes="db-select",
                )
                yield Tree("Tables", id="table-tree")
            with Vertical(id="browse-main"):
                yield Static("Select a table from the sidebar.", id="table-header")
                yield Static("", id="table-info")

                yield Label("Columns", classes="section-label")
                yield DataTable(id="columns-table", zebra_stripes=True)

                with Vertical(id="fk-section"):
                    yield Label("Foreign Keys", classes="section-label")
                    yield DataTable(id="fk-table", zebra_stripes=True)

                yield Label(
                    "Sample Data (first 10 rows)",
                    id="sample-label",
                    classes="section-label",
                )
                yield DataTable(id="sample-table", zebra_stripes=True)
        yield Footer()

    def on_mount(self) -> None:
        self._db_idx = 0
        self._current_table = None
        self._build_tree()

    def sync_database(self, idx: int) -> None:
        """Sync the database selector to match the practice screen."""
        if idx != self._db_idx:
            self._db_idx = idx
            self.query_one("#browse-db-select", Select).value = idx
            self._build_tree()

    # ── Tree / sidebar ────────────────────────────────────────────────────────

    def _build_tree(self) -> None:
        db_path = DATASETS[self._db_idx]["db_path"]
        tree = self.query_one("#table-tree", Tree)
        tree.clear()
        tree.show_root = False

        if not db_path.exists():
            ds = DATASETS[self._db_idx]
            tree.root.add_leaf(f"  Database not found — run setup.sh")
            self.query_one("#table-header", Static).update(
                f"⚠  Run:  bash {ds['name']}/setup.sh"
            )
            self.query_one("#table-info", Static).update("")
            return

        tables = _get_tables(db_path)
        for tbl in tables:
            cols = _get_columns(db_path, tbl)
            node = tree.root.add(f"  {tbl}", data=tbl)
            for col in cols:
                pk = " PK" if col["pk"] else ""
                nn = " NOT NULL" if col["notnull"] else ""
                node.add_leaf(f"  {col['name']}  [{col['type']}{pk}{nn}]")
        tree.root.expand_all()

        if tables:
            self._show_table(tables[0])

    @on(Select.Changed, "#browse-db-select")
    def _on_db_select(self, event: Select.Changed) -> None:
        if event.value is not Select.BLANK:
            idx = int(event.value)
            if idx != self._db_idx:
                self._db_idx = idx
                self._build_tree()

    @on(Tree.NodeHighlighted, "#table-tree")
    def _on_tree_highlight(self, event: Tree.NodeHighlighted) -> None:
        node = event.node
        while node.parent and node.data is None:
            node = node.parent
        if node.data and node.data != self._current_table:
            self._show_table(node.data)

    # ── Table detail ──────────────────────────────────────────────────────────

    def _show_table(self, table: str) -> None:
        self._current_table = table
        db = DATASETS[self._db_idx]
        db_path = db["db_path"]

        row_count = _get_row_count(db_path, table)
        self.query_one("#table-header", Static).update(f"  {table}")
        self.query_one("#table-info", Static).update(
            f"  {row_count:,} rows  |  {db['name']}/{db_path.name}"
        )

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

        sample_cols, sample_rows = _get_sample_rows(db_path, table)
        st = self.query_one("#sample-table", DataTable)
        st.clear(columns=True)
        if sample_cols:
            st.add_columns(*sample_cols)
            for row in sample_rows:
                st.add_row(*[("NULL" if v is None else str(v)) for v in row])


# ── App ───────────────────────────────────────────────────────────────────────


class SQLPractice(App):
    """Interactive SQL practice in the terminal."""

    CSS = APP_CSS
    TITLE = "SQL Practice"

    BINDINGS = [
        Binding("f2", "toggle_browse", "Browse", show=True),
        Binding("ctrl+q", "quit", "Quit", show=True),
    ]

    SCREENS = {
        "practice": PracticeScreen,
        "browse": BrowseScreen,
    }

    def on_mount(self) -> None:
        self.push_screen("practice")

    def action_toggle_browse(self) -> None:
        if isinstance(self.screen, BrowseScreen):
            self.pop_screen()
        else:
            # Sync database selection when switching to browse
            practice = self.screen
            self.push_screen("browse")
            if isinstance(practice, PracticeScreen):
                browse = self.screen
                if isinstance(browse, BrowseScreen):
                    browse.sync_database(practice._ds_idx)


# ── Entry point ───────────────────────────────────────────────────────────────


def main() -> None:
    load_datasets()
    if not DATASETS:
        print(
            "No datasets found!\n\n"
            "Download the databases first:\n"
            "  bash chinook/setup.sh\n"
            "  bash northwind/setup.sh\n"
            "  bash sakila/setup.sh\n\n"
            "Then run:  uv run practice.py"
        )
        raise SystemExit(1)
    SQLPractice().run()


if __name__ == "__main__":
    main()
