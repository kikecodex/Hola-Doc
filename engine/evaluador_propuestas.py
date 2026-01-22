"""
Módulo Evaluador de Propuestas Técnicas y Económicas
Ley N° 32069 - Arts. 77-78 del Reglamento D.S. N° 009-2025-EF

Este módulo permite:
1. Verificar si la evaluación técnica cumple con las bases
2. Verificar si la evaluación económica aplica la fórmula correcta
3. Detectar errores aritméticos en los cálculos
4. Generar informe de inconsistencias
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re


class EvaluadorPropuestas:
    """
    Evaluador inteligente de propuestas técnicas y económicas
    según Arts. 77-78 del Reglamento de la Ley 32069
    """
    
    # =========================================================================
    # FÓRMULAS DE EVALUACIÓN ECONÓMICA (Art. 78)
    # =========================================================================
    
    # Fórmula para bienes y servicios (precio menor = mejor)
    # PE = PmxPEB / Pi
    # PE = Puntaje económico
    # Pm = Precio más bajo
    # PEB = Puntaje máximo económico (100 por defecto)
    # Pi = Precio de la propuesta evaluada
    
    # Fórmula para consultoría (calidad-precio)
    # Puede variar según las bases
    
    PUNTAJE_ECONOMICO_MAXIMO = 100
    
    # Límites de evaluación
    LIMITE_INFERIOR_PRECIO = 0.90  # 90% del promedio (ofertas temerarias)
    
    # =========================================================================
    # TIPOS DE FACTORES DE EVALUACIÓN TÉCNICA
    # =========================================================================
    
    FACTORES_TECNICOS_TIPICOS = {
        "experiencia_postor": {
            "descripcion": "Experiencia del postor en actividades iguales o similares",
            "tipo_evaluacion": "cuantitativa",
            "unidad": "monto_acumulado",
            "verificacion": "Constancias, contratos, comprobantes de pago"
        },
        "experiencia_personal": {
            "descripcion": "Experiencia del personal clave propuesto",
            "tipo_evaluacion": "cuantitativa",
            "unidad": "meses_o_proyectos",
            "verificacion": "CV documentado, certificados de trabajo"
        },
        "mejoras_tecnicas": {
            "descripcion": "Mejoras técnicas ofrecidas adicionales al TDR",
            "tipo_evaluacion": "cualitativa",
            "unidad": "cumple_no_cumple",
            "verificacion": "Propuesta técnica"
        },
        "plazo_entrega": {
            "descripcion": "Reducción del plazo de entrega/ejecución",
            "tipo_evaluacion": "cuantitativa",
            "unidad": "dias",
            "verificacion": "Propuesta técnica"
        },
        "garantia_comercial": {
            "descripcion": "Período de garantía ofrecida",
            "tipo_evaluacion": "cuantitativa",
            "unidad": "meses",
            "verificacion": "Propuesta técnica"
        },
        "capacitacion": {
            "descripcion": "Horas o personal de capacitación ofrecidos",
            "tipo_evaluacion": "cuantitativa",
            "unidad": "horas",
            "verificacion": "Propuesta técnica"
        }
    }
    
    # =========================================================================
    # ERRORES COMUNES EN EVALUACIÓN
    # =========================================================================
    
    ERRORES_COMUNES = {
        "aritmetico": {
            "descripcion": "Error en operaciones matemáticas",
            "ejemplos": [
                "Suma incorrecta de puntajes parciales",
                "División mal calculada en puntaje económico",
                "Redondeo incorrecto"
            ],
            "gravedad": "ALTA",
            "consecuencia": "Puede cambiar el orden de prelación"
        },
        "formula_incorrecta": {
            "descripcion": "Aplicación de fórmula diferente a la del Art. 78",
            "ejemplos": [
                "Usar promedio en lugar de precio menor",
                "No considerar el puntaje máximo correcto",
                "Aplicar fórmula de consultoría a bienes"
            ],
            "gravedad": "ALTA",
            "consecuencia": "Nulidad de la evaluación"
        },
        "factor_no_establecido": {
            "descripcion": "Evaluación con factor no previsto en las bases",
            "ejemplos": [
                "Evaluar criterio no incluido en bases",
                "Añadir subfactores no especificados",
                "Modificar ponderaciones"
            ],
            "gravedad": "ALTA",
            "consecuencia": "Nulidad del procedimiento"
        },
        "documentacion_ignorada": {
            "descripcion": "No se consideró documentación válida presentada",
            "ejemplos": [
                "Omitir contrato en la suma de experiencia",
                "No valorar mejora técnica ofrecida",
                "Ignorar certificado válido"
            ],
            "gravedad": "MEDIA",
            "consecuencia": "Puntaje incorrecto"
        },
        "trato_desigual": {
            "descripcion": "Criterio diferente para postores",
            "ejemplos": [
                "Aceptar documento a uno y rechazar igual a otro",
                "Aplicar criterio distinto de validación",
                "Interpretación diferente de TDR"
            ],
            "gravedad": "ALTA",
            "consecuencia": "Nulidad por vulneración de igualdad de trato"
        },
        "requisito_subsanable": {
            "descripcion": "Descalificación por error subsanable",
            "ejemplos": [
                "Fecha incorrecta en documento",
                "Firma faltante subsanable",
                "Error de forma no de fondo"
            ],
            "gravedad": "MEDIA",
            "consecuencia": "Descalificación indebida"
        }
    }
    
    def __init__(self):
        pass
    
    # =========================================================================
    # VERIFICACIÓN DE EVALUACIÓN TÉCNICA
    # =========================================================================
    
    def verificar_evaluacion_tecnica(
        self,
        puntajes_bases: Dict[str, Dict],
        puntajes_otorgados: Dict[str, float],
        documentacion: Dict[str, any] = None
    ) -> Dict:
        """
        Verifica si la evaluación técnica fue correcta
        
        Args:
            puntajes_bases: Factores y puntajes establecidos en las bases
                           Ej: {"experiencia": {"maximo": 40, "metodologia": "..."}}
            puntajes_otorgados: Puntajes que el comité otorgó
                           Ej: {"experiencia": 30, "mejoras": 15}
            documentacion: Documentación presentada para validar
            
        Returns:
            Dict con análisis de la evaluación
        """
        inconsistencias = []
        advertencias = []
        puntaje_total_bases = 0
        puntaje_total_otorgado = 0
        
        # Verificar cada factor
        for factor, config in puntajes_bases.items():
            maximo = config.get("maximo", 0)
            puntaje_total_bases += maximo
            
            otorgado = puntajes_otorgados.get(factor, 0)
            puntaje_total_otorgado += otorgado
            
            # ¿Supera el máximo?
            if otorgado > maximo:
                inconsistencias.append({
                    "tipo": "puntaje_excede_maximo",
                    "factor": factor,
                    "maximo": maximo,
                    "otorgado": otorgado,
                    "descripcion": f"El puntaje de {factor} ({otorgado}) excede el máximo ({maximo})",
                    "gravedad": "ALTA"
                })
            
            # ¿Es negativo?
            if otorgado < 0:
                inconsistencias.append({
                    "tipo": "puntaje_negativo",
                    "factor": factor,
                    "otorgado": otorgado,
                    "descripcion": f"El puntaje de {factor} es negativo ({otorgado})",
                    "gravedad": "ALTA"
                })
        
        # Verificar factores no establecidos
        for factor, puntaje in puntajes_otorgados.items():
            if factor not in puntajes_bases:
                inconsistencias.append({
                    "tipo": "factor_no_establecido",
                    "factor": factor,
                    "puntaje": puntaje,
                    "descripcion": f"Se evaluó el factor '{factor}' que no está en las bases",
                    "gravedad": "ALTA"
                })
        
        # Verificar suma total
        suma_verificada = sum(puntajes_otorgados.values())
        if abs(suma_verificada - puntaje_total_otorgado) > 0.01:
            inconsistencias.append({
                "tipo": "error_aritmetico_suma",
                "suma_correcta": suma_verificada,
                "suma_reportada": puntaje_total_otorgado,
                "descripcion": f"Error en suma de puntajes: debería ser {suma_verificada}",
                "gravedad": "ALTA"
            })
        
        return {
            "puntaje_total_maximo": puntaje_total_bases,
            "puntaje_total_otorgado": puntaje_total_otorgado,
            "puntaje_verificado": suma_verificada,
            "inconsistencias": inconsistencias,
            "advertencias": advertencias,
            "evaluacion_correcta": len(inconsistencias) == 0,
            "cantidad_errores": len(inconsistencias)
        }
    
    # =========================================================================
    # VERIFICACIÓN DE EVALUACIÓN ECONÓMICA
    # =========================================================================
    
    def calcular_puntaje_economico(
        self,
        precio_propuesta: float,
        precio_menor: float,
        puntaje_economico_maximo: float = 100
    ) -> Dict:
        """
        Calcula el puntaje económico según Art. 78 del Reglamento
        
        Fórmula: PE = (Pm / Pi) x PEM
        donde:
            PE = Puntaje Económico
            Pm = Precio menor (propuesta más baja)
            Pi = Precio de la propuesta evaluada
            PEM = Puntaje Económico Máximo
        """
        if precio_propuesta <= 0:
            return {"error": "El precio de la propuesta debe ser mayor a cero"}
        
        if precio_menor <= 0:
            return {"error": "El precio menor debe ser mayor a cero"}
        
        # Calcular puntaje
        puntaje = (precio_menor / precio_propuesta) * puntaje_economico_maximo
        puntaje_redondeado = round(puntaje, 2)
        
        return {
            "precio_propuesta": precio_propuesta,
            "precio_menor": precio_menor,
            "puntaje_economico_maximo": puntaje_economico_maximo,
            "puntaje_calculado": puntaje_redondeado,
            "formula_aplicada": f"({precio_menor:,.2f} / {precio_propuesta:,.2f}) x {puntaje_economico_maximo} = {puntaje_redondeado}",
            "base_legal": "Art. 78 del D.S. N° 009-2025-EF"
        }
    
    def verificar_evaluacion_economica(
        self,
        propuestas: List[Dict],
        puntaje_economico_maximo: float = 100
    ) -> Dict:
        """
        Verifica la evaluación económica de todas las propuestas
        
        Args:
            propuestas: Lista de propuestas con precio y puntaje otorgado
                       Ej: [{"postor": "A", "precio": 100000, "puntaje_otorgado": 85}, ...]
            puntaje_economico_maximo: Puntaje máximo según bases
            
        Returns:
            Dict con análisis completo
        """
        if not propuestas:
            return {"error": "No hay propuestas para evaluar"}
        
        # Determinar precio menor
        precio_menor = min(p["precio"] for p in propuestas)
        
        # Verificar cada propuesta
        resultados = []
        inconsistencias = []
        
        for propuesta in propuestas:
            postor = propuesta.get("postor", "Sin nombre")
            precio = propuesta.get("precio", 0)
            puntaje_otorgado = propuesta.get("puntaje_otorgado", 0)
            
            # Calcular puntaje correcto
            calculo = self.calcular_puntaje_economico(precio, precio_menor, puntaje_economico_maximo)
            puntaje_correcto = calculo.get("puntaje_calculado", 0)
            
            # Diferencia
            diferencia = abs(puntaje_correcto - puntaje_otorgado)
            es_correcto = diferencia < 0.1  # tolerancia de 0.1 puntos
            
            resultado_postor = {
                "postor": postor,
                "precio": precio,
                "puntaje_otorgado": puntaje_otorgado,
                "puntaje_correcto": puntaje_correcto,
                "diferencia": round(diferencia, 2),
                "es_correcto": es_correcto
            }
            resultados.append(resultado_postor)
            
            if not es_correcto:
                inconsistencias.append({
                    "tipo": "error_calculo_economico",
                    "postor": postor,
                    "puntaje_otorgado": puntaje_otorgado,
                    "puntaje_correcto": puntaje_correcto,
                    "diferencia": round(diferencia, 2),
                    "descripcion": f"Error en puntaje de {postor}: debería ser {puntaje_correcto}, se otorgó {puntaje_otorgado}",
                    "gravedad": "ALTA"
                })
        
        # Verificar ofertas temerarias (< 90% del promedio)
        promedio_precios = sum(p["precio"] for p in propuestas) / len(propuestas)
        limite_inferior = promedio_precios * self.LIMITE_INFERIOR_PRECIO
        
        ofertas_temerarias = [
            p for p in propuestas 
            if p["precio"] < limite_inferior
        ]
        
        return {
            "precio_menor": precio_menor,
            "promedio_precios": round(promedio_precios, 2),
            "limite_inferior_90": round(limite_inferior, 2),
            "resultados_por_postor": resultados,
            "inconsistencias": inconsistencias,
            "ofertas_posiblemente_temerarias": ofertas_temerarias,
            "evaluacion_correcta": len(inconsistencias) == 0,
            "base_legal": "Art. 78 del D.S. N° 009-2025-EF"
        }
    
    # =========================================================================
    # VERIFICACIÓN DE ORDEN DE PRELACIÓN
    # =========================================================================
    
    def verificar_orden_prelacion(
        self,
        puntajes_totales: List[Dict],
        orden_buena_pro: List[str]
    ) -> Dict:
        """
        Verifica si el orden de prelación es correcto
        
        Args:
            puntajes_totales: Lista con postor y puntaje total
                             Ej: [{"postor": "A", "puntaje_total": 92.5}, ...]
            orden_buena_pro: Lista de postores en el orden de la buena pro
                            Ej: ["B", "A", "C"]
        """
        # Ordenar por puntaje (mayor a menor)
        ordenado_correcto = sorted(
            puntajes_totales, 
            key=lambda x: x["puntaje_total"], 
            reverse=True
        )
        
        orden_correcto = [p["postor"] for p in ordenado_correcto]
        
        # Comparar
        es_correcto = orden_correcto == orden_buena_pro
        
        discrepancias = []
        if not es_correcto:
            for i, (correcto, otorgado) in enumerate(zip(orden_correcto, orden_buena_pro)):
                if correcto != otorgado:
                    discrepancias.append({
                        "posicion": i + 1,
                        "deberia_ser": correcto,
                        "otorgado_a": otorgado,
                        "descripcion": f"En posición {i+1} debería estar {correcto} pero se otorgó a {otorgado}"
                    })
        
        return {
            "orden_correcto": orden_correcto,
            "orden_otorgado": orden_buena_pro,
            "es_correcto": es_correcto,
            "discrepancias": discrepancias,
            "puntajes_ordenados": ordenado_correcto
        }
    
    # =========================================================================
    # GENERACIÓN DE INFORME DE INCONSISTENCIAS
    # =========================================================================
    
    def generar_informe_inconsistencias(
        self,
        resultado_tecnica: Dict,
        resultado_economica: Dict,
        resultado_prelacion: Dict = None
    ) -> str:
        """
        Genera un informe completo de inconsistencias encontradas
        """
        informe = """
