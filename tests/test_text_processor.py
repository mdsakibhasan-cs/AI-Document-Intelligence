from src.text_processor import clean_text, chunk_text


def test_clean_text_removes_extra_spaces():
    text = "Hello     world\n\nThis   is   a test."

    result = clean_text(text)

    assert result == "Hello world This is a test."


def test_clean_text_removes_page_numbers():
    text = "This is a document.\n\n12\n\nAnother section."

    result = clean_text(text)

    assert "12" not in result


def test_chunk_text_creates_chunks():
    text = " ".join(["word"] * 250)

    chunks = chunk_text(
        text,
        chunk_size=100,
        overlap=20
    )

    assert len(chunks) > 1


def test_chunk_text_preserves_content():
    text = "This is an important document about embedded systems."

    chunks = chunk_text(
        text,
        chunk_size=20,
        overlap=5
    )

    combined_text = " ".join(chunks)

    assert "embedded systems" in combined_text