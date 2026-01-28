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

from google import genai
from config import Config


class PDFProcessor:
    """
    Procesador inteligente de PDFs para contrataciones públicas
    Extrae y estructura información de bases, actas y evaluaciones
    """
    
    def __init__(self):
        # Configurar Gemini para analisis con nueva API
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.model_name = 'gemini-2.0-flash'
    
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
        MEJORADO: Más indicadores y mejor cálculo de confianza
        
        Returns:
            Dict con tipo identificado y confianza
        """
        texto_lower = texto.lower()[:15000]  # Primeras 15000 chars para mejor detección
        
        # Indicadores ampliados con pesos (más específicos = mayor peso)
        indicadores = {
            "bases": {
                "alto": [  # Peso 3
                    "bases integradas", "bases del procedimiento", "bases estándar",
                    "licitación pública", "procedimiento abreviado", "adjudicación simplificada",
                    "concurso público", "selección de consultores",
                ],
                "medio": [  # Peso 2
                    "términos de referencia", "especificaciones técnicas", "tdr",
                    "requisitos de calificación", "factores de evaluación",
                    "valor referencial", "cronograma del procedimiento",
                    "capítulo i", "capítulo ii", "capítulo iii",
                ],
                "bajo": [  # Peso 1
                    "objeto de la contratación", "sistema de contratación",
                    "modalidad de ejecución", "plazo de ejecución",
                    "forma de pago", "penalidades", "garantías",
                    "osce", "seace", "ley 32069", "reglamento",
                    "postor", "contratista", "entidad",
                ]
            },
            "acta_buena_pro": {
                "alto": [
                    "acta de otorgamiento", "buena pro", "se otorga la buena pro",
                    "acta de adjudicación",
                ],
                "medio": [
                    "orden de prelación", "puntaje total", "adjudicado",
                    "ganador del proceso", "primer lugar",
                ],
                "bajo": [
                    "comité de selección", "resultado final",
                ]
            },
            "cuadro_evaluacion": {
                "alto": [
                    "cuadro comparativo", "cuadro de evaluación",
                    "evaluación de propuestas", "calificación de propuestas",
                ],
                "medio": [
                    "puntaje técnico", "puntaje económico", 
                    "propuesta técnica", "propuesta económica",
                    "evaluación técnica", "evaluación económica",
                ],
                "bajo": [
                    "postor 1", "postor 2", "monto ofertado",
                ]
            },
            "propuesta": {
                "alto": [
                    "propuesta técnica del postor", "propuesta económica del postor",
                    "sobre n° 1", "sobre n° 2", "sobre nº 1", "sobre nº 2",
                ],
                "medio": [
                    "carta de presentación", "declaración jurada",
                    "experiencia del postor", "promesa de consorcio",
                ],
                "bajo": [
                    "anexo", "formato", "cv documentado",
                ]
            },
            "contrato": {
                "alto": [
                    "contrato n°", "contrato de", "contratación de servicio",
                    "cláusula primera", "cláusula segunda",
                ],
                "medio": [
                    "obligaciones de las partes", "obligaciones del contratista",
                    "garantía de fiel cumplimiento", "resolución del contrato",
                ],
                "bajo": [
                    "vigencia del contrato", "conformidad del servicio",
                ]
            },
            "resolucion": {
                "alto": [
                    "resolución de", "resolución n°", "resuelve:",
                    "se resuelve:", "artículo primero",
                ],
                "medio": [
                    "visto:", "considerando:", "que,",
                ],
                "bajo": [
                    "fundamentación", "decisión",
                ]
            }
        }
        
        puntuaciones = {}
        detalles = {}
        
        for tipo, niveles in indicadores.items():
            puntuacion_total = 0
            encontrados = []
            
            # Contar indicadores por nivel con pesos
            for palabra in niveles.get("alto", []):
                if palabra in texto_lower:
                    puntuacion_total += 3
                    encontrados.append(f"[A]{palabra}")
                    
            for palabra in niveles.get("medio", []):
                if palabra in texto_lower:
                    puntuacion_total += 2
                    encontrados.append(f"[M]{palabra}")
                    
            for palabra in niveles.get("bajo", []):
                if palabra in texto_lower:
                    puntuacion_total += 1
                    encontrados.append(f"[B]{palabra}")
            
            puntuaciones[tipo] = puntuacion_total
            detalles[tipo] = encontrados
        
        # Identificar tipo con mayor puntuación
        tipo_identificado = max(puntuaciones, key=puntuaciones.get)
        puntuacion_max = puntuaciones[tipo_identificado]
        
        # Calcular confianza basada en puntuación absoluta
        # Umbral de puntuación para 100% confianza
        umbral_100 = 20  # Con 20+ puntos = 100% confianza
        confianza = min(100, (puntuacion_max / umbral_100) * 100)
        
        # Ajustar mínimo de confianza si hay coincidencias
        if puntuacion_max > 0 and confianza < 40:
            confianza = 40 + (puntuacion_max * 5)  # Mínimo 40% si hay algo
        
        print(f"📊 Tipo detectado: {tipo_identificado} (puntuación: {puntuacion_max}, confianza: {confianza:.1f}%)")
        print(f"   Indicadores encontrados: {detalles[tipo_identificado][:5]}...")  # Solo primeros 5
        
        return {
            "tipo": tipo_identificado,
            "confianza": round(min(confianza, 100), 1),
            "puntuaciones": puntuaciones,
            "indicadores_encontrados": detalles[tipo_identificado]
        }
    
    # =========================================================================
    # EXTRACCIÓN ESTRUCTURADA DE BASES
    # =========================================================================
    
    def extraer_datos_bases(self, texto: str) -> Dict:
        """
        Extrae datos estructurados de las bases de un procedimiento.
        MEJORADO: Múltiples patrones y análisis por secciones.
        """
        datos = {
            "numero_proceso": None,
            "tipo_procedimiento": None,
            "entidad": None,
            "objeto": None,
            "valor_referencial": None,
            "plazo_ejecucion": None,
            "experiencia_postor": None,
            "experiencia_personal": None,
            "penalidad_diaria": None,
            "garantia_fiel_cumplimiento": None,
            "requisitos_calificacion": [],
            "factores_evaluacion": [],
            "plazos": {},
            "garantias": {},
            "penalidades": [],
            "secciones_identificadas": []
        }
        
        # =====================================================================
        # PATRONES MEJORADOS PARA VALOR REFERENCIAL
        # =====================================================================
        patrones_vr = [
            # Formato: "VALOR REFERENCIAL: S/ 1,234,567.89"
            r'VALOR\s+REFERENCIAL[:\s]+S/?\s*\.?\s*([\d,]+(?:\.\d{2})?)',
            # Formato: "V.R.: S/. 1,234,567.89"
            r'V\.?R\.?[:\s]+S/?\s*\.?\s*([\d,]+(?:\.\d{2})?)',
            # Formato con soles al final
            r'VALOR\s+REFERENCIAL[:\s]+([\d,]+(?:\.\d{2})?)\s*(?:SOLES|NUEVOS SOLES)',
            # Formato tabla: "Valor Referencial   S/ 1,234,567.89"
            r'(?:VALOR|Valor)\s+(?:REFERENCIAL|Referencial)\s+S/?\s*\.?\s*([\d,]+(?:\.\d{2})?)',
            # Formato: "El valor referencial es de S/ 1,234,567.89"
            r'valor\s+referencial\s+(?:es\s+(?:de\s+)?)?S/?\s*\.?\s*([\d,]+(?:\.\d{2})?)',
            # Formato corto: "VR S/ 1,234,567.89"
            r'\bVR\b[:\s]+S/?\s*\.?\s*([\d,]+(?:\.\d{2})?)',
            # Formato: "monto referencial S/ 1,234,567.89"
            r'[Mm]onto\s+[Rr]eferencial[:\s]+S/?\s*\.?\s*([\d,]+(?:\.\d{2})?)',
            # Formato: "PRESUPUESTO REFERENCIAL: S/ 1,234,567.89"
            r'PRESUPUESTO\s+REFERENCIAL[:\s]+S/?\s*\.?\s*([\d,]+(?:\.\d{2})?)',
            # Formato con punto de miles y coma decimal (peruano)
            r'VALOR\s+REFERENCIAL[:\s]+S/?\s*\.?\s*([\d.]+,\d{2})',
            # Buscar montos grandes con S/ antes (más de 100,000)
            r'\bS/?\s*\.?\s*(\d{1,3}(?:,\d{3}){2,}(?:\.\d{2})?)\b',
            # Formato: "1,234,567.89 (VALOR REFERENCIAL)"
            r'([\d,]+(?:\.\d{2})?)\s*\(?VALOR\s+REFERENCIAL\)?',
            # Formato: "S/. 1'234,567.89" (con apóstrofe para millones)
            r"S/?\s*\.?\s*(\d{1,3}'\d{3},\d{3}(?:\.\d{2})?)",
            # Formato: buscar en contexto de "presupuesto" o "monto"
            r'(?:presupuesto|monto)\s+(?:total|base)?[:\s]+S/?\s*\.?\s*([\d,]+(?:\.\d{2})?)',
        ]
        
        for patron in patrones_vr:
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                try:
                    valor_str = match.group(1).replace(',', '').replace("'", '').replace('.', '', match.group(1).count('.') - 1)
                    # Si tiene coma como decimal, convertir
                    if ',' in match.group(1) and '.' not in match.group(1):
                        valor_str = match.group(1).replace('.', '').replace(',', '.')
                    valor = float(valor_str.replace(',', ''))
                    if valor > 1000:  # Validar que sea un monto razonable
                        datos["valor_referencial"] = valor
                        print(f"💰 VR encontrado: S/ {valor:,.2f} (patrón: {patron[:40]}...)")
                        break
                except (ValueError, IndexError):
                    continue
        
        # =====================================================================
        # PATRONES PARA NÚMERO DE PROCESO
        # =====================================================================
        patrones_proceso = [
            r'(?:LP|PA|CD|AS|SIE|CP|AMC)\s*N[°º]?\s*([\d\-]+\s*-\s*\d{4})',
            r'(?:LICITACI[ÓO]N|PROCEDIMIENTO)\s+(?:P[ÚU]BLICA|ABREVIADO)\s*N[°º]?\s*([\d\-]+(?:-\d{4})?)',
            r'PROCESO\s*N[°º]?\s*([\d\-]+(?:-\d{4})?)',
            r'(?:ADJUDICACI[ÓO]N)\s+(?:SIMPLIFICADA|DIRECTA)\s*N[°º]?\s*([\d\-]+)',
            r'N[°º]\s*([\d]+\s*-\s*\d{4})\s*-?\s*(?:LP|PA|AS|CD|SIE)',
            r'PROCEDIMIENTO\s+DE\s+SELECCI[ÓO]N\s*N[°º]?\s*([\d\-]+)',
            r'CONCURSO\s+P[ÚU]BLICO\s*N[°º]?\s*([\d\-]+)',
            r'([A-Z]{2,3}-\d+-\d{4}-[A-Z]+)',  # Formato: AS-001-2025-ENTIDAD
        ]
        
        for patron in patrones_proceso:
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                datos["numero_proceso"] = match.group(0) if match.group(0) else match.group(1)
                break
        
        # =====================================================================
        # PATRONES PARA PLAZO DE EJECUCIÓN
        # =====================================================================
        patrones_plazo = [
            r'PLAZO\s+(?:DE\s+)?EJECUCI[ÓO]N[:\s]+(\d+)\s*(?:D[ÍI]AS)',
            r'PLAZO\s+(?:DE\s+)?(?:ENTREGA|PRESTACI[ÓO]N)[:\s]+(\d+)\s*(?:D[ÍI]AS)',
            r'(?:PLAZO|Plazo)[:\s]+(\d+)\s*(?:d[íi]as\s+)?(?:calendario|h[áa]biles)',
            r'(?:plazo|PLAZO)\s+(?:m[áa]ximo|total)[:\s]+(\d+)\s*(?:d[íi]as)',
            r'duraci[óo]n[:\s]+(\d+)\s*(?:d[íi]as)',
            r'(?:en\s+un\s+plazo\s+de|dentro\s+de)\s+(\d+)\s*(?:d[íi]as)',
        ]
        
        for patron in patrones_plazo:
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                try:
                    datos["plazo_ejecucion"] = int(match.group(1))
                    datos["plazos"]["ejecucion"] = int(match.group(1))
                    break
                except:
                    pass
        
        # =====================================================================
        # PATRONES PARA EXPERIENCIA DEL POSTOR
        # =====================================================================
        patrones_exp = [
            r'[Ee]xperiencia\s+(?:del\s+)?[Pp]ostor[:\s]+(?:S/?\s*\.?\s*)?([\d,]+(?:\.\d{2})?)',
            r'[Ee]xperiencia\s+m[íi]nima[:\s]+(?:S/?\s*\.?\s*)?([\d,]+(?:\.\d{2})?)',
            r'[Mm]onto\s+(?:facturado|acumulado)\s+(?:m[íi]nimo)?[:\s]+(?:S/?\s*\.?\s*)?([\d,]+(?:\.\d{2})?)',
            r'acreditar\s+experiencia[^.]*(?:S/?\s*\.?\s*)([\d,]+(?:\.\d{2})?)',
            r'(?:hasta|por)\s+(?:un\s+)?(?:monto|valor)\s+acumulado[^.]*(?:S/?\s*\.?\s*)([\d,]+(?:\.\d{2})?)',
        ]
        
        for patron in patrones_exp:
            match = re.search(patron, texto, re.IGNORECASE | re.DOTALL)
            if match:
                try:
                    exp_valor = float(match.group(1).replace(',', ''))
                    if exp_valor > 1000:  # Validar monto razonable
                        datos["experiencia_postor"] = exp_valor
                        break
                except:
                    pass
        
        # =====================================================================
        # PATRONES PARA PENALIDAD
        # =====================================================================
        patrones_pen = [
            r'[Pp]enalidad\s+(?:diaria|por\s+mora)?[:\s]+([\d.]+)\s*%',
            r'([\d.]+)\s*%\s*(?:diario|por\s+d[íi]a)\s*(?:de\s+)?(?:penalidad|mora)',
            r'penalidad[^.]*([\d.]+)\s*%\s*(?:del\s+monto)',
            r'multa\s+(?:diaria)?[:\s]+([\d.]+)\s*%',
        ]
        
        for patron in patrones_pen:
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                try:
                    datos["penalidad_diaria"] = float(match.group(1))
                    break
                except:
                    pass
        
        # =====================================================================
        # IDENTIFICAR Y ANALIZAR SECCIONES CLAVE
        # =====================================================================
        secciones_clave = [
            ("terminos_referencia", [r'T[ÉE]RMINOS\s+DE\s+REFERENCIA', r'TDR', r'TÉRMINOS DE REFERENCIA']),
            ("especificaciones_tecnicas", [r'ESPECIFICACIONES\s+T[ÉE]CNICAS', r'EETT', r'E\.E\.T\.T']),
            ("requisitos_calificacion", [r'REQUISITOS\s+DE\s+CALIFICACI[ÓO]N', r'CAP[ÍI]TULO\s+III']),
            ("factores_evaluacion", [r'FACTORES\s+DE\s+EVALUACI[ÓO]N', r'CAP[ÍI]TULO\s+IV']),
            ("penalidades", [r'PENALIDADES', r'CAP[ÍI]TULO.*PENALIDADES']),
            ("garantias", [r'GARANT[ÍI]AS', r'GARANT[ÍI]A\s+DE\s+FIEL']),
        ]
        
        for seccion, patrones in secciones_clave:
            for patron in patrones:
                if re.search(patron, texto, re.IGNORECASE):
                    datos["secciones_identificadas"].append(seccion)
                    break
        
        print(f"📋 Secciones identificadas: {datos['secciones_identificadas']}")
        
        # Extraer requisitos de calificación
        datos["requisitos_calificacion"] = self._extraer_requisitos(texto)
        
        # Extraer factores de evaluación
        datos["factores_evaluacion"] = self._extraer_factores(texto)
        
        # Extraer entidad
        datos["entidad"] = self._extraer_entidad(texto)
        
        # =====================================================================
        # NUEVO: Extraer datos cuantificables para validación de vicios
        # =====================================================================
        datos["datos_cuantificables"] = self._extraer_datos_cuantificables(texto)
        
        return datos
    
    def _extraer_datos_cuantificables(self, texto: str) -> Dict:
        """
        NUEVA FUNCIÓN: Extrae VR, experiencias, penalidades, plazos con patrones robustos.
        Estos datos son críticos para validar vicios automáticamente.
        
        Returns:
            Dict con datos numéricos extraídos y validados
        """
        datos = {
            "valor_referencial": None,
            "experiencia_postor": None,
            "experiencia_personal": [],
            "penalidad_diaria": None,
            "plazo_ejecucion": None,
            "garantia_porcentaje": None,
            "ratio_experiencia_vr": None,
            "excede_limite_experiencia": False
        }
        
        texto_lower = texto.lower()
        
        # =====================================================================
        # 1. VALOR REFERENCIAL - Múltiples formatos
        # =====================================================================
        patrones_vr = [
            r'valor\s+referencial[:\s]+s/?\\.?\s*([\d,]+(?:\.\d{2})?)',
            r'v\.?\s*r\.?[:\s]+s/?\\.?\s*([\d,]+(?:\.\d{2})?)',
            r'presupuesto\s+(?:base|referencial)[:\s]+s/?\\.?\s*([\d,]+(?:\.\d{2})?)',
            r'monto\s+referencial[:\s]+s/?\\.?\s*([\d,]+(?:\.\d{2})?)',
            r'valor\s+estimado[:\s]+s/?\\.?\s*([\d,]+(?:\.\d{2})?)',
            r's/\\.?\s*([\d,]+(?:\.\d{2})?)\s+(?:\(|soles).*valor\s+referencial',
            # Patrones con formato diferente
            r'referencial[:\s]+(?:s/?\\.?\s*)?([\d]{1,3}(?:,\d{3})+(?:\.\d{2})?)',
        ]
        
        for patron in patrones_vr:
            match = re.search(patron, texto_lower)
            if match:
                try:
                    monto_str = match.group(1).replace(',', '').replace(' ', '')
                    monto = float(monto_str)
                    if monto > 1000:  # VR debe ser > 1000 soles para ser válido
                        datos["valor_referencial"] = monto
                        print(f"💰 VR detectado: S/ {monto:,.2f}")
                        break
                except (ValueError, AttributeError):
                    continue
        
        # =====================================================================
        # 2. EXPERIENCIA DEL POSTOR - Múltiples formatos
        # =====================================================================
        patrones_exp_postor = [
            r'experiencia\s+(?:del\s+)?postor[:\s]+(?:s/?\\.?\s*)?([\d,]+(?:\.\d{2})?)',
            r'experiencia\s+m[íi]nima[:\s]+(?:s/?\\.?\s*)?([\d,]+(?:\.\d{2})?)',
            r'monto\s+(?:facturado|acumulado)[^.]*(?:s/?\\.?\s*)?([\d,]+(?:\.\d{2})?)',
            r'acreditaci[óo]n\s+de\s+experiencia[^.]*(?:s/?\\.?\s*)?([\d,]+(?:\.\d{2})?)',
            r'contratos\s+(?:equivalentes|por\s+un\s+monto)[^.]*(?:s/?\\.?\s*)?([\d,]+(?:\.\d{2})?)',
            r'experiencia[^.]*(?:igual\s+o\s+mayor\s+a|no\s+menor\s+a)[^.]*(?:s/?\\.?\s*)?([\d,]+(?:\.\d{2})?)',
            r'(?:una|1)\s+(?:\(1\)\s+)?vez\s+el\s+valor\s+referencial',  # Caso especial: 1x VR
            r'(?:dos|2)\s+(?:\(2\)\s+)?veces?\s+el\s+valor\s+referencial',  # 2x VR
        ]
        
        for patron in patrones_exp_postor:
            match = re.search(patron, texto_lower)
            if match:
                try:
                    # Caso especial: "1 vez el VR" o "2 veces el VR"
                    if 'vez' in patron:
                        if datos["valor_referencial"]:
                            multiplicador = 2 if 'dos' in match.group(0) or '2' in match.group(0) else 1
                            datos["experiencia_postor"] = datos["valor_referencial"] * multiplicador
                            print(f"📊 Experiencia postor (calculada): S/ {datos['experiencia_postor']:,.2f} ({multiplicador}x VR)")
                    else:
                        monto_str = match.group(1).replace(',', '').replace(' ', '')
                        monto = float(monto_str)
                        if monto > 10000:  # Debe ser monto significativo
                            datos["experiencia_postor"] = monto
                            print(f"📊 Experiencia postor: S/ {monto:,.2f}")
                    break
                except (ValueError, AttributeError, IndexError):
                    continue
        
        # =====================================================================
        # 3. CALCULAR RATIO EXPERIENCIA/VR (CRÍTICO PARA VICIOS)
        # =====================================================================
        if datos["valor_referencial"] and datos["experiencia_postor"]:
            ratio = datos["experiencia_postor"] / datos["valor_referencial"]
            datos["ratio_experiencia_vr"] = round(ratio, 2)
            datos["excede_limite_experiencia"] = ratio > 1.0
            
            if ratio > 1.0:
                print(f"⚠️ VICIO DETECTADO: Experiencia ({ratio:.2f}x) EXCEDE el VR")
            else:
                print(f"✅ Ratio experiencia/VR: {ratio:.2f}x (dentro del límite)")
        
        # =====================================================================
        # 4. EXPERIENCIA DEL PERSONAL CLAVE
        # =====================================================================
        patrones_personal = [
            r'(?:profesional|personal|residente|especialista)[^.]{0,50}([\d]+)\s*a[ñn]os?\s+(?:de\s+)?experiencia',
            r'experiencia[^.]{0,30}([\d]+)\s*a[ñn]os?[^.]*(?:profesional|titulado|colegiado)',
            r'(?:m[íi]nimo\s+)?([\d]+)\s*a[ñn]os?\s+(?:de\s+)?experiencia[^.]*(?:profesional|espec[íi]fica)',
            r'haber\s+(?:ejercido|trabajado)[^.]{0,30}([\d]+)\s*a[ñn]os?',
        ]
        
        for patron in patrones_personal:
            matches = re.findall(patron, texto_lower)
            for match in matches:
                try:
                    anios = int(match)
                    if 1 <= anios <= 30:  # Rango válido
                        datos["experiencia_personal"].append(anios)
                except ValueError:
                    continue
        
        if datos["experiencia_personal"]:
            max_anios = max(datos["experiencia_personal"])
            print(f"👤 Experiencia personal máxima: {max_anios} años")
            if max_anios > 10:
                print(f"⚠️ POSIBLE VICIO: Experiencia personal > 10 años")
        
        # =====================================================================
        # 5. PENALIDAD DIARIA
        # =====================================================================
        patrones_penalidad = [
            r'penalidad[^.]*?([\d]+(?:[.,]\d+)?)\s*%',
            r'([\d]+(?:[.,]\d+)?)\s*%[^.]*penalidad\s+diaria',
            r'penalidad\s+por\s+mora[^.]*?([\d]+(?:[.,]\d+)?)\s*%',
        ]
        
        for patron in patrones_penalidad:
            match = re.search(patron, texto_lower)
            if match:
                try:
                    penalidad = float(match.group(1).replace(',', '.'))
                    if penalidad < 10:  # Penalidad razonable < 10%
                        datos["penalidad_diaria"] = penalidad
                        print(f"📉 Penalidad diaria: {penalidad}%")
                        if penalidad > 0.10:
                            print(f"⚠️ POSIBLE VICIO: Penalidad > 0.10%")
                        break
                except ValueError:
                    continue
        
        # =====================================================================
        # 6. PLAZO DE EJECUCIÓN
        # =====================================================================
        patrones_plazo = [
            r'plazo\s+(?:de\s+)?ejecuci[óo]n[:\s]+([\d]+)\s*d[íi]as?',
            r'plazo[:\s]+([\d]+)\s*d[íi]as?\s*(?:calendario|h[áa]biles)?',
            r'duraci[óo]n[:\s]+([\d]+)\s*d[íi]as?',
            r'(?:en\s+un\s+plazo\s+de|en|dentro\s+de)[:\s]+([\d]+)\s*d[íi]as?',
            r'([\d]+)\s*d[íi]as?\s*(?:calendario|h[áa]biles)?[^.]*plazo',
        ]
        
        for patron in patrones_plazo:
            match = re.search(patron, texto_lower)
            if match:
                try:
                    plazo = int(match.group(1))
                    if 1 <= plazo <= 1000:  # Rango válido
                        datos["plazo_ejecucion"] = plazo
                        print(f"📅 Plazo de ejecución: {plazo} días")
                        if plazo < 15:
                            print(f"⚠️ POSIBLE VICIO: Plazo muy corto ({plazo} días)")
                        break
                except ValueError:
                    continue
        
        # =====================================================================
        # 7. GARANTÍA
        # =====================================================================
        patrones_garantia = [
            r'garant[íi]a\s+(?:de\s+)?fiel\s+cumplimiento[^.]*?([\d]+)\s*%',
            r'([\d]+)\s*%[^.]*garant[íi]a\s+(?:de\s+)?fiel',
        ]
        
        for patron in patrones_garantia:
            match = re.search(patron, texto_lower)
            if match:
                try:
                    garantia = int(match.group(1))
                    if 1 <= garantia <= 100:
                        datos["garantia_porcentaje"] = garantia
                        print(f"🔒 Garantía: {garantia}%")
                        if garantia > 10:
                            print(f"⚠️ VICIO DETECTADO: Garantía > 10%")
                        break
                except ValueError:
                    continue
        
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
            response = self.client.models.generate_content(model=self.model_name, contents=prompt)
            
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
        """
        Versión síncrona del análisis con Gemini.
        Actúa como un abogado experto en contrataciones públicas.
        Incluye manejo robusto de errores y fallback con análisis basado en reglas.
        """
        prompts = {
            "bases": """Eres un ABOGADO LITIGANTE con 20 años de experiencia GANANDO CASOS ante el OECE y Tribunal de Contrataciones del Perú.

