import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import yagmail
import re
import random
from PIL import Image
import requests
from io import BytesIO

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

# Updated breed options
BREED_OPTIONS = {
    "Dog": ["None", "Labrador Retriever", "German Shepherd", "Golden Retriever", "Bulldog", "Beagle", "Poodle", "Rottweiler", "Boxer", "Dachshund", "Siberian Husky"],
    "Cat": ["None", "Siamese", "Persian", "Maine Coon", "Sphynx", "Bengal", "British Shorthair", "Scottish Fold", "Ragdoll", "Russian Blue", "American Shorthair"],
    "Reptile": ["None", "Bearded Dragon", "Leopard Gecko", "Ball Python", "Corn Snake", "Green Iguana", "Blue-Tongued Skink", "Crested Gecko", "Red-Eared Slider", "Chameleon", "Tortoise"]
}

# Pet names for randomizer
PET_NAMES = [
    # Add a list of pet names here...
]

# Initialize Streamlit
st.set_page_config(page_title="Animal Adoption System", page_icon="🐾", layout="wide")
st.title("🐶🐱 Animal Adoption System 🐰🦎")

# Initialize Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=5)
def load_data():
    try:
        data = conn.read(worksheet=WORKSHEET_NAME, usecols=list(range(15)), ttl=5)
        return data if not data.empty else pd.DataFrame(columns=["First Name",
                                                                 # Add other columns here...
                                                                 ])
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame(columns=["First Name",
                                     # Add other columns here...
                                     ])

def send_confirmation_email(email, first_name, dog_breed, cat_breed, reptile_breed, dog_name, cat_name, reptile_name):
    # Email sending logic...
    pass

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_zip_code(zip_code):
    return len(zip_code) == 5 and zip_code.isdigit()

def get_random_pet_name():
    return random.choice(PET_NAMES)

def display_pet_images(data):
    for index, row in data.iterrows():
        # Fetch and display image if available
        if 'Image URL' in row and row['Image URL']:
            response = requests.get(row['Image URL'])
            img = Image.open(BytesIO(response.content))
            st.image(img, caption=f"{row['Dog Breed']} - {row['Dog Name']}", use_column_width=True)
        
        # Display pet details below the image
        st.write(f"Breed: {row['Dog Breed']}")
        st.write(f"Name: {row['Dog Name']}")

def submit_application():
    with st.form("application_form"):
        # Form input logic...
        pass

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
            # Review stage logic...
            display_pet_images(existing_data)
            
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

if __name__ == "__main__":
    main()
