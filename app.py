from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

if __name__ == '__main__':
    app.run(debug=True)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=False, nullable=False)
    id_category = db.Column(db.Integer, unique=False, nullable=True)

    def __init__(self, name, id_category):
        self.name = name
        self.id_category = id_category

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name


db.create_all()


@app.route('/products', methods=['GET'])
def get_products():
    products = {}
    for product in db.session.query(Product):
        categories = []
        for category in db.session.query(Category).\
                filter(Category.id == product.id_category).all():
            categories.append(category.name)
        if products.get(product.name) is None:
            products[product.name] = categories
        else:
            for el in categories:
                products.get(product.name).append(el)
    return jsonify(products)

@app.route('/categories', methods=['GET'])
def get_categories():
    categories = {}
    for category in db.session.query(Category):
        products = []
        for product in db.session.query(Product).\
                filter(Product.id_category == category.id).all():
            products.append(product.name)
        if categories.get(category.name) is None:
            categories[category.name] = products
        else:
            for el in products:
                categories.get(category.name).append(el)
    return jsonify(categories)


@app.route('/couples', methods=['GET'])
def get_couples():
    couples = []
    for product, category in db.session.query(Product, Category). \
        join(Category, Product.id_category == Category.id, full=True).all():
        if product and category:
            couples.append(f"{product.name} - {category.name}")
        elif product is None:
            couples.append(f" - {category.name}")
        elif category is None:
            couples.append(f"{product.name} - ")
    return jsonify(couples)


@app.route('/list_categories', methods=['GET'])
def get_list_categories():
    categories = []
    for category in db.session.query(Category).all():
        del category.__dict__['_sa_instance_state']
        categories.append(category.__dict__)
    return jsonify(categories)

@app.route('/list_products', methods=['GET'])
def get_list_products():
    products = []
    for product in db.session.query(Product).all():
        del product.__dict__['_sa_instance_state']
        products.append(product.__dict__)
    return jsonify(products)


@app.route('/product', methods=['POST'])
def create_product():
    body = request.get_json()
    db.session.add(Product(body['name'], body['id_category']))
    db.session.commit()
    return "product created"

@app.route('/category', methods=['POST'])
def create_category():
    body = request.get_json()
    db.session.add(Category(body['name']))
    db.session.commit()
    return "category created"


@app.route('/category/<id>', methods=['DELETE'])
def delete_category(id):
    db.session.query(Category).filter_by(id=id).delete()
    db.session.commit()
    return "category deleted"

@app.route('/product/<id>', methods=['DELETE'])
def delete_product(id):
    db.session.query(Product).filter_by(id=id).delete()
    db.session.commit()
    return "product deleted"