╔══════════════════════════════════════════════════════════════════════════════╗
║           INFORME DE VERIFICACIÓN DE EVALUACIÓN DE PROPUESTAS                ║
╚══════════════════════════════════════════════════════════════════════════════╝

Fecha de análisis: {fecha}

═══════════════════════════════════════════════════════════════════════════════
                    I. EVALUACIÓN TÉCNICA
═══════════════════════════════════════════════════════════════════════════════

Estado: {estado_tecnica}
Puntaje máximo posible: {puntaje_max_tecnico}
Puntaje otorgado: {puntaje_tecnico}

""".format(
            fecha=datetime.now().strftime("%d/%m/%Y %H:%M"),
            estado_tecnica="✅ CORRECTA" if resultado_tecnica.get("evaluacion_correcta") else "❌ CON ERRORES",
            puntaje_max_tecnico=resultado_tecnica.get("puntaje_total_maximo", "N/A"),
            puntaje_tecnico=resultado_tecnica.get("puntaje_total_otorgado", "N/A")
        )
        
        # Agregar inconsistencias técnicas
        inconsistencias_tecnicas = resultado_tecnica.get("inconsistencias", [])
        if inconsistencias_tecnicas:
            informe += "INCONSISTENCIAS DETECTADAS:\n"
            for i, inc in enumerate(inconsistencias_tecnicas, 1):
                informe += f"""
{i}. {inc['descripcion']}
   Tipo: {inc['tipo']}
   Gravedad: {inc['gravedad']}
