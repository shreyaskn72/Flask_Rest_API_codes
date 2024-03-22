# Flask API with SQLAlchemy: Create, Update, and Undo Update

This Flask API provides endpoints to create an entry in an SQLite database, update the entry, and undo the update to restore the original data.

## Setup

1. Install dependencies:
   ```bash
   pip install Flask flask_sqlalchemy
   ```
   
2.  Run the Flask application:
    ```bash
     python app.py
    ```
    
## API Endpoints Curl Examples

1. Create Entry:

```
curl -X POST -H "Content-Type: application/json" -d '{"data":"example data"}' http://localhost:5000/create_entry
```

2. Update Entry:
```
curl -X PUT -H "Content-Type: application/json" -d '{"data":"updated data"}' http://localhost:5000/update_entry/1
```

3. Undo Updated entry:
```
curl -X PUT http://localhost:5000/undo_update/1
```



