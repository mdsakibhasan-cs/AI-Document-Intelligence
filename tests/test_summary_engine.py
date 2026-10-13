from src.summary_engine import SummaryEngine


def test_summary_engine_returns_summary():
    text = (
        "AIM is a dynamic firmware analysis framework. "
        "It supports unemulated MCU peripherals. "
        "AIM uses just-in-time interrupt firing. "
        "The system improves coverage of interrupt-dependent code."
    )

    summary_engine = SummaryEngine()

    summary = summary_engine.summarize(
        text,
        max_sentences=2
    )

    assert isinstance(summary, str)
    assert len(summary) > 0


def test_summary_engine_respects_max_sentences():
    text = (
        "AIM is a firmware analysis framework. "
        "It models interrupts during analysis. "
        "It improves firmware coverage. "
        "It supports MCU peripherals. "
        "It was evaluated on real-world firmware."
    )

    summary_engine = SummaryEngine()

    summary = summary_engine.summarize(
        text,
        max_sentences=2
    )

    sentences = [
        sentence.strip()
        for sentence in summary.split(".")
        if sentence.strip()
    ]

    assert len(sentences) <= 2


def test_summary_engine_handles_empty_text():
    summary_engine = SummaryEngine()

    summary = summary_engine.summarize(
        "",
        max_sentences=3
    )

    assert isinstance(summary, str)
    assert len(summary) > 0