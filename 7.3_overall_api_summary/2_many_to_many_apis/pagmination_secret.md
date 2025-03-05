Ah, I see! The issue you're describing seems to be related to how the `LEFT JOIN` is interacting with the pagination. When you set `per_page=10`, it might create some confusion due to how the database handles the `JOIN` operation. Since the user can have multiple roles, this may cause pagination to return more rows than expected (because of the multiple roles for each user), leading to potential "messing up" of the results.

### Problem Breakdown:

When you paginate results using `per_page=10`, each user may have multiple roles, leading to more than one row for a user (because of the `LEFT JOIN`). So, if a user has multiple roles, it will result in **more than 10 rows** per page, as each role for a user will take up one row.

To solve this issue and paginate the **users** correctly (with the appropriate number of users per page), we need to:

1. **Handle pagination at the user level**, not the result level. That means we need to ensure that the query returns one row per user, even if a user has multiple roles.

2. **Aggregate the roles into a single row for each user** after fetching the data, so that the pagination works on the user level and not the individual roles.

### Solution:

To fix this issue, we need to first retrieve all the users with their roles, then aggregate the roles for each user after the query has executed. This way, we can control pagination at the **user level**, not the **role level**.

### Updated Code:

We will update the query to fetch users in a way that ensures the correct pagination and role aggregation.

Here’s how to handle the situation:

1. Fetch the users with the roles using `LEFT JOIN`.
2. Aggregate roles at the application level (after the query is executed) to avoid having multiple rows per user.
3. Return the users and their roles in the proper format, with pagination done at the **user level**.

```python
@app.route('/users', methods=['GET'])
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '', type=str)
    sort_by = request.args.get('sort_by', 'id', type=str)
    sort_order = request.args.get('sort_order', 'asc', type=str)
    role_filter = request.args.get('role', '', type=str)

    # Using LEFT JOIN to include users without roles
    query = db.session.query(User).join(UserRole, UserRole.user_id == User.id, isouter=True).join(Role, Role.id == UserRole.role_id, isouter=True)

    if search:
        query = query.filter(
            (User.username.like(f'%{search}%')) | 
            (User.email.like(f'%{search}%'))
        )

    if role_filter:
        roles = role_filter.split(',')
        role_filters = [Role.name.like(f'%{role.strip()}%') for role in roles]
        query = query.filter(or_(*role_filters))

    if sort_by == 'username':
        sort_column = User.username
    elif sort_by == 'email':
        sort_column = User.email
    else:
        sort_column = User.id

    if sort_order == 'desc':
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Apply pagination for users (not roles)
    users = query.distinct(User.id).paginate(page, per_page, False)

    # Now aggregate roles for each user (to prevent duplication)
    result = {
        'total': users.total,
        'pages': users.pages,
        'current_page': users.page,
        'per_page': users.per_page,
        'users': []
    }

    for user in users.items:
        # Aggregating roles for each user
        user_roles = [{'id': role.id, 'name': role.name} for role in user.roles]
        result['users'].append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'roles': user_roles if user_roles else []
        })

    return jsonify(result)
```

### Key Changes:
1. **`distinct(User.id)`**: This ensures that the query retrieves **unique users**, regardless of how many roles they have. Without this, a user with multiple roles would be repeated in the result set.

   ```python
   query.distinct(User.id).paginate(page, per_page, False)
   ```

2. **Role aggregation**: After retrieving the users, we aggregate their roles into a list, so that users with multiple roles will appear only once, with all their roles in a single list.

   ```python
   user_roles = [{'id': role.id, 'name': role.name} for role in user.roles]
   ```

3. **Pagination**: Pagination is applied correctly at the **user level**, so it will give the right number of users per page, regardless of how many roles each user has.

### Explanation:
- **Pagination** is applied to the **users** (not the individual rows from the `LEFT JOIN`), so even if a user has multiple roles, they will only count as a single entry per page.
- **Distinct** ensures that each user is only included once, even if they have multiple roles.
- The **roles** are aggregated in the result after the query executes, so users with multiple roles will have a list of roles but will only appear once in the final paginated result.

### Example:
For `per_page=10`, if you have 15 users, and the first 10 users all have 1 or more roles, you’ll get the first 10 users with their roles. The roles are aggregated into a list for each user, so pagination will work as expected, without any issues.

### Testing:
You can test this fix with the same `curl` command, adjusting the `per_page` parameter:

```bash
curl "http://127.0.0.1:5000/users?page=1&per_page=10"
```

### Conclusion:
With these changes, the issue with pagination for users with multiple roles should be resolved. Each user will appear once per page, with all their roles aggregated in the response. You should now get the correct results when using different values for `per_page`, including when `per_page=10`.