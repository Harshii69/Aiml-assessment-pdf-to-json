import json
import re
from datetime import datetime
from typing import List, Dict, Any
import tkinter as tk
from tkinter import filedialog

import pdfplumber
import PyPDF2

class PDFExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.pdf_reader = PyPDF2.PdfReader(pdf_path)
        self.pdf = pdfplumber.open(pdf_path)

    def extract_text(self, page_num: int) -> str:
        page = self.pdf.pages[page_num]
        text = page.extract_text()
        return self.clean_text(text)

    def clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        return text.strip()

    def extract_tables(self, page_num: int) -> List[Dict[str, Any]]:
        page = self.pdf.pages[page_num]
        tables = page.extract_tables()
        return [self.process_table(table) for table in tables]

    def process_table(self, table: List[List[str]]) -> Dict[str, Any]:
        if not table:
            return {"table_name": "Empty Table", "columns": [], "rows": []}
        
        columns = table[0]
        rows = table[1:]
        return {
            "table_name": "Extracted Table",
            "columns": columns,
            "rows": rows
        }

    def extract_metadata(self) -> Dict[str, str]:
        info = self.pdf_reader.metadata
        return {
            "document_title": info.get('/Title', "Unknown Title"),
            "author": info.get('/Author', "Unknown Author"),
            "date": info.get('/CreationDate', datetime.now().isoformat())
        }

    def generate_json(self) -> Dict[str, Any]:
        metadata = self.extract_metadata()
        pages = []

        for i in range(len(self.pdf.pages)):
            page_text = self.extract_text(i)
            tables = self.extract_tables(i)
            page_data = {
                "page_number": i + 1,
                "text": page_text,
                "tables": tables
            }
            pages.append(page_data)

        return {
            **metadata,
            "pages": pages
        }

    def __del__(self):
        if hasattr(self, 'pdf'):
            self.pdf.close()

def select_pdf_file() -> str:
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select PDF file",
        filetypes=[("PDF files", "*.pdf")]
    )
    return file_path

def select_output_file() -> str:
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(
        title="Save JSON output as",
        defaultextension=".json",
        filetypes=[("JSON files", "*.json")]
    )
    return file_path

def main():
    pdf_path = select_pdf_file()
    if not pdf_path:
        print("No PDF file selected. Exiting.")
        return

    output_path = select_output_file()
    if not output_path:
        print("No output file selected. Exiting.")
        return

    extractor = PDFExtractor(pdf_path)
    json_data = extractor.generate_json()

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

    print(f"JSON data has been saved to {output_path}")

if __name__ == "__main__":
    main()
