from flask import Flask, jsonify, request

app = Flask(__name__)

# Temporary array to simulate storage. The storage could contain data from the OPenFoodFacts API.
inventory = [{
    "status": 1,
    "product": {"product_name": "Organic Almond Milk",
                "brands": "Silk",
                "ingredients_text": "Filtered water, almonds, cane sugar, ..."
            }   
}]

# Mock database. Each item must contain an id.

# Function to query OpenFoodFacts API either using 'barcode' or 'product name'





#Flask Routes and their view functions
@app.route('/inventory', methods=['GET']) #Route for fetching items(products) in the inventory.
def view_inventory():
    return 'This URL will be used to fetch all items in the inventory.' 

@app.route('/inventory/<int:id>', methods=['GET'])
def view_inventory_item(id):
    return f'This URL will fetch a single item with the id: {id}'

@app.route('/inventory', methods=['POST'])
def add_inventory_item():
    return 'This URL will be used to add a new item to the inventory.'

@app.route('/inventory/<int:id>', methods= ['PATCH'])
def update_inventory_item(id):
    return f'This URL will update an inventory with the id: {id}'

@app.route('/inventory/<int:id>', methods=['DELETE'])
def delete_inventory_item(id):
    return f'This URL will be used to delete an item from the inventory with the id: {id}'



if __name__ == '__main__':
    app.run(debug=True)
