# flask api to create row and donwload table as csv file

## Endpoints

### 1. Create Row
- **URL:** `/create_row/<name>`
- **Method:** GET
- **Description:** Creates a new row in the table with the given name.
- **Example:**
```bash
curl -X GET http://127.0.0.1:5000/create_row/John
```

### 2. Download Table
- **URL:** `/download_table/<primary_key>`
- **Method:** GET
- **Description:** Downloads the entire table as a CSV file based on the primary key.

- **Example:**
```bash
curl -OJ http://127.0.0.1:5000/download_table/1
```




