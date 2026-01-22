"""
Calculadora de Penalidades por Mora
Ley N° 32069 - Art. 163 del Reglamento D.S. N° 009-2025-EF
"""
import re
from typing import Dict, Optional
from datetime import datetime


class PenaltiesCalculator:
    """
    Calcula penalidades por mora en contratos públicos
    
    Fórmula: Penalidad diaria = (0.10 × monto) / (F × plazo)
    
    Donde F:
    - 0.25: Bienes/servicios/consultorías ≤ 60 días
    - 0.40: Bienes/servicios > 60 días, consultorías de obras, ejecución de obras
    """
    
    # Constantes según Art. 163 del Reglamento
    FACTOR_CORTO = 0.25   # Plazo ≤ 60 días
    FACTOR_LARGO = 0.40   # Plazo > 60 días o obras
    TOPE_PENALIDADES = 0.10  # 10% del monto del contrato
    
    def __init__(self):
        self.historial = []
    
    def determinar_factor_f(self, plazo_dias: int, tipo: str) -> float:
        """
        Determina el factor F según tipo de contrato y plazo
        
        Args:
            plazo_dias: Plazo del contrato en días calendario
            tipo: 'bienes', 'servicios', 'consultoria', 'obras'
            
        Returns:
            Factor F (0.25 o 0.40)
        """
        tipo_lower = tipo.lower()
        
        # Obras siempre usa F = 0.40
        if tipo_lower == 'obras':
            return self.FACTOR_LARGO
        
        # Consultoría de obras usa F = 0.40
        if 'consultoria' in tipo_lower and 'obra' in tipo_lower:
            return self.FACTOR_LARGO
        
        # Bienes y servicios: depende del plazo
        if plazo_dias <= 60:
            return self.FACTOR_CORTO
        else:
            return self.FACTOR_LARGO
    
    def calcular_penalidad_diaria(
        self, 
        monto_contrato: float, 
        plazo_dias: int, 
        tipo: str
    ) -> Dict:
        """
        Calcula la penalidad diaria por mora
        
        Args:
            monto_contrato: Monto del contrato en soles
            plazo_dias: Plazo del contrato en días calendario
            tipo: Tipo de contrato
            
        Returns:
            Dict con penalidad diaria y detalles
        """
        factor_f = self.determinar_factor_f(plazo_dias, tipo)
        
        # Fórmula: (0.10 × monto) / (F × plazo)
        penalidad_diaria = (0.10 * monto_contrato) / (factor_f * plazo_dias)
        
        return {
            "penalidad_diaria": round(penalidad_diaria, 2),
            "factor_f": factor_f,
            "monto_contrato": monto_contrato,
            "plazo_dias": plazo_dias,
            "tipo": tipo,
            "formula": f"(0.10 × S/{monto_contrato:,.2f}) / ({factor_f} × {plazo_dias})"
        }
    
    def calcular_penalidad_total(
        self,
        monto_contrato: float,
        plazo_dias: int,
        dias_atraso: int,
        tipo: str
    ) -> Dict:
        """
        Calcula la penalidad total acumulada por días de atraso
        
        Args:
            monto_contrato: Monto del contrato en soles
            plazo_dias: Plazo del contrato en días calendario
            dias_atraso: Cantidad de días de atraso
            tipo: Tipo de contrato
            
        Returns:
            Dict con penalidad total, porcentaje y si amerita resolución
        """
        calculo_diario = self.calcular_penalidad_diaria(monto_contrato, plazo_dias, tipo)
        penalidad_diaria = calculo_diario["penalidad_diaria"]
        
        penalidad_total = penalidad_diaria * dias_atraso
        tope = monto_contrato * self.TOPE_PENALIDADES
        
        # Verificar si supera el tope
        supera_tope = penalidad_total >= tope
        penalidad_aplicable = min(penalidad_total, tope)
        
        porcentaje = (penalidad_aplicable / monto_contrato) * 100
        
        resultado = {
            "penalidad_diaria": penalidad_diaria,
            "dias_atraso": dias_atraso,
            "penalidad_calculada": round(penalidad_total, 2),
            "penalidad_aplicable": round(penalidad_aplicable, 2),
            "tope_maximo": round(tope, 2),
            "porcentaje_del_contrato": round(porcentaje, 2),
            "supera_tope": supera_tope,
            "amerita_resolucion": porcentaje >= 10.0,
            "factor_f": calculo_diario["factor_f"],
            "monto_contrato": monto_contrato,
            "base_legal": "Art. 163 del D.S. N° 009-2025-EF"
        }
        
        # Guardar en historial
        self.historial.append(resultado)
        
        return resultado
    
    def formatear_resultado(self, resultado: Dict) -> str:
        """Formatea el resultado para mostrar en chat"""
        
        respuesta = f"""⚖️ **CÁLCULO DE PENALIDADES POR MORA**

📋 **Datos del contrato:**
• Monto: S/ {resultado['monto_contrato']:,.2f}
• Plazo: {resultado.get('plazo_dias', 'N/A')} días
• Factor F: {resultado['factor_f']}

📊 **Cálculo de penalidad:**
• Penalidad diaria: **S/ {resultado['penalidad_diaria']:,.2f}**
• Días de atraso: {resultado['dias_atraso']}
• Penalidad calculada: S/ {resultado['penalidad_calculada']:,.2f}

💰 **Resultado:**
• **Penalidad aplicable: S/ {resultado['penalidad_aplicable']:,.2f}**
• Porcentaje del contrato: **{resultado['porcentaje_del_contrato']:.2f}%**
• Tope máximo (10%): S/ {resultado['tope_maximo']:,.2f}
"""
        
        if resultado['supera_tope']:
            respuesta += "\n⚠️ **La penalidad calculada supera el tope del 10%**"
        
        if resultado['amerita_resolucion']:
            respuesta += """

🚨 **ATENCIÓN:** La penalidad alcanza el 10% del contrato.
Según el Art. 164 del Reglamento, la Entidad puede **resolver el contrato** por incumplimiento parcial.
• La resolución NO es automática
• Requiere carta notarial previa
• El contratista puede ser sancionado por el Tribunal"""
        
        respuesta += f"\n\n📚 *Base legal: {resultado['base_legal']}*"
        
        return respuesta
    
    def detect_and_calculate(self, message: str) -> Optional[str]:
        """
        Detecta si el mensaje es una consulta de penalidades y la procesa
        
        Returns:
            Respuesta formateada o None si no es consulta de penalidades
        """
        message_lower = message.lower()
        
        # Detectar si es consulta de penalidades
        keywords = ['penalidad', 'mora', 'atraso', 'retraso', 'días de atraso', 'demora']
        if not any(kw in message_lower for kw in keywords):
            return None
        
        # Buscar monto
        monto_match = re.search(r's/?\.?\s*([\d,]+(?:\.\d{2})?)', message_lower)
        if not monto_match:
            monto_match = re.search(r'([\d,]+(?:\.\d{2})?)\s*(?:soles|sol)', message_lower)
        
        # Buscar plazo
        plazo_match = re.search(r'plazo\s*(?:de)?\s*(\d+)\s*(?:días|dias|d)', message_lower)
        if not plazo_match:
            plazo_match = re.search(r'(\d+)\s*(?:días|dias)\s*(?:de\s*)?plazo', message_lower)
        
        # Buscar días de atraso
        atraso_match = re.search(r'(\d+)\s*(?:días|dias)\s*(?:de\s*)?(?:atraso|mora|retraso|demora)', message_lower)
        if not atraso_match:
            atraso_match = re.search(r'(?:atraso|mora|retraso|demora)\s*(?:de)?\s*(\d+)\s*(?:días|dias)', message_lower)
        
        # Buscar tipo
        tipo = 'bienes'  # default
        if 'obra' in message_lower:
            tipo = 'obras'
        elif 'servicio' in message_lower:
            tipo = 'servicios'
        elif 'consultor' in message_lower:
            tipo = 'consultoria'
        
        # Si tenemos todos los datos, calcular
        if monto_match and plazo_match and atraso_match:
            monto = float(monto_match.group(1).replace(',', ''))
            plazo = int(plazo_match.group(1))
            atraso = int(atraso_match.group(1))
            
            resultado = self.calcular_penalidad_total(monto, plazo, atraso, tipo)
            return self.formatear_resultado(resultado)
        
        # Si falta información, dar guía
        return """⚖️ **CALCULADORA DE PENALIDADES**

Para calcular la penalidad necesito los siguientes datos:
1. **Monto del contrato** (ej: S/ 500,000)
2. **Plazo del contrato** en días (ej: 90 días)
3. **Días de atraso** (ej: 15 días de atraso)
4. **Tipo de contrato**: bienes, servicios, consultoría u obras

📝 **Ejemplo de consulta:**
"Tengo un contrato de S/ 500,000 con plazo de 90 días. El contratista tiene 15 días de atraso. ¿Cuál es la penalidad?"

📚 *Base legal: Art. 163 del D.S. N° 009-2025-EF*"""


def get_penalties_info() -> str:
    """Retorna información general sobre penalidades"""
    return """⚖️ **PENALIDADES EN CONTRATACIONES PÚBLICAS**

**Base Legal:** Art. 163-164 del D.S. N° 009-2025-EF

**Fórmula de penalidad diaria:**
```
Penalidad = (0.10 × Monto) / (F × Plazo)
```

**Factor F:**
| Situación | Factor |
|-----------|--------|
| Bienes/servicios ≤ 60 días | 0.25 |
| Bienes/servicios > 60 días | 0.40 |
| Obras | 0.40 |
| Consultoría de obras | 0.40 |

**Tope máximo:** 10% del monto del contrato

**Si se alcanza el tope (10%):**
• La Entidad PUEDE (no debe) resolver el contrato
• Requiere carta notarial de 5 días calendario
• No es resolución automática

**Penalidades adicionales:**
Las bases pueden incluir otras penalidades por incumplimientos distintos a la mora."""
