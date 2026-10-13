"""
Document Classification Module

Classifies uploaded documents into predefined categories
using transformer-based zero-shot classification.
"""

from transformers import pipeline
from src.logger import get_logger


logger = get_logger(__name__)


class DocumentClassifier:
    """
    AI-based document classifier using Hugging Face transformers.
    """

    def __init__(self):
        logger.info("Loading document classification model...")

        self.classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )

        logger.info("Document classification model loaded successfully.")


    def classify(self, text: str):
        """
        Classify document text.

        Args:
            text (str): Document content

        Returns:
            dict: classification result
        """

        if not text or len(text.strip()) == 0:
            return {
                "category": "Unknown",
                "confidence": 0.0
            }


        candidate_labels = [
            "Research Paper",
            "Business Document",
            "Technical Report",
            "Legal Document",
            "Educational Material",
            "Financial Report",
            "News Article",
            "Resume / CV",
            "Other"
        ]


        result = self.classifier(
            text[:2000],
            candidate_labels
        )


        return {
            "category": result["labels"][0],
            "confidence": round(result["scores"][0], 4),
            "all_predictions": {
                label: round(score, 4)
                for label, score in zip(
                    result["labels"],
                    result["scores"]
                )
            }
        }