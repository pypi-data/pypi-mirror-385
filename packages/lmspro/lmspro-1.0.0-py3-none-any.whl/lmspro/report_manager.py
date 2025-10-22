
import csv
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

class ReportManager:
    """
    Generate CSV and PDF reports for LMS system.
    """

    def __init__(self, reports_dir="reports"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    # -----------------------------
    # CSV REPORT
    # -----------------------------
    def export_csv(self, filename: str, data: list[dict], headers: list[str]):
        """
        Export a list of dictionaries to CSV.
        """
        file_path = self.reports_dir / f"{filename}.csv"
        if not data:
            print(f"⚠️ No data to export for {filename}.")
            return
        with file_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)
        print(f"✅ CSV report saved: {file_path}")

    # -----------------------------
    # PDF REPORT
    # -----------------------------
    def export_pdf(self, filename: str, title: str, data: list[dict], headers: list[str]):
        """
        Export a simple PDF report with table-like text.
        """
        file_path = self.reports_dir / f"{filename}.pdf"
        if not data:
            print(f"⚠️ No data to export for {filename}.")
            return

        c = canvas.Canvas(str(file_path), pagesize=letter)
        width, height = letter
        y = height - 50

        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y, title)
        y -= 30

        # Date
        c.setFont("Helvetica", 10)
        c.drawString(50, y, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        y -= 30

        # Headers
        c.setFont("Helvetica-Bold", 12)
        x_positions = [50 + i*100 for i in range(len(headers))]
        for x, header in zip(x_positions, headers):
            c.drawString(x, y, header)
        y -= 20

        # Data rows
        c.setFont("Helvetica", 10)
        for row in data:
            for x, header in zip(x_positions, headers):
                c.drawString(x, y, str(row.get(header, "")))
            y -= 20
            if y < 50:  # New page
                c.showPage()
                y = height - 50

        c.save()
        print(f"✅ PDF report saved: {file_path}")
