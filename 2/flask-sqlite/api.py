# We are building a restful api . json data for a client.microservice
# import modules..... Flask and sqlite3 is used here

from flask import Flask, request, jsonify, make_response
import sqlite3
from flask_httpauth import HTTPBasicAuth

# Init app
app = Flask(__name__)
auth = HTTPBasicAuth()

db_name = "first.db"

@app.before_request
def initdb_command():
  try:
    with sqlite3.connect(db_name) as con:
      cur = con.cursor()
      cur.execute("CREATE TABLE IF NOT EXISTS Product (id INTEGER PRIMARY KEY, name text, description text, price INTEGER,qty INTEGER)")
      con.commit()
  finally:
    con.close()

@auth.get_password
def get_password(username):
    if username == 'shreyaskn72':
        return 'secret'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)


@app.route('/product', methods=["POST"])
@auth.login_required
def add_product():
    if request.is_json:
      req = request.get_json()
      if not (req.get('name') and req.get('description') and req.get('price') and req.get('qty')):
            res = make_response(jsonify("name, description, price and qty fields are required"), 403)
            return res

      else:

        name = request.json['name']
        description = request.json['description']
        price = request.json['price']
        qty = request.json['qty']
        try:
            with sqlite3.connect(db_name) as con:
                cur = con.cursor()
                cur.execute("INSERT into Product (name, description, price, qty) values (?,?,?,?)",
                            (name, description, price, qty))
                cur.execute('''SELECT * from Product WHERE id = (SELECT MAX(id)  FROM Product)''')
                # Fetching all rows from the table
                products = cur.fetchall();
                response_body = {
                    "name": products[0][1],
                    "description": products[0][2],
                    "price": products[0][3],
                    "qty": products[0][4]
                }
                con.commit()
                return jsonify({products[0][0]: response_body})
        except:
            con.rollback()
            return jsonify("The product could not be added! Contact the admin")
        finally:
            con.close()
    else:
        return make_response(jsonify({"message": "Request body must be JSON"}))

# Get Single Products
@app.route('/product/<id>', methods=['GET'])
@auth.login_required
def get_product(id):
  try:
    with sqlite3.connect(db_name) as con:
      cur = con.cursor()
      cur.execute('''SELECT * from Product where id = ?''', (id,))
      products = cur.fetchall();
      con.commit()
      if products!=[]:
          response_body = {
              "id": products[0][0],
              "name": products[0][1],
              "description" : products[0][2],
              "price" : products[0][3],
              "qty" : products[0][4]
          }
          return jsonify({products[0][0]: response_body})
      else:
        return jsonify("The product you searched is over/removed")
  except:
      con.rollback()
      return jsonify("The product you searched could not be read for some reason")
  finally:
      con.close()

# Update operation

@app.route('/product/update', methods=["PUT"])
@auth.login_required
def update_user():
    if request.is_json:
     req = request.get_json()

     if not (req.get('id') and req.get('name')):
       res = make_response(jsonify("id and name fields are required"), 403)
       return res

     else:

      try:
          _json = request.json
          js_id = _json['id']
          name = _json['name']
          description = _json['description']
          price = _json['price']
          qty = _json['qty']
          with sqlite3.connect(db_name) as con:
             sql = "UPDATE Product SET name=?, description= ?, price= ?, qty= ? WHERE id = ?"
             cur = con.cursor()
             cur.execute(sql, (name, description, price, qty, js_id))
             cur.execute('''SELECT * from Product where id = ?''', (js_id,))
             products = cur.fetchall();
             con.commit()

             response_body = {
                 "id": products[0][0],
                 "name": products[0][1],
                 "description": products[0][2],
                 "price": products[0][3],
                 "qty": products[0][4]
             }
             return jsonify({products[0][0]: response_body})

      except KeyError:
            return jsonify("Make sure you enter the id of the product to update it")

      except IndexError:
          return jsonify("The id you entered doesnot exist in the database")

      except:
            return jsonify("The product you searched could not be updated for some reason. Check your fields once")

      finally:
          con.close()

    else:
        return make_response(jsonify({"message": "Request body must be JSON"}), 400)


@app.route('/product/delete', methods=["DELETE"])
@auth.login_required
def delete_user():
    if request.is_json:
        _json = request.json
        try:
            if (_json['id'] and request.method == 'DELETE'):
                js_id = _json['id']
                with sqlite3.connect(db_name) as con:
                    cur = con.cursor()
                    cur.execute("delete from Product where id = ?", (js_id,))
                    con.commit()
                    resp = jsonify('Product deleted successfully!')
                    return resp
                    con.close()
        except KeyError:
            return jsonify("You have forgotten to enter key or the product with the key doesnot exist in the database")

        except:
            return jsonify("The product could not be deleted for some reason")


# Run server
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
