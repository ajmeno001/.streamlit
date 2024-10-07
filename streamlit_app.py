import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

st.title("🐶🐱 Animal Adoption System 🐰🦎")

conn = st.connection("gsheets", type=GSheetsConnection)

WORKSHEET_NAME = "PET"

@st.cache_data(ttl=5)
def load_data():
    try:
        data = conn.read(worksheet=WORKSHEET_NAME, usecols=list(range(9)), ttl=5)
        return data if not data.empty else pd.DataFrame(columns=["First Name", "Last Name", "Email", "Street Address", "City", "State", "Zip", "Pet Type", "Pet Breed"])
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame(columns=["First Name", "Last Name", "Email", "Street Address", "City", "State", "Zip", "Pet Type", "Pet Breed"])

existing_data = load_data()

def send_confirmation_email(email, first_name, pet_type, pet_breed):
    # Use environment variables for sensitive information
    sender_email = os.environ.get("SENDER_EMAIL", "menofinance2022@outlook.com")
    sender_password = os.environ.get("SENDER_PASSWORD", "USDcad23!!")
    
    pet_emojis = {
        "Dog": "🐶",
        "Cat": "🐱",
        "Reptile": "🦎"
    }
    pet_emoji = pet_emojis.get(pet_type, "")
    
    subject = "Pet Adoption Application Confirmation"
    body = f"""
    Dear {first_name},

    Thank you for submitting your pet adoption application for a {pet_emoji} {pet_breed} {pet_type}. 
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
        with smtplib.SMTP_SSL('smtp.office365.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Error sending confirmation email: {str(e)}")
        print(f"Detailed error: {e}")  # This will print to your console/logs
        return False

def update_breed_options():
    pet_type = st.session_state.pet_type
    breed_options = {
        "Dog": ["Labrador Retriever", "German Shepherd", "Golden Retriever", "Bulldog", "Beagle", "Poodle", "Rottweiler", "Boxer", "Dachshund", "Siberian Husky"],
        "Cat": ["Siamese", "Persian", "Maine Coon", "Sphynx", "Bengal", "British Shorthair", "Scottish Fold", "Ragdoll", "Russian Blue", "American Shorthair"],
        "Reptile": ["Bearded Dragon", "Leopard Gecko", "Ball Python", "Corn Snake", "Green Iguana", "Blue-Tongued Skink", "Crested Gecko", "Red-Eared Slider", "Chameleon", "Tortoise"]
    }
    st.session_state.pet_breed = breed_options[pet_type][0]

def submit_application():
    if 'pet_type' not in st.session_state:
        st.session_state.pet_type = "Dog"
    
    breed_options = {
        "Dog": ["Labrador Retriever", "German Shepherd", "Golden Retriever", "Bulldog", "Beagle", "Poodle", "Rottweiler", "Boxer", "Dachshund", "Siberian Husky"],
        "Cat": ["Siamese", "Persian", "Maine Coon", "Sphynx", "Bengal", "British Shorthair", "Scottish Fold", "Ragdoll", "Russian Blue", "American Shorthair"],
        "Reptile": ["Bearded Dragon", "Leopard Gecko", "Ball Python", "Corn Snake", "Green Iguana", "Blue-Tongued Skink", "Crested Gecko", "Red-Eared Slider", "Chameleon", "Tortoise"]
    }

    with st.form("application_form"):
        st.subheader("Contact Information")
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
        
        st.subheader("Pet Information")
        st.write("### What type of Pet do you want?")
        pet_type = st.radio("Select Pet Type", ["Dog", "Cat", "Reptile"], key="pet_type")

        st.write("### What Breed of Pet do you Want?")
        pet_breed = st.selectbox("Select Breed", breed_options[pet_type], key="pet_breed")

        submitted = st.form_submit_button("Submit Application")

        if submitted:
            st.session_state.application_data = {
                "First Name": first_name,
                "Last Name": last_name,
                "Email": email,
                "Street Address": street_address,
                "City": city,
                "State": state,
                "Zip": zip_code,
                "Pet Type": pet_type,
                "Pet Breed": pet_breed
            }
            st.session_state.review_stage = True

    if submitted:
        st.success("Application submitted successfully!")
        st.write("Review your application:")
        for key, value in st.session_state.application_data.items():
            st.write(f"{key}: {value}")
            
if 'pet_type' not in st.session_state:
    st.session_state.pet_type = "Dog"

if 'review_stage' not in st.session_state:
    st.session_state.review_stage = False

if 'application_submitted' not in st.session_state:
    st.session_state.application_submitted = False

if not st.session_state.application_submitted:
    if not st.session_state.review_stage:
        submit_application()
    else:
        st.subheader("Review Your Application")
        for key, value in st.session_state.application_data.items():
            st.write(f"{key}: {value}")
        
        if st.button("🐾 Confirm and Submit Application"):
            new_data = pd.DataFrame([st.session_state.application_data])
            existing_data = load_data()
            updated_data = pd.concat([existing_data, new_data], ignore_index=True)
            
            try:
                conn.update(worksheet=WORKSHEET_NAME, data=updated_data)
                st.success("🎉 Application sent to Admin! We'll be in touch soon. 🐾")
                st.session_state.application_submitted = True
                
                if send_confirmation_email(st.session_state.application_data["Email"], 
                                           st.session_state.application_data["First Name"],
                                           st.session_state.application_data["Pet Type"],
                                           st.session_state.application_data["Pet Breed"]):
                    st.success("Confirmation email sent!")
                else:
                    st.warning("Confirmation email could not be sent. Please check your email address.")
                
                st.balloons()
            except Exception as e:
                st.error(f"Error submitting application: {str(e)}")
        
        if st.button("Edit Application"):
            st.session_state.review_stage = False
            st.rerun()
else:
    if st.button("🆕 Enter New Application"):
        st.session_state.application_submitted = False
        st.session_state.review_stage = False
        st.rerun()

# Uncomment these lines if you want to display existing applications
# st.subheader("🐾 Existing Applications")
# st.dataframe(existing_data)
