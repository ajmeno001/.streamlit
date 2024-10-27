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
