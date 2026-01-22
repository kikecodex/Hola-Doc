from engine.rag_engine import RagEngine
import re

def inspect_chroma():
    print("🕵️ INSPECTING CHROMA DB FOR ARTICLE 100")
    print("========================================")
    
    rag = RagEngine()
    
    # Access the collection directly (if possible) or use a dummy search with huge K
    # Chroma doesn't allow easy "get all", so we search for "." with k=2000
    
    print("📚 Retrieving ALL chunks (limit 2000)...")
    try:
        results = rag.vector_store.similarity_search(".", k=2000)
    except Exception as e:
        print(f"Error retrieving chunks: {e}")
        return

    print(f"📊 Total retrieved: {len(results)}")
    
    target_match = None
    count = 0
    
    for i, doc in enumerate(results):
        content = doc.page_content
        # Look for the specific header found in the PDF check
        # "Artículo 100. Condiciones generales"
        
        # Normalize whitespace for check
        norm_content = " ".join(content.split())
        
        if "Artículo 100" in content:
            count += 1
            print(f"\n[Candidate {count}] ID: {i}")
            print(f"Context: ...{content[max(0, content.find('Artículo 100')-50):content.find('Artículo 100')+100]}...")
            
            if "Condiciones generales" in content:
                print("✅✅✅ FOUND THE EXACT HEADER CHUNK!")
                target_match = doc
                # Print full content
                print("-" * 20)
                print(content)
                print("-" * 20)

    if not target_match:
        print("\n❌ CRITICAL: The chunk for 'Artículo 100. Condiciones generales' is NOT in the vector store.")
    else:
        print("\n✅ The chunk EXISTS. The issue is retrieval ranking.")

if __name__ == "__main__":
    inspect_chroma()
