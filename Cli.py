import os
import sys
from db_schema import initialize_database
from models import Category, Product, InventoryLog

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """Print a formatted header."""
    clear_screen()
    print("=" * 50)
    print(f"{title.center(50)}")
    print("=" * 50)
    print()

def pause():
    """Pause execution until user presses Enter."""
    input("\nPress Enter to continue...")

def display_menu():
    """Display the main menu and get user choice."""
    print_header("INVENTORY MANAGEMENT SYSTEM")
    print("1. View Products")
    print("2. Add New Product")
    print("3. Update Product")
    print("4. Manage Inventory")
    print("5. Search Products")
    print("6. View Inventory Log")
    print("7. Manage Categories")
    print("0. Exit")
    
    choice = input("\nEnter your choice (0-7): ")
    return choice

def view_products():
    """Display all products in the inventory."""
    print_header("ALL PRODUCTS")
    
    products = Product.get_all()
    
    if not products:
        print("No products found in the inventory.")
        return
    
    # Print table header
    print(f"{'ID':<5} {'Name':<20} {'Category':<15} {'Price':<10} {'Quantity':<10}")
    print("-" * 60)
    
    # Print each product
    for product in products:
        print(f"{product['product_id']:<5} {product['name'][:18]:<20} {product.get('category_name', 'N/A')[:13]:<15} "
              f"${product['price']:<9.2f} {product['quantity']:<10}")
    
    pause()

def add_product():
    """Add a new product to the inventory."""
    print_header("ADD NEW PRODUCT")
    
    # Get categories for selection
    categories = Category.get_all()
    if not categories:
        print("No categories found. Please create a category first.")
        pause()
        return
    
    # Get product details
    name = input("Product Name: ")
    description = input("Product Description: ")
    
    # Validate price input
    while True:
        try:
            price = float(input("Price ($): "))
            if price < 0:
                print("Price cannot be negative.")
                continue
            break
        except ValueError:
            print("Please enter a valid number.")
    
    # Validate quantity input
    while True:
        try:
            quantity = int(input("Initial Quantity: "))
            if quantity < 0:
                print("Quantity cannot be negative.")
                continue
            break
        except ValueError:
            print("Please enter a valid number.")
    
    # Display categories for selection
    print("\nAvailable Categories:")
    for category in categories:
        print(f"{category['category_id']}. {category['name']}")
    
    # Validate category selection
    while True:
        try:
            category_id = int(input("\nSelect Category ID: "))
            if not any(c['category_id'] == category_id for c in categories):
                print("Invalid category ID.")
                continue
            break
        except ValueError:
            print("Please enter a valid number.")
    
    # Create the product
    product_id = Product.create(name, description, price, quantity, category_id)
    
    if product_id:
        print(f"\nProduct '{name}' added successfully with ID: {product_id}")
    else:
        print("\nFailed to add product. Please try again.")
    
    pause()

def update_product():
    """Update an existing product."""
    print_header("UPDATE PRODUCT")
    
    # Get product ID
    try:
        product_id = int(input("Enter Product ID to update: "))
    except ValueError:
        print("Invalid ID format.")
        pause()
        return
    
    # Get product
    product = Product.get_by_id(product_id)
    if not product:
        print(f"No product found with ID: {product_id}")
        pause()
        return
    
    print(f"\nCurrent Details for '{product['name']}':")
    print(f"Description: {product['description']}")
    print(f"Price: ${product['price']:.2f}")
    print(f"Category: {product.get('category_name', 'N/A')}")
    
    print("\nEnter new details (leave blank to keep current):")
    
    # Get updated details
    name = input(f"Name [{product['name']}]: ") or None
    description = input(f"Description [{product['description']}]: ") or None
    
    # Validate price input
    price = None
    price_input = input(f"Price [${product['price']:.2f}]: ")
    if price_input:
        try:
            price = float(price_input)
            if price < 0:
                print("Price cannot be negative. Keeping current price.")
                price = None
        except ValueError:
            print("Invalid price format. Keeping current price.")
    
    # Get categories for selection
    change_category = input("\nChange category? (y/n): ").lower() == 'y'
    category_id = None
    
    if change_category:
        categories = Category.get_all()
        if not categories:
            print("No categories found.")
        else:
            print("\nAvailable Categories:")
            for category in categories:
                print(f"{category['category_id']}. {category['name']}")
            
            # Validate category selection
            while True:
                try:
                    category_id = int(input("\nSelect Category ID: "))
                    if not any(c['category_id'] == category_id for c in categories):
                        print("Invalid category ID.")
                        continue
                    break
                except ValueError:
                    print("Please enter a valid number.")
    
    # Update the product
    success = Product.update(product_id, name, description, price, category_id)
    
    if success:
        print("\nProduct updated successfully.")
    else:
        print("\nFailed to update product. Please try again.")
    
    pause()

