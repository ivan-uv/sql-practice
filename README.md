# SQL Practice

Interactive terminal app for learning SQL through hands-on practice.
Three real-world SQLite databases, 45 questions across Easy / Medium / Hard,
and a built-in TUI to run queries and check your answers.

## Prerequisites

- **Python 3.10+**
- [**uv**](https://docs.astral.sh/uv/) — installs dependencies automatically on first run
- **curl** — used by the setup scripts to download databases

## Quick Start

```bash
# 1. Download the databases (~1–25 MB each)
bash setup.sh

# 2. Launch the app
uv run practice.py
```

## Databases

| Folder | Theme | Tables | Questions |
|--------|-------|--------|-----------|
| `chinook/` | Digital music store — artists, albums, tracks, invoices | 11 | 15 |
| `northwind/` | Classic business ERP — customers, orders, products | 11 | 15 |
| `sakila/` | DVD rental store — films, actors, rentals, payments | 15 | 15 |

## Keybindings

| Key | Action |
|-----|--------|
| **F2** | Toggle the Schema Browser |
| **F5** | Run your query and display results |
| **F6** | Check your answer against the solution |
| **F7** | Show a hint |
| **F8** | Load the reference solution into the editor |
| **F9** | Jump to the next question |
| **Ctrl+Q** | Quit |

## Using the App

1. Pick a database from the dropdown at the top of the sidebar.
2. Click a question in the list (Easy → Medium → Hard).
3. Read the description and write your SQL in the editor.
4. **F5** to run and see results; **F6** to check correctness.
5. Completed questions get a **✓** in the list.

## Querying Without the App

You can also query the databases directly with the SQLite CLI:

```bash
sqlite3 chinook/chinook.sqlite
sqlite3 northwind/northwind.db
sqlite3 sakila/sakila.db
```

Or with DuckDB (reads SQLite files natively):

```bash
duckdb
D ATTACH 'chinook/chinook.sqlite' AS chinook;
D SELECT * FROM chinook.Artist LIMIT 5;
```

## Schema Browser

Press **F2** to toggle the built-in schema browser. It shows:

- **Table tree** — all tables with their columns and types in the sidebar
- **Column details** — types, primary keys, nullability, defaults
- **Foreign keys** — which columns reference other tables
- **Sample data** — first 10 rows of each table for quick reference

The browser syncs to whichever database you have selected, so you can
flip between the questions and the schema while working.

Each folder also has a static `schema.md` with a table/column reference and
relationship diagram.

## Topics Covered

- `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`
- `JOIN` (INNER, LEFT, self-join)
- `GROUP BY`, `HAVING`, aggregate functions
- String functions, date functions (`strftime`, `julianday`)
- Subqueries and CTEs (`WITH`)
- Window functions (`RANK()`, `SUM() OVER`)
- Set operations (finding gaps with `LEFT JOIN ... IS NULL`)

## Database Sources

| Database | Source | License |
|----------|--------|---------|
| Chinook | [lerocha/chinook-database](https://github.com/lerocha/chinook-database) | MIT |
| Northwind | [jpwhite3/northwind-SQLite3](https://github.com/jpwhite3/northwind-SQLite3) | MIT |
| Sakila | [bradleygrant/sakila-sqlite3](https://github.com/bradleygrant/sakila-sqlite3) | BSD |
