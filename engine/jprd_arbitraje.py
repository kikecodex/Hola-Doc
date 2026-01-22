"""
Módulo de JPRD - Junta de Prevención y Resolución de Disputas
y Arbitraje en Contrataciones Públicas
Ley N° 32069 - Arts. 65-71 y Arts. 224-236 del Reglamento
"""
from typing import Dict, List, Optional


class JPRDArbitraje:
    """
    Gestiona información sobre JPRD (Dispute Boards) y Arbitraje
    en contrataciones públicas
    """
    
    # JPRD - Junta de Prevención y Resolución de Disputas
    JPRD_INFO = {
        "nombre": "Junta de Prevención y Resolución de Disputas",
        "siglas": "JPRD",
        "descripcion": "Mecanismo de solución de controversias en obras que permite resolver disputas durante la ejecución",
        "monto_obligatorio": 79000000,  # S/ 79 millones
        "base_legal": "Arts. 65-66 Ley 32069 y Arts. 224-226 del Reglamento",
        "ventajas": [
            "Resolución rápida durante la ejecución",
            "Menor costo que el arbitraje",
            "Junta conoce el proyecto desde el inicio",
            "Previene controversias antes de que escalen"
        ],
        "tipos": [
            {
                "tipo": "JPRD Permanente",
                "descripcion": "Se instala desde el inicio del contrato",
                "cuando": "Obras ≥ S/ 79,000,000",
                "miembros": 3
            },
            {
                "tipo": "JPRD Ad Hoc",
                "descripcion": "Se instala cuando surge una disputa",
                "cuando": "Obras < S/ 79,000,000 (opcional)",
                "miembros": "1 o 3"
            }
        ]
    }
    
    # Arbitraje en Contrataciones
    ARBITRAJE_INFO = {
        "descripcion": "Mecanismo de solución de controversias alternativo al Poder Judicial",
        "base_legal": "Arts. 67-71 Ley 32069 y Arts. 227-236 del Reglamento",
        "tipos": {
            "institucional": {
                "descripcion": "Administrado por una institución arbitral",
                "ventajas": ["Mayor predictibilidad", "Reglamento preestablecido", "Supervisión OECE"],
                "instituciones": "Supervisadas por el OECE"
            },
            "ad_hoc": {
                "descripcion": "Arbitraje sin institución, árbitros designados por las partes",
                "ventajas": ["Mayor flexibilidad", "Posiblemente menor costo"],
                "limitaciones": "Solo para controversias menores"
            }
        },
        "plazos": {
            "inicio": "30 días hábiles desde notificación de resolución o controversia",
            "laudo": "Depende del reglamento aplicable (usualmente 60-90 días)"
        }
    }
    
    # Materias arbitrables
    MATERIAS_ARBITRABLES = [
        "Resolución de contrato",
        "Ampliación de plazo",
        "Adicionales de obra",
        "Mayores gastos generales",
        "Penalidades",
        "Liquidación del contrato",
        "Vicios ocultos",
        "Indemnización por daños y perjuicios",
        "Valorizaciones",
        "Recepción de obra"
    ]
    
    # Materias NO arbitrables
    MATERIAS_NO_ARBITRABLES = [
        "Nulidad de contrato (competencia del Tribunal)",
        "Sanciones a proveedores",
        "Decisiones de la Entidad en procedimiento de selección",
        "Actos administrativos de fiscalización",
        "Determinación de responsabilidades administrativas"
    ]
    
    # Cláusula arbitral tipo
    CLAUSULA_ARBITRAL_TIPO = """
CLÁUSULA DE SOLUCIÓN DE CONTROVERSIAS

Las partes acuerdan que cualquier controversia que surja desde la celebración del contrato, 
durante su ejecución o ante su resolución, se resolverá mediante arbitraje de derecho.

El arbitraje será [INSTITUCIONAL/AD HOC], a cargo de [UN ÁRBITRO ÚNICO/TRIBUNAL ARBITRAL
DE TRES MIEMBROS], conforme al Reglamento del Centro de Arbitraje [NOMBRE], sede [CIUDAD].

La designación de árbitros se realizará conforme al artículo 229 del Reglamento de la Ley 
de Contrataciones del Estado. El laudo arbitral será definitivo e inapelable, tendrá valor 
de cosa juzgada y será ejecutable por la vía judicial.

Las partes renuncian expresamente al fuero judicial para la solución de controversias 
derivadas del presente contrato.
"""
    
    def __init__(self):
        pass
    
    def es_obligatoria_jprd(self, monto_obra: float) -> Dict:
        """
        Determina si es obligatoria la JPRD según el monto de la obra
        
        Args:
            monto_obra: Monto del contrato de obra
        """
        obligatoria = monto_obra >= self.JPRD_INFO["monto_obligatorio"]
        
        return {
            "monto_obra": monto_obra,
            "monto_obligatorio": self.JPRD_INFO["monto_obligatorio"],
            "es_obligatoria": obligatoria,
            "tipo_recomendado": "JPRD Permanente" if obligatoria else "JPRD Ad Hoc (opcional)",
            "miembros": 3 if obligatoria else "1 o 3 (a elección)",
            "momento_instalacion": "Desde inicio del contrato" if obligatoria else "Cuando surja disputa",
            "base_legal": self.JPRD_INFO["base_legal"]
        }
    
    def obtener_info_jprd(self) -> Dict:
        """Retorna información completa sobre JPRD"""
        return self.JPRD_INFO
    
    def obtener_info_arbitraje(self) -> Dict:
        """Retorna información sobre arbitraje"""
        return self.ARBITRAJE_INFO
    
    def obtener_clausula_tipo(self) -> str:
        """Retorna la cláusula arbitral tipo"""
        return self.CLAUSULA_ARBITRAL_TIPO
    
    def comparar_jprd_arbitraje(self) -> Dict:
        """Compara JPRD vs Arbitraje"""
        return {
            "comparacion": [
                {
                    "aspecto": "Momento de aplicación",
                    "jprd": "Durante la ejecución del contrato",
                    "arbitraje": "Después de la ejecución o resolución"
                },
                {
                    "aspecto": "Costo",
                    "jprd": "Menor (incluido en gastos generales)",
                    "arbitraje": "Mayor (honorarios árbitros + gastos)"
                },
                {
                    "aspecto": "Tiempo de resolución",
                    "jprd": "Rápido (14-28 días)",
                    "arbitraje": "Más largo (3-12 meses)"
                },
                {
                    "aspecto": "Tipo de resolución",
                    "jprd": "Recomendación o decisión",
                    "arbitraje": "Laudo definitivo"
                },
                {
                    "aspecto": "Efecto",
                    "jprd": "Ejecutable, salvo arbitraje posterior",
                    "arbitraje": "Cosa juzgada"
                }
            ]
        }
    
    def calcular_plazo_inicio_arbitraje(
        self,
        fecha_controversia: str
    ) -> Dict:
        """
        Calcula el plazo para iniciar arbitraje
        30 días hábiles desde la controversia
        """
        from engine.plazos import PlazosCalculator
        
        calc = PlazosCalculator()
        resultado = calc.calcular_plazo_generico(fecha_controversia, 30, "habiles")
        resultado["descripcion"] = "Plazo para iniciar arbitraje"
        resultado["base_legal"] = "Art. 227 del Reglamento"
        
        return resultado
    
    def formatear_resultado_jprd(self, resultado: Dict) -> str:
        """Formatea resultado de verificación JPRD"""
        obligatoria = "✅ SÍ ES OBLIGATORIA" if resultado['es_obligatoria'] else "❌ NO ES OBLIGATORIA (opcional)"
        
        return f"""🏗️ **JUNTA DE PREVENCIÓN Y RESOLUCIÓN DE DISPUTAS (JPRD)**

📋 **Consulta:**
• Monto de la obra: S/ {resultado['monto_obra']:,.2f}
• Monto obligatorio: S/ {resultado['monto_obligatorio']:,.0f}

📊 **Resultado:**
• **{obligatoria}**

📌 **Detalles:**
• Tipo recomendado: {resultado['tipo_recomendado']}
• Número de miembros: {resultado['miembros']}
• Momento de instalación: {resultado['momento_instalacion']}

📚 *Base legal: {resultado['base_legal']}*"""
    
    def detect_and_process(self, message: str) -> Optional[str]:
        """Detecta consultas sobre JPRD o arbitraje"""
        message_lower = message.lower()
        
        # Detectar JPRD
        if any(kw in message_lower for kw in ['jprd', 'junta de prevención', 'dispute board', 'junta de disputas']):
            return get_jprd_info()
        
        # Detectar arbitraje
        if any(kw in message_lower for kw in ['arbitraje', 'árbitro', 'arbitro', 'laudo', 'cláusula arbitral']):
            return get_arbitraje_info()
        
        return None


