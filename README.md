# SQL Practice

Free, offline SQL practice with real datasets and an interactive terminal app.
Write queries, check your answers instantly, and browse table schemas — no account, no browser, no cloud required.

![SQL Practice demo](demo.gif)

---

## Why This Exists

Most SQL practice platforms are either paywalled, require an internet connection, or feel nothing like real work. This is a local tool built around three real-world databases used in SQL courses and tutorials worldwide. You write actual SQL against actual data and get instant feedback.

45 questions total, sorted Easy → Medium → Hard across three datasets.

---

## What You'll Practice

Beginner through interview-level SQL:

- Filtering, sorting, and aggregating data (`WHERE`, `ORDER BY`, `GROUP BY`)
- Joining multiple tables — including self-joins and left joins
- Filtering on aggregates with `HAVING`
- Writing reusable logic with CTEs (`WITH` clauses)
- Window functions like `RANK()` and running totals
- Finding missing or unmatched rows
- Date and string manipulation in SQLite

---

## The Three Databases

| Database | What It Models | Tables | Questions |
|----------|---------------|--------|-----------|
| **Chinook** | A digital music store — artists, albums, tracks, customers, and invoice history | 11 | 15 |
| **Northwind** | A classic business ERP — customers, orders, products, employees, and suppliers | 11 | 15 |
| **Sakila** | A DVD rental store — films, actors, inventory, rentals, and payments | 15 | 15 |

---

## Getting Started

**You'll need:** Python 3.10+, [uv](https://docs.astral.sh/uv/getting-started/installation/), and `curl`.

> **Don't have `uv`?** It's a fast Python package manager. Install it with:
> ```bash
> curl -LsSf https://astral.sh/uv/install.sh | sh
> ```

```bash
# 1. Clone the repo
git clone https://github.com/ivan-uv/sql-practice.git
cd sql-practice

# 2. Download the databases (~30 MB total, one-time)
bash setup.sh

# 3. Launch
uv run practice.py
```

`uv` installs the one dependency (the TUI framework) automatically on first run. No virtual environment setup needed.

---

## The App

```
┌─ SQL Practice ────────────────────────────────────────────────────────────┐
│ Database  ▼ Chinook: Music Store                     F2 Browse  ^Q Quit  │
├───────────────────────┬───────────────────────────────────────────────────┤
│ ── Easy ────────────  │ 🟡  Q6  [MEDIUM]  Top 5 Customers by Spend       │
│  ✓ 01. List Artists   │                                                   │
│  ✓ 02. Genre Counts   │ Find the top 5 customers ranked by total amount   │
│  ✓ 03. Long Tracks    │ spent. Return customer and total_spent (rounded   │
│  ...                  │ to 2 decimal places). Order by total descending.  │
│ ── Medium ──────────  │                                                   │
│  ● 06. Top 5 Spend ◄  │ SQL Editor                                        │
│  ○ 07. Albums >20     │ ┌─────────────────────────────────────────────┐   │
│  ...                  │ │ SELECT c.FirstName || ' ' || c.LastName     │   │
│ ── Hard ────────────  │ │   AS customer, ROUND(SUM(i.Total), 2) ...   │   │
│  ○ 11. Artist Rank    │ └─────────────────────────────────────────────┘   │
│  ...                  │ [▶ Run F5] [✓ Check F6] [? Hint F7]               │
│                       │ [📖 Solution F8]  [→ Next F9]                     │
│                       │                                                   │
│                       │ ✓  Correct!  (5 rows matched the expected output) │
└───────────────────────┴───────────────────────────────────────────────────┘
│ F2 Browse  F5 Run  F6 Check  F7 Hint  F8 Solution  F9 Next  ^Q Quit      │
└───────────────────────────────────────────────────────────────────────────┘
```

### How to use it

1. Pick a database from the **dropdown** at the top of the sidebar.
2. Select a question from the list — they're grouped **Easy → Medium → Hard**.
3. Read the description and write your SQL in the editor.
4. **F5** runs your query and shows the results.
5. **F6** checks your answer — it compares your output to the expected result and marks the question **✓** if you got it right.
6. Stuck? **F7** shows a hint. **F8** loads the reference solution.
7. **F9** (or the Next button) moves to the next question.

---

## Schema Browser

Not sure what columns a table has? Press **F2** to open the built-in schema browser without leaving the app.

It shows every table's columns, data types, primary keys, foreign key relationships, and the first 10 rows of real data — everything you need to figure out a join without Googling.

Press **F2** again to return to the practice screen.

---

## Keybindings

| Key | Action |
|-----|--------|
| **F2** | Toggle the Schema Browser |
| **F5** | Run query |
| **F6** | Check your answer |
| **F7** | Show a hint |
| **F8** | Load the reference solution |
| **F9** | Next question |
| **Ctrl+Q** | Quit |

---

## Troubleshooting

**"Database not found" when launching**
Run the setup script to download the databases:
```bash
bash setup.sh
```

**`uv: command not found`**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Then open a new terminal tab and try again.

**Python version error**
Check your version with `python3 --version`. You need 3.10 or newer.

---

## Querying Without the App

The databases are plain SQLite files — open them with any SQL client you like:

```bash
# SQLite CLI (built into macOS and most Linux systems)
sqlite3 chinook/chinook.sqlite

# DuckDB (reads SQLite files natively — great for analytics)
duckdb
D ATTACH 'chinook/chinook.sqlite' AS chinook;
D SELECT * FROM chinook.Artist LIMIT 5;
```

---

## Database Sources

| Database | Source | License |
|----------|--------|---------|
| Chinook | [lerocha/chinook-database](https://github.com/lerocha/chinook-database) | MIT |
| Northwind | [jpwhite3/northwind-SQLite3](https://github.com/jpwhite3/northwind-SQLite3) | MIT |
| Sakila | [bradleygrant/sakila-sqlite3](https://github.com/bradleygrant/sakila-sqlite3) | BSD |

---

Built with [Textual](https://textual.textualize.io/) · MIT License
