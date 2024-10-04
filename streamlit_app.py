import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

st.title("🐶🐱 Pet Adoption Application 🐰🦎")
st.markdown("Enter your application details below to give a furry (or scaly) friend a forever home! 🏠💖")

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
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD")
    
    if not sender_email or not sender_password:
        st.error("Sender email or password not set in environment variables.")
        return False
    
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
        
        breed_options = {
            "Dog": ["Labrador Retriever", "German Shepherd", "Golden Retriever", "Bulldog", "Beagle", "Poodle", "Rottweiler", "Boxer", "Dachshund", "Siberian Husky"],
            "Cat": ["Siamese", "Persian", "Maine Coon", "Sphynx", "Bengal", "British Shorthair", "Scottish Fold", "Ragdoll", "Russian Blue", "American Shorthair"],
            "Reptile": ["Bearded Dragon", "Leopard Gecko", "Ball Python", "Corn Snake", "Green Iguana", "Blue-Tongued Skink", "Crested Gecko", "Red-Eared Slider", "Chameleon", "Tortoise"]
        }

        st.write("## Select Pet Type and Breed")
        
        col3, col4, col5 = st.columns(3)
        
        with col3:
            st.write("### 🐶 Dogs")
            dog_breed = st.selectbox("Dog Breed", breed_options["Dog"], key="dog_breed")
        
        with col4:
            st.write("### 🐱 Cats")
            cat_breed = st.selectbox("Cat Breed", breed_options["Cat"], key="cat_breed")
        
        with col5:
            st.write("### 🦎 Reptiles")
            reptile_breed = st.selectbox("Reptile Breed", breed_options["Reptile"], key="reptile_breed")

        pet_type = st.radio("Select Pet Type", ["Dog", "Cat", "Reptile"])

        if pet_type == "Dog":
            pet_breed = dog_breed
        elif pet_type == "Cat":
            pet_breed = cat_breed
        else:
            pet_breed = reptile_breed

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
