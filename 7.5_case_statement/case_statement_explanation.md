In SQL, the `CASE` statement is used to implement conditional logic directly within your query. It allows you to perform "if-then-else" logic in SQL and return different results depending on specified conditions. This can be useful for creating custom output or transforming data based on specific criteria.

There are two main types of `CASE` statements in SQL:

### 1. **Simple CASE Expression**
This type of `CASE` compares an expression to a set of possible values. The first match found will be returned.

#### Syntax:
```sql
CASE expression
    WHEN value1 THEN result1
    WHEN value2 THEN result2
    ...
    ELSE default_result
END
```

#### Example:
Let's say you have a `Sales` table with a column `SalesAmount`, and you want to classify sales into categories like 'Low', 'Medium', and 'High'.

```sql
SELECT SalesAmount,
       CASE SalesAmount
           WHEN 0 THEN 'No Sale'
           WHEN SalesAmount < 100 THEN 'Low'
           WHEN SalesAmount BETWEEN 100 AND 500 THEN 'Medium'
           ELSE 'High'
       END AS SalesCategory
FROM Sales;
```

### 2. **Searched CASE Expression**
This type allows you to define conditions more flexibly. Instead of matching an expression against specific values, you can evaluate different Boolean expressions in each `WHEN` clause.

#### Syntax:
```sql
CASE
    WHEN condition1 THEN result1
    WHEN condition2 THEN result2
    ...
    ELSE default_result
END
```

#### Example:
Suppose you want to categorize employees based on their years of experience (stored in the column `YearsExperience`).

```sql
SELECT EmployeeName,
       CASE
           WHEN YearsExperience < 2 THEN 'Beginner'
           WHEN YearsExperience BETWEEN 2 AND 5 THEN 'Intermediate'
           WHEN YearsExperience > 5 THEN 'Expert'
           ELSE 'Not Specified'
       END AS ExperienceLevel
FROM Employees;
```

### Key Points to Remember:
- The `CASE` statement returns a result based on the first matching condition.
- You can use `CASE` in `SELECT` statements, `WHERE` clauses, `ORDER BY`, `HAVING`, etc.
- `CASE` is evaluated in order, so the first condition that evaluates to true will be the one to return a result.
- If no conditions are met, the `ELSE` clause is returned (if specified). Otherwise, `NULL` is returned by default.

### Example in `ORDER BY`:
You can use a `CASE` statement in the `ORDER BY` clause to sort data dynamically.

```sql
SELECT ProductName, Price
FROM Products
ORDER BY 
    CASE 
        WHEN Price < 10 THEN 1
        WHEN Price BETWEEN 10 AND 50 THEN 2
        WHEN Price > 50 THEN 3
        ELSE 4
    END;
```

This would sort products in three categories: cheap (less than $10), medium ($10–50), and expensive (greater than $50). 

### Conclusion:
The `CASE` statement is a versatile tool for conditional logic in SQL. It helps transform and categorize data directly within queries, enabling complex data processing without needing to manipulate data in external applications.