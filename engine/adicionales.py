"""
Calculadora de Prestaciones Adicionales y Deductivos
Ley N° 32069 - Arts. 189-196 del Reglamento D.S. N° 009-2025-EF
"""
import re
from typing import Dict, Optional


class AdicionalesCalculator:
    """
    Calcula adicionales de obra, prestaciones adicionales y deductivos
    
    Límites:
    - Adicionales de obra: hasta 15% (Entidad), hasta 50% (CGR)
    - Prestaciones adicionales bienes/servicios: hasta 25%
    - Deductivos: hasta 50% sin nueva convocatoria
    """
    
    # Constantes según el Reglamento
    LIMITE_ADICIONAL_OBRA_ENTIDAD = 0.15  # 15% - aprueba Titular
    LIMITE_ADICIONAL_OBRA_CGR = 0.50      # 50% - requiere CGR
    LIMITE_ADICIONAL_BIENES_SERVICIOS = 0.25  # 25%
    LIMITE_DEDUCTIVO_VINCULADO = 0.50     # 50%
    
    def __init__(self):
        self.historial = []
    
    def calcular_adicional_obra(
        self,
        monto_contrato: float,
        monto_adicional: float,
        descripcion: str = ""
    ) -> Dict:
        """
        Calcula adicional de obra y determina quién debe aprobarlo
        
        Args:
            monto_contrato: Monto original del contrato
            monto_adicional: Monto del adicional solicitado
            descripcion: Descripción del adicional
            
        Returns:
            Dict con porcentaje, aprobador y requisitos
        """
        porcentaje = (monto_adicional / monto_contrato) * 100
        
        # Determinar quién aprueba
        if porcentaje <= 15:
            aprobador = "Titular de la Entidad"
            requiere_cgr = False
            aprobacion = "Resolución del Titular de la Entidad"
        elif porcentaje <= 50:
            aprobador = "Contraloría General de la República (CGR)"
            requiere_cgr = True
            aprobacion = "Autorización previa de la CGR"
        else:
            aprobador = "NO PERMITIDO"
            requiere_cgr = False
            aprobacion = "Excede el límite máximo de 50%"
        
        # Calcular montos acumulados
        monto_total = monto_contrato + monto_adicional
        
        resultado = {
            "monto_contrato": monto_contrato,
            "monto_adicional": monto_adicional,
            "monto_total": monto_total,
            "porcentaje_adicional": round(porcentaje, 2),
            "aprobador": aprobador,
            "requiere_cgr": requiere_cgr,
            "aprobacion_requerida": aprobacion,
            "es_procedente": porcentaje <= 50,
            "descripcion": descripcion,
            "base_legal": "Arts. 189-190 del D.S. N° 009-2025-EF"
        }
        
        self.historial.append(resultado)
        return resultado
    
    def calcular_adicional_bienes_servicios(
        self,
        monto_contrato: float,
        monto_adicional: float
    ) -> Dict:
        """
        Calcula prestación adicional de bienes o servicios
        Límite: 25% del monto del contrato
        """
        porcentaje = (monto_adicional / monto_contrato) * 100
        es_procedente = porcentaje <= 25
        
        resultado = {
            "monto_contrato": monto_contrato,
            "monto_adicional": monto_adicional,
            "monto_total": monto_contrato + monto_adicional,
            "porcentaje_adicional": round(porcentaje, 2),
            "limite_maximo": 25,
            "es_procedente": es_procedente,
            "aprobador": "Titular de la Entidad" if es_procedente else "NO PERMITIDO",
            "observacion": "" if es_procedente else "Excede el límite del 25%",
            "base_legal": "Art. 196 del D.S. N° 009-2025-EF"
        }
        
        return resultado
    
    def calcular_deductivo(
        self,
        monto_contrato: float,
        monto_deductivo: float,
        es_vinculado: bool = True
    ) -> Dict:
        """
        Calcula deductivo (reducción) del contrato
        
        Args:
            monto_contrato: Monto original
            monto_deductivo: Monto a reducir
            es_vinculado: Si está vinculado a un adicional
        """
        porcentaje = (monto_deductivo / monto_contrato) * 100
        monto_final = monto_contrato - monto_deductivo
        
        # Regla: deductivos vinculados hasta 50%
        limite = 50 if es_vinculado else 25
        es_procedente = porcentaje <= limite
        
        resultado = {
            "monto_contrato": monto_contrato,
            "monto_deductivo": monto_deductivo,
            "monto_final": monto_final,
            "porcentaje_deductivo": round(porcentaje, 2),
            "es_vinculado": es_vinculado,
            "limite_aplicable": limite,
            "es_procedente": es_procedente,
            "observacion": "Requiere nueva convocatoria" if not es_procedente else "Procedente",
            "base_legal": "Art. 191 del D.S. N° 009-2025-EF"
        }
        
        return resultado
    
    def calcular_adicional_mayores_metrados(
        self,
        monto_contrato: float,
        presupuesto_adicional: float,
        tipo: str = "sistema_precios_unitarios"
    ) -> Dict:
        """
        Calcula adicionales por mayores metrados en obras a precios unitarios
        """
        porcentaje = (presupuesto_adicional / monto_contrato) * 100
        
        if tipo == "sistema_precios_unitarios":
            observacion = "En contratos a precios unitarios, los mayores metrados se pagan con los precios del contrato"
        else:
            observacion = "En contratos a suma alzada, los adicionales requieren presupuesto adicional"
        
        resultado = {
            "monto_contrato": monto_contrato,
            "monto_mayores_metrados": presupuesto_adicional,
            "porcentaje": round(porcentaje, 2),
            "tipo_contrato": tipo,
            "observacion": observacion,
            "requiere_resolucion": porcentaje > 0,
            "base_legal": "Art. 189-190 del D.S. N° 009-2025-EF"
        }
        
        return resultado
    
    def formatear_resultado_obra(self, resultado: Dict) -> str:
        """Formatea resultado de adicional de obra para chat"""
        
        estado = "✅ PROCEDENTE" if resultado['es_procedente'] else "❌ NO PROCEDENTE"
        
        respuesta = f"""🏗️ **CÁLCULO DE ADICIONAL DE OBRA**

📋 **Datos del contrato:**
• Monto original: S/ {resultado['monto_contrato']:,.2f}
• Monto adicional: S/ {resultado['monto_adicional']:,.2f}
• Monto total: S/ {resultado['monto_total']:,.2f}

📊 **Análisis:**
• Porcentaje adicional: **{resultado['porcentaje_adicional']:.2f}%**
• Estado: **{estado}**

👤 **Aprobación requerida:**
• **{resultado['aprobador']}**
• {resultado['aprobacion_requerida']}
"""
        
        if resultado['requiere_cgr']:
            respuesta += """
⚠️ **IMPORTANTE - Requiere CGR:**
1. Informe técnico justificatorio
2. Resolución del Titular autorizando la gestión ante CGR
3. Expediente técnico del adicional
4. Pronunciamiento de la CGR ANTES de ejecutar"""
        
        respuesta += f"\n\n📚 *Base legal: {resultado['base_legal']}*"
        
        return respuesta
    
    def formatear_resultado_bienes_servicios(self, resultado: Dict) -> str:
        """Formatea resultado de adicional de bienes/servicios"""
        
        estado = "✅ PROCEDENTE" if resultado['es_procedente'] else "❌ NO PROCEDENTE"
        
        return f"""📦 **CÁLCULO DE PRESTACIÓN ADICIONAL**

📋 **Datos del contrato:**
• Monto original: S/ {resultado['monto_contrato']:,.2f}
• Monto adicional: S/ {resultado['monto_adicional']:,.2f}
• Monto total: S/ {resultado['monto_total']:,.2f}

📊 **Análisis:**
• Porcentaje adicional: **{resultado['porcentaje_adicional']:.2f}%**
• Límite máximo: {resultado['limite_maximo']}%
• Estado: **{estado}**

👤 **Aprobación:** {resultado['aprobador']}
{f"⚠️ {resultado['observacion']}" if resultado['observacion'] else ""}

📚 *Base legal: {resultado['base_legal']}*"""
    
    def detect_and_calculate(self, message: str) -> Optional[str]:
        """
        Detecta si el mensaje es consulta de adicionales y la procesa
        """
        message_lower = message.lower()
        
        # Detectar si es consulta de adicionales
        keywords = ['adicional', 'mayores metrados', 'deductivo', 'reduccion', 'ampliacion de prestacion']
        if not any(kw in message_lower for kw in keywords):
            return None
        
        # Determinar si es obra o bienes/servicios
        es_obra = any(w in message_lower for w in ['obra', 'construccion', 'metrados'])
        
        # Buscar monto del contrato
        monto_match = re.search(r's/?\.?\s*([\d,]+(?:\.\d{2})?)', message_lower)
        
        # Buscar porcentaje del adicional
        porcentaje_match = re.search(r'(\d+(?:\.\d+)?)\s*%', message_lower)
        
        # Si tenemos monto y porcentaje
        if monto_match and porcentaje_match:
            monto = float(monto_match.group(1).replace(',', ''))
            porcentaje = float(porcentaje_match.group(1))
            monto_adicional = monto * (porcentaje / 100)
            
            if es_obra:
                resultado = self.calcular_adicional_obra(monto, monto_adicional)
                return self.formatear_resultado_obra(resultado)
            else:
                resultado = self.calcular_adicional_bienes_servicios(monto, monto_adicional)
                return self.formatear_resultado_bienes_servicios(resultado)
        
        # Si solo tenemos monto, buscar monto del adicional directamente
        if monto_match:
            # Buscar segundo monto
            montos = re.findall(r's/?\.?\s*([\d,]+(?:\.\d{2})?)', message_lower)
            if len(montos) >= 2:
                monto_contrato = float(montos[0].replace(',', ''))
                monto_adicional = float(montos[1].replace(',', ''))
                
                if es_obra:
                    resultado = self.calcular_adicional_obra(monto_contrato, monto_adicional)
                    return self.formatear_resultado_obra(resultado)
                else:
                    resultado = self.calcular_adicional_bienes_servicios(monto_contrato, monto_adicional)
                    return self.formatear_resultado_bienes_servicios(resultado)
        
        # Dar información general
        return get_adicionales_info()


def get_adicionales_info() -> str:
    """Retorna información general sobre adicionales"""
    return """🏗️ **ADICIONALES EN CONTRATACIONES PÚBLICAS**

**1. ADICIONALES DE OBRA:**

| Porcentaje | Aprobador | Requisitos |
|------------|-----------|------------|
| Hasta 15% | Titular de la Entidad | Resolución aprobatoria |
| 15% - 50% | CGR (Contraloría) | Autorización previa de CGR |
| > 50% | NO PERMITIDO | - |

**2. PRESTACIONES ADICIONALES (Bienes/Servicios):**
• Límite: **25%** del monto del contrato
• Aprueba: Titular de la Entidad

**3. DEDUCTIVOS:**
• Deductivo vinculado a adicional: hasta 50%
• Deductivo no vinculado: hasta 25%

⚠️ **Para calcular, proporcione:**
• Monto del contrato
• Monto o porcentaje del adicional
• Tipo: obra, bienes o servicios

📝 **Ejemplo:** "Necesito un adicional del 18% en una obra de S/ 3,000,000. ¿Quién lo aprueba?"

📚 *Base legal: Arts. 189-196 del D.S. N° 009-2025-EF*"""
