"""
Base de Conocimiento Completa para el Agente de Contrataciones Públicas
Contiene respuestas precisas y verificadas sobre la Ley N° 32069
"""

# =============================================================================
# CONOCIMIENTO BASE - LEY 32069 Y NORMATIVA VIGENTE
# =============================================================================

CONOCIMIENTO_LEY = {
    "ley_32069": {
        "nombre": "Ley N° 32069 - Ley General de Contrataciones Públicas",
        "publicacion": "24 de junio de 2024",
        "vigencia": "22 de abril de 2025",
        "deroga": "Ley N° 30225 y su TUO aprobado por D.S. N° 082-2019-EF",
        "articulos": "118 artículos",
        "disposiciones_complementarias": "23 disposiciones"
    },
    "reglamento": {
        "nombre": "D.S. N° 009-2025-EF - Reglamento de la Ley 32069",
        "publicacion": "22 de enero de 2025",
        "vigencia": "22 de abril de 2025",
        "articulos": "289 artículos"
    },
    "modificaciones_2026": {
        "nombre": "D.S. N° 001-2026-EF - Modificaciones al Reglamento",
        "publicacion": "8 de enero de 2026",
        "vigencia": "17 de enero de 2026 (9 días después de publicación)",
        "articulos_modificados": "Más de 100 artículos modernizados",
        "principales_cambios": [
            "Certificación obligatoria de compradores públicos",
            "Ampliación del plazo de consulta al mercado de 3 a 6 días hábiles",
            "Subsanación de ofertas por evaluadores",
            "Flexibilización de garantías en emergencias",
            "OECE asume rol sancionador"
        ]
    }
}

# =============================================================================
# LOS 15 PRINCIPIOS DE LA LEY 32069 (Art. 2)
# =============================================================================

PRINCIPIOS = {
    "total": 15,
    "nuevos": ["Legalidad", "Valor por Dinero", "Presunción de Veracidad", "Causalidad", "Innovación"],
    "lista_completa": {
        1: {
            "nombre": "Legalidad",
            "nuevo": True,
            "descripcion": "Los actos de las entidades y proveedores deben realizarse conforme a la Constitución, la ley y el derecho dentro de las facultades atribuidas."
        },
        2: {
            "nombre": "Eficacia y Eficiencia",
            "nuevo": False,
            "descripcion": "El proceso de contratación y las decisiones deben orientarse al cumplimiento de los fines, metas y objetivos de la Entidad, priorizando el interés público."
        },
        3: {
            "nombre": "Valor por Dinero",
            "nuevo": True,
            "descripcion": "Las decisiones deben adoptarse aplicando criterios de calidad, precio, costo-beneficio y el ciclo de vida del objeto de contratación, privilegiando la eficacia."
        },
        4: {
            "nombre": "Integridad",
            "nuevo": False,
            "descripcion": "La conducta de los participantes debe guiarse por la honestidad y veracidad, evitando cualquier práctica indebida."
        },
        5: {
            "nombre": "Presunción de Veracidad",
            "nuevo": True,
            "descripcion": "Se presume que los documentos y declaraciones presentados por los proveedores responden a la verdad de los hechos que afirman."
        },
        6: {
            "nombre": "Causalidad",
            "nuevo": True,
            "descripcion": "La responsabilidad debe recaer en quien realiza la acción u omisión que constituye el incumplimiento."
        },
        7: {
            "nombre": "Publicidad",
            "nuevo": False,
            "descripcion": "El proceso de contratación debe ser objeto de publicidad y difusión con la finalidad de promover la libre concurrencia y competencia."
        },
        8: {
            "nombre": "Libertad de Concurrencia",
            "nuevo": False,
            "descripcion": "Las Entidades promueven el libre acceso y participación de proveedores en los procesos de contratación."
        },
        9: {
            "nombre": "Transparencia",
            "nuevo": False,
            "descripcion": "Las Entidades proporcionan información clara y coherente con el fin de que todas las etapas del proceso sean comprendidas."
        },
        10: {
            "nombre": "Competencia",
            "nuevo": False,
            "descripcion": "Los procesos de contratación incluyen disposiciones que permiten establecer condiciones de competencia efectiva."
        },
        11: {
            "nombre": "Igualdad de Trato",
            "nuevo": False,
            "descripcion": "Todos los proveedores deben disponer de las mismas oportunidades para formular sus ofertas."
        },
        12: {
            "nombre": "Equidad y Colaboración",
            "nuevo": False,
            "descripcion": "Las prestaciones y derechos de las partes deben guardar una razonable relación de equivalencia y proporcionalidad."
        },
        13: {
            "nombre": "Sostenibilidad",
            "nuevo": False,
            "descripcion": "En el diseño y desarrollo se consideran criterios y prácticas que permitan contribuir a la protección medioambiental, social y desarrollo humano."
        },
        14: {
            "nombre": "Innovación",
            "nuevo": True,
            "descripcion": "La Entidad promueve la incorporación de la innovación para la mejora de la calidad de los bienes, servicios y obras."
        },
        15: {
            "nombre": "Vigencia Tecnológica",
            "nuevo": False,
            "descripcion": "Los bienes, servicios u obras deben reunir las condiciones de calidad y modernidad tecnológicas necesarias."
        }
    }
}

