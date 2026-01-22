"""
Módulo de Observaciones a las Bases de Procedimientos de Selección
Ley N° 32069 - Arts. 51-52 del Reglamento D.S. N° 009-2025-EF

Este módulo permite:
1. Identificar vicios comunes en las bases
2. Generar observaciones formales con fundamento legal
3. Proponer modificaciones concretas
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import re


class ObservacionesGenerator:
    """
    Generador inteligente de observaciones a las bases
    según Arts. 51-52 del Reglamento de la Ley 32069
    """
    
    # =========================================================================
    # BASE DE DATOS DE VICIOS COMUNES EN BASES
    # =========================================================================
    
    VICIOS_REQUISITOS_CALIFICACION = {
        "experiencia_excesiva": {
            "descripcion": "Experiencia del postor excesiva o desproporcionada",
            "indicadores": [
                "experiencia mayor a 3 veces el valor referencial",
                "experiencia mayor a 5 años en el rubro",
                "número mínimo de contratos excesivo (más de 10)"
            ],
            "limite_legal": "Art. 29 del Reglamento: La experiencia no debe exceder el monto del valor referencial",
            "fundamento": """La experiencia del postor requerida resulta EXCESIVA y DESPROPORCIONADA 
respecto al objeto de la contratación, vulnerando el principio de LIBERTAD DE CONCURRENCIA 
(Art. 2, inc. 8 de la Ley 32069) y el Art. 29 del Reglamento que establece que los requisitos 
de calificación deben ser razonables y proporcionales al objeto del contrato.""",
            "jurisprudencia": [
                "Res. 1850-2025-TCE-S1: Requisitos de calificación excesivos que limitaban injustificadamente la participación",
                "Res. 2150-2025-TCE-S2: Factores de evaluación restrictivos"
            ]
        },
        
        "experiencia_personal_excesiva": {
            "descripcion": "Experiencia del personal clave excesiva",
            "indicadores": [
                "experiencia profesional mayor a 10 años",
                "número de obras/servicios similares excesivo",
                "títulos o certificaciones no requeridas por el mercado"
            ],
            "limite_legal": "Art. 29 del Reglamento: Proporcionalidad en requisitos de personal",
            "fundamento": """La experiencia exigida para el PERSONAL CLAVE resulta EXCESIVA y no guarda 
proporcionalidad con la complejidad del objeto contractual, restringiendo indebidamente 
la participación de postores calificados. El precedente TCE 2100-2025-TCE-SP establece que 
la experiencia del personal debe evaluarse al momento de presentación de ofertas con 
criterios razonables.""",
            "jurisprudencia": [
                "Res. 2100-2025-TCE-SP (Precedente Vinculante): Experiencia del personal clave se acredita al momento de la presentación de ofertas"
            ]
        },
        
        "certificaciones_restrictivas": {
            "descripcion": "Certificaciones o acreditaciones restrictivas",
            "indicadores": [
                "certificación ISO específica sin justificación",
                "certificaciones de un solo organismo",
                "acreditaciones no disponibles en el mercado peruano"
            ],
            "limite_legal": "Art. 16 Ley 32069: Especificaciones técnicas objetivas",
            "fundamento": """Las certificaciones o acreditaciones exigidas constituyen BARRERAS DE ACCESO 
al procedimiento, pues limitan la participación a proveedores específicos, vulnerando los 
principios de LIBERTAD DE CONCURRENCIA y COMPETENCIA (Arts. 2, incs. 8 y 10 de la Ley 32069).""",
            "jurisprudencia": []
        },
        
        "monto_facturacion_excesivo": {
            "descripcion": "Monto de facturación anual excesivo",
            "indicadores": [
                "facturación anual mayor a 3 veces el VR",
                "facturación de años específicos (no los últimos 3)",
                "facturación acumulada desproporcionada"
            ],
            "limite_legal": "Art. 29: Capacidad financiera proporcional",
            "fundamento": """El monto de facturación anual exigido NO guarda proporcionalidad con el 
valor referencial del procedimiento, constituyendo un requisito excesivo que restringe 
indebidamente la participación de MYPES y empresas con capacidad técnica pero menor 
volumen de operaciones.""",
            "jurisprudencia": []
        }
    }
    
    VICIOS_ESPECIFICACIONES_TECNICAS = {
        "marca_especifica": {
            "descripcion": "Referencia a marca específica sin 'o equivalente'",
            "indicadores": [
                "mención de marca sin alternativas",
                "modelo específico sin equivalencia",
                "características únicas de un fabricante"
            ],
            "limite_legal": "Art. 16 Ley 32069: Prohibición de referencia a marcas",
            "fundamento": """Las especificaciones técnicas hacen referencia a MARCA específica sin 
indicar 'O EQUIVALENTE', vulnerando el Art. 16 de la Ley 32069 que prohíbe expresamente 
la referencia a marcas, patentes o tipos que orienten la contratación hacia un proveedor.""",
            "jurisprudencia": []
        },
        
        "caracteristicas_direccionadas": {
            "descripcion": "Características técnicas que direccionan a proveedor único",
            "indicadores": [
                "combinación de características disponibles en un solo producto",
                "dimensiones exactas sin tolerancias",
                "especificaciones patentadas"
            ],
            "limite_legal": "Art. 2 inc. 10: Principio de Competencia",
            "fundamento": """Las especificaciones técnicas están DIRECCIONADAS a un producto o proveedor 
