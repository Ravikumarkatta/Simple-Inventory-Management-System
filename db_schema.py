import sqlite3
import os

# Function to initialize the database
def initialize_database():
    # Check if database file exists
    db_exists = os.path.exists('inventory.db')
    
    # Connect to database (will create it if it doesn't exist)
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL,
        category_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories (category_id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inventory_log (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        action TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        notes TEXT,
        FOREIGN KEY (product_id) REFERENCES products (product_id)
    )
    ''')
    
    # If database was just created, insert some sample data
    if not db_exists:
        # Insert sample categories
        categories = [
            ('Electronics', 'Electronic devices and accessories'),
            ('Clothing', 'Apparel and fashion items'),
            ('Groceries', 'Food and household supplies'),
            ('Furniture', 'Home and office furniture')
        ]
        cursor.executemany('INSERT INTO categories (name, description) VALUES (?, ?)', categories)
        
        # Insert sample products
        products = [
            ('Laptop', 'High-performance laptop', 999.99, 10, 1),
            ('Smartphone', 'Latest smartphone model', 699.99, 15, 1),
            ('T-shirt', 'Cotton t-shirt', 19.99, 50, 2),
            ('Jeans', 'Denim jeans', 39.99, 30, 2),
            ('Rice', '5kg bag of rice', 12.99, 100, 3),
            ('Office Chair', 'Ergonomic office chair', 149.99, 5, 4)
        ]
        cursor.executemany('INSERT INTO products (name, description, price, quantity, category_id) VALUES (?, ?, ?, ?, ?)', products)
        
        # Log initial inventory
        for product in products:
            name, _, _, quantity, _ = product
            cursor.execute('SELECT product_id FROM products WHERE name = ?', (name,))
            product_id = cursor.fetchone()[0]
            cursor.execute('INSERT INTO inventory_log (product_id, action, quantity, notes) VALUES (?, ?, ?, ?)', 
                          (product_id, 'INITIAL', quantity, 'Initial inventory setup'))
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Database initialized successfully!")

if __name__ == "__main__":
    initialize_database()
