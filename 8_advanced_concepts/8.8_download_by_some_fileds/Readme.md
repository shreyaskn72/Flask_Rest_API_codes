# flask api to create row and donwload table and other table as csv file based on some filed (age here)

## Endpoints

### 1. Create Row
- **URL:** `/create_row/<name>/<age>`
- **Method:** GET
- **Description:**Creates a new row in YourTable with the provided name and age. Also creates multiple corresponding rows in OtherTable.
- **Example:**
```bash
curl -X GET http://127.0.0.1:5000/create_row/John/30
```

### 2. Create Row
- **URL:** `/create_other_extra_row/<id>`
- **Method:** GET
- **Description:** Creates a new row in another  table with the given primary key.
- **Example:**
```bash
curl -X GET http://127.0.0.1:5000/create_other_extra_row/1
```

### 3. Download Tables by Age
- **URL:** `/download_tables_by_age/<age>`
- **Method:** GET
- **Description:** Downloads data from both tables (YourTable and OtherTable) as a CSV file based on the provided age.

- **Example:**
```bash
curl -OJ http://127.0.0.1:5000/download_tables_by_age/30
```

### 4. Download Tables by Age (automated)
- **URL:** `/download_tables_by_age_automated/<age>`
- **Method:** GET
- **Description:** Downloads data from both tables (YourTable and OtherTable) as a CSV file based on the provided age.

- **Example:**
```bash
curl -OJ http://127.0.0.1:5000/download_tables_by_age_automated/30
```