# =============================================================================
# MONTOS Y TOPES 2026
# =============================================================================

MONTOS_2026 = {
    "uit": 5500,
    "uit_descripcion": "Unidad Impositiva Tributaria 2026 = S/ 5,500 (D.S. N° 301-2025-EF)",
    "monto_minimo": {
        "uit": 8,
        "soles": 44000,
        "descripcion": "Monto mínimo para aplicar la Ley de Contrataciones (8 UIT)"
    },
    "procedimientos": {
        "bienes_servicios": {
            "licitacion_concurso_publico": {
                "desde": 485000,
                "descripcion": "≥ S/ 485,000"
            },
            "procedimiento_abreviado": {
                "desde": 44000,
                "hasta": 485000,
                "descripcion": "> S/ 44,000 y < S/ 485,000"
            },
            "comparacion_precios": {
                "desde": 44000,
                "hasta": 100000,
                "descripcion": "> S/ 44,000 y ≤ S/ 100,000"
            }
        },
        "obras": {
            "licitacion_publica": {
                "desde": 5000000,
                "hasta": 79000000,
                "descripcion": "≥ S/ 5,000,000 y < S/ 79,000,000"
            },
            "licitacion_abreviada": {
                "desde": 44000,
                "hasta": 5000000,
                "descripcion": "> S/ 44,000 y < S/ 5,000,000"
            },
            "concurso_oferta": {
                "desde": 79000000,
                "descripcion": "≥ S/ 79,000,000 (incluye diseño y construcción)"
            }
        }
    }
}

# =============================================================================
# PROCEDIMIENTOS DE SELECCIÓN
# =============================================================================

