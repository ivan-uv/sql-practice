#!/usr/bin/env bash
# Downloads the Sakila SQLite database (DVD rental store)
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
DB="$DIR/sakila.db"

if [ -f "$DB" ]; then
  echo "✓ sakila.db already exists."
  exit 0
fi

echo "Downloading Sakila database..."
curl -fL \
  "https://github.com/bradleygrant/sakila-sqlite3/raw/main/sakila_master.db" \
  -o "$DB"

if python3 -c "import sqlite3; c=sqlite3.connect('$DB'); print('Tables:', [r[0] for r in c.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()]); c.close()"; then
  echo "✓ Database ready: $DB"
else
  echo "✗ File appears invalid — removing."
  rm -f "$DB"
  exit 1
fi
