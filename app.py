# app.py
import streamlit as st
import openai
import fitz  # PyMuPDF
import os
import firebase_admin
from firebase_admin import credentials, firestore
from auth import login_screen, check_auth, logout # Import necessary functions from auth.py
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.stylable_container import stylable_container
from PIL import Image
import io
import google.cloud.vision_v1 as vision
from datetime import datetime
import json # Needed to load service account keys from secrets

# -----------------------------------------------------------------------------
# Configuration & Initialization
# -----------------------------------------------------------------------------

# 🔥 Initialize Firebase (Using Streamlit Secrets)
# Load Firebase credentials from secrets
try:
    # Check if secrets are loaded and contain the necessary keys
    if "firebase_service_account" in st.secrets:
        firebase_creds_dict = dict(st.secrets["firebase_service_account"])
        # Ensure the private_key is formatted correctly (replace escaped newlines)
        if "private_key" in firebase_creds_dict:
             firebase_creds_dict["private_key"] = firebase_creds_dict["private_key"].replace("\\n", "\n")

        cred = credentials.Certificate(firebase_creds_dict)

        # Initialize Firebase only if it hasn't been initialized yet
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        firebase_initialized = True
    else:
        st.error("Firebase credentials not found in Streamlit secrets (secrets.toml). Please configure them.")
        firebase_initialized = False
        st.stop() # Stop execution if Firebase cannot be initialized

except Exception as e:
    st.error(f"❌ Error initializing Firebase: {e}")
    st.error("Please ensure your Firebase service account key is correctly configured in secrets.toml.")
    firebase_initialized = False
    st.stop() # Stop execution

# Initialize Google Cloud Vision Client (Using Streamlit Secrets)
try:
    # Check if secrets are loaded and contain the necessary keys
    if "google_cloud_vision_service_account" in st.secrets:
        # Create a temporary file for the credentials JSON if needed by the library,
        # or ideally, load directly if the library supports it.
        # Here, we load the dictionary and pass it to the client constructor if possible,
        # or set the environment variable pointing to a temporary file.

        # Option 1: Load credentials directly (Preferred if supported)
        # vision_creds_dict = dict(st.secrets["google_cloud_vision_service_account"])
        # if "private_key" in vision_creds_dict:
        #     vision_creds_dict["private_key"] = vision_creds_dict["private_key"].replace("\\n", "\n")
        # vision_credentials = vision.Credentials.from_service_account_info(vision_creds_dict)
        # vision_client = vision.ImageAnnotatorClient(credentials=vision_credentials)

        # Option 2: Use environment variable (More common)
        google_creds_dict = dict(st.secrets["google_cloud_vision_service_account"])
        if "private_key" in google_creds_dict:
             google_creds_dict["private_key"] = google_creds_dict["private_key"].replace("\\n", "\n")

        # Create a temporary credentials file path
        creds_path = "temp_google_creds.json"
        with open(creds_path, "w") as f:
            json.dump(google_creds_dict, f)

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
        vision_client = vision.ImageAnnotatorClient()
        google_vision_initialized = True

        # Clean up the temporary file after client initialization (optional, consider security)
        # os.remove(creds_path) # Be careful if the client needs the file later

    else:
        st.error("Google Cloud Vision credentials not found in Streamlit secrets (secrets.toml). Please configure them.")
        google_vision_initialized = False
        # Don't stop here, maybe some functionality doesn't need vision
        vision_client = None

except Exception as e:
    st.error(f"❌ Error initializing Google Cloud Vision: {e}")
    st.error("Please ensure your Google Cloud Vision service account key is correctly configured in secrets.toml.")
    google_vision_initialized = False
    vision_client = None


# Load OpenAI API Key (Using Streamlit Secrets)
try:
    if "openai" in st.secrets and "api_key" in st.secrets["openai"]:
        openai.api_key = st.secrets["openai"]["api_key"]
        openai_initialized = True
    else:
        st.error("OpenAI API key not found in Streamlit secrets (secrets.toml). Please configure it.")
        openai_initialized = False
        # Don't stop, maybe some functionality doesn't need OpenAI
except Exception as e:
    st.error(f"❌ Error initializing OpenAI: {e}")
    openai_initialized = False


# -----------------------------------------------------------------------------
# Authentication Check
# -----------------------------------------------------------------------------

