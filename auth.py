import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, auth
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Firebase Admin SDK
if not firebase_admin._apps:  # Check if Firebase is already initialized
    firebase_credentials = st.secrets["FIREBASE_CREDENTIALS"]  # Already a dictionary
    st.write("Loaded Firebase Credentials:", firebase_credentials)  # Debugging
    cred = credentials.Certificate(firebase_credentials)
    firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()

def login_screen():
    st.markdown("""
        <style>
        .login-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            background: linear-gradient(to right, #1E3A8A, #3B82F6);
            color: white;
        }
        .login-container h1 {
            font-size: 3rem;
            margin-bottom: 2rem;
        }
        .login-container button {
            background: #3B82F6;
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 8px;
            font-size: 1.2rem;
            cursor: pointer;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("Welcome to Neural Scribe")
    choice = st.radio("Choose an option", ["Login", "Sign Up"])

    if choice == "Login":
        st.subheader("Login to your account")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        # Initialize a flag in session state to track button clicks
        if "login_clicked" not in st.session_state:
            st.session_state["login_clicked"] = False

        # Disable the button after it is clicked
        if st.button("Login", disabled=st.session_state["login_clicked"]):
            st.session_state["login_clicked"] = True  # Mark the button as clicked
            if not email.strip():
                st.error("❌ Email cannot be empty!")
                st.session_state["login_clicked"] = False  # Reset the flag
            else:
                user_ref = db.collection("users").document(email).get()
                if user_ref.exists:  # Correct usage of 'exists' as a property
                    user_data = user_ref.to_dict()
                    if check_password_hash(user_data["password"], password):
                        st.session_state["user"] = {"email": email}
                        st.success("✅ Login successful!")
                        st.query_params = {"page": "main"}  # Redirect to the main page
                    else:
                        st.error("❌ Incorrect password!")
                else:
                    st.error("❌ User does not exist!")
                st.session_state["login_clicked"] = False  # Reset the flag

    elif choice == "Sign Up":
        st.subheader("Create a new account")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        if st.button("Sign Up"):
            if not email.strip():
                st.error("❌ Email cannot be empty!")
            elif password != confirm_password:
                st.error("❌ Passwords do not match!")
            else:
                user_ref = db.collection("users").document(email).get()
                if user_ref.exists:  # Correct usage of 'exists' as a property
                    st.error("❌ Email already exists!")
                else:
                    try:
                        # Create user in Firebase Authentication
                        firebase_user = auth.create_user(
                            email=email,
                            password=password
                        )
                        # Use pbkdf2:sha256 as the hashing method for Firestore storage
                        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
                        # Store user details in Firestore
                        db.collection("users").document(email).set({
                            "password": hashed_password,
                            "uid": firebase_user.uid
                        })
                        st.success("✅ Account created successfully! Please log in.")
                    except Exception as e:
                        st.error(f"❌ Failed to create user: {e}")

def check_auth():
    return "user" in st.session_state

def logout():
    st.session_state.pop("user", None)
    st.rerun()
