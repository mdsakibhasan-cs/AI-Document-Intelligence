# 📄 AI-Powered Document Intelligence

An AI-powered document analysis system that allows users to upload PDF or DOCX documents, extract and process their content, perform semantic search, ask questions, and generate concise document summaries.

---

## 🚀 Features

- 📕 PDF document support
- 📘 DOCX document support
- 🔍 OCR support for scanned PDF documents
- 🧹 Automated text cleaning
- ✂️ Intelligent text chunking
- 🧠 Sentence-transformer embeddings
- 🔎 Semantic document search
- ⚡ FAISS vector similarity search
- 🤖 Context-based question answering
- 📝 Automatic document summarization
- 🌐 Interactive Streamlit web interface
- 📊 Document processing statistics
- 📚 Relevant source retrieval with similarity scores
- 📝 Application logging and error handling
- 🧪 Automated test suite

---

## 🏗️ System Architecture

```text
Document Upload
      ↓
Text Extraction
      ↓
OCR for Scanned PDFs
      ↓
Text Cleaning
      ↓
Text Chunking
      ↓
Sentence Embeddings
      ↓
FAISS Vector Index
      ↓
Semantic Search
      ↓
Question Answering
      ↓
Document Summary
```

---

## 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| Python | Core programming language |
| Streamlit | Web application interface |
| PyPDF | PDF text extraction |
| python-docx | DOCX text extraction |
| Tesseract OCR | OCR for scanned PDF pages |
| pytesseract | Python interface for Tesseract OCR |
| pdf2image | Convert PDF pages into images for OCR |
| Pillow | Image processing |
| Sentence Transformers | Text embeddings |
| FAISS | Vector similarity search |
| NumPy | Numerical processing |
| pytest | Automated testing |

---

## 📂 Project Structure

```text
AI-Document-Intelligence/
│
├── app/
│   └── app.py
│
├── src/
│   ├── document_processor.py
│   ├── text_processor.py
│   ├── vector_search.py
│   ├── qa_engine.py
│   ├── summary_engine.py
│   └── logger.py
│
├── data/
│   └── uploads/
│
├── tests/
│
├── screenshots/
│   ├── app-overview.png
│   └── question-answering.png
│
├── .gitignore
├── requirements.txt
├── README.md
└── LICENSE
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/mdsakibhasan-cs/AI-Document-Intelligence.git
cd AI-Document-Intelligence
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

#### Windows

```bash
.venv\Scripts\activate
```

### 4. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 5. OCR Requirements

Scanned PDF OCR requires:

- **Tesseract OCR**
- **Poppler**

On Windows, the application currently uses locally installed Tesseract and Poppler binaries.

> **Note:** The configured Windows paths are environment-specific. For deployment on another computer, Tesseract and Poppler paths may need to be configured for that environment.

---

## ▶️ Running the Application

Start the Streamlit application with:

```bash
streamlit run app/app.py --server.fileWatcherType none
```

The application will open in your browser.

You can also access it at:

```text
http://localhost:8501
```

---

## 📖 How It Works

The system processes uploaded documents through the following pipeline.

### 1. Document Upload

Users can upload PDF or DOCX documents through the Streamlit web interface.

### 2. Text Extraction

For regular PDF documents, the system extracts embedded text using PyPDF. DOCX documents are processed using python-docx.

### 3. OCR for Scanned PDFs

If a PDF page does not contain extractable text, the system automatically attempts OCR.

The PDF page is converted into an image using `pdf2image` and Poppler, and Tesseract OCR is used to extract the text from the image.

This allows the system to process scanned or image-based PDF pages.

### 4. Text Cleaning

Extracted text is cleaned by removing unnecessary formatting, page artifacts, broken lines, and other unwanted text fragments.

### 5. Text Chunking

The cleaned document is divided into smaller overlapping text chunks to make semantic search more effective.

### 6. Sentence Embeddings

Each text chunk is converted into a numerical vector representation using Sentence Transformers.

### 7. Vector Indexing

The generated embeddings are stored in a FAISS vector index for efficient similarity-based retrieval.

### 8. Semantic Search

When a user asks a question, the system converts the question into an embedding and retrieves the most semantically relevant document chunks.

### 9. Question Answering

The retrieved document content is analyzed to generate a context-based answer to the user's question.

### 10. Document Summarization

The system analyzes the processed document content and selects important sentences to generate a concise summary.

---

## 🖥️ Application Interface

The application provides an interactive web-based interface built with Streamlit.

Users can:

- 📂 Upload PDF or DOCX documents
- 📊 View document processing statistics
- 📝 Read an automatically generated document summary
- 🔎 Enter questions about the uploaded document
- 🤖 Receive context-based answers
- 📚 View relevant document sources
- 📈 Inspect similarity scores for retrieved content

### 📊 Document Overview

The application provides a clean interface for uploading and analyzing PDF and DOCX documents. It displays document statistics, processing status, and an automatically generated summary.

![Document Overview](screenshots/app-overview.png)

### 🔎 Question Answering

Users can ask natural-language questions about the uploaded document. The system performs semantic search using FAISS and returns an answer together with the most relevant document sections and similarity scores.

![Question Answering](screenshots/question-answering.png)

---

## 🔬 Example Query

After uploading a document, users can ask questions related to its content.

**Example question:**

> How does AIM handle interrupts?

The system performs semantic search across the document, retrieves the most relevant sections, and generates a context-based answer.

The interface also displays the retrieved source sections along with their similarity scores.

---

## 🎯 Project Goals

The main goals of this project are to:

- Build a practical document intelligence system for PDF and DOCX files
- Support both text-based and scanned PDF documents
- Enable semantic search over unstructured document content
- Retrieve relevant information based on the meaning of user queries
- Provide context-based question answering
- Generate concise summaries from lengthy documents
- Demonstrate the use of embeddings and vector similarity search
- Provide an interactive and user-friendly web interface
- Create a modular architecture that can be extended with additional AI capabilities

---

## 🔮 Future Improvements

The system can be further improved by adding:

- 🗂️ Automatic document classification
- 🤖 Advanced LLM-based question answering
- 💬 Conversational multi-turn document chat
- 🌐 Support for additional document formats
- ⚡ Improved retrieval and ranking strategies
- 📚 Multi-document semantic search
- 🔐 User authentication and document access control
- ☁️ Cloud-based document storage and deployment
- 📊 Advanced document analytics and visualization
- 🌍 Improved OCR configuration and multilingual OCR support

---

## 📌 Current Limitations

The current version of the system has the following limitations:

- OCR currently depends on locally installed Tesseract OCR and Poppler binaries.
- OCR accuracy depends on the quality, resolution, and layout of scanned documents.
- The current question-answering module uses retrieved document content rather than a large language model.
- Answer quality depends on the quality and relevance of the retrieved text chunks.
- The system currently processes one uploaded document at a time.
- Document classification is not yet implemented.
- Authentication and access control are not currently included.
- The application is designed primarily as a local prototype and has not yet been deployed as a production service.

---

## 👨‍💻 Author

**Md Sakib Hasan**

Computer Science and Technology  
Nantong University, China

Interested in:

- Artificial Intelligence
- Data Science
- Machine Learning
- Natural Language Processing
- Software Engineering
- Cyber Security
- Networking
- Embedded Systems
- Intelligent Systems

---

## 📄 License

This project is licensed under the MIT License.