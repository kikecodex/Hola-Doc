from engine.conversation import ConversationEngine

def test_regulation_retrieval():
    print("📜 TESTING REGLAMENTO RETRIEVAL")
    print("===============================")
    
    engine = ConversationEngine()
    
    query = "analizame el articulo 44 del reglamento"
    print(f"❓ Query: {query}")
    print("-" * 50)
    
    response = engine.process(query)
    
    print("\n🤖 RESPONSE:")
    print(response)
    print("-" * 50)
    
    # Check for keywords specific to Art. 44 of the new Regulation
    # Art. 44 usually talks about "Requisitos de Calificación" or similar in procurement context
    expected_keywords = ["capacidad legal", "capacidad técnica", "profesional", "experiencia"]
    
    found = any(k in response.lower() for k in expected_keywords)
    if found:
        print("✅ SUCCESS: Found keywords related to Article 44 content.")
    else:
        print("⚠️ WARNING: content might not be specific enough. Check manually.")

if __name__ == "__main__":
    test_regulation_retrieval()
