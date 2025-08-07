import streamlit as st
import os
import json
from logging_config import logger

BOOK_DIR = "resource/book_dir"
COVER_DIR = "resource/covers"
METADATA_DIR = "resource/metadata"
USER_FILE = "resource/user.json"
COVER_SIZE = (180, 250)
BOOKS_PER_ROW = 5 

st.set_page_config(page_title="AI Reading Assistant", layout="wide")

st.title("🔄 Switch Current Plan")
# read user.json
if not os.path.exists(USER_FILE):
    st.error("❌ User profile not found.")
    st.stop()

with open(USER_FILE, "r", encoding="utf-8") as f:
    user_data = json.load(f)

current_book = user_data.get("current_book", None)
email = user_data.get("email", "unknown@example.com")

if current_book:
    st.markdown(f"**📖 Current Book:** `{current_book}`")
else:
    st.warning("No current reading plan.")

# get all book that has_plan == True
pdf_files = [f for f in os.listdir(BOOK_DIR) if f.endswith(".pdf")]
switchable_books = []

for pdf in pdf_files:
    book_name = os.path.splitext(pdf)[0]
    if book_name == current_book:
        continue  # excluding current reading book

    metadata_path = os.path.join(METADATA_DIR, f"{book_name}.json")
    if not os.path.exists(metadata_path):
        continue

    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    if metadata.get("has_plan", False):
        switchable_books.append(book_name)

# choose a new book
if not switchable_books:
    st.info("No other books with plans available.")
else:
    selected_book = st.selectbox("Select a new book to switch to:", switchable_books)

    if st.button("✅ Confirm Switch"):
        user_data["current_book"] = selected_book
        try:
            with open(USER_FILE, "w", encoding="utf-8") as f:
                json.dump(user_data, f, indent=2)
            logger.info(f"Switched reading plan to: {selected_book}")
            st.success(f"Switched current plan to: {selected_book}")
        except Exception as e:
            logger.error(f"Failed to update user profile when switching to {selected_book}: {e}")
            st.error(f"Failed to update user profile: {e}")