# 🛑 Check if user is authenticated (using the function from auth.py)
# This relies on the authentication flow in auth.py setting the session state
if not check_auth():
    login_screen() # Display the login screen from auth.py
    st.stop() # Stop execution if not authenticated

# -----------------------------------------------------------------------------
# UI Styling and Layout
# -----------------------------------------------------------------------------

# 🎨 Apply Custom Styling (Consider moving to a separate CSS file for larger apps)
st.markdown("""
    <style>
        /* General body padding */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        /* Input elements styling */
        .stTextInput, .stButton, .stFileUploader, .stSelectbox {
            /* background: rgba(255, 255, 255, 0.1); Glass effect - adjust opacity */
            border-radius: 10px;
            /* padding: 10px; */ /* Handled by Streamlit's default padding */
            /* border: 1px solid rgba(255, 255, 255, 0.2); Optional border */
        }
        /* Input field text color */
        .stTextInput > div > div > input, .stTextArea > div > textarea {
            /* background: transparent !important; */ /* May cause usability issues */
            /* color: #31333F !important; /* Default Streamlit text color */
        }
        /* Button styling */
        .stButton button {
            background: linear-gradient(to right, #3B82F6, #1E40AF); /* Blue gradient */
            color: white;
            border-radius: 8px;
            font-weight: bold;
            border: none; /* Remove default border */
            padding: 0.5rem 1rem; /* Adjust padding */
        }
        .stButton button:hover {
            background: linear-gradient(to right, #2563EB, #1E3A8A); /* Darker gradient on hover */
        }
        /* Sidebar styling */
        .stSidebar {
            /* background: rgba(255, 255, 255, 0.05); /* Subtle glass effect */
            /* border-right: 1px solid rgba(255, 255, 255, 0.1); */
        }
        /* Card styling */
        .glass-card {
            background: rgba(240, 242, 246, 0.7); /* Light background with some transparency */
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); /* Soft shadow */
            border: 1px solid rgba(200, 200, 200, 0.3); /* Subtle border */
        }
        /* Hero section styling */
        .hero {
            background: linear-gradient(135deg, #1E3A8A, #3B82F6); /* Adjusted gradient */
            color: white;
            padding: 2.5rem;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
        }
        .hero h1 {
            font-size: 2.8rem;
            margin-bottom: 1rem;
            font-weight: 600;
        }
        .hero p {
            font-size: 1.3rem;
            opacity: 0.9;
        }
        /* Chat container styling */
        .chat-container {
            max-height: 450px; /* Increased height */
            overflow-y: auto;
            padding: 15px;
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            background-color: #ffffff; /* White background */
            margin-bottom: 1rem; /* Space below chat */
        }
        /* Chat bubble base style */
        .chat-bubble {
            padding: 12px 18px;
            margin: 8px 0;
            border-radius: 15px;
            max-width: 75%; /* Slightly narrower */
            word-wrap: break-word; /* Ensure long words wrap */
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            line-height: 1.4;
        }
        /* User chat bubble */
        .chat-bubble.user {
            background-color: #3B82F6; /* Blue background */
            color: white;
            margin-left: auto; /* Align to right */
            border-bottom-right-radius: 5px; /* Tail effect */
        }
        /* Assistant chat bubble */
        .chat-bubble.assistant {
            background-color: #e5e7eb; /* Light gray background */
            color: #1f2937; /* Dark gray text */
            margin-right: auto; /* Align to left */
            border-bottom-left-radius: 5px; /* Tail effect */
        }
    </style>
    <div class="hero">
        <h1>Welcome to Neural Scribe</h1>
        <p>AI-powered document processing at your fingertips.</p>
    </div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

def extract_text(uploaded_file):
    """Extracts text from uploaded file (PDF, TXT, JPG, PNG)."""
    text = ""
    file_bytes = uploaded_file.getvalue() # Read file bytes once

    try:
        if uploaded_file.name.lower().endswith(".txt"):
            text = file_bytes.decode("utf-8")
        elif uploaded_file.name.lower().endswith(".pdf"):
            # Use PyMuPDF (fitz) for PDF text and image extraction
            pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                # Extract text directly from the page
                text += page.get_text("text") + "\n" # Use "text" for better extraction

                # Check if Vision client is available before processing images
                if vision_client:
                    # Extract images and use Google Cloud Vision OCR
                    images = page.get_images(full=True)
                    for img_index, img in enumerate(images):
                        xref = img[0]
                        try:
                            base_image = pdf_document.extract_image(xref)
                            image_bytes_pdf = base_image["image"]
                            image = vision.Image(content=image_bytes_pdf)
                            response = vision_client.text_detection(image=image)
                            if response.error.message:
                                st.warning(f"Vision API Error on page {page_num+1}, image {img_index+1}: {response.error.message}")
                            else:
                                text += response.full_text_annotation.text + "\n"
                        except Exception as img_e:
                            st.warning(f"Could not process image {img_index+1} on page {page_num+1}: {img_e}")
                else:
                    st.warning("Google Cloud Vision client not initialized. Skipping image OCR in PDF.")
            pdf_document.close() # Close the document

        elif uploaded_file.name.lower().endswith((".jpg", ".jpeg", ".png")):
            if vision_client:
                # Process image files using Google Cloud Vision OCR
                image = vision.Image(content=file_bytes)
                response = vision_client.text_detection(image=image)
                if response.error.message:
                     st.error(f"Vision API Error processing image {uploaded_file.name}: {response.error.message}")
                     return "" # Return empty string on error
                else:
                    text = response.full_text_annotation.text
            else:
                st.error("Google Cloud Vision client not initialized. Cannot process image files.")
                return "" # Return empty string if vision client is unavailable
        else:
            st.error(f"Unsupported file type: {uploaded_file.name}")
            return ""

    except Exception as e:
        st.error(f"❌ Error extracting text from {uploaded_file.name}: {e}")
        return "" # Return empty string on error

    return text

def call_openai_api(prompt, model="gpt-4o-mini", temperature=0.7):
    """Calls the OpenAI ChatCompletion API."""
    if not openai_initialized:
        st.error("OpenAI client not initialized. Cannot generate response.")
        return None # Return None if OpenAI is not available

    try:
        response = openai.chat.completions.create( # Updated API call
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant processing documents."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content
    except openai.APIError as e:
        st.error(f"❌ OpenAI API Error: {e}")
    except Exception as e:
        st.error(f"❌ An unexpected error occurred calling OpenAI: {e}")
    return None # Return None on error


def save_to_firestore(collection_name, data):
    """Saves data to a specified Firestore collection."""
    if not firebase_initialized:
        st.warning("Firebase not initialized. Cannot save data.")
        return False

    try:
        # Ensure common fields are present
        data["user_email"] = st.session_state.get("user", {}).get("email", "unknown_user")
        data["timestamp"] = datetime.now()
        db.collection(collection_name).add(data)
        return True
    except Exception as e:
        st.error(f"❌ Error saving data to Firestore collection '{collection_name}': {e}")
        return False

# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------
st.sidebar.title("Navigation")

# Use session state for user info if available from auth.py
user_info = st.session_state.get("user", {})
user_name = user_info.get("name", "User")
user_email = user_info.get("email", None)
user_photo = user_info.get("photo", None)

if user_photo:
    st.sidebar.image(user_photo, width=100)
if user_name:
    st.sidebar.write(f"Welcome, {user_name}!")

# Sidebar navigation buttons
if st.sidebar.button("🏠 Dashboard"):
    st.session_state.view_history = False
    st.rerun() # Rerun to switch view

if st.sidebar.button("📜 View History"):
    st.session_state.view_history = True
    st.rerun() # Rerun to switch view

# Clear Chat button (only show if a document is loaded)
if "document_text" in st.session_state and st.session_state.document_text:
     if st.sidebar.button("🧹 Clear Current Chat"):
        st.session_state.chat_history = []  # Clear chat history for the current doc
        st.success("✅ Chat cleared for this document!")
        st.rerun()

# Clear All History Button (moved from main view)
if st.sidebar.button("🗑️ Clear All My History"):
    if user_email and firebase_initialized:
        try:
            # Delete summaries
            summaries_ref = db.collection("summaries").where("user_email", "==", user_email)
            for doc in summaries_ref.stream():
                doc.reference.delete()

            # Delete Q&A history
            chat_history_ref = db.collection("chat_history").where("user_email", "==", user_email)
            for doc in chat_history_ref.stream():
                doc.reference.delete()

            st.sidebar.success("✅ All history cleared successfully!")
            # Optionally clear local session state if needed
            if st.session_state.get("view_history"):
                st.rerun() # Rerun if currently viewing history

        except Exception as e:
            st.sidebar.error(f"❌ Error clearing history: {e}")
    elif not user_email:
        st.sidebar.error("Could not determine user email to clear history.")
    else:
         st.sidebar.error("Firebase not initialized. Cannot clear history.")


# Suggestion Box
st.sidebar.markdown("---")
st.sidebar.subheader("💡 Suggestions")
suggestion = st.sidebar.text_area("Share your feedback or ideas...", key="suggestion_box")
if st.sidebar.button("Submit Suggestion"):
    if suggestion:
        if save_to_firestore("suggestions", {"suggestion": suggestion}):
            st.sidebar.success("✅ Thank you for your suggestion!")
            # Clear the suggestion box after submission
            st.session_state.suggestion_box = "" # Clear the text area using its key
            st.rerun() # Rerun to reflect the cleared text area
        else:
            st.sidebar.error("❌ Error submitting suggestion.")
    else:
        st.sidebar.warning("Please enter a suggestion before submitting.")


# Logout Button
st.sidebar.markdown("---")
st.sidebar.button("🚪 Logout", on_click=logout) # Use logout function from auth.py

# -----------------------------------------------------------------------------
# Main Application Logic (Dashboard vs History View)
# -----------------------------------------------------------------------------

# Initialize session state keys if they don't exist
if "view_history" not in st.session_state:
    st.session_state.view_history = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "document_text" not in st.session_state:
    st.session_state.document_text = None
if "current_file_name" not in st.session_state:
    st.session_state.current_file_name = None


# --- History View ---
if st.session_state.view_history:
    st.title("📂 Your History")

    if not user_email:
        st.warning("Could not determine user email to fetch history.")
    elif not firebase_initialized:
        st.error("Firebase connection not available. Cannot fetch history.")
    else:
        # Display Summarization History
        st.subheader("📄 Summarization History")
        try:
            summaries_ref = db.collection("summaries").where("user_email", "==", user_email).order_by("timestamp", direction=firestore.Query.DESCENDING)
            summaries = summaries_ref.stream()
            summary_count = 0
            for doc in summaries:
                data = doc.to_dict()
                timestamp_str = data.get('timestamp', 'N/A')
                if isinstance(timestamp_str, datetime):
                    timestamp_str = timestamp_str.strftime('%Y-%m-%d %H:%M') # Format timestamp

                with st.expander(f"📄 **{data.get('file_name', 'N/A')}** ({data.get('language', 'N/A')}) - {timestamp_str}"):
                    st.write(data.get('summary', 'No summary available.'))
                summary_count += 1
            if summary_count == 0:
                st.info("No summarization history found.")

        except Exception as e:
            st.error(f"❌ Error fetching Summarization history: {e}")

        # Display Q&A History
        st.subheader("❓ Q&A History")
        try:
            chat_history_ref = db.collection("chat_history").where("user_email", "==", user_email).order_by("timestamp", direction=firestore.Query.DESCENDING)
            chats = chat_history_ref.stream()
            chat_count = 0
            # Group chats by file name might be better, but for simplicity, list them chronologically
            for doc in chats:
                data = doc.to_dict()
                timestamp_str = data.get('timestamp', 'N/A')
                if isinstance(timestamp_str, datetime):
                    timestamp_str = timestamp_str.strftime('%Y-%m-%d %H:%M') # Format timestamp

                with st.expander(f"💬 Chat about **{data.get('file_name', 'N/A')}** - {timestamp_str}"):
                    st.markdown(f"**You:** {data.get('user_message', 'N/A')}")
                    st.markdown(f"**Assistant:** {data.get('assistant_response', 'N/A')}")
                chat_count += 1
            if chat_count == 0:
                 st.info("No Q&A history found.")

        except Exception as e:
            st.error(f"❌ Error fetching Q&A history: {e}")

# --- Dashboard View ---
else:
    # st.title("📝 Neural Scribe - AI-Powered Document Processing") # Title is in the hero section

    uploaded_file = st.file_uploader(
        "📄 **Upload Document** (PDF/TXT/JPG/PNG)",
        type=["pdf", "txt", "jpg", "jpeg", "png"],
        key="file_uploader" # Add a key for potential state management
    )

    if uploaded_file:
        # Check if it's a new file; if so, reset state
        if st.session_state.current_file_name != uploaded_file.name:
            st.session_state.chat_history = []  # Clear chat history for the new file
            st.session_state.document_text = None # Clear previous document text
            st.session_state.current_file_name = uploaded_file.name
            # Clear previous summary display if any
            if "summary" in st.session_state:
                del st.session_state["summary"]
            st.info(f"Processing new file: {uploaded_file.name}")

        # Extract text only if it hasn't been extracted for this file yet
        if st.session_state.document_text is None:
            with st.spinner(f"Analyzing {uploaded_file.name}..."):
                st.session_state.document_text = extract_text(uploaded_file)
                if not st.session_state.document_text:
                    st.error("Failed to extract text from the document. Please try a different file or check the file format.")
                    # Reset state if extraction fails
                    st.session_state.current_file_name = None
                    st.session_state.document_text = None
                    uploaded_file = None # Prevent further processing
                # else:
                    # st.success("✅ Document text extracted successfully!") # Optional success message

        # Proceed only if text extraction was successful
        if uploaded_file and st.session_state.document_text:
            document_text = st.session_state.document_text # Use cached text

            # --- Summarization Section ---
            with stylable_container("glass-card", css_styles=""): # Use the glass card style
                st.subheader("✨ Generate Summary")
                language = st.selectbox("Select summary language:", ["en", "es", "fr", "de", "hi"], key="lang_select")

                if st.button("Summarize Document"):
                    if not openai_initialized:
                        st.error("OpenAI is not configured. Cannot summarize.")
                    else:
                        with st.spinner("🤔 Generating summary..."):
                            summary_prompt = f"Summarize the following document in {language}:\n\n---\n\n{document_text}\n\n---\n\nSummary:"
                            summary = call_openai_api(summary_prompt)

                            if summary:
                                st.session_state.summary = summary # Store summary in session state
                                st.success("✅ Summary Generated!")
                                # Save summary to Firestore
                                if not save_to_firestore("summaries", {
                                    "file_name": uploaded_file.name,
                                    "summary": summary,
                                    "language": language
                                }):
                                     st.warning("Could not save summary to history.") # Inform user if saving failed
                            else:
                                st.error("Failed to generate summary.")

                # Display summary if it exists in session state
                if "summary" in st.session_state:
                    st.markdown("**Summary:**")
                    st.markdown(st.session_state.summary) # Display the generated summary


            # --- Chat Section ---
            st.subheader("💬 Chat with Document")

            # Chat container to display history
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            if not st.session_state.chat_history:
                 st.markdown('<div style="text-align: center; color: grey; padding: 20px;">Chat history is empty. Ask a question below!</div>', unsafe_allow_html=True)
            else:
                for message in st.session_state.chat_history:
                    bubble_class = "user" if message["role"] == "user" else "assistant"
                    # Basic HTML escaping (consider a more robust library for production)
                    escaped_content = message["content"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    st.markdown(f'<div class="chat-bubble {bubble_class}">{escaped_content}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Input for user question
            user_input = st.chat_input("Ask a question about the document...")

            if user_input:
                if not openai_initialized:
                    st.error("OpenAI is not configured. Cannot process chat.")
                else:
                    # Add user message to chat history and display immediately
                    st.session_state.chat_history.append({"role": "user", "content": user_input})
                    # Display the user message instantly in the chat container (by rerunning)
                    # st.rerun() # Rerun can be disruptive, let's append and generate response

                    # Generate response using OpenAI
                    with st.spinner("💡 Thinking..."):
                        chat_prompt = f"""Context: You are chatting with a user about the following document:
                        --- Document Start ---
                        {document_text}
                        --- Document End ---

                        User's Question: {user_input}

                        Provide a helpful and concise answer based *only* on the document content provided. If the answer isn't in the document, say so.
                        """
                        response = call_openai_api(chat_prompt)

                        if response:
                            # Add assistant response to history
                            st.session_state.chat_history.append({"role": "assistant", "content": response})

                            # Save chat interaction to Firestore
                            if not save_to_firestore("chat_history", {
                                "file_name": uploaded_file.name,
                                "user_message": user_input,
                                "assistant_response": response
                            }):
                                st.warning("Could not save chat interaction to history.")
                        else:
                             st.error("Failed to get a response from the assistant.")

                    # Rerun to display the updated chat history including the assistant's response
                    st.rerun()

# Clean up temporary credential file if it exists
if os.path.exists("temp_google_creds.json"):
    try:
        os.remove("temp_google_creds.json")
    except Exception as e:
        st.warning(f"Could not remove temporary credentials file: {e}")
