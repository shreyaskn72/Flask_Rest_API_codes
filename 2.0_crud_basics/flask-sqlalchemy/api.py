from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'crud1.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    description = db.Column(db.String(120), unique=False)
    price = db.Column(db.String(120), unique=False)
    qty = db.Column(db.String(120), unique=False)

    def __init__(self, description, name, price, qty):
        self.description = description
        self.name = name
        self.price = price
        self.qty = qty


class ProductSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('description', 'name', 'price', 'qty')


product_schema = ProductSchema()
products_schema = ProductSchema(many=True)


# endpoint to create new product
@app.route("/product", methods=["POST"])
def add_product():
    description = request.json['description']
    name = request.json['name']
    price = request.json['price']
    qty = request.json['qty']
    new_product = Product(description, name, price, qty)
    db.session.add(new_product)
    db.session.commit()
    product = Product.query.get(new_product.id)
    return product_schema.jsonify(product)

# endpoint to show all products
@app.route("/product", methods=["GET"])
def get_product():
    all_products = Product.query.all()
    result = products_schema.dump(all_products)
    return jsonify(result)


# endpoint to get product detail by id
@app.route("/product/<id>", methods=["GET"])
def product_detail(id):
    product = Product.query.get(id)
    return product_schema.jsonify(product)


# endpoint to update product
@app.route("/product/<id>", methods=["PUT"])
def product_update(id):
    product = Product.query.get(id)
    description = request.json['description']
    name = request.json['name']
    price = request.json['price']
    qty = request.json['qty']
    product.name = name
    product.description = description
    product.price = price
    product.qty = qty
    db.session.commit()
    return product_schema.jsonify(product)


# endpoint to delete product
@app.route("/product/<id>", methods=["DELETE"])
def product_delete(id):
    product = Product.query.get(id)
    db.session.delete(product)
    db.session.commit()
    return product_schema.jsonify(product)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
