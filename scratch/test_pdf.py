from fpdf import FPDF
pdf = FPDF()
pdf.add_page()
pdf.set_font("helvetica", "B", size=16)
pdf.cell(0, 10, "Multi-Document RAG Research Report", ln=1)
pdf.ln(5)
pdf.set_font("helvetica", size=11)
pdf.multi_cell(0, 7, "Test line 1\nTest line 2")
output = pdf.output()
print(f"Type of output: {type(output)}")
if isinstance(output, (bytes, bytearray)):
    print(f"Length: {len(output)}")
    print(f"Starts with: {output[:5]}")
else:
    print(f"Output content: {output[:20]}...")