específico, vulnerando el principio de COMPETENCIA (Art. 2, inc. 10 de la Ley 32069), 
al no permitir la participación de productos equivalentes que satisfagan las necesidades 
de la Entidad.""",
            "jurisprudencia": []
        },
        
        "plazos_irreales": {
            "descripcion": "Plazos de ejecución irreales o imposibles",
            "indicadores": [
                "plazo de entrega menor a lo técnicamente viable",
                "plazo de ejecución de obra sin considerar clima",
                "tiempos de fabricación menores al estándar de mercado"
            ],
            "limite_legal": "Art. 16: Especificaciones objetivas y razonables",
            "fundamento": """El plazo de ejecución establecido resulta IRREAL e IMPOSIBLE de cumplir 
bajo estándares técnicos normales, lo cual evidencia una falta de estudio de mercado 
adecuado y puede constituir una estrategia para DIRECCIONAR la contratación.""",
            "jurisprudencia": []
        }
    }
    
    VICIOS_FACTORES_EVALUACION = {
        "factor_subjetivo": {
            "descripcion": "Factor de evaluación subjetivo o no medible",
            "indicadores": [
                "calidad sin criterios objetivos",
                "mejor propuesta técnica sin parámetros",
                "criterios de evaluación discrecionales"
            ],
            "limite_legal": "Art. 28 del Reglamento: Factores objetivos y medibles",
            "fundamento": """El factor de evaluación establecido carece de OBJETIVIDAD y MEDICIÓN 
cuantificable, lo cual vulnera el Art. 28 del Reglamento que exige que los factores 
de evaluación sean objetivos, razonables, congruentes y proporcionales.""",
            "jurisprudencia": []
        },
        
        "puntaje_experiencia_excesivo": {
            "descripcion": "Puntaje por experiencia que genera distorsión",
            "indicadores": [
                "más del 50% del puntaje técnico por experiencia",
                "experiencia que supera ampliamente el VR",
                "tabla de puntaje con saltos desproporcionados"
            ],
            "limite_legal": "Art. 28: Proporcionalidad en factores",
            "fundamento": """La metodología de evaluación del factor EXPERIENCIA genera una DISTORSIÓN 
significativa, pues otorga puntajes máximos a montos que exceden ampliamente el valor 
referencial, favoreciendo a empresas de mayor envergadura sin justificación técnica.""",
            "jurisprudencia": [
                "Res. 2150-2025-TCE-S2: Factores restrictivos y limitativos de la competencia"
            ]
        }
    }
    
    VICIOS_PENALIDADES = {
        "penalidad_excesiva": {
            "descripcion": "Penalidad por mora que supera límites legales",
            "indicadores": [
                "factor F mayor al establecido en el Art. 163",
                "penalidad diaria mayor al 0.10%",
                "causales de penalidad no previstas en la ley"
            ],
            "limite_legal": "Art. 163 del Reglamento: Fórmula de penalidad",
            "fundamento": """La penalidad por mora establecida EXCEDE los límites del Art. 163 del 
Reglamento (F=0.40 para plazos mayores a 60 días) y representa un riesgo contractual 
desproporcionado que afecta el precio de la oferta y limita la competencia.""",
            "jurisprudencia": []
        },
        
        "otras_penalidades_sin_base": {
            "descripcion": "Otras penalidades sin base legal o desproporcionadas",
            "indicadores": [
                "penalidades por incumplimientos menores",
                "monto fijo sin proporcionalidad",
                "causales ambiguas o subjetivas"
            ],
            "limite_legal": "Art. 163: Otras penalidades deben ser objetivas y razonables",
            "fundamento": """Las penalidades adicionales establecidas en las bases carecen de 
proporcionalidad y/o resultan ARBITRARIAS, pues no guardan relación con el perjuicio 
real que generaría su incumplimiento a la Entidad.""",
            "jurisprudencia": []
        }
    }
    
    VICIOS_GARANTIAS = {
        "garantia_excesiva": {
            "descripcion": "Monto de garantía que supera límites legales",
            "indicadores": [
                "garantía de fiel cumplimiento mayor al 10%",
                "garantía por adelantos mayor al monto del adelanto",
                "garantía técnica sin justificación"
            ],
            "limite_legal": "Art. 33 Ley 32069: Garantía de fiel cumplimiento = 10% del monto contractual",
            "fundamento": """La garantía exigida SUPERA los límites establecidos en el Art. 33 de la 
Ley 32069, que fija la garantía de fiel cumplimiento en el 10% del monto del contrato 
original.""",
            "jurisprudencia": []
        }
    }
    
    # =========================================================================
    # PLANTILLAS DE OBSERVACIÓN
    # =========================================================================
    
    PLANTILLA_OBSERVACION = """
═══════════════════════════════════════════════════════════════════════════════
                        FORMULACIÓN DE OBSERVACIONES
                    Procedimiento de Selección: {procedimiento}
                         N° {numero_proceso}
═══════════════════════════════════════════════════════════════════════════════

SEÑORES:
{entidad}

OBSERVANTE: {nombre_observante}
RUC: {ruc_observante}

═══════════════════════════════════════════════════════════════════════════════
                              OBSERVACIÓN N° {num_observacion}
═══════════════════════════════════════════════════════════════════════════════

I. ASPECTO OBSERVADO
─────────────────────────────────────────────────────────────────────────────────
{aspecto_observado}
{ubicacion_bases}

