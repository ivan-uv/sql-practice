# SQL Practice

Three real-world SQLite databases with 15 practice questions each (Easy / Medium / Hard),
plus an interactive terminal UI to run queries and check answers.

## Quick Start

```bash
# 1. Download the databases (each ~1–25 MB, uses curl)
bash chinook/setup.sh
bash northwind/setup.sh
bash sakila/setup.sh

# 2. Launch the practice app (uv installs dependencies automatically)
uv run practice.py
```

## Databases

| Folder | Theme | Tables | Questions |
|--------|-------|--------|-----------|
| `chinook/` | Digital music store — artists, albums, tracks, invoices | 11 | 15 |
| `northwind/` | Classic business ERP — customers, orders, products | 11 | 15 |
| `sakila/` | DVD rental store — films, actors, rentals, payments | 15 | 15 |

## App Keybindings

| Key | Action |
|-----|--------|
| **F5** | Run your query and display results |
| **F6** | Check your answer against the solution |
| **F7** | Show a hint |
| **F8** | Load the reference solution into the editor |
| **Ctrl+Q** | Quit |

## Using the App

1. Pick a database from the dropdown at the top of the sidebar.
2. Click a question in the list (Easy → Medium → Hard).
3. Read the description and write your SQL in the editor.
4. **F5** to run and see results; **F6** to check correctness.
5. Completed questions get a **✓** in the list.

## Checking Without the App

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

## Schema References

Each folder has a `schema.md` with a table/column reference and
relationship diagram — useful when writing your own queries.

## Topics Covered

- `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`
- `JOIN` (INNER, LEFT, self-join)
- `GROUP BY`, `HAVING`, aggregate functions
- String functions, date functions (`strftime`, `julianday`)
- Subqueries and CTEs (`WITH`)
- Window functions (`RANK()`, `SUM() OVER`)
- Set operations (finding gaps with `LEFT JOIN ... IS NULL`)
