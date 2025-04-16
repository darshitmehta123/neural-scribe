import streamlit as st
import requests
import openai
import fitz  # PyMuPDF
import os
import firebase_admin
from firebase_admin import credentials, firestore
from auth import login_screen, check_auth, logout
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.stylable_container import stylable_container
from PIL import Image
import google.cloud.vision_v1 as vision
from datetime import datetime

# 🔥 Initialize Firebase
if not firebase_admin._apps:
    # Use Streamlit secrets for Firebase credentials
    firebase_credentials = st.secrets["firebase_credentials"]
    cred = credentials.Certificate(firebase_credentials)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# 🛑 Check if user is authenticated
if not check_auth():
    login_screen()
    st.stop()

# Initialize Google Cloud Vision Client
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = st.secrets["google_cloud_credentials_path"]
vision_client = vision.ImageAnnotatorClient()

# 🎨 Apply Custom Styling
st.markdown("""
    <style>
    .css-1d391kg { padding-top: 2rem; }
    .stTextInput, .stButton, .stFileUploader {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        padding: 10px;
    }
    .stTextInput > div > div > input {
        background: transparent !important;
        color: white !important;
    }
    .stButton button {
        background: linear-gradient(to right, #3B82F6, #1E40AF);
        color: white;
        border-radius: 8px;
        font-weight: bold;
    }
    .stSidebar {
        background: rgba(255, 255, 255, 0.1);
        border-right: 1px solid rgba(255, 255, 255, 0.2);
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0px 4px 10px rgba(255, 255, 255, 0.1);
    }
    .hero {
        background: linear-gradient(to right, #1E3A8A, #3B82F6);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .hero h1 {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    .hero p {
        font-size: 1.2rem;
    }
    .chat-container {
        max-height: 400px;
        overflow-y: auto;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 10px;
        background-color: #f9f9f9;
    }
    .chat-bubble {
        padding: 10px;
        margin: 5px 0;
        border-radius: 10px;
        max-width: 80%;
    }
    .chat-bubble.user {
        background-color: #3B82F6;
        color: white;
        align-self: flex-end;
    }
    .chat-bubble.assistant {
        background-color: #e5e5e5;
        color: black;
        align-self: flex-start;
    }
    </style>
    <div class="hero">
        <h1>Welcome to Neural Scribe</h1>
        <p>AI-powered document processing at your fingertips.</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <script>
    window.scrollTo(0, 0);
    var chatContainer = document.querySelector('.chat-container');
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    </script>
""", unsafe_allow_html=True)

# Use relative path for logo
logo_path = os.path.join("assets", "logo.jpeg")
st.sidebar.image(logo_path, width=150)
st.sidebar.button("Logout", on_click=logout)

# Initialize session state for view toggling
if "view_history" not in st.session_state:
    st.session_state.view_history = False  # Default to dashboard view

# Handle "View History" button
if st.sidebar.button("📜 View History"):
    st.session_state.view_history = True  # Switch to history view

# Handle "Back to Dashboard" button
if st.session_state.view_history:
    # Add a styled "Back to Dashboard" button at the top left
    col1, col2 = st.columns([1, 1])  # Create two columns for layout
    with col1:
        if st.button("🔙 Back to Dashboard"):
            st.session_state.view_history = False  # Switch back to dashboard view
            st.rerun()  # Refresh the app to update the view

    with col2:
        st.title("📂 Your History")

    user_email = st.session_state.get("user", {}).get("email", "guest")

    # Display Summarization History
    st.subheader("📄 Summarization History")
    summaries = db.collection("summaries").where("user_email", "==", user_email).order_by("timestamp", direction=firestore.Query.DESCENDING).stream()
    for doc in summaries:
        data = doc.to_dict()
        st.text_area(f"📄 {data['file_name']} ({data['language']}) - {data['timestamp']}", data['summary'], height=100)

    # Display Q&A History
    st.subheader("❓ Q&A History")
    try:
        chat_history = db.collection("chat_history").where("user_email", "==", user_email).order_by("timestamp", direction=firestore.Query.DESCENDING).stream()
        for doc in chat_history:
            data = doc.to_dict()
            st.text_area(f"❓ Q: {data['user_message']} - {data['timestamp']}", f"💬 A: {data['assistant_response']}", height=100)
    except Exception as e:
        st.error(f"❌ Error fetching Q&A history: {e}")

