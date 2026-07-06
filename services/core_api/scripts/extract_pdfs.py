import os
import pdfplumber
import json
from tqdm import tqdm

RAW_DATA_PATH = "../data/raw_pdfs/supreme_court_judgments"
OUTPUT_PATH = "../data/processed"

os.makedirs(OUTPUT_PATH, exist_ok=True)

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
                text += "\n"
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return text


def main(limit_per_year=5):
    all_documents = []

    for year in os.listdir(RAW_DATA_PATH):
        year_path = os.path.join(RAW_DATA_PATH, year)
        if not os.path.isdir(year_path):
            continue

        pdf_files = os.listdir(year_path)[:limit_per_year]

        for pdf_file in tqdm(pdf_files, desc=f"Processing {year}"):
            pdf_path = os.path.join(year_path, pdf_file)
            text = extract_text_from_pdf(pdf_path)

            if len(text) > 1000:
                all_documents.append({
                    "year": year,
                    "file": pdf_file,
                    "text": text
                })

    output_file = os.path.join(OUTPUT_PATH, "documents_sample.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_documents, f, ensure_ascii=False, indent=2)

    print(f"\nSaved {len(all_documents)} documents.")


if __name__ == "__main__":
    main()
