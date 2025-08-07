import streamlit as st
import json
import os
from logging_config import logger

NOTES_FILE = "resource/notes.json"
METADATA_DIR = "resource/metadata"
USER_FILE = "resource/user.json"

from core.llm_feedback import evaluate_answers
from core.planer import advance_plan

st.set_page_config(page_title="Daily Notes Viewer", layout="wide")
st.title("📝 View & Evaluate Daily Notes")

if not os.path.exists(NOTES_FILE):
    st.error("❌ notes.json file not found.")
    st.stop()

# load notes.json
with open(NOTES_FILE, "r", encoding="utf-8") as f:
    notes = json.load(f)

# date list
dates = sorted([entry["date"] for entry in notes])

dates = [entry["date"] for entry in notes]
selected_date = st.selectbox("📅 Select a date to view:", options=dates[::-1])

is_latest = selected_date == dates[-1]

# select entry
selected_entry = next((n for n in notes if n["date"] == selected_date), None)

if selected_entry:
    st.markdown(f"**📖 Books:** {selected_entry['book']}")

    st.markdown(f"**📖 Pages:** {selected_entry['pages'][0]} to {selected_entry['pages'][1]}")

    st.markdown("### 📌 Summary")
    st.text_area("Summary", value=selected_entry.get("summary", ""), disabled=True)

    st.markdown("### ❓ Questions")
    for i, question in enumerate(selected_entry["questions"]):
        st.markdown(f"**Q{i+1}:** {question}")

    st.markdown("### ✍️ Your Answers")
    updated_answers = []
    for i, answer in enumerate(selected_entry["answers"]):
        updated = st.text_area(f"Answer {i+1}:", value=answer, key=f"ans_{i}")
        updated_answers.append(updated)

    
    st.markdown("### 📌 Evaluation")
    st.markdown(selected_entry.get("evaluation", "_No evaluation available._"))

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("💾 Save Answers"):
            for entry in notes:
                if entry["date"] == selected_date:
                    entry["answers"] = updated_answers
                    break
            with open(NOTES_FILE, "w", encoding="utf-8") as f:
                json.dump(notes, f, indent=2)
            logger.info(f"Answers saved for {selected_date}")
            st.success("Answers saved successfully.")

    with col2:
        if st.button("🧠 Evaluate"):
            try:
                logger.info(f"Evaluation triggered for {selected_date}")
                result=evaluate_answers(selected_entry)
                for entry in notes:
                    if entry["date"] == selected_date:
                        entry["evaluation"] = result
                        break
                with open(NOTES_FILE, "w", encoding="utf-8") as f:
                    json.dump(notes, f, indent=2)
                logger.info(f"Evaluation succeeded for {selected_date}")
                st.rerun()
            except Exception as e:
                logger.info(f"Evaluation failed for {selected_date}: {e}")
                st.error(f"Evaluation failed: {e}")

    with col3:
        if is_latest:
            if st.button("➡️ Advance Plan"):
                try:
                    with open(USER_FILE, "r", encoding="utf-8") as f:
                        user_data = json.load(f)
                    current_book = user_data.get("current_book", None)

                    metadata_path = os.path.join(METADATA_DIR, f"{current_book}.json")
                    success,info=advance_plan(metadata_path)
                    if success:
                        logger.info(f"Evaluation succeeded for {selected_date}: {info}")
                        st.success(info)
                    else:
                        logger.info(f"Evaluation failed for {selected_date}: {info}")
                        st.error(info)
                except Exception as e:
                    logger.info(f"Evaluation failed for {selected_date}: {e}")
                    st.error(f"Advance failed: {e}")

        else:
            st.button("➡️ Advance Plan", disabled=True)
            st.info("You can only advance today's plan.")

            
