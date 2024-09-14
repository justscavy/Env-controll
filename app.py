from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('plants.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS plant_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plant_name TEXT,
        date TEXT,
        water_amount TEXT,
        info TEXT
    )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/log_entry', methods=['POST'])
def log_entry():
    data = request.json
    plant_name = data['plant_name']
    water_amount = data['water_amount']
    info = data['info']
    date = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect('plants.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO plant_log (plant_name, date, water_amount, info)
        VALUES (?, ?, ?, ?)
    ''', (plant_name, date, water_amount, info))
    conn.commit()
    conn.close()

    return jsonify({"success": True})

@app.route('/get_logs_by_date', methods=['GET'])
def get_logs_by_date():
    selected_date = request.args.get('date')

    conn = sqlite3.connect('plants.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM plant_log WHERE date = ?', (selected_date,))
    logs = cursor.fetchall()
    conn.close()

    return jsonify(logs)

@app.route('/get_existing_plants', methods=['GET'])
def get_existing_plants():
    conn = sqlite3.connect('plants.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT plant_name FROM plant_log')
    plants = [row[0] for row in cursor.fetchall()]
    conn.close()

    return jsonify(plants)

@app.route('/get_entries_by_date', methods=['GET'])
def get_entries_by_date():
    date_str = request.args.get('date')  # Get the date from the query parameter
    if date_str:
        conn = sqlite3.connect('plants.db')
        cursor = conn.cursor()
        # Assuming 'log_date' is the column in your database where the entry date is stored
        cursor.execute('SELECT plant_name, water_amount, info FROM plant_log WHERE log_date = ?', (date_str,))
        entries = [{'plant_name': row[0], 'water_amount': row[1], 'info': row[2]} for row in cursor.fetchall()]
        conn.close()
        return jsonify(entries=entries)
    return jsonify(entries=[])

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)
