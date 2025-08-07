
import streamlit as st
import json
import os

USER_FILE = "resource/user.json"

st.set_page_config(page_title="User Settings", layout="wide")
st.title("👤 User Settings")

# 默认结构
default_user = {
    "current_book": None,
    "email": "your@email.com",
    "reminder_morning": "08:00",
    "reminder_evening": "21:00"
}

# 加载用户数据
if os.path.exists(USER_FILE):
    with open(USER_FILE, "r", encoding="utf-8") as f:
        user_data = json.load(f)
else:
    user_data = default_user

email = user_data.get("email", default_user["email"])
reminder_morning = user_data.get("reminder_morning", default_user["reminder_morning"])
reminder_evening = user_data.get("reminder_evening", default_user["reminder_evening"])

# 显示并修改邮箱
st.subheader("📧 Email")
new_email = st.text_input("Your email:", value=email)
if st.button("Update Email"):
    user_data["email"] = new_email
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(user_data, f, indent=2)
    st.success("Email updated!")

# 显示并修改早上提醒时间
st.subheader("🌅 Morning Reminder Time")
new_morning = st.time_input("Set morning reminder time:", value=st.time_input("dummy", value=None, label_visibility="collapsed") if reminder_morning is None else reminder_morning, key="morning_input")
if st.button("Update Morning Time"):
    user_data["reminder_morning"] = str(new_morning)
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(user_data, f, indent=2)
    st.success("Morning reminder time updated!")

# 显示并修改晚上提醒时间
st.subheader("🌙 Evening Reminder Time")
new_evening = st.time_input("Set evening reminder time:", value=st.time_input("dummy2", value=None, label_visibility="collapsed") if reminder_evening is None else reminder_evening, key="evening_input")
if st.button("Update Evening Time"):
    user_data["reminder_evening"] = str(new_evening)
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(user_data, f, indent=2)
    st.success("Evening reminder time updated!")
