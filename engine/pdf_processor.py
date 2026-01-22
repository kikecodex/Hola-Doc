"""
Procesador de PDFs para Análisis de Documentos de Contrataciones
Extrae texto estructurado de bases, actas y cuadros de evaluación

Usa PyMuPDF (fitz) para extracción de texto y Gemini para análisis inteligente
"""
import os
import re
import fitz  # PyMuPDF
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json

import google.generativeai as genai
from config import Config


class PDFProcessor:
    """
    Procesador inteligente de PDFs para contrataciones públicas
    Extrae y estructura información de bases, actas y evaluaciones
    """
    
    def __init__(self):
        # Configurar Gemini para análisis
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    # =========================================================================
    # EXTRACCIÓN DE TEXTO
    # =========================================================================
    
    def extraer_texto_pdf(self, pdf_path: str) -> Dict:
        """
        Extrae todo el texto de un PDF
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Dict con texto por página y metadatos
        """
        try:
            doc = fitz.open(pdf_path)
            
            resultado = {
                "archivo": os.path.basename(pdf_path),
                "paginas": doc.page_count,
                "texto_completo": "",
                "texto_por_pagina": [],
                "metadata": doc.metadata
            }
            
            for num_pagina, pagina in enumerate(doc, 1):
                texto = pagina.get_text("text")
                resultado["texto_por_pagina"].append({
                    "pagina": num_pagina,
                    "texto": texto
                })
                resultado["texto_completo"] += texto + "\n\n"
            
            doc.close()
            return resultado
            
        except Exception as e:
            return {"error": str(e)}
    
    def extraer_tablas_pdf(self, pdf_path: str) -> List[Dict]:
        """
        Extrae tablas de un PDF (para cuadros comparativos)
        """
        try:
            doc = fitz.open(pdf_path)
            tablas = []
            
            for num_pagina, pagina in enumerate(doc, 1):
                # Buscar tablas usando análisis de bloques
                bloques = pagina.get_text("dict")["blocks"]
                
                for bloque in bloques:
                    if "lines" in bloque:
                        # Detectar si parece tabla (múltiples columnas alineadas)
                        lineas = bloque["lines"]
                        if len(lineas) > 2:
                            tabla_texto = []
                            for linea in lineas:
                                fila = " | ".join([
                                    span["text"] for span in linea.get("spans", [])
                                ])
                                if fila.strip():
                                    tabla_texto.append(fila)
                            
                            if tabla_texto:
                                tablas.append({
                                    "pagina": num_pagina,
                                    "contenido": tabla_texto
                                })
            
            doc.close()
            return tablas
            
        except Exception as e:
            return [{"error": str(e)}]
    
    # =========================================================================
    # IDENTIFICACIÓN DE TIPO DE DOCUMENTO
    # =========================================================================
    
    def identificar_tipo_documento(self, texto: str) -> Dict:
        """
        Identifica qué tipo de documento es el PDF
        
        Returns:
            Dict con tipo identificado y confianza
        """
        texto_lower = texto.lower()[:5000]  # Primeras 5000 chars
        
        indicadores = {
            "bases": [
                "bases integradas", "bases del procedimiento",
                "licitación pública", "procedimiento abreviado",
                "términos de referencia", "especificaciones técnicas",
                "requisitos de calificación", "factores de evaluación"
            ],
            "acta_buena_pro": [
                "acta de otorgamiento", "buena pro", "orden de prelación",
                "se otorga la buena pro", "puntaje total", "adjudicado"
            ],
            "cuadro_evaluacion": [
                "cuadro comparativo", "evaluación de propuestas",
                "puntaje técnico", "puntaje económico", "propuesta técnica",
                "propuesta económica", "calificación de propuestas"
            ],
            "propuesta": [
                "propuesta técnica", "propuesta económica",
                "declaración jurada", "carta de presentación",
                "experiencia del postor", "promesa de consorcio"
            ],
            "contrato": [
                "contrato de", "contratación de", "cláusula primera",
                "obligaciones de las partes", "plazo de ejecución",
                "garantía de fiel cumplimiento"
            ],
            "resolucion": [
                "resuelve:", "se resuelve:", "resolución de",
                "visto:", "considerando:"
            ]
        }
        
        puntuaciones = {}
        for tipo, palabras in indicadores.items():
            puntuacion = sum(1 for palabra in palabras if palabra in texto_lower)
            puntuaciones[tipo] = puntuacion
        
        tipo_identificado = max(puntuaciones, key=puntuaciones.get)
        confianza = puntuaciones[tipo_identificado] / len(indicadores[tipo_identificado])
        
        return {
            "tipo": tipo_identificado,
            "confianza": round(confianza * 100, 1),
            "puntuaciones": puntuaciones
        }
    
    # =========================================================================
    # EXTRACCIÓN ESTRUCTURADA DE BASES
    # =========================================================================
    
    def extraer_datos_bases(self, texto: str) -> Dict:
        """
        Extrae datos estructurados de las bases de un procedimiento
        """
        datos = {
            "numero_proceso": None,
            "tipo_procedimiento": None,
            "entidad": None,
            "objeto": None,
            "valor_referencial": None,
            "requisitos_calificacion": [],
            "factores_evaluacion": [],
            "plazos": {},
            "garantias": {},
            "penalidades": []
        }
        
        # Patrones de extracción
        patrones = {
            "numero_proceso": [
                r'(?:LP|PA|CD|AS|SIE)\s*N[°º]?\s*([\d\-]+\s*-\s*\d{4})',
                r'(?:LICITACI[ÓO]N|PROCEDIMIENTO)\s+(?:P[ÚU]BLICA|ABREVIADO)\s*N[°º]?\s*([\d\-]+)',
            ],
            "valor_referencial": [
                r'VALOR\s+REFERENCIAL[:\s]+S/?\.?\s*([\d,]+(?:\.\d{2})?)',
                r'S/?\.?\s*([\d,]+(?:\.\d{2})?)\s*(?:SOLES|NUEVOS SOLES)',
            ],
            "plazo_ejecucion": [
                r'PLAZO\s+(?:DE\s+)?EJECUCI[ÓO]N[:\s]+(\d+)\s*(?:D[ÍI]AS)',
            ]
        }
        
        for campo, lista_patrones in patrones.items():
            for patron in lista_patrones:
                match = re.search(patron, texto, re.IGNORECASE)
                if match:
                    valor = match.group(1)
                    if campo == "valor_referencial":
                        valor = float(valor.replace(",", ""))
                    datos[campo] = valor
                    break
        
        # Extraer requisitos de calificación
        datos["requisitos_calificacion"] = self._extraer_requisitos(texto)
        
        # Extraer factores de evaluación
        datos["factores_evaluacion"] = self._extraer_factores(texto)
        
        return datos
    
    def _extraer_requisitos(self, texto: str) -> List[Dict]:
        """Extrae requisitos de calificación"""
        requisitos = []
        
        # Buscar sección de requisitos
        patron_seccion = r'REQUISITOS\s+DE\s+CALIFICACI[ÓO]N(.*?)(?:FACTORES|CAP[ÍI]TULO|$)'
        match = re.search(patron_seccion, texto, re.IGNORECASE | re.DOTALL)
        
        if match:
            seccion = match.group(1)
            
            # Buscar experiencia del postor
            patron_exp = r'EXPERIENCIA\s+DEL\s+POSTOR.*?(?:S/?\.?\s*([\d,]+)|(\d+)\s*(?:contratos|servicios))'
            match_exp = re.search(patron_exp, seccion, re.IGNORECASE | re.DOTALL)
            if match_exp:
                requisitos.append({
                    "tipo": "experiencia_postor",
                    "monto": match_exp.group(1).replace(",", "") if match_exp.group(1) else None,
                    "cantidad": match_exp.group(2) if match_exp.group(2) else None
                })
            
            # Buscar experiencia del personal
            patron_pers = r'PERSONAL\s+(?:CLAVE|T[ÉE]CNICO).*?(\d+)\s*(?:a[ñn]os|meses)'
            match_pers = re.search(patron_pers, seccion, re.IGNORECASE | re.DOTALL)
            if match_pers:
                requisitos.append({
                    "tipo": "experiencia_personal",
                    "tiempo": match_pers.group(1)
                })
        
        return requisitos
    
    def _extraer_factores(self, texto: str) -> List[Dict]:
        """Extrae factores de evaluación"""
        factores = []
        
        # Buscar patrones de factores con puntaje
        patron = r'(?:FACTOR|CRITERIO)\s+(?:DE\s+)?([A-Z\s]+)[:\s]+(?:HASTA\s+)?(\d+)\s*(?:PUNTOS|PTS)'
        matches = re.findall(patron, texto, re.IGNORECASE)
        
        for nombre, puntaje in matches:
            factores.append({
                "nombre": nombre.strip().title(),
                "puntaje_maximo": int(puntaje)
            })
        
        return factores
    
    # =========================================================================
    # EXTRACCIÓN DE CUADRO DE EVALUACIÓN
    # =========================================================================
    
    def extraer_cuadro_evaluacion(self, texto: str) -> Dict:
        """
        Extrae datos del cuadro comparativo de evaluación
        """
        resultado = {
            "propuestas": [],
            "precio_menor": None,
            "ganador": None
        }
        
        # Buscar patrones de postores con precios
        patron_postor = r'(?:POSTOR|EMPRESA|CONSORCIO)[:\s]+([A-Z\s\.]+).*?(?:PRECIO|MONTO)[:\s]+S/?\.?\s*([\d,]+(?:\.\d{2})?)'
        matches = re.findall(patron_postor, texto, re.IGNORECASE | re.DOTALL)
        
        for nombre, precio in matches:
            resultado["propuestas"].append({
                "postor": nombre.strip(),
                "precio": float(precio.replace(",", ""))
            })
        
        if resultado["propuestas"]:
            precios = [p["precio"] for p in resultado["propuestas"]]
            resultado["precio_menor"] = min(precios)
        
        # Buscar ganador
        patron_ganador = r'(?:BUENA\s+PRO|ADJUDICADO|GANADOR)[:\s]+([A-Z\s\.]+)'
        match = re.search(patron_ganador, texto, re.IGNORECASE)
        if match:
            resultado["ganador"] = match.group(1).strip()
        
        return resultado
    
    # =========================================================================
    # ANÁLISIS INTELIGENTE CON GEMINI
    # =========================================================================
    
    async def analizar_documento_gemini(self, texto: str, tipo_analisis: str) -> Dict:
        """
        Usa Gemini para análisis profundo del documento
        
        Args:
            texto: Texto extraído del PDF
            tipo_analisis: 'bases', 'evaluacion', 'vicios', 'apelacion'
        """
        prompts = {
            "bases": """Analiza las siguientes bases de un procedimiento de selección de Perú 
y extrae en formato JSON:
{
  "numero_proceso": "string",
  "entidad": "string",
  "objeto": "string",
  "valor_referencial": number,
  "tipo_procedimiento": "LP|PA|CD|AS",
  "requisitos_calificacion": [
    {"tipo": "string", "descripcion": "string", "monto_o_tiempo": "string"}
  ],
  "factores_evaluacion": [
    {"nombre": "string", "puntaje_maximo": number}
  ],
  "plazo_ejecucion_dias": number,
  "penalidad_diaria_porcentaje": number,
  "garantia_fiel_cumplimiento": number
}

TEXTO DE BASES:
""",
            "evaluacion": """Analiza el siguiente cuadro de evaluación de propuestas y extrae en JSON:
{
  "propuestas": [
    {
      "postor": "string",
      "precio": number,
      "puntaje_tecnico": number,
      "puntaje_economico": number,
      "puntaje_total": number,
      "calificado": boolean
    }
  ],
  "orden_prelacion": ["string"],
  "ganador": "string",
  "precio_menor": number
}

TEXTO:
""",
            "vicios": """Analiza las siguientes bases y detecta posibles vicios legales según 
la Ley 32069 y su Reglamento. Responde en JSON:
{
  "vicios_detectados": [
    {
      "tipo": "string",
      "descripcion": "string",
      "severidad": "ALTA|MEDIA|BAJA",
      "base_legal": "string",
      "recomendacion": "string"
    }
  ],
  "procede_observacion": boolean,
  "resumen": "string"
}

TEXTO:
"""
        }
        
        prompt = prompts.get(tipo_analisis, prompts["bases"]) + texto[:15000]
        
        try:
            response = self.model.generate_content(prompt)
            
            # Extraer JSON de la respuesta
            texto_respuesta = response.text
            
            # Buscar JSON en la respuesta
            match = re.search(r'\{.*\}', texto_respuesta, re.DOTALL)
            if match:
                return json.loads(match.group())
            
            return {"respuesta_texto": texto_respuesta}
            
        except Exception as e:
            return {"error": str(e)}
    
    def analizar_documento_gemini_sync(self, texto: str, tipo_analisis: str) -> Dict:
        """Versión síncrona del análisis con Gemini"""
        prompts = {
            "bases": """Analiza las siguientes bases de un procedimiento de selección peruano.
Extrae la información en formato JSON estructurado:

{
  "numero_proceso": "número del proceso",
  "entidad": "nombre de la entidad",
  "objeto": "objeto de la contratación",
  "valor_referencial": monto numérico,
  "requisitos_calificacion": [
    {"tipo": "experiencia_postor/personal/capacidad", "descripcion": "detalle", "valor": "monto o tiempo"}
  ],
  "factores_evaluacion": [
    {"nombre": "nombre del factor", "puntaje_maximo": número}
  ],
  "posibles_vicios": [
    {"tipo": "experiencia_excesiva/plazo_irreal/etc", "descripcion": "por qué es vicio", "severidad": "ALTA/MEDIA/BAJA"}
  ]
}

TEXTO:
""",
            "vicios": """Eres un experto en contrataciones públicas de Perú (Ley 32069).
Analiza estas bases y detecta TODOS los posibles vicios observables.
Responde en JSON:

{
  "vicios": [
    {
      "tipo": "tipo de vicio",
      "ubicacion": "sección de las bases",
      "descripcion": "descripción del vicio",
      "base_legal": "artículo vulnerado",
      "severidad": "ALTA/MEDIA/BAJA",
      "procede_observacion": true/false
    }
  ],
  "resumen": "resumen ejecutivo",
  "recomendacion": "qué hacer"
}

TEXTO:
"""
        }
        
        prompt = prompts.get(tipo_analisis, prompts["bases"]) + texto[:12000]
        
        try:
            response = self.model.generate_content(prompt)
            texto_respuesta = response.text
            
            # Limpiar y parsear JSON
            texto_limpio = texto_respuesta.replace("```json", "").replace("```", "").strip()
            match = re.search(r'\{.*\}', texto_limpio, re.DOTALL)
            
            if match:
                return json.loads(match.group())
            
            return {"respuesta_texto": texto_respuesta}
            
        except json.JSONDecodeError:
            return {"error": "No se pudo parsear JSON", "respuesta_texto": texto_respuesta}
        except Exception as e:
            return {"error": str(e)}


