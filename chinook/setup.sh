#!/usr/bin/env bash
# Downloads the Chinook SQLite database (music store)
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
DB="$DIR/chinook.sqlite"

if [ -f "$DB" ]; then
  echo "✓ chinook.sqlite already exists."
  exit 0
fi

echo "Downloading Chinook database..."
curl -fL \
  "https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite" \
  -o "$DB"

# Quick sanity check
if python3 -c "import sqlite3; c=sqlite3.connect('$DB'); print('Tables:', [r[0] for r in c.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()]); c.close()"; then
  echo "✓ Database ready: $DB"
else
  echo "✗ File appears invalid — removing."
  rm -f "$DB"
  exit 1
fi
