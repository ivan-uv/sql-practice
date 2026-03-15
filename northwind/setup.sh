#!/usr/bin/env bash
# Downloads the Northwind SQLite database (business / orders)
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
DB="$DIR/northwind.db"

if [ -f "$DB" ]; then
  echo "✓ northwind.db already exists."
  exit 0
fi

echo "Downloading Northwind database..."
curl -fL \
  "https://raw.githubusercontent.com/jpwhite3/northwind-SQLite3/main/dist/northwind.db" \
  -o "$DB"

if python3 -c "import sqlite3; c=sqlite3.connect('$DB'); print('Tables:', [r[0] for r in c.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()]); c.close()"; then
  echo "✓ Database ready: $DB"
else
  echo "✗ File appears invalid — removing."
  rm -f "$DB"
  exit 1
fi