PROCEDIMIENTOS = {
    "licitacion_publica": {
        "descripcion": "Para bienes ≥ S/ 485,000 y obras ≥ S/ 5,000,000",
        "etapas": ["Convocatoria", "Registro de participantes", "Consultas y observaciones", 
                   "Integración de bases", "Presentación de ofertas", "Evaluación y calificación",
                   "Otorgamiento de buena pro"],
        "plazo_minimo": "22 días hábiles desde convocatoria"
    },
    "concurso_publico": {
        "descripcion": "Para servicios y consultorías ≥ S/ 485,000",
        "etapas": ["Convocatoria", "Registro de participantes", "Consultas y observaciones",
                   "Integración de bases", "Presentación de ofertas", "Evaluación y calificación",
                   "Otorgamiento de buena pro"],
        "plazo_minimo": "22 días hábiles desde convocatoria"
    },
    "licitacion_abreviada": {
        "descripcion": "Para bienes > S/ 44,000 y < S/ 485,000, obras > S/ 44,000 y < S/ 5,000,000",
        "reemplazo": "Reemplaza a la Adjudicación Simplificada",
        "etapas": ["Convocatoria", "Consultas y observaciones", "Integración", 
                   "Presentación de ofertas", "Evaluación", "Buena pro"],
        "plazo_minimo": "8 días hábiles desde convocatoria"
    },
    "concurso_abreviado": {
        "descripcion": "Para servicios/consultorías > S/ 44,000 y < S/ 485,000",
        "reemplazo": "Reemplaza a la Adjudicación Simplificada de servicios",
        "plazo_minimo": "8 días hábiles desde convocatoria"
    },
    "subasta_inversa_electronica": {
        "descripcion": "Para bienes incluidos en el Listado de Bienes Comunes del OECE",
        "caracteristica": "Se compite solo por precio, las especificaciones están estandarizadas",
        "desde": 44000
    },
    "comparacion_precios": {
        "descripcion": "Para bienes/servicios de disponibilidad inmediata > S/ 44,000 y ≤ S/ 100,000",
        "requisitos": "Mínimo 3 cotizaciones de diferentes proveedores",
        "plazo": "5 días hábiles"
    },
    "contratacion_directa": {
        "descripcion": "Contratación sin proceso competitivo",
        "causales": [
            "Contratación entre entidades",
            "Situación de emergencia",
            "Situación de desabastecimiento",
            "Proveedor único",
            "Servicios personalísimos",
            "Servicios de publicidad en medios de comunicación",
            "Servicios de consultoría que son continuación",
            "Bienes y servicios con fines de investigación",
            "Arrendamiento de inmuebles",
            "Servicios especializados de asesoría legal"
        ],
        "aprobacion": "Requiere aprobación del Titular de la Entidad"
    }
}

# =============================================================================
# OECE - ORGANISMO ESPECIALIZADO
# =============================================================================

OECE = {
    "nombre_completo": "Organismo Especializado para las Contrataciones Públicas Eficientes",
    "siglas": "OECE",
    "reemplaza": "OSCE (Organismo Supervisor de las Contrataciones del Estado)",
    "creacion": "Ley N° 32069 - Vigente desde 22/04/2025",
    "naturaleza": "Organismo técnico especializado adscrito al MEF",
    "funciones_principales": [
        "Emitir directivas, lineamientos y documentos de orientación",
        "Administrar el RNP (Registro Nacional de Proveedores)",
        "Administrar el SEACE",
        "Emitir opiniones sobre normativa de contrataciones",
        "Imponer sanciones a proveedores",
        "Resolver recursos de apelación (para valores referenciales ≥ S/ 485,000)",
        "Supervisar instituciones arbitrales",
        "Certificar a los compradores públicos"
    ],
    "diferencia_con_osce": "El OECE tiene un enfoque más de asistencia técnica y orientación, además asume directamente el rol sancionador",
    "web": "https://www.gob.pe/oece"
}

# =============================================================================
# TRIBUNAL DE CONTRATACIONES
# =============================================================================

