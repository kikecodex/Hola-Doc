"""
Módulo de Ampliaciones de Plazo y Resolución de Contratos
Ley N° 32069 - Arts. 171-178 del Reglamento D.S. N° 009-2025-EF
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class AmpliacionesResolucion:
    """
    Gestiona ampliaciones de plazo y resolución de contratos
    Según Arts. 171-178 del D.S. N° 009-2025-EF
    """
    
    # Causales de ampliación de plazo (Art. 171)
    CAUSALES_AMPLIACION = [
        {
            "codigo": "A1",
            "causal": "Atrasos y/o paralizaciones por causas no atribuibles al contratista",
            "descripcion": "Cuando la Entidad no cumple sus obligaciones (ej: no entrega terreno, aprobaciones tardías)",
            "ejemplos": [
                "Entrega tardía del terreno para obra",
                "Demora en aprobación de adicionales",
                "Falta de entrega de información técnica"
            ],
            "requiere_sustento": True,
            "plazo_solicitud": 8
        },
        {
            "codigo": "A2",
            "causal": "Caso fortuito o fuerza mayor",
            "descripcion": "Eventos extraordinarios, imprevisibles e irresistibles",
            "ejemplos": [
                "Desastres naturales (terremotos, inundaciones)",
                "Pandemias con cuarentena obligatoria",
                "Conflictos sociales que impiden acceso"
            ],
            "requiere_sustento": True,
            "plazo_solicitud": 8
        },
        {
            "codigo": "A3",
            "causal": "Prestaciones adicionales aprobadas",
            "descripcion": "Cuando se aprueban adicionales que requieren mayor plazo",
            "ejemplos": [
                "Adicional de obra que afecta la ruta crítica",
                "Prestación adicional de servicios"
            ],
            "requiere_sustento": True,
            "plazo_solicitud": 8
        }
    ]
    
    # Causales de resolución de contrato (Art. 175-176)
    CAUSALES_RESOLUCION = {
        "por_incumplimiento": [
            {
                "codigo": "R1",
                "causal": "Incumplimiento injustificado de obligaciones esenciales",
                "descripcion": "Obligaciones establecidas en bases y contrato",
                "procedimiento": "Carta notarial de 5 días calendario"
            },
            {
                "codigo": "R2",
                "causal": "Acumulación del monto máximo de penalidad por mora",
                "descripcion": "Cuando las penalidades alcanzan el 10% del contrato",
                "procedimiento": "Carta notarial de 5 días calendario",
                "nota": "La resolución NO es automática"
            },
            {
                "codigo": "R3",
                "causal": "Paralización injustificada",
                "descripcion": "Suspensión de actividades sin autorización",
                "procedimiento": "Carta notarial de 5 días calendario"
            },
            {
                "codigo": "R4",
                "causal": "Incumplimiento de lo dispuesto en laudo arbitral",
                "descripcion": "No acatar decisión arbitral firme",
                "procedimiento": "Resolución inmediata"
            }
        ],
        "por_la_entidad": [
            {
                "codigo": "E1",
                "causal": "Falta de pago de valorizaciones o contraprestaciones",
                "descripcion": "Demora mayor a 60 días calendario en el pago",
                "procedimiento": "Carta notarial de 5 días"
            },
            {
                "codigo": "E2",
                "causal": "Reducción de prestaciones mayor al límite",
                "descripcion": "Deductivos que superan el 50%",
                "procedimiento": "Solicitud del contratista"
            }
        ],
        "por_caso_fortuito": [
            {
                "codigo": "F1",
                "causal": "Imposibilidad sobreviniente",
                "descripcion": "Imposibilidad de continuar el contrato por caso fortuito o fuerza mayor",
                "procedimiento": "Resolución por mutuo acuerdo"
            }
        ]
    }
    
    # Constantes
    PLAZO_SOLICITUD_AMPLIACION = 8  # días hábiles
    PLAZO_CARTA_NOTARIAL = 5  # días calendario
    PLAZO_LIQUIDACION_OBRA = 60  # días calendario
    
    def __init__(self):
        pass
    
    def evaluar_ampliacion(
        self,
        causal: str,
        dias_solicitados: int,
        dias_desde_conocimiento: int
    ) -> Dict:
        """
        Evalúa si una solicitud de ampliación es procedente
        
        Args:
            causal: Descripción de la causal
            dias_solicitados: Días de ampliación solicitados
            dias_desde_conocimiento: Días desde que se conoció la causal
        """
        # Verificar plazo de solicitud
        dentro_plazo = dias_desde_conocimiento <= self.PLAZO_SOLICITUD_AMPLIACION
        
        # Identificar causal
        causal_identificada = None
        for c in self.CAUSALES_AMPLIACION:
            if any(ej.lower() in causal.lower() for ej in c['ejemplos']) or \
               c['causal'].lower() in causal.lower():
                causal_identificada = c
                break
        
        if not dentro_plazo:
            return {
                "procedente": False,
                "motivo": f"La solicitud fue presentada fuera del plazo de {self.PLAZO_SOLICITUD_AMPLIACION} días hábiles",
                "dias_transcurridos": dias_desde_conocimiento,
                "plazo_maximo": self.PLAZO_SOLICITUD_AMPLIACION,
                "recomendacion": "La solicitud debió presentarse dentro de los 8 días hábiles de conocida la causal",
                "base_legal": "Art. 171 del D.S. N° 009-2025-EF"
            }
        
        if not causal_identificada:
            return {
                "procedente": "Por evaluar",
                "causal": causal,
                "dias_solicitados": dias_solicitados,
                "dentro_plazo": True,
                "observacion": "La causal debe ser evaluada por el área técnica",
                "requisitos": [
                    "Cuaderno de obra (si aplica)",
                    "Documentos que sustenten la causal",
                    "Nuevo calendario de avance de obra",
                    "Valorización de mayores gastos generales (si aplica)"
                ],
                "base_legal": "Art. 171 del D.S. N° 009-2025-EF"
            }
        
        return {
            "procedente": "Por evaluar (causal identificada)",
            "causal_identificada": causal_identificada['causal'],
            "codigo_causal": causal_identificada['codigo'],
            "dias_solicitados": dias_solicitados,
            "dentro_plazo": True,
            "dias_presentacion": dias_desde_conocimiento,
            "requisitos": [
                "Solicitud del contratista con sustento",
                "Documentación de respaldo",
                "Nuevo calendario propuesto"
            ],
            "plazo_pronunciamiento": "10 días hábiles desde recepción",
            "base_legal": "Art. 171 del D.S. N° 009-2025-EF"
        }
    
    def procedimiento_resolucion(
        self,
        tipo: str,
        causal: str
    ) -> Dict:
        """
        Retorna el procedimiento para resolver un contrato
        
        Args:
            tipo: 'incumplimiento', 'entidad', 'caso_fortuito'
            causal: Descripción de la causal
        """
        mapa_tipo = {
            "incumplimiento": "por_incumplimiento",
            "contratista": "por_incumplimiento",
            "entidad": "por_la_entidad",
            "fuerza_mayor": "por_caso_fortuito",
            "caso_fortuito": "por_caso_fortuito"
        }
        
        tipo_key = mapa_tipo.get(tipo.lower(), "por_incumplimiento")
        causales_tipo = self.CAUSALES_RESOLUCION.get(tipo_key, [])
        
        # Buscar causal específica
        causal_encontrada = None
        for c in causales_tipo:
            if causal.lower() in c['causal'].lower() or \
               causal.lower() in c['descripcion'].lower():
                causal_encontrada = c
                break
        
        if not causal_encontrada and causales_tipo:
            causal_encontrada = causales_tipo[0]  # Primera causal del tipo
        
        if not causal_encontrada:
            return {
                "error": "Tipo de resolución no identificado",
                "tipos_validos": list(mapa_tipo.keys())
            }
        
        return {
            "tipo_resolucion": tipo_key.replace("_", " ").title(),
            "causal": causal_encontrada['causal'],
            "codigo": causal_encontrada['codigo'],
            "descripcion": causal_encontrada['descripcion'],
            "procedimiento": causal_encontrada['procedimiento'],
            "pasos": [
                "1. Identificar y documentar la causal",
                "2. Emitir carta notarial con plazo de 5 días calendario",
                f"3. {causal_encontrada.get('nota', 'Esperar respuesta del contratista')}",
                "4. Emitir Resolución de resolución de contrato",
                "5. Realizar liquidación del contrato",
                "6. Informar al Tribunal (si corresponde sanción)"
            ],
            "consecuencias": [
                "Ejecución de garantía de fiel cumplimiento",
                "Pérdida de los adelantos no amortizados",
                "Posible sanción del Tribunal (inhabilitación)",
                "Inicio de nuevo proceso de contratación"
            ],
            "base_legal": "Arts. 175-178 del D.S. N° 009-2025-EF"
        }
    
    def calcular_mayores_gastos_generales(
        self,
        monto_contrato: float,
        porcentaje_gg: float,
        plazo_original: int,
        dias_ampliacion: int
    ) -> Dict:
        """
        Calcula mayores gastos generales variables por ampliación
        
        Args:
            monto_contrato: Monto del contrato
            porcentaje_gg: Porcentaje de gastos generales variables
            plazo_original: Plazo original en días
            dias_ampliacion: Días de ampliación
        """
        # Gastos generales variables totales
        gg_total = monto_contrato * (porcentaje_gg / 100)
        
        # Gasto diario
        gg_diario = gg_total / plazo_original
        
        # Mayores gastos generales
        mayores_gg = gg_diario * dias_ampliacion
        
        return {
            "monto_contrato": monto_contrato,
            "porcentaje_gg": porcentaje_gg,
            "gg_total": round(gg_total, 2),
            "gg_diario": round(gg_diario, 2),
            "dias_ampliacion": dias_ampliacion,
            "mayores_gg": round(mayores_gg, 2),
            "base_legal": "Art. 175 del D.S. N° 009-2025-EF"
        }
    
    def formatear_resultado_ampliacion(self, resultado: Dict) -> str:
        """Formatea resultado de ampliación"""
        if resultado.get("procedente") == False:
            estado = "❌ NO PROCEDENTE"
        else:
            estado = "🔄 POR EVALUAR"
        
        respuesta = f"""📅 **EVALUACIÓN DE AMPLIACIÓN DE PLAZO**

