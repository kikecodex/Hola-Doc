from engine.conversation import ConversationEngine
import time

def stress_test():
    print("🔥 INICIANDO STRESS TEST (Nivel: Difícil)", flush=True)
    print("=========================================", flush=True)
    
    engine = ConversationEngine()
    
    # Preguntas diseñadas para 'romper' o confundir al agente
    preguntas = [
        {
            "titulo": "Trampa de la Adjudicación Simplificada",
            "query": "Tengo un servicio de S/ 100,000. ¿Puedo convocar una Adjudicación Simplificada según la ley vigente?",
            "reto": "La 'Adjudicación Simplificada' fue eliminada. Debe sugerir Concurso Abreviado o Comparación.",
            "expected_keywords": ["ya no existe", "eliminada", "abreviado", "comparación"]
        },
        {
            "titulo": "Impedimento por Parentesco (Caso Borde)",
            "query": "Soy cuñado del Alcalde. ¿Puedo ser proveedor de su municipalidad si el monto es menor a 1 UIT?",
            "reto": "El impedimento es absoluto para parientes de 2do grado de afinidad (cuñados) en la entidad, sin importar el monto.",
            "expected_keywords": ["impedid", "cuñado", "segundo grado", "afinidad", "no puede"]
        },
        {
            "titulo": "Límite de Penalidad y Resolución",
            "query": "Llevo acumulado el 9.5% de penalidad por mora. La entidad me quiere resolver el contrato por acumulación máxima de penalidad. ¿Es legal?",
            "reto": "La resolución por acumulación máxima es al 10%. Con 9.5% NO procede resolución automática por esa causal.",
            "expected_keywords": ["10%", "tope", "no procede", "no es legal", "10 por ciento"]
        }
    ]
    
    for i, p in enumerate(preguntas):
        print(f"\n[{i+1}] {p['titulo'].upper()}")
        print(f"❓ Pregunta: {p['query']}")
        print(f"🎯 Reto: {p['reto']}")
        print("-" * 50)
        
        response = engine.process(p['query'])
        
        print("\n🤖 RESPUESTA AGENTE:")
        print(response)
        
        # Verificación básica
        passed = any(k.lower() in response.lower() for k in p['expected_keywords'])
        status = "✅ PASÓ" if passed else "❌ FALLÓ (o requiere revisión manual)"
        print(f"\n{status}")
        print("=" * 60)

if __name__ == "__main__":
    stress_test()