TRIBUNAL = {
    "nombre": "Tribunal de Contrataciones del Estado",
    "siglas": "TCE",
    "dependencia": "Forma parte del OECE",
    "salas": ["Primera Sala", "Segunda Sala", "Tercera Sala", "Sala Plena"],
    "competencias": [
        "Resolver recursos de apelación (valor referencial ≥ S/ 485,000)",
        "Imponer sanciones de inhabilitación a proveedores",
        "Emitir precedentes vinculantes",
        "Resolver denuncias por infracciones"
    ],
    "sanciones": {
        "amonestacion": {
            "descripcion": "Llamada de atención por escrito",
            "causales": "Infracciones menores, primera falta leve"
        },
        "multa": {
            "descripcion": "Sanción pecuniaria entre 1 y 5 UIT",
            "rango_2026": "S/ 5,500 a S/ 27,500",
            "causales": "Infracciones leves, retiro de propuesta, no suscripción de contrato"
        },
        "inhabilitacion_temporal": {
            "descripcion": "Impedimento temporal para contratar con el Estado",
            "duracion": "3 meses a 3 años",
            "causales": [
                "Presentar información inexacta",
                "Presentar documentos falsos",
                "Incumplimiento de obligaciones contractuales",
                "Contratar estando impedido"
            ]
        },
        "inhabilitacion_definitiva": {
            "descripcion": "Impedimento permanente para contratar con el Estado",
            "causales": [
                "Reincidencia en infracciones graves",
                "Actos de corrupción comprobados",
                "Falsificación de documentos esenciales"
            ]
        }
    },
    "infracciones": [
        {"codigo": "INF-01", "descripcion": "Presentar información inexacta o documentos falsos", "sancion": "12 a 36 meses"},
        {"codigo": "INF-02", "descripcion": "Contratar con el Estado estando impedido", "sancion": "18 a 36 meses"},
        {"codigo": "INF-03", "descripcion": "Incumplimiento injustificado de obligaciones", "sancion": "6 a 24 meses"},
        {"codigo": "INF-04", "descripcion": "No mantener la oferta", "sancion": "Multa 1-2 UIT"},
        {"codigo": "INF-05", "descripcion": "Negarse a suscribir el contrato", "sancion": "3 a 12 meses"},
        {"codigo": "INF-06", "descripcion": "Subcontratar sin autorización", "sancion": "Multa 2-4 UIT"}
    ]
}

# =============================================================================
# GARANTÍAS
# =============================================================================

GARANTIAS = {
    "tipos": {
        "fiel_cumplimiento": {
            "descripcion": "Garantiza el cumplimiento de las obligaciones del contratista",
            "porcentaje": "10% del monto del contrato original",
            "presentacion": "Antes de la firma del contrato",
            "excepcion_mype": "Las micro y pequeñas empresas pueden optar por retención del 10%"
        },
        "adelanto": {
            "descripcion": "Garantiza la devolución del adelanto otorgado",
            "porcentaje": "100% del monto del adelanto",
            "adelanto_maximo": "Hasta 30% del monto del contrato (puede ser mayor en obras)"
        },
        "por_monto_diferencial": {
            "descripcion": "En caso de propuestas con rebaja mayor al 10%",
            "formula": "25% de la diferencia entre el valor referencial y la oferta"
        }
    },
    "instrumentos": [
        "Carta fianza",
        "Póliza de caución",
        "Depósito en cuenta de la Entidad (solo para retención)"
    ],
    "novedades_2026": [
        "Flexibilización en contratos menores",
        "En emergencias pueden efectuarse pagos adelantados sin garantía en casos específicos",
        "Nuevas reglas sobre vigencia y renovación automática"
    ]
}

# =============================================================================
# RNP - REGISTRO NACIONAL DE PROVEEDORES
# =============================================================================

RNP = {
    "nombre": "Registro Nacional de Proveedores",
    "administrador": "OECE",
    "obligatoriedad": "Obligatorio para contratar con el Estado",
    "registros": [
        {"nombre": "Proveedores de bienes", "codigo": "B"},
        {"nombre": "Proveedores de servicios", "codigo": "S"},
        {"nombre": "Consultores de obras", "codigo": "C"},
        {"nombre": "Ejecutores de obras", "codigo": "E"}
    ],
    "vigencia": "Indefinida, sujeta a actualización de información",
    "novedad_2026": "Los ejecutores y consultores pueden acreditar experiencia proveniente de reorganización societaria",
    "web": "https://portal.osce.gob.pe/rnp/"
}

# =============================================================================
# COMPRADORES PÚBLICOS
# =============================================================================

