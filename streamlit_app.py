import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import yagmail
import re
import random

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
    "Buddy", "Max", "Charlie", "Lucy", "Bailey", "Cooper",
    "Daisy", "Luna", "Rocky", "Molly", "Jack",
    "Sadie", "Toby", "Chloe", "Lola",
    "Bear", "Duke", "Bella", "Oliver", "Sophie",
    "Maggie", "Rusty", "Zoe", "Gizmo", "Duke",
    "Roxy", "Teddy", "Winston", "Jasper", "Nala",
    "Coco", "Shadow", "Sasha", "Harley", "Simba",
    "Pepper", "Misty", "Sandy", "Rufus", "Rosie",
    "Finn", "Koda", "Chester", "Penny", "Apollo",
    "Milo", "Ruby", "Bandit", "Moose", "Lola",
    "Thor", "Cleo", "Buster", "Jax", "Ginger",
    "Willow", "Ollie", "Tucker", "Piper", "Cinnamon",
    "Scout", "Gus", "Honey", "Riley", "Chico",
    "Marley", "Ziggy", "Fiona", "Samantha", "Baxter",
    "Annie", "Benny", "Sophie", "Maggie", "Murphy",
    "Roscoe", "Lily", "Beau", "Maddie", "Ranger",
    "Peanut", "Fido", "Sasha", "Hank", "Daisy",
    "Yuki", "Cosmo", "Nina", "Pablo", "Milo",
    "Boomer", "Toby", "Rocco", "Sophie", "Coco",
    "Sparky", "Kiki", "Teddy", "Dobby", "Gizmo",
    "Rascal", "Juno", "Leo", "Jasper", "Zara",
    "Chester", "Nemo", "Willow", "Tango", "Freya",
    "Toby", "Coco", "Frankie", "Holly", "Nala",
    "Sunny", "Pippin", "Scout", "Skye", "Cuddles",
    "Bella", "Nugget", "Peanut", "Waffles", "Chester",
    "Snickers", "Mochi", "Socks", "Tater Tot", "Pumpkin",
    "Muffin", "Twix", "Snickerdoodle", "Cupcake", "Brownie",
    "Cookie Dough", "Marshmallow", "Sprinkles", "Biscuit",
    "Truffle", "Pudding", "Cheesecake", "Fudge", "Caramel",
    "Toffee", "Peaches", "Cherry", "S'mores", "Honeybun",
    "Whiskers", "Paws", "Fluffy", "Fuzzy", "Snuggles",
    "Cuddly", "Lovey", "Sweetheart", "Darling", "Angel",
    "Precious", "Lovebug", "Sugarplum", "Buttercup", "Doodle",
    "Dumpling", "Snickerdoodle", "Cupcake", "Kitty Cat",
    "Puppy Love", "Sweet Pea", "Little One", "Baby Cakes",
    "Boo Boo", "Sweet Cheeks", "Honey Bear", "Angel Eyes",
    "Lucky", "Nibbles", "Bubbles", "Pudding", "Biscuit",
    "Wiggles", "Chompers", "Sprout", "Snickers", "Nibbler",
    "Skittles", "Pickles", "Twinkie", "Tater", "Pudding Pop",
    "Peanut Butter", "Cotton Candy", "Gummy Bear", "Marshmallow Fluff",
    "Snickers Bar", "Twinkies", "Cinnamon Roll", "Sugar Cookie",
    "Butterscotch", "Honey Bunches", "Lollipop", "Cherry Pie",
    "Caramel Swirl", "Chocolate Chip", "Vanilla Bean",
    "Pumpkin Spice", "Peach Cobbler", "Blueberry Muffin",
    "Banana Split", "Cheesecake Factory", "Nutmeg", "Basil"
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
        return data if not data.empty else pd.DataFrame(columns=["First Name", "Last Name", "Email", "Street Address", "City", "State", "Zip", "Dog Breed", "Cat Breed", "Reptile Breed", "Dog Name", "Cat Name", "Reptile Name"])
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame(columns=["First Name", "Last Name", "Email", "Street Address", "City", "State", "Zip", "Dog Breed", "Cat Breed", "Reptile Breed", "Dog Name", "Cat Name", "Reptile Name"])

def send_confirmation_email(email, first_name, dog_breed, cat_breed, reptile_breed, dog_name, cat_name, reptile_name):
    selected_pets = []
    if dog_breed != "None":
        selected_pets.append(f"{PET_EMOJIS['Dog']} Dog: {dog_breed} (Name: {dog_name})")
    if cat_breed != "None":
        selected_pets.append(f"{PET_EMOJIS['Cat']} Cat: {cat_breed} (Name: {cat_name})")
    if reptile_breed != "None":
        selected_pets.append(f"{PET_EMOJIS['Reptile']} Reptile: {reptile_breed} (Name: {reptile_name})")

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

def get_random_pet_name():
    return random.choice(PET_NAMES)

def display_pet_options(pet_type):
    st.subheader(f"Available {pet_type}s")
    col1, col2, col3 = st.columns(3)
    
    for i, breed in enumerate(BREED_OPTIONS[pet_type][:3]):  # Display first 3 breeds
        with [col1, col2, col3][i]:
            # Replace 'IMAGE_URL' with actual JPG links for each breed
            st.image("https://via.placeholder.com/150", caption=breed, use_column_width=True)
            if st.button(f"Select {breed}", key=f"{pet_type}_{breed}"):
                st.session_state.selected_pet = {
                    "Type": pet_type,
                    "Breed": breed,
                    "Name": get_random_pet_name()
                }
                st.success(f"You've selected a {breed}!")

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
        st.subheader("Click on a pet to select it for adoption.")
        
        pet_type = st.radio("Select Pet Type", ["Dog", "Cat", "Reptile"])
        display_pet_options(pet_type)

        submitted = st.form_submit_button("Submit Application")

        if submitted:
            if not all([first_name, last_name, email, street_address, city, state, zip_code]):
                st.error("Please fill in all fields.")
            elif not validate_email(email):
                st.error("Please enter a valid email address.")
            elif not validate_zip_code(zip_code):
                st.error("Please enter a valid 5-digit zip code.")
            elif 'selected_pet' not in st.session_state:
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
                    "Pet Type": st.session_state.selected_pet["Type"],
                    "Pet Breed": st.session_state.selected_pet["Breed"],
                    "Pet Name": st.session_state.selected_pet["Name"]
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
                pet_info = ["Pet Type", "Pet Breed", "Pet Name"]
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
                                                   st.session_state.application_data["Pet Breed"] if st.session_state.application_data["Pet Type"] == "Dog" else "None",
                                                   st.session_state.application_data["Pet Breed"] if st.session_state.application_data["Pet Type"] == "Cat" else "None",
                                                   st.session_state.application_data["Pet Breed"] if st.session_state.application_data["Pet Type"] == "Reptile" else "None",
                                                   st.session_state.application_data["Pet Name"] if st.session_state.application_data["Pet Type"] == "Dog" else None,
                                                   st.session_state.application_data["Pet Name"] if st.session_state.application_data["Pet Type"] == "Cat" else None,
                                                   st.session_state.application_data["Pet Name"] if st.session_state.application_data["Pet Type"] == "Reptile" else None):
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
            st.session_state.review
