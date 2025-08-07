import streamlit as st
import os
import json
from core.pdf_parser import parse_pdf
from logging_config import logger


BOOK_DIR = "resource/book_dir"
COVER_DIR = "resource/covers"
METADATA_DIR = "resource/metadata"
USER_FILE = "resource/user.json"
COVER_SIZE = (180, 250)
BOOKS_PER_ROW = 5 

st.set_page_config(page_title="AI Reading Assistant", layout="wide")

st.title("📤 Upload PDF Book")

uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file is not None:
    filename = uploaded_file.name
    save_path = os.path.join(BOOK_DIR, filename)

    # save pdf file
    with open(save_path, "wb") as f:
        f.write(uploaded_file.read())

    logger.info(f"Uploaded book saved to {save_path}")
    st.success(f"Successfully saved: {filename}")

    logger.info(f"Started parsing {filename}")
    # parse pdf
    try:
        parse_pdf(filename)  # generate cover fig and metadata
        logger.info("Parsing completed successfully.")
        st.success("Parsing completed successfully.")
    except Exception as e:
        logger.error(f"Parsing failed: {e}")
        st.error(f"Parsing failed: {e}")
        
    # read metadata
    book_name = os.path.splitext(filename)[0]
    metadata_path = os.path.join(METADATA_DIR, f"{book_name}.json")

    if os.path.exists(metadata_path):
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        st.subheader("📄 Book Metadata Preview")
        has_plan = metadata.get("has_plan", False)
        current_page = metadata.get("current_page", 0)
        total_page = metadata.get("total_page", 1)

        st.markdown(f"- **Total Page Number:** `{total_page}`")

        st.markdown("### 📘 Table of Contents (Preview):")
        for section in metadata.get("metadata", [])[:4]:  # only show the first three
            st.markdown(f"- **{section['title']}**: pages {section['start_page']}–{section['end_page']}")
        st.markdown(f"- ....")
    else:
        st.warning("Metadata file not found.")

