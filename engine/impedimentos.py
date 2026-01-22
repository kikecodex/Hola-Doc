"""
Módulo de Verificación de Impedimentos para Contratar con el Estado
Ley N° 32069 - Artículo 11
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class ImpedimentosVerifier:
    """
    Verifica impedimentos para contratar con el Estado
    Según Art. 11 de la Ley N° 32069
    """
    
    # Categorías de impedidos (Art. 11 Ley 32069)
    IMPEDIDOS = {
        # Inciso a) - Máximas autoridades
        "presidente": {
            "cargo": "Presidente de la República",
            "vigencia_post_cese": 12,  # meses
            "alcance": "Nacional",
            "base_legal": "Art. 11, inc. a)"
        },
        "congresista": {
            "cargo": "Congresista de la República",
            "vigencia_post_cese": 12,
            "alcance": "Nacional",
            "base_legal": "Art. 11, inc. a)"
        },
        "ministro": {
            "cargo": "Ministro de Estado",
            "vigencia_post_cese": 12,
            "alcance": "Nacional (sector)",
            "base_legal": "Art. 11, inc. b)"
        },
        "viceministro": {
            "cargo": "Viceministro",
            "vigencia_post_cese": 12,
            "alcance": "Sector",
            "base_legal": "Art. 11, inc. b)"
        },
        
        # Inciso c) - Gobiernos regionales y locales
        "gobernador": {
            "cargo": "Gobernador Regional",
            "vigencia_post_cese": 12,
            "alcance": "Gobierno Regional y sus organismos",
            "base_legal": "Art. 11, inc. c)"
        },
        "vicegobernador": {
            "cargo": "Vicegobernador Regional",
            "vigencia_post_cese": 12,
            "alcance": "Gobierno Regional",
            "base_legal": "Art. 11, inc. c)"
        },
        "consejero_regional": {
            "cargo": "Consejero Regional",
            "vigencia_post_cese": 12,
            "alcance": "Gobierno Regional",
            "base_legal": "Art. 11, inc. c)"
        },
        "alcalde": {
            "cargo": "Alcalde",
            "vigencia_post_cese": 12,
            "alcance": "Municipalidad y sus organismos",
            "base_legal": "Art. 11, inc. d)"
        },
        "regidor": {
            "cargo": "Regidor",
            "vigencia_post_cese": 12,
            "alcance": "Municipalidad",
            "base_legal": "Art. 11, inc. d)"
        },
        
        # Inciso e) - Poder Judicial y Ministerio Público
        "juez_supremo": {
            "cargo": "Juez Supremo",
            "vigencia_post_cese": 12,
            "alcance": "Poder Judicial",
            "base_legal": "Art. 11, inc. e)"
        },
        "fiscal_supremo": {
            "cargo": "Fiscal Supremo",
            "vigencia_post_cese": 12,
            "alcance": "Ministerio Público",
            "base_legal": "Art. 11, inc. e)"
        },
        
        # Inciso f) - Órganos constitucionales
        "contralor": {
            "cargo": "Contralor General de la República",
            "vigencia_post_cese": 12,
            "alcance": "Contraloría",
            "base_legal": "Art. 11, inc. f)"
        },
        "defensor_pueblo": {
            "cargo": "Defensor del Pueblo",
            "vigencia_post_cese": 12,
            "alcance": "Defensoría del Pueblo",
            "base_legal": "Art. 11, inc. f)"
        },
        
        # Inciso g) - Titulares de entidades
        "titular_entidad": {
            "cargo": "Titular de la Entidad",
            "vigencia_post_cese": 12,
            "alcance": "La Entidad donde ejerció",
            "base_legal": "Art. 11, inc. g)"
        },
        
        # Inciso h) - Funcionarios con capacidad de decisión
        "funcionario_dec": {
            "cargo": "Funcionario con capacidad de decisión en contrataciones",
            "vigencia_post_cese": 12,
            "alcance": "La Entidad donde ejerce/ejerció",
            "base_legal": "Art. 11, inc. h)"
        },
        
        # Inciso i) - Servidores del OEC
        "servidor_oec": {
            "cargo": "Servidor del Órgano Encargado de Contrataciones",
            "vigencia_post_cese": 12,
            "alcance": "La Entidad donde ejerce",
            "base_legal": "Art. 11, inc. i)"
        }
    }
    
    # Grados de parentesco
    PARENTESCO = {
        "consanguinidad": {
            1: ["padre", "madre", "hijo", "hija"],
            2: ["hermano", "hermana", "abuelo", "abuela", "nieto", "nieta"]
        },
        "afinidad": {
            1: ["suegro", "suegra", "yerno", "nuera"],
            2: ["cuñado", "cuñada"]
        }
    }
    
    def __init__(self):
        pass
    
    def verificar_impedimento_cargo(
        self,
        cargo: str,
        meses_desde_cese: int = 0
    ) -> Dict:
        """
        Verifica si una persona está impedida por su cargo actual o anterior
        
        Args:
            cargo: Tipo de cargo (clave del diccionario IMPEDIDOS)
            meses_desde_cese: Meses desde que cesó en el cargo (0 si aún ejerce)
            
        Returns:
            Dict con resultado de verificación
        """
        cargo_lower = cargo.lower()
        
        # Buscar coincidencia
        cargo_info = None
        for key, info in self.IMPEDIDOS.items():
            if key in cargo_lower or cargo_lower in info["cargo"].lower():
                cargo_info = info
                break
        
        if not cargo_info:
            return {
                "impedido": False,
                "motivo": "Cargo no identificado en lista de impedidos",
                "recomendacion": "Verificar si el cargo tiene capacidad de decisión en contrataciones"
            }
        
        # Verificar vigencia
        vigencia = cargo_info["vigencia_post_cese"]
        
        if meses_desde_cese == 0:
            # Aún ejerce el cargo
            return {
                "impedido": True,
                "cargo": cargo_info["cargo"],
                "motivo": f"La persona ejerce actualmente el cargo de {cargo_info['cargo']}",
                "alcance": cargo_info["alcance"],
                "vigencia_impedimento": f"Mientras ejerza y hasta {vigencia} meses después de cesar",
                "base_legal": cargo_info["base_legal"]
            }
        elif meses_desde_cese < vigencia:
            # Dentro del período de impedimento post-cese
            meses_restantes = vigencia - meses_desde_cese
            return {
                "impedido": True,
                "cargo": cargo_info["cargo"],
                "motivo": f"El impedimento por haber sido {cargo_info['cargo']} aún está vigente",
                "alcance": cargo_info["alcance"],
                "meses_restantes": meses_restantes,
                "vigencia_impedimento": f"Faltan {meses_restantes} meses para que culmine el impedimento",
                "base_legal": cargo_info["base_legal"]
            }
        else:
            # Fuera del período de impedimento
            return {
                "impedido": False,
                "cargo": cargo_info["cargo"],
                "motivo": f"Han transcurrido más de {vigencia} meses desde el cese",
                "vigencia_cumplida": True,
                "base_legal": cargo_info["base_legal"]
            }
    
    def verificar_impedimento_parentesco(
        self,
        parentesco: str,
        cargo_funcionario: str
    ) -> Dict:
        """
        Verifica si existe impedimento por parentesco
        
        Args:
            parentesco: Tipo de parentesco (ej: "cuñado", "padre")
            cargo_funcionario: Cargo del funcionario público relacionado
        """
        parentesco_lower = parentesco.lower()
        grado = None
        tipo = None
        
        # Buscar el grado de parentesco
        for tipo_p, grados in self.PARENTESCO.items():
            for g, parientes in grados.items():
                if any(p in parentesco_lower for p in parientes):
                    grado = g
                    tipo = tipo_p
                    break
        
        if grado is None:
            return {
                "impedido": False,
                "motivo": "Tipo de parentesco no identificado",
                "recomendacion": "El impedimento aplica hasta 2do grado de consanguinidad/afinidad"
            }
        
        if grado <= 2:
            return {
                "impedido": True,
                "grado": grado,
                "tipo_parentesco": tipo,
                "parentesco": parentesco,
                "motivo": f"Impedido por ser pariente de {grado}° grado ({tipo}) de {cargo_funcionario}",
                "alcance": "La Entidad donde el funcionario tiene capacidad de decisión",
                "base_legal": "Art. 11, inc. k) Ley 32069"
            }
        else:
            return {
                "impedido": False,
                "grado": grado,
                "motivo": "El parentesco supera el 2do grado, no hay impedimento"
            }
    
    def obtener_lista_impedidos(self) -> List[Dict]:
        """Retorna la lista completa de cargos impedidos"""
        lista = []
        for key, info in self.IMPEDIDOS.items():
            lista.append({
                "codigo": key,
                "cargo": info["cargo"],
                "vigencia_post_cese": f"{info['vigencia_post_cese']} meses",
                "alcance": info["alcance"],
                "base_legal": info["base_legal"]
            })
        return lista
    
    def formatear_resultado(self, resultado: Dict) -> str:
        """Formatea el resultado para chat"""
        if resultado["impedido"]:
            return f"""🚫 **VERIFICACIÓN DE IMPEDIMENTO**

