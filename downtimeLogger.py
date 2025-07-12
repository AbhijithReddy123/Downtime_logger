import streamlit as st
import pandas as pd
from datetime import datetime
import os
import smtplib
from email.message import EmailMessage

# Page setup
st.set_page_config(layout="centered")
st.title("🛠️ Blending Downtime Logger")

# Initialize session state
if "log" not in st.session_state:
    st.session_state.log = []
if "tank" not in st.session_state:
    st.session_state.tank = ""
if "work_order" not in st.session_state:
    st.session_state.work_order = ""

# Shift setup: Tank & Work Order info
st.subheader("📋 Shift Details")
st.session_state.tank = st.text_input("Tank Number", value=st.session_state.tank)
st.session_state.work_order = st.text_input("Work Order Number", value=st.session_state.work_order)

# Downtime logging form
st.subheader("⏱️ Downtime Logger")
with st.form("log_form"):
    duration = st.number_input("Downtime Duration (minutes)", min_value=1, max_value=180, value=10)
    reason = st.text_input("Reason for Downtime")
    submitted = st.form_submit_button("Log Downtime")

if submitted:
    if reason and st.session_state.tank and st.session_state.work_order:
        event = {
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Tank Number": st.session_state.tank,
            "Work Order": st.session_state.work_order,
            "Duration (min)": duration,
            "Reason": reason
        }
        st.session_state.log.append(event)
        st.success(f"✅ Recorded: {duration} min – {reason}")
    else:
        st.warning("⚠️ Please enter all shift details before logging downtime.")

# Show current log
if st.session_state.log:
    st.subheader("📝 Logged Entries")
    df_log = pd.DataFrame(st.session_state.log)
    st.dataframe(df_log)

    # Clear button
    if st.button("🧹 Clear All Entries"):
        st.session_state.log.clear()
        st.success("All downtime entries cleared!")

# Export and Email section
if st.session_state.log:
    st.subheader("📤 Export Shift Summary & Email")
    shift_date = st.date_input("Shift Date")
    start_time = st.text_input("Start Time (e.g. 21:00)")
    end_time = st.text_input("End Time (e.g. 05:00)")

    if st.button("📧 Generate & Send Excel via Email"):
        df_log = pd.DataFrame(st.session_state.log)

        if not df_log.empty:
            summary = pd.DataFrame({
                "Tank Number": [st.session_state.tank],
                "Work Order": [st.session_state.work_order],
                "Shift Date": [shift_date.strftime("%Y-%m-%d")],
                "Start Time": [start_time],
                "End Time": [end_time],
                "Total Downtime (min)": [df_log["Duration (min)"].sum()]
            })

            # File naming
            safe_tank = st.session_state.tank.replace(" ", "_").replace("/", "_").replace(":", "-").strip()
            safe_order = st.session_state.work_order.replace(" ", "_").replace("/", "_").replace(":", "-").strip()
            safe_date = shift_date.strftime("%Y-%m-%d")
            filename = f"Downtime_{safe_tank}_{safe_order}_{safe_date}.xlsx"
            file_path = os.path.join(".", filename)  # Save to current directory

            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                summary.to_excel(writer, sheet_name="Shift Summary", index=False)
                df_log.to_excel(writer, sheet_name="Downtime Entries", index=False)

            # Email the file
            try:
                sender_email = "yourgmail@gmail.com"
                receiver_email = "abhijithreddykonda@gmail.com"
                gmail_password = "aowlxqauppjlkvlq"  # Use an app-specific password

                msg = EmailMessage()
                msg["Subject"] = "Downtime Log Summary"
                msg["From"] = sender_email
                msg["To"] = receiver_email
                msg.set_content(f"Here is your downtime summary file: {filename}")

                with open(file_path, "rb") as file:
                    msg.add_attachment(file.read(), maintype="application",
                                       subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                       filename=filename)

                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                    smtp.login(sender_email, gmail_password)
                    smtp.send_message(msg)

                st.success("📧 Excel file successfully emailed to abhijithreddykonda@gmail.com!")
            except Exception as e:
                st.warning("⚠️ Email failed to send. Please verify your credentials or enable app password.")
                st.text(f"Error: {e}")
        else:
            st.warning("⚠️ No data to export — your log is empty.")
