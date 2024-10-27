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
        {"breed": "Labrador Retriever", "name": "Buddy", "age": "2 years", "image": "https://3.bp.blogspot.com/-iX1ck5IPomE/Te8fiT-40GI/AAAAAAAAHVM/coJFdrPp2Vg/s1600/labrador-retriever-dog.jpg", "size": (25, 10)},
        {"breed": "German Shepherd", "name": "Max", "age": "3 years", "image": "https://pawinterest.com/wp-content/uploads/2020/11/16059481018p4cl.jpg", "size": (100, 75)},
        {"breed": "Golden Retriever", "name": "Charlie", "age": "1 year", "image": "https://goldenhearts.co/wp-content/uploads/2021/01/golden-retriever-2166211_1280-1024x678.jpg", "size": (300, 200)},
    ],
    "Cat": [
        {"breed": "Siamese", "name": "Luna", "age": "4 years", "image": "https://fishsubsidy.org/wp-content/uploads/2020/01/siamese-cat-health.jpg", "size": (300, 200)},
        {"breed": "Persian", "name": "Bella", "age": "2 years", "image": "https://media.cnn.com/api/v1/images/stellar/prod/181101165831-15-week-in-photos-1102-restricted.jpg?q=w_2000,h_1125,x_0,y_0,c_fill/h_778", "size": (300, 200)},
        {"breed": "Maine Coon", "name": "Oliver", "age": "3 years", "image": "https://upload.wikimedia.org/wikipedia/commons/5/57/Cat-MaineCoon-Lucy.png", "size": (300, 200)},
    ],
    "Reptile": [
        {"breed": "Bearded Dragon", "name": "Spike", "age": "1 year", "image": "https://farm4.staticflickr.com/3361/3224850521_16237541eb_z.jpg", "size": (300, 200)},
        {"breed": "Leopard Gecko", "name": "Spots", "age": "2 years", "image": "https://live.staticflickr.com/6102/6328338235_ea33556210.jpg", "size": (300, 200)},
        {"breed": "Ball Python", "name": "Slinky", "age": "3 years", "image": "https://c1.staticflickr.com/9/8183/8383675583_9ceac5ca1b_b.jpg", "size": (300, 200)},
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
        st.markdown("<h1 style='text-align: center;'>Pet Adoption Application Form</h1>", unsafe_allow_html=True)
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
        st.subheader("Choose a pet to adopt")
        
        col_dog, col_cat, col_reptile = st.columns(3)
        
        selected_pet = None
        
        with col_dog:
            st.header("Dogs 🐶")
            for pet in PETS["Dog"]:
                st.image(pet["image"], caption=pet["breed"], use_column_width=True)
                st.write(f"**Name:** {pet['name']}")
                st.write(f"**Breed:** {pet['breed']}")
                st.write(f"**Age:** {pet['age']}")
                if st.checkbox(f"Select {pet['name']}", key=f"Dog_{pet['name']}"):
                    selected_pet = {"Type": "Dog", **pet}
                st.write("---")
        
        with col_cat:
            st.header("Cats 🐱")
            for pet in PETS["Cat"]:
                st.image(pet["image"], caption=pet["breed"], use_column_width=True)
                st.write(f"**Name:** {pet['name']}")
                st.write(f"**Breed:** {pet['breed']}")
                st.write(f"**Age:** {pet['age']}")
                if st.checkbox(f"Select {pet['name']}", key=f"Cat_{pet['name']}"):
                    selected_pet = {"Type": "Cat", **pet}
                st.write("---")
        
        with col_reptile:
            st.header("Reptiles 🦎")
            for pet in PETS["Reptile"]:
                st.image(pet["image"], caption=pet["breed"], use_column_width=True)
                st.write(f"**Name:** {pet['name']}")
                st.write(f"**Breed:** {pet['breed']}")
                st.write(f"**Age:** {pet['age']}")
                if st.checkbox(f"Select {pet['name']}", key=f"Reptile_{pet['name']}"):
                    selected_pet = {"Type": "Reptile", **pet}
                st.write("---")

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
                    "Pet Type": selected_pet["Type"],
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
                pet_info = ["Pet Type", "Pet Breed", "Pet Name", "Pet Age"]
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
            st.session_state.pop('application_data', None)
            st.rerun()

if __name__ == "__main__":
    main()
