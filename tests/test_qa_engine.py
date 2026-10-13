from src.qa_engine import QAEngine


def test_qa_engine_returns_answer():
    search_results = [
        {
            "score": 0.95,
            "text": (
                "AIM handles interrupts using a just-in-time "
                "interrupt firing mechanism."
            ),
        },
        {
            "score": 0.85,
            "text": (
                "AIM improves the coverage of interrupt-dependent "
                "firmware paths."
            ),
        },
    ]

    qa_engine = QAEngine()

    answer = qa_engine.answer_question(
        "How does AIM handle interrupts?",
        search_results
    )

    assert isinstance(answer, str)
    assert len(answer) > 0
    assert "interrupt" in answer.lower()


def test_qa_engine_handles_empty_results():
    qa_engine = QAEngine()

    answer = qa_engine.answer_question(
        "How does AIM handle interrupts?",
        []
    )

    assert answer == "I could not find relevant information in the uploaded document."


def test_qa_engine_uses_relevant_content():
    search_results = [
        {
            "score": 0.90,
            "text": (
                "The system uses dynamic symbolic execution "
                "to analyze firmware behavior."
            ),
            },
        {
            "score": 0.88,
            "text": (
                "AIM uses just-in-time interrupt firing "
                "to handle interrupt-dependent paths."
            ),
        },
    ]

    qa_engine = QAEngine()

    answer = qa_engine.answer_question(
        "How does AIM handle interrupts?",
        search_results
    )

    assert "interrupt" in answer.lower()
    assert "AIM" in answer or "aim" in answer.lower()