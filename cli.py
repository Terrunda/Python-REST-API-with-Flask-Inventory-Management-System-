# CLI should handle CRUD operations.
import time
import requests
from app import fetch_external_data

BASE_URL = "http://127.0.0.1:5000" # CRUD operations to be prefixed with this to link to the Flask backend
# Key facts: Use try except syntax on API operations.

def print_cli_menu():
    print("GENERAL INFORMATION: Before using the CLI, ensure that Flask is running.")
    print("--- Inventory CLI ---")
    print("1: View all items")
    print("2: View item by id")
    print("3: Add an item")
    print("4: Update item price/stock")
    print("5: Delete an item")
    print("6: Find item on OpenFoodFacts API")
    print("7: Exit")

# def convert_into_dictionary(): #Function will be used to convert JSON responses from Flask into Python dictionaries.
#     #inbuild JSON functions could be used instead.
#     pass

# main functions for each CLI command.
def view_all_items():
    try:
        request_to_flask = requests.get(f"{BASE_URL}/inventory")
        request_to_flask.raise_for_status()
        items = request_to_flask.json()

        if not items:
            print('Inventory is empty')
            return
        
        #Iterationt through inventory items. They are referenced as dictionaries.
        print("[Current Inventory]")
        for item in items:
            print(f"ID: {item.get('id')} | Name: {item.get('name')} | Price: ${item.get('price', 0)} | Stock: {item.get('stock', 0)}")
 
    except requests.exceptions.RequestException as error:
        print(f"Failed to connect to API: {error}")

def view_item_by_id():
    item_id = input("Enter item ID: ")
    try:
        request_to_flask = requests.get(f"{BASE_URL}/inventory/{item_id}")

        if request_to_flask.status_code == 404: #Code of 404 means the item id passed as an argument by the user could not be found.
            print(f"Item with ID {item_id} not found.")
        
        request_to_flask.raise_for_status()

        #Case of the item witb the specified id being found.
        item = request_to_flask.json()
        print(f"ID: {item.get('id')} | Name: {item.get('name')} | Price: ${item.get('price', 0)} | Stock: {item.get('stock', 0)}")


    except requests.exceptions.RequestException as error:
            print(f"Failed to connect to API: {error}")

def add_item():
    # Inputs for adding item
    barcodeFlag = False
    barcode = None

    while not barcodeFlag:
        barcode_query = str(input("Do you want to enter a barcode? (y/n): ")).lower().strip()
        if barcode_query == 'y':
            barcode = input("Enter barcode (or leave empty): ")
        elif barcode_query == 'n':
            barcode = None
            break
        else:
            print("Invalid input for barcode. Please enter a choice ('y' or 'n')")
            barcode = input("Enter barcode (or leave empty): ")
    

    name = str(input('Enter the product name: '))
    price = float(input('Enter the price of the product: '))
    stock = int(input('Enter the stock level'))

    

    request_payload = {
        "name": name,
        "price": float(price),
        "stock": int(stock),
        "barcode": barcode
    } #Should store input data here.

    try:
        request_to_flask = requests.post(f"{BASE_URL}/inventory", json=request_payload)
        request_to_flask.raise_for_status()
        print("[Success] Item added successfully!")

    except requests.exceptions.RequestException as e:
        print(f"\n[Error] Failed to add item. API Error: {e}")

def update_item():
    pass

def delete_item():
    item_id = input("Enter item ID to delete: ")
    try:
        delete_request = requests.delete(f"{BASE_URL}/inventory/{item_id}")
        
        if delete_request.status_code == 404:
            print(f"Item with ID {item_id} not found.")
            return
            
        delete_request.raise_for_status()
        print(f"Item {item_id} deleted successfully!")
        
    except requests.exceptions.RequestException as error:
        print(f"Failed to delete item. Error: {error}")

def find_on_api():
    api_query_flag = False
    api_query_type = None
    query = None
    search_by = None

    while not api_query_flag:
        api_query_type = int(input("Search by (1) Barcode or (2) Name? "))
        if api_query_type == 1:
            query = input("Enter barcode: ").strip()
            search_by = "barcode"
            break
        elif api_query_type == 2:
            query = input("Enter product name: ").strip()
            search_by = "name"
            break
        else:
            print('Invalid entry. Please enter a number indicating your choice of search. 1 for Barcode or 2 for search')
        
    data = fetch_external_data(query, search_by)
    
    if not data:
        print("Product not found on external API.")
    
    elif data:
        print("--- OpenFoodFacts API Details ---")
        print(f"Name: {data.get('name', 'N/A')}")
        print(f"Brand: {data.get('brand', 'N/A')}")
        print(f"Category/Nutriscore: {data.get('nutriscore', data.get('category', 'N/A'))}")
        

if __name__ == '__main__':
    while True:
            print_cli_menu()
            choice = input("Select an option(number): ")
            
            if choice == '1':
                view_all_items()
            
            elif choice == '2':
               view_item_by_id()

            elif choice == '3':
                add_item()
            
            elif choice == '4':
                update_item()

            elif choice == '5':
                delete_item()

            elif choice == '6':
                find_on_api()
            
            elif choice == '7': 
                print('Termminating...')
                time.sleep(1)
                print('CLI terminated.')
                time.sleep(1)
                break
            else:
                print("Invalid choice. Please select a suitable choice by typing a number from 1 to 7.")