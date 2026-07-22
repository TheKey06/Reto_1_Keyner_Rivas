import base64
import io
import matplotlib.pyplot as plt
import pandas as pd
from weasyprint import HTML

# 1. Dataset de muestra (Ratings y comentarios limpios)
data = {
    "cliente_id": [101, 102, 103, 104, 105, 106, 107, 108],
    "rating": [5, 5, 4, 1, 5, 2, 3, 4],
    "descripcion": [
        "Excelente servicio y entrega rápida",
        "Muy satisfecho con la calidad",
        "Buen producto, aunque tardó un poco",
        "Llegó dañado y la atención fue mala",
        "Superó mis expectativas totalmente",
        "El producto no coincide",
        "Aceptable, cumple su función",
        "Buena relación calidad-precio",
    ],
    "categoria": [
        "Electrónica",
        "Hogar",
        "Electrónica",
        "Ropa",
        "Hogar",
        "Electrónica",
        "Hogar",
        "Electrónica",
    ],
}
df = pd.DataFrame(data)

# 2. Generar gráfico en memoria y convertira Base64
fig, ax = plt.subplots(figsize=(6, 2.5), dpi=150)
counts = df["rating"].value_counts().reindex([1, 2, 3, 4, 5], fill_value=0)
ax.bar(counts.index, counts.values, color="#3b82f6", width=0.55)
ax.set_title("Distribución de Ratings", fontsize=10, fontweight="bold")
plt.tight_layout()

img_buf = io.BytesIO()
plt.savefig(img_buf, format="png", bbox_inches="tight")
img_buf.seek(0)
img_base64 = base64.b64encode(img_buf.getvalue()).decode("utf-8")
plt.close()

# 3. Construir la estructura HTML con diseño responsivo/impresión
html_content = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    @page {{
        size: A4;
        margin: 12mm 10mm;
        background-color: #f8fafc;
    }}
    body {{
        font-family: Arial, sans-serif;
        color: #1e293b;
        margin: 0;
    }}
    .header {{
        background-color: #1e3a8a;
        color: white;
        padding: 15px;
        margin: -12mm -10mm 15px -10mm;
    }}
    .data-table {{
        width: 100%;
        border-collapse: collapse;
        background: white;
        margin-top: 10px;
    }}
    .data-table th {{
        background: #0f172a;
        color: white;
        padding: 8px;
        text-align: left;
    }}
    .data-table td {{
        padding: 8px;
        border-bottom: 1px solid #e2e8f0;
    }}
</style>
</head>
<body>

<div class="header">
    <h1 style="margin:0;">Reporte de Evaluaciones</h1>
    <p style="margin:4px 0 0 0;">Generado con Pandas & WeasyPrint</p>
</div>

<h3>Métricas Clave</h3>
<p><b>Rating Promedio:</b> {df['rating'].mean():.2f} / 5</p>

<h3>Visualización</h3>
<div style="text-align:center;">
    <img src="data:image/png;base64,{img_base64}" style="max-width:100%;">
</div>

<h3>Tabla de Datos</h3>
<table class="data-table">
    <thead>
        <tr><th>ID</th><th>Categoría</th><th>Rating</th><th>Comentario</th></tr>
    </thead>
    <tbody>
"""

for _, row in df.iterrows():
    html_content += f"""
        <tr>
            <td>#{row['cliente_id']}</td>
            <td>{row['categoria']}</td>
            <td><b>{row['rating']} ★</b></td>
            <td>{row['descripcion']}</td>
        </tr>
    """

html_content += """
    </tbody>
</table>
</body>
</html>
"""

# 4. Exportar a HTML
with open("reporte_evaluaciones.html", "w", encoding="utf-8") as f:
    f.write(html_content)

# 5. Exportar a PDF usando WeasyPrint
HTML("reporte_evaluaciones.html").write_pdf("reporte_evaluaciones.pdf")