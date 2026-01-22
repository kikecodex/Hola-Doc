"""
Motor de Conversación Híbrido
Sistema de 3 capas: Respuestas Rápidas → RAG → Gemini
Agente de Contrataciones Públicas - Perú
"""
from typing import Dict, Optional
import time

from config import Config
import google.generativeai as genai

# Importar el sistema de respuestas rápidas
from engine.respuestas_rapidas import buscar_respuesta_rapida

# Importar el motor RAG
from engine.rag_engine import RagEngine

# Importar módulos especializados
from engine.penalties import PenaltiesCalculator
from engine.adicionales import AdicionalesCalculator
from engine.plazos import PlazosCalculator
from engine.impedimentos import ImpedimentosVerifier
from engine.nulidad import NulidadAnalyzer
from engine.ampliaciones import AmpliacionesResolucion
from engine.jprd_arbitraje import JPRDArbitraje


class ConversationEngine:
    """
    Motor de conversación híbrido de 3 capas:
    1. Respuestas Precalculadas (milisegundos)
    2. Búsqueda RAG (Búsqueda semántica)
    3. Gemini como fallback (2-5 segundos)
    """
    
    SYSTEM_PROMPT = """Eres INKABOT, un asesor legal experto especializado en contrataciones públicas del Perú.
Tu misión es ayudar a proveedores, contratistas y funcionarios públicos con información precisa y actualizada.

CONTEXTO ADICIONAL DEL DOCUMENTO RECUPERADO:
{rag_context}

═══════════════════════════════════════════════════════════════════════════════
                           TU BASE DE CONOCIMIENTO
═══════════════════════════════════════════════════════════════════════════════

📚 MARCO NORMATIVO VIGENTE (Enero 2026):
• Ley N° 32069 - Ley General de Contrataciones Públicas (publicada 24/06/2024, vigente desde 22/04/2025)
• D.S. N° 009-2025-EF - Reglamento (publicado 22/01/2025, vigente desde 22/04/2025)
• D.S. N° 001-2026-EF - Modificaciones al Reglamento (publicado 08/01/2026, vigente desde 17/01/2026)
• D.S. N° 301-2025-EF - UIT 2026 = S/ 5,500

═══════════════════════════════════════════════════════════════════════════════
                              15 PRINCIPIOS (Art. 2)
═══════════════════════════════════════════════════════════════════════════════

1. LEGALIDAD (NUEVO), 2. EFICACIA Y EFICIENCIA, 3. VALOR POR DINERO (NUEVO),
4. INTEGRIDAD, 5. PRESUNCIÓN DE VERACIDAD (NUEVO), 6. CAUSALIDAD (NUEVO),
7. PUBLICIDAD, 8. LIBERTAD DE CONCURRENCIA, 9. TRANSPARENCIA, 10. COMPETENCIA,
11. IGUALDAD DE TRATO, 12. EQUIDAD Y COLABORACIÓN, 13. SOSTENIBILIDAD,
14. INNOVACIÓN (NUEVO), 15. VIGENCIA TECNOLÓGICA

═══════════════════════════════════════════════════════════════════════════════
                      MONTOS Y TOPES 2026 (UIT = S/ 5,500)
═══════════════════════════════════════════════════════════════════════════════

• MONTO MÍNIMO: 8 UIT = S/ 44,000
• Licitación/Concurso Público: ≥ S/ 485,000
• Procedimiento Abreviado: > S/ 44,000 y < S/ 485,000
• Comparación de Precios: > S/ 44,000 y ≤ S/ 100,000
• Obras LP: ≥ S/ 5,000,000 y < S/ 79,000,000
• Concurso Oferta: ≥ S/ 79,000,000

═══════════════════════════════════════════════════════════════════════════════
                              APELACIÓN (Arts. 97-103)
═══════════════════════════════════════════════════════════════════════════════

• Plazo: 8 días hábiles desde notificación
• Ante Entidad: Valor < S/ 485,000 (tasa 3%, mín S/ 150)
• Ante Tribunal: Valor ≥ S/ 485,000 (tasa 3%, mín S/ 1,100)
• Suspende el procedimiento
• Resolución: Entidad 12 días, Tribunal 20 días

═══════════════════════════════════════════════════════════════════════════════
                    CAMBIOS D.S. N° 001-2026-EF (Enero 2026)
═══════════════════════════════════════════════════════════════════════════════

1. Certificación obligatoria de compradores (niveles básico/intermedio/avanzado)
2. Plazo consulta mercado: de 3 a 6 días hábiles
3. Subsanación de ofertas por evaluadores
4. Experiencia de reorganización societaria en RNP
5. Garantías flexibles en emergencias
6. OECE asume rol sancionador directo

═══════════════════════════════════════════════════════════════════════════════
                    MÓDULOS ESPECIALIZADOS DISPONIBLES
═══════════════════════════════════════════════════════════════════════════════

• PENALIDADES: Calcula penalidades por mora (Art. 163)
• ADICIONALES: Evalúa adicionales de obra (15%/50%) y bienes/servicios (25%)
• PLAZOS: Calcula plazos en días hábiles con feriados Perú 2026
• IMPEDIMENTOS: Verifica impedimentos para contratar (Art. 11)
• NULIDAD: Analiza causales de nulidad (Art. 72)
• AMPLIACIONES: Evalúa ampliaciones de plazo y resolución de contratos
• JPRD: Junta de Prevención y Resolución de Disputas (obras ≥ S/ 79M)
• ARBITRAJE: Información sobre arbitraje en contrataciones

═══════════════════════════════════════════════════════════════════════════════
                    INSTRUCCIONES PARA TUS RESPUESTAS
═══════════════════════════════════════════════════════════════════════════════

1. Responde SIEMPRE en español, de forma clara y profesional
2. CITA los artículos y normas (ej: "Art. 2, Ley 32069")
3. Usa **negritas** y listas para mejor legibilidad
4. Sé CONCISO pero COMPLETO
5. Para montos, usa valores 2026 (UIT = S/ 5,500)
6. Si te piden calcular, explica el razonamiento
7. Incluye base legal en tus respuestas"""

    def __init__(self):
        """Inicializa el motor de conversación híbrido"""
        # Configurar Gemini
        genai.configure(api_key=Config.GEMINI_API_KEY)
        
        # Inicializar RAG Engine
        print("📚 Inicializando motor RAG...")
        self.rag_engine = RagEngine()
        
        self.model = genai.GenerativeModel(
            model_name=Config.GEMINI_MODEL,
            system_instruction=self.SYSTEM_PROMPT.format(rag_context="")
        )
        
        # Chats por sesión
        self.chats: Dict[str, any] = {}
        
        # Estadísticas
        self.stats = {
            "respuestas_rapidas": 0,
            "respuestas_rag": 0,
            "respuestas_gemini": 0
        }
        
        print("🔷 Motor Híbrido inicializado")
        print("   ├── Capa 1: Respuestas Rápidas ✅")
        print("   ├── Capa 2: RAG ✅")
        print("   └── Capa 3: Gemini Fallback ✅")
    
    def _get_chat(self, session_id: str, rag_context: str = ""):
        """Obtiene o crea un chat para la sesión"""
        if session_id not in self.chats:
            # Si se pasa contexto, inyectarlo en el system prompt para esta sesión nueva
            prompt_con_contexto = self.SYSTEM_PROMPT.format(rag_context=rag_context)
            
            model = genai.GenerativeModel(
                model_name=Config.GEMINI_MODEL,
                system_instruction=prompt_con_contexto
            )
            self.chats[session_id] = model.start_chat(history=[])
        return self.chats[session_id]
    
    def process(self, message: str, session_id: str = "default") -> str:
        """
        Procesa un mensaje usando el sistema híbrido de 3 capas:
        1. Busca en respuestas precalculadas (milisegundos)
        2. Busca en RAG (próxima implementación)
        3. Usa Gemini como fallback
        """
        start_time = time.time()
        rag_context = ""
        
        try:
            # ═══════════════════════════════════════════════════════════
            # CAPA 1: RESPUESTAS RÁPIDAS PRECALCULADAS
            # ═══════════════════════════════════════════════════════════
            respuesta_rapida = buscar_respuesta_rapida(message)
            
            if respuesta_rapida:
                elapsed = (time.time() - start_time) * 1000
                self.stats["respuestas_rapidas"] += 1
                print(f"⚡ Respuesta rápida encontrada en {elapsed:.0f}ms")
                return respuesta_rapida
            
            # ═══════════════════════════════════════════════════════════
            # CAPA 2: RAG (Búsqueda Semántica)
            # ═══════════════════════════════════════════════════════════
            print("🔍 Buscando en documentos RAG...")
            rag_results = self.rag_engine.search(message)
            
            if rag_results:
                rag_context = "\\n\\n".join(rag_results)
                print(f"📄 Se encontraron {len(rag_results)} fragmentos relevantes")
                self.stats["respuestas_rag"] += 1
            else:
                print("⚠️ No se encontraron documentos relevantes")
            
            # ═══════════════════════════════════════════════════════════
            # CAPA 3: GEMINI FALLBACK
            # ═══════════════════════════════════════════════════════════
            
            # Estrategia: Inyectar contexto en el mensaje actual
            final_prompt = message
            if rag_context:
                final_prompt = f"""
INFORMACIÓN DE REFERENCIA (USAR PARA RESPONDER):
{rag_context}

PREGUNTA DEL USUARIO:
{message}
"""
            
            # Recuperar chat existente
            chat = self._get_chat(session_id)
            
            # Enviar mensaje (con o sin contexto extra)
            response = chat.send_message(final_prompt)
            
            elapsed = (time.time() - start_time) * 1000
            self.stats["respuestas_gemini"] += 1
            print(f"🤖 Respuesta Gemini generada en {elapsed:.0f}ms")
            
            return response.text
            
        except Exception as e:
            error_msg = str(e)
            if "api_key" in error_msg.lower():
                return "❌ **Error de autenticación**: Verifica tu GEMINI_API_KEY"
            if "quota" in error_msg.lower():
                return "❌ **Límite alcanzado**: Intenta en unos minutos"
            return f"❌ Error: {error_msg}"
    
    def get_stats(self) -> dict:
        """Retorna estadísticas de uso"""
        return self.stats
    
    def clear_session(self, session_id: str):
        """Limpia la memoria de una sesión"""
        if session_id in self.chats:
            del self.chats[session_id]