COMPRADORES_PUBLICOS = {
    "certificacion": {
        "obligatoria": True,
        "desde": "D.S. N° 001-2026-EF",
        "emisor": "OECE",
        "niveles": ["Básico", "Intermedio", "Avanzado"],
        "requisitos": "Título profesional técnico o grado de bachiller universitario",
        "registro": "Se implementará el Registro de Compradores Públicos"
    },
    "dec": {
        "nombre": "Dependencia Encargada de las Contrataciones",
        "funcion": "Área responsable de gestionar las contrataciones de la Entidad"
    },
    "lineamientos_conducta": {
        "norma": "Resolución N° D000001-2026-OECE-PRE",
        "fecha": "9 de enero de 2026",
        "aplica_a": "Funcionarios y servidores de la DEC",
        "principios": "Legalidad, transparencia e integridad"
    }
}

# =============================================================================
# PLAZOS IMPORTANTES
# =============================================================================

PLAZOS = {
    "consulta_mercado": {
        "plazo_anterior": "3 días hábiles",
        "plazo_actual": "6 días hábiles",
        "norma": "D.S. N° 001-2026-EF, modificación Art. 51"
    },
    "consultas_observaciones": {
        "licitacion_concurso": "10 días hábiles desde convocatoria",
        "abreviado": "3 días hábiles desde convocatoria"
    },
    "absolucion": {
        "plazo": "5 días hábiles para absolver"
    },
    "integracion_bases": {
        "plazo": "1 día hábil después de absueltas las consultas"
    },
    "apelacion": {
        "plazo_interposicion": "8 días hábiles desde notificación",
        "resolucion_entidad": "12 días hábiles",
        "resolucion_tribunal": "20 días hábiles"
    },
    "suscripcion_contrato": {
        "plazo": "8 días hábiles desde que queda consentida la buena pro",
        "consecuencia_incumplimiento": "Pérdida de buena pro y sanción"
    }
}

# =============================================================================
# RECURSOS IMPUGNATIVOS
# =============================================================================

RECURSOS = {
    "apelacion": {
        "plazo": "8 días hábiles desde la notificación del acto impugnado",
        "ante_entidad": {
            "aplicable": "Valor referencial < S/ 485,000",
            "tasa": "3% del valor referencial (mínimo S/ 150)"
        },
        "ante_tribunal": {
            "aplicable": "Valor referencial ≥ S/ 485,000",
            "tasa": "3% del valor referencial (mínimo S/ 1,100)"
        },
        "efectos": "Suspende el proceso de selección",
        "resolucion": "Fundado, Infundado o Improcedente"
    }
}

# =============================================================================
# SEACE Y PLADICOP
# =============================================================================

PLATAFORMAS = {
    "seace": {
        "nombre": "Sistema Electrónico de Contrataciones del Estado",
        "administrador": "OECE",
        "funcion": "Plataforma oficial para publicar y gestionar procesos de contratación",
        "obligatorio": True,
        "costo_proveedores": "Gratuito para consulta",
        "web": "https://portal.osce.gob.pe/seace/"
    },
    "pladicop": {
        "nombre": "Plataforma Digital para las Contrataciones Públicas",
        "descripcion": "Nueva plataforma que integra el SEACE y el RNP",
        "creacion": "Ley N° 32069",
        "funcionalidades": [
            "Difusión previa del requerimiento",
            "Gestión de procedimientos de selección",
            "Registro de contratos",
            "Interoperabilidad con otras entidades del Estado"
        ]
    }
}

# =============================================================================
# IMPEDIMENTOS (Art. 11 - Ley 32069)
# =============================================================================

IMPEDIMENTOS = {
    "descripcion": "Personas naturales o jurídicas que no pueden ser participantes, postores ni contratistas",
    "lista": [
        "El Presidente de la República, hasta 12 meses después de dejar el cargo",
        "Los Congresistas de la República",
        "Los Ministros y Viceministros de Estado",
        "Los Jueces Supremos, Fiscales Supremos y miembros del JNE",
        "El Contralor General de la República",
        "Los Gobernadores y Vicegobernadores Regionales",
        "Los Alcaldes y Regidores",
        "Los funcionarios con capacidad de decisión en las contrataciones",
        "Los servidores públicos que intervienen directamente en el proceso",
        "Las personas jurídicas con accionariado de funcionarios impedidos",
        "Los cónyuges y parientes hasta el segundo grado de consanguinidad o afinidad",
        "Las personas sancionadas con inhabilitación",
        "Las personas inscritas en el Registro de Deudores de Reparaciones Civiles (REDERECI)"
    ],
    "duracion": "Varía según el cargo, desde permanente hasta 12 meses después de cesar",
    "consecuencia": "Nulidad del contrato y sanción por contratar estando impedido"
}


