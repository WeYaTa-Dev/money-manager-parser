import os
import sqlite3
from datetime import datetime, timedelta

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/")
def home():
    return "Money Manager Parser API - POST .mmbak file to /parse?days=7"


@app.route("/parse", methods=["POST", "OPTIONS"])
def parse():
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST")
        return response

    try:
        days = request.args.get("days", 7, type=int)
        file_data = request.get_data()

        temp_path = "/tmp/money_manager.db"
        with open(temp_path, "wb") as f:
            f.write(file_data)

        conn = sqlite3.connect(temp_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Calculate date threshold
        threshold_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        # Get recent transactions
        cursor.execute(
            """
            SELECT * FROM INOUTCOME
            WHERE WDATE >= ?
            ORDER BY WDATE DESC
        """,
            (threshold_date,),
        )
        transactions = [dict(row) for row in cursor.fetchall()]

        # Get all categories (small table)
        cursor.execute("SELECT * FROM ZCATEGORY")
        categories = [dict(row) for row in cursor.fetchall()]

        # Get all assets (small table)
        cursor.execute("SELECT * FROM ASSETS")
        assets = [dict(row) for row in cursor.fetchall()]

        conn.close()

        result = {
            "success": True,
            "filtered_days": days,
            "count": len(transactions),
            "transactions": transactions,
            "categories": categories,
            "assets": assets,
        }

        response = jsonify(result)
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    except Exception as e:
        response = jsonify({"success": False, "error": str(e)})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
