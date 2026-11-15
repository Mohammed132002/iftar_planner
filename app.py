import math

from flask import Flask, jsonify, request

from database import DishDatabase

app = Flask(__name__)
db = DishDatabase()

# the allowed categories
CATEGORIES = ['Dates', 'Soup', 'Fried Snacks', 'Main dish', 'Salad', 'Dessert', 'Drink']


def error(message, status):
    # one shape for every error reply
    return jsonify({'ok': False, 'error': message}), status


def read_fields(form):
    # reads and checks name, category and cost
    # returns (values, None) when valid, or (None, message) when not
    name = form.get('name', '').strip()
    category = form.get('category', '').strip()
    cost_text = form.get('cost', '').strip()

    if name == '':
        return None, 'The name is required.'
    if category not in CATEGORIES:
        return None, 'The category must be one of: ' + ', '.join(CATEGORIES)
    try:
        cost = float(cost_text)
    except ValueError:
        return None, 'The cost must be a number.'
    if not math.isfinite(cost) or cost < 0:
        return None, 'The cost must be zero or more.'

    return (name, category, cost), None


def read_id(form):
    # returns the id as an int, or None when it is not a whole number
    try:
        return int(form.get('id', '').strip())
    except ValueError:
        return None


@app.route('/dishes')
def list_dishes():
    # GET: read the saved dishes (also the route of the report helper)
    return jsonify({'ok': True, 'dishes': db.all_dishes()})


@app.route('/dishes/total')
def total():
    # GET: the extra feature, the total estimated cost
    return jsonify({'ok': True, 'total': db.total_cost()})


@app.route('/dishes/add', methods=['POST'])
def add_dish():
    # POST: check the fields, save the dish, reply with the new record
    values, message = read_fields(request.form)
    if message:
        return error(message, 400)

    name, category, cost = values
    new_id = db.add_dish(name, category, cost)
    dish = {'id': new_id, 'name': name, 'category': category, 'cost': cost}
    return jsonify({'ok': True, 'message': 'Saved ' + name, 'dish': dish})


@app.route('/dishes/edit', methods=['POST'])
def edit_dish():
    # POST: check the id and the fields, then change that dish only
    dish_id = read_id(request.form)
    if dish_id is None:
        return error('The id must be a whole number.', 400)

    values, message = read_fields(request.form)
    if message:
        return error(message, 400)

    name, category, cost = values
    if not db.update_dish(dish_id, name, category, cost):
        return error('Dish not found.', 404)

    dish = {'id': dish_id, 'name': name, 'category': category, 'cost': cost}
    return jsonify({'ok': True, 'message': 'Updated ' + name, 'dish': dish})


@app.route('/dishes/delete', methods=['POST'])
def delete_dish():
    # POST: check the id, then delete that dish only
    dish_id = read_id(request.form)
    if dish_id is None:
        return error('The id must be a whole number.', 400)

    dish = db.get_dish(dish_id)
    if dish is None or not db.delete_dish(dish_id):
        return error('Dish not found.', 404)

    return jsonify({'ok': True, 'message': 'Deleted ' + dish['name']})


if __name__ == '__main__':
    app.run(port=5050)
