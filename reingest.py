from engine.rag_engine import RagEngine

print("Initializing RagEngine...")
rag = RagEngine()
print("Ingesting documents...")
result = rag.ingest_documents()
print(f"Result: {result}")