# Main Dashboard
if not st.session_state.view_history:
    st.title("📝 Neural Scribe - AI-Powered Document Processing")

    uploaded_file = st.file_uploader("📄 Upload Document (PDF/TXT/JPG/PNG)", type=["pdf", "txt", "jpg", "jpeg", "png"])
    language = st.selectbox("🌎 Language", ["en", "es", "fr", "de", "hi"])

    def extract_text(file):
        text = ""
        if file.name.endswith(".txt"):
            # Extract text from .txt files
            text = file.read().decode("utf-8")
        elif file.name.endswith(".pdf"):
            # Use PyMuPDF to extract images and apply Google Cloud Vision OCR
            pdf_document = fitz.open(stream=file.read(), filetype="pdf")
            for page_number in range(len(pdf_document)):
                page = pdf_document[page_number]
                # Extract text from the page (if any selectable text exists)
                text += page.get_text() + "\n"
                # Extract images from the page
                images = page.get_images(full=True)
                for img_index, img in enumerate(images):
                    xref = img[0]
                    base_image = pdf_document.extract_image(xref)
                    image_bytes = base_image["image"]
                    image = vision.Image(content=image_bytes)
                    # Use Google Cloud Vision API to extract text from the image
                    response = vision_client.text_detection(image=image)
                    text += response.full_text_annotation.text + "\n"
        elif file.name.endswith((".jpg", ".jpeg", ".png")):
            # Process image files
            image_bytes = file.read()
            image = vision.Image(content=image_bytes)
            # Use Google Cloud Vision API to extract text from the image
            response = vision_client.text_detection(image=image)
            text = response.full_text_annotation.text
        return text

    def call_openai_api(prompt):
        openai.api_key = st.secrets["openai_api_key"]
        
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are an assistant."},
                      {"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        return response["choices"][0]["message"]["content"]

    if uploaded_file:
        # Clear session state on new upload
        if "last_uploaded_file" not in st.session_state or st.session_state.last_uploaded_file != uploaded_file.name:
            st.session_state.chat_history = []  # Clear chat history
            st.session_state.last_uploaded_file = uploaded_file.name  # Track the current file

        # Scroll to the top
        st.markdown("""
            <script>
            window.scrollTo(0, 0);
            </script>
        """, unsafe_allow_html=True)

        with stylable_container("glass-card", css_styles=""):
            st.subheader("✨ Generate Summary")
            if st.button("Summarize Document"):
                with st.spinner("🤔 Thinking..."):
                    document_text = extract_text(uploaded_file)
                    summary = call_openai_api(f"Summarize this document in {language}:\n{document_text}")

                    try:
                        db.collection("summaries").add({
                            "user_email": st.session_state.get("user", {}).get("email", "guest"),
                            "file_name": uploaded_file.name,
                            "summary": summary,
                            "language": language,
                            "timestamp": datetime.now()
                        })
                        st.success("✅ Summary saved successfully!")
                    except Exception as e:
                        st.error(f"❌ Error saving summary: {e}")

                    st.success("✅ Summary Generated!")
                    st.write(summary)

        st.subheader("💬 Chat with Document")

        # Initialize chat history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Clear chat button
        if st.sidebar.button("🧹 Clear Chat"):
            st.session_state.chat_history = []  # Clear chat history
            st.success("✅ Chat cleared!")

        # Chat container
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f'<div class="chat-bubble user">{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bubble assistant">{message["content"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Input for user question
        user_input = st.chat_input("Ask a question or request suggestions about the document...")
        if user_input:
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            # Generate response using OpenAI
            with st.spinner("💡 Generating suggestions..."):
                document_text = extract_text(uploaded_file)
                response = call_openai_api(f"""
                You are an assistant. The user uploaded a document. Here is the document content:
                {document_text}

                The user asked: {user_input}
                Provide a helpful response or suggestion based on the document.
                """)
                st.session_state.chat_history.append({"role": "assistant", "content": response})

                # Display the assistant's response
                st.chat_message("assistant").write(response)

                # Save chat history to Firestore
                db.collection("chat_history").add({
                    "user_email": st.session_state.get("user", {}).get("email", "guest"),
                    "file_name": uploaded_file.name,
                    "user_message": user_input,
                    "assistant_response": response,
                    "timestamp": datetime.now()
                })

    suggestion = st.sidebar.text_area("💡 Suggestions", placeholder="Share your feedback or ideas...")
    if st.sidebar.button("Submit Suggestion"):
        try:
            db.collection("suggestions").add({
                "user_email": st.session_state.get("user", {}).get("email", "guest"),
                "suggestion": suggestion,
                "timestamp": datetime.now()
            })
            st.sidebar.success("✅ Thank you for your suggestion!")
        except Exception as e:
            st.sidebar.error(f"❌ Error submitting suggestion: {e}")

    st.sidebar.markdown("---")
    st.sidebar.write("🚀 **Neural Scribe - AI-Powered Document Processing**")

if st.sidebar.button("🗑️ Clear History"):
    user_email = st.session_state.get("user", {}).get("email", "guest")
    try:
        # Delete summaries
        summaries = db.collection("summaries").where("user_email", "==", user_email).stream()
        for doc in summaries:
            db.collection("summaries").document(doc.id).delete()

        # Delete Q&A history
        chat_history = db.collection("chat_history").where("user_email", "==", user_email).stream()
        for doc in chat_history:
            db.collection("chat_history").document(doc.id).delete()

        st.sidebar.success("✅ History cleared successfully!")
    except Exception as e:
        st.sidebar.error(f"❌ Error clearing history: {e}")

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
        <div class="login-container">
            <h1>Welcome to Neural Scribe</h1>
            <button onclick="window.location.href='/login'">Login</button>
        </div>
    """, unsafe_allow_html=True)