def manage_inventory():
    """Add or remove stock from inventory."""
    print_header("MANAGE INVENTORY")
    
    # Get product ID
    try:
        product_id = int(input("Enter Product ID: "))
    except ValueError:
        print("Invalid ID format.")
        pause()
        return
    
    # Get product
    product = Product.get_by_id(product_id)
    if not product:
        print(f"No product found with ID: {product_id}")
        pause()
        return
    
    print(f"\nCurrent stock for '{product['name']}': {product['quantity']} units")
    
    # Choose action
    print("\nChoose action:")
    print("1. Add stock")
    print("2. Remove stock")
    
    action_choice = input("\nEnter choice (1-2): ")
    
    if action_choice not in ['1', '2']:
        print("Invalid choice.")
        pause()
        return
    
    # Get quantity change
    try:
        quantity = int(input("Enter quantity: "))
        if quantity <= 0:
            print("Quantity must be positive.")
            pause()
            return
    except ValueError:
        print("Invalid quantity format.")
        pause()
        return
    
    # Add notes
    notes = input("Notes (optional): ")
    
    # Update inventory
    if action_choice == '1':
        action = 'RESTOCK'
        quantity_change = quantity
    else:  # action_choice == '2'
        action = 'SALE'
        quantity_change = -quantity
    
    success = Product.update_quantity(product_id, quantity_change, action, notes)
    
    if success:
        updated_product = Product.get_by_id(product_id)
        print(f"\nInventory updated successfully. New stock: {updated_product['quantity']} units")
    else:
        print("\nFailed to update inventory. Please check quantity.")
    
    pause()

def search_products():
    """Search for products by name or description."""
    print_header("SEARCH PRODUCTS")
    
    keyword = input("Enter search keyword: ")
    
    if not keyword:
        print("Search keyword cannot be empty.")
        pause()
        return
    
    products = Product.search(keyword)
    
    if not products:
        print(f"No products found matching '{keyword}'.")
        pause()
        return
    
    print(f"\nFound {len(products)} products matching '{keyword}':\n")
    
    # Print table header
    print(f"{'ID':<5} {'Name':<20} {'Category':<15} {'Price':<10} {'Quantity':<10}")
    print("-" * 60)
    
    # Print each product
    for product in products:
        print(f"{product['product_id']:<5} {product['name'][:18]:<20} {product.get('category_name', 'N/A')[:13]:<15} "
              f"${product['price']:<9.2f} {product['quantity']:<10}")
    
    pause()

def view_inventory_log():
    """View the inventory change log."""
    print_header("INVENTORY LOG")
    
    # Ask if user wants to filter by product
    filter_choice = input("Filter by product ID? (y/n): ").lower()
    
    if filter_choice == 'y':
        try:
            product_id = int(input("Enter Product ID: "))
            logs = InventoryLog.get_by_product(product_id)
            
            # Get product name
            product = Product.get_by_id(product_id)
            if not product:
                print(f"No product found with ID: {product_id}")
                pause()
                return
            
            print(f"\nInventory Log for '{product['name']}':\n")
        except ValueError:
            print("Invalid ID format.")
            pause()
            return
    else:
        logs = InventoryLog.get_all(25)  # Limit to last 25 entries
        print("\nLatest 25 Inventory Changes:\n")
    
    if not logs:
        print("No log entries found.")
        pause()
        return
    
    # Print table header
    print(f"{'Date/Time':<20} {'Product':<20} {'Action':<10} {'Quantity':<10} {'Notes':<20}")
    print("-" * 80)
    
    # Print each log entry
    for log in logs:
        timestamp = log['timestamp'].split('.')[0]  # Remove milliseconds
        print(f"{timestamp:<20} {log['product_name'][:18]:<20} {log['action']:<10} "
              f"{log['quantity']:<10} {log['notes'][:18] if log['notes'] else '':<20}")
    
    pause()

