"""
Calculadora de Procedimientos de Selección
Ley N° 32069 - Montos vigentes 2026
Incluye: tasas de apelación, integración con penalidades, adicionales y plazos
"""
import re
from typing import Dict, Optional


class ProcurementCalculator:
    """
    Calcula el procedimiento de selección según monto y tipo de contratación
    Basado en Ley N° 32069, D.S. 009-2025-EF y Ley N° 32513
    """
    
    # UIT 2026 = S/ 5,500 (D.S. N° 301-2025-EF)
    UIT_2026 = 5500
    
    # Monto mínimo para procedimientos de selección (8 UIT)
    MONTO_MINIMO = 8 * UIT_2026  # S/ 44,000
    
    # Topes para procedimientos 2026
    TOPES = {
        'bienes': {
            'licitacion_publica': 485000,
            'comparacion_precios_max': 100000,
        },
        'servicios': {
            'concurso_publico': 485000,
            'comparacion_precios_max': 100000,
        },
        'consultoria': {
            'concurso_publico': 485000,
            'comparacion_precios_max': 100000,
        },
        'obras': {
            'licitacion_publica_min': 5000000,
            'licitacion_publica_max': 79000000,
        }
    }
    
    def get_procedure(self, monto: float, tipo: str) -> dict:
        """
        Determina el procedimiento de selección correspondiente
        
        Args:
            monto: Valor estimado de la contratación en soles
            tipo: 'bienes', 'servicios', 'consultoria', 'obras'
        
        Returns:
            dict con procedimiento recomendado y detalles
        """
        tipo = tipo.lower().strip()
        
        # Validar tipo
        tipos_validos = ['bienes', 'servicios', 'consultoria', 'obras']
        if tipo not in tipos_validos:
            return {
                'error': f'Tipo inválido. Usa: {", ".join(tipos_validos)}',
                'monto': monto,
                'tipo': tipo
            }
        
        # Menor a 8 UIT = No aplica Ley de Contrataciones
        if monto <= self.MONTO_MINIMO:
            return {
                'procedimiento': 'Contratación menor a 8 UIT',
                'descripcion': 'No requiere proceso de selección según Ley N° 32069',
                'base_legal': 'Art. 5, inciso a) - Ley N° 32069',
                'monto': monto,
                'tipo': tipo,
                'monto_minimo': self.MONTO_MINIMO,
                'nota': 'Se rige por procedimientos internos de la entidad'
            }
        
        # Determinar procedimiento según tipo
        if tipo == 'bienes':
            return self._calcular_bienes(monto)
        elif tipo in ['servicios', 'consultoria']:
            return self._calcular_servicios(monto, tipo)
        else:
            return self._calcular_obras(monto)
    
    def _calcular_bienes(self, monto: float) -> dict:
        """Calcula procedimiento para bienes"""
        topes = self.TOPES['bienes']
        
        if monto >= topes['licitacion_publica']:
            return {
                'procedimiento': 'Licitación Pública',
                'descripcion': 'Procedimiento para contratación de bienes de mayor cuantía',
                'base_legal': 'Art. 54, inc. 1 - Ley N° 32069',
                'monto': monto,
                'tipo': 'bienes',
                'rango': f"≥ S/ {topes['licitacion_publica']:,.0f}"
            }
        elif monto <= topes['comparacion_precios_max']:
            return {
                'procedimiento': 'Comparación de Precios o Licitación Pública Abreviada',
                'descripcion': 'Puede usar Comparación de Precios (hasta S/100,000) o Licitación Pública Abreviada',
                'base_legal': 'Arts. 54-55 - Ley N° 32069',
                'monto': monto,
                'tipo': 'bienes',
                'opciones': [
                    'Comparación de Precios: Para bienes de disponibilidad inmediata',
                    'Licitación Pública Abreviada: Procedimiento simplificado',
                    'Subasta Inversa Electrónica: Si el bien está en listado OECE'
                ]
            }
        else:
            return {
                'procedimiento': 'Licitación Pública Abreviada',
                'descripcion': 'Procedimiento simplificado para montos intermedios',
                'base_legal': 'Art. 54 - Ley N° 32069',
                'monto': monto,
                'tipo': 'bienes',
                'rango': f"> S/ {self.MONTO_MINIMO:,.0f} y < S/ {topes['licitacion_publica']:,.0f}",
                'alternativas': ['Subasta Inversa Electrónica (si aplica)']
            }
    
    def _calcular_servicios(self, monto: float, subtipo: str) -> dict:
        """Calcula procedimiento para servicios y consultoría"""
        topes = self.TOPES[subtipo]
        
        if monto >= topes['concurso_publico']:
            return {
                'procedimiento': 'Concurso Público',
                'descripcion': f'Procedimiento para {subtipo} de mayor cuantía',
                'base_legal': 'Art. 54, inc. 2 - Ley N° 32069',
                'monto': monto,
                'tipo': subtipo,
                'rango': f"≥ S/ {topes['concurso_publico']:,.0f}"
            }
        elif monto <= topes['comparacion_precios_max']:
            return {
                'procedimiento': 'Comparación de Precios o Concurso Público Abreviado',
                'descripcion': 'Puede usar Comparación de Precios o Concurso Abreviado',
                'base_legal': 'Arts. 54-55 - Ley N° 32069',
                'monto': monto,
                'tipo': subtipo,
                'opciones': [
                    'Comparación de Precios: Para servicios de disponibilidad inmediata',
                    'Concurso Público Abreviado: Procedimiento simplificado'
                ]
            }
        else:
            return {
                'procedimiento': 'Concurso Público Abreviado',
                'descripcion': 'Procedimiento simplificado para montos intermedios',
                'base_legal': 'Art. 54 - Ley N° 32069',
                'monto': monto,
                'tipo': subtipo,
                'rango': f"> S/ {self.MONTO_MINIMO:,.0f} y < S/ {topes['concurso_publico']:,.0f}"
            }
    
    def _calcular_obras(self, monto: float) -> dict:
        """Calcula procedimiento para obras"""
        topes = self.TOPES['obras']
        
        if monto >= topes['licitacion_publica_max']:
            return {
                'procedimiento': 'Licitación Pública Internacional',
                'descripcion': 'Obras de gran envergadura que superan el tope nacional',
                'base_legal': 'Art. 54 - Ley N° 32069 y normativa especial',
                'monto': monto,
                'tipo': 'obras',
                'rango': f"≥ S/ {topes['licitacion_publica_max']:,.0f}",
                'nota': 'Puede requerir procedimientos especiales'
            }
        elif monto >= topes['licitacion_publica_min']:
            return {
                'procedimiento': 'Licitación Pública',
                'descripcion': 'Procedimiento para obras de mayor cuantía',
                'base_legal': 'Art. 54, inc. 3 - Ley N° 32069',
                'monto': monto,
                'tipo': 'obras',
                'rango': f"≥ S/ {topes['licitacion_publica_min']:,.0f} y < S/ {topes['licitacion_publica_max']:,.0f}"
            }
        else:
            return {
                'procedimiento': 'Licitación Pública Abreviada',
                'descripcion': 'Procedimiento simplificado para obras de menor cuantía',
                'base_legal': 'Art. 54 - Ley N° 32069',
                'monto': monto,
                'tipo': 'obras',
                'rango': f"> S/ {self.MONTO_MINIMO:,.0f} y < S/ {topes['licitacion_publica_min']:,.0f}"
            }
    
    def detect_and_calculate(self, message: str) -> str:
        """
        Detecta si el mensaje contiene una consulta de cálculo y la procesa
        
        Returns:
            Respuesta formateada o None si no es una consulta de cálculo
        """
        message_lower = message.lower()
        
        # Palabras clave que indican una consulta LEGAL y NO de cálculo tarifario
        # Si estas palabras están presentes, el calculador se inhibe para dejar pasar al RAG
        BYPASS_KEYWORDS = [
            'impedimento', 'impedido', 'prohibido', 'cuñado', 'pariente', 'alcalde',
            'simplificada', 'adjudicacion simplificada', 'adjudicación simplificada',
            'garantia', 'garantía', 'fiel cumplimiento',
            'penalidad', 'mora', 'resolucion', 'resolución',
            'puedo contratar', 'puede contratar', 'legal', 'ilegal', 'procede',
            'plazo', 'apelacion', 'apelación'
        ]
        
        # Si contiene alguna palabra de exclusión, retornamos None para que lo atienda el RAG/Gemini
        if any(keyword in message_lower for keyword in BYPASS_KEYWORDS):
            return None

        # Patrones para detectar consultas de cálculo
        # Se añade negative lookahead (?!\s*(?:%|por ciento)) para evitar porcentajes
        patterns = [
            r'(?:monto|valor|presupuesto|precio).*?(?:de|por|:)?\s*(?:s/?\.?\s*)?(\d[\d,\.]*)(?!\s*(?:%|por ciento))',
            r'(?:s/?\.?\s*)(\d[\d,\.]*)(?!\s*(?:%|por ciento))',
            r'(\d[\d,\.]*)\s*(?:soles|nuevos soles)(?!\s*(?:%|por ciento))',
            r'(?:comprar?|contratar?|licitar?).*?(\d[\d,\.]*)(?!\s*(?:%|por ciento))',
        ]
        
        monto = None
        for pattern in patterns:
            match = re.search(pattern, message_lower)
            if match:
                monto_str = match.group(1).replace(',', '').replace('.', '')
                try:
                    monto = float(monto_str)
                    break
                except:
                    continue
        
        if monto is None:
            return None
        
        # Detectar tipo
        tipo = 'bienes'  # default
        if any(word in message_lower for word in ['servicio', 'consultor', 'asesor']):
            tipo = 'servicios'
        if any(word in message_lower for word in ['consultoría', 'estudio', 'expediente']):
            tipo = 'consultoria'
        if any(word in message_lower for word in ['obra', 'construcción', 'edificación', 'infraestructura']):
            tipo = 'obras'
        
        result = self.get_procedure(monto, tipo)
        return self._format_response(result)
    
    def _format_response(self, result: dict) -> str:
        """Formatea el resultado como respuesta de chat"""
        if 'error' in result:
            return f"❌ Error: {result['error']}"
        
        monto_fmt = f"S/ {result['monto']:,.2f}"
        
        response = f"""📊 **RESULTADO DEL CÁLCULO**

💰 **Monto:** {monto_fmt}
📦 **Tipo:** {result['tipo'].capitalize()}

🏛️ **Procedimiento recomendado:**
**{result['procedimiento']}**

📝 {result['descripcion']}

📚 **Base Legal:** {result['base_legal']}
"""
        
        if 'rango' in result:
            response += f"\n📏 **Rango aplicable:** {result['rango']}"
        
        if 'opciones' in result:
            response += "\n\n🔄 **Opciones disponibles:**\n"
            for opt in result['opciones']:
                response += f"  • {opt}\n"
        
        if 'nota' in result:
            response += f"\n⚠️ **Nota:** {result['nota']}"
        
        return response
    
    def get_all_procedures(self) -> dict:
        """Retorna todos los procedimientos y montos vigentes"""
        return {
            'uit_2026': self.UIT_2026,
            'monto_minimo': self.MONTO_MINIMO,
            'normativa': {
                'ley': 'Ley N° 32069 - Ley General de Contrataciones Públicas',
                'reglamento': 'D.S. N° 009-2025-EF',
                'modificatoria': 'D.S. N° 001-2026-EF',
                'presupuesto': 'Ley N° 32513 - Presupuesto 2026'
            },
            'procedimientos': {
                'bienes': {
                    'Licitación Pública': '≥ S/ 485,000',
                    'Licitación Pública Abreviada': '> S/ 44,000 y < S/ 485,000',
                    'Subasta Inversa Electrónica': '> S/ 44,000 (bienes en listado)',
                    'Comparación de Precios': '> S/ 44,000 y ≤ S/ 100,000'
                },
                'servicios': {
                    'Concurso Público': '≥ S/ 485,000',
                    'Concurso Público Abreviado': '> S/ 44,000 y < S/ 485,000',
                    'Comparación de Precios': '> S/ 44,000 y ≤ S/ 100,000'
                },
                'obras': {
                    'Licitación Pública': '≥ S/ 5,000,000 y < S/ 79,000,000',
                    'Licitación Pública Abreviada': '> S/ 44,000 y < S/ 5,000,000'
                }
            }
        }
    
    # =========================================================================
    # CALCULADORA DE TASAS DE APELACIÓN
    # =========================================================================
    
    # Constantes de apelación (Art. 97 del Reglamento)
    TOPE_RESOLUCION_ENTIDAD = 485000  # < S/ 485,000 resuelve Entidad
    TASA_PORCENTAJE = 0.03  # 3% del valor referencial
    TASA_MINIMA_ENTIDAD = 150  # S/ 150
    TASA_MINIMA_TRIBUNAL = 1100  # S/ 1,100
    
    def calcular_tasa_apelacion(self, valor_referencial: float) -> Dict:
        """
        Calcula la tasa de apelación y determina ante quién se presenta
        
        Args:
            valor_referencial: Valor referencial del proceso
            
        Returns:
            Dict con tasa, instancia y detalles
        """
        # Determinar instancia
        if valor_referencial < self.TOPE_RESOLUCION_ENTIDAD:
            instancia = "Entidad"
            tasa_minima = self.TASA_MINIMA_ENTIDAD
            plazo_resolucion = 12
        else:
            instancia = "Tribunal de Contrataciones del Estado"
            tasa_minima = self.TASA_MINIMA_TRIBUNAL
            plazo_resolucion = 20
        
        # Calcular tasa (3% del VR)
        tasa_calculada = valor_referencial * self.TASA_PORCENTAJE
        
        # Aplicar mínimo
        tasa_aplicable = max(tasa_calculada, tasa_minima)
        
        return {
            "valor_referencial": valor_referencial,
            "tasa_calculada": round(tasa_calculada, 2),
            "tasa_minima": tasa_minima,
            "tasa_aplicable": round(tasa_aplicable, 2),
            "instancia_resuelve": instancia,
            "plazo_resolucion_dias": plazo_resolucion,
            "plazo_interposicion": 8,  # días hábiles
            "efecto": "Suspende el procedimiento de selección",
            "base_legal": "Arts. 97-103 del D.S. N° 009-2025-EF"
        }
    
    def formatear_tasa_apelacion(self, resultado: Dict) -> str:
        """Formatea el resultado de tasa de apelación para chat"""
        return f"""⚖️ **CÁLCULO DE TASA DE APELACIÓN**

📋 **Datos del proceso:**
• Valor Referencial: S/ {resultado['valor_referencial']:,.2f}

💰 **Tasa de apelación:**
• Tasa calculada (3%): S/ {resultado['tasa_calculada']:,.2f}
• Tasa mínima: S/ {resultado['tasa_minima']:,.2f}
• **TASA A PAGAR: S/ {resultado['tasa_aplicable']:,.2f}**

👤 **Instancia que resuelve:**
• **{resultado['instancia_resuelve']}**

⏱️ **Plazos:**
• Plazo para apelar: **{resultado['plazo_interposicion']} días hábiles**
• Plazo para resolver: **{resultado['plazo_resolucion_dias']} días hábiles**

📌 **Efecto:** {resultado['efecto']}

📚 *Base legal: {resultado['base_legal']}*"""