TU MISIÓN: Encontrar TODOS los vicios para que tu cliente GANE la observación a las bases.

⚠️ REGLA DE ORO: Si la experiencia del postor es >= al valor referencial, ES UN VICIO AUTOMÁTICO (Art. 45).

PASO 1 - EXTRAE PRIMERO ESTOS DATOS (OBLIGATORIO):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. VALOR REFERENCIAL (VR): Busca "Valor Referencial", "V.R.", "Presupuesto Base" → S/ ____
2. EXPERIENCIA DEL POSTOR: Busca "Experiencia mínima", "Monto facturado" → S/ ____
3. RATIO = EXPERIENCIA / VR = ____ (Si > 1.0 = VICIO CONFIRMADO ALTA SEVERIDAD)
4. PLAZO DE EJECUCIÓN: Busca "Plazo de ejecución", "Duración" → ____ días
5. EXPERIENCIA PERSONAL: Busca "años de experiencia" del personal → ____ años

PASO 2 - CHECKLIST OBLIGATORIO (marca SÍ/NO mentalmente):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ ¿Experiencia del postor >= VR? → VICIO ALTA (Art. 45)
□ ¿Experiencia personal > 10 años? → VICIO ALTA  
□ ¿Experiencia personal > 5 años? → VICIO MEDIA
□ ¿Hay marcas sin "o equivalente"? → VICIO ALTA (Art. 16)
□ ¿Plazo < 15 días? → VICIO ALTA
□ ¿Plazo < 30 días para obra/servicio complejo? → VICIO MEDIA
□ ¿Penalidad > 0.10%? → VICIO ALTA (Art. 163)
□ ¿Garantía > 10%? → VICIO ALTA (Art. 33)
□ ¿Se exigen certificaciones ISO obligatorias? → VICIO MEDIA
□ ¿Se prohíbe consorcio sin justificación? → VICIO ALTA (Art. 13)
□ ¿Hay restricciones geográficas? → VICIO ALTA

