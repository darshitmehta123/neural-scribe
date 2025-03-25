Here is the updated and consolidated README.md file for your project:

```markdown
# Neural Scribe - AI-Powered Document Processing

Neural Scribe is an AI-powered document processing application that allows users to upload documents, extract text (including OCR for scanned PDFs and images), summarize content, and interact with the document through a ChatGPT-like interface. The application also supports history tracking, suggestions, and a modern UI design.

---

## **Features**

### 📄 Document Upload
- Supports **PDF**, **TXT**, **JPG**, **JPEG**, and **PNG** file formats.
- Extracts text from documents, including OCR for scanned PDFs and images.

### ✨ Summarization
- Summarizes the uploaded document using OpenAI's GPT model.
- Stores summaries in Firestore with timestamps for future reference.

### 💬 Chat with Document
- ChatGPT-like interface for interacting with the document.
- Users can ask questions or request suggestions about the document.
- Displays chat history with user and assistant messages styled as chat bubbles.
- Automatically scrolls to the bottom of the chat window for a seamless experience.

### 🧹 Clear Chat
- A button to clear the chat history for a fresh start.

### 📜 History Management
- View summarization and Q&A history in the sidebar.
- Includes timestamps for each entry.
- Option to clear all history.

### 💡 Suggestions
- Users can submit feedback or suggestions through the sidebar.

### 🔒 Authentication
- Includes a login screen for user authentication.

### 🎨 Modern UI
- Custom styling for a clean and user-friendly interface.
- ChatGPT-like chat bubbles for user and assistant messages.

---

## **Installation**

### Prerequisites
- Python 3.8 or higher
- Firebase credentials JSON file for Firestore integration
- Google Cloud Vision API credentials JSON file

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/neural-scribe.git
   cd neural-scribe
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Add your Firebase and Google Cloud credentials:
   - Place your `firebase_credentials.json` and `google_cloud_credentials.json` files in the project directory.
   - Alternatively, use **Streamlit Secrets Management** to securely store credentials.

4. Add a `.streamlit/secrets.toml` file for sensitive information:
   ```toml
   [FIREBASE_CREDENTIALS]
   type = "service_account"
   project_id = "your_project_id"
   private_key_id = "your_private_key_id"
   private_key = "your_private_key"
   client_email = "your_client_email"
   client_id = "your_client_id"
   auth_uri = "https://accounts.google.com/o/oauth2/auth"
   token_uri = "https://oauth2.googleapis.com/token"
   auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
   client_x509_cert_url = "your_client_cert_url"

   GOOGLE_APPLICATION_CREDENTIALS = "path_to_google_cloud_credentials.json"
   OPENAI_API_KEY = "your_openai_api_key"
   ```

5. Run the application:
   ```bash
   streamlit run app.py
   ```

---

## **Usage**

1. **Upload a Document**:
   - Use the file uploader to upload a PDF, TXT, or image file.

2. **Summarize the Document**:
   - Click the "Summarize Document" button to generate a summary.

3. **Chat with the Document**:
   - Use the chat input to ask questions or request suggestions about the document.
   - View responses in the chat window styled like ChatGPT.

4. **Manage History**:
   - View summarization and Q&A history in the sidebar.
   - Use the "Clear History" button to delete all history.

5. **Submit Suggestions**:
   - Use the suggestion box in the sidebar to share feedback or ideas.

---

## **Project Structure**

```
neural-scribe/
│
├── app.py                     # Main application file
├── auth.py                    # Authentication logic
├── firebase_credentials.json  # Firebase credentials (not included in the repo)
├── google_cloud_credentials.json  # Google Cloud Vision credentials (not included in the repo)
├── assets/
│   └── logo.jpeg              # Logo for the sidebar
├── requirements.txt           # Python dependencies
├── .streamlit/
│   └── secrets.toml           # Secrets for deployment
└── README.md                  # Project documentation
```

---

## **Dependencies**

- **Streamlit**: For building the web application.
- **PyPDF2**: For extracting text from PDFs.
- **PyMuPDF (fitz)**: For extracting images from PDFs.
- **Pillow**: For image processing.
- **OpenAI API**: For summarization and chat responses.
- **Google Cloud Vision API**: For OCR text extraction.
- **Firebase Admin SDK**: For Firestore integration.

Install all dependencies using:
```bash
pip install -r requirements.txt
```

---

## **Environment Variables**

- **Firebase Credentials**: Use `firebase_credentials.json` or Streamlit Secrets.
- **Google Cloud Vision Credentials**: Use `google_cloud_credentials.json` or Streamlit Secrets.
- **OpenAI API Key**: Store securely in Streamlit Secrets.

---

## **Screenshots**

### Login Page
![Login Page](assets/screenshots/login_page.png)

### Homepage
![Homepage](assets/screenshots/homepage.png)

### Chat Interface
![Chat Interface](assets/screenshots/chat_interface.png)

---

## **Contributing**

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a detailed description of your changes.

---

## **License**

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## **Acknowledgments**

- [Streamlit](https://streamlit.io/) for the web framework.
- [OpenAI](https://openai.com/) for the GPT model.
- [Google Cloud Vision API](https://cloud.google.com/vision) for OCR capabilities.
- [Firebase](https://firebase.google.com/) for database and authentication.

---
```

### **Key Updates**
1. **Removed Tesseract OCR**:
   - Updated the dependencies and instructions to reflect the use of Google Cloud Vision API instead of Tesseract.

2. **Streamlit Secrets**:
   - Added instructions for using `.streamlit/secrets.toml` to securely store sensitive credentials.

3. **Screenshots Section**:
   - Included placeholders for screenshots to visually showcase the app.

4. **Project Structure**:
   - Updated the structure to include all relevant files, including secrets and assets.

This README.md is now comprehensive and ready for deployment or sharing on platforms like GitHub.

Similar code found with 1 license type