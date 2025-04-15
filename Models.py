import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_file='inventory.db'):
        self.db_file = db_file
        
    def __enter__(self):
        self.conn = sqlite3.connect(self.db_file)
        self.conn.row_factory = sqlite3.Row  # Allow access to columns by name
        self.cursor = self.conn.cursor()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()


class Category:
    @staticmethod
    def get_all():
        with Database() as db:
            db.cursor.execute('SELECT * FROM categories ORDER BY name')
            return [dict(row) for row in db.cursor.fetchall()]
    
    @staticmethod
    def get_by_id(category_id):
        with Database() as db:
            db.cursor.execute('SELECT * FROM categories WHERE category_id = ?', (category_id,))
            result = db.cursor.fetchone()
            return dict(result) if result else None
    
    @staticmethod
    def create(name, description=None):
        with Database() as db:
            try:
                db.cursor.execute('INSERT INTO categories (name, description) VALUES (?, ?)', 
                               (name, description))
                return db.cursor.lastrowid
            except sqlite3.IntegrityError:
                return None  # Category with this name already exists
    
    @staticmethod
    def update(category_id, name=None, description=None):
        with Database() as db:
            # Get current values
            db.cursor.execute('SELECT name, description FROM categories WHERE category_id = ?', (category_id,))
            result = db.cursor.fetchone()
            if not result:
                return False
            
            current_name, current_description = result
            
            # Use current values if new ones not provided
            new_name = name if name is not None else current_name
            new_description = description if description is not None else current_description
            
            try:
                db.cursor.execute('UPDATE categories SET name = ?, description = ? WHERE category_id = ?', 
                               (new_name, new_description, category_id))
                return db.cursor.rowcount > 0
            except sqlite3.IntegrityError:
                return False
    
    @staticmethod
    def delete(category_id):
        with Database() as db:
            # Check if category has products
            db.cursor.execute('SELECT COUNT(*) FROM products WHERE category_id = ?', (category_id,))
            if db.cursor.fetchone()[0] > 0:
                return False  # Cannot delete category with products
            
            db.cursor.execute('DELETE FROM categories WHERE category_id = ?', (category_id,))
            return db.cursor.rowcount > 0


class Product:
    @staticmethod
    def get_all():
        with Database() as db:
            db.cursor.execute('''
                SELECT p.*, c.name as category_name 
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                ORDER BY p.name
            ''')
            return [dict(row) for row in db.cursor.fetchall()]
    
    @staticmethod
    def get_by_id(product_id):
        with Database() as db:
            db.cursor.execute('''
                SELECT p.*, c.name as category_name 
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                WHERE p.product_id = ?
            ''', (product_id,))
            result = db.cursor.fetchone()
            return dict(result) if result else None
    
    @staticmethod
    def search(keyword):
        with Database() as db:
            search_term = f"%{keyword}%"
            db.cursor.execute('''
                SELECT p.*, c.name as category_name 
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                WHERE p.name LIKE ? OR p.description LIKE ?
                ORDER BY p.name
            ''', (search_term, search_term))
            return [dict(row) for row in db.cursor.fetchall()]
    
    @staticmethod
    def create(name, description, price, quantity, category_id):
        with Database() as db:
            try:
                db.cursor.execute('''
                    INSERT INTO products (name, description, price, quantity, category_id) 
                    VALUES (?, ?, ?, ?, ?)
                ''', (name, description, price, quantity, category_id))
                
                product_id = db.cursor.lastrowid
                
                # Log the initial inventory
                db.cursor.execute('''
                    INSERT INTO inventory_log (product_id, action, quantity, notes) 
                    VALUES (?, ?, ?, ?)
                ''', (product_id, 'CREATE', quantity, 'Product created'))
                
                return product_id
            except sqlite3.Error:
                return None
    
    @staticmethod
    def update(product_id, name=None, description=None, price=None, category_id=None):
        with Database() as db:
            # Get current values
            db.cursor.execute('''
                SELECT name, description, price, category_id 
                FROM products WHERE product_id = ?
            ''', (product_id,))
            result = db.cursor.fetchone()
            if not result:
                return False
            
            current_name, current_description, current_price, current_category_id = result
            
            # Use current values if new ones not provided
            new_name = name if name is not None else current_name
            new_description = description if description is not None else current_description
            new_price = price if price is not None else current_price
            new_category_id = category_id if category_id is not None else current_category_id
            
            try:
                db.cursor.execute('''
                    UPDATE products 
                    SET name = ?, description = ?, price = ?, category_id = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE product_id = ?
                ''', (new_name, new_description, new_price, new_category_id, product_id))
                
                return db.cursor.rowcount > 0
            except sqlite3.Error:
                return False
    
    @staticmethod
    def update_quantity(product_id, quantity_change, action, notes=None):
        with Database() as db:
            # Get current quantity
            db.cursor.execute('SELECT quantity FROM products WHERE product_id = ?', (product_id,))
            result = db.cursor.fetchone()
            if not result:
                return False
            
            current_quantity = result[0]
            new_quantity = current_quantity + quantity_change
            
            # Ensure quantity doesn't go negative
            if new_quantity < 0:
                return False
            
            # Update product quantity
            db.cursor.execute('''
                UPDATE products 
                SET quantity = ?, updated_at = CURRENT_TIMESTAMP
                WHERE product_id = ?
            ''', (new_quantity, product_id))
            
            # Log the inventory change
            db.cursor.execute('''
                INSERT INTO inventory_log (product_id, action, quantity, notes) 
                VALUES (?, ?, ?, ?)
            ''', (product_id, action, quantity_change, notes))
            
            return True
    
    @staticmethod
    def delete(product_id):
        with Database() as db:
            # Get current quantity for logging
            db.cursor.execute('SELECT quantity FROM products WHERE product_id = ?', (product_id,))
            result = db.cursor.fetchone()
            if not result:
                return False
            
            current_quantity = result[0]
            
            # Log the deletion
            db.cursor.execute('''
                INSERT INTO inventory_log (product_id, action, quantity, notes) 
                VALUES (?, ?, ?, ?)
            ''', (product_id, 'DELETE', -current_quantity, 'Product deleted'))
            
            # Delete the product
            db.cursor.execute('DELETE FROM products WHERE product_id = ?', (product_id,))
            return db.cursor.rowcount > 0


class InventoryLog:
    @staticmethod
    def get_all(limit=100):
        with Database() as db:
            db.cursor.execute('''
                SELECT l.*, p.name as product_name
                FROM inventory_log l
                JOIN products p ON l.product_id = p.product_id
                ORDER BY l.timestamp DESC
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in db.cursor.fetchall()]
    
    @staticmethod
    def get_by_product(product_id):
        with Database() as db:
            db.cursor.execute('''
                SELECT l.*, p.name as product_name
                FROM inventory_log l
                JOIN products p ON l.product_id = p.product_id
                WHERE l.product_id = ?
                ORDER BY l.timestamp DESC
            ''', (product_id,))
            return [dict(row) for row in db.cursor.fetchall()]
