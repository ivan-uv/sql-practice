"""
Sakila — DVD Rental Store
Tables: film, actor, film_actor, category, film_category, language,
        inventory, rental, payment, customer, staff, store,
        address, city, country
"""

DB_NAME = "sakila.db"
DB_TITLE = "Sakila: DVD Rental"
DB_DESCRIPTION = (
    "A DVD rental store with films, actors, customers, inventory,\n"
    "rentals, payments, staff, and stores. Rich many-to-many relationships."
)

QUESTIONS = [
    # ── Easy ──────────────────────────────────────────────────────────────────
    {
        "id": 1,
        "title": "Film Count per Category",
        "difficulty": "easy",
        "description": (
            "Count how many films belong to each category.\n"
            "Return category name and film_count.\n"
            "Order by film_count descending.\n"
            "Tables: category, film_category  |  Join on category_id"
        ),
        "hint": "JOIN category → film_category, COUNT, GROUP BY category.",
        "solution": (
            "SELECT c.name, COUNT(fc.film_id) AS film_count\n"
            "FROM category c\n"
            "JOIN film_category fc ON c.category_id = fc.category_id\n"
            "GROUP BY c.category_id\n"
            "ORDER BY film_count DESC;"
        ),
    },
    {
        "id": 2,
        "title": "Rated R Films with High Rental Rate",
        "difficulty": "easy",
        "description": (
            "Find all R-rated films with a rental rate above $3.00.\n"
            "Return title, rating, and rental_rate.\n"
            "Order by rental_rate descending, then title.\n"
            "Table: film"
        ),
        "hint": "WHERE rating = 'R' AND rental_rate > 3.00",
        "solution": (
            "SELECT title, rating, rental_rate\n"
            "FROM film\n"
            "WHERE rating = 'R' AND rental_rate > 3.00\n"
            "ORDER BY rental_rate DESC, title;"
        ),
    },
    {
        "id": 3,
        "title": "Top 10 Actors by Film Count",
        "difficulty": "easy",
        "description": (
            "Find the 10 actors who have appeared in the most films.\n"
            "Return actor (first_name || ' ' || last_name) and film_count.\n"
            "Order by film_count descending.\n"
            "Tables: actor, film_actor"
        ),
        "hint": "JOIN actor → film_actor, COUNT(film_id), GROUP BY actor, LIMIT 10.",
        "solution": (
            "SELECT a.first_name || ' ' || a.last_name AS actor,\n"
            "       COUNT(fa.film_id) AS film_count\n"
            "FROM actor a\n"
            "JOIN film_actor fa ON a.actor_id = fa.actor_id\n"
            "GROUP BY a.actor_id\n"
            "ORDER BY film_count DESC\n"
            "LIMIT 10;"
        ),
    },
    {
        "id": 4,
        "title": "Average Film Length by Rating",
        "difficulty": "easy",
        "description": (
            "What is the average film length (in minutes) for each rating?\n"
            "Return rating and avg_length (rounded to 1 decimal).\n"
            "Order by avg_length descending.\n"
            "Table: film  |  Column: length"
        ),
        "hint": "GROUP BY rating, ROUND(AVG(length), 1).",
        "solution": (
            "SELECT rating, ROUND(AVG(length), 1) AS avg_length\n"
            "FROM film\n"
            "GROUP BY rating\n"
            "ORDER BY avg_length DESC;"
        ),
    },
    {
        "id": 5,
        "title": "Films Never Added to Inventory",
        "difficulty": "easy",
        "description": (
            "Find films that have no inventory records at all.\n"
            "Return title and rental_rate, ordered by title.\n"
            "Tables: film, inventory  |  Use LEFT JOIN + IS NULL"
        ),
        "hint": "LEFT JOIN film → inventory, WHERE inventory_id IS NULL.",
        "solution": (
            "SELECT f.title, f.rental_rate\n"
            "FROM film f\n"
            "LEFT JOIN inventory i ON f.film_id = i.film_id\n"
            "WHERE i.inventory_id IS NULL\n"
            "ORDER BY f.title;"
        ),
    },
    # ── Medium ─────────────────────────────────────────────────────────────────
    {
        "id": 6,
        "title": "Top 10 Most Rented Films",
        "difficulty": "medium",
        "description": (
            "Find the 10 most rented films.\n"
            "Return title, category name, and rental_count.\n"
            "Order by rental_count descending.\n"
            "Tables: film, film_category, category, inventory, rental"
        ),
        "hint": "Five-table join: film → film_category → category, film → inventory → rental.",
        "solution": (
            "SELECT f.title, c.name AS category, COUNT(r.rental_id) AS rental_count\n"
            "FROM film f\n"
            "JOIN film_category fc ON f.film_id      = fc.film_id\n"
            "JOIN category      c  ON fc.category_id = c.category_id\n"
            "JOIN inventory     i  ON f.film_id      = i.film_id\n"
            "JOIN rental        r  ON i.inventory_id = r.inventory_id\n"
            "GROUP BY f.film_id\n"
            "ORDER BY rental_count DESC\n"
            "LIMIT 10;"
        ),
    },
    {
        "id": 7,
        "title": "Actors Spanning 5+ Categories",
        "difficulty": "medium",
        "description": (
            "Find actors whose films span 5 or more distinct categories.\n"
            "Return actor name and category_count.\n"
            "Order by category_count descending.\n"
            "Tables: actor, film_actor, film_category"
        ),
        "hint": "JOIN actor → film_actor → film_category, COUNT(DISTINCT category_id), HAVING >= 5.",
        "solution": (
            "SELECT a.first_name || ' ' || a.last_name AS actor,\n"
            "       COUNT(DISTINCT fc.category_id)      AS category_count\n"
            "FROM actor a\n"
            "JOIN film_actor    fa ON a.actor_id  = fa.actor_id\n"
            "JOIN film_category fc ON fa.film_id  = fc.film_id\n"
            "GROUP BY a.actor_id\n"
            "HAVING category_count >= 5\n"
            "ORDER BY category_count DESC;"
        ),
    },
    {
        "id": 8,
        "title": "Revenue by Store",
        "difficulty": "medium",
        "description": (
            "Calculate total payment revenue per store.\n"
            "Return store_id, city, and total_revenue (rounded to 2 dp).\n"
            "Order by total_revenue descending.\n"
            "Tables: store, staff, payment, address, city"
        ),
        "hint": "store → staff (store_id) → payment, also join address → city for city name.",
        "solution": (
            "SELECT s.store_id, ci.city,\n"
            "       ROUND(SUM(p.amount), 2) AS total_revenue\n"
            "FROM store    s\n"
            "JOIN staff    st ON s.store_id   = st.store_id\n"
            "JOIN payment  p  ON st.staff_id  = p.staff_id\n"
            "JOIN address  a  ON s.address_id = a.address_id\n"
            "JOIN city     ci ON a.city_id    = ci.city_id\n"
            "GROUP BY s.store_id\n"
            "ORDER BY total_revenue DESC;"
        ),
    },
    {
        "id": 9,
        "title": "Customers Above Average Spend (CTE)",
        "difficulty": "medium",
        "description": (
            "Using a CTE, find customers who paid more than the average\n"
            "customer total. Return customer name and total_paid\n"
            "(rounded to 2 dp), ordered by total_paid descending.\n"
            "Tables: customer, payment"
        ),
        "hint": "CTE: total per customer. Filter WHERE total > (SELECT AVG(total) FROM cte).",
        "solution": (
            "WITH customer_totals AS (\n"
            "    SELECT c.customer_id,\n"
            "           c.first_name || ' ' || c.last_name AS name,\n"
            "           SUM(p.amount) AS total\n"
            "    FROM customer c\n"
            "    JOIN payment p ON c.customer_id = p.customer_id\n"
            "    GROUP BY c.customer_id\n"
            ")\n"
            "SELECT name, ROUND(total, 2) AS total_paid\n"
            "FROM customer_totals\n"
            "WHERE total > (SELECT AVG(total) FROM customer_totals)\n"
            "ORDER BY total_paid DESC;"
        ),
    },
    {
        "id": 10,
        "title": "Customers Who Never Rented",
        "difficulty": "medium",
        "description": (
            "Find customers who have never made a rental.\n"
            "Return their full name (first_name || ' ' || last_name)\n"
            "and email, ordered by last_name.\n"
            "Tables: customer, rental  |  Use LEFT JOIN + IS NULL"
        ),
        "hint": "LEFT JOIN customer → rental, WHERE rental_id IS NULL.",
        "solution": (
            "SELECT c.first_name || ' ' || c.last_name AS customer, c.email\n"
            "FROM customer c\n"
            "LEFT JOIN rental r ON c.customer_id = r.customer_id\n"
            "WHERE r.rental_id IS NULL\n"
            "ORDER BY c.last_name;"
        ),
    },
    # ── Hard ───────────────────────────────────────────────────────────────────
    {
        "id": 11,
        "title": "Top 10 Most Profitable Films",
        "difficulty": "hard",
        "description": (
            "Find the 10 films that generated the most payment revenue.\n"
            "Return title, category, and total_revenue (rounded to 2 dp).\n"
            "Order by total_revenue descending.\n"
            "Tables: film → film_category → category,\n"
            "        film → inventory → rental → payment"
        ),
        "hint": "Six-table join. SUM(payment.amount) per film.",
        "solution": (
            "SELECT f.title, c.name AS category,\n"
            "       ROUND(SUM(p.amount), 2) AS total_revenue\n"
            "FROM film          f\n"
            "JOIN film_category fc ON f.film_id      = fc.film_id\n"
            "JOIN category      c  ON fc.category_id = c.category_id\n"
            "JOIN inventory     i  ON f.film_id      = i.film_id\n"
            "JOIN rental        r  ON i.inventory_id = r.inventory_id\n"
            "JOIN payment       p  ON r.rental_id    = p.rental_id\n"
            "GROUP BY f.film_id\n"
            "ORDER BY total_revenue DESC\n"
            "LIMIT 10;"
        ),
    },
    {
        "id": 12,
        "title": "Running Total of Daily Revenue (Window Function)",
        "difficulty": "hard",
        "description": (
            "Calculate a running total of payment revenue by day.\n"
            "Return payment_day, daily_total, and running_total\n"
            "(both rounded to 2 dp). Order by payment_day.\n"
            "Table: payment  |  Use DATE() and SUM() OVER (ORDER BY ...)"
        ),
        "hint": "CTE for daily totals, then SUM(...) OVER (ORDER BY payment_day ROWS UNBOUNDED PRECEDING).",
        "solution": (
            "WITH daily AS (\n"
            "    SELECT DATE(payment_date) AS payment_day,\n"
            "           ROUND(SUM(amount), 2) AS daily_total\n"
            "    FROM payment\n"
            "    GROUP BY payment_day\n"
            ")\n"
            "SELECT payment_day,\n"
            "       daily_total,\n"
            "       ROUND(SUM(daily_total) OVER (ORDER BY payment_day), 2) AS running_total\n"
            "FROM daily\n"
            "ORDER BY payment_day;"
        ),
    },
    {
        "id": 13,
        "title": "Top 10 Actor Co-Star Pairs",
        "difficulty": "hard",
        "description": (
            "Find the 10 pairs of actors who have co-starred in the\n"
            "most films together. Return actor1, actor2, and films_together.\n"
            "Order by films_together descending.\n"
            "Tables: film_actor, actor  |  Self-join film_actor"
        ),
        "hint": "Self-join film_actor on film_id WHERE a1.actor_id < a2.actor_id to avoid duplicates.",
        "solution": (
            "SELECT a1.first_name || ' ' || a1.last_name AS actor1,\n"
            "       a2.first_name || ' ' || a2.last_name AS actor2,\n"
            "       COUNT(*)                              AS films_together\n"
            "FROM film_actor fa1\n"
            "JOIN film_actor fa2 ON fa1.film_id = fa2.film_id\n"
            "                   AND fa1.actor_id < fa2.actor_id\n"
            "JOIN actor a1 ON fa1.actor_id = a1.actor_id\n"
            "JOIN actor a2 ON fa2.actor_id = a2.actor_id\n"
            "GROUP BY fa1.actor_id, fa2.actor_id\n"
            "ORDER BY films_together DESC\n"
            "LIMIT 10;"
        ),
    },
    {
        "id": 14,
        "title": "Longest Rental Duration per Category",
        "difficulty": "hard",
        "description": (
            "For each category, find the maximum rental duration in days\n"
            "(only for returned rentals). Return category, film title,\n"
            "and max_rental_days (rounded to 1 dp).\n"
            "Order by max_rental_days descending.\n"
            "Tables: category → film_category → film → inventory → rental"
        ),
        "hint": "julianday(return_date) - julianday(rental_date), WHERE return_date IS NOT NULL.",
        "solution": (
            "SELECT c.name AS category, f.title,\n"
            "       ROUND(MAX(julianday(r.return_date) - julianday(r.rental_date)), 1)\n"
            "           AS max_rental_days\n"
            "FROM category      c\n"
            "JOIN film_category fc ON c.category_id  = fc.category_id\n"
            "JOIN film          f  ON fc.film_id      = f.film_id\n"
            "JOIN inventory     i  ON f.film_id       = i.film_id\n"
            "JOIN rental        r  ON i.inventory_id  = r.inventory_id\n"
            "WHERE r.return_date IS NOT NULL\n"
            "GROUP BY c.category_id\n"
            "ORDER BY max_rental_days DESC;"
        ),
    },
    {
        "id": 15,
        "title": "Customers Who Rented Every Category",
        "difficulty": "hard",
        "description": (
            "Find customers who have rented at least one film from\n"
            "every category. Return the customer name.\n"
            "Order alphabetically.\n"
            "Tables: customer, rental, inventory, film_category, category"
        ),
        "hint": (
            "Correlated subquery or HAVING COUNT(DISTINCT category_id) = "
            "(SELECT COUNT(*) FROM category)."
        ),
        "solution": (
            "SELECT c.first_name || ' ' || c.last_name AS customer\n"
            "FROM customer c\n"
            "WHERE (\n"
            "    SELECT COUNT(DISTINCT fc.category_id)\n"
            "    FROM rental        r\n"
            "    JOIN inventory     i  ON r.inventory_id = i.inventory_id\n"
            "    JOIN film_category fc ON i.film_id      = fc.film_id\n"
            "    WHERE r.customer_id = c.customer_id\n"
            ") = (SELECT COUNT(*) FROM category)\n"
            "ORDER BY customer;"
        ),
    },
]
