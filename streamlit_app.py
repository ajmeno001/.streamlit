import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Title and Description
st.title("🐶🐱 Pet Adoption Application 🐰🐦")
st.markdown("Enter your application details below to give a furry friend a forever home! 🏠💖")

# Establishing connection to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

WORKSHEET_NAME = "PET"

@st.cache_data(ttl=5)
def load_data():
    try:
        data = conn.read(worksheet=WORKSHEET_NAME, usecols=list(range(7)), ttl=5)
        return data if not data.empty else pd.DataFrame(columns=["First Name", "Last Name", "Email", "Street Address", "City", "State", "Zip"])
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame(columns=["First Name", "Last Name", "Email", "Street Address", "City", "State", "Zip"])

existing_data = load_data()

def submit_application():
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
        
        submitted = st.form_submit_button("🐾 Submit Application")

        if submitted:
            new_data = pd.DataFrame({
                "First Name": [first_name],
                "Last Name": [last_name],
                "Email": [email],
                "Street Address": [street_address],
                "City": [city],
                "State": [state],
                "Zip": [zip_code]
            })
            
            # Get existing data
            existing_data = load_data()
            
            # Append new data to existing data
            updated_data = pd.concat([existing_data, new_data], ignore_index=True)
            
            try:
                # Update the Google Sheet
                conn.update(worksheet=WORKSHEET_NAME, data=updated_data)
                st.success("🎉 Application sent to Admin! We'll be in touch soon. 🐾")
                st.session_state.application_submitted = True
                st.balloons()
            except Exception as e:
                st.error(f"Error submitting application: {str(e)}")

if 'application_submitted' not in st.session_state:
    st.session_state.application_submitted = False

if not st.session_state.application_submitted:
    submit_application()
else:
    if st.button("🆕 Enter New Application"):
        st.session_state.application_submitted = False
        st.rerun()

# Uncomment these lines if you want to display existing applications
# st.subheader("🐾 Existing Applications")
# st.dataframe(existing_data)
