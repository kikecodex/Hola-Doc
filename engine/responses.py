"""
Base de Conocimiento y Respuestas
Ley N° 32069 - Contrataciones Públicas del Perú
"""

def get_principles() -> list:
    """Retorna los principios de la Ley 32069"""
    return [
        {
            "nombre": "Legalidad",
            "descripcion": "Las partes deben actuar con respeto a la Constitución Política del Perú, la Ley y el derecho.",
            "articulo": "Art. 2, inc. 1"
        },
        {
            "nombre": "Eficacia y Eficiencia",
            "descripcion": "Las entidades buscan cumplir los fines públicos, priorizando estos sobre formalidades no esenciales.",
            "articulo": "Art. 2, inc. 2"
        },
        {
            "nombre": "Valor por Dinero",
            "descripcion": "Maximizar el valor obtenido en cada contratación en términos de eficiencia, eficacia y economía, considerando calidad, sostenibilidad y evaluación de costos y plazos.",
            "articulo": "Art. 2, inc. 3"
        },
        {
            "nombre": "Integridad",
            "descripcion": "Actuar con honestidad, ética y neutralidad para prevenir actos de corrupción.",
            "articulo": "Art. 2, inc. 4"
        },
        {
            "nombre": "Presunción de Veracidad",
            "descripcion": "Los documentos y declaraciones son considerados veraces en la tramitación.",
            "articulo": "Art. 2, inc. 5"
        },
        {
            "nombre": "Causalidad",
            "descripcion": "La responsabilidad recae en quien realiza la conducta infractora.",
            "articulo": "Art. 2, inc. 6"
        },
        {
            "nombre": "Publicidad",
            "descripcion": "Promover el libre acceso y participación de proveedores.",
            "articulo": "Art. 2, inc. 7"
        },
        {
            "nombre": "Libertad de Concurrencia",
            "descripcion": "Fomentar la participación de proveedores evitando exigencias innecesarias.",
            "articulo": "Art. 2, inc. 8"
        },
        {
            "nombre": "Transparencia y Facilidad de Uso",
            "descripcion": "Las actuaciones y decisiones deben ser claras, accesibles y con información pública oportuna.",
            "articulo": "Art. 2, inc. 9"
        },
        {
            "nombre": "Competencia",
            "descripcion": "Garantizar la participación de múltiples postores.",
            "articulo": "Art. 2, inc. 10"
        },
        {
            "nombre": "Igualdad de Trato",
            "descripcion": "Evitar favoritismos y asegurar las mismas oportunidades para todos los proveedores.",
            "articulo": "Art. 2, inc. 11"
        },
        {
            "nombre": "Equidad y Colaboración",
            "descripcion": "Promover un equilibrio en las relaciones contractuales.",
            "articulo": "Art. 2, inc. 12"
        },
        {
            "nombre": "Sostenibilidad",
            "descripcion": "Promover prácticas responsables que consideren aspectos económicos, sociales y medioambientales.",
            "articulo": "Art. 2, inc. 13"
        },
        {
            "nombre": "Innovación",
            "descripcion": "Promover la creación de nuevos bienes y servicios o la optimización de los existentes.",
            "articulo": "Art. 2, inc. 14"
        },
        {
            "nombre": "Vigencia Tecnológica",
            "descripcion": "Incorporar tecnologías actualizadas en las contrataciones.",
            "articulo": "Art. 2, inc. 15"
        }
    ]


