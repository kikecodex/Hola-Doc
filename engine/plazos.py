"""
Calculador de Plazos con Días Hábiles
Feriados oficiales de Perú 2026
Ley N° 32069 y D.S. N° 009-2025-EF
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re


class PlazosCalculator:
    """
    Calcula plazos en días hábiles considerando feriados del Perú
    """
    
    # Feriados oficiales de Perú 2026
    FERIADOS_2026 = [
        "2026-01-01",  # Año Nuevo
        "2026-04-02",  # Jueves Santo
        "2026-04-03",  # Viernes Santo
        "2026-05-01",  # Día del Trabajo
        "2026-06-07",  # Batalla de Arica (domingo, no adiciona)
        "2026-06-29",  # San Pedro y San Pablo
        "2026-07-23",  # Día de la Fuerza Aérea
        "2026-07-28",  # Fiestas Patrias
        "2026-07-29",  # Fiestas Patrias
        "2026-08-06",  # Batalla de Junín
        "2026-08-30",  # Santa Rosa de Lima
        "2026-10-08",  # Combate de Angamos
        "2026-11-01",  # Día de Todos los Santos
        "2026-12-08",  # Inmaculada Concepción
        "2026-12-09",  # Batalla de Ayacucho
        "2026-12-25",  # Navidad
        "2026-12-31",  # Feriado bancario
    ]
    
    # Feriados 2025 (para cálculos que abarcan fin de año)
    FERIADOS_2025 = [
        "2025-12-25",
        "2025-12-31",
    ]
    
    # Plazos importantes de la Ley 32069
    PLAZOS_LEGALES = {
        "apelacion": {
            "dias": 8,
            "tipo": "habiles",
            "descripcion": "Plazo para interponer recurso de apelación",
            "base_legal": "Art. 97 del Reglamento"
        },
        "suscripcion_contrato": {
            "dias": 8,
            "tipo": "habiles",
            "descripcion": "Plazo para suscribir contrato después de buena pro consentida",
            "base_legal": "Art. 139 del Reglamento"
        },
        "consultas_observaciones_lp": {
            "dias": 10,
            "tipo": "habiles",
            "descripcion": "Plazo para formular consultas y observaciones en Licitación Pública",
            "base_legal": "Art. 68 del Reglamento"
        },
        "consultas_observaciones_abreviado": {
            "dias": 5,
            "tipo": "habiles",
            "descripcion": "Plazo para consultas en procedimiento abreviado",
            "base_legal": "Art. 76 del Reglamento"
        },
        "absolucion_consultas": {
            "dias": 5,
            "tipo": "habiles",
            "descripcion": "Plazo para absolver consultas y observaciones",
            "base_legal": "Art. 68 del Reglamento"
        },
        "integracion_bases": {
            "dias": 3,
            "tipo": "habiles",
            "descripcion": "Plazo para integrar bases",
            "base_legal": "Art. 69 del Reglamento"
        },
        "presentacion_garantia": {
            "dias": 8,
            "tipo": "habiles", 
            "descripcion": "Plazo para presentar garantía de fiel cumplimiento",
            "base_legal": "Art. 139 del Reglamento"
        },
        "conformidad_bienes": {
            "dias": 10,
            "tipo": "habiles",
            "descripcion": "Plazo para otorgar conformidad de bienes",
            "base_legal": "Art. 168 del Reglamento"
        },
        "conformidad_servicios": {
            "dias": 10,
            "tipo": "habiles",
            "descripcion": "Plazo para otorgar conformidad de servicios",
            "base_legal": "Art. 168 del Reglamento"
        },
        "ampliacion_plazo": {
            "dias": 8,
            "tipo": "habiles",
            "descripcion": "Plazo para solicitar ampliación desde conocida la causal",
            "base_legal": "Art. 171 del Reglamento"
        },
        "resolucion_contrato": {
            "dias": 5,
            "tipo": "calendario",
            "descripcion": "Plazo de carta notarial para resolver contrato",
            "base_legal": "Art. 176 del Reglamento"
        },
        "inicio_arbitraje": {
            "dias": 30,
            "tipo": "habiles",
            "descripcion": "Plazo para iniciar arbitraje después de resolución",
            "base_legal": "Art. 227 del Reglamento"
        },
        "liquidacion_obra": {
            "dias": 60,
            "tipo": "calendario",
            "descripcion": "Plazo para presentar liquidación de obra",
            "base_legal": "Art. 209 del Reglamento"
        },
        "observaciones_liquidacion": {
            "dias": 60,
            "tipo": "calendario",
            "descripcion": "Plazo para pronunciarse sobre liquidación",
            "base_legal": "Art. 209 del Reglamento"
        },
        "consulta_mercado": {
            "dias": 6,
            "tipo": "habiles",
            "descripcion": "Plazo para consulta al mercado (D.S. 001-2026-EF)",
            "base_legal": "Art. 51 del Reglamento (modificado)"
        }
    }
    
    def __init__(self):
        self.feriados = set(self.FERIADOS_2025 + self.FERIADOS_2026)
    
    def es_dia_habil(self, fecha: datetime) -> bool:
        """
        Verifica si una fecha es día hábil
        
        Args:
            fecha: Fecha a verificar
            
        Returns:
            True si es día hábil
        """
        # Verificar si es fin de semana
        if fecha.weekday() >= 5:  # 5=Sábado, 6=Domingo
            return False
        
        # Verificar si es feriado
        fecha_str = fecha.strftime("%Y-%m-%d")
        if fecha_str in self.feriados:
            return False
        
        return True
    
    def agregar_dias_habiles(self, fecha_inicio: datetime, dias: int) -> datetime:
        """
        Agrega días hábiles a una fecha
        
        Args:
            fecha_inicio: Fecha de inicio
            dias: Cantidad de días hábiles a agregar
            
        Returns:
            Fecha resultante
        """
        fecha = fecha_inicio
        dias_agregados = 0
        
        while dias_agregados < dias:
            fecha += timedelta(days=1)
            if self.es_dia_habil(fecha):
                dias_agregados += 1
        
        return fecha
    
    def agregar_dias_calendario(self, fecha_inicio: datetime, dias: int) -> datetime:
        """Agrega días calendario (corridos) a una fecha"""
        return fecha_inicio + timedelta(days=dias)
    
    def calcular_plazo(
        self,
        fecha_inicio: str,
        tipo_plazo: str
    ) -> Dict:
        """
        Calcula un plazo específico según la normativa
        
        Args:
            fecha_inicio: Fecha de inicio en formato YYYY-MM-DD o DD/MM/YYYY
            tipo_plazo: Clave del plazo (ver PLAZOS_LEGALES)
            
        Returns:
            Dict con fecha límite y detalles
        """
        # Parsear fecha
        try:
            if "/" in fecha_inicio:
                fecha = datetime.strptime(fecha_inicio, "%d/%m/%Y")
            else:
                fecha = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        except ValueError:
            return {"error": "Formato de fecha inválido. Use DD/MM/YYYY o YYYY-MM-DD"}
        
        if tipo_plazo not in self.PLAZOS_LEGALES:
            return {"error": f"Tipo de plazo '{tipo_plazo}' no reconocido"}
        
        plazo_info = self.PLAZOS_LEGALES[tipo_plazo]
        dias = plazo_info["dias"]
        tipo = plazo_info["tipo"]
        
        if tipo == "habiles":
            fecha_limite = self.agregar_dias_habiles(fecha, dias)
        else:
            fecha_limite = self.agregar_dias_calendario(fecha, dias)
        
        return {
            "fecha_inicio": fecha.strftime("%d/%m/%Y"),
            "fecha_limite": fecha_limite.strftime("%d/%m/%Y"),
            "dias": dias,
            "tipo_dias": tipo,
            "descripcion": plazo_info["descripcion"],
            "base_legal": plazo_info["base_legal"],
            "dia_semana": self._nombre_dia(fecha_limite.weekday())
        }
    
    def calcular_plazo_generico(
        self,
        fecha_inicio: str,
        dias: int,
        tipo: str = "habiles"
    ) -> Dict:
        """
        Calcula un plazo genérico
        
        Args:
            fecha_inicio: Fecha en formato DD/MM/YYYY o YYYY-MM-DD
            dias: Cantidad de días
            tipo: 'habiles' o 'calendario'
        """
        try:
            if "/" in fecha_inicio:
                fecha = datetime.strptime(fecha_inicio, "%d/%m/%Y")
            else:
                fecha = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        except ValueError:
            return {"error": "Formato de fecha inválido"}
        
        if tipo == "habiles":
            fecha_limite = self.agregar_dias_habiles(fecha, dias)
        else:
            fecha_limite = self.agregar_dias_calendario(fecha, dias)
        
        return {
            "fecha_inicio": fecha.strftime("%d/%m/%Y"),
            "fecha_limite": fecha_limite.strftime("%d/%m/%Y"),
            "dias": dias,
            "tipo_dias": tipo,
            "dia_semana": self._nombre_dia(fecha_limite.weekday())
        }
    
    def _nombre_dia(self, weekday: int) -> str:
        """Retorna el nombre del día de la semana"""
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        return dias[weekday]
    
    def calcular_plazo_apelacion(self, fecha_notificacion: str) -> Dict:
        """Calcula el plazo para apelar (8 días hábiles)"""
        resultado = self.calcular_plazo(fecha_notificacion, "apelacion")
        resultado["tipo_plazo"] = "Recurso de Apelación"
        return resultado
    
    def calcular_plazo_contrato(self, fecha_buena_pro: str) -> Dict:
        """Calcula el plazo para suscribir contrato (8 días hábiles)"""
        resultado = self.calcular_plazo(fecha_buena_pro, "suscripcion_contrato")
        resultado["tipo_plazo"] = "Suscripción de Contrato"
        return resultado
    
    def formatear_resultado(self, resultado: Dict) -> str:
        """Formatea el resultado para mostrar en chat"""
        if "error" in resultado:
            return f"❌ Error: {resultado['error']}"
        
        return f"""📅 **CÁLCULO DE PLAZO**

