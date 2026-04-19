# CLI should handle CRUD operations.
BASE_URL = "http://127.0.0.1:5000"
# Key facts: Use try except syntax on API operations.

def print_cli_menu():
    print("\n--- Inventory CLI ---")
    print("1. View all items")
    print("2: View item by id")
    print("2. Add an item")
    print("3. Update item price/stock")
    print("4. Delete an item")
    print("5. Find item on OpenFoodFacts API")
    print("6. Exit")


while True:
            
        print_cli_menu()
        choice = input("Select an option: ")
        if choice == '1':
            pass
        
        elif choice == '6': 
            break
        else:
            print("Invalid option.")