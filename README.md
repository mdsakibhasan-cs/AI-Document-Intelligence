# 📄 AI-Powered Document Intelligence

An AI-powered document intelligence system for processing PDF and DOCX documents, extracting and cleaning text, classifying documents, generating extractive summaries, performing semantic search, and answering questions using retrieved document context.

---

## 🚀 Features

- 📕 PDF document support
- 📘 DOCX document support
- 🔍 OCR support for scanned PDF documents
- 🧹 Automated text cleaning
- ✂️ Overlapping text chunking
- 🧠 Sentence-transformer embeddings
- 🔎 Semantic document search
- ⚡ FAISS vector similarity search
- 🏷️ Transformer-based zero-shot document classification
- 📝 Extractive document summarization
- 🤖 Source-grounded question answering
- 📚 Relevant source retrieval with similarity scores
- 📊 Document processing statistics
- 🌐 Interactive Streamlit web interface
- 📝 Application logging and error handling
- 🧪 Automated pytest test suite
- 📂 Multiple PDF/DOCX upload support

---

## 🏗️ System Architecture

```text
                    Document Upload
                           │
                           ▼
                PDF / DOCX Extraction
                           │
                           ▼
                  OCR for Scanned PDFs
                           │
                           ▼
                     Text Cleaning
                           │
                           ▼
                Document Classification
                           │
                           ▼
                    Text Chunking
                           │
                           ▼
                 Sentence Embeddings
                           │
                           ▼
                  FAISS Vector Index
                           │
                           ▼
                   Semantic Search
                           │
                           ▼
              Source-Grounded Q&A
                           │
                           ▼
              Extractive Summarization
```

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Interactive web application |
| PyMuPDF | PDF text extraction |
| python-docx | DOCX text extraction |
| Tesseract OCR | OCR for scanned PDF pages |
| pytesseract | Python interface for Tesseract |
| pdf2image | Convert PDF pages to images for OCR |
| Poppler | PDF rendering for OCR |
| Pillow | Image processing |
| Sentence Transformers | Text embedding generation |
| FAISS | Vector similarity search |
| Hugging Face Transformers | Zero-shot document classification |
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
│   ├── document_classifier.py
│   ├── text_processor.py
│   ├── vector_search.py
│   ├── qa_engine.py
│   ├── summary_engine.py
│   ├── logger.py
│   └── main.py
│
├── tests/
│   ├── test_document_processor.py
│   ├── test_document_classifier.py
│   ├── test_text_processor.py
│   ├── test_vector_search.py
│   ├── test_qa_engine.py
│   ├── test_summary_engine.py
│   └── test_logger.py
│
├── screenshots/
│   ├── app-overview.png
│   └── question-answering.png
│
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
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

#### Windows PowerShell

```powershell
.venv\Scripts\activate
```

#### Windows Command Prompt

```cmd
.venv\Scripts\activate
```

### 4. Install Python dependencies

```bash
pip install -r requirements.txt
```

---

## 🔍 OCR Setup

Scanned PDF OCR requires:

- Tesseract OCR
- Poppler

The application uses locally installed Tesseract and Poppler binaries when a PDF page does not contain extractable text.

### Important

The Tesseract and Poppler paths are environment-specific.

When running the project on another computer, configure the corresponding paths in:

```text
src/document_processor.py
```

---

## ▶️ Running the Application

Start the Streamlit application with:

```bash
streamlit run app/app.py --server.fileWatcherType none
```

The application will open in your default web browser.

Local address:

```text
http://localhost:8501
```

---

## 📖 How It Works

### 1. Document Upload

Users can upload one or more PDF or DOCX documents through the Streamlit web interface.

### 2. Document Text Extraction

PDF documents are processed using PyMuPDF, while DOCX documents are processed using python-docx.

### 3. OCR for Scanned PDFs

When a PDF page does not contain extractable text, the system automatically attempts OCR.

The page is converted into an image using `pdf2image` and Poppler, and Tesseract OCR extracts the text.

This allows the system to process scanned and image-based PDF pages.

### 4. Text Cleaning

Extracted text is cleaned before further processing.

The cleaning stage handles:

- Unnecessary whitespace
- Broken line structures
- Hyphenated line breaks
- PDF extraction artifacts
- Unwanted numeric-only lines
- Figure and table labels
- Common document formatting noise

### 5. Document Classification

The system includes a transformer-based zero-shot document classification module.

The classifier uses:

```text
facebook/bart-large-mnli
```

Documents can be classified into categories including:

- Research Paper
- Business Document
- Technical Report
- Legal Document
- Educational Material
- Financial Report
- News Article
- Resume / CV
- Other