📋 **Tipo:** {resultado.get('tipo_plazo', resultado.get('descripcion', 'Plazo'))}

📆 **Fechas:**
• Fecha inicio: **{resultado['fecha_inicio']}**
• Fecha límite: **{resultado['fecha_limite']}** ({resultado['dia_semana']})

⏱️ **Plazo:** {resultado['dias']} días {resultado['tipo_dias']}

📚 *Base legal: {resultado.get('base_legal', 'D.S. N° 009-2025-EF')}*"""
    
    def detect_and_calculate(self, message: str) -> Optional[str]:
        """
        Detecta si el mensaje es consulta de plazos y la procesa
        """
        message_lower = message.lower()
        
        # Detectar si es consulta de plazos
        keywords = ['plazo', 'días hábiles', 'dias habiles', 'fecha límite', 'fecha limite', 'cuándo vence', 'cuando vence']
        if not any(kw in message_lower for kw in keywords):
            return None
        
        # Buscar fecha en el mensaje
        fecha_match = re.search(r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{2,4})', message)
        
        # Detectar tipo de plazo
        tipo_plazo = None
        if any(w in message_lower for w in ['apelar', 'apelación', 'apelacion', 'impugnar']):
            tipo_plazo = "apelacion"
        elif any(w in message_lower for w in ['contrato', 'suscribir', 'firmar']):
            tipo_plazo = "suscripcion_contrato"
        elif any(w in message_lower for w in ['consulta', 'observacion']):
            if 'abreviado' in message_lower:
                tipo_plazo = "consultas_observaciones_abreviado"
            else:
                tipo_plazo = "consultas_observaciones_lp"
        elif any(w in message_lower for w in ['conformidad']):
            tipo_plazo = "conformidad_bienes"
        elif any(w in message_lower for w in ['ampliación', 'ampliacion']):
            tipo_plazo = "ampliacion_plazo"
        elif any(w in message_lower for w in ['arbitraje']):
            tipo_plazo = "inicio_arbitraje"
        elif any(w in message_lower for w in ['liquidación', 'liquidacion']):
            tipo_plazo = "liquidacion_obra"
        
        if fecha_match and tipo_plazo:
            dia, mes, año = fecha_match.groups()
            if len(año) == 2:
                año = "20" + año
            fecha = f"{dia}/{mes}/{año}"
            
            resultado = self.calcular_plazo(fecha, tipo_plazo)
            return self.formatear_resultado(resultado)
        
        # Información general
        return get_plazos_info()


def get_plazos_info() -> str:
    """Retorna información sobre plazos importantes"""
    return """📅 **PLAZOS IMPORTANTES EN CONTRATACIONES PÚBLICAS**

| Plazo | Días | Tipo | Base Legal |
|-------|------|------|------------|
| Recurso de apelación | 8 | Hábiles | Art. 97 |
| Suscripción de contrato | 8 | Hábiles | Art. 139 |
| Consultas/Obs. LP | 10 | Hábiles | Art. 68 |
| Consultas/Obs. Abreviado | 5 | Hábiles | Art. 76 |
| Absolver consultas | 5 | Hábiles | Art. 68 |
| Integración de bases | 3 | Hábiles | Art. 69 |
| Conformidad | 10 | Hábiles | Art. 168 |
| Solicitar ampliación | 8 | Hábiles | Art. 171 |
| Carta notarial resolución | 5 | Calendario | Art. 176 |
| Inicio de arbitraje | 30 | Hábiles | Art. 227 |
| Presentar liquidación | 60 | Calendario | Art. 209 |
| Consulta al mercado | 6 | Hábiles | Art. 51 (mod.) |

🗓️ **Para calcular un plazo específico:**
Proporcione la fecha de inicio y el tipo de plazo.

📝 **Ejemplo:** "¿Cuál es el plazo para apelar si notificaron el 21/01/2026?"

📚 *Base legal: D.S. N° 009-2025-EF*"""