"""
        else:
            informe += "No se detectaron inconsistencias en la evaluación técnica.\n"
        
        # Sección económica
        informe += """
═══════════════════════════════════════════════════════════════════════════════
                    II. EVALUACIÓN ECONÓMICA
═══════════════════════════════════════════════════════════════════════════════

Estado: {estado_economica}
Precio menor: S/ {precio_menor:,.2f}
Promedio de precios: S/ {promedio:,.2f}

""".format(
            estado_economica="✅ CORRECTA" if resultado_economica.get("evaluacion_correcta") else "❌ CON ERRORES",
            precio_menor=resultado_economica.get("precio_menor", 0),
            promedio=resultado_economica.get("promedio_precios", 0)
        )
        
        # Tabla de resultados económicos
        informe += "VERIFICACIÓN POR POSTOR:\n"
        informe += "─" * 70 + "\n"
        informe += f"{'Postor':<20} {'Precio':>15} {'Otorgado':>10} {'Correcto':>10} {'Estado':>10}\n"
        informe += "─" * 70 + "\n"
        
        for r in resultado_economica.get("resultados_por_postor", []):
            estado = "✅" if r["es_correcto"] else "❌"
            informe += f"{r['postor']:<20} {r['precio']:>15,.2f} {r['puntaje_otorgado']:>10.2f} {r['puntaje_correcto']:>10.2f} {estado:>10}\n"
        
        informe += "─" * 70 + "\n"
        
        # Inconsistencias económicas
        inconsistencias_economicas = resultado_economica.get("inconsistencias", [])
        if inconsistencias_economicas:
            informe += "\nINCONSISTENCIAS DETECTADAS:\n"
            for i, inc in enumerate(inconsistencias_economicas, 1):
                informe += f"""
{i}. {inc['descripcion']}
   Diferencia: {inc['diferencia']} puntos
   Gravedad: {inc['gravedad']}
