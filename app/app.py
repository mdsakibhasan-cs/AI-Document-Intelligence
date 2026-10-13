import sys
from pathlib import Path

import streamlit as st


# =========================================================
# PROJECT PATH
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"

sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(SRC_DIR))


from document_processor import extract_text
from text_processor import clean_text, chunk_text
from vector_search import VectorSearch
from qa_engine import QAEngine
from summary_engine import SummaryEngine
from document_classifier import DocumentClassifier


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI Document Intelligence",
    page_icon="📄",
    layout="wide"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 2.4rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        font-size: 1.05rem;
        color: #666;
        margin-bottom: 1.5rem;
    }

    .answer-box {
        padding: 1.2rem !important;
        border-radius: 12px !important;
        border: 1px solid #cccccc !important;
        background-color: #f8f9fa !important;
        color: #222222 !important;
        line-height: 1.7 !important;
        font-size: 1.05rem !important;
    }

    .answer-box * {
        color: #222222 !important;
    }

    .section-title {
        font-size: 1.3rem;
        font-weight: 600;
        margin-top: 1rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">📄 AI-Powered Document Intelligence</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Upload documents, classify their type, search their content semantically, '
    'and ask questions using AI-powered document analysis.'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("⚙️ Document Intelligence")

    st.write(
        "Supported document formats:"
    )

    st.markdown(
        """
        - 📕 PDF
        - 📘 DOCX
        """
    )

    st.divider()

    st.write("### 🔧 Pipeline")

    st.markdown(
        """
        **Document**
        ↓  
        **Text Extraction + OCR**
        ↓  
        **Text Cleaning**
        ↓  
        **AI Document Classification**
        ↓  
        **Chunking**
        ↓  
        **Embeddings**
        ↓  
        **FAISS Vector Search**
        ↓  
        **Question Answering**
        ↓  
        **Summarization**
        """
    )

    st.divider()

    st.caption(
        "AI Document Intelligence System"
    )


# =========================================================
# FILE UPLOAD
# =========================================================

st.subheader("📂 Upload Your Document")

uploaded_files = st.file_uploader(
    "Choose PDF or DOCX files",
    type=["pdf", "docx"],
    accept_multiple_files=True,
    help="Upload one or more documents to analyze."
)


# =========================================================
# DOCUMENT CLASSIFIER
# =========================================================

@st.cache_resource
def load_document_classifier():
    """
    Load and cache the document classification model.

    Streamlit reruns the application frequently, so caching
    prevents the transformer model from loading repeatedly.
    """

    return DocumentClassifier()


# =========================================================
# PROCESS DOCUMENT
# =========================================================

if uploaded_files:

    upload_dir = ROOT_DIR / "data" / "uploads"

    upload_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    for uploaded_file in uploaded_files:

        file_path = upload_dir / uploaded_file.name

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(
            f"✅ Uploaded successfully: {uploaded_file.name}"
        )



    # -----------------------------------------------------
    # PROCESSING
    # -----------------------------------------------------

    with st.spinner(
        "🔄 Extracting, classifying, and indexing documents..."
    ):

        try:

            documents = []
            all_chunks = []
            all_sources = []

            classifier = load_document_classifier()

            # -------------------------------------------------
            # PROCESS EACH DOCUMENT
            # -------------------------------------------------

            for uploaded_file in uploaded_files:

                file_path = upload_dir / uploaded_file.name

                # STEP 1 — TEXT EXTRACTION
                text = extract_text(file_path)

                # STEP 2 — TEXT CLEANING
                cleaned_text = clean_text(text)

                # STEP 3 — DOCUMENT CLASSIFICATION
                classification_result = classifier.classify(
                    cleaned_text
                )

                # STEP 4 — CREATE CHUNKS
                chunks = chunk_text(cleaned_text)

                # Store document information
                documents.append({
                    "name": uploaded_file.name,
                    "file_path": file_path,
                    "cleaned_text": cleaned_text,
                    "chunks": chunks,
                    "classification": classification_result
                })

                # Add chunks to global search collection
                all_chunks.extend(chunks)

                # Remember which document each chunk belongs to
                all_sources.extend(
                    [uploaded_file.name] * len(chunks)
                )

            # -------------------------------------------------
            # BUILD VECTOR SEARCH INDEX
            # -------------------------------------------------

            search_engine = VectorSearch()

            search_engine.build_index(
                all_chunks,
                all_sources
            )

            # -------------------------------------------------
            # INITIALIZE QA + SUMMARY
            # -------------------------------------------------

            qa_engine = QAEngine()

            summary_engine = SummaryEngine()

            processing_success = True

        except Exception as e:

            processing_success = False

            st.error(
                f"❌ Error while processing documents: {e}"
            )


    # =====================================================
    # DOCUMENT INFORMATION
    # =====================================================

    if processing_success:

        st.success(
            "🎉 All documents processed, classified, and indexed successfully!"
        )


        # =================================================
        # DOCUMENT CLASSIFICATION
        # =================================================

        st.subheader("🤖 AI Document Classification")

        for document in documents:

            classification = document["classification"]

            st.markdown(
                f"### 📄 {document['name']}"
            )

            class_col1, class_col2 = st.columns(2)

            with class_col1:

                st.metric(
                    "Document Type",
                    classification["category"]
                )

            with class_col2:

                st.metric(
                    "Classification Confidence",
                    f"{classification['confidence'] * 100:.2f}%"
                )

            with st.expander(
                "View all classification predictions"
            ):

                predictions = classification["all_predictions"]

                for label, score in predictions.items():

                    st.write(
                        f"**{label}** — {score * 100:.2f}%"
                    )

            st.divider()


        # =================================================
        # DOCUMENT OVERVIEW
        # =================================================

        st.subheader("📊 Document Overview")

        total_characters = sum(
            len(document["cleaned_text"])
            for document in documents
        )

        total_chunks = len(all_chunks)

        total_file_size = sum(
            document["file_path"].stat().st_size
            for document in documents
        )

        total_file_size_mb = total_file_size / (
            1024 * 1024
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Documents",
                len(documents)
            )

        with col2:

            st.metric(
                "Characters",
                f"{total_characters:,}"
            )

        with col3:

            st.metric(
                "Total Chunks",
                total_chunks
            )

        with col4:

            st.metric(
                "Total Size",
                f"{total_file_size_mb:.2f} MB"
            )

        st.divider()


        # =================================================
        # DOCUMENT SUMMARIES
        # =================================================

        st.subheader("📝 Document Summaries")

        for document in documents:

            with st.expander(
                f"📄 Summary — {document['name']}"
            ):

                with st.spinner(
                    f"📝 Generating summary for {document['name']}..."
                ):

                    summary = summary_engine.summarize(
                        document["cleaned_text"],
                        max_sentences=4
                    )

                st.write(summary)

        st.divider()


        # =================================================
        # QUESTION ANSWERING
        # =================================================

        st.subheader(
            "🔎 Ask Questions About Your Document"
        )

        question = st.text_input(
            "Enter your question",
            placeholder="Example: How does ADFEmu improve code coverage?"
        )

        if question.strip():

            with st.spinner(
                "🤖 Searching the document..."
            ):
                results = search_engine.search(
                    question,
                    top_k=12
                )

                answer = qa_engine.answer_question(
                    question,
                    results
                )

            # =============================================
            # ANSWER
            # =============================================

            st.markdown(
                '<div class="section-title">🤖 AI Answer</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f"""
                <div class="answer-box">
                {answer}
                </div>
                """,
                unsafe_allow_html=True
            )

            # =============================================
            # SOURCES
            # =============================================

            st.markdown(
                '<div class="section-title">📚 Relevant Sources</div>',
                unsafe_allow_html=True
            )

            for i, result in enumerate(
                results,
                start=1
            ):

                score = result["score"]
                source = result["source"]

                with st.expander(
                    f"Source {i}  •  {source}  •  Similarity Score: {score:.4f}"
                ):

                    st.write(
                        result["text"]
                    )

            # =============================================
            # SEARCH EXPLANATION
            # =============================================

            st.info(
                "💡 The answer is generated from the most "
                "semantically relevant sections of your uploaded documents."
            )

        else:

            st.info(
                "💡 Enter a question above to search and analyze your documents."
            )