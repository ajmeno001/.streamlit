import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Set up Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Read data from Google Sheet
df = conn.read(worksheet="PET", usecols=list(range(9)), ttl=5)

st.title("🐶🐱 Pet Adoption Application 🐰🦎")
st.markdown("Enter your application details below to give a furry (or scaly) friend a forever home! 🏠💖")

# Application form
with st.form("application_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        email = st.text_input("Email")
    with col2:
        street_address = st.text_input("Street Address")
        city = st.text_input("City")
        state = st.text_input("State")
        zip_code = st.text_input("Zip")
    
    pet_type = st.selectbox("Pet Type", ["Dog", "Cat", "Reptile"])
    pet_breed = st.text_input("Pet Breed")
    
    submitted = st.form_submit_button("Submit Application")

if submitted:
    # Add new application to dataframe
    new_application = pd.DataFrame({
        "First Name": [first_name],
        "Last Name": [last_name],
        "Email": [email],
        "Street Address": [street_address],
        "City": [city],
        "State": [state],
        "Zip": [zip_code],
        "Pet Type": [pet_type],
        "Pet Breed": [pet_breed]
    })
    
    updated_df = pd.concat([df, new_application], ignore_index=True)
    
    # Update Google Sheet
    conn.update(worksheet="PET", data=updated_df)
    
    # Send confirmation email
    sender_email = st.secrets["SENDER_EMAIL"]
    sender_password = st.secrets["SENDER_PASSWORD"]
    
    subject = "Pet Adoption Application Confirmation"
    body = f"""
    Dear {first_name},

    Thank you for submitting your pet adoption application for a {pet_breed} {pet_type}. 
    We have received your application and will review it shortly.

    Best regards,
    The Pet Adoption Team
    """
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        with smtplib.SMTP('smtp.office365.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        st.success("Application submitted and confirmation email sent!")
    except Exception as e:
        st.error(f"Error sending confirmation email: {str(e)}")

# Display existing applications
st.subheader("Existing Applications")
st.dataframe(df)