"""
        
        # Ofertas temerarias
        temerarias = resultado_economica.get("ofertas_posiblemente_temerarias", [])
        if temerarias:
            informe += f"\n⚠️ OFERTAS POSIBLEMENTE TEMERARIAS (< 90% del promedio):\n"
            for t in temerarias:
                informe += f"   • {t['postor']}: S/ {t['precio']:,.2f}\n"
        
        # Orden de prelación
        if resultado_prelacion:
            informe += """
═══════════════════════════════════════════════════════════════════════════════
                    III. ORDEN DE PRELACIÓN
═══════════════════════════════════════════════════════════════════════════════

Estado: {estado_prelacion}
""".format(
                estado_prelacion="✅ CORRECTO" if resultado_prelacion.get("es_correcto") else "❌ INCORRECTO"
            )
            
            if not resultado_prelacion.get("es_correcto"):
                informe += f"\nOrden correcto debería ser: {', '.join(resultado_prelacion['orden_correcto'])}\n"
                informe += f"Orden otorgado fue: {', '.join(resultado_prelacion['orden_otorgado'])}\n"
                
                for disc in resultado_prelacion.get("discrepancias", []):
                    informe += f"\n⚠️ Posición {disc['posicion']}: debería ser {disc['deberia_ser']}, se otorgó a {disc['otorgado_a']}"
        
        # Conclusiones
        total_errores = len(inconsistencias_tecnicas) + len(inconsistencias_economicas)
        
        informe += """
