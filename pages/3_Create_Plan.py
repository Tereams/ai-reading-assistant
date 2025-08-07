import streamlit as st
import os
import json
from core.planer import assign_reading_plan
from logging_config import logger

BOOK_DIR = "resource/book_dir"
COVER_DIR = "resource/covers"
METADATA_DIR = "resource/metadata"
USER_FILE = "resource/user.json"
COVER_SIZE = (180, 250)
BOOKS_PER_ROW = 5 

st.set_page_config(page_title="AI Reading Assistant", layout="wide")

st.title("🗓️ Create a New Reading Plan")
available_books = []

pdf_files = [f for f in os.listdir(BOOK_DIR) if f.endswith(".pdf")]
for pdf in pdf_files:
    book_name = os.path.splitext(pdf)[0]
    metadata_path = os.path.join(METADATA_DIR, f"{book_name}.json")
    if not os.path.exists(metadata_path):
        continue
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    if not metadata.get("has_plan", False):
        available_books.append(book_name)

if not available_books:
    st.info("🎉 All books already have reading plans.")
else:
    selected_book = st.selectbox("Select a book to create a plan for:", available_books)
    days = st.number_input("How many days to finish reading?", min_value=1, max_value=365, value=30)

    if st.button("📘 Generate Plan"):
        try:
            print(selected_book)
            metadata_path=os.path.join(METADATA_DIR, f"{selected_book}.json")
            assign_reading_plan(metadata_path, days)
            logger.info(f"Plan created for book: {selected_book}, duration: {days} days")
            st.success(f"✅ Plan created for \"{selected_book}\" ({days} days)")
        except Exception as e:
            logger.error(f"Failed to create plan for {selected_book}: {e}")
            st.error(f"❌ Failed to create plan: {e}")
