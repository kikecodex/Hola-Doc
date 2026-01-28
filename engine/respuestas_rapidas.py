"""
Sistema de Respuestas Rápidas Precalculadas
Respuestas instantáneas para las preguntas más frecuentes sobre contrataciones públicas
"""

# =============================================================================
# BASE DE PREGUNTAS Y RESPUESTAS PRECALCULADAS
# Estas respuestas se entregan en milisegundos sin necesidad de IA
# =============================================================================

RESPUESTAS_RAPIDAS = {
    # =========================================================================
    # LEY 32069 - INFORMACIÓN GENERAL
    # =========================================================================
    
    "vigencia_ley": {
        "preguntas": [
            "¿cuándo entró en vigencia la ley 32069?",
            "cuando entro en vigencia la ley 32069",
            "vigencia de la ley 32069",
            "desde cuando esta vigente la ley 32069",
            "cuando se aplica la ley 32069"
        ],
        "respuesta": """📜 **Vigencia de la Ley N° 32069**

La **Ley N° 32069 - Ley General de Contrataciones Públicas** tiene las siguientes fechas:

• **Publicación:** 24 de junio de 2024
• **Entrada en vigencia:** 22 de abril de 2025

Esta ley **derogó** la anterior Ley N° 30225 y su TUO (D.S. N° 082-2019-EF).

📚 *Base legal: Tercera Disposición Complementaria Final de la Ley 32069*"""
    },
    
    "ley_derogada": {
        "preguntas": [
            "¿qué ley derogó la ley 32069?",
            "que ley derogo la 32069",
            "cual fue la ley anterior",
            "que paso con la ley 30225"
        ],
        "respuesta": """📜 **Ley Derogada**

La **Ley N° 32069** derogó las siguientes normas:

• **Ley N° 30225** - Ley de Contrataciones del Estado (anterior)
• **D.S. N° 082-2019-EF** - TUO de la Ley de Contrataciones

La derogación fue **expresa y total**, entrando en vigencia el nuevo marco normativo el 22 de abril de 2025.

📚 *Base legal: Única Disposición Complementaria Derogatoria de la Ley 32069*"""
    },

    # =========================================================================
    # LOS 15 PRINCIPIOS
    # =========================================================================
    
    "cantidad_principios": {
        "preguntas": [
            "¿cuántos principios tiene la ley 32069?",
            "cuantos principios tiene la ley 32069",
            "cuantos son los principios",
            "numero de principios",
            "cantidad de principios"
        ],
        "respuesta": """📜 **Cantidad de Principios**

La **Ley N° 32069** establece **15 PRINCIPIOS** rectores para las contrataciones públicas, de los cuales **5 son NUEVOS** respecto a la ley anterior.

**Los 5 nuevos principios son:**
1. Legalidad
2. Valor por Dinero
3. Presunción de Veracidad
4. Causalidad
5. Innovación

📚 *Base legal: Artículo 2 de la Ley N° 32069*"""
    },
    
    "lista_principios": {
        "preguntas": [
            "¿cuáles son los principios de la ley 32069?",
            "cuales son los principios",
            "lista de principios",
            "dime los 15 principios",
            "principios de las contrataciones publicas",
            "menciona los principios"
        ],
        "respuesta": """📜 **Los 15 Principios de la Ley N° 32069** (Art. 2)

1. **Legalidad** ⭐ NUEVO
2. **Eficacia y Eficiencia**
3. **Valor por Dinero** ⭐ NUEVO
4. **Integridad**
5. **Presunción de Veracidad** ⭐ NUEVO
6. **Causalidad** ⭐ NUEVO
7. **Publicidad**
8. **Libertad de Concurrencia**
9. **Transparencia**
10. **Competencia**
11. **Igualdad de Trato**
12. **Equidad y Colaboración**
13. **Sostenibilidad**
14. **Innovación** ⭐ NUEVO
15. **Vigencia Tecnológica**

📚 *Base legal: Artículo 2 de la Ley N° 32069*"""
    },
    
    "principios_nuevos": {
        "preguntas": [
            "¿cuáles son los nuevos principios?",
            "cuales son los nuevos principios",
            "principios nuevos de la ley 32069",
            "que principios se agregaron",
            "5 nuevos principios"
        ],
        "respuesta": """📜 **Los 5 Nuevos Principios de la Ley 32069**

La Ley N° 32069 incorporó **5 NUEVOS PRINCIPIOS** que no estaban en la Ley 30225:

1. **LEGALIDAD**: Los actos deben realizarse conforme a la Constitución, la ley y el derecho.

2. **VALOR POR DINERO**: Las decisiones aplican criterios de calidad, precio, costo-beneficio y ciclo de vida.

3. **PRESUNCIÓN DE VERACIDAD**: Los documentos presentados se presumen verdaderos.

4. **CAUSALIDAD**: La responsabilidad recae en quien realiza la acción u omisión.

5. **INNOVACIÓN**: Se promueve la incorporación de innovación para mejorar la calidad.

📚 *Base legal: Artículo 2 de la Ley N° 32069*"""
    },

    # =========================================================================
    # MONTOS Y TOPES 2026
    # =========================================================================
    
    "uit_2026": {
        "preguntas": [
            "¿cuál es la uit 2026?",
            "cual es la uit 2026",
            "valor de la uit 2026",
            "monto uit 2026",
            "cuanto es la uit",
            "uit actual"
        ],
        "respuesta": """💰 **UIT 2026**

La **Unidad Impositiva Tributaria (UIT)** para el año 2026 es:

# **S/ 5,500**

Este valor fue establecido por el **D.S. N° 301-2025-EF** publicado en diciembre de 2025.

📊 **Datos relevantes:**
• 8 UIT (mínimo para ley) = **S/ 44,000**
• 100 UIT = **S/ 550,000**

📚 *Base legal: D.S. N° 301-2025-EF*"""
    },
    
    "monto_minimo": {
        "preguntas": [
            "¿cuál es el monto mínimo para aplicar la ley?",
            "cual es el monto minimo",
            "monto minimo contrataciones",
            "a partir de que monto aplica la ley",
            "8 uit cuanto es"
        ],
        "respuesta": """💰 **Monto Mínimo para Aplicar la Ley de Contrataciones**

El monto mínimo es **8 UIT** (equivalente a **S/ 44,000** en 2026).

• **Contrataciones < S/ 44,000**: NO requieren proceso de selección
• **Contrataciones ≥ S/ 44,000**: SÍ requieren proceso de selección

⚠️ Las contrataciones menores a 8 UIT se rigen por directivas internas de cada Entidad.

📚 *Base legal: Artículo 5.1 literal a) de la Ley N° 32069*"""
    },
    
    "tope_licitacion_bienes": {
        "preguntas": [
            "¿cuál es el monto para licitación pública de bienes?",
            "monto licitacion publica bienes",
            "a partir de cuanto es licitacion publica",
            "tope para licitacion bienes"
        ],
        "respuesta": """💰 **Monto para Licitación Pública de Bienes (2026)**

**≥ S/ 485,000**

| Procedimiento | Rango de Montos |
|--------------|-----------------|
| Licitación Pública | ≥ S/ 485,000 |
| Licitación Abreviada | > S/ 44,000 y < S/ 485,000 |
| Comparación de Precios | > S/ 44,000 y ≤ S/ 100,000 |

📚 *Base legal: Artículos 54-55 de la Ley 32069 y Art. 19 del Reglamento*"""
    },
    
    "tope_licitacion_obras": {
        "preguntas": [
            "¿cuál es el monto para licitación pública de obras?",
            "monto licitacion publica obras",
            "a partir de cuanto es licitacion obras",
            "tope para licitacion obras"
        ],
        "respuesta": """💰 **Monto para Licitación Pública de Obras (2026)**

**≥ S/ 5,000,000 y < S/ 79,000,000**

| Procedimiento | Rango de Montos |
|--------------|-----------------|
| Licitación Pública | ≥ S/ 5,000,000 y < S/ 79,000,000 |
| Licitación Abreviada | > S/ 44,000 y < S/ 5,000,000 |
| Concurso Oferta | ≥ S/ 79,000,000 |

📚 *Base legal: Art. 54-55 de la Ley 32069 y Art. 19 del Reglamento*"""
    },

    # =========================================================================
    # PROCEDIMIENTOS DE SELECCIÓN
    # =========================================================================
    
    "procedimientos_seleccion": {
        "preguntas": [
            "¿cuáles son los procedimientos de selección?",
            "cuales son los procedimientos de seleccion",
            "tipos de procedimientos",
            "procedimientos de seleccion vigentes",
            "que procedimientos existen"
        ],
        "respuesta": """📋 **Procedimientos de Selección Vigentes (Ley 32069)**

1. **Licitación Pública**
   - Bienes: ≥ S/ 485,000
   - Obras: ≥ S/ 5,000,000

2. **Concurso Público**
   - Servicios/Consultorías: ≥ S/ 485,000

3. **Licitación Pública Abreviada** (reemplaza Adjudicación Simplificada)
   - Bienes: > S/ 44,000 y < S/ 485,000
   - Obras: > S/ 44,000 y < S/ 5,000,000

4. **Concurso Público Abreviado**
   - Servicios: > S/ 44,000 y < S/ 485,000

5. **Subasta Inversa Electrónica**
   - Bienes del listado OECE

6. **Comparación de Precios**
   - > S/ 44,000 y ≤ S/ 100,000

7. **Contratación Directa**
   - Causales específicas del Art. 56

📚 *Base legal: Arts. 54-56 de la Ley N° 32069*"""
    },
    
    "adjudicacion_simplificada": {
        "preguntas": [
            "¿qué pasó con la adjudicación simplificada?",
            "que paso con la adjudicacion simplificada",
            "existe la adjudicacion simplificada",
            "adjudicacion simplificada ya no existe"
        ],
        "respuesta": """📋 **Adjudicación Simplificada - Ya No Existe**

La **Adjudicación Simplificada** de la antigua Ley 30225 **fue eliminada**.

En la Ley N° 32069 fue **reemplazada** por:

• **Licitación Pública Abreviada** → para bienes y obras
• **Concurso Público Abreviado** → para servicios y consultorías

Estos "procedimientos abreviados" tienen plazos y etapas reducidas respecto a la LP/CP.

📚 *Base legal: Arts. 54-55 de la Ley N° 32069*"""
    },

    # =========================================================================
    # APELACIÓN
    # =========================================================================
    
    "procedimiento_apelacion": {
        "preguntas": [
            "¿cuál es el procedimiento para apelar?",
            "procedimiento para la apelacion",
            "como apelo una buena pro",
            "recurso de apelacion",
            "como impugno",
            "en que circunstancias procede una apelacion",
            "cuando puedo apelar",
            "plazo para apelar"
        ],
        "respuesta": """⚖️ **Recurso de Apelación** (Art. 97-103 del Reglamento)

**¿Cuándo procede?**
• Contra actos dictados durante el procedimiento de selección
• Desde convocatoria hasta otorgamiento de buena pro

**Plazo para interponer:**
• **8 días hábiles** desde la notificación del acto impugnado

**¿Ante quién se presenta?**

| Valor Referencial | Resuelve |
|------------------|----------|
| < S/ 485,000 | La Entidad |
| ≥ S/ 485,000 | Tribunal de Contrataciones |

**Tasa:**
• 3% del valor referencial
• Mínimo ante Entidad: S/ 150
• Mínimo ante Tribunal: S/ 1,100

**Efectos:**
• **Suspende** el procedimiento de selección

**Plazo para resolver:**
• Entidad: 12 días hábiles
• Tribunal: 20 días hábiles

📚 *Base legal: Arts. 97-103 del D.S. N° 009-2025-EF*"""
    },

    # =========================================================================
    # OECE
    # =========================================================================
    
    "que_es_oece": {
        "preguntas": [
            "¿qué es el oece?",
            "que es el oece",
            "que significa oece",
            "oece que es"
        ],
        "respuesta": """🏛️ **OECE - Organismo Especializado para las Contrataciones Públicas Eficientes**

Es el organismo técnico especializado adscrito al MEF que **reemplaza al OSCE**.

**Funciones principales:**
• Emitir directivas y lineamientos
• Administrar el RNP y SEACE
• Imponer sanciones a proveedores
• Resolver recursos de apelación (≥ S/ 485,000)
• Emitir opiniones sobre normativa
• Certificar compradores públicos
• Supervisar instituciones arbitrales

**Creación:** Ley N° 32069
**Web:** https://www.gob.pe/oece

📚 *Base legal: Arts. 81-84 de la Ley N° 32069*"""
    },
    
    "diferencia_osce_oece": {
        "preguntas": [
            "¿cuál es la diferencia entre osce y oece?",
            "diferencia osce oece",
            "osce vs oece",
            "que cambio de osce a oece"
        ],
        "respuesta": """🏛️ **Diferencia entre OSCE y OECE**

| Aspecto | OSCE (antes) | OECE (ahora) |
|---------|-------------|--------------|
| Nombre | Organismo Supervisor | Organismo Especializado |
| Enfoque | Supervisión/Fiscalización | Asistencia técnica + Eficiencia |
| Rol sancionador | A través del Tribunal | Directo + Tribunal |
| Certificación | No existía | Certifica compradores públicos |
| JPRD | No supervisaba | Supervisa directamente |

El OECE tiene un enfoque más orientado a la **eficiencia y asistencia técnica**, además asume directamente funciones sancionadoras.

📚 *Base legal: Arts. 81-84 de la Ley N° 32069*"""
    },

    # =========================================================================
    # TRIBUNAL
    # =========================================================================
    
    "tribunal_sanciones": {
        "preguntas": [
            "¿qué sanciones aplica el tribunal?",
            "sanciones del tribunal",
            "tipos de sanciones tribunal",
            "que sanciones puede imponer el tribunal"
        ],
        "respuesta": """⚖️ **Sanciones del Tribunal de Contrataciones** (Art. 75 Ley 32069)

El Tribunal puede imponer las siguientes sanciones:

1️⃣ **AMONESTACIÓN**
• Llamada de atención por escrito
• Para infracciones menores

2️⃣ **MULTA**
• De 1 a 5 UIT (S/ 5,500 a S/ 27,500 en 2026)
• Por incumplimientos leves

3️⃣ **INHABILITACIÓN TEMPORAL**
• De 3 meses a 3 años
• Por presentar documentos falsos, incumplimientos, etc.

4️⃣ **INHABILITACIÓN DEFINITIVA**
• Permanente
• Por reincidencia grave o actos de corrupción

📚 *Base legal: Art. 75 Ley 32069 y Arts. 237-244 del Reglamento*"""
    },

    # =========================================================================
    # GARANTÍAS
    # =========================================================================
    
    "garantia_fiel_cumplimiento": {
        "preguntas": [
            "¿cuánto es la garantía de fiel cumplimiento?",
            "garantia de fiel cumplimiento",
            "porcentaje garantia fiel cumplimiento",
            "monto garantia fiel cumplimiento"
        ],
        "respuesta": """🔒 **Garantía de Fiel Cumplimiento**

**Porcentaje:** 10% del monto del contrato original

**Presentación:** Antes de la firma del contrato

**Instrumentos aceptados:**
• Carta fianza
• Póliza de caución

**Excepción para MYPE:**
Las micro y pequeñas empresas pueden optar por retención del 10% sobre pagos.

**Devolución:**
Después de la conformidad de la última prestación o liquidación.

📚 *Base legal: Art. 61 de la Ley 32069 y Arts. 141-145 del Reglamento*"""
    },

    # =========================================================================
    # PENALIDADES POR MORA
    # =========================================================================
    
    "calculo_penalidad": {
        "preguntas": [
            "calculo de penalidad",
            "cálculo de penalidad",
            "como calcular penalidad",
            "cómo calcular penalidad",
            "monto de penalidad",
            "penalidad por mora",
            "penalidad por atraso",
            "formula de penalidad",
            "fórmula de penalidad",
            "dias de atraso penalidad",
            "días de atraso penalidad",
            "contrato penalidad monto",
            "contrato dias atraso penalidad",
            "tengo un contrato penalidad",
            "cual es el monto exacto de la penalidad"
        ],
        "respuesta": """💰 **CÁLCULO DE PENALIDADES POR MORA**

📐 **FÓRMULA (Art. 163 del Reglamento D.S. N° 009-2025-EF):**

```
Penalidad diaria = 0.10 × (Monto del contrato / F × Plazo en días)
```

**Donde F:** Factor según tipo de contratación
• Bienes/Servicios/Consultorías: **F = 0.25**
• Obras: **F = 0.15**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **EJEMPLO DE CÁLCULO:**
- Contrato: **S/ 500,000**
- Plazo: **90 días**
- Días de atraso: **15 días**
- Tipo: Bienes (F = 0.25)

**Paso 1:** Penalidad diaria = 0.10 × (500,000 / 0.25 × 90)
**Paso 2:** Penalidad diaria = 0.10 × (500,000 / 22.5) = 0.10 × 22,222.22
**Paso 3:** Penalidad diaria = **S/ 2,222.22**
**Paso 4:** Penalidad total = S/ 2,222.22 × 15 días = **S/ 33,333.33**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ **TOPE MÁXIMO:** La penalidad **NO puede exceder el 10%** del monto del contrato.
- Tope para S/ 500,000 = S/ 50,000

⚠️ Si alcanza el 10%, la Entidad puede **RESOLVER EL CONTRATO**.

🔢 Usa el módulo **"Penalidades"** para calcular automáticamente.

📚 *Base legal: Art. 163 del Reglamento D.S. N° 009-2025-EF*""",
    },

    # =========================================================================
    # AMPLIACIÓN DE PLAZO
    # =========================================================================
    
    "ampliacion_plazo": {
        "preguntas": [
            "ampliación de plazo",
            "ampliacion de plazo",
            "solicitud de ampliación",
            "solicitud de ampliacion",
            "como solicitar ampliación de plazo",
            "como solicitar ampliacion de plazo",
            "prórroga de plazo",
            "prorroga de plazo",
            "extensión de plazo",
            "extension de plazo",
            "caso fortuito contrataciones",
            "fuerza mayor contrataciones",
            "atrasos no imputables",
            "plazo adicional contrataciones",
            "cuando procede ampliación de plazo",
            "cuando procede ampliacion de plazo",
            "requisitos ampliación de plazo",
            "requisitos ampliacion de plazo",
            # Preguntas de la versión anterior (compatibilidad)
            "¿cuándo procede la ampliación de plazo?",
            "causales ampliacion plazo",
            "ampliacion de plazo contrato"
        ],
        "respuesta": """📅 **AMPLIACIÓN DE PLAZO CONTRACTUAL**

⚖️ **Base Legal:** Arts. 170-173 del Reglamento D.S. N° 009-2025-EF

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**¿CUÁNDO PROCEDE?**
La ampliación de plazo procede cuando el atraso o paralización es causada por:

1️⃣ **Caso Fortuito o Fuerza Mayor** debidamente comprobado
2️⃣ **Atrasos en el cumplimiento de prestaciones accesorias** de la Entidad
3️⃣ **Atrasos por causas no imputables al contratista**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**📋 PROCEDIMIENTO:**

| Paso | Descripción | Plazo |
|------|-------------|-------|
| 1 | Contratista comunica la causal | Dentro de los **7 días hábiles** de iniciada |
| 2 | Solicitud formal con sustento | Dentro de los **15 días hábiles** de concluida la causal |
| 3 | Pronunciamiento de la Entidad | **10 días hábiles** desde recibida la solicitud |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**📝 DOCUMENTOS REQUERIDOS:**
• Solicitud escrita indicando la causal invocada
• Cuantificación del plazo de ampliación solicitado
• Documentación de sustento (actas, informes, fotos)
• Nuevo cronograma de ejecución propuesto

**⚠️ IMPORTANTE:**
• El silencio administrativo es **NEGATIVO**
• Si no hay pronunciamiento en plazo, se considera denegada
• El contratista puede interponer recurso impugnativo

📚 *Base legal: Arts. 170-173 del Reglamento D.S. N° 009-2025-EF*""",
    },

    # =========================================================================
    # CAMBIOS D.S. 001-2026-EF
    # =========================================================================
    
    "cambios_2026": {
        "preguntas": [
            "¿qué cambios trajo el ds 001-2026-ef?",
            "cambios ds 001-2026",
            "modificaciones 2026",
            "novedades del reglamento 2026",
            "que cambio en enero 2026"
        ],
        "respuesta": """🆕 **Principales Cambios del D.S. N° 001-2026-EF**

Publicado: 08/01/2026 | Vigente desde: 17/01/2026

1️⃣ **CERTIFICACIÓN OBLIGATORIA DE COMPRADORES**
• Niveles: básico, intermedio, avanzado
• Emitida por OECE
• Requisito: título técnico o bachiller

2️⃣ **NUEVO PLAZO CONSULTA AL MERCADO**
• Antes: 3 días hábiles
• Ahora: **6 días hábiles** (Art. 51)

3️⃣ **SUBSANACIÓN DE OFERTAS**
• Evaluadores pueden solicitar subsanar errores formales
• No altera contenido esencial

4️⃣ **EXPERIENCIA EN RNP**
• Se acepta experiencia de reorganización societaria

5️⃣ **GARANTÍAS EN EMERGENCIAS**
• Pagos adelantados sin garantía en casos específicos

6️⃣ **OECE ASUME ROL SANCIONADOR**
• Supervisión directa de JPRD e instituciones arbitrales

📚 *Base legal: D.S. N° 001-2026-EF*"""
    },

    # =========================================================================
    # RNP
    # =========================================================================
    
    "que_es_rnp": {
        "preguntas": [
            "¿qué es el rnp?",
            "que es el rnp",
            "registro nacional de proveedores",
            "rnp que es"
        ],
        "respuesta": """📝 **RNP - Registro Nacional de Proveedores**

Sistema administrado por el OECE donde se inscriben las personas naturales y jurídicas que desean contratar con el Estado.

**Registros disponibles:**
• Proveedores de Bienes (B)
• Proveedores de Servicios (S)
• Consultores de Obras (C)
• Ejecutores de Obras (E)

**¿Es obligatorio?**
Sí, es **OBLIGATORIO** para participar en procesos de contratación.

**Vigencia:**
Indefinida (sujeta a actualización de información)

**Web:** https://portal.osce.gob.pe/rnp/

📚 *Base legal: Art. 78-80 de la Ley 32069*"""
    },

    # =========================================================================
    # PLAZOS
    # =========================================================================
    
    "plazo_suscripcion_contrato": {
        "preguntas": [
            "¿cuál es el plazo para firmar el contrato?",
            "plazo para suscribir contrato",
            "cuanto tiempo para firmar contrato",
            "plazo suscripcion contrato"
        ],
        "respuesta": """📅 **Plazo para Suscribir Contrato**

El postor ganador tiene **8 días hábiles** desde que la buena pro queda consentida para suscribir el contrato.

**¿Qué pasa si no firma?**
• Pierde la buena pro
• Se le aplica sanción de inhabilitación (3-12 meses)
• Se llama al postor que ocupó el segundo lugar

📚 *Base legal: Art. 139 del D.S. N° 009-2025-EF*"""
    },

    # =========================================================================
    # RNP - REGISTRO NACIONAL DE PROVEEDORES (AMPLIADO)
    # =========================================================================

    "registros_rnp": {
        "preguntas": [
            "¿cuáles son los registros del rnp?",
            "tipos de registro rnp",
            "cuales registros tiene el rnp",
            "categorias del rnp"
        ],
        "respuesta": """📝 **Registros del RNP**

El RNP tiene **4 registros principales**:

| Código | Registro | Para contratar |
|--------|----------|----------------|
| **B** | Proveedores de Bienes | Suministro de bienes |
| **S** | Proveedores de Servicios | Prestación de servicios |
| **C** | Consultores de Obras | Estudios y supervisión de obras |
| **E** | Ejecutores de Obras | Ejecución de obras |

**Importante:**
• Cada registro tiene requisitos específicos
• Los ejecutores y consultores deben acreditar capacidad técnica y económica
• Web: https://portal.osce.gob.pe/rnp/

📚 *Base legal: Arts. 78-80 de la Ley 32069*"""
    },

    "inscripcion_rnp": {
        "preguntas": [
            "¿cómo me inscribo en el rnp?",
            "como inscribirse en rnp",
            "requisitos inscripcion rnp",
            "como ser proveedor del estado"
        ],
        "respuesta": """📝 **Cómo Inscribirse en el RNP**

**Pasos generales:**
1. Ingresar a https://portal.osce.gob.pe/rnp/
2. Seleccionar tipo de registro (Bienes, Servicios, Consultor, Ejecutor)
3. Completar formulario con datos de la empresa
4. Adjuntar documentación requerida
5. Pagar la tasa correspondiente
6. Esperar verificación

**Requisitos comunes:**
• RUC activo y habido
• Ficha RUC de SUNAT
• DNI del representante legal
• Vigencia de poder
• Declaración jurada

**Vigencia:** Indefinida (sujeta a actualización)

📚 *Base legal: Arts. 78-80 de la Ley 32069*"""
    },

    "experiencia_rnp": {
        "preguntas": [
            "¿puedo acreditar experiencia por reorganización societaria?",
            "experiencia reorganizacion societaria rnp",
            "experiencia por fusion rnp",
            "heredar experiencia rnp"
        ],
        "respuesta": """📝 **Experiencia por Reorganización Societaria (Novedad 2026)**

**Sí es posible.** El D.S. N° 001-2026-EF permite acreditar experiencia de reorganización societaria.

**Casos permitidos:**
• Fusión por absorción
• Fusión por constitución
• Escisión
• Reorganización simple

**Requisitos:**
1. Documento público que acredite la reorganización
2. Inscripción en Registros Públicos
3. Los contratos deben estar debidamente sustentados

📚 *Base legal: D.S. N° 001-2026-EF*"""
    },

    # =========================================================================
    # SEACE Y PLADICOP
    # =========================================================================

    "que_es_seace": {
        "preguntas": [
            "¿qué es el seace?",
            "que es el seace",
            "sistema electronico de contrataciones",
            "seace que es"
        ],
        "respuesta": """💻 **SEACE - Sistema Electrónico de Contrataciones del Estado**

Es la plataforma oficial donde se **publican y gestionan** los procesos de contratación pública.

**Información que contiene:**
• Convocatorias de procesos
• Bases y documentos del procedimiento
• Absolución de consultas
• Resultados y buena pro
• Contratos y sus modificaciones

**Administrador:** OECE

**¿Tiene costo?**
• Para proveedores: GRATUITO para consulta
• Para entidades: Obligatorio registrar información

**Web:** https://portal.osce.gob.pe/seace/

📚 *Base legal: Arts. 85-88 de la Ley 32069*"""
    },

    "que_es_pladicop": {
        "preguntas": [
            "¿qué es pladicop?",
            "que es pladicop",
            "plataforma digital contrataciones",
            "diferencia seace pladicop"
        ],
        "respuesta": """💻 **PLADICOP - Plataforma Digital para las Contrataciones Públicas**

Es la **nueva plataforma** creada por la Ley 32069 que integra todos los sistemas de contrataciones.

**Diferencias con SEACE:**

| SEACE | PLADICOP |
|-------|----------|
| Sistema actual | Nueva plataforma integral |
| Solo procesos | Integra RNP + SEACE |
| Funcionalidades limitadas | Interoperabilidad total |

**Funcionalidades de PLADICOP:**
• Difusión previa del requerimiento
• Gestión completa de procedimientos
• Registro de contratos
• Interoperabilidad con otras entidades

📚 *Base legal: Art. 85 de la Ley 32069*"""
    },

    # =========================================================================
    # IMPEDIMENTOS
    # =========================================================================

    "quienes_impedidos": {
        "preguntas": [
            "¿quiénes están impedidos de contratar?",
            "quienes estan impedidos",
            "impedidos de contratar con el estado",
            "quien no puede contratar con el estado"
        ],
        "respuesta": """🚫 **Impedidos de Contratar con el Estado** (Art. 11 Ley 32069)

**Funcionarios y autoridades:**
• Presidente de la República (hasta 12 meses después)
• Congresistas
• Ministros y Viceministros
• Jueces y Fiscales Supremos
• Contralor General
• Gobernadores y Alcaldes
• Funcionarios con decisión en contrataciones

**Otros impedidos:**
• Cónyuges y parientes hasta 2° grado de los anteriores
• Empresas donde participen los impedidos
• Proveedores sancionados con inhabilitación
• Inscritos en REDERECI

**Consecuencia de contratar estando impedido:**
• Nulidad del contrato
• Inhabilitación del proveedor

📚 *Base legal: Art. 11 de la Ley 32069*"""
    },

    "parentesco_impedimento": {
        "preguntas": [
            "¿hasta qué grado de parentesco aplica el impedimento?",
            "grado parentesco impedimento",
            "parientes impedidos contratar",
            "familiares impedidos"
        ],
        "respuesta": """🚫 **Grado de Parentesco en Impedimentos**

El impedimento aplica hasta el **SEGUNDO GRADO** de consanguinidad o afinidad.

**Parientes por consanguinidad:**
• 1er grado: Padres, hijos
• 2do grado: Hermanos, abuelos, nietos

**Parientes por afinidad:**
• 1er grado: Suegros, yernos, nueras
• 2do grado: Cuñados

**Aplica cuando:**
El pariente es funcionario con capacidad de decisión en el proceso de contratación de la Entidad.

📚 *Base legal: Art. 11 literal k) de la Ley 32069*"""
    },

    # =========================================================================
    # COMPRADORES PÚBLICOS
    # =========================================================================

    "certificacion_compradores": {
        "preguntas": [
            "¿qué es la certificación de compradores públicos?",
            "certificacion compradores publicos",
            "como certificarse comprador publico",
            "es obligatoria la certificacion"
        ],
        "respuesta": """👔 **Certificación de Compradores Públicos**

Desde el D.S. N° 001-2026-EF, es **OBLIGATORIA** para funcionarios de la DEC.

**Niveles de certificación:**
• Básico
• Intermedio
• Avanzado

**Requisitos:**
• Título profesional técnico o grado de bachiller universitario
• Capacitación en contrataciones del Estado

**Emisor:** OECE

**Registro:** Se implementará el Registro de Compradores Públicos

📚 *Base legal: D.S. N° 001-2026-EF y Lineamientos de Conducta*"""
    },

    "lineamientos_conducta": {
        "preguntas": [
            "¿qué son los lineamientos de conducta?",
            "lineamientos conducta compradores",
            "normas eticas compradores publicos"
        ],
        "respuesta": """👔 **Lineamientos de Conducta para Compradores Públicos**

**Norma:** Resolución N° D000001-2026-OECE-PRE

**Fecha:** 9 de enero de 2026

**Aplica a:**
• Funcionarios de la DEC (Dependencia Encargada de Contrataciones)
• Servidores que participan en contrataciones

**Principios rectores:**
• Legalidad
• Transparencia
• Integridad
• Imparcialidad

**Incluye:**
• Deberes y obligaciones
• Prohibiciones
• Régimen disciplinario

📚 *Base legal: Resolución N° D000001-2026-OECE-PRE*"""
    },

    # =========================================================================
    # EJECUCIÓN CONTRACTUAL
    # =========================================================================

    "penalidad_mora": {
        "preguntas": [
            "¿cómo se calcula la penalidad por mora?",
            "calculo penalidad mora",
            "formula penalidad mora",
            "penalidad por atraso"
        ],
        "respuesta": """⚠️ **Cálculo de Penalidad por Mora**

**Fórmula:**
```
Penalidad = 0.05 x Monto Vigente / F x Días de Atraso
```

**Valor de F:**
• F = 0.25 → si el plazo es ≤ 60 días
• F = 0.40 → si el plazo es > 60 días

**Tope máximo:** 10% del monto del contrato vigente

**Ejemplo:**
Contrato de S/ 100,000 con 10 días de atraso (plazo > 60 días):
Penalidad = 0.05 x 100,000 / 0.40 x 10 = S/ 1,250 por día x 10 = **S/ 12,500**

📚 *Base legal: Art. 162 del D.S. N° 009-2025-EF*"""
    },

    "adicionales_obra": {
        "preguntas": [
            "¿cuál es el porcentaje máximo de adicionales de obra?",
            "adicionales de obra porcentaje",
            "limite adicionales obras",
            "prestaciones adicionales obras"
        ],
        "respuesta": """🏗️ **Adicionales de Obra**

**Límites:**
• **Hasta 15%:** Aprueba el Titular de la Entidad
• **Mayor a 15%:** Requiere autorización de la Contraloría
• **Hasta 50%:** Solo en caso de emergencia (Art. 34-A)

**Para bienes y servicios:**
• Hasta 25% del monto del contrato original

**Para consultorías de obra:**
• Hasta 25% del monto del contrato original

**Requisito:**
Necesidad no prevista en el expediente de contratación.

📚 *Base legal: Art. 34-A Ley 32069 y Art. 175 del Reglamento*"""
    },

    "resolucion_contrato": {
        "preguntas": [
            "¿cuáles son las causales de resolución de contrato?",
            "causales resolucion contrato",
            "como resolver un contrato",
            "cuando se resuelve el contrato"
        ],
        "respuesta": """📋 **Resolución de Contrato**

**Causales por parte de la Entidad:**
• Incumplimiento injustificado de obligaciones
• Acumulación del 10% de penalidades
• Paralización injustificada de la ejecución
• No obtención de licencias o autorizaciones

**Causales por parte del Contratista:**
• Incumplimiento de la Entidad de obligaciones esenciales
• Caso fortuito o fuerza mayor

**Procedimiento:**
1. Carta notarial requiriendo cumplimiento (mínimo 5 días)
2. Si no subsana: Carta notarial de resolución
3. Liquidación del contrato

📚 *Base legal: Arts. 167-171 del D.S. N° 009-2025-EF*"""
    },

    # NOTA: La entrada "ampliacion_plazo" fue consolidada en la sección de PENALIDADES
    # con información más completa (Arts. 170-173 del Reglamento)

    # =========================================================================
    # CONTROVERSIAS
    # =========================================================================

    "que_es_conciliacion": {
        "preguntas": [
            "¿qué es la conciliación en contrataciones?",
            "conciliacion contrataciones publicas",
            "cuando se usa conciliacion"
        ],
        "respuesta": """🤝 **Conciliación en Contrataciones Públicas**

Es un **mecanismo alternativo** de solución de controversias durante la ejecución contractual.

**Características:**
• Se realiza ante un Centro de Conciliación autorizado
• Es **obligatoria** para algunas materias antes del arbitraje
• Las partes buscan un acuerdo asistidos por un conciliador

**Materias conciliables:**
• Ampliación de plazo
• Valorización de prestaciones
• Liquidación del contrato
• Recepción y conformidad

**Resultado:**
• Si hay acuerdo: Acta de Conciliación con valor de cosa juzgada
• Si no hay acuerdo: Se puede ir a arbitraje

📚 *Base legal: Art. 72 de la Ley 32069*"""
    },

    "que_es_arbitraje": {
        "preguntas": [
            "¿cuándo es obligatorio el arbitraje?",
            "arbitraje contrataciones publicas",
            "cuando procede arbitraje",
            "tipos de arbitraje"
        ],
        "respuesta": """⚖️ **Arbitraje en Contrataciones Públicas**

**¿Cuándo es obligatorio?**
Para controversias durante la ejecución contractual que no se resuelvan por conciliación.

**Tipos:**
• **Arbitraje institucional:** Ante un centro arbitral acreditado
• **Arbitraje ad-hoc:** Árbitros designados por las partes

**Plazo para iniciar:**
**30 días hábiles** desde notificada la resolución o acto impugnado

**Supervisión:**
El OECE supervisa a las instituciones arbitrales (novedad 2026)

**Materias arbitrables:**
• Resolución de contrato
• Ampliación de plazo
• Adicionales y mayores gastos
• Valorizaciones
• Liquidación

📚 *Base legal: Arts. 72-74 de la Ley 32069*"""
    },

    "que_es_jprd": {
        "preguntas": [
            "¿qué es la jprd?",
            "que es jprd",
            "junta prevencion resolucion disputas",
            "jprd obras"
        ],
        "respuesta": """🏗️ **JPRD - Junta de Prevención y Resolución de Disputas**

**Definición:**
Órgano colegiado para **prevenir y resolver disputas** durante la ejecución de contratos de obra.

**¿Cuándo aplica?**
Obras con valor igual o superior a **S/ 20,000,000**

**Composición:**
• 1 miembro (obras menos complejas)
• 3 miembros (obras de mayor complejidad)

**Ventajas:**
• Decisiones rápidas durante la ejecución
• Previene conflictos antes de que escalen
• Evita paralización de obras

**Novedad 2026:**
El OECE asume la **supervisión directa** de las JPRD

📚 *Base legal: Art. 73 de la Ley 32069 y D.S. 001-2026-EF*"""
    },

    # =========================================================================
    # NOTICIAS OECE 2026
    # =========================================================================
    
    "comunicado_001_2026_oece": {
        "preguntas": [
            # Preguntas directas sobre el comunicado
            "comunicado 001-2026 oece consultores de obra",
            "¿qué dice el comunicado n°001-2026-oece?",
            "comunicado 001-2026 oece",
            "comunicado oece consultores",
            "noticias oece 2026",
            "noticias oece",
            # Preguntas sobre categorías
            "asignación de categorías consultores de obra",
            "categorías consultores obra ley 32069",
            "que categorias se otorgan segun el nuevo comunicado",
            "qué categorías se otorgan según el nuevo comunicado",
            "categorias de consultores de obra",
            "categorías de consultores de obra",
            "nuevas categorias consultores",
            "nuevas categorías consultores",
            "recategorizacion consultores obra",
            "recategorización consultores obra",
            # Preguntas sobre el proceso
            "plazo ampliacion categorias consultores",
            "120 dias habiles consultores",
            "como ampliar categorias consultores obra",
            "contratos menores consultores obra",
            # Pregunta larga original
            "¿qué dice el comunicado n°001-2026-oece sobre la asignación de especialidades y categorías de consultores de obra según la ley 32069?"
        ],
        "respuesta": """📰 **COMUNICADO N°001-2026-OECE** (19 de enero de 2026)
📋 **Asignación de Especialidades y Categorías de Consultores de Obra**

Este comunicado aplica el numeral 3 de la Cuarta Disposición Complementaria Transitoria del D.S. N° 009-2025-EF.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**🟢 CONSULTORES CON CATEGORÍA A (anterior Ley 30225):**
• El RNP les otorga **de oficio** TODAS las categorías del Art. 27.2 del Reglamento
• Solo habilitados para **CONTRATOS MENORES** en sus especialidades

**🟡 CONSULTORES CON CATEGORÍAS B, C o D (anterior Ley 30225):**
• El RNP les otorga **de oficio y provisionalmente** TODAS las categorías
• Habilitados para **CUALQUIER procedimiento de selección** en sus especialidades

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏰ **PLAZO IMPORTANTE:**
• **120 días hábiles** (desde el 19/01/2026) para solicitar **ampliación de categorías**
• Si **NO** solicitan en plazo → Solo quedan habilitados para contratos menores

📌 **REVALUACIÓN:**
En la primera reinscripción o ampliación, el OECE revaluará y asignará categorías según el Art. 27 del Reglamento.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔗 **Enlace oficial:** https://www.gob.pe/institucion/oece/noticias/1336986

📚 *Base legal: Cuarta Disposición Complementaria Transitoria del D.S. N° 009-2025-EF, Art. 27 del Reglamento*"""
    },
}