PASO 3 - RESPUESTA EN JSON (estricto, sin texto adicional):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{
  "numero_proceso": "string",
  "entidad": "string", 
  "objeto": "string",
  "valor_referencial": number,
  "experiencia_postor": number,
  "ratio_experiencia_vr": number,
  "plazo_ejecucion": number,
  "experiencia_personal_anios": number,
  "tipo_procedimiento": "LP/PA/CD/AS",
  "posibles_vicios": [
    {
      "tipo": "experiencia_excesiva/direccionamiento/plazo_irreal/penalidad_excesiva/garantia_excesiva/requisito_innecesario/factor_subjetivo/otro",
      "descripcion": "descripción detallada",
      "ubicacion": "sección de las bases",
      "base_legal": "Art. XX de Ley 32069 / Reglamento",
      "severidad": "ALTA/MEDIA/BAJA",
      "fundamento": "argumentación legal"
    }
  ],
  "requisitos_calificacion": [],
  "factores_evaluacion": [],
  "resumen_ejecutivo": "string",
  "recomendacion": "string"
}

⚠️ IMPORTANTE: 
- En Perú, TODAS las bases tienen vicios. Encuentra MÍNIMO 5.
- Si el ratio experiencia/VR > 1.0, SIEMPRE es un vicio ALTA.
- Sé AGRESIVO buscando vicios, como un abogado que quiere ganar.

TEXTO DE LAS BASES:
""",
            "vicios": """Eres un ABOGADO LITIGANTE EXPERTO EN IMPUGNACIONES DE CONTRATACIONES PÚBLICAS.
Tu cliente quiere OBSERVAR estas bases. Tu trabajo es encontrar TODOS los vicios posibles.

BUSCA ESPECÍFICAMENTE:
- Experiencia del postor superior al VR (Art. 45 Reglamento - máximo 1 vez el VR)
- Experiencia del personal clave excesiva (más de lo técnicamente necesario)
- Mención de marcas sin "o equivalente" (Art. 16 Ley 32069)
- Especificaciones técnicas direccionadas
- Requisitos que limitan la libre competencia (Art. 2 Ley 32069)
- Penalidades que exceden la fórmula del Art. 163 Reglamento
- Plazos de ejecución irreales
- Factores de evaluación subjetivos (deben ser objetivos según Art. 28)
- Restricciones arbitrarias de participación
- Documentación innecesaria para calificación

Responde ÚNICAMENTE con un JSON válido (sin texto adicional):
{
  "vicios_detectados": [
    {
      "tipo": "tipo de vicio",
      "descripcion": "descripción detallada",
      "ubicacion": "numeral de las bases",
      "base_legal": "Art. XX de Ley 32069 / Art. XX Reglamento",
      "severidad": "ALTA/MEDIA/BAJA",
      "probabilidad_acogimiento": 0.0 a 1.0,
      "fundamento_juridico": "argumentación legal completa"
    }
  ],
  "total_vicios": number,
  "procede_observacion": true/false,
  "resumen": "string"
}

