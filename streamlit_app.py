import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import yagmail
import re

# Configuration
WORKSHEET_NAME = "PET"
SENDER_EMAIL = "petadoptionteam4@gmail.com"
APP_PASSWORD = "uwdg bcvt fzcf dcbs"

# Emoji mappings
PET_EMOJIS = {
    "Dog": "🐶",
    "Cat": "🐱",
    "Reptile": "🦎"
}

# Pet information
PETS = {
    "Dog": [
        {"breed": "Labrador Retriever", "name": "Buddy", "age": "2 years", "image": "https://example.com/labrador.jpg"},
        {"breed": "German Shepherd", "name": "Max", "age": "3 years", "image": "https://example.com/german_shepherd.jpg"},
        {"breed": "Golden Retriever", "name": "Charlie", "age": "1 year", "image": "https://example.com/golden_retriever.jpg"},
    ],
    "Cat": [
        {"breed": "Siamese", "name": "Luna", "age": "4 years", "image": "https://example.com/siamese.jpg"},
        {"breed": "Persian", "name": "Bella", "age": "2 years", "image": "https://example.com/persian.jpg"},
        {"breed": "Maine Coon", "name": "Oliver", "age": "3 years", "image": "https://example.com/maine_coon.jpg"},
    ],
    "Reptile": [
        {"breed": "Bearded Dragon", "name": "Spike", "age": "1 year", "image": "https://example.com/bearded_dragon.jpg"},
        {"breed": "Leopard Gecko", "name": "Spots", "age": "2 years", "image": "https://example.com/leopard_gecko.jpg"},
        {"breed": "Ball Python", "name": "Slinky", "age": "3 years", "image": "https://example.com/ball_python.jpg"},
    ]
}

# Initialize Streamlit
st.set_page_config(page_title="Animal Adoption System", page_icon="🐾", layout="wide")
st.title("🐶🐱 Animal Adoption System 🐰🦎")

# Initialize Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=5)
def load_data():
    try:
        data = conn.read(worksheet=WORKSHEET_NAME, usecols=list(range(11)), ttl=5)
        return data if not data.empty else pd.DataFrame(columns=["First Name", "Last Name", "Email", "Street Address", "City", "State", "Zip", "Pet Type", "Pet Breed", "Pet Name", "Pet Age"])
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame(columns=["First Name", "Last Name", "Email", "Street Address", "City", "State", "Zip", "Pet Type", "Pet Breed", "Pet Name", "Pet Age"])

def send_confirmation_email(email, first_name, pet_type, pet_breed, pet_name):
    subject = "Pet Adoption Application Confirmation"
    body = f"""
    Dear {first_name},

    Thank you for submitting your pet adoption application.
    We have received your application for the following:

    {PET_EMOJIS[pet_type]} {pet_type}: {pet_breed} (Name: {pet_name})

    We will review it shortly.

    Best regards,
    The Pet Adoption Team
    """
    
    try:
        yag = yagmail.SMTP(SENDER_EMAIL, APP_PASSWORD)
        yag.send(
            to=email,
            subject=subject,
            contents=body
        )
        return True
    except Exception as e:
        st.error(f"Error sending confirmation email: {str(e)}")
        return False

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_zip_code(zip_code):
    return len(zip_code) == 5 and zip_code.isdigit()

def display_pet_options():
    st.subheader("Available Pets")
    pet_type = st.radio("Select Pet Type", ["Dog", "Cat", "Reptile"])
    
    for pet in PETS[pet_type]:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(pet["image"], caption=pet["breed"], use_column_width=True)
        with col2:
            st.write(f"**Name:** {pet['name']}")
            st.write(f"**Breed:** {pet['breed']}")
            st.write(f"**Age:** {pet['age']}")
            if st.button(f"Select {pet['name']}", key=f"{pet_type}_{pet['name']}"):
                st.session_state.selected_pet = {
                    "Type": pet_type,
                    "Breed": pet["breed"],
                    "Name": pet["name"],
                    "Age": pet["age"]
                }
                st.success(f"You've selected {pet['name']}!")

