from pathlib import Path

from flask import Flask, render_template
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "Dangerous Goods.xlsx"

app = Flask(__name__)

def load_hazmat():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Data file not found: {DATA_FILE}")
    df = pd.read_excel(DATA_FILE)
    return df.fillna("").astype(str)


@app.get("/")
def index():
    df = load_hazmat()
    return render_template(
        "index.html",
        columns=list(df.columns),
        rows=df.values.tolist(),
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
