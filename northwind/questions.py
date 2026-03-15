"""
Northwind — Classic Business / ERP Database
Tables: Categories, Customers, Employees, EmployeeTerritories,
        Orders, OrderDetails, Products, Region, Shippers, Suppliers, Territories
"""

DB_NAME = "northwind.db"
DB_TITLE = "Northwind: Business / ERP"
DB_DESCRIPTION = (
    "Microsoft's classic sample database: customers, orders, products,\n"
    "employees, suppliers, shippers, and territories."
)

QUESTIONS = [
    # ── Easy ──────────────────────────────────────────────────────────────────
    {
        "id": 1,
        "title": "Products with Category Names",
        "difficulty": "easy",
        "description": (
            "List every product with its category name.\n"
            "Return ProductName and CategoryName.\n"
            "Order by CategoryName, then ProductName.\n"
            "Tables: Products, Categories  |  Join on CategoryID"
        ),
        "hint": "JOIN Products and Categories on CategoryID.",
        "solution": (
            "SELECT p.ProductName, c.CategoryName\n"
            "FROM Products p\n"
            "JOIN Categories c ON p.CategoryID = c.CategoryID\n"
            "ORDER BY c.CategoryName, p.ProductName;"
        ),
    },
    {
        "id": 2,
        "title": "German Customers",
        "difficulty": "easy",
        "description": (
            "Find all customers from Germany.\n"
            "Return CompanyName, ContactName, and City.\n"
            "Order by CompanyName.\n"
            "Table: Customers  |  Column: Country"
        ),
        "hint": "WHERE Country = 'Germany'",
        "solution": (
            "SELECT CompanyName, ContactName, City\n"
            "FROM Customers\n"
            "WHERE Country = 'Germany'\n"
            "ORDER BY CompanyName;"
        ),
    },
    {
        "id": 3,
        "title": "Orders per Employee",
        "difficulty": "easy",
        "description": (
            "Count how many orders each employee has processed.\n"
            "Return employee (FirstName || ' ' || LastName) and order_count.\n"
            "Order by order_count descending.\n"
            "Tables: Employees, Orders  |  Join on EmployeeID"
        ),
        "hint": "LEFT JOIN so employees with zero orders still appear.",
        "solution": (
            "SELECT e.FirstName || ' ' || e.LastName AS employee,\n"
            "       COUNT(o.OrderID) AS order_count\n"
            "FROM Employees e\n"
            "LEFT JOIN Orders o ON e.EmployeeID = o.EmployeeID\n"
            "GROUP BY e.EmployeeID\n"
            "ORDER BY order_count DESC;"
        ),
    },
    {
        "id": 4,
        "title": "Discontinued Products",
        "difficulty": "easy",
        "description": (
            "List all discontinued products.\n"
            "Return ProductName, CategoryName, and UnitPrice.\n"
            "Order by ProductName.\n"
            "Tables: Products, Categories  |  Discontinued = 1"
        ),
        "hint": "WHERE p.Discontinued = 1, join Categories for the name.",
        "solution": (
            "SELECT p.ProductName, c.CategoryName, p.UnitPrice\n"
            "FROM Products p\n"
            "JOIN Categories c ON p.CategoryID = c.CategoryID\n"
            "WHERE p.Discontinued = 1\n"
            "ORDER BY p.ProductName;"
        ),
    },
    {
        "id": 5,
        "title": "Top 5 Priciest In-Stock Products",
        "difficulty": "easy",
        "description": (
            "Find the 5 most expensive products that are currently in stock\n"
            "(UnitsInStock > 0).\n"
            "Return ProductName, UnitPrice, and UnitsInStock.\n"
            "Table: Products"
        ),
        "hint": "WHERE UnitsInStock > 0, ORDER BY UnitPrice DESC, LIMIT 5.",
        "solution": (
            "SELECT ProductName, UnitPrice, UnitsInStock\n"
            "FROM Products\n"
            "WHERE UnitsInStock > 0\n"
            "ORDER BY UnitPrice DESC\n"
            "LIMIT 5;"
        ),
    },
    # ── Medium ─────────────────────────────────────────────────────────────────
    {
        "id": 6,
        "title": "Top 10 Products by Quantity Ordered",
        "difficulty": "medium",
        "description": (
            "Find the 10 most ordered products by total quantity sold.\n"
            "Return ProductName and total_quantity.\n"
            "Order by total_quantity descending.\n"
            "Tables: Products, OrderDetails  |  Join on ProductID"
        ),
        "hint": "JOIN Products → 'Order Details', SUM(Quantity), GROUP BY product.",
        "solution": (
            "SELECT p.ProductName, SUM(od.Quantity) AS total_quantity\n"
            "FROM Products p\n"
            'JOIN "Order Details" od ON p.ProductID = od.ProductID\n'
            "GROUP BY p.ProductID\n"
            "ORDER BY total_quantity DESC\n"
            "LIMIT 10;"
        ),
    },
    {
        "id": 7,
        "title": "Revenue by Category",
        "difficulty": "medium",
        "description": (
            "Calculate total revenue per category.\n"
            "Revenue = UnitPrice * Quantity * (1 - Discount).\n"
            "Return CategoryName and total_revenue (rounded to 2 dp).\n"
            "Order by total_revenue descending.\n"
            "Tables: Categories → Products → OrderDetails"
        ),
        "hint": "Three-way join, SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)).",
        "solution": (
            "SELECT c.CategoryName,\n"
            "       ROUND(SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)), 2) AS total_revenue\n"
            "FROM Categories c\n"
            "JOIN Products p ON c.CategoryID = p.CategoryID\n"
            'JOIN "Order Details" od ON p.ProductID = od.ProductID\n'
            "GROUP BY c.CategoryID\n"
            "ORDER BY total_revenue DESC;"
        ),
    },
    {
        "id": 8,
        "title": "Late Shipments",
        "difficulty": "medium",
        "description": (
            "Find orders that were shipped after their required date.\n"
            "Return OrderID, CompanyName, RequiredDate, and ShippedDate.\n"
            "Order by ShippedDate descending.\n"
            "Tables: Orders, Customers  |  ShippedDate > RequiredDate"
        ),
        "hint": "JOIN Customers, WHERE ShippedDate > RequiredDate (and ShippedDate IS NOT NULL).",
        "solution": (
            "SELECT o.OrderID, c.CompanyName, o.RequiredDate, o.ShippedDate\n"
            "FROM Orders o\n"
            "JOIN Customers c ON o.CustomerID = c.CustomerID\n"
            "WHERE o.ShippedDate > o.RequiredDate\n"
            "ORDER BY o.ShippedDate DESC;"
        ),
    },
    {
        "id": 9,
        "title": "Loyal Customers (15+ Orders)",
        "difficulty": "medium",
        "description": (
            "Find customers who have placed more than 15 orders.\n"
            "Return CompanyName, Country, and order_count.\n"
            "Order by order_count descending.\n"
            "Tables: Customers, Orders"
        ),
        "hint": "GROUP BY customer, HAVING COUNT(OrderID) > 15.",
        "solution": (
            "SELECT c.CompanyName, c.Country, COUNT(o.OrderID) AS order_count\n"
            "FROM Customers c\n"
            "JOIN Orders o ON c.CustomerID = o.CustomerID\n"
            "GROUP BY c.CustomerID\n"
            "HAVING order_count > 15\n"
            "ORDER BY order_count DESC;"
        ),
    },
    {
        "id": 10,
        "title": "Supplier Inventory Value",
        "difficulty": "medium",
        "description": (
            "For each supplier, calculate the total value of products\n"
            "they supply (UnitPrice * UnitsInStock).\n"
            "Return CompanyName and inventory_value (rounded to 2 dp).\n"
            "Order by inventory_value descending.\n"
            "Tables: Suppliers, Products"
        ),
        "hint": "JOIN Suppliers → Products, SUM(UnitPrice * UnitsInStock), GROUP BY supplier.",
        "solution": (
            "SELECT s.CompanyName,\n"
            "       ROUND(SUM(p.UnitPrice * p.UnitsInStock), 2) AS inventory_value\n"
            "FROM Suppliers s\n"
            "JOIN Products p ON s.SupplierID = p.SupplierID\n"
            "GROUP BY s.SupplierID\n"
            "ORDER BY inventory_value DESC;"
        ),
    },
    # ── Hard ───────────────────────────────────────────────────────────────────
    {
        "id": 11,
        "title": "Products Never Ordered",
        "difficulty": "hard",
        "description": (
            "Find products that have never appeared in any order.\n"
            "Return ProductName and UnitPrice, ordered by ProductName.\n"
            "Tables: Products, OrderDetails  |  Use LEFT JOIN + IS NULL"
        ),
        "hint": "LEFT JOIN Products → 'Order Details', WHERE od.ProductID IS NULL.",
        "solution": (
            "SELECT p.ProductName, p.UnitPrice\n"
            "FROM Products p\n"
            'LEFT JOIN "Order Details" od ON p.ProductID = od.ProductID\n'
            "WHERE od.ProductID IS NULL\n"
            "ORDER BY p.ProductName;"
        ),
    },
    {
        "id": 12,
        "title": "Monthly Revenue in 1997",
        "difficulty": "hard",
        "description": (
            "Calculate revenue for each month of 1997.\n"
            "Return month (e.g. '01') and revenue (rounded to 2 dp).\n"
            "Revenue = UnitPrice * Quantity * (1 - Discount).\n"
            "Order by month ascending.\n"
            "Tables: Orders, OrderDetails  |  Use strftime"
        ),
        "hint": "JOIN Orders → 'Order Details', WHERE year = '1997', GROUP BY month.",
        "solution": (
            "SELECT strftime('%m', o.OrderDate) AS month,\n"
            "       ROUND(SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)), 2) AS revenue\n"
            "FROM Orders o\n"
            'JOIN "Order Details" od ON o.OrderID = od.OrderID\n'
            "WHERE strftime('%Y', o.OrderDate) = '1997'\n"
            "GROUP BY month\n"
            "ORDER BY month;"
        ),
    },
    {
        "id": 13,
        "title": "Top Employees by Avg Order Value (CTE)",
        "difficulty": "hard",
        "description": (
            "Using a CTE, find the top 5 employees ranked by their average\n"
            "order value (revenue per order).\n"
            "Return employee, avg_order_value (rounded to 2 dp), and num_orders.\n"
            "Tables: Employees, Orders, OrderDetails"
        ),
        "hint": "CTE: sum revenue per order. Then AVG those per employee. JOIN Employees.",
        "solution": (
            "WITH order_totals AS (\n"
            "    SELECT o.OrderID, o.EmployeeID,\n"
            "           SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)) AS order_total\n"
            "    FROM Orders o\n"
            '    JOIN "Order Details" od ON o.OrderID = od.OrderID\n'
            "    GROUP BY o.OrderID\n"
            ")\n"
            "SELECT e.FirstName || ' ' || e.LastName     AS employee,\n"
            "       ROUND(AVG(ot.order_total), 2)         AS avg_order_value,\n"
            "       COUNT(ot.OrderID)                     AS num_orders\n"
            "FROM Employees e\n"
            "JOIN order_totals ot ON e.EmployeeID = ot.EmployeeID\n"
            "GROUP BY e.EmployeeID\n"
            "ORDER BY avg_order_value DESC\n"
            "LIMIT 5;"
        ),
    },
    {
        "id": 14,
        "title": "Customer Tenure (Days Between First and Last Order)",
        "difficulty": "hard",
        "description": (
            "For customers with more than one order, calculate how many\n"
            "days elapsed between their first and last order.\n"
            "Return CompanyName, first_order, last_order, and days_as_customer.\n"
            "Order by days_as_customer descending.\n"
            "Tables: Customers, Orders  |  Use julianday()"
        ),
        "hint": "julianday(MAX(...)) - julianday(MIN(...)), HAVING COUNT > 1.",
        "solution": (
            "SELECT c.CompanyName,\n"
            "       MIN(o.OrderDate) AS first_order,\n"
            "       MAX(o.OrderDate) AS last_order,\n"
            "       CAST(julianday(MAX(o.OrderDate)) - julianday(MIN(o.OrderDate)) AS INTEGER)\n"
            "           AS days_as_customer\n"
            "FROM Customers c\n"
            "JOIN Orders o ON c.CustomerID = o.CustomerID\n"
            "GROUP BY c.CustomerID\n"
            "HAVING COUNT(o.OrderID) > 1\n"
            "ORDER BY days_as_customer DESC;"
        ),
    },
    {
        "id": 15,
        "title": "Price Rank Within Category (Window Function)",
        "difficulty": "hard",
        "description": (
            "Use a window function to rank products within each category\n"
            "by UnitPrice (most expensive = rank 1).\n"
            "Return CategoryName, ProductName, UnitPrice, and price_rank.\n"
            "Order by CategoryName, then price_rank.\n"
            "Tables: Categories, Products"
        ),
        "hint": "RANK() OVER (PARTITION BY CategoryID ORDER BY UnitPrice DESC)",
        "solution": (
            "SELECT c.CategoryName, p.ProductName, p.UnitPrice,\n"
            "       RANK() OVER (PARTITION BY c.CategoryID ORDER BY p.UnitPrice DESC)\n"
            "           AS price_rank\n"
            "FROM Products p\n"
            "JOIN Categories c ON p.CategoryID = c.CategoryID\n"
            "ORDER BY c.CategoryName, price_rank;"
        ),
    },
]
