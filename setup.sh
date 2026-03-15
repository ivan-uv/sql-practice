#!/usr/bin/env bash
# Download all practice databases
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"

bash "$DIR/chinook/setup.sh"
bash "$DIR/northwind/setup.sh"
bash "$DIR/sakila/setup.sh"

echo ""
echo "All databases ready!  Run:  uv run practice.py"
