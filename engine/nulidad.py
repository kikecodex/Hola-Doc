"""
Módulo de Causales de Nulidad de Contrato y Proceso
Ley N° 32069 - Artículo 72
"""
from typing import Dict, List, Optional
from datetime import datetime


class NulidadAnalyzer:
    """
    Analiza y verifica causales de nulidad en contrataciones públicas
    Según Art. 72 de la Ley N° 32069
    """
    
    # Causales de nulidad de oficio (Art. 72)
    CAUSALES_NULIDAD = [
        {
            "numero": 1,
            "causal": "Contravención de la Constitución, la Ley o el Reglamento",
            "descripcion": "Cuando el acto administrativo o el procedimiento contraviene normas constitucionales, legales o reglamentarias",
            "ejemplos": [
                "Otorgar buena pro sin cumplir etapas del procedimiento",
                "Evaluar con factores no previstos en las bases",
                "No publicar convocatoria en SEACE"
            ],
            "consecuencia": "Nulidad total o parcial del procedimiento",
            "plazo_prescripcion": "3 años desde otorgamiento de buena pro"
        },
        {
            "numero": 2,
            "causal": "Defecto u omisión de alguno de los requisitos de validez del acto",
            "descripcion": "Cuando el acto carece de competencia, objeto, finalidad, motivación o procedimiento regular",
            "ejemplos": [
                "Comité de selección no autorizado",
                "Falta de disponibilidad presupuestal",
                "Ausencia de expediente de contratación"
            ],
            "consecuencia": "Nulidad del acto administrativo",
            "plazo_prescripcion": "3 años"
        },
        {
            "numero": 3,
            "causal": "Postor ganador impedido de contratar con el Estado",
            "descripcion": "Cuando se verifica que el postor ganador estaba impedido según Art. 11",
            "ejemplos": [
                "Postor con inhabilitación vigente",
                "Empresa de funcionario impedido",
                "Postor inscrito en REDERECI"
            ],
            "consecuencia": "Nulidad del contrato y sanción al postor",
            "plazo_prescripcion": "3 años"
        },
        {
            "numero": 4,
            "causal": "Verificación posterior de falsedad documental",
            "descripcion": "Cuando se comprueba que documentos presentados son falsos o con información inexacta",
            "ejemplos": [
                "Certificados de experiencia adulterados",
                "Constancias de trabajo falsas",
                "Declaraciones juradas inexactas"
            ],
            "consecuencia": "Nulidad + Denuncia penal + Inhabilitación",
            "plazo_prescripcion": "Durante ejecución o hasta 3 años después"
        },
        {
            "numero": 5,
            "causal": "Falta de requisitos de calificación del postor",
            "descripcion": "Cuando el postor no cumplía los requisitos de calificación establecidos en las bases",
            "ejemplos": [
                "Falta de experiencia mínima requerida",
                "RNP vencido al momento de presentación",
                "Personal clave sin calificación exigida"
            ],
            "consecuencia": "Nulidad y llamamiento al segundo lugar",
            "plazo_prescripcion": "Hasta la conformidad final"
        },
        {
            "numero": 6,
            "causal": "Vicios en el procedimiento de evaluación",
            "descripcion": "Errores sustanciales en la evaluación que afectaron el resultado",
            "ejemplos": [
                "Error en el cálculo de puntajes",
                "No evaluar a todos los postores",
                "Aplicar criterios distintos a los establecidos"
            ],
            "consecuencia": "Retrotraer a la etapa afectada",
            "plazo_prescripcion": "Hasta consentimiento de buena pro"
        }
    ]
    
    # Causales de nulidad del contrato
    CAUSALES_NULIDAD_CONTRATO = [
        {
            "numero": "C1",
            "causal": "Contratación con proveedor impedido",
            "base_legal": "Art. 11 y 72 Ley 32069"
        },
        {
            "numero": "C2",
            "causal": "Omisión del procedimiento de selección requerido",
            "base_legal": "Art. 54-56 Ley 32069"
        },
        {
            "numero": "C3",
            "causal": "Fraccionamiento indebido",
            "base_legal": "Art. 29 del Reglamento"
        },
        {
            "numero": "C4",
            "causal": "Contratación sin disponibilidad presupuestal",
            "base_legal": "Art. 8 Ley 32069"
        }
    ]
    
    def __init__(self):
        pass
    
    def analizar_causal(self, descripcion_caso: str) -> Dict:
        """
        Analiza una situación y determina posibles causales de nulidad
        
        Args:
            descripcion_caso: Descripción del caso a analizar
            
        Returns:
            Dict con causales identificadas y recomendaciones
        """
        descripcion_lower = descripcion_caso.lower()
        causales_aplicables = []
        
        # Mapeo de palabras clave a causales
        keywords_causales = {
            0: ['contravención', 'ilegal', 'sin procedimiento', 'sin convocatoria'],
            1: ['requisito', 'validez', 'competencia', 'presupuesto', 'expediente'],
            2: ['impedido', 'inhabilitado', 'sancionado', 'redereci'],
            3: ['falso', 'falsedad', 'adulterado', 'inexacto', 'documento falso'],
            4: ['calificación', 'experiencia', 'rnp vencido', 'no cumple'],
            5: ['evaluación', 'puntaje', 'error de cálculo', 'no evaluaron']
        }
        
        for idx, keywords in keywords_causales.items():
            if any(kw in descripcion_lower for kw in keywords):
                causales_aplicables.append(self.CAUSALES_NULIDAD[idx])
        
        if not causales_aplicables:
            return {
                "causales_identificadas": [],
                "analisis": "No se identificaron causales evidentes de nulidad",
                "recomendacion": "Se requiere análisis detallado del expediente para determinar si existe causal de nulidad"
            }
        
        return {
            "causales_identificadas": causales_aplicables,
            "cantidad": len(causales_aplicables),
            "recomendacion": "Se recomienda evaluar la procedencia de declarar nulidad de oficio",
            "plazo_prescripcion": "3 años desde otorgamiento de buena pro"
        }
    
    def verificar_prescripcion(
        self,
        fecha_buena_pro: str,
        fecha_actual: str = None
    ) -> Dict:
        """
        Verifica si ha prescrito la facultad de declarar nulidad
        
        Args:
            fecha_buena_pro: Fecha de buena pro en formato DD/MM/YYYY
            fecha_actual: Fecha actual (opcional, usa hoy si no se proporciona)
        """
        try:
            if "/" in fecha_buena_pro:
                bp = datetime.strptime(fecha_buena_pro, "%d/%m/%Y")
            else:
                bp = datetime.strptime(fecha_buena_pro, "%Y-%m-%d")
            
            if fecha_actual:
                actual = datetime.strptime(fecha_actual, "%d/%m/%Y")
            else:
                actual = datetime.now()
            
            diferencia = actual - bp
            anos_transcurridos = diferencia.days / 365.25
            
            prescrito = anos_transcurridos >= 3
            
            return {
                "fecha_buena_pro": bp.strftime("%d/%m/%Y"),
                "fecha_verificacion": actual.strftime("%d/%m/%Y"),
                "anos_transcurridos": round(anos_transcurridos, 2),
                "prescrito": prescrito,
                "mensaje": "La facultad de declarar nulidad HA PRESCRITO" if prescrito else "La facultad de nulidad AÚN ESTÁ VIGENTE",
                "plazo_limite": (bp.replace(year=bp.year + 3)).strftime("%d/%m/%Y")
            }
            
        except ValueError:
            return {"error": "Formato de fecha inválido. Use DD/MM/YYYY"}
    
    def obtener_causales(self) -> List[Dict]:
        """Retorna la lista de causales de nulidad"""
        return self.CAUSALES_NULIDAD
    
    def formatear_resultado(self, resultado: Dict) -> str:
        """Formatea el resultado para chat"""
        if not resultado.get("causales_identificadas"):
            return f"""📋 **ANÁLISIS DE NULIDAD**

ℹ️ {resultado.get('analisis', resultado.get('mensaje', 'Análisis completado'))}

💡 **Recomendación:** {resultado.get('recomendacion', 'Consultar con área legal')}

📚 *Base legal: Art. 72 de la Ley N° 32069*"""
        
        causales = resultado["causales_identificadas"]
        respuesta = f"""⚖️ **ANÁLISIS DE CAUSALES DE NULIDAD**

🔍 **Causales identificadas:** {len(causales)}

"""
        for i, causal in enumerate(causales, 1):
            respuesta += f"""**{i}. {causal['causal']}**
   📝 {causal['descripcion']}
   ⚠️ Consecuencia: {causal['consecuencia']}

"""
        
        respuesta += f"""⏱️ **Plazo de prescripción:** {resultado.get('plazo_prescripcion', '3 años')}

💡 **Recomendación:** {resultado['recomendacion']}

📚 *Base legal: Art. 72 Ley 32069*"""
        
        return respuesta
    
    def detect_and_analyze(self, message: str) -> Optional[str]:
        """Detecta si el mensaje es consulta de nulidad"""
        message_lower = message.lower()
        
        keywords = ['nulidad', 'nulo', 'anular', 'invalidar', 'causal de nulidad',
                    'documento falso', 'falsedad', 'impedido', 'prescripción']
        
        if not any(kw in message_lower for kw in keywords):
            return None
        
        # Analizar el mensaje
        resultado = self.analizar_causal(message)
        return self.formatear_resultado(resultado)


def get_nulidad_info() -> str:
    """Información general sobre nulidad"""
    return """⚖️ **NULIDAD EN CONTRATACIONES PÚBLICAS**

**Base Legal:** Art. 72 de la Ley N° 32069

**Causales de nulidad de oficio:**

1️⃣ **Contravención de normas**
   - Constitución, Ley o Reglamento

2️⃣ **Defecto en requisitos de validez**
   - Competencia, motivación, procedimiento

3️⃣ **Postor impedido**
   - Inhabilitado o en REDERECI

4️⃣ **Falsedad documental**
   - Documentos falsos o inexactos

5️⃣ **Falta de requisitos de calificación**
   - No cumplía experiencia o capacidad

6️⃣ **Vicios en evaluación**
   - Errores que afectaron resultado

**Plazo de prescripción:** 3 años desde buena pro

**¿Quién declara la nulidad?**
- El Titular de la Entidad (de oficio)
- El Tribunal de Contrataciones

📚 *Base legal: Art. 72 Ley 32069*"""