### 6. Text Chunking

After cleaning, each document is divided into smaller overlapping text chunks.

This allows the retrieval system to work with manageable sections of document content.

### 7. Sentence Embeddings

Each text chunk is converted into a numerical vector representation using:

```text
sentence-transformers/all-MiniLM-L6-v2
```

These embeddings represent the semantic meaning of the document content.

### 8. Vector Indexing

The generated embeddings are stored in a FAISS vector index.

The project uses FAISS inner-product similarity with normalized embeddings for vector retrieval.

### 9. Semantic Search

When a user enters a question, the question is converted into an embedding and compared with the indexed document chunks.

The retrieval system combines:

- 70% semantic similarity
- 30% keyword overlap

to rank relevant document sections.

### 10. Source-Grounded Question Answering

The retrieved document sections are passed to the question-answering engine.

The current system generates answers from the retrieved document context rather than relying on an external generative LLM.

Relevant source sections and similarity scores are also displayed in the interface.

### 11. Extractive Document Summarization

The summarization module generates a concise extractive summary from the processed document.

It identifies important sentences using signals related to:

- Problems and motivation
- Main contributions
- Methods and mechanisms
- Evaluation and results

The module also removes duplicate or low-quality sentences before producing the final summary.

---

## 🖥️ Application Interface

The application provides an interactive web interface built with Streamlit.

Users can:

- 📂 Upload one or more PDF/DOCX documents
- 📊 View document processing statistics
- 🏷️ View document classification results
- 📝 Read generated document summaries
- 🔎 Ask natural-language questions
- 🤖 Receive source-grounded answers
- 📚 View relevant document sources
- 📈 Inspect similarity scores

### 📊 Document Overview

The application provides an interface for uploading and analyzing documents, displaying processing information, classification results, and generated summaries.

![Application Overview](screenshots/app-overview.png)

### 🔎 Question Answering

Users can ask natural-language questions about the uploaded documents.

The system performs semantic retrieval using FAISS and returns a context-based answer together with relevant document sections and similarity scores.

![Question Answering](screenshots/question-answering.png)

---

## 🔬 Example Query

After uploading a document, users can ask questions related to its content.

Example:

> How does AIM handle interrupts?

The system performs semantic search across the uploaded document content, retrieves relevant sections, and generates a source-grounded answer.

The retrieved sources and their similarity scores are also displayed.

---

## 🧪 Testing

The project includes an automated pytest test suite covering the major components of the system.

The test suite covers:

- Document processing
- PDF extraction
- OCR-aware document processing
- DOCX extraction
- Text cleaning
- Text chunking
- Semantic vector search
- Document classification
- Question answering
- Document summarization
- Logging

### Verified Test Result

```text
20 passed
```

---

## 🎯 Project Goals

The main goals of this project are to:

- Build a practical document intelligence system for PDF and DOCX files
- Support text-based and scanned PDF documents
- Automatically classify uploaded documents
- Generate concise extractive summaries
- Enable semantic search over unstructured document content
- Retrieve relevant information based on query meaning
- Provide source-grounded question answering
- Demonstrate sentence embeddings and vector similarity search
- Provide an interactive web interface
- Maintain a modular architecture that can be extended with additional AI capabilities

---

## 🔮 Future Improvements

Potential future improvements include:

- 🤖 Integration of a generative LLM for more advanced question answering
- 💬 Conversational multi-turn document chat
- 📚 Advanced multi-document retrieval and cross-document analysis
- 🌐 Support for additional document formats
- ⚡ Advanced retrieval and reranking strategies
- 🔐 User authentication and document access control
- ☁️ Cloud-based document storage and deployment
- 📊 Advanced document analytics and visualization
- 🌍 Improved multilingual OCR configuration
- 🚀 Production-oriented deployment and scalability improvements

---

## 📌 Current Limitations

The current version has the following limitations:

- OCR depends on locally installed Tesseract OCR and Poppler binaries.
- OCR accuracy depends on the quality, resolution, and layout of scanned documents.
- The current question-answering module is source-grounded and does not use a generative LLM.
- Answer quality depends on the relevance and quality of retrieved document chunks.
- Document classification uses a predefined set of zero-shot categories.
- Authentication and access control are not currently included.
- The application is primarily designed as a local prototype and has not yet been deployed as a production service.
- Large documents and multiple uploaded documents may require more computational resources for embedding and indexing.

---

## 👨‍💻 Author

**Md Sakib Hasan**

Computer Science and Technology  
Nantong University, China

### Areas of Interest

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

This project is licensed under the **MIT License**.