import pdfplumber

# pdf_path = "Mid Term Schedule Summer 2025 V7.pdf"
pdf_path = "ENG091-1.pdf"

with pdfplumber.open(pdf_path) as pdf:
    total_pages = len(pdf.pages)
    for i in range(total_pages):
        page = pdf.pages[i]
        print(f"\n--- Page {i+1} ---")
        tables = page.extract_tables()

        if tables:
            table = tables[0]
            for row in table:
                print(row)
        else:
            print("No tables found on this page.")
