import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import yagmail
import re
import random

# ... (previous code remains the same)

# Add this list of pet names
PET_NAMES = [
    "Buddy", "Max", "Charlie", "Lucy", "Bailey", "Cooper", "Daisy", "Luna", "Rocky", "Molly",
    "Jack", "Sadie", "Toby", "Chloe", "Lola", "Bear", "Duke", "Bella", "Oliver", "Sophie"
]

def get_random_pet_name():
    return random.choice(PET_NAMES)

# ... (previous functions remain the same)

def main():
    existing_data = load_data()

    if 'review_stage' not in st.session_state:
        st.session_state.review_stage = False

    if 'application_submitted' not in st.session_state:
        st.session_state.application_submitted = False

    if 'random_pet_name' not in st.session_state:
        st.session_state.random_pet_name = get_random_pet_name()

    if not st.session_state.application_submitted:
        if not st.session_state.review_stage:
            submit_application()
        else:
            st.subheader("Contact Information Summary")
            contact_info = ["First Name", "Last Name", "Email", "Street Address", "City", "State", "Zip"]
            for key in contact_info:
                st.write(f"{key}: {st.session_state.application_data[key]}")
            
            st.subheader("Pet Information Summary")
            st.write(f"Pet Name: {st.session_state.random_pet_name}")
            pet_info = ["Dog Breed", "Cat Breed", "Reptile Breed"]
            for key in pet_info:
                if st.session_state.application_data[key] != "None":
                    st.write(f"{key}: {st.session_state.application_data[key]}")
            
            col1, col2, col3 = st.columns(3)
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
            with col3:
                if st.button("Get New Pet Name"):
                    st.session_state.random_pet_name = get_random_pet_name()
                    st.rerun()
    else:
        st.success("Your application has been submitted successfully!")
        if st.button("🆕 Enter New Application"):
            st.session_state.application_submitted = False
            st.session_state.review_stage = False
            del st.session_state.random_pet_name
            st.rerun()

if __name__ == "__main__":
    main()
