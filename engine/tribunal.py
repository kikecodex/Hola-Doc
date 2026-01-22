"""
Módulo de Resoluciones del Tribunal de Contrataciones del Estado
Gestión y consulta de resoluciones, sanciones e inhabilitaciones
"""
from datetime import datetime, timedelta

class TribunalContrataciones:
    """
    Gestiona información sobre el Tribunal de Contrataciones del Estado (TCE)
    Incluye resoluciones, sanciones, inhabilitaciones y precedentes vinculantes
    """
    
    # Información del Tribunal
    INFO_TRIBUNAL = {
        "nombre": "Tribunal de Contrataciones del Estado",
        "siglas": "TCE",
        "organismo": "OECE (antes OSCE)",
        "funcion": "Resolver controversias y aplicar sanciones en contrataciones públicas",
        "salas": ["Primera Sala", "Segunda Sala", "Tercera Sala", "Sala Plena"],
        "web": "https://www.gob.pe/oece"
    }
    
    # Tipos de sanciones
    TIPOS_SANCIONES = {
        "inhabilitacion_temporal": {
            "descripcion": "Impedimento temporal para participar en procedimientos de selección",
            "duracion": "3 meses a 3 años",
            "causales": [
                "Presentar información inexacta",
                "Presentar documentos falsos o adulterados",
                "Incumplimiento injustificado de obligaciones",
                "Contratar con el Estado estando impedido"
            ]
        },
        "inhabilitacion_definitiva": {
            "descripcion": "Impedimento permanente para contratar con el Estado",
            "duracion": "Permanente",
            "causales": [
                "Reincidencia en infracciones graves",
                "Actos de corrupción comprobados",
                "Falsificación de documentos esenciales"
            ]
        },
        "multa": {
            "descripcion": "Sanción pecuniaria",
            "rango": "1 a 5 UIT (S/ 5,500 a S/ 27,500 en 2026)",
            "causales": [
                "Infracciones leves",
                "Retiro injustificado de propuesta",
                "No suscripción injustificada del contrato"
            ]
        },
        "amonestacion": {
            "descripcion": "Llamada de atención por escrito",
            "duracion": "N/A",
            "causales": [
                "Infracciones menores",
                "Primera falta leve"
            ]
        }
    }
    
    # Resoluciones relevantes 2025-2026 - EXPANDIDO
    RESOLUCIONES_RELEVANTES = [
        # 2026 - Resoluciones recientes
        {
            "numero": "0001-2026-TCE-S1",
            "sala": "Primera Sala",
            "fecha": "2026-01-10",
            "tipo": "Sanción",
            "materia": "Presentación de información inexacta",
            "sancion": "Inhabilitación temporal por 12 meses",
            "resumen": "Proveedor sancionado por declarar experiencia no acreditable"
        },
        {
            "numero": "0002-2026-TCE-S2",
            "sala": "Segunda Sala",
            "fecha": "2026-01-12",
            "tipo": "Sanción",
            "materia": "Contratar con el Estado estando impedido",
            "sancion": "Inhabilitación temporal por 18 meses",
            "resumen": "Proveedor que contrató teniendo sanción vigente"
        },
        {
            "numero": "0003-2026-TCE-S3",
            "sala": "Tercera Sala",
            "fecha": "2026-01-15",
            "tipo": "Recurso de apelación",
            "materia": "Descalificación de propuesta",
            "resolucion": "Fundado",
            "resumen": "Se revocó la descalificación por error formal subsanable"
        },
        {
            "numero": "0010-2026-TCE-S1",
            "sala": "Primera Sala",
            "fecha": "2026-01-18",
            "tipo": "Sanción",
            "materia": "Subcontratación no autorizada",
            "sancion": "Multa de 3 UIT",
            "resumen": "Subcontratación del 40% de la obra sin autorización de la Entidad"
        },
        {
            "numero": "0015-2026-TCE-S2",
            "sala": "Segunda Sala",
            "fecha": "2026-01-20",
            "tipo": "Recurso de apelación",
            "materia": "Evaluación de experiencia",
            "resolucion": "Infundado",
            "resumen": "La experiencia declarada no correspondía al objeto de la convocatoria"
        },
        
        # 2025 - Resoluciones importantes
        {
            "numero": "2345-2025-TCE-SP",
            "sala": "Sala Plena",
            "fecha": "2025-12-20",
            "tipo": "Precedente vinculante",
            "materia": "Retroactividad de sanción más favorable",
            "resumen": "Debe aplicarse la sanción más favorable según Ley 32069. Aplicable a procedimientos en trámite."
        },
        {
            "numero": "2340-2025-TCE-SP",
            "sala": "Sala Plena",
            "fecha": "2025-12-18",
            "tipo": "Precedente vinculante",
            "materia": "Subsanación de ofertas",
            "resumen": "Los errores formales que no alteran el contenido esencial pueden ser subsanados a solicitud del comité."
        },
        {
            "numero": "2300-2025-TCE-S2",
            "sala": "Segunda Sala",
            "fecha": "2025-12-15",
            "tipo": "Sanción",
            "materia": "Documentos falsos",
            "sancion": "Inhabilitación definitiva",
            "resumen": "Proveedor que presentó certificados de experiencia adulterados, con firma falsificada"
        },
        {
            "numero": "2250-2025-TCE-S3",
            "sala": "Tercera Sala",
            "fecha": "2025-12-10",
            "tipo": "Recurso de apelación",
            "materia": "Nulidad de procedimiento",
            "resolucion": "Fundado",
            "resumen": "Nulidad por no cumplir con difusión previa del requerimiento"
        },
        {
            "numero": "2200-2025-TCE-S1",
            "sala": "Primera Sala",
            "fecha": "2025-12-05",
            "tipo": "Sanción",
            "materia": "Incumplimiento de obligaciones contractuales",
            "sancion": "Inhabilitación temporal por 8 meses",
            "resumen": "Contratista no ejecutó prestación en el plazo, causando perjuicio a la Entidad"
        },
        {
            "numero": "2150-2025-TCE-S2",
            "sala": "Segunda Sala",
            "fecha": "2025-11-28",
            "tipo": "Recurso de apelación",
            "materia": "Factores de evaluación",
            "resolucion": "Fundado",
            "resumen": "Factores de evaluación eran restrictivos y limitaban la competencia"
        },
        {
            "numero": "2100-2025-TCE-SP",
            "sala": "Sala Plena",
            "fecha": "2025-11-20",
            "tipo": "Precedente vinculante",
            "materia": "Experiencia del personal clave",
            "resumen": "La experiencia del personal clave se acredita al momento de la presentación de ofertas"
        },
        {
            "numero": "2050-2025-TCE-S1",
            "sala": "Primera Sala",
            "fecha": "2025-11-15",
            "tipo": "Sanción",
            "materia": "No suscribir contrato",
            "sancion": "Inhabilitación temporal por 6 meses",
            "resumen": "Postor ganador no se presentó a suscribir contrato sin justificación válida"
        },
        {
            "numero": "2000-2025-TCE-S3",
            "sala": "Tercera Sala",
            "fecha": "2025-11-10",
            "tipo": "Recurso de apelación",
            "materia": "Garantía de fiel cumplimiento",
            "resolucion": "Infundado",
            "resumen": "La carta fianza no cumplía los requisitos formales establecidos"
        },
        {
            "numero": "1950-2025-TCE-S2",
            "sala": "Segunda Sala",
            "fecha": "2025-11-05",
            "tipo": "Sanción",
            "materia": "Fraccionamiento indebido",
            "sancion": "Inhabilitación temporal por 12 meses",
            "resumen": "La Entidad fraccionó indebidamente para evadir proceso de selección"
        },
        {
            "numero": "1900-2025-TCE-SP",
            "sala": "Sala Plena",
            "fecha": "2025-10-30",
            "tipo": "Precedente vinculante",
            "materia": "Consorcio y responsabilidad solidaria",
            "resumen": "Los integrantes de un consorcio responden solidariamente por las sanciones impuestas"
        },
        {
            "numero": "1850-2025-TCE-S1",
            "sala": "Primera Sala",
            "fecha": "2025-10-25",
            "tipo": "Recurso de apelación",
            "materia": "Requisitos de calificación",
            "resolucion": "Fundado",
            "resumen": "Requisitos de calificación excesivos que limitaban injustificadamente la participación"
        },
        {
            "numero": "1800-2025-TCE-S3",
            "sala": "Tercera Sala",
            "fecha": "2025-10-20",
            "tipo": "Sanción",
            "materia": "Información inexacta en declaración jurada",
            "sancion": "Inhabilitación temporal por 10 meses",
            "resumen": "DJ de habilitación profesional contenía información que no correspondía"
        },
        {
            "numero": "1750-2025-TCE-SP",
            "sala": "Sala Plena",
            "fecha": "2025-10-15",
            "tipo": "Precedente vinculante",
            "materia": "Cómputo de plazos de inhabilitación",
            "resumen": "El plazo de inhabilitación se computa desde la notificación de la resolución firme"
        },
        {
            "numero": "1700-2025-TCE-S2",
            "sala": "Segunda Sala",
            "fecha": "2025-10-10",
            "tipo": "Recurso de apelación",
            "materia": "Impedimentos para contratar",
            "resolucion": "Fundado",
            "resumen": "Se declaró nulo el proceso por contratar con empresa de funcionario impedido"
        }
    ]
    
    # Infracciones comunes
    INFRACCIONES = [
        {
            "codigo": "INF-01",
            "descripcion": "Presentar información inexacta o documentos falsos",
            "sancion_tipica": "Inhabilitación de 12 a 36 meses",
            "base_legal": "Art. 74 inc. a) - Ley 32069"
        },
        {
            "codigo": "INF-02",
            "descripcion": "Contratar con el Estado estando impedido",
            "sancion_tipica": "Inhabilitación de 18 a 36 meses",
            "base_legal": "Art. 74 inc. b) - Ley 32069"
        },
        {
            "codigo": "INF-03",
            "descripcion": "Incumplimiento injustificado de obligaciones contractuales",
            "sancion_tipica": "Inhabilitación de 6 a 24 meses",
            "base_legal": "Art. 74 inc. c) - Ley 32069"
        },
        {
            "codigo": "INF-04",
            "descripcion": "No mantener la oferta hasta la suscripción del contrato",
            "sancion_tipica": "Multa de 1 a 2 UIT",
            "base_legal": "Art. 74 inc. d) - Ley 32069"
        },
        {
            "codigo": "INF-05",
            "descripcion": "Negarse injustificadamente a suscribir el contrato",
            "sancion_tipica": "Inhabilitación de 3 a 12 meses",
            "base_legal": "Art. 74 inc. e) - Ley 32069"
        },
        {
            "codigo": "INF-06",
            "descripcion": "Subcontratar sin autorización",
            "sancion_tipica": "Multa de 2 a 4 UIT",
            "base_legal": "Art. 74 inc. f) - Ley 32069"
        }
    ]
    
    def __init__(self):
        """Inicializa el gestor del Tribunal"""
        pass
    
    def buscar_resoluciones(self, consulta: str) -> list:
        """Busca resoluciones por materia o palabras clave"""
        consulta_lower = consulta.lower()
        resultados = []
        
        for res in self.RESOLUCIONES_RELEVANTES:
            if consulta_lower in res['materia'].lower():
                resultados.append(res)
            elif consulta_lower in res['resumen'].lower():
                resultados.append(res)
            elif consulta_lower in res.get('tipo', '').lower():
                resultados.append(res)
        
        return resultados[:5]
    
    def obtener_tipos_sanciones(self) -> dict:
        """Retorna los tipos de sanciones disponibles"""
        return self.TIPOS_SANCIONES
    
    def obtener_infracciones(self) -> list:
        """Retorna la lista de infracciones"""
        return self.INFRACCIONES
    
    def formatear_resolucion(self, res: dict) -> str:
        """Formatea una resolución para mostrar"""
        texto = f"""⚖️ **Resolución N° {res['numero']}**
📅 Fecha: {res['fecha']}
🏛️ Sala: {res['sala']}
📌 Tipo: {res['tipo']}
📋 Materia: {res['materia']}
"""
        if 'sancion' in res:
            texto += f"⚠️ Sanción: {res['sancion']}\n"
        if 'resolucion' in res:
            texto += f"✅ Resolución: {res['resolucion']}\n"
        texto += f"📝 Resumen: {res['resumen']}"
        return texto
    
    def formatear_lista_resoluciones(self, resoluciones: list) -> str:
        """Formatea una lista de resoluciones"""
        if not resoluciones:
            return "No se encontraron resoluciones relacionadas."
        
        resultado = "⚖️ **RESOLUCIONES DEL TRIBUNAL:**\n\n"
        for i, res in enumerate(resoluciones, 1):
            resultado += f"{i}. **{res['numero']}** - {res['tipo']}\n"
            resultado += f"   📋 {res['materia']}\n"
            resultado += f"   📅 {res['fecha']}\n\n"
        
        return resultado
    
    def formatear_infraccion(self, inf: dict) -> str:
        """Formatea una infracción"""
        return f"""🚫 **{inf['codigo']}: {inf['descripcion']}**
⚠️ Sanción típica: {inf['sancion_tipica']}
📚 Base legal: {inf['base_legal']}"""


def get_tribunal_info() -> str:
    """Retorna información general sobre el Tribunal"""
    return """⚖️ **TRIBUNAL DE CONTRATACIONES DEL ESTADO (TCE)**

Es el órgano del OECE encargado de resolver controversias y aplicar sanciones en materia de contrataciones públicas.

**Competencias:**
• Resolver recursos de apelación (valor ref. > S/ 485,000)
• Imponer sanciones a proveedores
• Emitir precedentes vinculantes
• Resolver denuncias por infracciones

**Tipos de Sanciones:**
1. **Inhabilitación temporal**: 3 meses a 3 años
2. **Inhabilitación definitiva**: Permanente
3. **Multa**: 1 a 5 UIT (S/ 5,500 a S/ 27,500)
4. **Amonestación**: Llamada de atención

**Infracciones más comunes:**
• Presentar información inexacta o documentos falsos
• Contratar estando impedido
• Incumplimiento de obligaciones contractuales
• No suscribir contrato injustificadamente

**Precedente vinculante 2025:**
Retroactividad de sanción más favorable (Res. 2345-2025-TCE-S1)

**Consulta de proveedores sancionados:**
https://portal.osce.gob.pe/rnp/

¿Sobre qué tema del Tribunal deseas más información?"""
