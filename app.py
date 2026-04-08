from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Temporary array to simulate storage. The storage could contain data from the OPenFoodFacts API.
inventory = []
next_inventory_id = 0 # Key ffor identifying unique inventory based on id.


# structure = {
#   "status": 1,
#   "product": {
#     "product_name": "Organic Almond Milk",
#     "brands": "Silk",
#     "ingredients_text": "Filtered water, almonds, cane sugar, ..."
#     // Additional product information
#   }

# OpenFoodFacts URLS.
# - Get product by barcode: https://world.openfoodfacts.net/api/v2/product/3017624010701?fields=product_name,nutriscore_data or https://world.openfoodfacts.net/api/v2/product/{barcode}

# function should be defined for searching API.

#Flask Routes and their view functions
@app.route('/inventory', methods=['GET'])
def view_inventory():
    return jsonify(inventory), 200


@app.route('/inventory/<int:id>', methods=['GET'])
def view_inventory_item(id):
    inventory_query = next((item for item in inventory if item["id"] == id), None)
    if inventory_query == None:
        return jsonify(f'Item with id: {id} not found'), 404
    else:
        return jsonify(inventory_query), 200

@app.route('/inventory', methods=['POST'])
def add_inventory_item():
    request_data = request.get_json() # Retrieve user input.
    global next_inventory_id
    
    if not request_data or 'name' not in request_data:
        return jsonify({"error": "Item name is required"}), 400

    new_item = {
        "id": next_inventory_id,
        "name": request_data['name'],
        "price": request_data.get('price', 0.0),
        "stock": request_data.get('stock', 0),
        "barcode": request_data.get('barcode', None)
    }

    inventory.append(new_item)
    next_inventory_id += 1
    return jsonify(new_item), 201

@app.route('/inventory/<int:id>', methods= ['PATCH'])
def update_inventory_item(id):
    item = next((i for i in inventory if i['id'] == id), None)
    if not item:
        return jsonify({"Error": "Item not found"}), 404

    request_data = request.get_json()
    if 'price' in request_data:
        item['price'] = request_data['price']
    if 'stock' in request_data:
        item['stock'] = request_data['stock']
    if 'name' in request_data:
        item['name'] = request_data['name']

    return jsonify(item), 200

@app.route('/inventory/<int:id>', methods=['DELETE'])
def delete_inventory_item(id):
    global inventory
    initial_len = len(inventory)
    inventory = [i for i in inventory if i['id'] != id]
    
    if len(inventory) < initial_len:
        return jsonify("Item deleted"), 204
    return jsonify("Error: Item not found"), 404

if __name__ == '__main__':
    app.run(debug=True)
