# Sakila Schema — DVD Rental Store

## Tables

| Table | Key Columns |
|-------|-------------|
| **film** | film_id, title, description, release_year, language_id, rental_duration, rental_rate, length, replacement_cost, rating |
| **actor** | actor_id, first_name, last_name |
| **film_actor** | actor_id → actor, film_id → film  *(many-to-many bridge)* |
| **category** | category_id, name |
| **film_category** | film_id → film, category_id → category  *(many-to-many bridge)* |
| **language** | language_id, name |
| **inventory** | inventory_id, film_id → film, store_id → store |
| **rental** | rental_id, rental_date, inventory_id → inventory, customer_id → customer, return_date, staff_id |
| **payment** | payment_id, customer_id → customer, staff_id → staff, rental_id → rental, amount, payment_date |
| **customer** | customer_id, store_id, first_name, last_name, email, address_id → address, active |
| **staff** | staff_id, first_name, last_name, store_id → store |
| **store** | store_id, manager_staff_id, address_id → address |
| **address** | address_id, address, city_id → city |
| **city** | city_id, city, country_id → country |
| **country** | country_id, country |

## Key Relationship Paths

```
film ──< film_actor >── actor           (actor credits)
film ──< film_category >── category     (genre tags)
film ──< inventory ──< rental           (rental history)
rental ──< payment                      (revenue)
rental >── customer                     (who rented)
store >── address >── city >── country  (location)
```

## Useful Notes

- **Rental duration**: `julianday(return_date) - julianday(rental_date)` (days)
- **Active customers**: filter `WHERE customer.active = 1`
- **Ratings**: G, PG, PG-13, R, NC-17
- **String concat**: `first_name || ' ' || last_name`
- **Date functions**: `DATE(payment_date)`, `strftime('%Y-%m', rental_date)`
- **Films never rented**: LEFT JOIN film → inventory → rental, WHERE rental_id IS NULL
