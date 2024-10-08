import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import yagmail
import re
import time
import matplotlib.pyplot as plt

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

# Example image URLs (replace with actual URLs)
BREED_IMAGES = {
    "Dog": {
        "Labrador Retriever": "https://example.com/labrador.jpg",
        "German Shepherd": "https://example.com/german_shepherd.jpg",
        # Add other breeds...
    },
    "Cat": {
        "Siamese": "https://example.com/siamese.jpg",
        "Persian": "https://example.com/persian.jpg",
        # Add other breeds...
    },
    "Reptile": {
        "Bearded Dragon": "https://i.pinimg.com/originals/c2/0a/9a/c20a9a2451c3fc2c45281f69dab1e547.jpg",
        "Leopard Gecko": "https://wallpapercave.com/wp/9JtSjSW.jpg",
        # Add other breeds...
    }
}

# Initialize Streamlit
st.set_page_config(page_title="Animal Adoption System", page_icon="🐾", layout="wide")

# Custom CSS
st.markdown(
    """
    <style>
    .reportview-container {
        background-color: #f0f8ff;
    }
    .big-font {
        font-size:30px !important;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<p class='big-font'>🐶🐱 Animal Adoption System 🐰🦎</p>", unsafe_allow_html=True)

# Initialize Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=5)
def load_data():
    try:
        data = conn.read(worksheet=WORKSHEET_NAME, usecols=list(range(11)), ttl=5)
        return data if not data.empty else pd.DataFrame(columns=["First Name", "Last Name", "Email", "Street Address", "City", "State", "Zip", "Dog Breed", "Cat Breed", "Reptile Breed"])
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame(columns=["First Name", "Last Name", "Email", "Street Address", "City", "State", "Zip", "Dog Breed", "Cat Breed", "Reptile Breed"])

def send_confirmation_email(email, first_name, dog_breed, cat_breed, reptile_breed):
    selected_pets = []
    if dog_breed != "None":
        selected_pets.append(f"{PET_EMOJIS['Dog']} Dog: {dog_breed}")
    if cat_breed != "None":
        selected_pets.append(f"{PET_EMOJIS['Cat']} Cat: {cat_breed}")
    if reptile_breed != "None":
        selected_pets.append(f"{PET_EMOJIS['Reptile']} Reptile: {reptile_breed}")

    pet_info = "\n".join(selected_pets)

    subject = "Pet Adoption Application Confirmation"
    body = f"""
    Dear {first_name},

    Thank you for submitting your pet adoption application.
    We have received your application for the following:

    {pet_info}

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

def submit_application():
    with st.form("application_form"):
        st.markdown("### Contact Information")
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
        
        st.markdown("### Pet Information")
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
                    "Reptile Breed": reptile_breed
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
            st.markdown("### Review Your Application")
            for key, value in st.session_state.application_data.items():
                st.write(f"{key}: {value}")
            
            # Display selected breed images
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.session_state.application_data["Dog Breed"] != "None":
                    st.image(BREED_IMAGES["Dog"].get(st.session_state.application_data["Dog Breed"], "https://example.com/placeholder.jpg"), caption=st.session_state.application_data["Dog Breed"])
            with col2:
                if st.session_state.application_data["Cat Breed"] != "None":
                    st.image(BREED_IMAGES["Cat"].get(st.session_state.application_data["Cat Breed"], "https://example.com/placeholder.jpg"), caption=st.session_state.application_data["Cat Breed"])
            with col3:
                if st.session_state.application_data["Reptile Breed"] != "None":
                    st.image(BREED_IMAGES["Reptile"].get(st.session_state.application_data["Reptile Breed"], "https://example.com/placeholder.jpg"), caption=st.session_state.application_data["Reptile Breed"])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🐾 Confirm and Submit Application"):
                    new_data = pd.DataFrame([st.session_state.application_data])
                    updated_data = pd.concat([existing_data, new_data], ignore_index=True)
                    
                    try:
                        with st.spinner("Submitting your application..."):
                            conn.update(worksheet=WORKSHEET_NAME, data=updated_data)
                            for i in range(100):
                                time.sleep(0.02)
                                st.progress(i + 1)
                        st.success("🎉 Application sent to Admin! We'll be in touch soon. 🐾")
                        st.session_state.application_submitted = True
                        
                        if send_confirmation_email(st.session_state.application_data["Email"], 
                                                   st.session_state.application_data["First Name"],
                                                   st.session_state.application_data["Dog Breed"],
                                                   st.session_state.application_data["Cat Breed"],
                                                   st.session_state.application_data["Reptile Breed"]):
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

    # Display chart of applications by pet type
    st.markdown("### Application Statistics")
    pet_types = ['Dog', 'Cat', 'Reptile']
    applications = [
        len(existing_data[existing_data['Dog Breed'] != 'None']),
        len(existing_data[existing_data['Cat Breed'] != 'None']),
        len(existing_data[existing_data['Reptile Breed'] != 'None'])
    ]

    fig, ax = plt.subplots()
    ax.bar(pet_types, applications)
    ax.set_title('Applications by Pet Type')
    ax.set_xlabel('Pet Type')
    ax.set_ylabel('Number of Applications')
    st.pyplot(fig)

if __name__ == "__main__":
    main()