def submit_application():
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
        
        st.title("Pet Selection")
        st.subheader("Select a pet type and then choose a pet to adopt.")
        
        pet_type = st.radio("Select Pet Type", ["Dog", "Cat", "Reptile"])
        
        selected_pet = None
        for pet in PETS[pet_type]:
            col1, col2 = st.columns([1, 3])
            with col1:
                st.image(pet["image"], caption=pet["breed"], use_column_width=True)
            with col2:
                st.write(f"**Name:** {pet['name']}")
                st.write(f"**Breed:** {pet['breed']}")
                st.write(f"**Age:** {pet['age']}")
                if st.checkbox(f"Select {pet['name']}", key=f"{pet_type}_{pet['name']}"):
                    selected_pet = pet

        submitted = st.form_submit_button("Submit Application")

        if submitted:
            if not all([first_name, last_name, email, street_address, city, state, zip_code]):
                st.error("Please fill in all fields.")
            elif not validate_email(email):
                st.error("Please enter a valid email address.")
            elif not validate_zip_code(zip_code):
                st.error("Please enter a valid 5-digit zip code.")
            elif selected_pet is None:
                st.error("Please select a pet for adoption.")
            else:
                st.session_state.application_data = {
                    "First Name": first_name,
                    "Last Name": last_name,
                    "Email": email,
                    "Street Address": street_address,
                    "City": city,
                    "State": state,
                    "Zip": zip_code,
                    "Pet Type": pet_type,
                    "Pet Breed": selected_pet["breed"],
                    "Pet Name": selected_pet["name"],
                    "Pet Age": selected_pet["age"]
                }
                st.session_state.review_stage = True
                st.rerun()

def main():
    existing_data = load_data()

    if 'review_stage' not in st.session_state:
        st.session_state.review_stage = False

    if 'application_submitted' not in st.session_state:
        st.session_state.application_submitted = False

    if not st.session_state.application_submitted:
        if not st.session_state.review_stage:
            submit_application()
        else:
            st.subheader("Application Summary")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("### Contact Information")
                contact_info = ["First Name", "Last Name", "Email", "Street Address", "City", "State", "Zip"]
                for key in contact_info:
                    st.write(f"{key}: {st.session_state.application_data[key]}")
            
            with col2:
                st.write("### Pet Information")
                pet_info = [("Dog", "Dog Breed", "Dog Name"), ("Cat", "Cat Breed", "Cat Name"), ("Reptile", "Reptile Breed", "Reptile Name")]
                for pet_type, breed_key, name_key in pet_info:
                    if st.session_state.application_data[breed_key] != "None":
                        st.write(f"**{pet_type}**")
                        st.write(f"Breed: {st.session_state.application_data[breed_key]}")
                        st.write(f"Name: {st.session_state.application_data[name_key]}")
                        
                        # Display the pet's image
                        pet_image = PETS[pet_type][st.session_state.application_data[breed_key]]["image"]
                        st.image(pet_image, caption=f"{st.session_state.application_data[name_key]} - {st.session_state.application_data[breed_key]}", use_column_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🐾 Confirm and Submit Application"):
                    new_data = pd.DataFrame([st.session_state.application_data])
                    updated_data = pd.concat([existing_data, new_data], ignore_index=True)
                    
                    try:
                        conn.update(worksheet=WORKSHEET_NAME, data=updated_data)
                        st.success("🎉 Application sent to Admin! We'll be in touch soon. 🐾")
                        st.session_state.application_submitted = True
                        
                        if send_confirmation_email(st.session_state.application_data["Email"], 
                                                   st.session_state.application_data["First Name"],
                                                   st.session_state.application_data["Dog Breed"],
                                                   st.session_state.application_data["Cat Breed"],
                                                   st.session_state.application_data["Reptile Breed"],
                                                   st.session_state.application_data["Dog Name"],
                                                   st.session_state.application_data["Cat Name"],
                                                   st.session_state.application_data["Reptile Name"]):
                            st.success("Confirmation email sent!")
                        else:
                            st.warning("Confirmation email could not be sent. Please check your email address.")
                        
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error submitting application: {str(e)}")
            with col2:
                if st.button("Edit Application"):
                    st.session_state.review_stage = False
                    st.rerun()
    else:
        st.success("Your application has been submitted successfully!")
        if st.button("🆕 Enter New Application"):
            st.session_state.application_submitted = False
            st.session_state.review_stage = False
            st.rerun()
