# Inventory Management System

A comprehensive command-line inventory management application built with Python and SQLite.

## Features

- **Product Management**: Add, update, delete, and search products
- **Category Organization**: Create and manage product categories
- **Inventory Tracking**: Monitor stock levels and changes
- **Transaction Logging**: Complete audit trail of all inventory operations
- **Data Reporting**: Generate insights from inventory data

## Technology Stack

- **Python 3.x**: Core programming language
- **SQLite3**: Embedded database engine
- **Git/GitHub**: Version control and collaboration

## Database Design

The application uses a normalized relational database with three main tables:
- `categories`: Stores product categories
- `products`: Maintains product information with foreign key references to categories
- `inventory_log`: Records all inventory transactions with timestamps

## Project Structure

```
inventory-management-system/
├── main.py               # Application entry point
├── models.py             # Data models and database operations
├── cli.py                # Command-line interface implementation
├── db_schema.py          # Database schema definition and initialization
└── inventory.db          # SQLite database file
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/Ravikumarkatta/inventory-management-system.git
   ```

2. Navigate to the project directory:
   ```
   cd inventory-management-system
   ```

3. Initialize the database:
   ```
   python db_schema.py
   ```

## Usage

Run the application:
```
python main.py
```

Follow the interactive menu to:
- Manage product categories
- Add and update products
- Adjust inventory levels
- View transaction history
- Generate reports

## Development

The codebase demonstrates:
- SQL database design with relationships
- Python context managers for database connections
- Parameterized queries for security
- Transaction management
- Clean separation of concerns (MVC pattern)

## Future Enhancements

- User authentication system
- Web interface
- Advanced reporting features
- Data visualization
- Barcode/QR code integration