def get_knowledge_base() -> list:
    """
    Retorna la base de conocimiento para el RAG
    Textos sobre la Ley 32069 y su reglamento
    """
    return [
        # Información General
        """LEY N° 32069 - LEY GENERAL DE CONTRATACIONES PÚBLICAS
        
Publicada el 24 de junio de 2024 en el diario oficial El Peruano.
Entró en vigencia el 22 de abril de 2025.
Deroga la Ley N° 30225, Ley de Contrataciones del Estado.

El Reglamento fue aprobado mediante D.S. N° 009-2025-EF (22 enero 2025).
Modificaciones al Reglamento: D.S. N° 001-2026-EF (8 enero 2026).

CAMBIO IMPORTANTE: El OSCE se transforma en OECE (Organismo Especializado para las Contrataciones Públicas Eficientes) a partir del 22 de abril de 2025.

Nueva plataforma: PLADICOP (Plataforma Digital para las Contrataciones Públicas) integra SEACE y RNP.""",

        # Principios
        """PRINCIPIOS DE LAS CONTRATACIONES PÚBLICAS (Art. 2 - Ley 32069)

La Ley 32069 introduce 15 principios rectores:

1. LEGALIDAD: Actuar con respeto a la Constitución y la Ley.
2. EFICACIA Y EFICIENCIA: Cumplir fines públicos sobre formalidades no esenciales.
3. VALOR POR DINERO: Maximizar valor considerando calidad, sostenibilidad, costos y plazos.
4. INTEGRIDAD: Honestidad, ética y neutralidad para prevenir corrupción.
5. PRESUNCIÓN DE VERACIDAD: Documentos considerados veraces en la tramitación.
6. CAUSALIDAD: Responsabilidad recae en quien comete la infracción.
7. PUBLICIDAD: Libre acceso y participación de proveedores.
8. LIBERTAD DE CONCURRENCIA: Fomentar participación sin exigencias innecesarias.
9. TRANSPARENCIA: Actuaciones claras, accesibles e información pública oportuna.
10. COMPETENCIA: Garantizar participación de múltiples postores.
11. IGUALDAD DE TRATO: Sin favoritismos, mismas oportunidades.
12. EQUIDAD Y COLABORACIÓN: Equilibrio en relaciones contractuales.
13. SOSTENIBILIDAD: Prácticas responsables (económico, social, ambiental).
14. INNOVACIÓN: Promover nuevos bienes/servicios u optimización.
15. VIGENCIA TECNOLÓGICA: Incorporar tecnologías actualizadas.

Los 5 nuevos principios son: Legalidad, Valor por Dinero, Presunción de Veracidad, Causalidad e Innovación.""",

        # Procedimientos y Montos
        """PROCEDIMIENTOS DE SELECCIÓN Y MONTOS 2026 (Ley 32069, Arts. 54-55)

UIT 2026 = S/ 5,500 (D.S. N° 301-2025-EF)
MONTO MÍNIMO (8 UIT) = S/ 44,000

PARA BIENES:
- Licitación Pública: ≥ S/ 485,000
- Licitación Pública Abreviada: > S/ 44,000 y < S/ 485,000
- Subasta Inversa Electrónica: > S/ 44,000 (bienes en listado OECE)
- Comparación de Precios: > S/ 44,000 y ≤ S/ 100,000
- Contratación Directa: > S/ 44,000 (causales específicas)

PARA SERVICIOS Y CONSULTORÍA:
- Concurso Público: ≥ S/ 485,000
- Concurso Público Abreviado: > S/ 44,000 y < S/ 485,000
- Concurso para Evaluadores Expertos: > S/ 44,000 y < S/ 100,000
- Concurso para Gerentes de Proyectos: > S/ 44,000 y < S/ 485,000
- Subasta Inversa Electrónica: > S/ 44,000 (servicios en listado)
- Comparación de Precios: > S/ 44,000 y ≤ S/ 100,000
- Contratación Directa: > S/ 44,000 (causales específicas)

PARA OBRAS:
- Licitación Pública: ≥ S/ 5,000,000 y < S/ 79,000,000
- Licitación Pública Abreviada: > S/ 44,000 y < S/ 5,000,000
- Concurso Proyecto Arquitectónico: > S/ 44,000
- Contratación Directa: > S/ 44,000 (causales específicas)

NOTA: La Adjudicación Simplificada de la Ley 30225 fue reemplazada por los procedimientos abreviados.""",

        # Contratación Directa
        """CONTRATACIÓN DIRECTA (Art. 58 - Ley 32069)

La contratación directa procede por causales específicas:

a) Contratación entre entidades
b) Situación de emergencia
c) Situación de desabastecimiento
d) Carácter secreto, secreto militar o por razones de orden interno
e) Proveedor único
f) Servicios personalísimos
g) Servicios de publicidad en medios de comunicación
h) Servicios de consultoría que continúen de otro proceso
i) Contratación de bienes o servicios con fines de investigación
j) Arrendamiento de bienes inmuebles
k) Servicios especializados de asesoría legal

Requiere informe técnico-legal que sustente la causal.
Debe publicarse en SEACE/PLADICOP.""",

        # Etapas del proceso
        """ETAPAS DEL PROCESO DE CONTRATACIÓN (Ley 32069)

1. ACTUACIONES PREPARATORIAS:
   - Requerimiento del área usuaria
   - Estudio de mercado
   - Determinación del valor referencial
   - Certificación presupuestal
   - Aprobación del expediente de contratación

2. PROCEDIMIENTO DE SELECCIÓN:
   - Convocatoria
   - Registro de participantes
   - Presentación de consultas y observaciones
   - Absolución de consultas y observaciones
   - Integración de bases
   - Presentación de ofertas
   - Evaluación y calificación
   - Otorgamiento de la buena pro

3. EJECUCIÓN CONTRACTUAL:
   - Suscripción del contrato
   - Garantías
   - Adelantos (si aplica)
   - Ejecución de prestaciones
   - Conformidad
   - Pago
   - Cierre del contrato""",

        # SEACE y OECE
        """SEACE Y OECE (ANTES OSCE)

SEACE 3.0 es el Sistema Electrónico de Contrataciones del Estado.
Es el canal único y obligatorio para toda información de contrataciones públicas.
URL: https://prod2.seace.gob.pe/

OECE (Organismo Especializado para las Contrataciones Públicas Eficientes):
- Antes se llamaba OSCE
- Cambió de nombre con la Ley 32069 (abril 2025)
- Funciones: supervisión, asistencia técnica, RNP, PLADICOP
- Administra el Registro Nacional de Proveedores (RNP)
- Implementa el estándar OCDS (Open Contracting Data Standard)

PLADICOP (Plataforma Digital para las Contrataciones Públicas):
- Nueva plataforma que integra SEACE y RNP
- En implementación progresiva
- Interoperabilidad con otros sistemas del Estado

Datos Abiertos: https://contratacionesabiertas.osce.gob.pe/
Formatos disponibles: CSV, XLSX, JSON""",

        # Registro Nacional de Proveedores
        """REGISTRO NACIONAL DE PROVEEDORES (RNP)

El RNP es obligatorio para participar en contrataciones con el Estado.
Administrado por OECE.

TIPOS DE REGISTRO:
- Proveedores de Bienes
- Proveedores de Servicios
- Consultores de Obras
- Ejecutores de Obras

REQUISITOS GENERALES:
- RUC activo
- No tener deudas tributarias exigibles
- No estar impedido de contratar
- Capacidad técnica y económica (para obras)

VIGENCIA: 1 año renovable

VERIFICACIÓN: https://portal.osce.gob.pe/rnp/

IMPORTANTE: Verificar siempre la habilitación del proveedor antes de contratar.""",

        # Garantías
        """GARANTÍAS EN CONTRATACIONES PÚBLICAS (Art. 43 - Ley 32069)

TIPOS DE GARANTÍAS:

1. GARANTÍA DE FIEL CUMPLIMIENTO:
   - 10% del monto del contrato original
   - Obligatoria en todos los contratos
   - Vigencia hasta conformidad o liquidación

2. GARANTÍA POR ADELANTOS:
   - Por el 100% del monto del adelanto
   - Se reduce conforme se amortiza
   - Adelanto directo: hasta 30%
   - Adelanto para materiales: hasta 20%

3. GARANTÍA POR MONTO DIFERENCIAL DE PROPUESTA (obras):
   - Cuando la oferta es menor al 90% del valor referencial
   - Por la diferencia entre el 90% y el monto ofertado

FORMAS DE GARANTÍA ACEPTADAS:
- Carta fianza bancaria
- Póliza de caución
- Depósito en cuenta (casos excepcionales)

Las garantías deben ser incondicionales, solidarias, irrevocables y de realización automática.""",

        # Impedimentos
        """IMPEDIMENTOS PARA CONTRATAR (Art. 11 - Ley 32069)

Están impedidos de ser participantes, postores, contratistas y/o subcontratistas:

a) El Presidente y Vicepresidentes de la República
b) Congresistas
c) Ministros y Viceministros
d) Gobernadores y Vicegobernadores Regionales
e) Alcaldes y Regidores
f) Titulares de organismos autónomos
g) Funcionarios con poder de decisión en la contratación
h) El cónyuge o conviviente de los anteriores
i) Personas jurídicas donde los anteriores tengan participación
j) Proveedores sancionados
k) Proveedores con socios/representantes sancionados
l) Personas naturales o jurídicas con condena por delitos contra la administración pública

El impedimento aplica en el ámbito de su función o jurisdicción.
Verificar siempre en el RNP.""",

        # Recursos impugnativos
        """RECURSOS IMPUGNATIVOS (Arts. 66-67 - Ley 32069)

RECURSO DE APELACIÓN:
- Contra actos dictados durante el procedimiento de selección
- Plazo: 8 días hábiles desde notificación
- Suspende el procedimiento

COMPETENCIA:
- Tribunal de Contrataciones del Estado: Si valor referencial > S/ 485,000
- Titular de la Entidad: Si valor referencial ≤ S/ 485,000

GARANTÍA POR RECURSO:
- 3% del valor referencial
- Mínimo: 3 UIT
- Máximo: 500 UIT

PLAZO DE RESOLUCIÓN:
- 12 días hábiles

El Tribunal de Contrataciones es parte del OECE.
Sus resoluciones agotan la vía administrativa."""
    ]


def format_principles_response() -> str:
    """Formatea los principios para respuesta de chat"""
    principles = get_principles()
    
    response = """📜 **PRINCIPIOS DE LAS CONTRATACIONES PÚBLICAS**
*Ley N° 32069, Artículo 2*

"""
    for i, p in enumerate(principles, 1):
        response += f"**{i}. {p['nombre']}** ({p['articulo']})\n"
        response += f"   {p['descripcion']}\n\n"
    
    response += """
💡 *Los 5 nuevos principios incorporados son: Legalidad, Valor por Dinero, Presunción de Veracidad, Causalidad e Innovación.*"""
    
    return response
