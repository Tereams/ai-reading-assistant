import streamlit as st
import os
import json
from PIL import Image

BOOK_DIR = "resource/book_dir"
COVER_DIR = "resource/covers"
METADATA_DIR = "resource/metadata"
USER_FILE = "resource/user.json"
COVER_SIZE = (180, 250)
BOOKS_PER_ROW = 5 


st.set_page_config(page_title="AI Reading Assistant", layout="wide")

# Tab 1: Upload Book
st.title("📚 Your Library")

current_book = None
if os.path.exists(USER_FILE):
    with open(USER_FILE, "r", encoding="utf-8") as f:
        user_data = json.load(f)
    current_book = user_data.get("current_book", None)

# get all the books
pdf_files = [f for f in os.listdir(BOOK_DIR) if f.endswith(".pdf")]
book_names = [os.path.splitext(f)[0] for f in pdf_files]

if not book_names:
    st.info("No books found in the library.")
else:
    # remove current book
    if current_book in book_names:
        book_names.remove(current_book)

    # show current book alone
    if current_book:
        st.markdown("### 📖 Currently Reading")
        metadata_path = os.path.join(METADATA_DIR, f"{current_book}.json")
        cover_path = os.path.join(COVER_DIR, f"{current_book}.png")

        if os.path.exists(cover_path):
            cover_img = Image.open(cover_path).resize(COVER_SIZE)
        else:
            cover_img = Image.new("RGB", COVER_SIZE, color=(200, 200, 200))

        if os.path.exists(metadata_path):
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            has_plan = metadata.get("has_plan", False)
            current_page = metadata.get("current_page", 0)
            total_page = metadata.get("total_page", 1)
        else:
            has_plan = False
            current_page = 0
            total_page = 1

        col = st.columns(1)[0]
        with col:
            st.image(cover_img, use_container_width=False)
            short_title = current_book[:25] + "..." if len(current_book) > 25 else current_book
            st.markdown(f"**{short_title}**", help=current_book)
            if has_plan:
                progress = current_page / total_page
                st.progress(progress, text=f"{current_page} / {total_page} pages read")
            else:
                st.markdown("**🕒 Not started**")

    # show other books in grid
    st.markdown("### 📚 All Other Books")
    cols = st.columns(BOOKS_PER_ROW)
    for idx, book_name in enumerate(book_names):
        # get cover
        cover_path = os.path.join(COVER_DIR, f"{book_name}.png")
        if os.path.exists(cover_path):
            cover_img = Image.open(cover_path).resize(COVER_SIZE)
        else:
            cover_img = Image.new("RGB", COVER_SIZE, color=(200, 200, 200))  # placeholder

        # read metadata
        metadata_path = os.path.join(METADATA_DIR, f"{book_name}.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            has_plan = metadata.get("has_plan", False)
            current_page = metadata.get("current_page", 0)
            total_page = metadata.get("total_page", 1)
        else:
            has_plan = False
            current_page = 0
            total_page = 1

        # show book card
        with cols[idx % BOOKS_PER_ROW]:
            st.image(cover_img, use_container_width=False)
            short_title = book_name[:25] + "..." if len(book_name) > 25 else book_name
            st.markdown(f"**{short_title}**", help=book_name)
            if has_plan:
                progress = current_page / total_page
                st.progress(progress, text=f"{current_page} / {total_page} pages read")
            else:
                st.markdown("**🕒 Not started**")
