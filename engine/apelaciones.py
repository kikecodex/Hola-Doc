"""
Módulo Generador de Recursos de Apelación
Ley N° 32069 - Arts. 97-103 del Reglamento D.S. N° 009-2025-EF

Este módulo permite:
1. Calcular automáticamente tasa, plazo e instancia
2. Generar recursos de apelación con fundamentos completos
3. Proporcionar plantillas por tipo de impugnación
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import re


class ApelacionesGenerator:
    """
    Generador inteligente de recursos de apelación
    según Arts. 97-103 del Reglamento de la Ley 32069
    """
    
    # =========================================================================
    # CONSTANTES LEGALES
    # =========================================================================
    
    TOPE_RESOLUCION_ENTIDAD = 485000  # < S/ 485,000 resuelve Entidad
    TASA_PORCENTAJE = 0.03  # 3% del valor referencial
    TASA_MINIMA_ENTIDAD = 150  # S/ 150
    TASA_MINIMA_TRIBUNAL = 1100  # S/ 1,100
    PLAZO_INTERPOSICION = 8  # días hábiles
    
    # =========================================================================
    # TIPOS DE APELACIÓN Y SUS FUNDAMENTOS
    # =========================================================================
    
    TIPOS_APELACION = {
        "descalificacion_indebida": {
            "titulo": "DESCALIFICACIÓN INDEBIDA DE PROPUESTA",
            "descripcion": "Cuando la propuesta fue descalificada sin fundamento legal válido",
            "fundamentos_tipicos": [
                "Descalificación por error formal subsanable",
                "Descalificación por requisito no establecido en bases",
                "Descalificación sin motivación adecuada",
                "Desestimación de documentos válidos",
                "No aplicación del principio de presunción de veracidad"
            ],
            "base_legal_principal": [
                "Art. 2 inc. 5 Ley 32069 - Principio de Presunción de Veracidad",
                "Art. 52 del Reglamento - Evaluación de propuestas",
                "Res. 0003-2026-TCE-S3 - Error formal subsanable"
            ],
            "petitorio_tipo": "Se declare NULA la descalificación de mi propuesta y se ordene retrotraer el procedimiento a la etapa de evaluación"
        },
        
        "error_evaluacion_tecnica": {
            "titulo": "ERROR EN LA EVALUACIÓN TÉCNICA",
            "descripcion": "Cuando existe error en el cálculo de puntajes técnicos",
            "fundamentos_tipicos": [
                "Error aritmético en cálculo de puntajes",
                "No valoración de documentos presentados",
                "Aplicación errónea de factores de evaluación",
                "Incumplimiento de metodología de evaluación",
                "Tratamiento desigual entre postores"
            ],
            "base_legal_principal": [
                "Art. 2 inc. 11 Ley 32069 - Principio de Igualdad de Trato",
                "Art. 77-78 del Reglamento - Evaluación de propuestas",
                "Art. 28 del Reglamento - Factores de evaluación"
            ],
            "petitorio_tipo": "Se declare FUNDADA la apelación, se CORRIJA el puntaje técnico de mi propuesta y se me otorgue la buena pro"
        },
        
        "error_evaluacion_economica": {
            "titulo": "ERROR EN LA EVALUACIÓN ECONÓMICA",
            "descripcion": "Cuando existe error en el cálculo del puntaje económico",
            "fundamentos_tipicos": [
                "Error en aplicación de fórmula del Art. 78",
                "Conversión errónea de moneda",
                "No consideración de propuesta económica válida",
                "Error aritmético en cálculo de precios"
            ],
            "base_legal_principal": [
                "Art. 78 del Reglamento - Evaluación económica",
                "Art. 2 inc. 2 Ley 32069 - Principio de Eficacia y Eficiencia"
            ],
            "petitorio_tipo": "Se declare FUNDADA la apelación, se RECALCULE el puntaje económico conforme al Art. 78 del Reglamento"
        },
        
        "vicios_procedimiento": {
            "titulo": "VICIOS EN EL PROCEDIMIENTO DE SELECCIÓN",
            "descripcion": "Cuando existen irregularidades procesales que afectan la validez",
            "fundamentos_tipicos": [
                "Incumplimiento de plazos del procedimiento",
                "Falta de notificación de actos",
                "Irregularidades en instalación del comité",
                "No absolución de consultas u observaciones",
                "Modificación de bases sin procedimiento"
            ],
            "base_legal_principal": [
                "Art. 2 inc. 1 Ley 32069 - Principio de Legalidad",
                "Art. 72 Ley 32069 - Causales de nulidad",
                "Art. 51-52 del Reglamento - Consultas y observaciones"
            ],
            "petitorio_tipo": "Se declare NULO el procedimiento de selección y se ordene retrotraer a la etapa afectada"
        },
        
        "requisitos_restrictivos": {
            "titulo": "REQUISITOS DE CALIFICACIÓN RESTRICTIVOS",
            "descripcion": "Cuando las bases contienen requisitos que limitan indebidamente la participación",
            "fundamentos_tipicos": [
                "Experiencia desproporcionada al objeto",
                "Requisitos técnicos direccionados",
                "Certificaciones no justificadas",
                "Plazos imposibles de cumplir"
            ],
            "base_legal_principal": [
                "Art. 2 inc. 8 Ley 32069 - Libertad de Concurrencia",
                "Art. 2 inc. 10 Ley 32069 - Competencia",
                "Art. 29 del Reglamento - Requisitos de calificación",
                "Res. 1850-2025-TCE-S1 - Requisitos restrictivos"
            ],
            "petitorio_tipo": "Se declare NULAS las bases en los extremos observados y se ordene su reformulación conforme a ley"
        },
        
        "otorgamiento_buena_pro_indebida": {
            "titulo": "OTORGAMIENTO INDEBIDO DE LA BUENA PRO",
            "descripcion": "Cuando la buena pro fue otorgada a postor que no debía ganar",
            "fundamentos_tipicos": [
                "El ganador no cumplía requisitos de calificación",
                "El ganador presentó documentación falsa o inexacta",
                "El ganador está impedido de contratar",
                "Error en determinación del orden de prelación"
            ],
            "base_legal_principal": [
                "Art. 11 Ley 32069 - Impedimentos",
                "Art. 29 del Reglamento - Requisitos de calificación",
                "Art. 74 Ley 32069 - Infracciones"
            ],
            "petitorio_tipo": "Se declare NULA la buena pro otorgada y se determine nuevo ganador conforme al orden de prelación"
        }
    }
    
    # =========================================================================
    # PLANTILLA DE RECURSO DE APELACIÓN
    # =========================================================================
    
    PLANTILLA_APELACION = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                        RECURSO DE APELACIÓN                                   ║
║                 Procedimiento de Selección N° {numero_proceso}                ║
╚══════════════════════════════════════════════════════════════════════════════╝

SEÑORES:
{instancia_resolutora}
{direccion_instancia}

═══════════════════════════════════════════════════════════════════════════════
                              SUMILLA
═══════════════════════════════════════════════════════════════════════════════

APELANTE      : {nombre_apelante}
RUC           : {ruc_apelante}
DOMICILIO     : {domicilio_apelante}
CORREO        : {correo_apelante}

PROCEDIMIENTO : {tipo_procedimiento} N° {numero_proceso}
ENTIDAD       : {entidad}
OBJETO        : {objeto_contratacion}
VALOR REF.    : S/ {valor_referencial:,.2f}

ACTO IMPUGNADO: {acto_impugnado}
FECHA ACTO    : {fecha_acto}

TASA PAGADA   : S/ {tasa_apelacion:,.2f}

═══════════════════════════════════════════════════════════════════════════════
                              I. PETITORIO
═══════════════════════════════════════════════════════════════════════════════

{petitorio}

═══════════════════════════════════════════════════════════════════════════════
                     II. FUNDAMENTOS DE HECHO
═══════════════════════════════════════════════════════════════════════════════

1. ANTECEDENTES DEL PROCEDIMIENTO:
───────────────────────────────────────────────────────────────────────────────
{antecedentes}

2. DEL ACTO IMPUGNADO:
───────────────────────────────────────────────────────────────────────────────
{descripcion_acto_impugnado}

3. DE LOS AGRAVIOS CAUSADOS:
───────────────────────────────────────────────────────────────────────────────
{agravios}

═══════════════════════════════════════════════════════════════════════════════
                    III. FUNDAMENTOS DE DERECHO
═══════════════════════════════════════════════════════════════════════════════

{fundamentos_derecho}

═══════════════════════════════════════════════════════════════════════════════
                    IV. MEDIOS PROBATORIOS
═══════════════════════════════════════════════════════════════════════════════

{medios_probatorios}

═══════════════════════════════════════════════════════════════════════════════
                         V. ANEXOS
═══════════════════════════════════════════════════════════════════════════════

1-A  : Copia del DNI del representante legal
1-B  : Vigencia de poder del representante legal
1-C  : Ficha RUC
1-D  : Comprobante de pago de tasa de apelación (S/ {tasa_apelacion:,.2f})
1-E  : Copia de la propuesta técnica presentada
1-F  : Copia de la propuesta económica presentada
1-G  : Acta de otorgamiento de buena pro
1-H  : Bases integradas del procedimiento
{anexos_adicionales}

═══════════════════════════════════════════════════════════════════════════════

POR TANTO:
Solicito a ustedes se sirvan admitir el presente recurso de apelación, tramitarlo 
conforme a ley y, en su oportunidad, declararlo FUNDADO.

OTROSI DIGO: Que, autorizo a {nombre_abogado} identificado con CAL N° {colegiatura} 
para que realice el seguimiento del presente recurso.

{lugar}, {fecha}

_______________________________
{nombre_apelante}
RUC: {ruc_apelante}
"""

    # =========================================================================
    # FERIADOS PERU 2026 (para cálculo de plazos)
    # =========================================================================
    
    FERIADOS_2026 = [
        datetime(2026, 1, 1),   # Año Nuevo
        datetime(2026, 4, 2),   # Jueves Santo
        datetime(2026, 4, 3),   # Viernes Santo
        datetime(2026, 5, 1),   # Día del Trabajo
        datetime(2026, 6, 29),  # San Pedro y San Pablo
        datetime(2026, 7, 28),  # Fiestas Patrias
        datetime(2026, 7, 29),  # Fiestas Patrias
        datetime(2026, 8, 6),   # Batalla de Junín
        datetime(2026, 8, 30),  # Santa Rosa de Lima
        datetime(2026, 10, 8),  # Combate de Angamos
        datetime(2026, 11, 1),  # Todos los Santos
        datetime(2026, 12, 8),  # Inmaculada Concepción
        datetime(2026, 12, 9),  # Batalla de Ayacucho
        datetime(2026, 12, 25), # Navidad
    ]
    
    def __init__(self):
        pass
    
    # =========================================================================
    # CÁLCULOS DE APELACIÓN
    # =========================================================================
    
    def calcular_tasa_y_competencia(self, valor_referencial: float) -> Dict:
        """
        Calcula la tasa de apelación y determina la instancia competente
        
        Args:
            valor_referencial: Valor referencial del proceso
            
        Returns:
            Dict con tasa, instancia y detalles
        """
        # Determinar instancia
        if valor_referencial < self.TOPE_RESOLUCION_ENTIDAD:
            instancia = "Titular de la Entidad"
            tasa_minima = self.TASA_MINIMA_ENTIDAD
            plazo_resolucion = 12
            direccion = "[DIRECCIÓN DE LA ENTIDAD]"
        else:
            instancia = "Tribunal de Contrataciones del Estado"
            tasa_minima = self.TASA_MINIMA_TRIBUNAL
            plazo_resolucion = 20
            direccion = "Av. La Poesía 155, San Borja, Lima"
        
        # Calcular tasa (3% del VR)
        tasa_calculada = valor_referencial * self.TASA_PORCENTAJE
        
        # Aplicar mínimo
        tasa_aplicable = max(tasa_calculada, tasa_minima)
        
        return {
            "valor_referencial": valor_referencial,
            "tasa_calculada": round(tasa_calculada, 2),
            "tasa_minima": tasa_minima,
            "tasa_a_pagar": round(tasa_aplicable, 2),
            "instancia_resolutora": instancia,
            "direccion_instancia": direccion,
            "plazo_interposicion_dias": self.PLAZO_INTERPOSICION,
            "plazo_resolucion_dias": plazo_resolucion,
            "efecto": "Suspende el procedimiento de selección",
            "base_legal": "Arts. 97-103 del D.S. N° 009-2025-EF"
        }
    
    def calcular_plazo_limite(
        self,
        fecha_notificacion: str,
        formato: str = "%d/%m/%Y"
    ) -> Dict:
        """
        Calcula la fecha límite para interponer apelación (8 días hábiles)
        
        Args:
            fecha_notificacion: Fecha de notificación del acto impugnado
            formato: Formato de la fecha
        """
        try:
            fecha_inicio = datetime.strptime(fecha_notificacion, formato)
        except ValueError:
            try:
                fecha_inicio = datetime.strptime(fecha_notificacion, "%Y-%m-%d")
            except:
                return {"error": "Formato de fecha inválido. Use DD/MM/YYYY"}
        
        dias_contados = 0
        fecha_actual = fecha_inicio
        
        while dias_contados < self.PLAZO_INTERPOSICION:
            fecha_actual += timedelta(days=1)
            
            # Saltar fines de semana
            if fecha_actual.weekday() >= 5:
                continue
            
            # Saltar feriados
            if fecha_actual in self.FERIADOS_2026:
                continue
            
            dias_contados += 1
        
        dias_restantes = (fecha_actual - datetime.now()).days
        
        return {
            "fecha_notificacion": fecha_inicio.strftime("%d/%m/%Y"),
            "fecha_limite_apelacion": fecha_actual.strftime("%d/%m/%Y"),
            "dias_habiles_plazo": self.PLAZO_INTERPOSICION,
            "dias_calendario_restantes": max(0, dias_restantes),
            "estado": "VENCIDO" if dias_restantes < 0 else ("URGENTE" if dias_restantes <= 2 else "VIGENTE"),
            "base_legal": "Art. 97 del Reglamento"
        }
    
    # =========================================================================
    # GENERACIÓN DE FUNDAMENTOS LEGALES
    # =========================================================================
    
    def generar_fundamentos_derecho(self, tipo_apelacion: str, detalles: Dict = None) -> str:
        """
        Genera los fundamentos de derecho para el tipo de apelación
        
        Args:
            tipo_apelacion: Tipo de apelación (ver TIPOS_APELACION)
            detalles: Detalles adicionales para personalizar
        """
        tipo_info = self.TIPOS_APELACION.get(tipo_apelacion, {})
        
        bases_legales = tipo_info.get("base_legal_principal", [])
        fundamentos = tipo_info.get("fundamentos_tipicos", [])
        
        texto = f"""
A. DEL DERECHO A IMPUGNAR (Art. 97 del Reglamento):
───────────────────────────────────────────────────────────────────────────────
Conforme al Art. 97 del Reglamento de la Ley 32069, los postores tienen derecho 
a interponer recurso de apelación contra los actos dictados desde la convocatoria 
hasta aquellos emitidos antes de la celebración del contrato, inclusive.

B. DE LA VULNERACIÓN DE NORMAS:
───────────────────────────────────────────────────────────────────────────────
"""
        
        for i, base in enumerate(bases_legales, 1):
            texto += f"\n{i}. {base}\n"
        
        texto += """
C. DE LOS PRINCIPIOS VULNERADOS:
───────────────────────────────────────────────────────────────────────────────
"""
        
        # Agregar principios según tipo
        principios = {
            "descalificacion_indebida": [
                ("Presunción de Veracidad", "Art. 2 inc. 5", "Se debe presumir que los documentos y declaraciones presentados son verídicos"),
                ("Legalidad", "Art. 2 inc. 1", "Los actos deben sujetarse a normas expresas")
            ],
            "error_evaluacion_tecnica": [
                ("Igualdad de Trato", "Art. 2 inc. 11", "Todos los postores deben ser evaluados con los mismos criterios"),
                ("Eficacia y Eficiencia", "Art. 2 inc. 2", "Se debe buscar el mejor resultado")
            ],
            "vicios_procedimiento": [
                ("Legalidad", "Art. 2 inc. 1", "Todo acto debe sujetarse a ley"),
                ("Transparencia", "Art. 2 inc. 9", "Procedimientos claros e imparciales")
            ],
            "requisitos_restrictivos": [
                ("Libertad de Concurrencia", "Art. 2 inc. 8", "No se debe restringir indebidamente la participación"),
                ("Competencia", "Art. 2 inc. 10", "Promover mayor participación de postores")
            ]
        }
        
        for nombre, articulo, descripcion in principios.get(tipo_apelacion, []):
            texto += f"""
• PRINCIPIO DE {nombre.upper()} ({articulo} de la Ley 32069):
  {descripcion}
"""
        
        texto += """
D. DE LA JURISPRUDENCIA APLICABLE:
───────────────────────────────────────────────────────────────────────────────
"""
        
        jurisprudencia = {
            "descalificacion_indebida": [
                "Res. 0003-2026-TCE-S3: Error formal subsanable no amerita descalificación",
                "Res. 2340-2025-TCE-SP (Precedente): Errores formales pueden ser subsanados"
            ],
            "error_evaluacion_tecnica": [
                "Res. 2100-2025-TCE-SP (Precedente): La experiencia se evalúa objetivamente"
            ],
            "requisitos_restrictivos": [
                "Res. 1850-2025-TCE-S1: Requisitos que limitan participación son nulos",
                "Res. 2150-2025-TCE-S2: Factores restrictivos afectan competencia"
            ]
        }
        
        for j in jurisprudencia.get(tipo_apelacion, ["No se identificó jurisprudencia específica"]):
            texto += f"• {j}\n"
        
        return texto
    
    # =========================================================================
    # GENERACIÓN DE DOCUMENTO COMPLETO
    # =========================================================================
    
    def generar_recurso_apelacion(
        self,
        tipo_apelacion: str,
        datos_proceso: Dict,
        datos_apelante: Dict,
        datos_impugnacion: Dict
    ) -> str:
        """
        Genera el recurso de apelación completo
        
        Args:
            tipo_apelacion: Tipo de apelación
            datos_proceso: Datos del proceso (VR, número, entidad, etc.)
            datos_apelante: Datos del apelante
            datos_impugnacion: Datos del acto impugnado y fundamentos
        """
        # Calcular tasa y competencia
        vr = datos_proceso.get("valor_referencial", 0)
        calculo_tasa = self.calcular_tasa_y_competencia(vr)
        
        # Obtener tipo de apelación
        tipo_info = self.TIPOS_APELACION.get(tipo_apelacion, self.TIPOS_APELACION["descalificacion_indebida"])
        
        # Generar fundamentos de derecho
        fundamentos_derecho = self.generar_fundamentos_derecho(tipo_apelacion)
        
        # Generar petitorio
        petitorio = datos_impugnacion.get("petitorio", tipo_info["petitorio_tipo"])
        
        # Generar medios probatorios
        medios_probatorios = datos_impugnacion.get("medios_probatorios", """
1. Mérito de las bases integradas del procedimiento
2. Mérito de la propuesta técnica y económica presentada
3. Mérito del acta de otorgamiento de buena pro
4. Mérito del cuadro comparativo de evaluación
5. Demás documentos que obran en el expediente del procedimiento
""")
        
        # Anexos adicionales
        anexos_adicionales = ""
        for i, anexo in enumerate(datos_impugnacion.get("anexos", []), 9):
            anexos_adicionales += f"1-{chr(64+i)}  : {anexo}\n"
        
        # Generar documento
        documento = self.PLANTILLA_APELACION.format(
            numero_proceso=datos_proceso.get("numero", "N° XXX-2026"),
            instancia_resolutora=calculo_tasa["instancia_resolutora"],
            direccion_instancia=calculo_tasa["direccion_instancia"],
            nombre_apelante=datos_apelante.get("nombre", "[NOMBRE DEL APELANTE]"),
            ruc_apelante=datos_apelante.get("ruc", "[RUC]"),
            domicilio_apelante=datos_apelante.get("domicilio", "[DOMICILIO PROCESAL]"),
            correo_apelante=datos_apelante.get("correo", "[correo@email.com]"),
            tipo_procedimiento=datos_proceso.get("tipo", "LICITACION PUBLICA"),
            entidad=datos_proceso.get("entidad", "[NOMBRE DE LA ENTIDAD]"),
            objeto_contratacion=datos_proceso.get("objeto", "[OBJETO DE LA CONTRATACIÓN]"),
            valor_referencial=vr,
            acto_impugnado=datos_impugnacion.get("acto_impugnado", tipo_info["titulo"]),
            fecha_acto=datos_impugnacion.get("fecha_acto", datetime.now().strftime("%d/%m/%Y")),
            tasa_apelacion=calculo_tasa["tasa_a_pagar"],
            petitorio=f"""
Interpongo RECURSO DE APELACIÓN contra el acto que dispone {datos_impugnacion.get('descripcion_breve', 'la descalificación de mi propuesta')}, 
emitido en el procedimiento de selección de la referencia, solicitando:

PRINCIPAL:
{petitorio}

ACCESORIO:
Se disponga la devolución de la tasa de apelación en caso de declararse fundado el recurso.
""",
            antecedentes=datos_impugnacion.get("antecedentes", """
Con fecha XX de XX de 2026, la Entidad convocó el procedimiento de selección de la 
referencia para la contratación de [OBJETO].

El recurrente participó en el procedimiento, presentando su propuesta técnica y 
económica dentro del plazo establecido en el calendario.

Con fecha XX de XX de 2026, el Comité de Selección procedió a evaluar las propuestas 
y emitió el acto materia de impugnación.
"""),
            descripcion_acto_impugnado=datos_impugnacion.get("descripcion_acto", f"""
El acto impugnado consiste en {tipo_info['descripcion'].lower()}.

El citado acto adolece de los siguientes vicios:
""" + "\n".join([f"• {f}" for f in tipo_info["fundamentos_tipicos"][:3]])),
            agravios=datos_impugnacion.get("agravios", """
El acto impugnado causa los siguientes agravios al recurrente:

a) AGRAVIO ECONÓMICO: La imposibilidad de participar en la contratación representa 
   una pérdida económica significativa, considerando los costos incurridos en la 
   preparación de la propuesta.

b) AGRAVIO JURÍDICO: La decisión vulnera los principios de la contratación pública 
   y afecta el derecho del recurrente a competir en igualdad de condiciones.

c) AGRAVIO INSTITUCIONAL: El proceder de la Entidad afecta la confianza de los 
   proveedores en el sistema de contratación pública.
"""),
            fundamentos_derecho=fundamentos_derecho,
            medios_probatorios=medios_probatorios,
            anexos_adicionales=anexos_adicionales,
            nombre_abogado=datos_apelante.get("abogado", "[NOMBRE DEL ABOGADO]"),
            colegiatura=datos_apelante.get("colegiatura", "[N° CAL]"),
            lugar=datos_proceso.get("lugar", "Lima"),
            fecha=datetime.now().strftime("%d de %B de %Y")
        )
        
        return documento
    
    # =========================================================================
    # OBTENER LISTA DE TIPOS
    # =========================================================================
    
    def obtener_tipos_apelacion(self) -> List[Dict]:
        """Retorna la lista de tipos de apelación disponibles"""
        return [
            {
                "codigo": codigo,
                "titulo": info["titulo"],
                "descripcion": info["descripcion"]
            }
            for codigo, info in self.TIPOS_APELACION.items()
        ]
    
    # =========================================================================
    # FORMATEO PARA CHAT
    # =========================================================================
    
    def formatear_calculo_apelacion(self, resultado: Dict) -> str:
        """Formatea el resultado de cálculo para chat"""
        
        return f"""⚖️ **CÁLCULO DE RECURSO DE APELACIÓN**

📋 **Datos del proceso:**
• Valor Referencial: S/ {resultado['valor_referencial']:,.2f}

💰 **Tasa de apelación:**
• Tasa calculada (3%): S/ {resultado['tasa_calculada']:,.2f}
• Tasa mínima aplicable: S/ {resultado['tasa_minima']:,.2f}
• **TASA A PAGAR: S/ {resultado['tasa_a_pagar']:,.2f}**

🏛️ **Instancia competente:**
• **{resultado['instancia_resolutora']}**
• Dirección: {resultado['direccion_instancia']}

⏱️ **Plazos:**
• Plazo para apelar: **{resultado['plazo_interposicion_dias']} días hábiles**
• Plazo para resolver: **{resultado['plazo_resolucion_dias']} días hábiles**

⚠️ **Efecto:** {resultado['efecto']}

📚 *Base legal: {resultado['base_legal']}*"""
    
    def formatear_plazo_limite(self, resultado: Dict) -> str:
        """Formatea el cálculo de plazo límite"""
        
        estado_emoji = {"VIGENTE": "✅", "URGENTE": "⚠️", "VENCIDO": "❌"}
        
        return f"""{estado_emoji.get(resultado['estado'], '📅')} **PLAZO PARA APELAR**

📅 **Fechas:**
• Fecha de notificación: {resultado['fecha_notificacion']}
• **Fecha límite: {resultado['fecha_limite_apelacion']}**

⏱️ **Estado:**
• Días hábiles de plazo: {resultado['dias_habiles_plazo']}
• Días calendario restantes: {resultado['dias_calendario_restantes']}
• Estado: **{resultado['estado']}**

📚 *Base legal: {resultado['base_legal']}*"""
    
    def detect_and_process(self, message: str) -> Optional[str]:
        """Detecta si el mensaje es consulta sobre apelaciones"""
        message_lower = message.lower()
        
        keywords = ['apelación', 'apelacion', 'apelar', 'impugnar', 'recurso',
                    'buena pro', 'descalificaron', 'tasa de apelación']
        
        if not any(kw in message_lower for kw in keywords):
            return None
        
        return get_apelaciones_info()


