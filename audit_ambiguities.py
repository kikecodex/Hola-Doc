from engine.conversation import ConversationEngine
import time

def audit_ambiguities():
    print("🕵️ INICIANDO AUDITORÍA DE AMBIGÜEDADES")
    print("=======================================")
    
    engine = ConversationEngine()
    
    # Lista de casos de prueba diseñados para encontrar falsos positivos o clasificaciones erróneas
    test_cases = [
        # CASO 1: Coincidencia parcial en Respuestas Rápidas
        # Riesgo: Que "ley" o "vigencia" activen la respuesta de la Ley 32069 incorrectamente
        {
            "query": "Cual es la vigencia del poder del representante legal",
            "context": "El usuario pregunta por 'vigencia de poder', NO 'vigencia de la ley'.",
            "expected_type": "RAG" # Debería ir a RAG porque es un requisito específico
        },
        
        # CASO 2: Números en contexto no monetario
        # Riesgo: Que "32069" o "2026" se detecten como montos si el regex es muy laxo
        {
            "query": "La ley 32069 se aplica en el 2026",
            "context": "Menciona números grandes pero son años y número de ley.",
            "expected_type": "Respuesta Rápida" # Debería detectar la intención sobre la ley
        },
        
        # CASO 3: Palabras clave de procedimientos en contextos negativos
        # Riesgo: Que detecte "licitacion" y lance respuesta rápida genérica
        {
            "query": "No quiero hacer una licitación pública",
            "context": "Frase negativa.",
            "expected_type": "Gemini/RAG"
        },
        
        # CASO 4: Ambigüedad Licitación vs Licitación Abreviada
        # Riesgo: Confusión entre definiciones
        {
            "query": "diferencia entre licitación pública y la abreviada",
            "context": "Comparación de conceptos.",
            "expected_type": "RAG"
        },

        # CASO 5: Porcentajes engañosos
        # Riesgo: Que "100%" se confunda con monto
        {
            "query": "El avance de obra está al 100%",
            "context": "Porcentaje de avance, no dinero.",
            "expected_type": "Gemini/RAG"
        }
    ]
    
    for i, case in enumerate(test_cases):
        print(f"\n[TEST {i+1}] '{case['query']}'")
        print(f"Contexto: {case['context']}")
        
        # Capturamos la salida para ver qué motor respondió
        # (Esto es una simulación visual, en un test real interceptaríamos la clase)
        response = engine.process(case['query'])
        
        print("--- RESPUESTA ---")
        print(response[:200] + "..." if len(response) > 200 else response)
        print("-----------------")

if __name__ == "__main__":
    audit_ambiguities()
