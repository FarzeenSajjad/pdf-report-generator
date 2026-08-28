import random
from datetime import datetime, timedelta

from database import get_connection, init_orders_table

PRODUCTS = ["Wireless Mouse", "Mechanical Keyboard", "USB-C Hub", "Webcam", "Desk Lamp", "Monitor Stand"]
CUSTOMERS = [
    "Ayesha Khan", "Bilal Ahmed", "Sara Malik", "Hamza Iqbal", "Zainab Riaz",
    "Usman Tariq", "Mahnoor Fatima", "Ali Raza", "Hira Baig", "Fahad Sheikh",
]


def seed_orders(count=200):
    conn = get_connection()
    conn.execute("DELETE FROM orders")

    rows = []
    today = datetime.now()
    for _ in range(count):
        customer = random.choice(CUSTOMERS)
        product = random.choice(PRODUCTS)
        amount = round(random.uniform(5, 200), 2)
        days_ago = random.randint(0, 30)
        created_at = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        rows.append((customer, product, amount, created_at))

    conn.executemany(
        "INSERT INTO orders (customer, product, amount, created_at) VALUES (?, ?, ?, ?)",
        rows,
    )
    conn.commit()

    count_row = conn.execute("SELECT COUNT(*) AS total FROM orders").fetchone()
    conn.close()
    return count_row["total"]


if __name__ == "__main__":
    init_orders_table()
    total = seed_orders(200)
    print(f"Seeded {total} orders into report.db")