II. SUSTENTO DE LA OBSERVACIÓN
─────────────────────────────────────────────────────────────────────────────────
{fundamento}

III. BASE LEGAL
─────────────────────────────────────────────────────────────────────────────────
{base_legal}

IV. JURISPRUDENCIA APLICABLE
─────────────────────────────────────────────────────────────────────────────────
{jurisprudencia}

V. PEDIDO CONCRETO
─────────────────────────────────────────────────────────────────────────────────
{pedido_concreto}

VI. PROPUESTA DE MODIFICACIÓN
─────────────────────────────────────────────────────────────────────────────────
DICE:
{texto_actual}

DEBE DECIR:
{texto_propuesto}

═══════════════════════════════════════════════════════════════════════════════

Lugar y fecha: {lugar}, {fecha}

_______________________________
{nombre_observante}
{cargo}
"""
    
    def __init__(self):
        # Consolidar todos los vicios en un diccionario único
        self.vicios_db = {
            **self.VICIOS_REQUISITOS_CALIFICACION,
            **self.VICIOS_ESPECIFICACIONES_TECNICAS,
            **self.VICIOS_FACTORES_EVALUACION,
            **self.VICIOS_PENALIDADES,
            **self.VICIOS_GARANTIAS
        }
    
    # =========================================================================
    # MÉTODOS DE ANÁLISIS DE BASES
    # =========================================================================
    
    def analizar_requisito_experiencia(
        self,
        experiencia_requerida: float,
        valor_referencial: float,
        tipo: str = "postor"
    ) -> Dict:
        """
        Analiza si el requisito de experiencia es proporcional
        
        Args:
            experiencia_requerida: Monto de experiencia requerida
            valor_referencial: Valor referencial del proceso
            tipo: 'postor' o 'personal'
        """
        ratio = experiencia_requerida / valor_referencial if valor_referencial > 0 else 0
        
        # Límites recomendados según jurisprudencia
        limite_maximo = 1.0 if tipo == "postor" else 0.5
        limite_recomendado = 0.8 if tipo == "postor" else 0.3
        
        es_excesivo = ratio > limite_maximo
        es_alto = ratio > limite_recomendado
        
        resultado = {
            "experiencia_requerida": experiencia_requerida,
            "valor_referencial": valor_referencial,
            "ratio": round(ratio, 2),
            "limite_maximo": limite_maximo,
            "porcentaje_vr": f"{ratio * 100:.1f}%",
            "evaluacion": "EXCESIVO" if es_excesivo else ("ALTO" if es_alto else "RAZONABLE"),
            "procede_observacion": es_excesivo or es_alto
        }
        
        if es_excesivo or es_alto:
            resultado["observacion"] = self._generar_observacion_experiencia(
                experiencia_requerida, valor_referencial, ratio, tipo
            )
        
        return resultado
    
    def _generar_observacion_experiencia(
        self,
        experiencia: float,
        vr: float,
        ratio: float,
        tipo: str
    ) -> Dict:
        """Genera observación por experiencia excesiva"""
        
        vicio = self.VICIOS_REQUISITOS_CALIFICACION[
            "experiencia_excesiva" if tipo == "postor" else "experiencia_personal_excesiva"
        ]
        
        propuesta_monto = vr * (0.8 if tipo == "postor" else 0.3)
        
        return {
            "tipo_vicio": "experiencia_excesiva",
            "aspecto_observado": f"Requisito de experiencia del {tipo} - Monto: S/ {experiencia:,.2f}",
            "fundamento": vicio["fundamento"],
            "base_legal": vicio["limite_legal"],
            "jurisprudencia": vicio["jurisprudencia"],
            "pedido_concreto": f"Se solicita REDUCIR el requisito de experiencia a un monto proporcional al valor referencial",
            "texto_actual": f"Experiencia mínima: S/ {experiencia:,.2f}",
            "texto_propuesto": f"Experiencia mínima: S/ {propuesta_monto:,.2f} (equivalente al {0.8 if tipo == 'postor' else 0.3:.0%} del valor referencial)"
        }
    
    def analizar_plazo_ejecucion(
        self,
        plazo_dias: int,
        tipo_contratacion: str,
        complejidad: str = "media"
    ) -> Dict:
        """
        Analiza si el plazo de ejecución es razonable
        
        Args:
            plazo_dias: Plazo establecido en días
            tipo_contratacion: 'bienes', 'servicios', 'obras'
            complejidad: 'baja', 'media', 'alta'
        """
        # Plazos mínimos razonables según tipo y complejidad
        plazos_minimos = {
            "bienes": {"baja": 7, "media": 15, "alta": 30},
            "servicios": {"baja": 15, "media": 30, "alta": 60},
            "obras": {"baja": 60, "media": 120, "alta": 180}
        }
        
        plazo_minimo = plazos_minimos.get(tipo_contratacion, {}).get(complejidad, 30)
        
        es_irreal = plazo_dias < plazo_minimo * 0.5
        es_ajustado = plazo_dias < plazo_minimo
        
        return {
            "plazo_establecido": plazo_dias,
            "plazo_minimo_recomendado": plazo_minimo,
            "tipo_contratacion": tipo_contratacion,
            "complejidad": complejidad,
            "evaluacion": "IRREAL" if es_irreal else ("AJUSTADO" if es_ajustado else "RAZONABLE"),
            "procede_observacion": es_irreal,
            "observacion": self._generar_observacion_plazo(plazo_dias, plazo_minimo, tipo_contratacion) if es_irreal else None
        }
    
    def _generar_observacion_plazo(self, plazo_actual: int, plazo_minimo: int, tipo: str) -> Dict:
        """Genera observación por plazo irreal"""
        
        vicio = self.VICIOS_ESPECIFICACIONES_TECNICAS["plazos_irreales"]
        
        return {
            "tipo_vicio": "plazos_irreales",
            "aspecto_observado": f"Plazo de ejecución - {plazo_actual} días calendario",
            "fundamento": vicio["fundamento"],
            "base_legal": vicio["limite_legal"],
            "pedido_concreto": "Se solicita AMPLIAR el plazo de ejecución a un período técnicamente viable",
            "texto_actual": f"Plazo de ejecución: {plazo_actual} días calendario",
            "texto_propuesto": f"Plazo de ejecución: {plazo_minimo} días calendario"
        }
    
    def analizar_penalidad(
        self,
        penalidad_diaria: float,
        plazo_dias: int,
        monto_contrato: float
    ) -> Dict:
        """
        Analiza si la penalidad por mora es legal
        
        Args:
            penalidad_diaria: Porcentaje de penalidad diaria
            plazo_dias: Plazo del contrato
            monto_contrato: Monto del contrato
        """
        # Calcular F según Art. 163
        if plazo_dias <= 60:
            f_legal = 0.40
        elif plazo_dias <= 120:
            f_legal = 0.25
        else:
            f_legal = 0.15
        
        penalidad_legal = (0.10 * monto_contrato) / (f_legal * plazo_dias)
        penalidad_legal_porcentaje = (penalidad_legal / monto_contrato) * 100
        
        excede_limite = penalidad_diaria > penalidad_legal_porcentaje
        
        return {
            "penalidad_diaria_bases": f"{penalidad_diaria:.4f}%",
            "penalidad_legal_maxima": f"{penalidad_legal_porcentaje:.4f}%",
            "factor_f": f_legal,
            "plazo_dias": plazo_dias,
            "excede_limite_legal": excede_limite,
            "procede_observacion": excede_limite,
            "observacion": self._generar_observacion_penalidad(
                penalidad_diaria, penalidad_legal_porcentaje, f_legal, plazo_dias
            ) if excede_limite else None
        }
    
    def _generar_observacion_penalidad(
        self, 
        penalidad_bases: float, 
        penalidad_legal: float,
        factor_f: float,
        plazo: int
    ) -> Dict:
        """Genera observación por penalidad excesiva"""
        
        vicio = self.VICIOS_PENALIDADES["penalidad_excesiva"]
        
        return {
            "tipo_vicio": "penalidad_excesiva",
            "aspecto_observado": f"Penalidad por mora diaria: {penalidad_bases:.4f}%",
            "fundamento": vicio["fundamento"],
            "base_legal": f"{vicio['limite_legal']} - Factor F={factor_f} para plazo de {plazo} días",
            "pedido_concreto": "Se solicita AJUSTAR la penalidad por mora al límite establecido en el Art. 163 del Reglamento",
            "texto_actual": f"Penalidad diaria: {penalidad_bases:.4f}% del monto",
            "texto_propuesto": f"Penalidad diaria: {penalidad_legal:.4f}% del monto (según Art. 163, F={factor_f})"
        }
    
    def analizar_garantia(
        self,
        porcentaje_garantia: float,
        tipo_garantia: str = "fiel_cumplimiento"
    ) -> Dict:
        """
        Analiza si la garantía es legal
        
        Args:
            porcentaje_garantia: Porcentaje de garantía sobre el monto
            tipo_garantia: 'fiel_cumplimiento', 'adelanto'
        """
        limites = {
            "fiel_cumplimiento": 10.0,
            "adelanto": 100.0  # 100% del adelanto
        }
        
        limite = limites.get(tipo_garantia, 10.0)
        excede = porcentaje_garantia > limite
        
        return {
            "porcentaje_solicitado": f"{porcentaje_garantia}%",
            "limite_legal": f"{limite}%",
            "tipo_garantia": tipo_garantia,
            "excede_limite": excede,
            "procede_observacion": excede,
            "base_legal": "Art. 33 de la Ley 32069"
        }
    
    # =========================================================================
    # GENERACIÓN DE DOCUMENTO DE OBSERVACIÓN
    # =========================================================================
    
    def generar_documento_observacion(
        self,
        observacion: Dict,
        datos_proceso: Dict,
        datos_observante: Dict
    ) -> str:
        """
        Genera el documento formal de observación
        
        Args:
            observacion: Diccionario con datos de la observación
            datos_proceso: Datos del proceso (entidad, número, procedimiento)
            datos_observante: Datos del observante (nombre, RUC)
        """
        jurisprudencia_texto = "\n".join(
            [f"• {j}" for j in observacion.get("jurisprudencia", [])]
        ) or "• No se identificó jurisprudencia específica aplicable"
        
        documento = self.PLANTILLA_OBSERVACION.format(
            procedimiento=datos_proceso.get("procedimiento", "LICITACION PUBLICA"),
            numero_proceso=datos_proceso.get("numero", "N° XXX-2026"),
            entidad=datos_proceso.get("entidad", "[NOMBRE DE LA ENTIDAD]"),
            nombre_observante=datos_observante.get("nombre", "[NOMBRE DEL OBSERVANTE]"),
            ruc_observante=datos_observante.get("ruc", "[RUC]"),
            num_observacion=observacion.get("numero", "1"),
            aspecto_observado=observacion.get("aspecto_observado", ""),
            ubicacion_bases=observacion.get("ubicacion_bases", "Numeral X.X de las Bases"),
            fundamento=observacion.get("fundamento", ""),
            base_legal=observacion.get("base_legal", ""),
            jurisprudencia=jurisprudencia_texto,
            pedido_concreto=observacion.get("pedido_concreto", ""),
            texto_actual=observacion.get("texto_actual", ""),
            texto_propuesto=observacion.get("texto_propuesto", ""),
            lugar=datos_proceso.get("lugar", "Lima"),
            fecha=datetime.now().strftime("%d de %B de %Y"),
            cargo=datos_observante.get("cargo", "Representante Legal")
        )
        
        return documento
    
    def generar_multiples_observaciones(
        self,
        lista_observaciones: List[Dict],
        datos_proceso: Dict,
        datos_observante: Dict
    ) -> str:
        """Genera documento con múltiples observaciones"""
        
        documentos = []
        for i, obs in enumerate(lista_observaciones, 1):
            obs["numero"] = str(i)
            doc = self.generar_documento_observacion(obs, datos_proceso, datos_observante)
            documentos.append(doc)
        
        return "\n\n".join(documentos)
    
    # =========================================================================
    # DETECCIÓN AUTOMÁTICA DE VICIOS
    # =========================================================================
    
    def analizar_texto_bases(self, texto_bases: str) -> List[Dict]:
        """
        Analiza el texto de las bases para detectar posibles vicios
        
        Args:
            texto_bases: Texto extraído de las bases
            
        Returns:
            Lista de posibles vicios identificados
        """
        vicios_detectados = []
        texto_lower = texto_bases.lower()
        
        # Detectar marcas específicas
        patrones_marca = [
            r'marca\s*:\s*(\w+)',
            r'modelo\s*:\s*(\w+)',
            r'tipo\s*:\s*(\w+\s+\w+)'
        ]
        
        for patron in patrones_marca:
            matches = re.findall(patron, texto_lower)
            if matches and 'equivalente' not in texto_lower:
                vicios_detectados.append({
                    "tipo": "marca_especifica",
                    "detalle": f"Se menciona marca/modelo sin 'o equivalente'",
                    "severidad": "ALTA"
                })
                break
        
        # Detectar experiencia potencialmente excesiva
        patron_experiencia = r'experiencia\s+m[íi]nima.*?(\d+(?:,\d{3})*(?:\.\d{2})?)'
        matches = re.findall(patron_experiencia, texto_lower)
        if matches:
            for monto_str in matches:
                try:
                    monto = float(monto_str.replace(',', ''))
                    vicios_detectados.append({
                        "tipo": "experiencia_posible_excesiva",
                        "detalle": f"Experiencia mínima: S/ {monto:,.2f} - Verificar proporcionalidad",
                        "monto": monto,
                        "severidad": "MEDIA"
                    })
                except:
                    pass
        
        # Detectar plazos muy cortos
        patron_plazo = r'plazo.*?(\d+)\s*d[íi]as'
        matches = re.findall(patron_plazo, texto_lower)
        for plazo in matches:
            try:
                dias = int(plazo)
                if dias < 10:
                    vicios_detectados.append({
                        "tipo": "plazo_muy_corto",
                        "detalle": f"Plazo de {dias} días puede ser irreal",
                        "dias": dias,
                        "severidad": "ALTA"
                    })
            except:
                pass
        
        # Detectar penalidades potencialmente excesivas
        patron_penalidad = r'penalidad.*?(\d+(?:\.\d+)?)\s*%'
        matches = re.findall(patron_penalidad, texto_lower)
        for penalidad in matches:
            try:
                pct = float(penalidad)
                if pct > 0.1:  # mayor a 0.10%
                    vicios_detectados.append({
                        "tipo": "penalidad_alta",
                        "detalle": f"Penalidad del {pct}% puede exceder límite legal",
                        "porcentaje": pct,
                        "severidad": "MEDIA"
                    })
            except:
                pass
        
        return vicios_detectados
    
    # =========================================================================
    # ANÁLISIS HÍBRIDO IA + REGLAS
    # =========================================================================
    
    def analizar_vicios_hibrido(
        self, 
        texto_bases: str, 
        analisis_gemini: Dict,
        valor_referencial: Optional[float] = None
    ) -> Dict:
        """
        Combina análisis IA con validación de reglas legales para máxima precisión
        
        Args:
            texto_bases: Texto extraído del PDF de bases
            analisis_gemini: Resultado del análisis de Gemini
            valor_referencial: VR del proceso (para validaciones proporcionales)
            
        Returns:
            Dict con vicios validados, observaciones sugeridas y métricas
        """
        # 1. Obtener vicios detectados por IA
        vicios_ia = analisis_gemini.get("posibles_vicios", [])
        if not vicios_ia:
            vicios_ia = analisis_gemini.get("vicios", [])
        
        # 2. Obtener vicios detectados por reglas
        vicios_reglas = self.analizar_texto_bases(texto_bases)
        
        # 3. Fusionar y eliminar duplicados
        vicios_fusionados = self._fusionar_vicios(vicios_ia, vicios_reglas)
        
        # 4. Validar cada vicio contra reglas legales y calcular probabilidad
        vicios_validados = []
        for vicio in vicios_fusionados:
            vicio_validado = self._validar_vicio_contra_reglas(vicio, valor_referencial)
            vicio_validado["jurisprudencia"] = self._buscar_jurisprudencia(vicio_validado["tipo"])
            vicio_validado["probabilidad_acogimiento"] = self._calcular_probabilidad_acogimiento(vicio_validado)
            vicios_validados.append(vicio_validado)
        
        # 5. Ordenar por probabilidad de acogimiento
        vicios_validados.sort(key=lambda x: x["probabilidad_acogimiento"], reverse=True)
        
        # 6. Generar observaciones sugeridas para vicios de alta probabilidad
        observaciones_sugeridas = []
        for vicio in vicios_validados:
            if vicio["probabilidad_acogimiento"] >= 0.6:
                obs = self._generar_observacion_desde_vicio(vicio)
                observaciones_sugeridas.append(obs)
        
        return {
            "vicios_detectados": vicios_validados,
            "total_vicios": len(vicios_validados),
            "vicios_alta_probabilidad": len([v for v in vicios_validados if v["probabilidad_acogimiento"] >= 0.7]),
            "vicios_media_probabilidad": len([v for v in vicios_validados if 0.4 <= v["probabilidad_acogimiento"] < 0.7]),
            "vicios_baja_probabilidad": len([v for v in vicios_validados if v["probabilidad_acogimiento"] < 0.4]),
            "observaciones_sugeridas": observaciones_sugeridas,
            "procede_formular_observaciones": len(observaciones_sugeridas) > 0,
            "resumen": self._generar_resumen_analisis(vicios_validados)
        }
    
    def _fusionar_vicios(self, vicios_ia: List, vicios_reglas: List) -> List[Dict]:
        """Fusiona vicios de IA y reglas eliminando duplicados"""
        vicios_fusionados = []
        tipos_vistos = set()
        
        # Mapeo de tipos de IA a tipos internos
        mapeo_tipos = {
            "experiencia_excesiva": ["experiencia", "experiencia_postor", "experiencia_posible_excesiva"],
            "experiencia_personal_excesiva": ["personal", "experiencia_personal"],
            "marca_especifica": ["marca", "marca_especifica", "direccionamiento"],
            "plazos_irreales": ["plazo", "plazo_muy_corto", "plazo_irreal"],
            "penalidad_excesiva": ["penalidad", "penalidad_alta"],
            "certificaciones_restrictivas": ["certificacion", "iso", "acreditacion"],
            "caracteristicas_direccionadas": ["direccionamiento", "caracteristicas"]
        }
        
        # Procesar vicios de reglas (tienen prioridad por ser más precisos)
        for vicio in vicios_reglas:
            tipo_normalizado = vicio.get("tipo", "").lower()
            if tipo_normalizado not in tipos_vistos:
                tipos_vistos.add(tipo_normalizado)
                vicios_fusionados.append({
                    "tipo": tipo_normalizado,
                    "descripcion": vicio.get("detalle", vicio.get("descripcion", "")),
                    "severidad": vicio.get("severidad", "MEDIA"),
                    "fuente": "REGLAS",
                    "datos_extra": vicio
                })
        
        # Procesar vicios de IA (agregar solo si no existen)
        for vicio in vicios_ia:
            tipo_ia = vicio.get("tipo", "").lower()
            
            # Normalizar tipo de IA a tipo interno
            tipo_normalizado = tipo_ia
            for tipo_interno, aliases in mapeo_tipos.items():
                if any(alias in tipo_ia for alias in aliases):
                    tipo_normalizado = tipo_interno
                    break
            
            # Solo agregar si no existe
            es_duplicado = False
            for tipo_visto in tipos_vistos:
                if tipo_normalizado in tipo_visto or tipo_visto in tipo_normalizado:
                    es_duplicado = True
                    break
            
            if not es_duplicado:
                tipos_vistos.add(tipo_normalizado)
                vicios_fusionados.append({
                    "tipo": tipo_normalizado,
                    "descripcion": vicio.get("descripcion", ""),
                    "severidad": vicio.get("severidad", "MEDIA"),
                    "fuente": "IA",
                    "base_legal_ia": vicio.get("base_legal", ""),
                    "datos_extra": vicio
                })
        
        return vicios_fusionados
    
    def _validar_vicio_contra_reglas(self, vicio: Dict, valor_referencial: Optional[float]) -> Dict:
        """Valida un vicio detectado contra las reglas legales hardcodeadas"""
        tipo = vicio.get("tipo", "")
        vicio_validado = vicio.copy()
        
        # Buscar en base de datos de vicios
        vicio_db = self.vicios_db.get(tipo)
        
        if vicio_db:
            vicio_validado["validado_por_reglas"] = True
            vicio_validado["limite_legal"] = vicio_db.get("limite_legal", "")
            vicio_validado["fundamento_legal"] = vicio_db.get("fundamento", "")
            vicio_validado["indicadores"] = vicio_db.get("indicadores", [])
            # Aumentar severidad si está en nuestra BD
            if vicio.get("severidad") == "MEDIA":
                vicio_validado["severidad"] = "ALTA"
        else:
            vicio_validado["validado_por_reglas"] = False
            vicio_validado["limite_legal"] = vicio.get("base_legal_ia", "Revisar manualmente")
            vicio_validado["fundamento_legal"] = "Vicio detectado por IA - requiere validación manual"
        
        # Validaciones específicas con datos
        datos_extra = vicio.get("datos_extra", {})
        
        if "experiencia" in tipo and valor_referencial:
            monto = datos_extra.get("monto", 0)
            if monto:
                try:
                    monto_num = float(str(monto).replace(",", ""))
                    ratio = monto_num / valor_referencial
                    vicio_validado["ratio_vr"] = round(ratio, 2)
                    vicio_validado["excede_limite"] = ratio > 1.0
                    if ratio > 1.0:
                        vicio_validado["severidad"] = "ALTA"
                        vicio_validado["validado_por_reglas"] = True
                except:
                    pass
        
        return vicio_validado
    
    def _buscar_jurisprudencia(self, tipo_vicio: str) -> List[str]:
        """Busca jurisprudencia aplicable para el tipo de vicio"""
        jurisprudencia = []
        
        # Buscar en BD de vicios
        vicio_db = self.vicios_db.get(tipo_vicio)
        if vicio_db:
            jurisprudencia = vicio_db.get("jurisprudencia", [])
        
        # Jurisprudencia general aplicable
        jurisprudencia_general = {
            "experiencia": [
                "Res. 1850-2025-TCE-S1: Requisitos de calificación excesivos",
                "Res. 2150-2025-TCE-S2: Factores restrictivos de competencia"
            ],
            "plazo": [
                "Res. 1900-2025-TCE-S1: Plazos que no permiten participación efectiva"
            ],
            "marca": [
                "Res. 2000-2025-TCE-S2: Direccionamiento a proveedor específico"
            ],
            "penalidad": [
                "Res. 1750-2025-TCE-S1: Penalidades que exceden límites del Art. 163"
            ]
        }
        
        for keyword, juris in jurisprudencia_general.items():
            if keyword in tipo_vicio.lower() and not jurisprudencia:
                jurisprudencia = juris
                break
        
        return jurisprudencia if jurisprudencia else ["No se identificó jurisprudencia específica"]
    
    def _calcular_probabilidad_acogimiento(self, vicio: Dict) -> float:
        """
        Calcula la probabilidad de que la observación sea acogida
        basándose en múltiples factores
        """
        probabilidad = 0.3  # Base
        
        # +0.3 si está validado por reglas legales
        if vicio.get("validado_por_reglas"):
            probabilidad += 0.3
        
        # +0.2 si tiene jurisprudencia aplicable
        juris = vicio.get("jurisprudencia", [])
        if juris and juris[0] != "No se identificó jurisprudencia específica":
            probabilidad += 0.2
        
        # +0.15 por severidad ALTA
        if vicio.get("severidad") == "ALTA":
            probabilidad += 0.15
        elif vicio.get("severidad") == "MEDIA":
            probabilidad += 0.05
        
        # +0.1 si excede límite legal verificable
        if vicio.get("excede_limite"):
            probabilidad += 0.1
        
        # Ajustar por fuente
        if vicio.get("fuente") == "REGLAS":
            probabilidad += 0.05
        
        return min(probabilidad, 0.95)  # Máximo 95%
    
    def _generar_observacion_desde_vicio(self, vicio: Dict) -> Dict:
        """Genera una observación formal desde un vicio validado"""
        return {
            "tipo_vicio": vicio.get("tipo"),
            "aspecto_observado": vicio.get("descripcion", ""),
            "fundamento": vicio.get("fundamento_legal", ""),
            "base_legal": vicio.get("limite_legal", ""),
            "jurisprudencia": vicio.get("jurisprudencia", []),
            "severidad": vicio.get("severidad"),
            "probabilidad_acogimiento": vicio.get("probabilidad_acogimiento"),
            "validado": vicio.get("validado_por_reglas", False),
            "pedido_concreto": f"Se solicita modificar/eliminar el requisito observado por contravenir la Ley 32069",
            "texto_actual": vicio.get("datos_extra", {}).get("texto_actual", "[Revisar bases]"),
            "texto_propuesto": vicio.get("datos_extra", {}).get("texto_propuesto", "[Proponer modificación según Art. 51]")
        }
    
    def _generar_resumen_analisis(self, vicios: List[Dict]) -> str:
        """Genera resumen ejecutivo del análisis híbrido"""
        if not vicios:
            return "No se detectaron vicios observables en las bases."
        
        alta = len([v for v in vicios if v.get("probabilidad_acogimiento", 0) >= 0.7])
        media = len([v for v in vicios if 0.4 <= v.get("probabilidad_acogimiento", 0) < 0.7])
        baja = len([v for v in vicios if v.get("probabilidad_acogimiento", 0) < 0.4])
        
        resumen = f"Se detectaron {len(vicios)} posibles vicios: "
        resumen += f"{alta} de alta probabilidad de acogimiento, "
        resumen += f"{media} de media probabilidad, "
        resumen += f"{baja} de baja probabilidad. "
        
        if alta > 0:
            resumen += "SE RECOMIENDA FORMULAR OBSERVACIONES dentro del plazo establecido."
        elif media > 0:
            resumen += "Se sugiere evaluar la formulación de observaciones."
        else:
            resumen += "Los vicios detectados tienen baja probabilidad de acogimiento."
        
        return resumen
    
    def formatear_resultado_hibrido(self, resultado: Dict) -> str:
        """Formatea el resultado del análisis híbrido para chat"""
        vicios = resultado.get("vicios_detectados", [])
        
        if not vicios:
            return """✅ **ANÁLISIS HÍBRIDO DE BASES**

