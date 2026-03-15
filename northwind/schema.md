# Northwind Schema — Business / ERP Database

## Tables

| Table | Key Columns |
|-------|-------------|
| **Customers** | CustomerID, CompanyName, ContactName, City, Country |
| **Employees** | EmployeeID, FirstName, LastName, Title, ReportsTo → Employee |
| **Orders** | OrderID, CustomerID → Customers, EmployeeID → Employees, OrderDate, RequiredDate, ShippedDate, ShipVia → Shippers |
| **OrderDetails** | OrderID → Orders, ProductID → Products, UnitPrice, Quantity, Discount |
| **Products** | ProductID, ProductName, SupplierID → Suppliers, CategoryID → Categories, UnitPrice, UnitsInStock, Discontinued |
| **Categories** | CategoryID, CategoryName, Description |
| **Suppliers** | SupplierID, CompanyName, Country |
| **Shippers** | ShipperID, CompanyName |
| **Territories** | TerritoryID, TerritoryDescription, RegionID → Region |
| **EmployeeTerritories** | EmployeeID → Employees, TerritoryID → Territories |
| **Region** | RegionID, RegionDescription |

## Relationships

```
Customers ──< Orders ──< OrderDetails >── Products >── Categories
                                                  >── Suppliers
Orders >── Employees >── Employees (ReportsTo)
Orders >── Shippers
Employees ──< EmployeeTerritories >── Territories >── Region
```

## Useful Notes

- **Revenue formula**: `UnitPrice * Quantity * (1 - Discount)`
- **Discontinued products**: `WHERE Discontinued = 1`
- **Late shipments**: `WHERE ShippedDate > RequiredDate`
- **Date functions**: `strftime('%Y', OrderDate)`, `strftime('%m', OrderDate)`
- **Customer tenure**: `julianday(MAX(OrderDate)) - julianday(MIN(OrderDate))`
- **Table name**: `"Order Details"` (has a space — always quote it in queries)
