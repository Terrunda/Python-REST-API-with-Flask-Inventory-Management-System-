from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import base64

app = Flask(__name__)
CORS(app)

MAIN_AUTH = base64.b64encode(b'off:off').decode()
API_AUTH = {"Authorization": f"Basic {MAIN_AUTH}"}
BASE_QUERY = 'https://world.openfoodfacts.net/api/v2'


# Temporary array to simulate storage. The storage could contain data from the OPenFoodFacts API.
inventory = []
next_inventory_id = 0 # Key ffor identifying unique inventory based on id.


# function should be defined for searching API.
def fetch_external_data(query, search_by="barcode"):
    """Fetch product details from OpenFoodFacts API."""
    try:
        if search_by == "barcode":
            url = f"{BASE_QUERY}/product/{query}.json"
            response = requests.get(url, timeout=5, headers=API_AUTH)
            data = response.json()
            if data.get("status") == 1:
                product = data["product"]
                return {"name": product.get("product_name"), "brand": product.get("brands"), "category": product.get("categories")}
        elif search_by == "name":
            url = f"{BASE_QUERY}/search?categories_tags={query}&fields=code,product_name,brands,categories"
            response = requests.get(url, timeout=5, headers=API_AUTH)
            data = response.json()
            if data.get("products") and len(data["products"]) > 0:
                p = data["products"][0]
                return {"name": p.get("product_name"), "brand": p.get("brands"), "category": p.get("categories")}
    except requests.RequestException:
        return None
    return None

#Flask Routes and their view functions
@app.route('/inventory', methods=['GET'])
def view_inventory():
    return jsonify(inventory), 200


@app.route('/inventory/<int:id>', methods=['GET'])
def view_inventory_item(id):
    inventory_query = next((item for item in inventory if item["id"] == id), None)
    if inventory_query is None:
        return jsonify(f'Item with id: {id} not found'), 404
    else:
        return jsonify(inventory_query), 200

@app.route('/inventory', methods=['POST'])
def add_inventory_item():
    request_data = request.get_json() # Retrieve user input.
    global next_inventory_id
    
    if not request_data or 'name' not in request_data:
        return jsonify("Error: Item name is required"), 400

    new_item = {
        "id": next_inventory_id,
        "name": request_data['name'],
        "price": request_data.get('price', 0.0),
        "stock": request_data.get('stock', 0),
        "barcode": request_data.get('barcode', None)
    }
    
    if new_item['barcode']:
        extra_data = fetch_external_data(new_item['barcode'], search_by="barcode")
        if extra_data:
            new_item['api_details'] = extra_data
    
    inventory.append(new_item)
    next_inventory_id += 1
    return jsonify(new_item), 201

@app.route('/inventory/<int:id>', methods= ['PATCH'])
def update_inventory_item(id):
    request_data = request.get_json()
    if not request_data:
        return jsonify("Error: No data provided"), 400
    item = next((i for i in inventory if i['id'] == id), None)
    if not item:
        return jsonify({"Error": "Item not found"}), 404

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
        return jsonify(''), 204
    return jsonify("Error: Item not found"), 404

if __name__ == '__main__':
    app.run(debug=True, port = 5000)
