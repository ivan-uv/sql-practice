#!/usr/bin/env python3
"""SQL Practice — interactive terminal SQL learning app.

Usage:
    python practice.py

Keybindings:
    F5          Run query
    F6          Check answer against solution
    F7          Show hint
    F8          Show / hide solution
    Ctrl+Q      Quit
"""
from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path
from typing import Optional

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
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
) -> tuple[list[str], list[tuple], Optional[str]]:
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


# ── CSS ───────────────────────────────────────────────────────────────────────

APP_CSS = """
Screen { background: $surface; }

/* ── Sidebar ─────────────────────────── */
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
#question-list { height: 1fr; border: none; }
.diff-header { color: $warning; text-style: bold; }

/* ── Main panel ──────────────────────── */
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
"""

DIFF_ICON = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}


# ── App ───────────────────────────────────────────────────────────────────────

class SQLPractice(App):
    """Interactive SQL practice in the terminal."""

    CSS = APP_CSS

    BINDINGS = [
        Binding("f5", "run_query", "Run", show=True),
        Binding("f6", "check_answer", "Check", show=True),
        Binding("f7", "show_hint", "Hint", show=True),
        Binding("f8", "show_solution", "Solution", show=True),
        Binding("ctrl+q", "quit", "Quit", show=True),
    ]

    # ── State (initialised in on_mount) ───────────────────────────────────────
    _ds_idx: int
    _cur_question: Optional[dict]
    _completion: dict

    # ── Layout ────────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="layout"):
            with Vertical(id="sidebar"):
                yield Label("Database", id="sidebar-heading")
                yield Select(
                    [(d["title"], i) for i, d in enumerate(DATASETS)],
                    value=0,
                    id="db-select",
                )
                yield ListView(id="question-list")
            with Vertical(id="main"):
                yield Static("Select a question from the sidebar.", id="q-header")
                yield Static("", id="q-desc")
                yield Label(
                    "SQL Editor", id="editor-label"
                )
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
        """Update just the icon for one question without rebuilding the list."""
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

    @on(Select.Changed, "#db-select")
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

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _get_sql(self) -> Optional[str]:
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
