# flask api to create row and donwload table and other table as csv file based on primary key

## Endpoints

### 1. Create Row
- **URL:** `/create_row/<name>`
- **Method:** GET
- **Description:** Creates a new row in the table with the given name.
- **Example:**
```bash
curl -X GET http://127.0.0.1:5000/create_row/John
```

### 2. Create Row
- **URL:** `/create_other_extra_row/<id>`
- **Method:** GET
- **Description:** Creates a new row in another  table with the given primary key.
- **Example:**
```bash
curl -X GET http://127.0.0.1:5000/create_other_extra_row/1
```

### 3. Download Table
- **URL:** `/download_tables/<primary_key>`
- **Method:** GET
- **Description:** Downloads the entire table as a CSV file based on the primary key.

- **Example:**
```bash
curl -OJ http://127.0.0.1:5000/download_tables/1
```