class DocumentAnalyzer:
    """
    Analizador de documentos que combina extracción y análisis inteligente
    """
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
    
    def analizar_bases_completo(self, pdf_path: str) -> Dict:
        """
        Análisis completo de bases de un procedimiento
        Ahora incluye análisis híbrido automático para detectar vicios
        
        Returns:
            Dict con datos estructurados, vicios detectados, observaciones sugeridas
        """
        # Extraer texto
        extraccion = self.pdf_processor.extraer_texto_pdf(pdf_path)
        
        if "error" in extraccion:
            return extraccion
        
        texto = extraccion["texto_completo"]
        
        # Identificar tipo
        tipo = self.pdf_processor.identificar_tipo_documento(texto)
        
        # Extracción estructurada básica
        datos_basicos = self.pdf_processor.extraer_datos_bases(texto)
        
        # Análisis inteligente con Gemini
        analisis_ia = self.pdf_processor.analizar_documento_gemini_sync(texto, "bases")
        
        # NUEVO: Análisis híbrido para detectar vicios
        from engine.observaciones import ObservacionesGenerator
        obs_gen = ObservacionesGenerator()
        
        valor_referencial = datos_basicos.get("valor_referencial")
        analisis_hibrido = obs_gen.analizar_vicios_hibrido(
            texto, analisis_ia, valor_referencial
        )
        
        return {
            "archivo": extraccion["archivo"],
            "paginas": extraccion["paginas"],
            "tipo_documento": tipo,
            "datos_extraidos": datos_basicos,
            "analisis_ia": analisis_ia,
            "analisis_hibrido": analisis_hibrido,  # Nuevo campo
            "observaciones_sugeridas": analisis_hibrido.get("observaciones_sugeridas", []),
            "procede_observar": analisis_hibrido.get("procede_formular_observaciones", False),
            "texto_muestra": texto[:2000]  # Primeros 2000 chars para referencia
        }
    
    def detectar_vicios_bases(self, pdf_path: str) -> Dict:
        """
        Detecta vicios observables en las bases
        """
        extraccion = self.pdf_processor.extraer_texto_pdf(pdf_path)
        
        if "error" in extraccion:
            return extraccion
        
        texto = extraccion["texto_completo"]
        
        # Análisis de vicios con Gemini
        vicios = self.pdf_processor.analizar_documento_gemini_sync(texto, "vicios")
        
        return {
            "archivo": extraccion["archivo"],
            "vicios_detectados": vicios.get("vicios", []),
            "resumen": vicios.get("resumen", ""),
            "recomendacion": vicios.get("recomendacion", "")
        }
    
    def analizar_evaluacion(self, pdf_path: str) -> Dict:
        """
        Analiza un cuadro de evaluación para verificar cálculos
        """
        extraccion = self.pdf_processor.extraer_texto_pdf(pdf_path)
        
        if "error" in extraccion:
            return extraccion
        
        texto = extraccion["texto_completo"]
        
        # Extracción de datos de evaluación
        datos_eval = self.pdf_processor.extraer_cuadro_evaluacion(texto)
        
        return {
            "archivo": extraccion["archivo"],
            "propuestas": datos_eval["propuestas"],
            "precio_menor": datos_eval["precio_menor"],
            "ganador": datos_eval["ganador"]
        }
    
    def formatear_resultado_analisis(self, resultado: Dict) -> str:
        """Formatea el resultado para chat"""
        
        if "error" in resultado:
            return f"❌ **Error al procesar documento:** {resultado['error']}"
        
        respuesta = f"""📄 **ANÁLISIS DE DOCUMENTO**

**Archivo:** {resultado.get('archivo', 'N/A')}
**Páginas:** {resultado.get('paginas', 'N/A')}
**Tipo identificado:** {resultado.get('tipo_documento', {}).get('tipo', 'N/A')} 
(Confianza: {resultado.get('tipo_documento', {}).get('confianza', 0)}%)

"""
        
        # Agregar datos extraídos
        datos = resultado.get('datos_extraidos', {})
        if datos:
            respuesta += f"""📋 **DATOS EXTRAÍDOS:**
• Proceso: {datos.get('numero_proceso', 'No identificado')}
• Valor Referencial: S/ {datos.get('valor_referencial', 'N/A'):,.2f}

"""
        
        # Agregar análisis IA
        analisis = resultado.get('analisis_ia', {})
        if analisis and "error" not in analisis:
            vicios = analisis.get('posibles_vicios', [])
            if vicios:
                respuesta += "⚠️ **POSIBLES VICIOS DETECTADOS:**\n"
                for v in vicios:
                    respuesta += f"• **{v.get('tipo', 'N/A')}** ({v.get('severidad', 'N/A')}): {v.get('descripcion', '')}\n"
        
        return respuesta


def get_pdf_processor_info() -> str:
    """Información sobre el procesador de PDFs"""
    return """📄 **PROCESADOR DE DOCUMENTOS**

**Tipos de documentos soportados:**
• 📋 Bases de procedimientos
• 📊 Cuadros de evaluación
• 📝 Actas de buena pro
• 📑 Propuestas técnicas/económicas
• 📜 Contratos

**Análisis disponibles:**
1. **Extracción de datos:** VR, requisitos, factores
2. **Detección de vicios:** Requisitos excesivos, plazos irreales
3. **Verificación de evaluación:** Cálculos, orden de prelación

**Cómo usar:**
Sube un PDF y especifica qué análisis deseas:
- "Analiza estas bases y detecta vicios"
- "Verifica si calcularon bien los puntajes"
- "¿Debería observar estas bases?"

📚 *Powered by PyMuPDF + Gemini AI*"""