def get_apelaciones_info() -> str:
    """Información general sobre recursos de apelación"""
    return """⚖️ **RECURSO DE APELACIÓN EN CONTRATACIONES PÚBLICAS**

**Base Legal:** Arts. 97-103 del D.S. N° 009-2025-EF

**¿Qué es?**
Mecanismo para impugnar actos del procedimiento de selección que causan agravio.

**¿Ante quién se presenta?**
| Valor Referencial | Instancia |
|-------------------|-----------|
| < S/ 485,000 | Titular de la Entidad |
| ≥ S/ 485,000 | Tribunal de Contrataciones |

**Plazo para apelar:** 8 días hábiles desde notificación

**Tasa de apelación:**
• 3% del valor referencial
• Mínimo Entidad: S/ 150
• Mínimo Tribunal: S/ 1,100

**Tipos de apelación:**
1. 📋 Descalificación indebida
2. 📊 Error en evaluación técnica
3. 💰 Error en evaluación económica
4. ⚠️ Vicios en el procedimiento
5. 🚫 Requisitos restrictivos
6. 🏆 Otorgamiento indebido de buena pro

**Efecto:** Suspende el procedimiento

**Para generar un recurso, proporcione:**
• Número del proceso
• Valor referencial
• Tipo de impugnación
• Descripción del agravio

📚 *Base legal: Arts. 97-103 del Reglamento*"""