═══════════════════════════════════════════════════════════════════════════════
                    IV. CONCLUSIONES Y RECOMENDACIONES
═══════════════════════════════════════════════════════════════════════════════

Total de errores detectados: {total_errores}

""".format(total_errores=total_errores)
        
        if total_errores > 0:
            informe += """RECOMENDACIÓN:
Se han detectado errores en la evaluación que podrían afectar el resultado 
del procedimiento de selección. Se recomienda:

1. INTERPONER RECURSO DE APELACIÓN dentro del plazo de 8 días hábiles
2. Fundamentar la apelación en los errores aquí documentados
3. Solicitar la corrección de los puntajes y/o la nulidad de la evaluación

Base legal: Arts. 97-103 del Reglamento D.S. N° 009-2025-EF
"""
        else:
            informe += """RECOMENDACIÓN:
No se detectaron errores significativos en la evaluación. Si considera que 
existe alguna irregularidad no detectada por este análisis, consulte con 
un especialista en contrataciones públicas.
"""
        
        return informe
    
    # =========================================================================
    # FORMATEO PARA CHAT
    # =========================================================================
    
    def formatear_resultado_verificacion(self, resultado: Dict, tipo: str) -> str:
        """Formatea resultado de verificación para chat"""
        
        if tipo == "tecnica":
            estado = "✅ CORRECTA" if resultado.get("evaluacion_correcta") else "❌ CON ERRORES"
            
            respuesta = f"""📋 **VERIFICACIÓN DE EVALUACIÓN TÉCNICA**

