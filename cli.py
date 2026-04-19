# CLI should handle CRUD operations.
import time
import requests
BASE_URL = "http://127.0.0.1:5000" # CRUD operations to be prefixed with this to link to the Flask backend
# Key facts: Use try except syntax on API operations.

def print_cli_menu():
    print("--- Inventory CLI ---")
    print("1: View all items")
    print("2: View item by id")
    print("3: Add an item")
    print("4: Update item price/stock")
    print("5: Delete an item")
    print("6: Find item on OpenFoodFacts API")
    print("7: Exit")

def convert_into_dictionary(): #Function will be used to convert JSON responses from Flask into Python dictionaries.
    #inbuild JSON functions could be used instead.
    pass


# Use 
if __name__ == '__main__':
    while True:
            print_cli_menu()
            choice = input("Select an option(number): ")
            
            if choice == '1':
                try:
                    request_to_flask = response = requests.get(f"{BASE_URL}/inventory")
                    items = response.json()

                    if not items:
                        print('Inventory is empty')
                        print_cli_menu()
                    
                    # Function should come here if inventory items are found.
        
                except:
                    # Exceptions are to be raised here, such as a loss in conncection, et,c.
                    pass
            


            elif choice == '2':
                item_id = input("Enter item ID: ")
                try:
                    request_to_flask = requests.get(f"{BASE_URL}/inventory/{item_id}")

                    if request_to_flask.status_code == 404: #Code of 404 means the item id passed as an argument by the user could not be found.
                        print(f"Item with ID {item_id} not found.")

                    # Functionality for item with the specified id being found.
                except:
                     # Exceptions are to be raised here, such as a loss in conncection, et,c.
                    pass


            elif choice == '3':
                # Inputs for adding item
                name = str(input('Enter the product name: '))
                price = float(input('Enter the price of the priduct: '))
                stock = int(input('Enter the stock level'))
                barcode_query = str(input("Do you want to enter a barcode? (y/n): "))
                if barcode_query == 'y':
                    barcode = input("Enter barcode (or leave empty): ")
                else:
                    barcode = ''
                

                request_payload = {} #Should store input data here.

                try:
                      response = requests.post(f"{BASE_URL}/inventory", json=request_payload)
                      response.raise_for_status()
                except:
                     # Exceptions are to be raised here, such as a loss in conncection, et,c.
                    pass
            
            elif choice == '4':
                item_id = input("Enter item ID to update: ")
                price = input("Enter new price (leave empty to skip): ")
                stock = input("Enter new stock (leave empty to skip): ")
    
                request_payload = {}

            try:
                if price:
                    payload['price'] = float(price)
                if stock: payload['stock'] = int(stock)

                response = requests.patch(f"{BASE_URL}/inventory/{item_id}", json=request_payload)
                
                if response.status_code == 404:
                    print(f"Item with ID {item_id} not found.")
            
        
                print("Item updated successfully!")

            except:
                # Exceptions are to be raised here, such as a loss in conncection, et,c.
                pass
            
            elif choice == '5':
                pass

            elif choice == '6':
                pass
            
            elif choice == '7': 
                print('Termminating...')
                time.sleep(1)
                print('CLI terminated.')
                time.sleep(1)
                break
            else:
                print("Invalid choice. Please select a suitable choice by typing a number from 1 to 7.")