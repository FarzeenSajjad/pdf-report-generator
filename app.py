from datetime import datetime

from fastapi import BackgroundTasks, FastAPI, HTTPException, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel

from database import get_connection, init_db
from jobs import generate_report

app = FastAPI(title="PDF Report Generator")


@app.on_event("startup")
def startup():
    init_db()


class ReportRequest(BaseModel):
    force: bool = False


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/reports", status_code=202)
def create_report(response: Response, background_tasks: BackgroundTasks, body: ReportRequest = ReportRequest()):
    conn = get_connection()

    if not body.force:
        today = datetime.now().strftime("%Y-%m-%d")
        existing = conn.execute(
            "SELECT * FROM reports WHERE status = 'done' AND created_at LIKE ? ORDER BY id DESC LIMIT 1",
            (f"{today}%",),
        ).fetchone()
        if existing:
            conn.close()
            response.status_code = 200
            return {
                "id": existing["id"],
                "status": existing["status"],
                "file": f"/reports/{existing['id']}/file",
            }

    created_at = datetime.now().isoformat()
    cursor = conn.execute(
        "INSERT INTO reports (status, created_at) VALUES ('pending', ?)",
        (created_at,),
    )
    report_id = cursor.lastrowid
    conn.commit()
    conn.close()

    background_tasks.add_task(generate_report, report_id)

    return {
        "id": report_id,
        "status": "pending",
        "file": f"/reports/{report_id}/file",
    }


@app.get("/reports/{report_id}")
def get_report(report_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Report not found")

    return {
        "id": row["id"],
        "status": row["status"],
        "created_at": row["created_at"],
        "file": f"/reports/{row['id']}/file" if row["status"] == "done" else None,
    }


@app.get("/reports/{report_id}/file")
def get_report_file(report_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Report not found")
    if row["status"] != "done":
        raise HTTPException(status_code=409, detail="Report is still being generated")

    return FileResponse(row["path"], media_type="application/pdf", filename=f"report-{report_id}.pdf")
