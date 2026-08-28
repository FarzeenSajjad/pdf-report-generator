from datetime import datetime

from playwright.sync_api import sync_playwright

from database import get_connection


def build_html(data):
    today = datetime.now().strftime("%B %d, %Y")

    top_products_rows = "".join(
        f"<tr><td>{row['product']}</td><td>${row['revenue']:.2f}</td></tr>"
        for row in data["top_products"]
    )

    conn = get_connection()
    all_orders = conn.execute(
        "SELECT customer, product, amount, created_at FROM orders ORDER BY created_at DESC"
    ).fetchall()
    conn.close()

    all_orders_rows = "".join(
        f"<tr><td>{o['customer']}</td><td>{o['product']}</td><td>${o['amount']:.2f}</td><td>{o['created_at']}</td></tr>"
        for o in all_orders
    )

    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #222; }}
            h1 {{ font-size: 22px; margin-bottom: 0; }}
            .subtitle {{ color: #666; margin-top: 4px; }}
            .totals {{ display: flex; gap: 40px; margin: 20px 0; }}
            .totals div {{ font-size: 14px; }}
            .totals strong {{ display: block; font-size: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; }}
            th, td {{ text-align: left; padding: 6px 8px; border-bottom: 1px solid #ddd; font-size: 12px; }}
            th {{ background: #f2f2f2; }}
            tr {{ break-inside: avoid; }}
            thead {{ display: table-header-group; }}
        </style>
    </head>
    <body>
        <h1>Sales Report</h1>
        <p class="subtitle">Generated on {today}</p>

        <div class="totals">
            <div>Total orders<strong>{data['total_orders']}</strong></div>
            <div>Total revenue<strong>${data['total_revenue']:.2f}</strong></div>
        </div>

        <h3>Top 5 products by revenue</h3>
        <table>
            <thead><tr><th>Product</th><th>Revenue</th></tr></thead>
            <tbody>{top_products_rows}</tbody>
        </table>

        <h3>All orders</h3>
        <table>
            <thead><tr><th>Customer</th><th>Product</th><th>Amount</th><th>Date</th></tr></thead>
            <tbody>{all_orders_rows}</tbody>
        </table>
    </body>
    </html>
    """
    return html


def render_pdf(html, output_path):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html)
        page.pdf(path=output_path, format="A4", print_background=True)
        browser.close()


if __name__ == "__main__":
    from queries import get_report_data

    data = get_report_data()
    html = build_html(data)
    render_pdf(html, "reports/test.pdf")
    print("Saved reports/test.pdf")
