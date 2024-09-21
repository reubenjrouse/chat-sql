import sqlite3

connection = sqlite3.connect("Products.db")

cursor = connection.cursor()
cursor.execute("DROP TABLE IF EXISTS products")

table_info = """
    CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    quantity_in_stock INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (product_name)
);
"""

cursor.execute(table_info)

insert_values = """
INSERT INTO products (product_id, product_name, price, quantity_in_stock, created_at) 
VALUES 
(1, 'Laptop', 999.99, 10, '2024-09-21 10:30:00'),
(2, 'Smartphone', 499.50, 25, '2024-09-21 10:31:00'),
(3, 'Headphones', 79.95, 50, '2024-09-21 10:32:00'),
(4, 'Smartwatch', 199.99, 30, '2024-09-21 10:33:00'),
(5, 'Tablet', 299.99, 15, '2024-09-21 10:32:00');
"""

cursor.execute(insert_values)

data = cursor.execute("select * from Products")
for i in data:
    print(i)

connection.commit()
connection.close()



from pathlib import Path
filepath = (Path(__file__).parent/"Products.db").absolute()
print(filepath)