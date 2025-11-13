from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

@app.route('/')
def home():
    return 'Money Manager Parser API - POST .mmbak file to /parse'

@app.route('/parse', methods=['POST', 'OPTIONS'])
def parse():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    try:
        file_data = request.get_data()

        # Write to temp file
        temp_path = '/tmp/money_manager.db'
        with open(temp_path, 'wb') as f:
            f.write(file_data)

        conn = sqlite3.connect(temp_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        result = {
            "success": True,
            "tables": tables,
            "data": {}
        }

        # Get data from each table
        for table_name in tables:
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            result["data"][table_name] = [dict(row) for row in rows]

        conn.close()

        response = jsonify(result)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    except Exception as e:
        response = jsonify({"success": False, "error": str(e)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
```

**`requirements.txt`:**
```
flask==3.0.0
gunicorn==21.2.0
