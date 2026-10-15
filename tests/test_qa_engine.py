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

def test_objective_extraction_avoids_lessons_learned():
    search_results = [
        {
            "score": 0.95,
            "text": (
                "Lessons Learned. Recall the three questions "
                "we aim to answer in this paper: 1."
            ),
        },
        {
            "score": 0.90,
            "text": (
                "The main objective of this paper is to introduce "
                "a method for generating tests for embedded C "
                "programs with hardware-aware constraints."
            ),
        },
    ]

    qa_engine = QAEngine()

    answer = qa_engine.answer_question(
        "What is the main goal of this paper?",
        search_results
    )

    assert "lessons learned" not in answer.lower()
    assert "main objective" in answer.lower() or "generating tests" in answer.lower()

def test_objective_extraction_prefers_paper_goal_over_component_goal():
    search_results = [
        {
            "score": 0.95,
            "text": (
                "The main goal of the IRQ modeling is to determine "
                "the type and status of an IRQ."
            ),
        },
        {
            "score": 0.90,
            "text": (
                "In this paper, we present AidFuzzer, an adaptive "
                "interrupt-driven firmware fuzzing method, to tackle "
                "the interrupt triggering problem."
            ),
        },
    ]

    qa_engine = QAEngine()

    answer = qa_engine.answer_question(
        "What is the main goal of this paper?",
        search_results
    )

    assert "AidFuzzer" in answer
    assert "interrupt triggering problem" in answer
    assert "IRQ modeling" not in answer
