import os
import sqlite3
from datetime import datetime, timedelta

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/")
def home():
    return """Money Manager Parser API - POST .mmbak file to /parse

Filter options:
- ?days=7 (last N days, use 0 for all)
- ?start_date=2024-01-01&end_date=2024-12-31 (specific range)
- ?start_date=2024-01-01 (from date to now)
- ?end_date=2024-12-31 (all up to date)
"""


@app.route("/parse", methods=["POST", "OPTIONS"])
def parse():
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST")
        return response

    try:
        # Get filter parameters
        start_date = request.args.get("start_date")  # YYYY-MM-DD
        end_date = request.args.get("end_date")      # YYYY-MM-DD
        days = request.args.get("days", type=int)

        file_data = request.get_data()

        temp_path = "/tmp/money_manager.db"
        with open(temp_path, "wb") as f:
            f.write(file_data)

        conn = sqlite3.connect(temp_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Build query based on filters
        query = "SELECT * FROM INOUTCOME"
        params = []
        conditions = []

        if start_date or end_date:
            # Use explicit date range
            if start_date:
                conditions.append("WDATE >= ?")
                params.append(start_date)
            if end_date:
                conditions.append("WDATE <= ?")
                params.append(end_date)
        elif days is not None:
            # Use days parameter (existing behavior)
            if days > 0:
                threshold_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
                conditions.append("WDATE >= ?")
                params.append(threshold_date)
            # days=0 means no filter (all records)
        else:
            # Default: last 7 days
            threshold_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            conditions.append("WDATE >= ?")
            params.append(threshold_date)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY WDATE DESC"

        cursor.execute(query, params)
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
            "filter": {
                "start_date": start_date,
                "end_date": end_date,
                "days": days
            },
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
