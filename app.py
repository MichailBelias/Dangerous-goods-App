from pathlib import Path

import pandas as pd
from flask import Flask, abort, render_template, send_file

BASE_DIR = Path(__file__).resolve().parent
SDS_DIR = BASE_DIR / "SDS"
DATA_FILE = BASE_DIR / "SDS_dictionary.xlsx"

DISPLAY_COLUMNS = [
    {"key": "Material", "label": "Material"},
    {"key": "Folder", "label": "Folder"},
    {"key": "FileName", "label": "File name"},
    {"key": "FileSizeKB", "label": "Size (KB)"},
]
PDF_FIELD = "PdfRelativePath"

app = Flask(__name__)


def build_sds_index() -> pd.DataFrame:
    if not SDS_DIR.exists():
        raise FileNotFoundError(f"SDS directory not found: {SDS_DIR}")

    records: list[dict] = []
    for pdf in sorted(SDS_DIR.rglob("*.pdf")):
        rel = pdf.relative_to(SDS_DIR).as_posix()
        records.append(
            {
                "Material": " ".join(pdf.stem.replace("_", " ").split()),
                "Folder": pdf.parent.name,
                "FileName": pdf.name,
                "FileSizeKB": round(pdf.stat().st_size / 1024, 1),
                "PdfRelativePath": rel,
            }
        )

    if not records:
        raise FileNotFoundError(f"No PDF files found under {SDS_DIR}")

    df = pd.DataFrame(records).sort_values(["Folder", "Material"])
    df.to_excel(DATA_FILE, index=False)
    return df


def load_materials() -> list[dict]:
    if DATA_FILE.exists():
        df = pd.read_excel(DATA_FILE)
    else:
        df = build_sds_index()

    rows = df.fillna("").to_dict(orient="records")
    for row in rows:
        size = row.get("FileSizeKB")
        if size != "":
            try:
                row["FileSizeKB"] = f"{float(size):.1f}"
            except (TypeError, ValueError):
                row["FileSizeKB"] = str(size)
    return rows


@app.get("/")
def index():
    rows = load_materials()
    return render_template(
        "index.html",
        columns=DISPLAY_COLUMNS,
        rows=rows,
        pdf_field=PDF_FIELD,
    )


@app.get("/pdf/<path:pdf_rel>")
def serve_pdf(pdf_rel: str):
    pdf_path = (SDS_DIR / pdf_rel).resolve()
    if not pdf_path.is_file() or SDS_DIR not in pdf_path.parents:
        abort(404)
    return send_file(pdf_path, mimetype="application/pdf", as_attachment=False)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
