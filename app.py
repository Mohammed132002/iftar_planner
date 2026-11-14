import math

from flask import Flask, jsonify, request

from database import DishDatabase

app = Flask(__name__)
db = DishDatabase()

# the allowed categories
CATEGORIES = ['Soup', 'Salad', 'Main dish', 'Dessert', 'Drink']


def error(message, status):
    # one shape for every error reply
    return jsonify({'ok': False, 'error': message}), status


@app.route('/dishes')
def list_dishes():
    # GET: read the saved dishes (also the route of the report helper)
    return jsonify({'ok': True, 'dishes': db.all_dishes()})


@app.route('/dishes/add', methods=['POST'])
def add_dish():
    # POST: read the three fields from the form body
    name = request.form.get('name', '').strip()
    category = request.form.get('category', '').strip()
    cost_text = request.form.get('cost', '').strip()

    # check the required fields and the values
    if name == '':
        return error('The name is required.', 400)
    if category not in CATEGORIES:
        return error('The category must be one of: ' + ', '.join(CATEGORIES), 400)
    try:
        cost = float(cost_text)
    except ValueError:
        return error('The cost must be a number.', 400)
    if not math.isfinite(cost) or cost < 0:
        return error('The cost must be zero or more.', 400)

    # save the dish and reply with the new record
    new_id = db.add_dish(name, category, cost)
    dish = {'id': new_id, 'name': name, 'category': category, 'cost': cost}
    return jsonify({'ok': True, 'message': 'Saved ' + name, 'dish': dish})


if __name__ == '__main__':
    app.run(port=5050)
