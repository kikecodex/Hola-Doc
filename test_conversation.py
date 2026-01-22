from engine.conversation import ConversationEngine
import time

def test():
    print("Initializing Conversation Engine...")
    engine = ConversationEngine()
    
    query = "Según la Opinión N° 008-2026 de la OECE, ¿cuál es el criterio exacto sobre la participación de la Junta de Resolución de Disputas? Detalla los supuestos"
    print(f"\nUser Query: {query}\n")
    
    response = engine.process(query)
    print("\n--- RESPONSE START ---")
    print(response)
    print("--- RESPONSE END ---")

if __name__ == "__main__":
    test()
