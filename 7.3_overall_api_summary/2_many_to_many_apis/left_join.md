Yes, you're absolutely right! If some users don't have any roles assigned, they should still be included in the query results, as long as the query logic doesn't filter them out.

To ensure that users with no roles assigned are still included in the results, you need to adjust the query when filtering by roles. The current query is using a `JOIN` between `User`, `UserRole`, and `Role`, which can exclude users who do not have any roles assigned (i.e., when there is no matching row in the `user_roles` table).

### To include users without any roles, you should use a **LEFT JOIN** instead of an **INNER JOIN**. This will allow users without any roles to still be part of the result set.

### Updated Code with LEFT JOIN:

```python
@app.route('/left_join/users', methods=['GET'])
def get_users_left_join():
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

    users = query.paginate(page, per_page, False)

    result = {
        'total': users.total,
        'pages': users.pages,
        'current_page': users.page,
        'per_page': users.per_page,
        'users': [{
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'roles': [{'id': role.id, 'name': role.name} for role in user.roles] if user.roles else []
        } for user in users.items]
    }

    return jsonify(result)
```

### Key Changes:

- **LEFT JOIN**: The query now uses `isouter=True` in the `join()` calls to perform a **LEFT JOIN** on both the `UserRole` and `Role` tables. This ensures that users who do not have any roles assigned are still included in the results.
  
  ```python
  query = db.session.query(User).join(UserRole, UserRole.user_id == User.id, isouter=True).join(Role, Role.id == UserRole.role_id, isouter=True)
  ```

- **Handling users without roles**: In the result, the `roles` field will be an empty list (`[]`) for users who don't have any roles assigned. This is done using the check `if user.roles else []`.

  ```python
  'roles': [{'id': role.id, 'name': role.name} for role in user.roles] if user.roles else []
  ```

### Example Responses:

#### 1. **User with roles assigned**:
```json
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "roles": [
        {
            "id": 1,
            "name": "Admin"
        }
    ]
}
```

#### 2. **User with no roles assigned**:
```json
{
    "id": 2,
    "username": "jane_doe",
    "email": "jane@example.com",
    "roles": []
}
```

### Explanation:

1. **LEFT JOIN**: The `isouter=True` makes sure that even if there are no matching entries in the `user_roles` or `roles` tables, the `User` will still appear in the result.
2. **Empty Roles**: Users without any roles will have an empty list (`[]`) in the `roles` field, making it clear that they have no roles assigned.
3. **Pagination, Sorting, and Searching**: These features continue to work as expected, and users without roles will not be excluded by the role filter.

### Testing with `curl`:

You can use the same `curl` commands to test this:

```bash
curl "http://127.0.0.1:5000/left_join/users?page=1&per_page=5"
```

This will return both users with and without roles assigned, depending on the data in your database.

### Conclusion:

With the change to use **LEFT JOIN**, users without roles are now included in the query results, and the API will return them with an empty list for roles (`[]`). This allows for more flexibility in querying users regardless of whether they have roles assigned.