📋 **Estado:** {estado}

"""
        if resultado.get("causal_identificada"):
            respuesta += f"""✅ **Causal identificada:** {resultado['causal_identificada']}
📆 **Días solicitados:** {resultado['dias_solicitados']}
⏱️ **Días desde conocimiento:** {resultado.get('dias_presentacion', 'N/A')}
📌 **Dentro del plazo:** {"Sí" if resultado.get('dentro_plazo') else "No"}

"""
        
        if resultado.get("requisitos"):
            respuesta += "📝 **Requisitos:**\n"
            for req in resultado['requisitos']:
                respuesta += f"   • {req}\n"
        
        if resultado.get("motivo"):
            respuesta += f"\n⚠️ **Motivo:** {resultado['motivo']}"
        
        respuesta += f"\n\n📚 *Base legal: {resultado.get('base_legal', 'Art. 171 del Reglamento')}*"
        
        return respuesta
    
    def formatear_resultado_resolucion(self, resultado: Dict) -> str:
        """Formatea resultado de resolución"""
        if "error" in resultado:
            return f"❌ Error: {resultado['error']}"
        
        respuesta = f"""⚠️ **PROCEDIMIENTO DE RESOLUCIÓN DE CONTRATO**

📋 **Tipo:** {resultado['tipo_resolucion']}
📌 **Causal:** {resultado['causal']}
📝 {resultado['descripcion']}

