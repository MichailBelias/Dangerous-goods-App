from flask import Flask, render_template_string
import pandas as pd

app = Flask(__name__)

# Example dataset (replace with your real data load)
HAZMAT = pd.DataFrame(
    {
        "MaterialCode": ["HM-001", "HM-002", "HM-003", "HM-004"],
        "MaterialName": ["Benzene", "Asbestos", "Mercury", "Lead Compounds"],
        "HazardClass": ["Carcinogenic", "Carcinogenic", "Toxic", "Toxic"],
        "HealthEffects": [
            "Cancer, dizziness, headaches",
            "Lung cancer, asbestosis",
            "Neurological damage",
            "Organ damage, developmental issues",
        ],
        "Regulation": ["REACH, OSHA", "EU Ban", "REACH", "REACH, OSHA"],
    }
)

HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Hazardous Materials Register</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; }
    .banner {
      background: #fff3cd; color: #856404; border: 1px solid #ffeeba;
      padding: 14px 16px; border-radius: 8px; font-weight: 600; margin-bottom: 16px;
    }
    .controls { margin: 12px 0 16px; }
    input[type="text"]{
      width: min(720px, 100%); padding: 10px 12px; border: 1px solid #ccc;
      border-radius: 8px; font-size: 14px;
    }
    table { border-collapse: collapse; width: 100%; max-width: 1200px; }
    th, td { border: 1px solid #e6e6e6; padding: 10px; text-align: left; vertical-align: top; }
    th { background: #f7f7f7; position: sticky; top: 0; z-index: 1; }
    .muted { color: #666; font-size: 12px; margin-top: 8px; }
    .count { margin: 10px 0; font-size: 13px; color: #333; }
  </style>
</head>
<body>
  <h2>Hazardous Materials Register</h2>

  <div class="banner">
    WARNING: This table contains information about hazardous materials that may pose serious risks to human health.
    Data is provided for informational and compliance purposes only. Always follow official safety guidance and applicable regulations.
  </div>

  <div class="controls">
    <label for="search"><strong>Search hazardous materials</strong></label><br />
    <input id="search" type="text" placeholder="Search by code, name, hazard class, health effects, regulation..." autocomplete="off" />
    <div class="muted">Tip: search is case-insensitive and matches across all columns.</div>
  </div>

  <div class="count" id="count"></div>

  <table id="hazmatTable">
    <thead>
      <tr>
        {% for col in columns %}
          <th>{{ col }}</th>
        {% endfor %}
      </tr>
    </thead>
    <tbody>
      {% for row in rows %}
        <tr>
          {% for cell in row %}
            <td>{{ cell }}</td>
          {% endfor %}
        </tr>
      {% endfor %}
    </tbody>
  </table>

<script>
(function(){
  const input = document.getElementById("search");
  const table = document.getElementById("hazmatTable");
  const tbody = table.tBodies[0];
  const rows = Array.from(tbody.rows);
  const countEl = document.getElementById("count");

  function normalize(s){
    return (s || "").toString().toLowerCase();
  }

  function updateCount(visible){
    countEl.textContent = `Showing ${visible} of ${rows.length} materials`;
  }

  function filter(){
    const q = normalize(input.value).trim();
    let visible = 0;

    for (const r of rows){
      const text = normalize(r.innerText);
      const show = !q || text.includes(q);
      r.style.display = show ? "" : "none";
      if (show) visible++;
    }
    updateCount(visible);
  }

  input.addEventListener("input", filter);
  filter(); // initial count
})();
</script>

</body>
</html>
"""

@app.get("/")
def index():
    # Ensure safe strings for template output
    df = HAZMAT.fillna("").astype(str)
    return render_template_string(
        HTML,
        columns=list(df.columns),
        rows=df.values.tolist()
    )

if __name__ == "__main__":
    # 0.0.0.0 makes it reachable on your LAN if needed
    app.run(host="127.0.0.1", port=5000, debug=True)
