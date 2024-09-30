import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
    # ... (keep the email sending function as is)

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
        
        pet_type = st.selectbox("Select Pet Type", ["Dog", "Cat", "Reptile"])

        if pet_type == "Dog":
            pet_breed = st.selectbox("Dog Breed", breed_options["Dog"])
        elif pet_type == "Cat":
            pet_breed = st.selectbox("Cat Breed", breed_options["Cat"])
        else:
            pet_breed = st.selectbox("Reptile Breed", breed_options["Reptile"])

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

    # This is outside the form
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
                
                # Send confirmation email
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
