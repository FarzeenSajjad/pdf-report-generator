from datetime import datetime, timedelta

from database import get_connection


def get_report_data():
    conn = get_connection()

    total_orders = conn.execute("SELECT COUNT(*) AS total FROM orders").fetchone()["total"]

    total_revenue = conn.execute("SELECT SUM(amount) AS total FROM orders").fetchone()["total"] or 0

    top_products = conn.execute(
        """
        SELECT product, SUM(amount) AS revenue
        FROM orders
        GROUP BY product
        ORDER BY revenue DESC
        LIMIT 5
        """
    ).fetchall()

    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    orders_per_day = conn.execute(
        """
        SELECT created_at AS day, COUNT(*) AS orders
        FROM orders
        WHERE created_at >= ?
        GROUP BY created_at
        ORDER BY created_at
        """,
        (seven_days_ago,),
    ).fetchall()

    conn.close()

    return {
        "total_orders": total_orders,
        "total_revenue": round(total_revenue, 2),
        "top_products": [dict(row) for row in top_products],
        "orders_last_7_days": [dict(row) for row in orders_per_day],
    }


if __name__ == "__main__":
    import json

    print(json.dumps(get_report_data(), indent=2))