📊 **Resultado:** No se detectaron vicios observables.

Las bases analizadas no presentan irregularidades significativas según:
• Análisis de Inteligencia Artificial (Gemini)
• Validación contra reglas de la Ley 32069

📚 *Análisis realizado con el motor híbrido IA + Reglas*"""
        
        respuesta = f"""⚠️ **ANÁLISIS HÍBRIDO DE BASES - {len(vicios)} VICIOS DETECTADOS**

📊 **Métricas:**
• 🔴 Alta probabilidad: {resultado.get('vicios_alta_probabilidad', 0)}
• 🟡 Media probabilidad: {resultado.get('vicios_media_probabilidad', 0)}  
• 🟢 Baja probabilidad: {resultado.get('vicios_baja_probabilidad', 0)}

"""
        
        for i, vicio in enumerate(vicios[:5], 1):  # Mostrar máximo 5
            prob = vicio.get("probabilidad_acogimiento", 0)
            emoji = "🔴" if prob >= 0.7 else ("🟡" if prob >= 0.4 else "🟢")
            validado = "✓ Validado" if vicio.get("validado_por_reglas") else "⚡ Solo IA"
            
            respuesta += f"""**{i}. {vicio.get('tipo', 'N/A').upper()}** {emoji}
   • Probabilidad: {prob*100:.0f}%
   • Severidad: {vicio.get('severidad', 'N/A')}
   • Estado: {validado}
   • Base legal: {vicio.get('limite_legal', 'N/A')[:80]}...

