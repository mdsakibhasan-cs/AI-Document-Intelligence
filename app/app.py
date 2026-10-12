import sys
from pathlib import Path

import streamlit as st


# =========================================================
# PROJECT PATH
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"

sys.path.append(str(SRC_DIR))


from document_processor import extract_text
from text_processor import clean_text, chunk_text
from vector_search import VectorSearch
from qa_engine import QAEngine
from summary_engine import SummaryEngine


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
    'Upload documents, search their content semantically, and ask questions using AI-powered document analysis.'
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
        **Text Extraction**
        ↓  
        **Text Cleaning**
        ↓  
        **Chunking**
        ↓  
        **Embeddings**
        ↓  
        **FAISS Vector Search**
        ↓  
        **Question Answering**
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

uploaded_file = st.file_uploader(
    "Choose a PDF or DOCX file",
    type=["pdf", "docx"],
    help="Upload a document to analyze its content."
)


# =========================================================
# PROCESS DOCUMENT
# =========================================================

if uploaded_file is not None:

    upload_dir = ROOT_DIR / "data" / "uploads"
    upload_dir.mkdir(
        parents=True,
        exist_ok=True
    )

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
        "🔄 Extracting and indexing document..."
    ):

        try:

            # Extract text
            text = extract_text(file_path)

            # Clean text
            cleaned_text = clean_text(text)

            # Create chunks
            chunks = chunk_text(cleaned_text)

            # Build vector search index
            search_engine = VectorSearch()
            search_engine.build_index(chunks)

            qa_engine = QAEngine()
            summary_engine = SummaryEngine()

            processing_success = True

            

        except Exception as e:

            processing_success = False

            st.error(
                f"❌ Error while processing document: {e}"
            )


    # =====================================================
    # DOCUMENT INFORMATION
    # =====================================================

    if processing_success:

        st.success(
            "🎉 Document processed and indexed successfully!"
        )

        st.subheader("📊 Document Overview")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Characters",
                f"{len(cleaned_text):,}"
            )

        with col2:
            st.metric(
                "Chunks",
                len(chunks)
            )

        with col3:
            st.metric(
                "File Type",
                file_path.suffix.upper()
            )

        with col4:
            file_size_mb = file_path.stat().st_size / (
                1024 * 1024
            )

            st.metric(
                "File Size",
                f"{file_size_mb:.2f} MB"
            )


        st.divider()
                # =================================================
        # DOCUMENT SUMMARY
        # =================================================

        st.subheader("📝 Document Summary")

        with st.spinner("📝 Generating document summary..."):

            summary = summary_engine.summarize(
                cleaned_text,
                max_sentences=4
            )
        st.write(summary)
    
        

        st.divider()


        # =================================================
        # QUESTION ANSWERING
        # =================================================

        st.subheader("🔎 Ask Questions About Your Document")

        question = st.text_input(
            "Enter your question",
            placeholder="Example: How does AIM handle interrupts?"
        )


        if question.strip():

            with st.spinner(
                "🤖 Searching the document..."
            ):

                results = search_engine.search(
                    question,
                    top_k=3
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

                with st.expander(
                    f"Source {i}  •  Similarity Score: {score:.4f}"
                ):

                    st.write(
                        result["text"]
                    )


            # =============================================
            # SEARCH EXPLANATION
            # =============================================

            st.info(
                "💡 The answer is generated from the most "
                "semantically relevant sections of your uploaded document."
            )


        else:
            st.info(
               "💡 Enter a question above to search and analyze your document."
            )