# =============================================================================
# EJECUCIÓN CONTRACTUAL
# =============================================================================

EJECUCION_CONTRACTUAL = {
    "penalidades": {
        "penalidad_mora": {
            "descripcion": "Penalidad por demora injustificada en la ejecución de prestaciones",
            "formula": "0.05 x monto vigente / F x días de atraso",
            "formula_f": "F = 0.25 para plazos ≤ 60 días; F = 0.40 para plazos > 60 días",
            "tope": "10% del monto del contrato vigente",
            "base_legal": "Art. 162 del Reglamento"
        },
        "otras_penalidades": {
            "descripcion": "Penalidades diferentes a la mora establecidas en el contrato",
            "tope": "10% del monto del contrato vigente",
            "requisito": "Deben estar objetivamente previstas en las bases"
        },
        "tope_total": "El total de penalidades no puede exceder el 10% del monto contractual"
    },
    "adicionales": {
        "bienes_servicios": {
            "limite": "Hasta 25% del monto del contrato original",
            "aprobacion": "Titular de la Entidad o funcionario delegado",
            "requisito": "Necesidad no prevista en el expediente"
        },
        "consultoria_obras": {
            "limite": "Hasta 25% del monto del contrato original",
            "aprobacion": "Titular de la Entidad"
        },
        "obras": {
            "limite_normal": "Hasta 15% del monto del contrato de obra",
            "limite_emergencia": "Hasta 50% en caso de emergencia (Art. 34-A Ley)",
            "aprobacion_hasta_15": "Titular de la Entidad",
            "aprobacion_mayor_15": "Contraloría General de la República"
        }
    },
    "ampliacion_plazo": {
        "causales": [
            "Atrasos y/o paralizaciones no imputables al contratista",
            "Aprobación de adicionales",
            "Caso fortuito o fuerza mayor debidamente comprobado"
        ],
        "procedimiento": {
            "paso_1": "El contratista solicita ampliación dentro de los 7 días de conocida la causal",
            "paso_2": "La Entidad resuelve en 10 días hábiles",
            "paso_3": "El silencio administrativo es negativo"
        }
    },
    "resolucion_contrato": {
        "causales_entidad": [
            "Incumplimiento injustificado de obligaciones contractuales",
            "Acumulación del monto máximo de penalidades",
            "Paralización o reducción injustificada de la ejecución",
            "No obtención de licencias, autorizaciones requeridas"
        ],
        "causales_contratista": [
            "Incumplimiento de la Entidad de sus obligaciones esenciales",
            "Caso fortuito o fuerza mayor que imposibilite continuar"
        ],
        "procedimiento": {
            "paso_1": "Carta notarial requiriendo cumplimiento en plazo no menor a 5 días",
            "paso_2": "Si no subsana, carta notarial de resolución",
            "paso_3": "Liquidación del contrato"
        }
    },
    "conformidad": {
        "bienes": "Dentro de los 7 días de la recepción",
        "servicios": "Dentro de los 7 días de la prestación",
        "consultorias": "Dentro de los 10 días de la recepción del entregable",
        "obras": "Acta de recepción de obra por Comité de Recepción"
    }
}

# =============================================================================
# CONTROVERSIAS Y SOLUCIÓN DE CONFLICTOS
# =============================================================================

