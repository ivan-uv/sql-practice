"""
Chinook — Digital Music Store
Tables: Artist, Album, Track, Genre, MediaType,
        Playlist, PlaylistTrack, Customer, Invoice, InvoiceLine, Employee
"""

DB_NAME = "chinook.sqlite"
DB_TITLE = "Chinook: Music Store"
DB_DESCRIPTION = (
    "A digital media store with artists, albums, tracks, playlists,\n"
    "customers, invoices, and employees (sales reps)."
)

QUESTIONS = [
    # ── Easy ──────────────────────────────────────────────────────────────────
    {
        "id": 1,
        "title": "List All Artists",
        "difficulty": "easy",
        "description": (
            "Return the Name of every artist, sorted alphabetically.\n"
            "Table: Artist  |  Column: Name"
        ),
        "hint": "SELECT ... FROM Artist ORDER BY ...",
        "solution": "SELECT Name FROM Artist ORDER BY Name;",
    },
    {
        "id": 2,
        "title": "Track Count per Genre",
        "difficulty": "easy",
        "description": (
            "Show each genre's Name and how many tracks belong to it.\n"
            "Label the count 'track_count'. Order by count descending.\n"
            "Tables: Genre, Track  |  Join on GenreId"
        ),
        "hint": "JOIN Genre and Track, then GROUP BY genre, COUNT tracks.",
        "solution": (
            "SELECT g.Name, COUNT(t.TrackId) AS track_count\n"
            "FROM Genre g\n"
            "JOIN Track t ON g.GenreId = t.GenreId\n"
            "GROUP BY g.GenreId\n"
            "ORDER BY track_count DESC;"
        ),
    },
    {
        "id": 3,
        "title": "Tracks Longer Than 5 Minutes",
        "difficulty": "easy",
        "description": (
            "Find all tracks longer than 5 minutes (300 000 ms).\n"
            "Return Name and duration in minutes rounded to 2 decimals\n"
            "(label it 'duration_min'). Order by duration descending.\n"
            "Table: Track  |  Column: Milliseconds"
        ),
        "hint": "Divide Milliseconds by 60000.0, use ROUND(..., 2).",
        "solution": (
            "SELECT Name, ROUND(Milliseconds / 60000.0, 2) AS duration_min\n"
            "FROM Track\n"
            "WHERE Milliseconds > 300000\n"
            "ORDER BY Milliseconds DESC;"
        ),
    },
    {
        "id": 4,
        "title": "Customers from Brazil",
        "difficulty": "easy",
        "description": (
            "List all customers from Brazil.\n"
            "Return full_name (FirstName || ' ' || LastName) and Email.\n"
            "Order by LastName.\n"
            "Table: Customer  |  Column: Country"
        ),
        "hint": "WHERE Country = 'Brazil', concatenate first and last name.",
        "solution": (
            "SELECT FirstName || ' ' || LastName AS full_name, Email\n"
            "FROM Customer\n"
            "WHERE Country = 'Brazil'\n"
            "ORDER BY LastName;"
        ),
    },
    {
        "id": 5,
        "title": "Most Expensive Track",
        "difficulty": "easy",
        "description": (
            "Find the single most expensive track.\n"
            "Return its Name and UnitPrice.\n"
            "Table: Track  |  Column: UnitPrice"
        ),
        "hint": "ORDER BY UnitPrice DESC LIMIT 1",
        "solution": (
            "SELECT Name, UnitPrice\n"
            "FROM Track\n"
            "ORDER BY UnitPrice DESC\n"
            "LIMIT 1;"
        ),
    },
    # ── Medium ─────────────────────────────────────────────────────────────────
    {
        "id": 6,
        "title": "Top 5 Customers by Spend",
        "difficulty": "medium",
        "description": (
            "Find the top 5 customers ranked by total amount spent.\n"
            "Return customer (FirstName || ' ' || LastName) and\n"
            "total_spent (rounded to 2 decimals). Order by total descending.\n"
            "Tables: Customer, Invoice  |  Join on CustomerId"
        ),
        "hint": "JOIN Customer → Invoice, GROUP BY customer, SUM(Total), LIMIT 5.",
        "solution": (
            "SELECT c.FirstName || ' ' || c.LastName AS customer,\n"
            "       ROUND(SUM(i.Total), 2) AS total_spent\n"
            "FROM Customer c\n"
            "JOIN Invoice i ON c.CustomerId = i.CustomerId\n"
            "GROUP BY c.CustomerId\n"
            "ORDER BY total_spent DESC\n"
            "LIMIT 5;"
        ),
    },
    {
        "id": 7,
        "title": "Albums with More Than 20 Tracks",
        "difficulty": "medium",
        "description": (
            "Which albums contain more than 20 tracks?\n"
            "Return album Title, artist Name, and track_count.\n"
            "Order by track_count descending.\n"
            "Tables: Artist, Album, Track"
        ),
        "hint": "Three-way JOIN, GROUP BY album, HAVING COUNT > 20.",
        "solution": (
            "SELECT al.Title, ar.Name AS artist, COUNT(t.TrackId) AS track_count\n"
            "FROM Album al\n"
            "JOIN Artist ar ON al.ArtistId = ar.ArtistId\n"
            "JOIN Track t  ON al.AlbumId  = t.AlbumId\n"
            "GROUP BY al.AlbumId\n"
            "HAVING track_count > 20\n"
            "ORDER BY track_count DESC;"
        ),
    },
    {
        "id": 8,
        "title": "Employee Reporting Hierarchy",
        "difficulty": "medium",
        "description": (
            "List every employee and the name of their manager.\n"
            "Return employee and manager (both as FirstName || ' ' || LastName).\n"
            "Employees with no manager should show 'No Manager'.\n"
            "Table: Employee  |  Self-join on ReportsTo / EmployeeId"
        ),
        "hint": "Self-join Employee on ReportsTo = EmployeeId. Use LEFT JOIN + COALESCE.",
        "solution": (
            "SELECT e.FirstName || ' ' || e.LastName AS employee,\n"
            "       COALESCE(m.FirstName || ' ' || m.LastName, 'No Manager') AS manager\n"
            "FROM Employee e\n"
            "LEFT JOIN Employee m ON e.ReportsTo = m.EmployeeId\n"
            "ORDER BY manager, employee;"
        ),
    },
    {
        "id": 9,
        "title": "High-Revenue Countries",
        "difficulty": "medium",
        "description": (
            "Find countries with more than 5 invoices.\n"
            "Return BillingCountry, invoice_count, and total revenue\n"
            "(label: total, rounded to 2 dp). Order by total descending.\n"
            "Table: Invoice"
        ),
        "hint": "GROUP BY BillingCountry, HAVING COUNT(*) > 5.",
        "solution": (
            "SELECT BillingCountry,\n"
            "       COUNT(*)            AS invoice_count,\n"
            "       ROUND(SUM(Total), 2) AS total\n"
            "FROM Invoice\n"
            "GROUP BY BillingCountry\n"
            "HAVING invoice_count > 5\n"
            "ORDER BY total DESC;"
        ),
    },
    {
        "id": 10,
        "title": "Sales Rep Performance",
        "difficulty": "medium",
        "description": (
            "For each employee who has customers, show their name\n"
            "(employee), number of customers (num_customers), and\n"
            "total sales revenue (total_sales, rounded to 2 dp).\n"
            "Tables: Employee, Customer (SupportRepId), Invoice"
        ),
        "hint": "JOIN Employee → Customer (SupportRepId) → Invoice, GROUP BY employee.",
        "solution": (
            "SELECT e.FirstName || ' ' || e.LastName AS employee,\n"
            "       COUNT(DISTINCT c.CustomerId)      AS num_customers,\n"
            "       ROUND(SUM(i.Total), 2)            AS total_sales\n"
            "FROM Employee e\n"
            "JOIN Customer c ON e.EmployeeId = c.SupportRepId\n"
            "JOIN Invoice  i ON c.CustomerId = i.CustomerId\n"
            "GROUP BY e.EmployeeId\n"
            "ORDER BY total_sales DESC;"
        ),
    },
    # ── Hard ───────────────────────────────────────────────────────────────────
    {
        "id": 11,
        "title": "Top 5 Artists by Track Count",
        "difficulty": "hard",
        "description": (
            "Rank the top 5 artists by their total number of tracks\n"
            "across all albums. Return artist Name and total_tracks.\n"
            "Tables: Artist → Album → Track (two joins)"
        ),
        "hint": "JOIN Artist → Album → Track, GROUP BY artist, ORDER BY count DESC LIMIT 5.",
        "solution": (
            "SELECT ar.Name, COUNT(t.TrackId) AS total_tracks\n"
            "FROM Artist ar\n"
            "JOIN Album  al ON ar.ArtistId = al.ArtistId\n"
            "JOIN Track  t  ON al.AlbumId  = t.AlbumId\n"
            "GROUP BY ar.ArtistId\n"
            "ORDER BY total_tracks DESC\n"
            "LIMIT 5;"
        ),
    },
    {
        "id": 12,
        "title": "Multi-Playlist Tracks",
        "difficulty": "hard",
        "description": (
            "Find tracks that appear in more than one playlist.\n"
            "Return track Name and playlist_count. Order by count desc.\n"
            "Tables: Track, PlaylistTrack"
        ),
        "hint": "JOIN Track → PlaylistTrack, GROUP BY track, HAVING COUNT > 1.",
        "solution": (
            "SELECT t.Name, COUNT(pt.PlaylistId) AS playlist_count\n"
            "FROM Track t\n"
            "JOIN PlaylistTrack pt ON t.TrackId = pt.TrackId\n"
            "GROUP BY t.TrackId\n"
            "HAVING playlist_count > 1\n"
            "ORDER BY playlist_count DESC;"
        ),
    },
    {
        "id": 13,
        "title": "Top 10 Revenue Months",
        "difficulty": "hard",
        "description": (
            "Find the top 10 year-month combinations by total invoice revenue.\n"
            "Return year, month (both as strings, e.g. '2009', '01'),\n"
            "and total (rounded to 2 dp). Order by total descending.\n"
            "Table: Invoice  |  Use strftime('%Y', ...) and strftime('%m', ...)"
        ),
        "hint": "Use strftime to extract year and month, GROUP BY both, ORDER BY total DESC.",
        "solution": (
            "SELECT strftime('%Y', InvoiceDate) AS year,\n"
            "       strftime('%m', InvoiceDate) AS month,\n"
            "       ROUND(SUM(Total), 2)         AS total\n"
            "FROM Invoice\n"
            "GROUP BY year, month\n"
            "ORDER BY total DESC\n"
            "LIMIT 10;"
        ),
    },
    {
        "id": 14,
        "title": "Customers Above Average Spend (CTE)",
        "difficulty": "hard",
        "description": (
            "Using a CTE, find customers who have spent more than\n"
            "the average customer total. Return name and total_spent\n"
            "(rounded to 2 dp), ordered by total_spent descending.\n"
            "Tables: Customer, Invoice"
        ),
        "hint": "CTE 1: customer totals. CTE 2 (or subquery): AVG of those totals. Filter.",
        "solution": (
            "WITH customer_totals AS (\n"
            "    SELECT c.CustomerId,\n"
            "           c.FirstName || ' ' || c.LastName AS name,\n"
            "           SUM(i.Total) AS total\n"
            "    FROM Customer c\n"
            "    JOIN Invoice i ON c.CustomerId = i.CustomerId\n"
            "    GROUP BY c.CustomerId\n"
            ")\n"
            "SELECT name, ROUND(total, 2) AS total_spent\n"
            "FROM customer_totals\n"
            "WHERE total > (SELECT AVG(total) FROM customer_totals)\n"
            "ORDER BY total_spent DESC;"
        ),
    },
    {
        "id": 15,
        "title": "Tracks in Every Genre? (Subquery)",
        "difficulty": "hard",
        "description": (
            "Find artists whose tracks span the most distinct genres.\n"
            "Return artist Name and genre_count. Show top 10.\n"
            "Tables: Artist → Album → Track → Genre"
        ),
        "hint": "Four-table join, GROUP BY artist, COUNT(DISTINCT GenreId), LIMIT 10.",
        "solution": (
            "SELECT ar.Name, COUNT(DISTINCT t.GenreId) AS genre_count\n"
            "FROM Artist ar\n"
            "JOIN Album al ON ar.ArtistId = al.ArtistId\n"
            "JOIN Track t  ON al.AlbumId  = t.AlbumId\n"
            "GROUP BY ar.ArtistId\n"
            "ORDER BY genre_count DESC\n"
            "LIMIT 10;"
        ),
    },
]