def manage_categories():
    """Manage product categories."""
    while True:
        print_header("MANAGE CATEGORIES")
        
        print("1. View All Categories")
        print("2. Add New Category")
        print("3. Update Category")
        print("4. Delete Category")
        print("0. Back to Main Menu")
        
        choice = input("\nEnter your choice (0-4): ")
        
        if choice == '0':
            break
        elif choice == '1':
            view_categories()
        elif choice == '2':
            add_category()
        elif choice == '3':
            update_category()
        elif choice == '4':
            delete_category()
        else:
            print("Invalid choice. Please try again.")
            pause()

def view_categories():
    """Display all categories."""
    print_header("ALL CATEGORIES")
    
    categories = Category.get_all()
    
    if not categories:
        print("No categories found.")
        pause()
        return
    
    # Print table header
    print(f"{'ID':<5} {'Name':<20} {'Description':<50}")
    print("-" * 75)
    
    # Print each category
    for category in categories:
        description = category['description'] or ''
        print(f"{category['category_id']:<5} {category['name'][:18]:<20} {description[:48]:<50}")
    
    pause()

def add_category():
    """Add a new category."""
    print_header("ADD NEW CATEGORY")
    
    name = input("Category Name: ")
    
    if not name:
        print("Category name cannot be empty.")
        pause()
        return
    
    description = input("Category Description (optional): ")
    
    category_id = Category.create(name, description)
    
    if category_id:
        print(f"\nCategory '{name}' added successfully with ID: {category_id}")
    else:
        print("\nFailed to add category. Name may already exist.")
    
    pause()

def update_category():
    """Update an existing category."""
    print_header("UPDATE CATEGORY")
    
    # Get category ID
    try:
        category_id = int(input("Enter Category ID to update: "))
    except ValueError:
        print("Invalid ID format.")
        pause()
        return
    
    # Get category
    category = Category.get_by_id(category_id)
    if not category:
        print(f"No category found with ID: {category_id}")
        pause()
        return
    
    print(f"\nCurrent Details for '{category['name']}':")
    print(f"Description: {category['description']}")
    
    print("\nEnter new details (leave blank to keep current):")
    
    # Get updated details
    name = input(f"Name [{category['name']}]: ") or None
    description = input(f"Description [{category['description']}]: ") or None
    
    # Update the category
    success = Category.update(category_id, name, description)
    
    if success:
        print("\nCategory updated successfully.")
    else:
        print("\nFailed to update category. Name may already exist.")
    
    pause()

def delete_category():
    """Delete an existing category."""
    print_header("DELETE CATEGORY")
    
    # Get category ID
    try:
        category_id = int(input("Enter Category ID to delete: "))
    except ValueError:
        print("Invalid ID format.")
        pause()
        return
    
    # Get category
    category = Category.get_by_id(category_id)
    if not category:
        print(f"No category found with ID: {category_id}")
        pause()
        return
    
    # Confirm deletion
    confirm = input(f"Are you sure you want to delete '{category['name']}'? (y/n): ").lower()
    
    if confirm != 'y':
        print("\nDeletion cancelled.")
        pause()
        return
    
    # Delete the category
    success = Category.delete(category_id)
    
    if success:
        print("\nCategory deleted successfully.")
    else:
        print("\nFailed to delete category. It may have associated products.")
    
    pause()

def main():
    """Main application entry point."""
    # Initialize database
    initialize_database()
    
    while True:
        choice = display_menu()
        
        if choice == '0':
            print("\nThank you for using the Inventory Management System. Goodbye!")
            sys.exit(0)
        elif choice == '1':
            view_products()
        elif choice == '2':
            add_product()
        elif choice == '3':
            update_product()
        elif choice == '4':
            manage_inventory()
        elif choice == '5':
            search_products()
        elif choice == '6':
            view_inventory_log()
        elif choice == '7':
            manage_categories()
        else:
            print("Invalid choice. Please try again.")
            pause()

if __name__ == "__main__":
    main()
