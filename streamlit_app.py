import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import yagmail
import re
import random
from datetime import datetime, timedelta

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

# Pet names for randomizer
PET_NAMES = [
    "Buddy", "Max", "Charlie", "Lucy", "Bailey", "Cooper",
    # ... (rest of the names)
]

# Initialize Streamlit
st.set_page_config(page_title="Animal Adoption System", page_icon="🐾", layout="wide")
st.title("🐶🐱 Animal Adoption System 🐰🦎")

# Initialize Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=5)
def load_data():
    try:
        data = conn.read(worksheet=WORKSHEET_NAME, usecols=list(range(14)), ttl=5)
        return data if not data.empty else pd.DataFrame(columns=["First Name", "Last Name", "Email", "Street Address", "City", "State", "Zip", "Pet Type", "Pet Breed", "Pet Name", "Pet DOB", "Pet Weight"])
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame(columns=["First Name", "Last Name", "Email", "Street Address", "City", "State", "Zip", "Pet Type", "Pet Breed", "Pet Name", "Pet DOB", "Pet Weight"])

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

def get_random_pet_details():
    name = random.choice(PET_NAMES)
    dob = (datetime.now() - timedelta(days=random.randint(180, 1825))).strftime("%Y-%m-%d")
    weight = round(random.uniform(5, 50), 1)
    return name, dob, weight

def display_pet_options(pet_type):
    st.subheader(f"Available {pet_type}s")
    col1, col2, col3 = st.columns(3)
    
    pets = [
        {"breed": f"{pet_type} Breed 1", "image": "https://wallpapers-all.com/uploads/posts/2016-11/19_dog.jpg"},
        {"breed": f"{pet_type} Breed 2", "image": "https://wallpapers-all.com/uploads/posts/2016-11/19_dog.jpg"},
        {"breed": f"{pet_type} Breed 3", "image": "https://wallpapers-all.com/uploads/posts/2016-11/19_dog.jpg"}
    ]
    
    for i, pet in enumerate(pets):
        with [col1, col2, col3][i]:
            # Replace 'IMAGE_URL_X' with actual JPG links
            st.image(pet["image"], caption=pet["breed"], use_column_width=True)
            if st.button(f"Select {pet['breed']}", key=f"{pet_type}_{i}"):
                name, dob, weight = get_random_pet_details()
                st.session_state.selected_pet = {
                    "Type": pet_type,
                    "Breed": pet["breed"],
                    "Name": name,
                    "DOB": dob,
                    "Weight": weight
                }
                st.success(f"You've selected a {pet['breed']}!")

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
        
        st.title("Pet Information")
        st.subheader("Select the type of pet and breed you wish to adopt.")
        dog_breed = st.selectbox("Select Dog Breed 🐶", BREED_OPTIONS["Dog"], key="dog_breed")
        cat_breed = st.selectbox("Select Cat Breed 🐱", BREED_OPTIONS["Cat"], key="cat_breed")
        reptile_breed = st.selectbox("Select Reptile Breed 🦎", BREED_OPTIONS["Reptile"], key="reptile_breed")

        submitted = st.form_submit_button("Submit Application")

        if submitted:
            if not all([first_name, last_name, email, street_address, city, state, zip_code]):
                st.error("Please fill in all fields.")
            elif not validate_email(email):
                st.error("Please enter a valid email address.")
            elif not validate_zip_code(zip_code):
                st.error("Please enter a valid 5-digit zip code.")
            elif dog_breed == "None" and cat_breed == "None" and reptile_breed == "None":
                st.error("Please select at least one pet breed.")
            else:
                st.session_state.application_data = {
                    "First Name": first_name,
                    "Last Name": last_name,
                    "Email": email,
                    "Street Address": street_address,
                    "City": city,
                    "State": state,
                    "Zip": zip_code,
                    "Dog Breed": dog_breed,
                    "Cat Breed": cat_breed,
                    "Reptile Breed": reptile_breed,
                    "Dog Name": get_random_pet_name() if dog_breed != "None" else None,
                    "Cat Name": get_random_pet_name() if cat_breed != "None" else None,
                    "Reptile Name": get_random_pet_name() if reptile_breed != "None" else None
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
                pet_info = ["Pet Type", "Pet Breed", "Pet Name", "Pet DOB", "Pet Weight"]
                for key in pet_info:
                    st.write(f"{key}: {st.session_state.application_data[key]}")
            
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
                                                   st.session_state.application_data["Pet Type"],
                                                   st.session_state.application_data["Pet Breed"],
                                                   st.session_state.application_data["Pet Name"]):
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
            st.session_state.pop('selected_pet', None)
            st.rerun()

if __name__ == "__main__":
    main()
