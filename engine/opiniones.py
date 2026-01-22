"""
Módulo de Opiniones OECE (ex-OSCE)
Gestión y consulta de opiniones de la Dirección Técnico Normativa
"""
import os
import json
from datetime import datetime

class OpinionesOECE:
    """
    Gestiona las opiniones emitidas por la Dirección Técnico Normativa (DTN) del OECE
    Las opiniones son pronunciamientos que interpretan la normativa de contrataciones
    """
    
    # Base de conocimiento de opiniones recientes
    OPINIONES_2026 = [
        {
            "numero": "D000001-2026-OECE-DTN",
            "fecha": "2026-01-03",
            "tema": "Aplicación de la Ley 32069 en procedimientos iniciados bajo Ley 30225",
            "resumen": "Consulta sobre la aplicación temporal de la normativa de contrataciones",
            "palabras_clave": ["transitoriedad", "vigencia", "Ley 32069", "Ley 30225"]
        },
        {
            "numero": "D000002-2026-OECE-DTN",
            "fecha": "2026-01-05",
            "tema": "Requisitos de calificación en procedimientos abreviados",
            "resumen": "Interpretación sobre los requisitos de calificación aplicables",
            "palabras_clave": ["calificación", "procedimiento abreviado", "requisitos"]
        },
        {
            "numero": "D000003-2026-OECE-DTN",
            "fecha": "2026-01-08",
            "tema": "Garantías de fiel cumplimiento en contratos menores",
            "resumen": "Alcances de las modificaciones sobre garantías en el D.S. 001-2026-EF",
            "palabras_clave": ["garantías", "fiel cumplimiento", "contratos menores"]
        },
        {
            "numero": "D000004-2026-OECE-DTN",
            "fecha": "2026-01-10",
            "tema": "Subsanación de ofertas por parte de evaluadores",
            "resumen": "Límites y alcances de la facultad de subsanación",
            "palabras_clave": ["subsanación", "ofertas", "evaluadores", "errores formales"]
        },
        {
            "numero": "D000005-2026-OECE-DTN",
            "fecha": "2026-01-12",
            "tema": "Certificación de compradores públicos",
            "resumen": "Requisitos y proceso para obtener la certificación obligatoria",
            "palabras_clave": ["certificación", "compradores públicos", "OECE", "niveles"]
        },
        {
            "numero": "D000006-2026-OECE-DTN",
            "fecha": "2026-01-15",
            "tema": "Plazos en la difusión previa del requerimiento",
            "resumen": "Interpretación del nuevo plazo de 6 días hábiles para consulta al mercado",
            "palabras_clave": ["difusión", "requerimiento", "plazo", "consulta mercado"]
        },
        {
            "numero": "D000007-2026-OECE-DTN",
            "fecha": "2026-01-17",
            "tema": "Contratación directa en situaciones de emergencia",
            "resumen": "Alcances de la flexibilización de garantías y adelantos en emergencias",
            "palabras_clave": ["contratación directa", "emergencia", "garantías", "adelantos"]
        },
        {
            "numero": "D000008-2026-OECE-DTN",
            "fecha": "2026-01-19",
            "tema": "Experiencia en reorganización societaria para inscripción en RNP",
            "resumen": "Requisitos para acreditar experiencia proveniente de reorganización",
            "palabras_clave": ["RNP", "experiencia", "reorganización societaria", "inscripción"]
        }
    ]
    
    # Opiniones importantes de 2025
    OPINIONES_2025 = [
        {
            "numero": "D000095-2025-OECE-DTN",
            "fecha": "2025-12-20",
            "tema": "Aplicación de nuevos principios de la Ley 32069",
            "resumen": "Interpretación de los 5 nuevos principios incorporados",
            "palabras_clave": ["principios", "Ley 32069", "Valor por dinero", "Innovación"]
        },
        {
            "numero": "D000090-2025-OECE-DTN",
            "fecha": "2025-12-15",
            "tema": "Procedimientos de selección abreviados",
            "resumen": "Diferencias con la antigua adjudicación simplificada",
            "palabras_clave": ["procedimiento abreviado", "licitación abreviada", "concurso abreviado"]
        },
        {
            "numero": "D000085-2025-OECE-DTN",
            "fecha": "2025-12-10",
            "tema": "Funcionamiento de PLADICOP",
            "resumen": "Implementación de la Plataforma Digital de Contrataciones Públicas",
            "palabras_clave": ["PLADICOP", "plataforma digital", "SEACE", "RNP"]
        }
    ]
    
    def __init__(self):
        """Inicializa el gestor de opiniones"""
        self.todas_opiniones = self.OPINIONES_2026 + self.OPINIONES_2025
    
    def buscar_opinion(self, consulta: str) -> list:
        """
        Busca opiniones relevantes según la consulta
        
        Args:
            consulta: Texto de búsqueda
            
        Returns:
            Lista de opiniones relevantes
        """
        consulta_lower = consulta.lower()
        resultados = []
        
        for opinion in self.todas_opiniones:
            # Buscar en tema, resumen y palabras clave
            if any(palabra.lower() in consulta_lower for palabra in opinion['palabras_clave']):
                resultados.append(opinion)
            elif consulta_lower in opinion['tema'].lower():
                resultados.append(opinion)
            elif consulta_lower in opinion['resumen'].lower():
                resultados.append(opinion)
        
        return resultados[:5]  # Máximo 5 resultados
    
    def obtener_opinion_por_numero(self, numero: str) -> dict:
        """Obtiene una opinión específica por su número"""
        for opinion in self.todas_opiniones:
            if numero.upper() in opinion['numero'].upper():
                return opinion
        return None
    
    def listar_opiniones_recientes(self, cantidad: int = 5) -> list:
        """Lista las opiniones más recientes"""
        return self.OPINIONES_2026[:cantidad]
    
    def formatear_opinion(self, opinion: dict) -> str:
        """Formatea una opinión para mostrar"""
        return f"""📋 **Opinión N° {opinion['numero']}**
📅 Fecha: {opinion['fecha']}
📌 Tema: {opinion['tema']}
📝 Resumen: {opinion['resumen']}
🏷️ Palabras clave: {', '.join(opinion['palabras_clave'])}"""
    
    def formatear_lista_opiniones(self, opiniones: list) -> str:
        """Formatea una lista de opiniones"""
        if not opiniones:
            return "No se encontraron opiniones relacionadas."
        
        resultado = "📚 **OPINIONES ENCONTRADAS:**\n\n"
        for i, op in enumerate(opiniones, 1):
            resultado += f"{i}. **{op['numero']}** - {op['tema']}\n"
            resultado += f"   📅 {op['fecha']}\n\n"
        
        return resultado


def get_opiniones_info() -> str:
    """Retorna información general sobre las opiniones OECE"""
    return """📜 **OPINIONES DE LA DIRECCIÓN TÉCNICO NORMATIVA (DTN) - OECE**

Las opiniones son pronunciamientos que interpretan y aclaran la normativa de contrataciones públicas.

**¿Qué son?**
Son respuestas a consultas formuladas por entidades públicas o proveedores sobre la interpretación de la Ley N° 32069 y su Reglamento.

**Características:**
• Emitidas por la DTN del OECE
• Tienen carácter orientador, no vinculante
• Interpretan normas, no resuelven casos concretos
• Disponibles en: https://www.gob.pe/oece

**Opiniones recientes 2026:**
• D000001 a D000008-2026-OECE-DTN
• Temas: certificación de compradores, subsanación, garantías, RNP

**¿Cómo consultar?**
Pregúntame sobre un tema específico y buscaré opiniones relacionadas."""
