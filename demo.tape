Output demo.gif

Set FontSize 13
Set Width 1200
Set Height 750
Set Theme "Catppuccin Mocha"
Set Padding 10
Set Framerate 24
Set TypingSpeed 60ms

# ── Launch ────────────────────────────────────────────────────────────────────
Type "uv run practice.py"
Enter
Sleep 2.5s

# ── Show the database dropdown (Select widget has initial focus) ───────────────
Enter
Sleep 1.5s
Escape
Sleep 0.5s

# ── Focus the SQL editor (Tab: Select → ListView → TextArea) ──────────────────
Tab
Sleep 0.2s
Tab
Sleep 0.4s

# ── Move past the placeholder comment and type the answer ─────────────────────
Ctrl+E
Enter
Sleep 0.2s
Type "SELECT name"
Enter
Sleep 0.2s
Type "FROM artist"
Enter
Sleep 0.2s
Type "ORDER BY name"
Enter
Type ";"
Sleep 1.5s

# ── Run the query and show results (F5 = Escape + [15~) ───────────────────────
Escape
Type "[15~"
Sleep 3s

# ── Open the schema browser (F2 = Escape + OQ) ────────────────────────────────
Escape
Type "OQ"
Sleep 3s

# ── Back to practice ──────────────────────────────────────────────────────────
Escape
Type "OQ"
Sleep 1.5s

# ── Quit ─────────────────────────────────────────────────────────────────────
Ctrl+C
