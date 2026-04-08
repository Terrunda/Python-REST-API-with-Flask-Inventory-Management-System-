from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Temporary array to simulate storage. The storage could contain data from the OPenFoodFacts API.
inventory = []
next_inventory_id = 0 # Key ffor identifying unique inventory based on id.


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
    request_data = request.get_json()

@app.route('/inventory/<int:id>', methods= ['PATCH'])
def update_inventory_item(id):
    request_data = request.get_json()
    return f'This URL will update an inventory with the id: {id}'

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
