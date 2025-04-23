# auth.py
import streamlit as st
from streamlit_google_auth import Authenticate
import json # To load the credentials dict

# -----------------------------------------------------------------------------
# Configuration & Initialization
# -----------------------------------------------------------------------------

# Initialize session state keys if they don't exist
if 'connected' not in st.session_state:
    st.session_state['connected'] = False
if 'user_info' not in st.session_state:
    st.session_state['user_info'] = {}
if 'user' not in st.session_state: # Ensure 'user' key exists for check_auth
    st.session_state['user'] = None

# Load Google OAuth Credentials from Streamlit Secrets
try:
    # Ensure the secret exists and has the expected structure ('web' key)
    if "google_oauth_credentials" in st.secrets and "web" in st.secrets["google_oauth_credentials"]:
        # The Authenticate library expects a dictionary, not a file path, when passing credentials directly
        credentials_dict = dict(st.secrets["google_oauth_credentials"])

        # Initialize Google Authenticator with credentials from secrets
        authenticator = Authenticate(
            # Pass the dictionary directly
            secret_credentials=credentials_dict,
            cookie_name='neural_scribe_cookie_v2', # Use a unique cookie name
            cookie_key='a_reasonably_strong_secret_key_v2', # Use a strong, unique key from secrets if possible
            redirect_uri='http://localhost:8501', # Ensure this matches your redirect URI in Google Cloud Console
        )
        google_auth_initialized = True
    else:
        st.error("Google OAuth credentials ('google_oauth_credentials' with 'web' key) not found or invalid in Streamlit secrets (secrets.toml).")
        google_auth_initialized = False
        authenticator = None # Set authenticator to None if initialization fails

except Exception as e:
    st.error(f"❌ Error initializing Google Authenticator: {e}")
    st.error("Please ensure your Google OAuth client secrets JSON content is correctly configured under 'google_oauth_credentials' in secrets.toml.")
    google_auth_initialized = False
    authenticator = None

# -----------------------------------------------------------------------------
# Authentication Functions
# -----------------------------------------------------------------------------

def google_login_flow():
    """Handles the Google login button and authentication check."""
    if not google_auth_initialized or not authenticator:
        st.error("Google Authentication is not configured correctly.")
        return

    # Check authentication status using the library's method
    # This method handles the token verification based on cookies
    authenticator.check_authentification() # Removed timeout, let library handle it

    # If check_authentification finds a valid token, it sets st.session_state['connected'] = True
    # and populates st.session_state['user_info']

    if not st.session_state.get('connected', False):
        # If not connected, show the login button which redirects to Google
        try:
            # Get the authorization URL from the library
            authorization_url = authenticator.get_authorization_url()
            # Display the login button as a link
            st.link_button("Login with Google", authorization_url)
        except Exception as e:
             st.error(f"Error getting Google authorization URL: {e}")
    else:
        # If connected (authentication successful)
        user_info = st.session_state.get('user_info', {})
        user_email = user_info.get('email')
        user_name = user_info.get('name')
        user_photo = user_info.get('picture')

        # Store standardized user info in session_state['user'] for app.py
        st.session_state["user"] = {
            "email": user_email,
            "name": user_name,
            "photo": user_photo
        }
        # Don't automatically switch page here, let app.py handle the main view
        # st.success(f"Logged in as {user_name}") # Confirmation is good
        # st.rerun() # Rerun to remove the login button and let app.py take over

def login_screen():
    """Displays the login options."""
    st.markdown("""
        <style>
        .login-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 80vh; /* Use min-height */
            /* background: linear-gradient(to right, #1E3A8A, #3B82F6); Optional background */
            color: #31333F; /* Default text color */
            padding: 2rem;
        }
        .login-container h1 {
            font-size: 2.5rem; /* Adjusted size */
            color: #1E3A8A; /* Dark blue */
            margin-bottom: 2rem;
        }
        /* Style the link_button if needed, though it's generally styled by Streamlit */
        </style>
    """, unsafe_allow_html=True)

    with st.container(): # Use a container for centering
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.title("Welcome to Neural Scribe")
        st.write("Please log in to continue.")

        # Only show Google Login if initialized correctly
        if google_auth_initialized:
            google_login_flow() # Integrate the Google login button/logic here
        else:
            st.warning("Google Login is currently unavailable. Please check configuration.")

        # Placeholder for other methods if you add them later
        # choice = st.radio("Choose an option", ["Login with Google"]) # Simplified
        # if choice == "Login with Google":
        #    google_login_flow()

        st.markdown('</div>', unsafe_allow_html=True)


def check_auth():
    """Checks if the user is authenticated based on session state."""
    # Check if the 'user' key exists and is not None (set after successful login)
    # Also rely on the 'connected' state from the auth library for robustness
    return st.session_state.get("connected", False) and st.session_state.get("user") is not None

def logout():
    """Logs the user out and clears session state."""
    if google_auth_initialized and authenticator:
        try:
            # Use the library's logout method if available and needed
            # authenticator.logout() # Check library docs if this is the correct method
            pass # Often, just clearing state is enough
        except Exception as e:
            st.warning(f"Issue during library logout: {e}") # Non-critical usually

    # Clear relevant session state keys
    keys_to_clear = ['connected', 'user_info', 'user', 'chat_history', 'document_text', 'current_file_name', 'summary']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

    st.success("You have been logged out.")
    # Rerun to go back to the login screen
    st.rerun()