📜 **Procedimiento requerido:**
{resultado['procedimiento']}

"""
        respuesta += "📋 **Pasos a seguir:**\n"
        for paso in resultado['pasos']:
            respuesta += f"   {paso}\n"
        
        respuesta += "\n⚠️ **Consecuencias:**\n"
        for cons in resultado['consecuencias']:
            respuesta += f"   • {cons}\n"
        
        respuesta += f"\n📚 *Base legal: {resultado['base_legal']}*"
        
        return respuesta
    
    def detect_and_process(self, message: str) -> Optional[str]:
        """Detecta si el mensaje es sobre ampliación o resolución"""
        message_lower = message.lower()
        
        # Detectar ampliación
        if any(kw in message_lower for kw in ['ampliación', 'ampliacion', 'ampliar plazo', 'extender plazo']):
            return get_ampliaciones_info()
        
        # Detectar resolución
        if any(kw in message_lower for kw in ['resolver contrato', 'resolución de contrato', 'resolucion de contrato', 
                                               'terminar contrato', 'incumplimiento']):
            return get_resolucion_info()
        
        return None


def get_ampliaciones_info() -> str:
    """Información sobre ampliaciones de plazo"""
    return """📅 **AMPLIACIÓN DE PLAZO CONTRACTUAL**

**Base Legal:** Art. 171-172 del D.S. N° 009-2025-EF

**Causales válidas:**
1️⃣ Atrasos por causas no atribuibles al contratista
2️⃣ Caso fortuito o fuerza mayor
3️⃣ Prestaciones adicionales aprobadas

**Plazo para solicitar:** 8 días hábiles desde conocida la causal

**Requisitos:**
• Solicitud fundamentada
• Documentación de respaldo
• Nuevo calendario propuesto
• Cuaderno de obra (obras)

**Plazo para resolver:** 10 días hábiles

**Gastos generales:** Se reconocen mayores GG variables

📚 *Base legal: Arts. 171-172 del Reglamento*"""


def get_resolucion_info() -> str:
    """Información sobre resolución de contratos"""
    return """⚠️ **RESOLUCIÓN DE CONTRATO**

**Base Legal:** Arts. 175-178 del D.S. N° 009-2025-EF

**Por incumplimiento del contratista:**
• Incumplimiento de obligaciones esenciales
• Acumulación del 10% de penalidades
• Paralización injustificada
• Incumplimiento de laudo arbitral

**Por la Entidad:**
• Falta de pago (más de 60 días)
• Reducción mayor al 50%

**Procedimiento:**
1. Carta notarial (5 días calendario)
2. Resolución del contrato
3. Liquidación
4. Informe al Tribunal (si corresponde)

**Consecuencias:**
• Ejecución de garantías
• Posible inhabilitación
• Pérdida de adelantos

📚 *Base legal: Arts. 175-178 del Reglamento*"""
