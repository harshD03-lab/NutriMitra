import os
from fpdf import FPDF

txt_path = r"C:\Users\harsh\OneDrive\Documents\ALL Projext\Open code\Diet System\nutrimitra_documentation.txt"
pdf_path = r"C:\Users\harsh\OneDrive\Documents\ALL Projext\Open code\Diet System\nutrimitra_documentation.pdf"

def sanitize(text):
    # Replace common Unicode characters with ASCII equivalents
    replacements = {
        '\u2014': '-',   # em dash
        '\u2013': '-',   # en dash
        '\u2018': "'",   # left single quotation mark
        '\u2019': "'",   # right single quotation mark
        '\u201c': '"',   # left double quotation mark
        '\u201d': '"',   # right double quotation mark
        '\u2026': '...', # horizontal ellipsis
        '\u00a0': ' ',   # non-breaking space
        '\u2022': '-',   # bullet
        '\u201a': ',',   # single low-9 quotation mark
        '\u201e': '"',   # double low-9 quotation mark
        '\u201d': '"',   # right double quotation mark (already)
        '\u2018': "'",   # left single quotation mark (already)
        '\u2032': "'",   # prime
        '\u2033': '"',   # double prime
        '\u00b0': ' degrees', # degree sign
        '\u00b5': 'u',   # micro sign
        '\u00b2': '^2',  # superscript two
        '\u00b3': '^3',  # superscript three
        '\u2070': '0',   # superscript zero
        '\u2071': 'i',   # superscript latin small letter i
        '\u2074': '4',   # superscript four
        '\u2075': '5',   # superscript five
        '\u2076': '6',   # superscript six
        '\u2077': '7',   # superscript seven
        '\u2078': '8',   # superscript eight
        '\u2079': '9',   # superscript nine
        '\u2080': '0',   # subscript zero
        '\u2081': '1',   # subscript one
        '\u2082': '2',   # subscript two
        '\u2083': '3',   # subscript three
        '\u2084': '4',   # subscript four
        '\u2085': '5',   # subscript five
        '\u2086': '6',   # subscript six
        '\u2087': '7',   # subscript seven
        '\u2088': '8',   # subscript eight
        '\u2089': '9',   # subscript nine
    }
    for uni, ascii in replacements.items():
        text = text.replace(uni, ascii)
    # Remove any remaining non-latin-1 characters (optional)
    # We'll encode to latin-1, ignoring errors, then decode back
    try:
        text = text.encode('latin-1', 'ignore').decode('latin-1')
    except:
        pass
    return text

# Read the text file
with open(txt_path, 'r', encoding='utf-8') as f:
    text = f.read()

text = sanitize(text)

# Create PDF
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Arial", size=10)

# Write text line by line (preserve paragraphs)
for line in text.split('\n'):
    pdf.cell(0, 5, txt=line, ln=1)

pdf.output(pdf_path)
print(f"PDF created: {pdf_path}")