def get_jprd_info() -> str:
    """Información general sobre JPRD"""
    return """🏗️ **JUNTA DE PREVENCIÓN Y RESOLUCIÓN DE DISPUTAS (JPRD)**

**Base Legal:** Arts. 65-66 Ley 32069 y Arts. 224-226 del Reglamento

**¿Qué es?**
Mecanismo de solución de controversias que opera DURANTE la ejecución de obras, permitiendo resolver disputas de forma rápida.

**¿Cuándo es obligatoria?**
• Obras ≥ **S/ 79,000,000** → JPRD Obligatoria (3 miembros)
• Obras < S/ 79,000,000 → JPRD Opcional

**Ventajas:**
• ⚡ Resolución rápida (14-28 días)
• 💰 Menor costo que arbitraje
• 🏗️ La Junta conoce el proyecto desde el inicio
• 🛡️ Previene que controversias escalen

**¿Quién supervisa las JPRD?**
El OECE supervisa directamente a las JPRD según D.S. 001-2026-EF

**Procedimiento:**
1. Instalación de la Junta (inicio del contrato)
2. Presentación de disputa por cualquier parte
3. Audiencia y revisión de documentos
4. Decisión de la Junta
5. Ejecución o arbitraje posterior

📚 *Base legal: Arts. 65-66 Ley 32069*"""


def get_arbitraje_info() -> str:
    """Información sobre arbitraje"""
    return """⚖️ **ARBITRAJE EN CONTRATACIONES PÚBLICAS**

**Base Legal:** Arts. 67-71 Ley 32069 y Arts. 227-236 del Reglamento

**¿Qué es?**
Mecanismo alternativo de solución de controversias. Las partes renuncian al Poder Judicial y someten sus disputas a árbitros.

**Tipos de arbitraje:**
1. **Institucional:** Administrado por institución supervisada por OECE
2. **Ad Hoc:** Sin institución, árbitros elegidos por las partes

**Materias arbitrables:**
✅ Resolución de contrato
✅ Ampliación de plazo
✅ Adicionales y deductivos
✅ Penalidades
✅ Liquidación
✅ Valorizaciones

**Materias NO arbitrables:**
❌ Nulidad de contrato
❌ Sanciones a proveedores
❌ Actos del procedimiento de selección

**Plazos:**
• Inicio: **30 días hábiles** desde la controversia
• Laudo: Según reglamento (60-90 días)

**Supervisión:**
El OECE supervisa a las instituciones arbitrales desde D.S. 001-2026-EF

📚 *Base legal: Arts. 67-71 Ley 32069*"""
