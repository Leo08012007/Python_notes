import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import smtplib
from email.mime.text import MIMEText
import requests
import base64
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIGURATION & CREDENTIALS ---
st.set_page_config(page_title="Community Wildlife Guard", page_icon="🐾", layout="wide")

IMGBB_API_KEY = "354650f530b00c02ddd30a28a9c808f7"
GMAIL_SENDER = "mokshithatailuru@gmail.com"
GMAIL_PASSWORD = st.secrets["EMAIL_PASS"]

# --- CONNECT TO GOOGLE SHEETS DATABASE ---
# --- CONNECT TO GOOGLE SHEETS DATABASE ---
import json

@st.cache_resource
def init_db():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    # 1. Read the JSON string from Streamlit Secrets
    gcp_secret = st.secrets["GCP_KEY"]
    
    # 2. Convert it into a Python dictionary
    creds_dict = json.loads(gcp_secret)
    
    # 3. Authenticate using the dictionary directly (no file needed!)
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    
    return client.open("Wildlife_Reports").sheet1

sheet = init_db()
# --- HELPER FUNCTIONS ---
def upload_image_to_cloud(image_file):
    """Uploads the photo to ImgBB and returns a public URL"""
    url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": IMGBB_API_KEY,
        "image": base64.b64encode(image_file.getvalue()).decode("utf-8")
    }
    response = requests.post(url, data=payload)
    return response.json()['data']['url']

def send_admin_email(report_id, description, location):
    """Sends an email alert to the admin"""
    subject = f"🚨 URGENT: Wildlife Incident #{report_id} Reported"
    body = f"Incident ID: {report_id}\nLocation: {location}\nDescription: {description}\n\nPlease check the Security Portal."
    msg = MIMEText(body)
    msg['Subject'], msg['From'], msg['To'] = subject, GMAIL_SENDER, GMAIL_SENDER
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_SENDER, GMAIL_PASSWORD)
            server.sendmail(GMAIL_SENDER, GMAIL_SENDER, msg.as_string())
    except Exception as e:
        print(f"Email failed: {e}")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🐾 Wildlife Guard")
user_type = st.sidebar.radio("Login As:", ["Community User", "Admin / Security"])

# ==========================
# 1. COMMUNITY USER PORTAL
# ==========================
if user_type == "Community User":
    st.title("📢 Report a Dangerous or Injured Animal")

    img_file = st.camera_input("Take a Photo")
    use_gps = st.checkbox("Use my current GPS location", value=True)
    lat, long = (13.6288, 79.4192) if use_gps else (None, None)
    
    description = st.text_area("Description (e.g., 'Injured monkey')", height=100)
    contact = st.text_input("Your Contact Number")

    if st.button("🔴 SUBMIT REPORT"):
        if img_file is not None:
            with st.spinner('Uploading report to database...'):
                # 1. Upload Image to Cloud
                img_url = upload_image_to_cloud(img_file)
                
                # 2. Get next ID
                existing_records = sheet.get_all_records()
                report_id = len(existing_records) + 1
                
                # 3. Save to Google Sheets
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                location_str = f"{lat}, {long}" if lat else "Unknown"
                status = "🚨 Pending Action"
                
                new_row = [report_id, timestamp, location_str, description, contact, status, img_url]
                sheet.append_row(new_row)
                
                # 4. Trigger Email
                send_admin_email(report_id, description, location_str)
                
            st.success("✅ Report submitted to the central database successfully!")
            st.balloons()
        else:
            st.warning("Please take a photo to submit.")

    # Show Recent Alerts directly from Database
    st.divider()
    st.subheader("⚠️ Recent Alerts in Your Area")
    records = sheet.get_all_records()
    if not records:
        st.info("No active threats reported nearby.")
    else:
        # Show last 3 records
        for report in records[-3:][::-1]:
            col1, col2 = st.columns([1, 4])
            with col1:
                st.image(report['Image_URL'], width=100)
            with col2:
                st.warning(f"**{report['Description']}**")
                st.caption(f"📍 {report['Location']} | 🕒 {report['Timestamp']}")
                st.write(f"Status: **{report['Status']}**")

# ==========================
# 2. ADMIN / SECURITY PORTAL
# ==========================
elif user_type == "Admin / Security":
    st.title("🛡️ Security Command Center")
    password = st.sidebar.text_input("Admin Password", type="password")
    
    if password == "admin123":
        st.success("Connected to Live Database")
        
        # Fetch Live Data
        records = sheet.get_all_records()
        total = len(records)
        pending = sum(1 for r in records if "Pending" in r['Status'])
        
        c1, c2 = st.columns(2)
        c1.metric("Total Incidents", total)
        c2.metric("Pending Actions", pending, delta_color="inverse")

        st.divider()
        if not records:
            st.info("No incidents in database.")
        else:
            for i, report in enumerate(records[::-1]): # Show newest first
                with st.expander(f"🔴 Incident #{report['ID']}: {report['Description']} ({report['Status']})", expanded=True):
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.image(report['Image_URL'], use_container_width=True)
                    with col2:
                        st.write(f"**Location:** {report['Location']}")
                        st.write(f"**Time:** {report['Timestamp']}")
                        st.write(f"**Reporter:** {report['Contact']}")
                        
                        # Admin Status Update Logic
                        new_status = st.selectbox(
                            "Update Status", 
                            ["🚨 Pending Action", "⚠️ Rescue Team Dispatched", "✅ Resolved/Safe"], 
                            key=f"status_{report['ID']}",
                            index=["🚨 Pending Action", "⚠️ Rescue Team Dispatched", "✅ Resolved/Safe"].index(report['Status'])
                        )
                        
                        if new_status != report['Status']:
                            # Google Sheets is 1-indexed. Row 1 is headers.
                            # We need to find the correct row number to update
                            row_number = report['ID'] + 1 
                            # Column 6 is the Status column
                            sheet.update_cell(row_number, 6, new_status)
                            st.rerun()
    else:
        st.info("Please enter the admin password to access the database.")