❌ **RESULTADO: IMPEDIDO**

📋 **Detalles:**
• Cargo: {resultado.get('cargo', resultado.get('parentesco', 'N/A'))}
• Motivo: {resultado['motivo']}
• Alcance: {resultado.get('alcance', 'N/A')}
{f"• Meses restantes: {resultado['meses_restantes']}" if 'meses_restantes' in resultado else ""}

⚠️ **CONSECUENCIAS DE CONTRATAR ESTANDO IMPEDIDO:**
• Nulidad del contrato
• Inhabilitación del proveedor
• Responsabilidad administrativa del funcionario

📚 *Base legal: {resultado.get('base_legal', 'Art. 11 Ley 32069')}*"""
        else:
            return f"""✅ **VERIFICACIÓN DE IMPEDIMENTO**

✅ **RESULTADO: NO IMPEDIDO**

📋 **Detalles:**
• {resultado['motivo']}
{f"• Nota: {resultado.get('recomendacion', '')}" if resultado.get('recomendacion') else ""}

📚 *Base legal: Art. 11 Ley 32069*"""
    
    def detect_and_verify(self, message: str) -> Optional[str]:
        """
        Detecta si el mensaje es consulta de impedimentos
        """
        message_lower = message.lower()
        
        keywords = ['impedido', 'impedimento', 'puede participar', 'puede contratar', 
                    'cuñado', 'pariente', 'familiar', 'hijo de', 'esposo de']
        
        if not any(kw in message_lower for kw in keywords):
            return None
        
        # Detectar parentesco
        parentescos = ['cuñado', 'cuñada', 'suegro', 'suegra', 'yerno', 'nuera',
                       'padre', 'madre', 'hijo', 'hija', 'hermano', 'hermana']
        
        parentesco_encontrado = None
        for p in parentescos:
            if p in message_lower:
                parentesco_encontrado = p
                break
        
        # Detectar cargo
        cargos = ['alcalde', 'gobernador', 'regidor', 'director', 'funcionario', 
                  'gerente', 'jefe', 'titular']
        
        cargo_encontrado = "funcionario con capacidad de decisión"
        for c in cargos:
            if c in message_lower:
                cargo_encontrado = c
                break
        
        if parentesco_encontrado:
            resultado = self.verificar_impedimento_parentesco(
                parentesco_encontrado, 
                cargo_encontrado
            )
            return self.formatear_resultado(resultado)
        
        return get_impedimentos_info()


def get_impedimentos_info() -> str:
    """Retorna información general sobre impedimentos"""
    return """🚫 **IMPEDIMENTOS PARA CONTRATAR CON EL ESTADO**

**Base Legal:** Art. 11 de la Ley N° 32069

**Principales impedidos:**

| Categoría | Vigencia post-cese |
|-----------|-------------------|
| Presidente, Congresistas, Ministros | 12 meses |
| Gobernadores, Alcaldes, Regidores | 12 meses |
| Titulares de Entidad | 12 meses |
| Funcionarios del OEC | 12 meses |

**Impedimento por parentesco:**
• Hasta **2do grado** de consanguinidad o afinidad
• 1er grado: padres, hijos, suegros, yernos
• 2do grado: hermanos, abuelos, cuñados

**Consecuencias:**
• Nulidad del contrato
• Inhabilitación del proveedor
• Responsabilidad del funcionario

📝 **Para verificar, indique:**
• Cargo de la persona
• Parentesco (si aplica)
• Tiempo desde el cese (si ya no ejerce)

📚 *Base legal: Art. 11 Ley 32069*"""