"""
        
        respuesta += f"""📝 **Resumen:** {resultado.get('resumen', '')}

💡 **Observaciones sugeridas:** {len(resultado.get('observaciones_sugeridas', []))}

📚 *Motor híbrido: Gemini AI + Reglas Ley 32069 + Jurisprudencia TCE*"""
        
        return respuesta
    
    # =========================================================================
    # FORMATEO PARA CHAT
    # =========================================================================
    
    def formatear_resultado_analisis(self, resultado: Dict) -> str:
        """Formatea resultado de análisis para chat"""
        
        if not resultado.get("procede_observacion"):
            return f"""✅ **ANÁLISIS DE BASES**

📋 **Aspecto evaluado:** {resultado.get('tipo', 'General')}
📊 **Resultado:** RAZONABLE

No se identificaron vicios que ameriten observación formal.

📚 *Análisis según Ley 32069 y Reglamento D.S. 009-2025-EF*"""
        
        obs = resultado.get("observacion", {})
        
        return f"""⚠️ **SE DETECTÓ POSIBLE VICIO EN LAS BASES**

📋 **Aspecto observado:**
{obs.get('aspecto_observado', 'N/A')}

⚖️ **Fundamento legal:**
{obs.get('base_legal', 'N/A')}

📝 **Fundamento técnico:**
{obs.get('fundamento', 'N/A')[:300]}...

