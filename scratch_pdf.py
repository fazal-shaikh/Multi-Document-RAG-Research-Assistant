from fpdf import FPDF

def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    
    text = "Hello 📚 world! 📝 💬"
    safe_text = text.encode('latin-1', 'ignore').decode('latin-1')
    
    pdf.multi_cell(0, 10, safe_text)
    
    with open("test.pdf", "wb") as f:
        f.write(pdf.output())

create_pdf()
