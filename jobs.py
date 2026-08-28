import os

from database import get_connection
from queries import get_report_data
from render import build_html, render_pdf

REPORTS_DIR = "reports"


def generate_report(report_id: int):
    """Runs in the background: query -> render -> save -> mark done.

    Kept as a plain function (not async) so FastAPI's BackgroundTasks
    runs it in a worker thread and the request doesn't have to wait
    for Playwright to finish.
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)
    output_path = os.path.join(REPORTS_DIR, f"{report_id}.pdf")

    data = get_report_data()
    html = build_html(data)
    render_pdf(html, output_path)

    conn = get_connection()
    conn.execute(
        "UPDATE reports SET status = ?, path = ? WHERE id = ?",
        ("done", output_path, report_id),
    )
    conn.commit()
    conn.close()
