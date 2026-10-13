from src.vector_search import VectorSearch


def test_vector_search_builds_index():
    chunks = [
        "AIM handles interrupts using just-in-time interrupt firing.",
        "Dynamic symbolic execution improves firmware analysis.",
        "FAISS performs efficient vector similarity search.",
    ]

    search_engine = VectorSearch()
    search_engine.build_index(chunks)

    assert search_engine.index is not None
    assert len(search_engine.chunks) == 3


def test_vector_search_returns_relevant_results():
    chunks = [
        "AIM handles interrupts using just-in-time interrupt firing.",
        "Dynamic symbolic execution improves firmware analysis.",
        "FAISS performs efficient vector similarity search.",
    ]

    search_engine = VectorSearch()
    search_engine.build_index(chunks)

    results = search_engine.search(
        "How does AIM handle interrupts?",
        top_k=2
    )

    assert len(results) == 2
    assert all("score" in result for result in results)
    assert all("text" in result for result in results)

    assert "interrupt" in results[0]["text"].lower()


def test_vector_search_respects_top_k():
    chunks = [
        "Document about embedded systems.",
        "Document about cybersecurity.",
        "Document about machine learning.",
        "Document about software engineering.",
    ]

    search_engine = VectorSearch()
    search_engine.build_index(chunks)

    results = search_engine.search(
        "embedded systems",
        top_k=2
    )

    assert len(results) == 2