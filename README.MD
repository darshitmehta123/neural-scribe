# Neural Scribe - AI-Powered Document Processing

Neural Scribe is an AI-powered document processing application that allows users to upload documents, extract text (including OCR for scanned PDFs and images), summarize content, and interact with the document through a ChatGPT-like interface. The application also supports history tracking, suggestions, and a modern UI design.

---

## Features

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

## Installation

### Prerequisites
- Python 3.8 or higher
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installed on your system
- Firebase credentials JSON file for Firestore integration

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

3. Set up Tesseract OCR:
   - Install Tesseract OCR from [here](https://github.com/tesseract-ocr/tesseract).
   - Update the path to `tesseract.exe` in the code:
     ```python
     pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
     ```

4. Add your Firebase credentials:
   - Place your `firebase_credentials.json` file in the project directory.

5. Run the application:
   ```bash
   streamlit run app.py
   ```

---

## Usage

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

## Project Structure

```
neural-scribe/
│
├── app.py                # Main application file
├── firebase_credentials.json  # Firebase credentials (not included in the repo)
├── assets/
│   └── logo.jpeg         # Logo for the sidebar
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

---

## Dependencies

- **Streamlit**: For building the web application.
- **PyPDF2**: For extracting text from PDFs.
- **PyMuPDF (fitz)**: For extracting images from PDFs.
- **Pillow**: For image processing.
- **pytesseract**: For OCR text extraction.
- **OpenAI API**: For summarization and chat responses.
- **Firebase Admin SDK**: For Firestore integration.

Install all dependencies using:
```bash
pip install -r requirements.txt
```

---

## Environment Variables

- **Tesseract Path**: Update the path to `tesseract.exe` in the code:
  ```python
  pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
  ```

- **OpenAI API Key**: Replace the placeholder API key in the `call_openai_api` function:
  ```python
  API_KEY = "your-openai-api-key"
  ```

---

## Screenshots

### Login Page
![Login Page](assets/screenshots/login_page.png)

### Homepage
![Homepage](assets/screenshots/homepage.png)

### Chat Interface
![Chat Interface](assets/screenshots/chat_interface.png)

---

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a detailed description of your changes.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- [Streamlit](https://streamlit.io/) for the web framework.
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for OCR capabilities.
- [OpenAI](https://openai.com/) for the GPT model.
- [Firebase](https://firebase.google.com/) for database and authentication.

---
