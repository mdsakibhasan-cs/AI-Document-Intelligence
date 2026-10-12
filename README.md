# 📄 AI-Powered Document Intelligence

An AI-powered document analysis system that allows users to upload PDF or DOCX documents, search their content semantically, ask questions, and generate concise document summaries.

---

## 🚀 Features

- 📕 PDF document support
- 📘 DOCX document support
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

---

## 🏗️ System Architecture

```text
Document Upload
      ↓
Text Extraction
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
---

## 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| Python | Core programming language |
| Streamlit | Web application interface |
| PyPDF | PDF text extraction |
| python-docx | DOCX text extraction |
| Sentence Transformers | Text embeddings |
| FAISS | Vector similarity search |
| NumPy | Numerical processing |

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
│   └── summary_engine.py
│
├── data/
│   └── uploads/
│
├── tests/
│
├── screenshots/
│
├── .gitignore
├── requirements.txt
├── README.md
└── LICENSE

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/mdsakibhasan-cs/AI-Document-Intelligence.git
cd AI-Document-Intelligence

### 2. Create a virtual environment

```bash
python -m venv .venv

### 3. Activate the virtual environment

#### Windows

```bash
.venv\Scripts\activate

### 4. Install dependencies

```bash
pip install -r requirements.txt

---

## ▶️ Running the Application

Start the Streamlit application with:

```bash
streamlit run app/app.py --server.fileWatcherType none

The application will open in your browser.

You can also access it at:

```text
http://localhost:8501

---

## 📖 How It Works

The system processes uploaded documents through the following pipeline:

### 1. Document Upload

Users can upload PDF or DOCX documents through the Streamlit web interface.

### 2. Text Extraction

The system extracts readable text from the uploaded document using PyPDF for PDF files and python-docx for DOCX files.

### 3. Text Cleaning

Extracted text is cleaned by removing unnecessary formatting, page artifacts, broken lines, and other unwanted text fragments.

### 4. Text Chunking

The cleaned document is divided into smaller overlapping text chunks to make semantic search more effective.

### 5. Sentence Embeddings

Each text chunk is converted into a numerical vector representation using Sentence Transformers.

### 6. Vector Indexing

The generated embeddings are stored in a FAISS vector index for efficient similarity-based retrieval.

### 7. Semantic Search

When a user asks a question, the system converts the question into an embedding and retrieves the most semantically relevant document chunks.

### 8. Question Answering

The retrieved document content is analyzed to generate a context-based answer to the user's question.

### 9. Document Summarization

The system analyzes the document content and selects important sentences to generate a concise summary.

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

---
### 📊 Document Overview

The application provides a clean interface for uploading and analyzing PDF and DOCX documents. It displays document statistics, processing status, and an automatically generated summary.

![Document Overview](screenshots/app-overview.png)

### 🔎 Question Answering

Users can ask natural-language questions about the uploaded document. The system performs semantic search using FAISS and returns an answer together with the most relevant document sections and similarity scores.

![Question Answering](screenshots/question-answering.png)

## 🔬 Example Query

After uploading a document, users can ask questions related to its content.

Example:

**Question:**

> How does AIM handle interrupts?

The system performs semantic search across the document, retrieves the most relevant sections, and generates a context-based answer.

The interface also displays the retrieved source sections along with their similarity scores.

---

## 🎯 Project Goals

The main goals of this project are to:

- Build a practical document intelligence system for PDF and DOCX files
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

- 🔍 OCR support for scanned PDF documents
- 🗂️ Automatic document classification
- 🤖 Advanced LLM-based question answering
- 💬 Conversational multi-turn document chat
- 🌐 Support for additional document formats
- ⚡ Improved retrieval and ranking strategies
- 📚 Multi-document semantic search
- 🔐 User authentication and document access control
- ☁️ Cloud-based document storage and deployment
- 📊 Advanced document analytics and visualization

---

## 📌 Current Limitations

The current version of the system has the following limitations:

- Scanned PDFs without an embedded text layer are not yet supported through OCR.
- The current question-answering module uses retrieved document content rather than a large language model.
- Answer quality depends on the quality and relevance of the retrieved text chunks.
- The system currently processes one uploaded document at a time.
- Document classification is not yet implemented.
- Authentication and access control are not currently included.
- The application is designed primarily as a local prototype and has not yet been deployed as a production service.

---

## 👨‍💻 Author

**Hasan Md Sakib**

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