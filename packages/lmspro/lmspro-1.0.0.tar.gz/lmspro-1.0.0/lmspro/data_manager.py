
from pathlib import Path
import json
import csv


class DataManager:
    """
    Smart and efficient file handler for text, JSON, CSV, and binary files.

    ✅ Auto-creates folders if missing
    ✅ Handles file-not-found safely
    ✅ Supports text, JSON, CSV, and binary operations
    ✅ Perfect for CLI or OOP-based projects
    """

    def __init__(self, file_path):
        self.path = Path(file_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    # -----------------------------
    # 🧾 TEXT HANDLING
    # -----------------------------
    def write_text(self, text: str):
        """Write plain text to file."""
        self.path.write_text(text, encoding="utf-8")

    def read_text(self) -> str:
        """Read plain text safely."""
        return self.path.read_text(encoding="utf-8") if self.path.exists() else ""

    # -----------------------------
    # 💾 JSON HANDLING
    # -----------------------------
    def write_json(self, data: dict):
        """Write a dictionary as JSON."""
        self.path.write_text(json.dumps(data, indent=4, ensure_ascii=False))

    def read_json(self) -> dict:
        """Read JSON safely and return a dict."""
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

    # -----------------------------
    # 📊 CSV HANDLING
    # -----------------------------
    def write_csv(self, rows: list[dict]):
        """Write a list of dictionaries to a CSV file."""
        if not rows:
            return
        with self.path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    def read_csv(self) -> list[dict]:
        """Read CSV into a list of dictionaries."""
        if not self.path.exists():
            return []
        with self.path.open("r", newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    # -----------------------------
    # 💽 BINARY HANDLING
    # -----------------------------
    def write_bytes(self, data: bytes):
        """Write binary data to file."""
        self.path.write_bytes(data)

    def read_bytes(self) -> bytes:
        """Read binary data safely."""
        return self.path.read_bytes() if self.path.exists() else b""

    # -----------------------------
    # 🧹 UTILITIES
    # -----------------------------
    def exists(self) -> bool:
        """Check if file exists."""
        return self.path.exists()

    def delete(self):
        """Delete the file safely."""
        if self.path.exists():
            self.path.unlink()
