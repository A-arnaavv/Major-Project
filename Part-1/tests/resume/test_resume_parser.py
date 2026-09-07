from app.resume.parser import extract_text_from_pdf


pdf_path = "data/raw/Tanishka latest.pdf"

text = extract_text_from_pdf(pdf_path)

print("\n----- EXTRACTED TEXT -----\n")

print(text)

print("\n----- INFO -----")
print("Number of characters extracted:", len(text))