from document_processor import extract_text
from text_processor import clean_text, chunk_text
from vector_search import VectorSearch
from qa_engine import QAEngine

file_path = "data/sample.pdf"

# Extract text
text = extract_text(file_path)

# Clean text
cleaned_text = clean_text(text)

# Create chunks
chunks = chunk_text(cleaned_text)

print("Document processed successfully!")
print("-" * 50)

print(f"Total characters: {len(cleaned_text)}")
print(f"Total chunks: {len(chunks)}")

print("\nFirst chunk:")
print("-" * 50)
print(chunks[0])
from vector_search import VectorSearch


# Build semantic search index
search_engine = VectorSearch()
search_engine.build_index(chunks)

# Test question
query = "How does AIM handle interrupts?"

results = search_engine.search(query, top_k=3)

print("\nSemantic Search Results:")
print("=" * 50)

for i, result in enumerate(results, start=1):
    print(f"\nResult {i} | Score: {result['score']:.4f}")
    print("-" * 50)
    print(result["text"][:1000])
    # Build QA engine
qa_engine = QAEngine()

# Generate answer
answer = qa_engine.answer_question(
    query,
    results
)

print("\nAI Answer:")
print("=" * 50)
print(answer)