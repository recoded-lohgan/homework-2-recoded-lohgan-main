import flask
import creds
import mysql.connector
from mysql.connector import Error
from sql import create_connection
from sql import execute_query
from sql import execute_read_query
from flask import jsonify
from flask import request

# Setting up app name
app = flask.Flask(__name__)
app.config["DEBUG"] = True  # Enable debug mode

# Creating a connection to MySQL database
myCreds = creds.Creds()
def get_db_connection():
    return mysql.connector.connect(
        host=myCreds.conString,
        user=myCreds.userName,
        password=myCreds.password,
        database=myCreds.dbName
    )

# Ensure inventory table exists
create_inv_table = """
CREATE TABLE IF NOT EXISTS inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    barbelltype VARCHAR(50) NOT NULL,
    brand VARCHAR(50) NOT NULL,
    msrp DECIMAL(10,2) NOT NULL,
    weight DECIMAL(5,2) NOT NULL,
    length DECIMAL(6,2) NOT NULL,
    color VARCHAR(30),
);
"""
conn = get_db_connection()
cursor = conn.cursor()
# Creates inventory table if one doesn't already exist
# cursor.execute(create_inv_table)
conn.commit()
cursor.close()
conn.close()

@app.route('/', methods=['GET'])
def home():
    return "<h1>WELCOME TO OUR FIRST API</h1>"

@app.route('/api/barbell', methods=['GET'])  # Get all barbells
def get_barbells():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM inventory")
    barbells = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(barbells)

@app.route('/api/barbell', methods=['POST'])  # Add a new barbell
def add_barbell():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = """
        INSERT INTO inventory (barbelltype, brand, msrp, weight, length, color)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    values = (data['barbelltype'], data['brand'], data['msrp'], data['weight'], data['length'], data['color'])
    cursor.execute(sql, values)
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Barbell added successfully!"}), 201

@app.route('/api/barbell', methods=['PUT'])  # Update MSRP
def update_msrp():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "UPDATE inventory SET msrp = %s WHERE id = %s"
    cursor.execute(sql, (data['msrp'], data['id']))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "MSRP updated successfully!"})

@app.route('/api/barbell', methods=['DELETE'])  # Delete barbell by ID (requires token)
def delete_barbell():
    data = request.get_json()
    if 'token' not in data or data['token'] != '88oo88':
        return jsonify({"error": "Invalid token!"}), 403
    
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "DELETE FROM inventory WHERE id = %s"
    cursor.execute(sql, (data['id'],))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Barbell deleted successfully!"})

@app.route('/api/inventoryvalue', methods=['GET']) # Returns JSON object of quantity and total value of inventory
def get_inv_value():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) AS quantity, SUM(msrp) AS totalvalue FROM inventory")
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify({"quantity": result[0], "totalvalue": float(result[1]) if result[1] else 0.0})


if __name__ == '__main__':
    app.run()

