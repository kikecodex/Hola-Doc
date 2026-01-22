from engine.rag_engine import RagEngine

rag = RagEngine()
query = "Según la Opinión N° 008-2026 de la OECE, ¿cuál es el criterio exacto sobre la participación de la Junta de Resolución de Disputas?"
print(f"Query: {query}")
print("-" * 50)
results = rag.search(query, k=5)

if results:
    for i, res in enumerate(results):
        print(f"Result {i+1}:")
        print(f"Content: {res[:200]}...") # Print first 200 chars of the string
        print("-" * 50)
else:
    print("No results found.")
