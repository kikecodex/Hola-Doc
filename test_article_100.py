from engine.rag_engine import RagEngine

def debug_article_100():
    print("🔍 DEBUGGING ARTICLE 100 RETRIEVAL")
    print("==================================")
    
    rag = RagEngine()
    
    queries = [
        "analiza y explicame el articulo 100 del reglamento",
        "Artículo 100",
        "Art. 100"
    ]
    
    for query in queries:
        print(f"\n❓ Testing Query: '{query}'")
        print("-" * 40)
        
        results = rag.search(query)
        
        if not results:
            print("❌ No results found.")
            continue
            
        print(f"📄 Found {len(results)} chunks.")
        for i, doc_content in enumerate(results):
            print(f"\n[Chunk {i+1}] Start content:")
            print(doc_content[:300].replace("\n", " ") + "...")
            
            # Check if it actually contains "100"
            if "100" in doc_content:
                print("   ✅ Contains '100'")
            else:
                print("   ⚠️ Does NOT contain '100'")

if __name__ == "__main__":
    debug_article_100()