TEXTO:
"""
        }
        
        # Usamos más texto para tener mejor contexto (hasta 25000 caracteres)
        prompt = prompts.get(tipo_analisis, prompts["bases"]) + texto[:25000]
        texto_limpio = ""
        
        try:
            print(f"🤖 Enviando a Gemini API... ({len(texto)} caracteres de texto)")
            response = self.client.models.generate_content(model=self.model_name, contents=prompt)
            
            # Verificar si hay respuesta válida
            if not response or not hasattr(response, 'text'):
                print(f"⚠️ Respuesta de Gemini vacía o inválida")
                return self._generar_analisis_fallback(texto, "Respuesta vacía de la API")
            
            texto_respuesta = response.text
            print(f"📝 Respuesta Gemini recibida: {len(texto_respuesta)} caracteres")
            
            # Verificar si la respuesta está vacía
            if not texto_respuesta or len(texto_respuesta.strip()) < 10:
                print(f"⚠️ Respuesta de Gemini muy corta o vacía")
                return self._generar_analisis_fallback(texto, "Respuesta muy corta")
            
            # Limpiar y parsear JSON
            texto_limpio = texto_respuesta.replace("```json", "").replace("```", "").strip()
            match = re.search(r'\{.*\}', texto_limpio, re.DOTALL)
            
            if match:
                resultado = json.loads(match.group())
                print(f"✅ JSON parseado correctamente: {list(resultado.keys())}")
                
                # Verificar que tenga vicios detectados
                vicios = resultado.get('posibles_vicios', resultado.get('vicios_detectados', []))
                if not vicios:
                    print(f"⚠️ Gemini no detectó vicios, complementando con análisis de reglas...")
                    vicios_reglas = self._detectar_vicios_por_reglas(texto)
                    if vicios_reglas:
                        resultado['posibles_vicios'] = vicios_reglas
                        print(f"✅ Añadidos {len(vicios_reglas)} vicios detectados por reglas")
                
                return resultado
            
            print(f"⚠️ No se encontró JSON en la respuesta: {texto_limpio[:200]}...")
            return self._generar_analisis_fallback(texto, "JSON no encontrado en respuesta")
            
        except json.JSONDecodeError as e:
            print(f"❌ Error de JSON: {str(e)}")
            print(f"   Texto recibido: {texto_limpio[:200] if texto_limpio else 'N/A'}...")
            return self._generar_analisis_fallback(texto, f"Error parseando JSON: {str(e)}")
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            print(f"❌ Error de Gemini API: {error_type}: {error_msg}")
            
            # Detectar errores comunes de la API de Gemini
            if "blocked" in error_msg.lower() or "safety" in error_msg.lower():
                print(f"   🛡️ Contenido bloqueado por filtros de seguridad")
            elif "quota" in error_msg.lower() or "rate" in error_msg.lower():
                print(f"   ⏱️ Límite de tasa excedido")
            elif "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                print(f"   🔑 Error de autenticación con API Key")
            
            return self._generar_analisis_fallback(texto, f"{error_type}: {error_msg}")
    
    def _generar_analisis_fallback(self, texto: str, motivo_error: str) -> Dict:
        """
        Genera un análisis de fallback basado en reglas cuando Gemini falla.
        Esto asegura que siempre se detecten vicios potenciales.
        """
        print(f"🔄 Generando análisis de fallback (motivo: {motivo_error})")
        
        vicios = self._detectar_vicios_por_reglas(texto)
        
        return {
            "analisis_fallback": True,
            "motivo_fallback": motivo_error,
            "numero_proceso": self._extraer_numero_proceso(texto),
            "entidad": self._extraer_entidad(texto),
            "objeto": "[Extraído por análisis de reglas]",
            "valor_referencial": None,
            "tipo_procedimiento": self._extraer_tipo_procedimiento(texto),
            "posibles_vicios": vicios,
            "requisitos_calificacion": [],
            "factores_evaluacion": [],
            "resumen_ejecutivo": f"Análisis realizado con motor de reglas (Gemini no disponible: {motivo_error}). Se detectaron {len(vicios)} posibles vicios.",
            "recomendacion": "Revisar los vicios detectados y complementar con análisis manual detallado."
        }
    
    def _detectar_vicios_por_reglas(self, texto: str, texto_por_pagina: List[Dict] = None) -> List[Dict]:
        """
        Detecta vicios usando patrones de texto y reglas legales.
        VERSIÓN MEJORADA: 
        - Análisis exhaustivo de múltiples tipos de vicios
        - Incluye número de página donde se encontró el vicio
        - Identifica capítulo/sección de las bases
        
        Args:
            texto: Texto completo del documento
            texto_por_pagina: Lista de dicts con {"pagina": int, "texto": str}
                              Si se provee, se busca en qué página está cada vicio
        """
        vicios = []
        texto_lower = texto.lower()
        
        # Función auxiliar para encontrar página y capítulo
        def encontrar_ubicacion(patron):
            """Busca en qué página y sección está el match"""
            resultado = {"pagina": None, "capitulo": None, "cita_textual": None}
            
            if texto_por_pagina:
                for pagina_data in texto_por_pagina:
                    num_pagina = pagina_data["pagina"]
                    texto_pagina = pagina_data["texto"].lower()
                    match = re.search(patron, texto_pagina, re.IGNORECASE)
                    if match:
                        resultado["pagina"] = num_pagina
                        # Extraer cita textual (contexto alrededor del match)
                        start = max(0, match.start() - 50)
                        end = min(len(texto_pagina), match.end() + 100)
                        resultado["cita_textual"] = texto_pagina[start:end].strip()
                        
                        # Identificar capítulo
                        capitulo = identificar_capitulo(texto_pagina[:match.start()])
                        if capitulo:
                            resultado["capitulo"] = capitulo
                        break
            
            return resultado
        
        def identificar_capitulo(texto_previo):
            """Identifica el último capítulo/sección mencionado antes de un texto"""
            patrones = [
                r'(capítulo\s+[ivxlcd]+[^\n]*)',
                r'(cap[íi]tulo\s+\d+[^\n]*)',
                r'(secci[óo]n\s+[ivxlcd]+[^\n]*)',
                r'(\d+\.\d+\.?\s*[A-ZÁÉÍÓÚ][^\n]+)',  # 3.1 REQUISITOS...
                r'([IVXLCD]+\.\s*[A-ZÁÉÍÓÚ][^\n]+)',  # III. FACTORES...
            ]
            
            for patron in patrones:
                matches = re.findall(patron, texto_previo, re.IGNORECASE)
                if matches:
                    return matches[-1].strip()[:100]  # Último match, max 100 chars
            return None
        
        # =====================================================================
        # 1. DETECTAR DIRECCIONAMIENTO POR MARCAS
        # =====================================================================
        patrones_marca = [
            r'marca\s*[:\s]\s*([A-Za-z0-9]+)',
            r'modelo\s*[:\s]\s*([A-Za-z0-9\-]+)',
            r'fabricante\s*[:\s]\s*([A-Za-z]+)',
            r'tipo\s*[:\s]\s*([A-Za-z]+\s+[A-Za-z]+)',
        ]
        
        marcas_detectadas = []
        for patron in patrones_marca:
            matches = re.findall(patron, texto, re.IGNORECASE)
            marcas_detectadas.extend(matches)
        
        # Verificar si hay marcas sin "o equivalente" cerca
        if marcas_detectadas:
            # Buscar contextos donde no aparece "equivalente"
            contextos_sin_equiv = 0
            for marca in marcas_detectadas[:5]:  # Solo revisar las primeras 5
                patron_contexto = rf'{re.escape(marca)}[^.]*'
                match = re.search(patron_contexto, texto, re.IGNORECASE)
                if match and 'equivalente' not in match.group(0).lower():
                    contextos_sin_equiv += 1
            
            if contextos_sin_equiv > 0:
                # Buscar ubicación del primer match
                ubicacion_info = encontrar_ubicacion(patrones_marca[0])
                vicio = {
                    "tipo": "direccionamiento",
                    "descripcion": f"Se detectaron {len(marcas_detectadas)} referencias a marcas/modelos específicos sin 'o equivalente'",
                    "ubicacion": "Especificaciones técnicas / TDR",
                    "base_legal": "Art. 16 de la Ley 32069 - Prohibición de referencia a marcas",
                    "severidad": "ALTA",
                    "fundamento": "La mención de marca específica sin permitir equivalentes direcciona la contratación hacia un proveedor específico"
                }
                # Agregar ubicación por página si se encontró
                if ubicacion_info["pagina"]:
                    vicio["pagina"] = ubicacion_info["pagina"]
                    vicio["ubicacion"] = f"Página {ubicacion_info['pagina']} - Especificaciones técnicas / TDR"
                if ubicacion_info["capitulo"]:
                    vicio["capitulo"] = ubicacion_info["capitulo"]
                if ubicacion_info["cita_textual"]:
                    vicio["cita_textual"] = ubicacion_info["cita_textual"]
                vicios.append(vicio)
        
        # =====================================================================
        # 2. DETECTAR EXPERIENCIA EXCESIVA DEL POSTOR
        # =====================================================================
        patrones_exp_postor = [
            r'experiencia\s+(?:del\s+)?postor[:\s]+(?:s/?\.?\s*)?(\d[\d,\.]+)',
            r'experiencia\s+m[íi]nima[:\s]+(?:s/?\.?\s*)?(\d[\d,\.]+)',
            r'monto\s+(?:facturado|acumulado)[^.]*(?:s/?\.?\s*)?(\d[\d,\.]+)',
            r'(\d[\d,\.]+)\s*(?:soles|s/\.?)\s*(?:de\s+)?experiencia',
        ]
        
        for patron in patrones_exp_postor:
            match = re.search(patron, texto_lower)
            if match:
                try:
                    monto_str = match.group(1).replace(',', '').replace('.', '', match.group(1).count('.') - 1)
                    monto = float(monto_str)
                    if monto > 50000:  # Monto significativo
                        vicios.append({
                            "tipo": "experiencia_excesiva",
                            "descripcion": f"Experiencia mínima requerida: S/ {monto:,.2f} - Verificar si excede el valor referencial",
                            "ubicacion": "Requisitos de calificación - Experiencia del postor",
                            "base_legal": "Art. 45 del Reglamento D.S. 009-2025-EF",
                            "severidad": "ALTA",
                            "fundamento": "La experiencia del postor no debe exceder 1 vez el valor referencial (Art. 45). Verificar proporcionalidad."
                        })
                        break
                except:
                    pass
        
        # =====================================================================
        # 3. DETECTAR EXPERIENCIA EXCESIVA DEL PERSONAL
        # =====================================================================
        patrones_exp_personal = [
            r'experiencia\s+(?:del\s+)?(?:profesional|personal|residente|especialista)[^.]*(\d+)\s*a[ñn]os',
            r'profesional[^.]*(?:m[íi]nimo\s+)?(\d+)\s*a[ñn]os',
            r'(?:ingeniero|arquitecto|abogado|contador)[^.]*(\d+)\s*a[ñn]os\s*(?:de\s+)?experiencia',
            r'experiencia[^.]*(\d+)\s*a[ñn]os[^.]*(?:profesional|titulado)',
        ]
        
        for patron in patrones_exp_personal:
            match = re.search(patron, texto_lower)
            if match:
                try:
                    anios = int(match.group(1))
                    if anios > 5:  # Más de 5 años puede ser excesivo
                        vicios.append({
                            "tipo": "experiencia_personal_excesiva",
                            "descripcion": f"Se requiere {anios} años de experiencia para personal clave - Posible requisito excesivo",
                            "ubicacion": "Requisitos de calificación - Personal",
                            "base_legal": "Art. 16 y 29 del Reglamento D.S. 009-2025-EF",
                            "severidad": "ALTA" if anios > 10 else "MEDIA",
                            "fundamento": "Exigir experiencia excesiva del personal limita la participación de postores calificados"
                        })
                        break
                except:
                    pass
        
        # =====================================================================
        # 4. DETECTAR PROFESIONES ESPECÍFICAS RESTRICTIVAS
        # =====================================================================
        profesiones_especificas = [
            (r'(?:colegiatura|colegiado)\s+(?:activo|vigente|hábil)', "colegiatura activa"),
            (r'(?:maestr[íi]a|doctorado)\s+(?:en|de)', "grado académico avanzado"),
            (r'(?:diplomado|especialización)\s+(?:en|de)', "diplomado/especialización"),
            (r'(?:certificación|certificado)\s+(?:de|en|como)\s+(?!calidad)', "certificación profesional específica"),
        ]
        
        for patron, descripcion in profesiones_especificas:
            if re.search(patron, texto_lower):
                vicios.append({
                    "tipo": "requisito_profesional_restrictivo",
                    "descripcion": f"Se exige {descripcion} que puede limitar la competencia",
                    "ubicacion": "Requisitos de calificación - Personal",
                    "base_legal": "Art. 2 numeral 8 de la Ley 32069 (Libertad de Concurrencia)",
                    "severidad": "MEDIA",
                    "fundamento": "Los requisitos profesionales deben ser proporcionales al objeto de la contratación"
                })
                break
        
        # =====================================================================
        # 5. DETECTAR RESTRICCIONES A CONSORCIOS
        # =====================================================================
        patrones_consorcio = [
            r'no\s+(?:se\s+)?permite[n]?\s+consorcio',
            r'prohibi(?:do|da|ción)[^.]*consorcio',
            r'consorcio[^.]*(?:no|prohib)',
            r'(?:únicamente|solo)\s+(?:personas?\s+)?(?:natural|jurídica)',
            r'presentarse\s+(?:de\s+)?manera\s+(?:individual|independiente)',
        ]
        
        for patron in patrones_consorcio:
            if re.search(patron, texto_lower):
                vicios.append({
                    "tipo": "restriccion_consorcio",
                    "descripcion": "Las bases restringen o prohíben la participación en consorcio",
                    "ubicacion": "Condiciones generales de participación",
                    "base_legal": "Art. 13 de la Ley 32069",
                    "severidad": "ALTA",
                    "fundamento": "No se puede restringir indebidamente la participación en consorcio sin justificación técnica"
                })
                break
        
        # =====================================================================
        # 6. DETECTAR PLAZOS IRREALES
        # =====================================================================
        patrones_plazo = [
            r'plazo\s+(?:de\s+)?(?:ejecuci[óo]n|entrega|prestaci[óo]n)[:\s]+(\d+)\s*(?:d[íi]as)',
            r'(?:en\s+)?(\d+)\s*(?:d[íi]as)\s*(?:calendario|h[áa]biles)?\s*(?:de\s+)?(?:plazo|ejecución)',
            r'duraci[óo]n[:\s]+(\d+)\s*(?:d[íi]as)',
        ]
        
        for patron in patrones_plazo:
            matches = re.findall(patron, texto_lower)
            for plazo_str in matches:
                try:
                    plazo = int(plazo_str)
                    if plazo <= 7:
                        vicios.append({
                            "tipo": "plazo_irreal",
                            "descripcion": f"Plazo de ejecución de {plazo} días es técnicamente inviable",
                            "ubicacion": "Condiciones del servicio / TDR",
                            "base_legal": "Art. 16 de la Ley 32069 (Razonabilidad)",
                            "severidad": "ALTA",
                            "fundamento": "Plazos muy cortos limitan la competencia y comprometen la calidad del servicio"
                        })
                        break
                    elif plazo <= 15:
                        vicios.append({
                            "tipo": "plazo_ajustado",
                            "descripcion": f"Plazo de ejecución de {plazo} días puede ser ajustado para algunos postores",
                            "ubicacion": "Condiciones del servicio / TDR",
                            "base_legal": "Art. 16 de la Ley 32069",
                            "severidad": "MEDIA",
                            "fundamento": "Verificar si el plazo es técnicamente viable para la prestación requerida"
                        })
                        break
                except:
                    pass
        
        # =====================================================================
        # 7. DETECTAR PENALIDADES EXCESIVAS
        # =====================================================================
        patron_pen = r'penalidad[^.]*?(\d+(?:[,\.]\d+)?)\s*%'
        matches_pen = re.findall(patron_pen, texto_lower)
        for pen_str in matches_pen:
            try:
                penalidad = float(pen_str.replace(',', '.'))
                if penalidad > 0.5:  # Mayor a 0.5% es excesiva
                    vicios.append({
                        "tipo": "penalidad_excesiva",
                        "descripcion": f"Penalidad del {penalidad}% puede exceder los límites del Art. 163",
                        "ubicacion": "Cláusula de penalidades",
                        "base_legal": "Art. 163 del Reglamento D.S. 009-2025-EF",
                        "severidad": "ALTA" if penalidad > 1 else "MEDIA",
                        "fundamento": "Las penalidades deben calcularse según la fórmula: Penalidad = (0.10 x Monto) / (F x Plazo)"
                    })
                    break
            except:
                pass
        
        # =====================================================================
        # 8. DETECTAR CERTIFICACIONES COMO REQUISITO OBLIGATORIO
        # =====================================================================
        certif_patterns = [
            (r'iso\s*9001', "ISO 9001"),
            (r'iso\s*14001', "ISO 14001"),
            (r'iso\s*45001', "ISO 45001"),
            (r'ohsas\s*18001', "OHSAS 18001"),
            (r'iso\s*27001', "ISO 27001"),
        ]
        
        for patron, nombre_cert in certif_patterns:
            if re.search(patron, texto_lower):
                # Verificar si es obligatoria
                contexto = re.search(rf'{patron}[^.]*', texto_lower)
                if contexto:
                    contexto_str = contexto.group(0)
                    if any(word in contexto_str for word in ['obligatori', 'requisito', 'indispensable', 'acreditar']):
                        vicios.append({
                            "tipo": "certificacion_restrictiva",
                            "descripcion": f"Se exige certificación {nombre_cert} como requisito obligatorio",
                            "ubicacion": "Requisitos de calificación",
                            "base_legal": "Art. 2 numeral 8 de la Ley 32069 (Libertad de Concurrencia)",
                            "severidad": "MEDIA",
                            "fundamento": "Las certificaciones ISO deben ser factor de evaluación, no requisito de calificación"
                        })
                        break
        
        # =====================================================================
        # 9. DETECTAR RESTRICCIONES GEOGRÁFICAS
        # =====================================================================
        patrones_geo = [
            r'domicili(?:o|ado)\s+(?:en|dentro\s+de)\s+([A-Za-záéíóúñ\s]+)',
            r'(?:oficina|local|establecimiento)\s+(?:en|dentro\s+de)\s+([A-Za-záéíóúñ\s]+)',
            r'sede\s+(?:en|dentro\s+de)\s+([A-Za-záéíóúñ\s]+)',
            r'ubicad[oa]\s+(?:en|dentro\s+de)\s+([A-Za-záéíóúñ\s]+)',
        ]
        
        for patron in patrones_geo:
            match = re.search(patron, texto_lower)
            if match:
                vicios.append({
                    "tipo": "restriccion_geografica",
                    "descripcion": f"Se exige ubicación geográfica específica: '{match.group(1).strip()}'",
                    "ubicacion": "Requisitos de calificación",
                    "base_legal": "Art. 2 de la Ley 32069 (Libre Competencia)",
                    "severidad": "ALTA",
                    "fundamento": "No se puede exigir domicilio o ubicación geográfica como requisito de calificación"
                })
                break
        
        # =====================================================================
        # 10. DETECTAR FACTORES DE EVALUACIÓN SUBJETIVOS
        # =====================================================================
        patrones_subjetivos = [
            (r'(?:criterio|factor)\s+(?:de\s+)?(?:evaluación|calificación)[^.]*(?:subjetiv|discrecional|a\s+criterio)', "factor subjetivo"),
            (r'(?:comité|evaluador)[^.]*(?:considerar[áa]|valorar[áa]|determinar[áa])', "discrecionalidad del evaluador"),
            (r'(?:mejor|mayor)\s+(?:propuesta|presentación|creatividad)', "criterio de creatividad/presentación"),
        ]
        
        for patron, tipo in patrones_subjetivos:
            if re.search(patron, texto_lower):
                vicios.append({
                    "tipo": "factor_subjetivo",
                    "descripcion": f"Se detectó posible {tipo} en los criterios de evaluación",
                    "ubicacion": "Factores de evaluación",
                    "base_legal": "Art. 28 del Reglamento D.S. 009-2025-EF",
                    "severidad": "MEDIA",
                    "fundamento": "Los factores de evaluación deben ser objetivos y cuantificables"
                })
                break
        
        # =====================================================================
        # 11. DETECTAR DOCUMENTACIÓN EXCESIVA
        # =====================================================================
        docs_innecesarios = [
            (r'carta\s+(?:de\s+)?(?:recomendación|referencia)', "cartas de recomendación"),
            (r'fotos?\s+(?:del\s+)?(?:local|establecimiento|oficina)', "fotos del establecimiento"),
            (r'(?:original|legalizad[oa])\s+(?:de|del)\s+(?:contrato|documento)', "documentos legalizados"),
            (r'constancia\s+(?:de\s+)?(?:no\s+)?(?:adeudo|deuda)', "constancia de no adeudo"),
        ]
        
        for patron, doc_tipo in docs_innecesarios:
            if re.search(patron, texto_lower):
                vicios.append({
                    "tipo": "documentacion_excesiva",
                    "descripcion": f"Se exige {doc_tipo} que no es requisito legal obligatorio",
                    "ubicacion": "Documentación para presentación de propuestas",
                    "base_legal": "Art. 29 del Reglamento D.S. 009-2025-EF",
                    "severidad": "BAJA",
                    "fundamento": "Solo se debe exigir documentación establecida en la normativa o necesaria para verificar requisitos"
                })
                break
        
        # =====================================================================
        # 12. DETECTAR EQUIPAMIENTO ESPECÍFICO
        # =====================================================================
        patron_equipamiento = r'(?:equipamiento|maquinaria|veh[íi]culo)[^.]*(?:propio|propiedad|a\s+nombre)'
        if re.search(patron_equipamiento, texto_lower):
            vicios.append({
                "tipo": "equipamiento_restrictivo",
                "descripcion": "Se exige equipamiento propio como requisito de calificación",
                "ubicacion": "Requisitos de calificación - Equipamiento",
                "base_legal": "Art. 29 del Reglamento D.S. 009-2025-EF",
                "severidad": "MEDIA",
                "fundamento": "El equipamiento puede ser propio, alquilado o mediante compromiso. No se puede exigir propiedad."
            })
        
        # =====================================================================
        # 13. CAPACIDAD FINANCIERA EXCESIVA (Ratios)
        # =====================================================================
        patrones_financ = [
            (r'(?:ratio|índice)\s+(?:de\s+)?liquidez[^.]*(?:mayor|superior|mínimo)\s+(?:a\s+)?(\d+(?:[.,]\d+)?)', "ratio de liquidez"),
            (r'(?:ratio|índice)\s+(?:de\s+)?solvencia[^.]*(?:mayor|superior|mínimo)\s+(?:a\s+)?(\d+(?:[.,]\d+)?)', "ratio de solvencia"),
            (r'(?:ratio|índice)\s+(?:de\s+)?endeudamiento[^.]*(?:menor|inferior|máximo)\s+(?:a\s+)?(\d+(?:[.,]\d+)?)', "ratio de endeudamiento"),
            (r'capital\s+(?:social|de\s+trabajo)[^.]*(?:mayor|superior|mínimo)[^.]*s/?\.?\s*(\d[\d,\.]+)', "capital mínimo"),
            (r'patrimonio\s+neto[^.]*(?:mayor|superior|mínimo)[^.]*s/?\.?\s*(\d[\d,\.]+)', "patrimonio mínimo"),
        ]
        
        for patron, tipo_ratio in patrones_financ:
            match = re.search(patron, texto_lower)
            if match:
                vicios.append({
                    "tipo": "capacidad_financiera_excesiva",
                    "descripcion": f"Se exige {tipo_ratio} que puede limitar la participación de postores",
                    "ubicacion": "Requisitos de calificación - Capacidad económico financiera",
                    "base_legal": "Art. 29 del Reglamento D.S. 009-2025-EF",
                    "severidad": "MEDIA",
                    "fundamento": "Los requisitos de capacidad financiera deben ser proporcionales al objeto de la contratación"
                })
                break
        
        # =====================================================================
        # 14. CONDICIONES LEONINAS O ABUSIVAS EN CONTRATO
        # =====================================================================
        condiciones_leoninas = [
            (r'renuncia[^.]*(?:derecho|reclam|demand)', "renuncia a derechos"),
            (r'(?:no\s+procede|improcedente)[^.]*(?:ampliación|adicional|reclamo)', "exclusión de derechos de ampliación"),
            (r'asume[^.]*(?:todo|cualquier)[^.]*riesgo', "asunción total de riesgos"),
            (r'(?:sin\s+derecho|no\s+corresponde)[^.]*(?:gastos\s+generales|utilidad)', "exclusión de gastos generales"),
            (r'bajo\s+(?:su\s+)?(?:exclusiva\s+)?responsabilidad', "responsabilidad exclusiva del contratista"),
        ]
        
        for patron, tipo_cond in condiciones_leoninas:
            if re.search(patron, texto_lower):
                vicios.append({
                    "tipo": "condicion_leonina",
                    "descripcion": f"Posible cláusula abusiva: {tipo_cond}",
                    "ubicacion": "Condiciones del contrato / Proforma",
                    "base_legal": "Art. 2 de la Ley 32069 (Equidad)",
                    "severidad": "ALTA",
                    "fundamento": "Las condiciones contractuales no deben ser desproporcionadas ni abusivas para una de las partes"
                })
                break
        
        # =====================================================================
        # 15. ADELANTOS EXCESIVOS O CONDICIONES
        # =====================================================================
        patron_adelanto = r'adelanto[^.]*(\d+)\s*%'
        match_adel = re.search(patron_adelanto, texto_lower)
        if match_adel:
            try:
                adelanto = int(match_adel.group(1))
                if adelanto > 30:  # Más del 30% puede ser excesivo
                    vicios.append({
                        "tipo": "adelanto_excesivo",
                        "descripcion": f"Se establece adelanto del {adelanto}% que puede exceder límites razonables",
                        "ubicacion": "Condiciones económicas",
                        "base_legal": "Art. 156-157 del Reglamento D.S. 009-2025-EF",
                        "severidad": "MEDIA",
                        "fundamento": "El adelanto directo no debe exceder el 30% del monto del contrato"
                    })
            except:
                pass
        
        # =====================================================================
        # 16. GARANTÍAS DESPROPORCIONADAS
        # =====================================================================
        patron_garantia = r'garantía[^.]*(\d+)\s*%'
        matches_gar = re.findall(patron_garantia, texto_lower)
        for gar_str in matches_gar:
            try:
                garantia = int(gar_str)
                if garantia > 10 and garantia < 100:  # Mayor a 10% (fiel cumplimiento)
                    vicios.append({
                        "tipo": "garantia_excesiva",
                        "descripcion": f"Se exige garantía del {garantia}% que excede el límite legal del 10%",
                        "ubicacion": "Requisitos de garantías",
                        "base_legal": "Art. 33 de la Ley 32069 y Art. 162 del Reglamento",
                        "severidad": "ALTA",
                        "fundamento": "La garantía de fiel cumplimiento es equivalente al 10% del monto del contrato"
                    })
                    break
            except:
                pass
        
        # =====================================================================
        # 17. CARTA FIANZA DE BANCO ESPECÍFICO
        # =====================================================================
        patrones_banco = [
            r'carta\s+fianza[^.]*(?:únicamente|solo|exclusivamente)[^.]*(?:banco|entidad)',
            r'(?:banco|entidad\s+financiera)[^.]*(?:clase\s+a|primer\s+orden|rating)',
            r'fianza[^.]*(?:emitida\s+por|de)[^.]*(?:banco\s+específico|determinado\s+banco)',
        ]
        
        for patron in patrones_banco:
            if re.search(patron, texto_lower):
                vicios.append({
                    "tipo": "fianza_restrictiva",
                    "descripcion": "Se exige carta fianza de banco específico o con restricciones excesivas",
                    "ubicacion": "Requisitos de garantías",
                    "base_legal": "Art. 33 de la Ley 32069",
                    "severidad": "MEDIA",
                    "fundamento": "No se puede restringir la procedencia de la carta fianza a entidades específicas"
                })
                break
        
        # =====================================================================
        # 18. SEGURO CAR/POLIZA EXCESIVA
        # =====================================================================
        patron_seguro = r'(?:seguro|póliza)[^.]*(\d+)\s*%[^.]*(?:monto|valor)'
        match_seg = re.search(patron_seguro, texto_lower)
        if match_seg:
            try:
                seguro = int(match_seg.group(1))
                if seguro > 100:  # Mayor al 100% del monto
                    vicios.append({
                        "tipo": "seguro_excesivo",
                        "descripcion": f"Se exige cobertura de seguro del {seguro}% que puede ser desproporcionada",
                        "ubicacion": "Requisitos de seguros",
                        "base_legal": "Art. 2 de la Ley 32069 (Proporcionalidad)",
                        "severidad": "MEDIA",
                        "fundamento": "Los requisitos de seguro deben ser proporcionales al riesgo de la contratación"
                    })
            except:
                pass
        
        # =====================================================================
        # 19. SUBCONTRATACIÓN PROHIBIDA O RESTRINGIDA
        # =====================================================================
        patrones_subcontrato = [
            r'(?:no\s+se\s+permite|prohib)[^.]*subcontrat',
            r'subcontrat[^.]*(?:prohib|no\s+permit)',
            r'ejecutar[^.]*(?:íntegramente|totalmente|directamente)[^.]*(?:sin|no)[^.]*subcontrat',
        ]
        
        for patron in patrones_subcontrato:
            if re.search(patron, texto_lower):
                vicios.append({
                    "tipo": "subcontratacion_prohibida",
                    "descripcion": "Se prohíbe la subcontratación sin justificación técnica",
                    "ubicacion": "Condiciones de ejecución",
                    "base_legal": "Art. 35 de la Ley 32069",
                    "severidad": "MEDIA",
                    "fundamento": "La subcontratación puede restringirse solo hasta el 40% según el Art. 35"
                })
                break
        
        # =====================================================================
        # 20. CONDICIONES DE PAGO LEONINAS
        # =====================================================================
        patrones_pago = [
            r'pago[^.]*(?:contra\s+)?conformidad[^.]*(\d+)\s*días',
            r'(\d+)\s*días[^.]*(?:para\s+)?pago',
            r'pago[^.]*(?:previa|posterior)\s+a\s+la\s+liquidación',
        ]
        
        for patron in patrones_pago:
            match = re.search(patron, texto_lower)
            if match:
                try:
                    if match.groups():
                        dias = int(match.group(1))
                        if dias > 30:  # Más de 30 días para pago
                            vicios.append({
                                "tipo": "condicion_pago_excesiva",
                                "descripcion": f"Plazo de pago de {dias} días excede lo razonable (máximo 30 días)",
                                "ubicacion": "Condiciones de pago",
                                "base_legal": "Art. 171 del Reglamento D.S. 009-2025-EF",
                                "severidad": "MEDIA",
                                "fundamento": "El plazo de pago debe ser razonable para no afectar la liquidez del contratista"
                            })
                            break
                except:
                    pass
        
        # =====================================================================
        # 21. MODIFICACIÓN UNILATERAL DEL CONTRATO
        # =====================================================================
        patrones_modif = [
            r'entidad[^.]*(?:podrá|puede)[^.]*modificar[^.]*(?:unilateral|sin\s+consentimiento)',
            r'modificaci[óo]n[^.]*(?:a\s+criterio|discreción)[^.]*entidad',
            r'reserva[^.]*(?:derecho|facultad)[^.]*modificar',
        ]
        
        for patron in patrones_modif:
            if re.search(patron, texto_lower):
                vicios.append({
                    "tipo": "modificacion_unilateral",
                    "descripcion": "Se reserva derecho de modificación unilateral del contrato",
                    "ubicacion": "Condiciones del contrato",
                    "base_legal": "Art. 34 de la Ley 32069",
                    "severidad": "ALTA",
                    "fundamento": "Las modificaciones contractuales deben seguir el procedimiento establecido en la Ley"
                })
                break
        
        # =====================================================================
        # 22. CAUSALES DE RESOLUCIÓN EXCESIVAS
        # =====================================================================
        patrones_resol = [
            r'resoluci[óo]n[^.]*(?:automática|ipso\s+facto|de\s+pleno\s+derecho)',
            r'(?:cualquier|todo)[^.]*incumplimiento[^.]*resoluci[óo]n',
            r'resoluci[óo]n[^.]*sin\s+(?:previo\s+)?(?:aviso|requerimiento)',
        ]
        
        for patron in patrones_resol:
            if re.search(patron, texto_lower):
                vicios.append({
                    "tipo": "resolucion_excesiva",
                    "descripcion": "Se establecen causales de resolución automática o desproporcionadas",
                    "ubicacion": "Cláusulas de resolución",
                    "base_legal": "Art. 36 de la Ley 32069 y Art. 164 del Reglamento",
                    "severidad": "ALTA",
                    "fundamento": "La resolución del contrato debe seguir el procedimiento del Art. 36 de la Ley"
                })
                break
        
        # =====================================================================
        # 23. PERSONAL RESIDENTE/CLAVE EXCESIVO
        # =====================================================================
        patron_personal = r'(?:personal\s+(?:clave|técnico|profesional)|staff)[^.]*(\d+)\s*(?:profesionales|personas|integrantes)'
        match_pers = re.search(patron_personal, texto_lower)
        if match_pers:
            try:
                num_personal = int(match_pers.group(1))
                if num_personal > 10:  # Más de 10 profesionales puede ser excesivo
                    vicios.append({
                        "tipo": "personal_excesivo",
                        "descripcion": f"Se exige {num_personal} profesionales como personal clave - Posible sobredimensionamiento",
                        "ubicacion": "Requisitos de calificación - Personal",
                        "base_legal": "Art. 29 del Reglamento D.S. 009-2025-EF",
                        "severidad": "MEDIA",
                        "fundamento": "El personal exigido debe ser proporcional al objeto de la contratación"
                    })
            except:
                pass
        
        # =====================================================================
        # 24. PLAZO DE CONSULTAS/OBSERVACIONES MUY CORTO
        # =====================================================================
        patrones_consultas = [
            r'(?:consultas|observaciones)[^.]*(\d+)\s*(?:días?\s+)?(?:calendario|hábil)',
            r'(\d+)\s*(?:días?\s+)?(?:calendario|hábil)[^.]*(?:consultas|observaciones)',
        ]
        
        for patron in patrones_consultas:
            match = re.search(patron, texto_lower)
            if match:
                try:
                    dias = int(match.group(1))
                    if dias < 3:  # Menos de 3 días es muy poco
                        vicios.append({
                            "tipo": "plazo_consultas_corto",
                            "descripcion": f"Plazo de {dias} días para consultas/observaciones es insuficiente",
                            "ubicacion": "Cronograma del procedimiento",
                            "base_legal": "Art. 51 del Reglamento D.S. 009-2025-EF",
                            "severidad": "MEDIA",
                            "fundamento": "El plazo para formular observaciones debe ser razonable para analizar las bases"
                        })
                        break
                except:
                    pass
        
        # =====================================================================
        # 25. FORMA DE PRESENTACIÓN RESTRICTIVA
        # =====================================================================
        patrones_present = [
            r'(?:únicamente|solo|exclusivamente)[^.]*(?:físico|presencial|impreso)',
            r'no\s+(?:se\s+)?acepta[^.]*(?:electrónico|digital|virtual)',
            r'(?:original|fedatead)[^.]*obligatori',
        ]
        
        for patron in patrones_present:
            if re.search(patron, texto_lower):
                vicios.append({
                    "tipo": "presentacion_restrictiva",
                    "descripcion": "Se restringe la forma de presentación de propuestas sin justificación",
                    "ubicacion": "Condiciones de presentación de propuestas",
                    "base_legal": "Art. 2 de la Ley 32069 (Libertad de Concurrencia)",
                    "severidad": "BAJA",
                    "fundamento": "La forma de presentación debe facilitar la participación, no restringirla"
                })
                break
        
        # =====================================================================
        # 26. ANTICORRUPCIÓN/COMPLIANCE EXCESIVO
        # =====================================================================
        patrones_compliance = [
            r'(?:certificación|certificado)[^.]*(?:anticorrupción|compliance|integridad)',
            r'(?:programa|sistema)[^.]*(?:compliance|anticorrupción)[^.]*(?:obligatori|requisito)',
            r'(?:obligatori|exig)[^.]*(?:código\s+de\s+ética|norma\s+ética)',
        ]
        
        for patron in patrones_compliance:
            if re.search(patron, texto_lower):
                vicios.append({
                    "tipo": "compliance_restrictivo",
                    "descripcion": "Se exige certificación de compliance/anticorrupción como requisito",
                    "ubicacion": "Requisitos de calificación",
                    "base_legal": "Art. 2 numeral 8 de la Ley 32069",
                    "severidad": "BAJA",
                    "fundamento": "Los programas de compliance son voluntarios y no pueden ser requisito obligatorio"
                })
                break
        
        # =====================================================================
        # 27. VALORIZACIÓN ÚNICA O CONDICIONADA
        # =====================================================================
        patrones_valor = [
            r'valorización[^.]*(?:única|final|al\s+término)',
            r'pago[^.]*(?:único|contra\s+entrega\s+total)',
            r'no\s+(?:se\s+)?(?:procede|acepta)[^.]*valorización[^.]*(?:parcial|mensual)',
        ]
        
        for patron in patrones_valor:
            if re.search(patron, texto_lower):
                vicios.append({
                    "tipo": "valorizacion_restrictiva",
                    "descripcion": "Se exige valorización única sin pagos parciales",
                    "ubicacion": "Condiciones de pago",
                    "base_legal": "Art. 166-171 del Reglamento D.S. 009-2025-EF",
                    "severidad": "MEDIA",
                    "fundamento": "Las valorizaciones deben permitir pagos periódicos según el avance de ejecución"
                })
                break

        # =====================================================================
        # 28. REQUERIMIENTOS TÉCNICOS MÍNIMOS (RTM) EXCESIVOS
        # =====================================================================
        patrones_rtm = [
            (r'(?:rtm|requerimiento\s+técnico\s+mínimo)[^.]*(?:capacidad|rendimiento)[^.]*([\d,]+)\s*(?:gb|tb|ghz|mb)', "especificaciones técnicas altas"),
            (r'(?:rtm|especificaci[óo]n)[^.]*(?:marca|modelo)\s+(?:específic|únic)', "marca/modelo específico en RTM"),
            (r'(?:rtm|requerimiento)[^.]*(?:nuevo|sin\s+uso|reciente)', "producto nuevo obligatorio"),
            (r'(?:rtm|requerimiento)[^.]*(?:original|no\s+compatible|genuino)', "original/genuino obligatorio"),
        ]
        
        for patron, desc in patrones_rtm:
            if re.search(patron, texto_lower):
                vicios.append({
                    "tipo": "rtm_restrictivo",
                    "descripcion": f"RTM restrictivo: {desc}",
                    "ubicacion": "Requerimientos Técnicos Mínimos / TDR",
                    "base_legal": "Art. 16 de la Ley 32069 - Especificaciones objetivas",
                    "severidad": "ALTA",
                    "fundamento": "Los RTM deben ser objetivos y permitir la mayor concurrencia posible"
                })
                break
        
        # =====================================================================
        # 29. REQUISITOS DE ADMISIBILIDAD EXCESIVOS
        # =====================================================================
        patrones_admisibilidad = [
            (r'requisito\s+(?:de\s+)?admisibilidad[^.]*(?:carta\s+fianza|garantía\s+de\s+seriedad)', "garantía de seriedad como admisibilidad"),
            (r'admisi[óo]n[^.]*(?:constancia|certificado)[^.]*(?:vigente|actualizado)', "documentos actualizados para admisión"),
            (r'admisibilidad[^.]*(?:balance|estado\s+financiero)', "balance/estados financieros para admisión"),
            (r'(?:no\s+ser\s+admitid|exclu)[^.]*(?:por\s+)?(?:error|omisión)\s+(?:formal|subsanable)', "exclusión por errores formales"),
            (r'admisibilidad[^.]*(?:notarial|legalizado)', "documentos notariales para admisión"),
        ]
        
        for patron, desc in patrones_admisibilidad:
            if re.search(patron, texto_lower):
                vicios.append({
                    "tipo": "admisibilidad_excesiva",
                    "descripcion": f"Requisito de admisibilidad excesivo: {desc}",
                    "ubicacion": "Requisitos de Admisibilidad",
                    "base_legal": "Art. 29 del Reglamento - Solo documentos necesarios",
                    "severidad": "ALTA",
                    "fundamento": "Los requisitos de admisibilidad deben limitarse a lo estrictamente necesario"
                })
                break
        
        # =====================================================================
        # 30. FACTORES DE EVALUACIÓN SUBJETIVOS O MAL DISEÑADOS
        # =====================================================================
        patrones_factores = [
            (r'factor\s+(?:de\s+)?evaluación[^.]*(?:a\s+criterio|discreción|consideración)', "factor subjetivo"),
            (r'puntaje[^.]*(?:calidad|presentación|creatividad)', "criterio de calidad subjetivo"),
            (r'(?:metodología|plan\s+de\s+trabajo)[^.]*(?:mejor|más\s+completo)', "metodología sin criterios claros"),
            (r'factor[^.]*(?:100|90|80)\s*(?:puntos|%)[^.]*experiencia', "peso excesivo en experiencia"),
            (r'evalua(?:ción|rá)[^.]*(?:presentación|formato|estética)', "evaluación de presentación"),
        ]
        
        for patron, desc in patrones_factores:
            if re.search(patron, texto_lower):
                vicios.append({
                    "tipo": "factor_evaluacion_defectuoso",
                    "descripcion": f"Factor de evaluación defectuoso: {desc}",
                    "ubicacion": "Factores de Evaluación",
                    "base_legal": "Art. 28 del Reglamento - Factores objetivos y cuantificables",
                    "severidad": "ALTA",
                    "fundamento": "Los factores de evaluación deben ser objetivos, medibles y proporcionales"
                })
                break
        
        # =====================================================================
        # 31. METODOLOGÍA DE EVALUACIÓN TÉCNICA DEFECTUOSA
        # =====================================================================
        patrones_metodologia = [
            (r'puntaje\s+técnico[^.]*(?:mínimo|aprobatorio)[^.]*([\d]+)', "puntaje mínimo alto"),
            (r'evalua(?:ción|rá)\s+técnic[^.]*(?:eliminatori|excluyente)', "evaluación técnica eliminatoria"),
            (r'propuesta\s+técnica[^.]*(?:descartad|rechazad)[^.]*(?:por|si)', "descarte técnico estricto"),
        ]
        
        for patron, desc in patrones_metodologia:
            match = re.search(patron, texto_lower)
            if match:
                vicios.append({
                    "tipo": "metodologia_evaluacion_defectuosa",
                    "descripcion": f"Metodología de evaluación defectuosa: {desc}",
                    "ubicacion": "Metodología de Evaluación",
                    "base_legal": "Art. 28-29 del Reglamento",
                    "severidad": "MEDIA",
                    "fundamento": "La metodología de evaluación debe permitir competencia efectiva"
                })
                break
        
        # =====================================================================
        # 32. TÉRMINOS DE REFERENCIA (TDR) MAL DEFINIDOS
        # =====================================================================
        patrones_tdr = [
            (r't[ée]rminos\s+de\s+referencia[^.]*(?:según|conforme)[^.]*entidad', "TDR a criterio de entidad"),
            (r'(?:alcance|prestaci[óo]n)[^.]*(?:y/o\s+)?(?:otros|adicionales)\s+que\s+(?:la\s+entidad|se)', "alcance abierto"),
            (r'(?:podr[áa]|podr[íi]a)[^.]*(?:solicitar|requerir)[^.]*(?:adicional|otros)', "prestaciones adicionales indefinidas"),
            (r'(?:actividades|trabajos)[^.]*(?:no\s+previst|complement)', "actividades no previstas"),
        ]
        
        for patron, desc in patrones_tdr:
            if re.search(patron, texto_lower):
                vicios.append({
                    "tipo": "tdr_indefinido",
                    "descripcion": f"TDR mal definido: {desc}",
                    "ubicacion": "Términos de Referencia / TDR",
                    "base_legal": "Art. 16 de la Ley 32069",
                    "severidad": "ALTA",
                    "fundamento": "El objeto de la contratación debe estar claramente definido"
                })
                break
        
        # =====================================================================
        # 33. CAPACIDAD TÉCNICA Y PROFESIONAL EXCESIVA
        # =====================================================================
        patrones_capacidad = [
            (r'capacidad\s+técnica[^.]*([\d]+)\s*(?:obras|servicios|contratos)[^.]*similar', "cantidad de contratos similares alta"),
            (r'(?:igual|idéntico)[^.]*(?:servicio|obra|bien)', "experiencia idéntica requerida"),
            (r'(?:mismo\s+)?(?:sector|rubro|giro)[^.]*(?:obligatori|requerid)', "mismo sector obligatorio"),
            (r'(?:cliente|entidad)[^.]*(?:público|estatal)[^.]*(?:obligatori|únicamente)', "solo clientes públicos"),
        ]
        
        for patron, desc in patrones_capacidad:
            if re.search(patron, texto_lower):
                vicios.append({
                    "tipo": "capacidad_tecnica_excesiva",
                    "descripcion": f"Capacidad técnica excesiva: {desc}",
                    "ubicacion": "Requisitos de Calificación - Capacidad Técnica",
                    "base_legal": "Art. 29 del Reglamento",
                    "severidad": "ALTA",
                    "fundamento": "Los requisitos de capacidad técnica deben ser proporcionales"
                })
                break
        
        # =====================================================================
        # 34. DOCUMENTOS DE PRESENTACIÓN OBLIGATORIA EXCESIVOS
        # =====================================================================
        patrones_documentos = [
            (r'(?:obligatori|present)[^.]*(?:curriculum|cv|hoja\s+de\s+vida)', "CV obligatorio"),
            (r'(?:obligatori|present)[^.]*(?:brochure|catálogo|portafolio)', "catálogo/brochure obligatorio"),
            (r'(?:copia|fotocopia)[^.]*(?:legalizada|certificada|notarial)', "copias legalizadas"),
            (r'(?:documento|constancia)[^.]*(?:apostillad)', "apostilla requerida"),
            (r'(?:traducción\s+)?(?:oficial|certificada)', "traducción oficial"),
        ]
        
        for patron, desc in patrones_documentos:
            if re.search(patron, texto_lower):
                vicios.append({
                    "tipo": "documentos_excesivos",
                    "descripcion": f"Documentación obligatoria excesiva: {desc}",
                    "ubicacion": "Documentos de Presentación",
                    "base_legal": "Art. 29 del Reglamento - Simplificación administrativa",
                    "severidad": "MEDIA",
                    "fundamento": "Solo se debe exigir documentación necesaria para la evaluación"
                })
                break
        
        # =====================================================================
        # 35. CRITERIOS DE DESEMPATE NO CLAROS
        # =====================================================================
        patrones_desempate = [
            (r'desempate[^.]*(?:a\s+criterio|discreción|sorteo)', "desempate subjetivo"),
            (r'(?:empate|igualdad)[^.]*(?:no\s+se\s+establece|sin\s+criterio)', "sin criterio de desempate"),
        ]
        
        for patron, desc in patrones_desempate:
            if re.search(patron, texto_lower):
                vicios.append({
                    "tipo": "desempate_defectuoso",
                    "descripcion": f"Criterio de desempate defectuoso: {desc}",
                    "ubicacion": "Metodología de Evaluación - Desempate",
                    "base_legal": "Art. 28 del Reglamento",
                    "severidad": "MEDIA",
                    "fundamento": "Los criterios de desempate deben ser objetivos (MYPE, RSE, etc.)"
                })
                break
        
        # =====================================================================
        # 36. OBJETO CONTRACTUAL MAL DEFINIDO
        # =====================================================================
        patrones_objeto = [
            (r'objeto[^.]*(?:y/o|u\s+otros|entre\s+otros)', "objeto contractual ambiguo"),
            (r'(?:incluye|comprende)[^.]*(?:todo|cualquier)[^.]*(?:necesari|requerid)', "alcance abierto"),
            (r'(?:prestaciones|actividades)[^.]*(?:complement|adicional|conexas)', "prestaciones conexas indefinidas"),
        ]
        
        for patron, desc in patrones_objeto:
            if re.search(patron, texto_lower):
                vicios.append({
                    "tipo": "objeto_mal_definido",
                    "descripcion": f"Objeto contractual mal definido: {desc}",
                    "ubicacion": "Objeto de la Contratación",
                    "base_legal": "Art. 16 de la Ley 32069",
                    "severidad": "ALTA",
                    "fundamento": "El objeto debe ser claro, preciso y determinable"
                })
                break
        
        # =====================================================================
        # 37. HABILITACIÓN PROFESIONAL EXCESIVA
        # =====================================================================
        patrones_habilitacion = [
            (r'habilitaci[óo]n[^.]*(?:vigente|activa)[^.]*(?:colegio|institución)', "habilitación profesional específica"),
            (r'(?:inscripci[óo]n|registro)[^.]*(?:obligatori|requerid)[^.]*(?:cámar|asociación|gremio)', "inscripción en gremio"),
            (r'(?:rne|rnp|sunat)[^.]*(?:específic|determinad)', "registro específico no necesario"),
        ]
        
        for patron, desc in patrones_habilitacion:
            if re.search(patron, texto_lower):
                vicios.append({
                    "tipo": "habilitacion_excesiva",
                    "descripcion": f"Habilitación profesional excesiva: {desc}",
                    "ubicacion": "Requisitos de Habilitación",
                    "base_legal": "Art. 29 del Reglamento - Solo habilitación necesaria",
                    "severidad": "MEDIA",
                    "fundamento": "Solo se debe exigir la habilitación legalmente requerida para la actividad"
                })
                break
        
        # =====================================================================
        # 38. PONDERACIÓN TÉCNICA/ECONÓMICA DESEQUILIBRADA
        # =====================================================================
        patron_ponderacion = r'(?:ponderaci[óo]n|peso)[^.]*(?:técnic|económic)[^.]*(\d+)[^.]*%'
        matches_pond = re.findall(patron_ponderacion, texto_lower)
        if matches_pond:
            for peso in matches_pond:
                try:
                    peso_num = int(peso)
                    if peso_num > 80 or peso_num < 20:
                        vicios.append({
                            "tipo": "ponderacion_desequilibrada",
                            "descripcion": f"Ponderación técnica/económica desequilibrada ({peso_num}%)",
                            "ubicacion": "Metodología de Evaluación",
                            "base_legal": "Art. 28 del Reglamento",
                            "severidad": "MEDIA",
                            "fundamento": "La ponderación debe equilibrar aspectos técnicos y económicos (usualmente 70-30 o 80-20)"
                        })
                        break
                except:
                    pass
        
        # =====================================================================
        # 39. VISITA TÉCNICA OBLIGATORIA
        # =====================================================================
        patrones_visita = [
            r'visita\s+(?:técnica|de\s+campo)[^.]*(?:obligatori|indispensable)',
            r'(?:obligatori|indispensable)[^.]*visita\s+(?:al\s+)?(?:lugar|sitio|obra)',
            r'no\s+(?:se\s+)?admitir[áa][^.]*(?:sin|que\s+no)[^.]*visita',
        ]
        
        for patron in patrones_visita:
            if re.search(patron, texto_lower):
                vicios.append({
                    "tipo": "visita_obligatoria",
                    "descripcion": "Se exige visita técnica obligatoria como requisito",
                    "ubicacion": "Requisitos de Participación",
                    "base_legal": "Art. 2 de la Ley 32069 - Libertad de Concurrencia",
                    "severidad": "MEDIA",
                    "fundamento": "La visita técnica debe ser facultativa, no obligatoria"
                })
                break
        
        # =====================================================================
        # 40. MUESTRAS FÍSICAS OBLIGATORIAS
        # =====================================================================
        patrones_muestras = [
            r'muestra\s+(?:física|original)[^.]*(?:obligatori|present)',
            r'prototipo[^.]*(?:obligatori|present|entregar)',
            r'(?:obligatori|present)[^.]*(?:muestra|prototipo|ejemplar)',
        ]
        
        for patron in patrones_muestras:
            if re.search(patron, texto_lower):
                vicios.append({
                    "tipo": "muestras_obligatorias",
                    "descripcion": "Se exige presentación obligatoria de muestras físicas",
                    "ubicacion": "Requisitos de Presentación",
                    "base_legal": "Art. 2 de la Ley 32069",
                    "severidad": "MEDIA",
                    "fundamento": "Las muestras deben ser facultativas o limitadas a casos técnicamente justificados"
                })
                break
        
        # =====================================================================
        # 41. PLAZO DE VALIDEZ DE OFERTA EXCESIVO
        # =====================================================================
        patron_validez = r'(?:validez|vigencia)\s+(?:de\s+)?(?:la\s+)?(?:oferta|propuesta)[^.]*(\d+)\s*(?:días|meses)'
        match_validez = re.search(patron_validez, texto_lower)
        if match_validez:
            try:
                plazo_validez = int(match_validez.group(1))
                if plazo_validez > 90:  # Más de 90 días puede ser excesivo
                    vicios.append({
                        "tipo": "validez_oferta_excesiva",
                        "descripcion": f"Validez de oferta de {plazo_validez} días es excesiva",
                        "ubicacion": "Condiciones de Presentación",
                        "base_legal": "Art. 2 de la Ley 32069",
                        "severidad": "BAJA",
                        "fundamento": "La validez de oferta no debe exceder plazos razonables (60-90 días)"
                    })
            except:
                pass
        
        # =====================================================================
        # 42. CRONOGRAMA CON PLAZOS INSUFICIENTES
        # =====================================================================
        patrones_cronograma = [
            (r'(?:registro|inscripción)\s+(?:de\s+)?participantes[^.]*(\d+)\s*días?', "registro de participantes"),
            (r'presentaci[óo]n\s+(?:de\s+)?(?:propuestas|ofertas)[^.]*(\d+)\s*días?', "presentación de propuestas"),
        ]
        
        for patron, etapa in patrones_cronograma:
            match = re.search(patron, texto_lower)
            if match:
                try:
                    dias = int(match.group(1))
                    if dias < 3:
                        vicios.append({
                            "tipo": "cronograma_ajustado",
                            "descripcion": f"Plazo insuficiente para {etapa}: {dias} días",
                            "ubicacion": "Cronograma del Procedimiento",
                            "base_legal": "Directivas de Bases Estándar",
                            "severidad": "MEDIA",
                            "fundamento": "Los plazos del cronograma deben permitir participación efectiva"
                        })
                        break
                except:
                    pass

        print(f"🔍 Análisis exhaustivo por reglas: {len(vicios)} vicios detectados")
        
        # =====================================================================
        # POST-PROCESAMIENTO: Agregar ubicación por página a cada vicio
        # =====================================================================
        if texto_por_pagina:
            for vicio in vicios:
                if "pagina" not in vicio:  # Si no tiene página aún
                    # Buscar palabras clave del vicio en las páginas
                    descripcion = vicio.get("descripcion", "").lower()
                    tipo = vicio.get("tipo", "").lower()
                    
                    # Extraer palabras clave para buscar
                    palabras_clave = []
                    if "experiencia" in tipo or "experiencia" in descripcion:
                        palabras_clave = ["experiencia", "monto facturado", "experiencia mínima"]
                    elif "penalidad" in tipo:
                        palabras_clave = ["penalidad", "mora", "retraso"]
                    elif "garantia" in tipo or "garantía" in descripcion:
                        palabras_clave = ["garantía", "carta fianza", "garantia"]
                    elif "plazo" in tipo:
                        palabras_clave = ["plazo", "ejecución", "días"]
                    elif "marca" in tipo or "direccionamiento" in tipo:
                        palabras_clave = ["marca", "modelo", "fabricante"]
                    elif "rtm" in tipo:
                        palabras_clave = ["rtm", "requerimiento técnico", "especificación"]
                    elif "admisibilidad" in tipo:
                        palabras_clave = ["admisibilidad", "admisión", "requisitos de admisión"]
                    elif "factor" in tipo or "evaluación" in tipo:
                        palabras_clave = ["factor", "evaluación", "puntaje"]
                    elif "tdr" in tipo:
                        palabras_clave = ["términos de referencia", "tdr", "alcance"]
                    elif "capacidad" in tipo:
                        palabras_clave = ["capacidad técnica", "calificación"]
                    elif "habilitación" in tipo:
                        palabras_clave = ["habilitación", "inscripción", "registro"]
                    elif "ponderación" in tipo:
                        palabras_clave = ["ponderación", "peso", "técnico", "económico"]
                    elif "visita" in tipo:
                        palabras_clave = ["visita técnica", "visita obligatoria"]
                    elif "muestra" in tipo:
                        palabras_clave = ["muestra", "prototipo"]
                    elif "cronograma" in tipo:
                        palabras_clave = ["cronograma", "calendario", "etapa"]
                    elif "consulta" in tipo:
                        palabras_clave = ["consulta", "absolución"]
                    elif "objeto" in tipo:
                        palabras_clave = ["objeto", "contratación", "materia"]
                    else:
                        # Usar el tipo como palabra clave
                        palabras_clave = [tipo.replace("_", " ")]
                    
                    # Buscar en qué página aparecen las palabras clave
                    for pagina_data in texto_por_pagina:
                        num_pagina = pagina_data["pagina"]
                        texto_pagina = pagina_data["texto"].lower()
                        
                        for palabra in palabras_clave:
                            if palabra in texto_pagina:
                                vicio["pagina"] = num_pagina
                                
                                # Buscar capítulo en esa página
                                cap_match = re.search(
                                    r'(capítulo\s+[ivxlcd\d]+[^\n]*|[\d\.]+\s*[A-ZÁÉÍÓÚ][^\n]{0,50})',
                                    texto_pagina[:texto_pagina.find(palabra)],
                                    re.IGNORECASE
                                )
                                if cap_match:
                                    vicio["capitulo"] = cap_match.group(1).strip()[:100]
                                
                                # Extraer cita textual (contexto)
                                idx = texto_pagina.find(palabra)
                                start = max(0, idx - 30)
                                end = min(len(texto_pagina), idx + 100)
                                vicio["cita_textual"] = "..." + texto_pagina[start:end].strip() + "..."
                                
                                # Actualizar ubicación con el número de página
                                ubicacion_original = vicio.get("ubicacion", "")
                                vicio["ubicacion"] = f"Página {num_pagina} - {ubicacion_original}"
                                break
                        
                        if "pagina" in vicio:
                            break  # Ya encontramos la página
            
            print(f"📍 Ubicación por página agregada a {sum(1 for v in vicios if 'pagina' in v)} vicios")
        
        return vicios
    
    def _extraer_numero_proceso(self, texto: str) -> str:
        """Extrae el número de proceso del texto"""
        patrones = [
            r'(?:LP|PA|CD|AS|SIE)\s*N[°º]?\s*([\d\-]+\s*-\s*\d{4})',
            r'Procedimiento\s+N[°º]?\s*([\d\-]+)',
        ]
        for patron in patrones:
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                return match.group(0)
        return "No identificado"
    
    def _extraer_entidad(self, texto: str) -> str:
        """Extrae el nombre de la entidad del texto"""
        patrones = [
            r'(?:ENTIDAD|CONVOCANTE)[:\s]+([A-ZÁÉÍÓÚÑ\s]+)',
            r'(?:MUNICIPALIDAD|GOBIERNO REGIONAL|MINISTERIO)[^\n]+',
        ]
        for patron in patrones:
            match = re.search(patron, texto[:2000], re.IGNORECASE)
            if match:
                return match.group(0)[:100]
        return "Entidad no identificada"
    
    def _extraer_tipo_procedimiento(self, texto: str) -> str:
        """Extrae el tipo de procedimiento"""
        texto_upper = texto[:1000].upper()
        if 'LICITACIÓN PÚBLICA' in texto_upper or 'LP N' in texto_upper:
            return "LP"
        elif 'PROCEDIMIENTO ABREVIADO' in texto_upper or 'PA N' in texto_upper:
            return "PA"
        elif 'ADJUDICACIÓN SIMPLIFICADA' in texto_upper or 'AS N' in texto_upper:
            return "AS"
        elif 'CONTRATACIÓN DIRECTA' in texto_upper or 'CD N' in texto_upper:
            return "CD"
        return "No identificado"


class DocumentAnalyzer:
    """
    Analizador de documentos que combina extracción y análisis inteligente
    """
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
    
    def analizar_bases_completo(self, pdf_path: str) -> Dict:
        """
        Análisis completo de bases de un procedimiento.
        VERSIÓN MEJORADA: Usa datos cuantificables para detección automática de vicios.
        
        Returns:
            Dict con datos estructurados, vicios detectados, observaciones sugeridas
        """
        # Extraer texto
        extraccion = self.pdf_processor.extraer_texto_pdf(pdf_path)
        
        if "error" in extraccion:
            return extraccion
        
        texto = extraccion["texto_completo"]
        print(f"📄 PDF extraído: {len(texto)} caracteres")
        
        # Identificar tipo
        tipo = self.pdf_processor.identificar_tipo_documento(texto)
        
        # Extracción estructurada básica (incluye datos cuantificables)
        datos_basicos = self.pdf_processor.extraer_datos_bases(texto)
        
        # =====================================================================
        # NUEVO: Extraer datos cuantificables para validación automática
        # =====================================================================
        datos_cuantificables = datos_basicos.get("datos_cuantificables", {})
        
        if datos_cuantificables:
            print(f"📊 Datos cuantificables extraídos:")
            if datos_cuantificables.get("valor_referencial"):
                print(f"   💰 VR: S/ {datos_cuantificables['valor_referencial']:,.2f}")
            if datos_cuantificables.get("experiencia_postor"):
                print(f"   📋 Exp. Postor: S/ {datos_cuantificables['experiencia_postor']:,.2f}")
            if datos_cuantificables.get("ratio_experiencia_vr"):
                ratio = datos_cuantificables['ratio_experiencia_vr']
                emoji = "⚠️" if ratio > 1.0 else "✅"
                print(f"   {emoji} Ratio Exp/VR: {ratio}x")
            if datos_cuantificables.get("plazo_ejecucion"):
                print(f"   📅 Plazo: {datos_cuantificables['plazo_ejecucion']} días")
            if datos_cuantificables.get("experiencia_personal"):
                print(f"   👤 Exp. Personal: {max(datos_cuantificables['experiencia_personal'])} años máx")
        
        # Análisis inteligente con Gemini
        print("🤖 Enviando a Gemini para análisis...")
        analisis_ia = self.pdf_processor.analizar_documento_gemini_sync(texto, "bases")
        
        # =====================================================================
        # NUEVO: Fusionar datos cuantificables con análisis de Gemini
        # =====================================================================
        # Agregar datos cuantificables al análisis de IA para que el híbrido los use
        analisis_ia["datos_cuantificables"] = datos_cuantificables
        
        # Si Gemini extrajo VR y experiencia, usarlos también
        if analisis_ia.get("valor_referencial") and not datos_cuantificables.get("valor_referencial"):
            datos_cuantificables["valor_referencial"] = analisis_ia["valor_referencial"]
        if analisis_ia.get("experiencia_postor") and not datos_cuantificables.get("experiencia_postor"):
            datos_cuantificables["experiencia_postor"] = analisis_ia["experiencia_postor"]
        
        # Recalcular ratio si tenemos ambos valores
        if datos_cuantificables.get("valor_referencial") and datos_cuantificables.get("experiencia_postor"):
            vr = datos_cuantificables["valor_referencial"]
            exp = datos_cuantificables["experiencia_postor"]
            ratio = exp / vr
            datos_cuantificables["ratio_experiencia_vr"] = round(ratio, 2)
            datos_cuantificables["excede_limite_experiencia"] = ratio > 1.0
            
            if ratio > 1.0:
                print(f"🚨 VICIO CRÍTICO DETECTADO: Experiencia ({ratio:.2f}x) EXCEDE el VR")
        
        # DEBUG: Ver qué devolvió Gemini
        print(f"🔍 Gemini devolvió: {list(analisis_ia.keys())}")
        vicios_gemini = analisis_ia.get('posibles_vicios', [])
        print(f"⚠️  Vicios de Gemini: {len(vicios_gemini)}")
        if vicios_gemini:
            for v in vicios_gemini[:3]:  # Mostrar solo los primeros 3
                print(f"   - {v.get('tipo', 'N/A')}: {v.get('descripcion', 'N/A')[:50]}...")
        
        # Análisis híbrido para detectar vicios
        from engine.observaciones import ObservacionesGenerator
        obs_gen = ObservacionesGenerator()
        
        valor_referencial = datos_cuantificables.get("valor_referencial") or datos_basicos.get("valor_referencial")
        # Pasar texto_por_pagina para identificar ubicación exacta de cada vicio
        texto_por_pagina = extraccion.get("texto_por_pagina", [])
        analisis_hibrido = obs_gen.analizar_vicios_hibrido(
            texto, analisis_ia, valor_referencial, texto_por_pagina
        )
        
        # DEBUG: Ver resultado híbrido
        vicios_hibrido = analisis_hibrido.get('vicios_detectados', [])
        print(f"🔷 Vicios del análisis híbrido: {len(vicios_hibrido)}")
        for v in vicios_hibrido[:5]:
            prob = v.get('probabilidad_acogimiento', 0)
            emoji = "🔴" if prob >= 0.7 else ("🟡" if prob >= 0.4 else "🟢")
            print(f"   {emoji} {v.get('tipo', 'N/A')}: {prob*100:.0f}%")
        
        return {
            "archivo": extraccion["archivo"],
            "paginas": extraccion["paginas"],
            "tipo_documento": tipo,
            "datos_extraidos": datos_basicos,
            "datos_cuantificables": datos_cuantificables,  # NUEVO: Incluir datos numéricos
            "analisis_ia": analisis_ia,
            "analisis_hibrido": analisis_hibrido,
            "vicios_detectados": vicios_hibrido,
            "observaciones_sugeridas": analisis_hibrido.get("observaciones_sugeridas", []),
            "procede_observar": analisis_hibrido.get("procede_formular_observaciones", False),
            "resumen": analisis_hibrido.get("resumen", ""),
            "texto_muestra": texto[:2000]
        }
    
    def detectar_vicios_bases(self, pdf_path: str) -> Dict:
        """
        Detecta vicios observables en las bases.
        VERSIÓN MEJORADA: Usa análisis híbrido con datos cuantificables.
        """
        extraccion = self.pdf_processor.extraer_texto_pdf(pdf_path)
        
        if "error" in extraccion:
            return extraccion
        
        texto = extraccion["texto_completo"]
        
        # Extraer datos cuantificables primero
        datos_cuantificables = self.pdf_processor._extraer_datos_cuantificables(texto)
        
        # Análisis de vicios con Gemini
        analisis_ia = self.pdf_processor.analizar_documento_gemini_sync(texto, "vicios")
        analisis_ia["datos_cuantificables"] = datos_cuantificables
        
        # Análisis híbrido
        from engine.observaciones import ObservacionesGenerator
        obs_gen = ObservacionesGenerator()
        
        valor_referencial = datos_cuantificables.get("valor_referencial")
        analisis_hibrido = obs_gen.analizar_vicios_hibrido(
            texto, analisis_ia, valor_referencial
        )
        
        return {
            "archivo": extraccion["archivo"],
            "datos_cuantificables": datos_cuantificables,
            "vicios_detectados": analisis_hibrido.get("vicios_detectados", []),
            "observaciones_sugeridas": analisis_hibrido.get("observaciones_sugeridas", []),
            "procede_observar": analisis_hibrido.get("procede_formular_observaciones", False),
            "resumen": analisis_hibrido.get("resumen", ""),
            "recomendacion": "Formular observaciones dentro del plazo del calendario" if analisis_hibrido.get("procede_formular_observaciones") else "Evaluar vicios de menor probabilidad"
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
            valor_ref = datos.get('valor_referencial')
            valor_ref_str = f"S/ {valor_ref:,.2f}" if isinstance(valor_ref, (int, float)) else "No identificado"
            respuesta += f"""📋 **DATOS EXTRAÍDOS:**
• Proceso: {datos.get('numero_proceso', 'No identificado')}
• Valor Referencial: {valor_ref_str}

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