**Estado:** {estado}
**Puntaje máximo:** {resultado.get('puntaje_total_maximo', 'N/A')}
**Puntaje otorgado:** {resultado.get('puntaje_total_otorgado', 'N/A')}

"""
            if resultado.get("inconsistencias"):
                respuesta += "⚠️ **Errores detectados:**\n"
                for inc in resultado["inconsistencias"]:
                    respuesta += f"• {inc['descripcion']}\n"
            
            return respuesta
        
        elif tipo == "economica":
            estado = "✅ CORRECTA" if resultado.get("evaluacion_correcta") else "❌ CON ERRORES"
            
            respuesta = f"""💰 **VERIFICACIÓN DE EVALUACIÓN ECONÓMICA**

**Estado:** {estado}
**Precio menor:** S/ {resultado.get('precio_menor', 0):,.2f}
**Promedio:** S/ {resultado.get('promedio_precios', 0):,.2f}

"""
            if resultado.get("inconsistencias"):
                respuesta += "⚠️ **Errores detectados:**\n"
                for inc in resultado["inconsistencias"]:
                    respuesta += f"• {inc['descripcion']}\n"
            
            return respuesta
        
        return "Tipo de verificación no reconocido"
    
    def detect_and_process(self, message: str) -> Optional[str]:
        """Detecta si el mensaje es consulta sobre evaluación"""
        message_lower = message.lower()
        
        keywords = ['evaluación', 'evaluacion', 'evaluar', 'puntaje', 
                    'calificaron', 'calificación', 'error aritmético',
                    'propuesta técnica', 'propuesta económica']
        
        if not any(kw in message_lower for kw in keywords):
            return None
        
        return get_evaluador_info()


def get_evaluador_info() -> str:
    """Información general sobre evaluación de propuestas"""
    return """📊 **EVALUADOR DE PROPUESTAS**

**Base Legal:** Arts. 77-78 del D.S. N° 009-2025-EF

**¿Qué verifica este módulo?**

**1. Evaluación Técnica:**
• ✅ Puntajes dentro de los máximos establecidos
• ✅ Factores evaluados coinciden con las bases
• ✅ Suma correcta de puntajes parciales
• ✅ Trato igualitario a todos los postores

**2. Evaluación Económica:**
• ✅ Fórmula correcta: PE = (Pm/Pi) x PEM
• ✅ Identificación correcta del precio menor
• ✅ Cálculo correcto para cada postor
• ✅ Detección de ofertas temerarias (< 90%)

**3. Orden de Prelación:**
• ✅ Mayor puntaje = Primer lugar
• ✅ Coherencia con puntajes calculados

**Errores comunes detectados:**
❌ Errores aritméticos
❌ Fórmula incorrecta
❌ Factores no establecidos
❌ Documentación ignorada
❌ Trato desigual

**Para verificar una evaluación, proporcione:**
• Factores y puntajes de las bases
• Puntajes otorgados por el comité
• Precios de las propuestas económicas
• Orden de prelación otorgado

📚 *Base legal: Arts. 77-78 del Reglamento*"""
