import os
from fpdf import FPDF

txt_path = r"C:\Users\harsh\OneDrive\Documents\ALL Projext\Open code\Diet System\nutrimitra_documentation.txt"
pdf_path = r"C:\Users\harsh\OneDrive\Documents\ALL Projext\Open code\Diet System\nutrimitra_documentation.pdf"

# Read the text file
with open(txt_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Create PDF
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Arial", size=10)

# Write text line by line (preserve paragraphs)
for line in text.split('\n'):
    pdf.cell(0, 5, txt=line.lstrip('\ufeff'), ln=1)

pdf.output(pdf_path)
print(f"PDF created: {pdf_path}")