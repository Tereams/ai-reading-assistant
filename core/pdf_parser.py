import os
import fitz  # PyMuPDF
import json
from logging_config import logger

BOOK_DIR = "resource/book_dir"
COVER_DIR = "resource/covers"
METADATA_DIR = "resource/metadata"

def extract_and_filter_sections(path):
    doc = fitz.open(path)
    toc = doc.get_toc()
    toc = [item for item in doc.get_toc() if item[0] == 1]
    sections = []

    if not toc:
        sections.append({
            "title": "Full Document",
            "start_page": 0,
            "end_page": len(doc) - 1,
            "page_count": len(doc),
            'page_per_day': None
        })

    else: 
        
        toc = [item for item in doc.get_toc() if item[0] == 1]

        for i, item in enumerate(toc):
            _, title, start_page = item
            start_page -= 1  # change into 0-indexed

            if i + 1 < len(toc):
                end_page = toc[i + 1][2] - 1
            else:
                end_page = len(doc)

            page_count = end_page - start_page

            sections.append({
                "title": title,
                "start_page": start_page,
                "end_page": end_page - 1,
                "page_count": page_count,
                'page_per_day': None
            })

        # flitered sectons that page_count < 3
        sections = [
            sec for sec in sections if sec["page_count"] >= 3
        ]
    return sections,len(doc)

def extract_cover_image(pdf_path, image_output_path):
    doc = fitz.open(pdf_path)
    page = doc.load_page(0)  
    pix = page.get_pixmap(dpi=150) 
    pix.save(image_output_path)

def parse_pdf(file_name):
    logger.info(f"Starting to parse PDF: {file_name}")
    book_name = os.path.splitext(file_name)[0]
    book_path = os.path.join(BOOK_DIR, f"{book_name}.pdf")
    meta_path = os.path.join(METADATA_DIR, f"{book_name}.json")
    cover_path = os.path.join(COVER_DIR, f"{book_name}.png")
    logger.info(f"Extracted cover image for: {file_name}")

    extract_cover_image(book_path, cover_path)

    section,total_len=extract_and_filter_sections(book_path)
    logger.info(f"Extracted {len(section)} sections from {file_name}, total pages: {total_len}")

    book={
        "has_plan": False,
        "current_page": 0,
        "current_chapter_plan":(0,0),
        'total_page': total_len,
        "planed_date": -1,
        "has_asked_llm": False,
        'has_advanced': False,
        "metadata": section
    }

    
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(book, f, ensure_ascii=False, indent=2)
    logger.info(f"Metadata saved to: {meta_path}")

if __name__=='__main__':

    pdf_path="book_dir/Stoner-John Williams.pdf"

    output_json_path='metadata/Stoner-John Williams.json'
    output_cover_path='covers/Stoner-John Williams.png'

    extract_cover_image(pdf_path, output_cover_path)

    section,total_len=extract_and_filter_sections(pdf_path)

    book={
        "has_plan": False,
        "current_page": 0,
        "current_chapter_plan":(0,0),
        'total_page': total_len,
        "planed_date": -1,
        "metadata": section
    }

    
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(book, f, ensure_ascii=False, indent=2)