def buscar_respuesta_rapida(pregunta: str) -> str | None:
    """
    Busca una respuesta precalculada para la pregunta.
    Retorna None si no encuentra coincidencia.
    
    Sistema mejorado con 3 niveles de búsqueda:
    1. Coincidencia exacta
    2. Detección por palabras clave (temas críticos)
    3. Coincidencia por porcentaje de palabras
    """
    pregunta_lower = pregunta.lower().strip()
    
    # Limpiar caracteres especiales
    pregunta_clean = pregunta_lower.replace("¿", "").replace("?", "").replace("¡", "").replace("!", "").replace("°", "")
    
    # =========================================================================
    # NIVEL 1: BÚSQUEDA EXACTA
    # =========================================================================
    for key, data in RESPUESTAS_RAPIDAS.items():
        for pregunta_template in data["preguntas"]:
            template_clean = pregunta_template.replace("¿", "").replace("?", "").replace("°", "").lower()
            if pregunta_clean == template_clean:
                return data["respuesta"]
    
    # =========================================================================
    # NIVEL 2: DETECCIÓN POR PALABRAS CLAVE (TEMAS CRÍTICOS)
    # Detecta automáticamente temas específicos para evitar confusiones
    # Sistema de EXCLUSIONES para distinguir temas similares
    # =========================================================================
    
    # --- AMPLIACIÓN DE PLAZO (PRIORIDAD ALTA - detectar antes de penalidades) ---
    # Palabras clave de ampliación de plazo
    palabras_ampliacion = ["ampliacion", "ampliación", "prorroga", "prórroga", 
                           "extension", "extensión", "caso fortuito", "fuerza mayor",
                           "atrasos no imputables", "plazo adicional"]
    
    # Si contiene palabras de ampliación Y NO es claramente sobre penalidades
    if any(palabra in pregunta_clean for palabra in palabras_ampliacion):
        # Exclusiones: si menciona cálculo/fórmula/monto de penalidad, NO es ampliación
        exclusiones_ampliacion = ["formula", "fórmula", "calculo", "cálculo", 
                                   "10%", "tope", "multa", "calcular penalidad"]
        if not any(excl in pregunta_clean for excl in exclusiones_ampliacion):
            return RESPUESTAS_RAPIDAS.get("ampliacion_plazo", {}).get("respuesta")
    
    # --- PENALIDADES (PRIORIDAD ALTA) ---
    # Palabras que indican claramente una consulta sobre penalidades
    palabras_penalidad = ["penalidad", "penalidades", "mora", "multa"]
    exclusiones_penalidad = ["ampliacion", "ampliación", "prorroga", "prórroga", 
                             "extension", "extensión", "caso fortuito", "fuerza mayor"]
    
    if any(palabra in pregunta_clean for palabra in palabras_penalidad):
        # Verificar que NO sea una consulta de ampliación que menciona penalidades
        if not any(excl in pregunta_clean for excl in exclusiones_penalidad):
            # Si tiene datos de cálculo (monto, días, plazo) → Calcular penalidad
            if any(x in pregunta_clean for x in ["monto", "dias", "días", "plazo", "s/", "soles", "contrato", "atraso"]):
                # Esta es una consulta de cálculo de penalidad
                return RESPUESTAS_RAPIDAS.get("calculo_penalidad", {}).get("respuesta") or \
                       RESPUESTAS_RAPIDAS.get("penalidades", {}).get("respuesta")
    
    # --- PROCEDIMIENTOS DE SELECCIÓN ---
    if ("procedimiento" in pregunta_clean and "selección" in pregunta_clean) or \
       ("procedimiento" in pregunta_clean and "seleccion" in pregunta_clean) or \
       "licitacion" in pregunta_clean or "licitación" in pregunta_clean or \
       "concurso publico" in pregunta_clean or "concurso público" in pregunta_clean:
        if "abreviada" in pregunta_clean or "abreviado" in pregunta_clean:
            return RESPUESTAS_RAPIDAS.get("adjudicacion_simplificada", {}).get("respuesta")
        return RESPUESTAS_RAPIDAS.get("procedimientos_seleccion", {}).get("respuesta")
    
    # --- GARANTÍAS ---
    if "garantia" in pregunta_clean or "garantía" in pregunta_clean:
        if "fiel cumplimiento" in pregunta_clean:
            return RESPUESTAS_RAPIDAS.get("garantia_fiel_cumplimiento", {}).get("respuesta")
    
    # --- APELACIÓN ---
    if "apelacion" in pregunta_clean or "apelación" in pregunta_clean or \
       "apelar" in pregunta_clean or "recurso" in pregunta_clean:
        if "impugn" in pregunta_clean or "apel" in pregunta_clean:
            return RESPUESTAS_RAPIDAS.get("procedimiento_apelacion", {}).get("respuesta")
    
    # --- TRIBUNAL DE CONTRATACIONES ---
    if "tribunal" in pregunta_clean:
        if "sancion" in pregunta_clean or "sanción" in pregunta_clean or \
           "inhabilitacion" in pregunta_clean or "inhabilitación" in pregunta_clean:
            return RESPUESTAS_RAPIDAS.get("tribunal_sanciones", {}).get("respuesta")
    
    # --- OECE (antes OSCE) ---
    if "oece" in pregunta_clean or "osce" in pregunta_clean:
        if "diferencia" in pregunta_clean:
            return RESPUESTAS_RAPIDAS.get("diferencia_osce_oece", {}).get("respuesta")
        return RESPUESTAS_RAPIDAS.get("que_es_oece", {}).get("respuesta")
    
    # --- RNP ---
    if "rnp" in pregunta_clean:
        if "inscrib" in pregunta_clean or "registro" in pregunta_clean:
            return RESPUESTAS_RAPIDAS.get("inscripcion_rnp", {}).get("respuesta")
        if "experiencia" in pregunta_clean and ("reorgan" in pregunta_clean or "fusion" in pregunta_clean or "fusión" in pregunta_clean):
            return RESPUESTAS_RAPIDAS.get("experiencia_rnp", {}).get("respuesta")
        return RESPUESTAS_RAPIDAS.get("que_es_rnp", {}).get("respuesta")
    
    # --- PRINCIPIOS ---
    if "principio" in pregunta_clean or "principios" in pregunta_clean:
        if "cuantos" in pregunta_clean or "cuántos" in pregunta_clean:
            return RESPUESTAS_RAPIDAS.get("cantidad_principios", {}).get("respuesta")
        if "nuevo" in pregunta_clean:
            return RESPUESTAS_RAPIDAS.get("principios_nuevos", {}).get("respuesta")
        if "cuales" in pregunta_clean or "cuáles" in pregunta_clean or "lista" in pregunta_clean:
            return RESPUESTAS_RAPIDAS.get("lista_principios", {}).get("respuesta")
    
    # --- UIT y MONTOS ---
    if "uit" in pregunta_clean:
        return RESPUESTAS_RAPIDAS.get("uit_2026", {}).get("respuesta")
    if "monto minimo" in pregunta_clean or "monto mínimo" in pregunta_clean or "8 uit" in pregunta_clean:
        return RESPUESTAS_RAPIDAS.get("monto_minimo", {}).get("respuesta")
    
    # --- JPRD ---
    if "jprd" in pregunta_clean or "junta de prevencion" in pregunta_clean or \
       "junta de prevención" in pregunta_clean or "junta de resolucion de disputas" in pregunta_clean:
        return RESPUESTAS_RAPIDAS.get("que_es_jprd", {}).get("respuesta")
    
    # --- CAMBIOS 2026 ---
    if ("cambio" in pregunta_clean or "novedad" in pregunta_clean or "modificacion" in pregunta_clean) and \
       ("2026" in pregunta_clean or "001-2026" in pregunta_clean or "ds" in pregunta_clean):
        return RESPUESTAS_RAPIDAS.get("cambios_2026", {}).get("respuesta")
    
    # --- IMPEDIMENTOS ---
    if "impedido" in pregunta_clean or "impedidos" in pregunta_clean or "impedimento" in pregunta_clean:
        if "parentesco" in pregunta_clean or "grado" in pregunta_clean:
            return RESPUESTAS_RAPIDAS.get("parentesco_impedimento", {}).get("respuesta")
        return RESPUESTAS_RAPIDAS.get("quienes_impedidos", {}).get("respuesta")
    
    # --- SEACE / PLADICOP ---
    if "seace" in pregunta_clean:
        return RESPUESTAS_RAPIDAS.get("que_es_seace", {}).get("respuesta")
    if "pladicop" in pregunta_clean:
        return RESPUESTAS_RAPIDAS.get("que_es_pladicop", {}).get("respuesta")
    
    # --- Comunicado N°001-2026-OECE - Categorías de Consultores de Obra ---
    palabras_comunicado = ["comunicado", "001-2026", "oece", "consultores", "obra", "noticias"]
    palabras_categorias = ["categoria", "categorias", "categoría", "categorías", "recategorizacion", "recategorización", "otorgan", "otorga"]
    
    # Detección directa: "nuevo comunicado" + categorías
    if "nuevo" in pregunta_clean and "comunicado" in pregunta_clean:
        return RESPUESTAS_RAPIDAS.get("comunicado_001_2026_oece", {}).get("respuesta")
    
    # Detección: palabras clave del comunicado + contexto
    if any(palabra in pregunta_clean for palabra in palabras_comunicado):
        if any(palabra in pregunta_clean for palabra in palabras_categorias) or \
           "consultores" in pregunta_clean or "nuevo" in pregunta_clean or \
           "comunicado" in pregunta_clean:
            return RESPUESTAS_RAPIDAS.get("comunicado_001_2026_oece", {}).get("respuesta")
    
    # Detección: categorías + consultores de obra
    if ("categoria" in pregunta_clean or "categoría" in pregunta_clean or 
        "categorias" in pregunta_clean or "categorías" in pregunta_clean):
        if "consultores" in pregunta_clean or "obra" in pregunta_clean or "nuevo" in pregunta_clean:
            return RESPUESTAS_RAPIDAS.get("comunicado_001_2026_oece", {}).get("respuesta")
    
    # =========================================================================
    # NIVEL 3: COINCIDENCIA POR PORCENTAJE DE PALABRAS (70%)
    # =========================================================================
    for key, data in RESPUESTAS_RAPIDAS.items():
        for pregunta_template in data["preguntas"]:
            palabras_template = set(pregunta_template.lower().split())
            palabras_pregunta = set(pregunta_clean.split())
            
            if len(palabras_template) > 0:
                coincidencia = len(palabras_template.intersection(palabras_pregunta)) / len(palabras_template)
                if coincidencia >= 0.7:
                    return data["respuesta"]
    
    return None


def get_todas_las_preguntas() -> list:
    """Retorna una lista de todas las preguntas disponibles"""
    preguntas = []
    for key, data in RESPUESTAS_RAPIDAS.items():
        preguntas.extend(data["preguntas"])
    return preguntas