CONTROVERSIAS = {
    "mecanismos": {
        "conciliacion": {
            "descripcion": "Mecanismo alternativo de solución de controversias",
            "obligatoriedad": "Obligatoria antes del arbitraje para algunas materias",
            "centro": "Centro de Conciliación autorizado por el MINJUSDH",
            "etapa": "Durante la ejecución contractual"
        },
        "arbitraje": {
            "descripcion": "Mecanismo heterocompositivo de resolución de controversias",
            "tipos": ["Arbitraje institucional", "Arbitraje ad-hoc"],
            "obligatoriedad": "Obligatorio para controversias durante la ejecución que no se resuelvan por conciliación",
            "supervision": "OECE supervisa a las instituciones arbitrales",
            "plazo_inicio": "30 días hábiles de notificada la resolución o acto que se impugna"
        },
        "jprd": {
            "nombre": "Junta de Prevención y Resolución de Disputas",
            "descripcion": "Órgano colegiado para prevenir y resolver disputas en contratos de obra",
            "aplicacion": "Obras con valor igual o superior a S/ 20,000,000",
            "composicion": "1 o 3 miembros según complejidad",
            "supervision": "OECE supervisa directamente (D.S. 001-2026-EF)",
            "ventaja": "Decisiones más rápidas durante la ejecución"
        }
    },
    "materias_arbitrables": [
        "Resolución de contrato",
        "Ampliación de plazo",
        "Recepción y conformidad",
        "Valorizaciones y pagos",
        "Adicionales",
        "Mayores gastos generales",
        "Indemnizaciones",
        "Liquidación del contrato"
    ],
    "novedades_2026": {
        "supervisión_jprd": "OECE asume supervisión directa de las JPRD",
        "instituciones_arbitrales": "Mayor control y fiscalización por parte del OECE",
        "registro_arbitros": "Registro de árbitros administrado por OECE"
    }
}

# =============================================================================
# DOCUMENTOS DEL PROCEDIMIENTO
# =============================================================================

DOCUMENTOS_PROCEDIMIENTO = {
    "expediente_contratacion": {
        "contenido": [
            "Requerimiento del área usuaria",
            "Estudio de mercado",
            "Valor estimado o referencial",
            "Certificación presupuestal",
            "Bases",
            "Resolución de aprobación"
        ]
    },
    "requerimiento": {
        "descripcion": "Documento que contiene las características técnicas del bien, servicio u obra",
        "tipos": {
            "bienes": "Especificaciones Técnicas (EETT)",
            "servicios": "Términos de Referencia (TDR)",
            "obras": "Expediente Técnico"
        }
    },
    "estudio_mercado": {
        "contenido": [
            "Análisis de alternativas del mercado",
            "Cotizaciones de proveedores",
            "Precios históricos",
            "Determinación del valor estimado o referencial"
        ],
        "plazo_consulta": "6 días hábiles (modificado por D.S. 001-2026-EF)"
    },
    "bases": {
        "contenido": [
            "Denominación del objeto del contrato",
            "Especificaciones técnicas o términos de referencia",
            "Valor referencial",
            "Sistema de contratación",
            "Requisitos de calificación",
            "Factores de evaluación",
            "Proforma de contrato"
        ]
    }
}


def get_respuesta(pregunta_clave: str) -> str:
    """Retorna la respuesta apropiada según la consulta"""
    # Esta función puede expandirse para búsqueda semántica
    pass


def get_conocimiento_completo() -> dict:
    """Retorna todo el conocimiento estructurado"""
    return {
        "ley": CONOCIMIENTO_LEY,
        "principios": PRINCIPIOS,
        "montos": MONTOS_2026,
        "procedimientos": PROCEDIMIENTOS,
        "oece": OECE,
        "tribunal": TRIBUNAL,
        "garantias": GARANTIAS,
        "rnp": RNP,
        "compradores": COMPRADORES_PUBLICOS,
        "plazos": PLAZOS,
        "recursos": RECURSOS,
        "plataformas": PLATAFORMAS,
        "impedimentos": IMPEDIMENTOS,
        "ejecucion_contractual": EJECUCION_CONTRACTUAL,
        "controversias": CONTROVERSIAS,
        "documentos": DOCUMENTOS_PROCEDIMIENTO
    }