✏️ **Propuesta de modificación:**
• DICE: {obs.get('texto_actual', 'N/A')}
• DEBE DECIR: {obs.get('texto_propuesto', 'N/A')}

💡 **Recomendación:**
FORMULAR OBSERVACIÓN dentro del plazo establecido en el calendario del proceso.

📚 *Base legal: Art. 51-52 del Reglamento D.S. 009-2025-EF*"""
    
    def detect_and_analyze(self, message: str) -> Optional[str]:
        """Detecta si el mensaje es consulta sobre observaciones"""
        message_lower = message.lower()
        
        keywords = ['observación', 'observacion', 'observar', 'bases', 'vicio', 
                    'experiencia excesiva', 'requisito excesivo', 'penalidad alta',
                    'plazo irreal', 'marca específica']
        
        if not any(kw in message_lower for kw in keywords):
            return None
        
        # Si es consulta general, dar información
        if any(kw in message_lower for kw in ['cómo', 'como', 'qué', 'que', 'cuándo', 'cuando']):
            return get_observaciones_info()
        
        return None


def get_observaciones_info() -> str:
    """Información general sobre observaciones a las bases"""
    return """📝 **OBSERVACIONES A LAS BASES**

**Base Legal:** Arts. 51-52 del D.S. N° 009-2025-EF

**¿Qué son?**
Son cuestionamientos formales que los participantes pueden formular contra las bases de un procedimiento de selección cuando contienen vicios o regulaciones ilegales.

**Plazo para formular:**
Según el calendario del procedimiento, usualmente:
• **Licitación/Concurso Público:** 10 días hábiles
• **Procedimiento Abreviado:** 5 días hábiles

**Vicios más comunes:**
1. ❌ Experiencia del postor excesiva
2. ❌ Experiencia del personal desproporcionada
3. ❌ Marcas o modelos específicos sin equivalentes
4. ❌ Plazos de ejecución irreales
5. ❌ Penalidades que exceden límites legales
6. ❌ Factores de evaluación subjetivos
7. ❌ Garantías mayores al 10%

**¿Qué debe contener?**
• Aspecto observado
• Fundamento (de hecho y de derecho)
• Pedido concreto
• Propuesta de modificación

**Si no son acogidas:**
Se puede ELEVAR al OECE para que emita pronunciamiento.

📚 *Base legal: Arts. 51-52 del Reglamento*

💡 **Para analizar una base específica, indique:**
• Monto de experiencia requerida vs valor referencial
• Plazo de ejecución y tipo de contratación
• Penalidades establecidas"""
