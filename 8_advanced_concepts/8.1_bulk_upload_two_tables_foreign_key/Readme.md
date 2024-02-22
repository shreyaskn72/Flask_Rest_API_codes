# SQLAlchemy Bulk Upload API

This Flask API allows for bulk uploading of data into two tables using SQLAlchemy. The primary key of the first table is auto-incremented and serves as the foreign key in the second table.

## Models

- **Parent**: Defines a model with an auto-incremented primary key `id` and a `name`.
- **Child**: Defines a model with an auto-incremented primary key `id`, a `name`, and a foreign key `parent_id` referencing the `id` of the `Parent` table.

## Endpoint

### `/upload` [POST]

- Accepts POST requests containing JSON data with arrays of parents.
- Bulk inserts parents and retrieves their auto-incremented ids.
- Uses these ids to insert children along with their corresponding parent ids.
- In case of an error during the upload process, the API will roll back the transaction and return an error response.
- If successful, it will commit the changes and return a success message.

### Example JSON Payload

```json
{
  "parents": [
    {"name": "Parent 1"},
    {"name": "Parent 2"}
  ]
}
```

### Example CURL Command

```bash
curl --location 'http://localhost:5000/upload' \
--header 'Content-Type: application/json' \
--data '{
    "parents": [
        {"name": "Parent 1"},
        {"name": "Parent 2"},
        {"name": "Parent 3"},
        {"name": "Parent 4"}
    ]
}'
```




