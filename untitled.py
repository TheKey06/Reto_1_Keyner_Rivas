import base64
import io
import matplotlib.pyplot as plt
import pandas as pd
from fpdf import FPDF

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

# 2. Generar gráfico en memoria y convertir a Base64
fig, ax = plt.subplots(figsize=(6, 2.5), dpi=150)
counts = df["rating"].value_counts().reindex([1, 2, 3, 4, 5], fill_value=0)
ax.bar(counts.index, counts.values, color="#3b82f6", width=0.55)
ax.set_title("Distribución de Ratings", fontsize=10, fontweight="bold")
ax.set_xlabel("Rating")
ax.set_ylabel("Cantidad")
plt.tight_layout()

img_buf = io.BytesIO()
plt.savefig(img_buf, format="png", bbox_inches="tight")
img_buf.seek(0)
img_base64 = base64.b64encode(img_buf.getvalue()).decode("utf-8")
plt.close()

# 3. Generar archivo HTML (opcional, para referencia)
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
    <p style="margin:4px 0 0 0;">Generado con Pandas & fpdf2</p>
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

# Exportar a HTML
with open("reporte_evaluaciones.html", "w", encoding="utf-8") as f:
    f.write(html_content)

# 4. Exportar a PDF usando fpdf2
class PDF(FPDF):
    def header(self):
        # Header con fondo azul
        self.set_fill_color(30, 58, 138)  # #1e3a8a
        self.rect(0, 0, 210, 25, 'F')
        self.set_font('Arial', 'B', 16)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, 'Reporte de Evaluaciones', 0, 1, 'L')
        self.set_font('Arial', '', 9)
        self.set_text_color(200, 200, 200)
        self.cell(0, 5, 'Generado con Pandas & fpdf2', 0, 1, 'L')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

pdf = PDF(orientation='P', unit='mm', format='A4')
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=20)

# Métricas Clave
pdf.set_font('Arial', 'B', 12)
pdf.set_text_color(30, 41, 59)
pdf.cell(0, 10, 'Métricas Clave', 0, 1, 'L')
pdf.set_font('Arial', '', 11)
pdf.cell(0, 8, f'Rating Promedio: {df["rating"].mean():.2f} / 5', 0, 1, 'L')
pdf.ln(5)

# Insertar gráfico desde Base64
pdf.set_font('Arial', 'B', 12)
pdf.cell(0, 10, 'Visualización', 0, 1, 'L')

# Decodificar imagen y guardar temporalmente
import tempfile
import os
img_data = base64.b64decode(img_base64)
with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_img:
    tmp_img.write(img_data)
    tmp_path = tmp_img.name

pdf.image(tmp_path, x=30, w=150)
os.unlink(tmp_path)  # Eliminar archivo temporal
pdf.ln(5)

# Tabla de Datos
pdf.set_font('Arial', 'B', 12)
pdf.cell(0, 10, 'Tabla de Datos', 0, 1, 'L')

# Encabezados de tabla
pdf.set_fill_color(15, 23, 42)  # #0f172a
pdf.set_text_color(255, 255, 255)
pdf.set_font('Arial', 'B', 10)
pdf.cell(20, 8, 'ID', 1, 0, 'C', True)
pdf.cell(35, 8, 'Categoria', 1, 0, 'C', True)
pdf.cell(25, 8, 'Rating', 1, 0, 'C', True)
pdf.cell(110, 8, 'Comentario', 1, 1, 'C', True)

# Filas de datos
pdf.set_text_color(30, 41, 59)
pdf.set_font('Arial', '', 9)
fill = False
for _, row in df.iterrows():
    # Alternar colores de fila
    if fill:
        pdf.set_fill_color(248, 250, 252)
    else:
        pdf.set_fill_color(255, 255, 255)

    pdf.cell(20, 7, f"#{row['cliente_id']}", 1, 0, 'C', True)
    pdf.cell(35, 7, row['categoria'], 1, 0, 'L', True)
    pdf.cell(25, 7, f"{row['rating']} *", 1, 0, 'C', True)

    # Ajustar texto largo del comentario
    comment = row['descripcion']
    if len(comment) > 60:
        comment = comment[:57] + "..."
    pdf.cell(110, 7, comment, 1, 1, 'L', True)
    fill = not fill

# Guardar PDF
pdf.output("reporte_evaluaciones.pdf")

print("Archivos generados exitosamente:")
print("   - reporte_evaluaciones.html")
print("   - reporte_evaluaciones.pdf")
