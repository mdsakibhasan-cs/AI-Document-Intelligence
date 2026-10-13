from src.document_classifier import DocumentClassifier


def test_classifier_creation():

    classifier = DocumentClassifier()

    assert classifier.classifier is not None


def test_classification():

    classifier = DocumentClassifier()

    result = classifier.classify(
        """
        This paper presents a machine learning approach
        for vulnerability detection in embedded systems.
        """
    )

    assert "category" in result
    assert "confidence" in result