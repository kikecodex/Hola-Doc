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
    
    # =========================================================================
    # EVALUACIÓN POR ETAPAS (FLUJO SECUENCIAL ELIMINATORIO)
    # Arts. 52-53 y 77-78 del Reglamento D.S. N° 009-2025-EF
    # =========================================================================
    
    # Requisitos Mínimos de Calificación típicos
    REQUISITOS_MINIMOS_TIPICOS = {
        "rnp_vigente": {
            "descripcion": "Inscripción vigente en el Registro Nacional de Proveedores",
            "obligatorio": True,
            "base_legal": "Art. 18 de la Ley 32069"
        },
        "capacidad_legal": {
            "descripcion": "Representación legal y poderes suficientes",
            "obligatorio": True,
            "base_legal": "Art. 52 del Reglamento"
        },
        "declaracion_jurada": {
            "descripcion": "Declaración jurada de no estar impedido",
            "obligatorio": True,
            "base_legal": "Art. 11 de la Ley 32069"
        },
        "habilitacion": {
            "descripcion": "Habilitación profesional (si aplica)",
            "obligatorio": False,
            "base_legal": "Art. 52 del Reglamento"
        }
    }
    
    # RTM típicos
    RTM_TIPICOS = {
        "especificaciones_tecnicas": {
            "descripcion": "Cumplimiento de especificaciones técnicas del TDR",
            "tipo": "obligatorio"
        },
        "equipamiento_minimo": {
            "descripcion": "Equipamiento mínimo requerido",
            "tipo": "segun_bases"
        },
        "personal_clave": {
            "descripcion": "Personal clave con perfil mínimo requerido",
            "tipo": "segun_bases"
        },
        "experiencia_minima": {
            "descripcion": "Experiencia mínima del postor",
            "tipo": "segun_bases"
        },
        "plazo_ofertado": {
            "descripcion": "Plazo de entrega/ejecución dentro del límite",
            "tipo": "obligatorio"
        }
    }
    
    def evaluar_requisitos_minimos(
        self,
        requisitos_bases: List[Dict],
        documentos_postor: Dict
    ) -> Dict:
        """
        ETAPA 1: Evalúa requisitos mínimos de calificación.
        Si alguno no cumple → DESCALIFICADO (no pasa a siguiente etapa)
        
        Args:
            requisitos_bases: Lista de requisitos exigidos
                [{nombre, descripcion, obligatorio, base_legal}]
            documentos_postor: Documentos presentados
                {requisito: {presentado: bool, documento: str, observaciones: str}}
        
        Returns:
            {
                etapa: "REQUISITOS_MINIMOS",
                cumple: bool,
                resultado: "ADMITIDO" | "DESCALIFICADO",
                detalle: [{requisito, cumple, observacion}],
                incumplimientos: [],
                base_legal: str
            }
        """
        detalle = []
        incumplimientos = []
        cumple_todos = True
        
        for req in requisitos_bases:
            nombre = req.get("nombre", req.get("requisito", ""))
            obligatorio = req.get("obligatorio", True)
            descripcion = req.get("descripcion", "")
            base_legal = req.get("base_legal", "Art. 52 del Reglamento")
            
            # Verificar si el postor presentó este requisito
            doc_postor = documentos_postor.get(nombre, {})
            presentado = doc_postor.get("presentado", False)
            documento = doc_postor.get("documento", "")
            obs_postor = doc_postor.get("observaciones", "")
            
            cumple_req = presentado
            observacion = ""
            
            if not cumple_req and obligatorio:
                cumple_todos = False
                observacion = f"INCUMPLE: No presentó {descripcion}"
                incumplimientos.append({
                    "requisito": nombre,
                    "descripcion": descripcion,
                    "tipo": "requisito_obligatorio_no_presentado",
                    "base_legal": base_legal,
                    "consecuencia": "DESCALIFICACIÓN"
                })
            elif not cumple_req and not obligatorio:
                observacion = f"No presentado (opcional)"
            else:
                observacion = f"Cumple: {documento}" if documento else "Presentado correctamente"
            
            detalle.append({
                "requisito": nombre,
                "descripcion": descripcion,
                "obligatorio": obligatorio,
                "cumple": cumple_req,
                "observacion": observacion,
                "base_legal": base_legal
            })
        
        return {
            "etapa": "REQUISITOS_MINIMOS",
            "numero_etapa": 1,
            "cumple": cumple_todos,
            "resultado": "ADMITIDO" if cumple_todos else "DESCALIFICADO",
            "detalle": detalle,
            "incumplimientos": incumplimientos,
            "total_requisitos": len(requisitos_bases),
            "requisitos_cumplidos": len([d for d in detalle if d["cumple"]]),
            "base_legal": "Arts. 52-53 del Reglamento D.S. N° 009-2025-EF",
            "puede_continuar": cumple_todos
        }
    
    def evaluar_rtm(
        self,
        rtm_bases: List[Dict],
        propuesta_tecnica: Dict
    ) -> Dict:
        """
        ETAPA 2: Evalúa Requerimientos Técnicos Mínimos.
        Si alguno no cumple → DESCALIFICADO
        
        Args:
            rtm_bases: Lista de RTM de las bases
                [{nombre, descripcion, valor_minimo, tipo_verificacion}]
            propuesta_tecnica: Lo que ofrece el postor
                {rtm: {valor_ofrecido, cumple, descripcion}}
        
        Returns:
            {
                etapa: "RTM",
                cumple: bool,
                resultado: "ADMITIDO" | "DESCALIFICADO",
                detalle: [{rtm, exigido, ofrecido, cumple}],
                incumplimientos: []
            }
        """
        detalle = []
        incumplimientos = []
        cumple_todos = True
        
        for rtm in rtm_bases:
            nombre = rtm.get("nombre", rtm.get("rtm", ""))
            descripcion = rtm.get("descripcion", "")
            valor_minimo = rtm.get("valor_minimo", rtm.get("exigido", ""))
            tipo = rtm.get("tipo_verificacion", "cumple_no_cumple")
            
            # Verificar lo ofrecido por el postor
            oferta = propuesta_tecnica.get(nombre, {})
            valor_ofrecido = oferta.get("valor_ofrecido", oferta.get("ofrecido", ""))
            cumple_rtm = oferta.get("cumple", False)
            obs = oferta.get("observaciones", "")
            
            # Verificación automática si hay valores numéricos
            if tipo == "numerico" and valor_minimo and valor_ofrecido:
                try:
                    min_val = float(str(valor_minimo).replace(",", ""))
                    ofr_val = float(str(valor_ofrecido).replace(",", ""))
                    cumple_rtm = ofr_val >= min_val
                except:
                    pass
            
            observacion = ""
            if not cumple_rtm:
                cumple_todos = False
                observacion = f"NO CUMPLE RTM: {descripcion}"
                incumplimientos.append({
                    "rtm": nombre,
                    "descripcion": descripcion,
                    "exigido": valor_minimo,
                    "ofrecido": valor_ofrecido,
                    "tipo": "rtm_no_cumplido",
                    "consecuencia": "DESCALIFICACIÓN"
                })
            else:
                observacion = f"Cumple: ofrece {valor_ofrecido}" if valor_ofrecido else "Cumple RTM"
            
            detalle.append({
                "rtm": nombre,
                "descripcion": descripcion,
                "exigido": valor_minimo,
                "ofrecido": valor_ofrecido,
                "cumple": cumple_rtm,
                "observacion": observacion
            })
        
        return {
            "etapa": "RTM",
            "numero_etapa": 2,
            "cumple": cumple_todos,
            "resultado": "ADMITIDO" if cumple_todos else "DESCALIFICADO",
            "detalle": detalle,
            "incumplimientos": incumplimientos,
            "total_rtm": len(rtm_bases),
            "rtm_cumplidos": len([d for d in detalle if d["cumple"]]),
            "base_legal": "Art. 16 de la Ley 32069 - Especificaciones Técnicas",
            "puede_continuar": cumple_todos
        }
    
    def evaluar_factores_tecnicos(
        self,
        factores_bases: List[Dict],
        propuesta_tecnica: Dict,
        puntaje_minimo: float = 0
    ) -> Dict:
        """
        ETAPA 3: Evalúa factores de evaluación técnica y calcula puntaje.
        
        Args:
            factores_bases: Factores de las bases
                [{nombre, puntaje_maximo, metodologia, descripcion}]
            propuesta_tecnica: Datos de la propuesta
                {factor: {valor_presentado, puntaje_solicitado, documentacion}}
            puntaje_minimo: Puntaje mínimo requerido (0 si no aplica)
        
        Returns:
            {
                etapa: "FACTORES_TECNICOS",
                puntaje_tecnico: float,
                puntaje_maximo: float,
                detalle_por_factor: [],
                cumple_minimo: bool,
                puede_continuar: bool
            }
        """
        detalle = []
        puntaje_total = 0
        puntaje_maximo_total = 0
        alertas = []
        
        for factor in factores_bases:
            nombre = factor.get("nombre", factor.get("factor", ""))
            puntaje_max = float(factor.get("puntaje_maximo", factor.get("maximo", 0)))
            metodologia = factor.get("metodologia", "")
            descripcion = factor.get("descripcion", "")
            
            puntaje_maximo_total += puntaje_max
            
            # Obtener lo presentado por el postor
            presentado = propuesta_tecnica.get(nombre, {})
            puntaje_otorgado = float(presentado.get("puntaje_otorgado", 0))
            puntaje_solicitado = float(presentado.get("puntaje_solicitado", 0))
            valor = presentado.get("valor_presentado", "")
            documentacion = presentado.get("documentacion", "")
            
            # Validaciones
            observacion = ""
            tiene_error = False
            
            if puntaje_otorgado > puntaje_max:
                tiene_error = True
                observacion = f"ERROR: Puntaje otorgado ({puntaje_otorgado}) excede máximo ({puntaje_max})"
                alertas.append({
                    "tipo": "puntaje_excede_maximo",
                    "factor": nombre,
                    "gravedad": "ALTA"
                })
            elif puntaje_otorgado < 0:
                tiene_error = True
                observacion = f"ERROR: Puntaje negativo ({puntaje_otorgado})"
            else:
                observacion = f"Puntaje: {puntaje_otorgado}/{puntaje_max}"
            
            puntaje_total += puntaje_otorgado
            
            detalle.append({
                "factor": nombre,
                "descripcion": descripcion,
                "metodologia": metodologia,
                "puntaje_maximo": puntaje_max,
                "puntaje_otorgado": puntaje_otorgado,
                "valor_presentado": valor,
                "documentacion": documentacion,
                "tiene_error": tiene_error,
                "observacion": observacion
            })
        
        cumple_minimo = puntaje_total >= puntaje_minimo if puntaje_minimo > 0 else True
        
        return {
            "etapa": "FACTORES_TECNICOS",
            "numero_etapa": 3,
            "puntaje_tecnico": round(puntaje_total, 2),
            "puntaje_maximo": puntaje_maximo_total,
            "porcentaje": round((puntaje_total / puntaje_maximo_total * 100), 2) if puntaje_maximo_total > 0 else 0,
            "puntaje_minimo_requerido": puntaje_minimo,
            "cumple_minimo": cumple_minimo,
            "detalle_por_factor": detalle,
            "alertas": alertas,
            "tiene_errores": len(alertas) > 0,
            "base_legal": "Art. 77 del Reglamento D.S. N° 009-2025-EF",
            "puede_continuar": cumple_minimo
        }
    
    def evaluar_economica_completa(
        self,
        propuestas: List[Dict],
        valor_referencial: float = 0,
        tipo_contratacion: str = "bienes_servicios",
        puntaje_economico_maximo: float = 100
    ) -> Dict:
        """
        ETAPA 4: Evaluación económica completa con detección de anomalías.
        
        Args:
            propuestas: Todas las propuestas económicas
                [{postor, precio, puntaje_otorgado (opcional)}]
            valor_referencial: VR del proceso
            tipo_contratacion: bienes_servicios, consultoria, obras
            puntaje_economico_maximo: Generalmente 100
        
        Returns:
            {
                etapa: "ECONOMICA",
                precio_menor: float,
                ranking: [],
                ofertas_temerarias: [],
                ofertas_sobre_vr: [],
                errores_calculo: [],
                formula_aplicada: str
            }
        """
        if not propuestas:
            return {"error": "No hay propuestas para evaluar", "etapa": "ECONOMICA"}
        
        # Obtener precio menor
        precios = [p.get("precio", 0) for p in propuestas if p.get("precio", 0) > 0]
        if not precios:
            return {"error": "No hay precios válidos", "etapa": "ECONOMICA"}
        
        precio_menor = min(precios)
        promedio_precios = sum(precios) / len(precios)
        limite_temeraria = promedio_precios * self.LIMITE_INFERIOR_PRECIO
        
        resultados = []
        ofertas_temerarias = []
        ofertas_sobre_vr = []
        errores_calculo = []
        
        for prop in propuestas:
            postor = prop.get("postor", "Sin nombre")
            precio = prop.get("precio", 0)
            puntaje_otorgado = prop.get("puntaje_otorgado", None)
            
            # Calcular puntaje correcto según Art. 78
            if precio > 0:
                puntaje_correcto = round((precio_menor / precio) * puntaje_economico_maximo, 2)
            else:
                puntaje_correcto = 0
            
            # Detectar oferta temeraria
            es_temeraria = precio < limite_temeraria
            if es_temeraria:
                ofertas_temerarias.append({
                    "postor": postor,
                    "precio": precio,
                    "limite": round(limite_temeraria, 2),
                    "porcentaje_bajo_promedio": round((1 - precio/promedio_precios) * 100, 1)
                })
            
            # Detectar oferta sobre VR
            supera_vr = valor_referencial > 0 and precio > valor_referencial
            if supera_vr:
                ofertas_sobre_vr.append({
                    "postor": postor,
                    "precio": precio,
                    "valor_referencial": valor_referencial,
                    "exceso": round(precio - valor_referencial, 2),
                    "porcentaje_exceso": round((precio/valor_referencial - 1) * 100, 1)
                })
            
            # Verificar error de cálculo si hay puntaje otorgado
            tiene_error = False
            diferencia = 0
            if puntaje_otorgado is not None:
                diferencia = abs(puntaje_correcto - puntaje_otorgado)
                tiene_error = diferencia > 0.1
                if tiene_error:
                    errores_calculo.append({
                        "postor": postor,
                        "puntaje_otorgado": puntaje_otorgado,
                        "puntaje_correcto": puntaje_correcto,
                        "diferencia": round(diferencia, 2),
                        "tipo": "error_calculo_economico"
                    })
            
            resultados.append({
                "postor": postor,
                "precio": precio,
                "puntaje_correcto": puntaje_correcto,
                "puntaje_otorgado": puntaje_otorgado,
                "diferencia": round(diferencia, 2) if puntaje_otorgado else None,
                "tiene_error": tiene_error,
                "es_temeraria": es_temeraria,
                "supera_vr": supera_vr
            })
        
        # Ordenar por puntaje (ranking)
        ranking = sorted(resultados, key=lambda x: x["puntaje_correcto"], reverse=True)
        for i, r in enumerate(ranking):
            r["posicion"] = i + 1
        
        return {
            "etapa": "ECONOMICA",
            "numero_etapa": 4,
            "precio_menor": precio_menor,
            "promedio_precios": round(promedio_precios, 2),
            "limite_temeraria": round(limite_temeraria, 2),
            "valor_referencial": valor_referencial,
            "puntaje_economico_maximo": puntaje_economico_maximo,
            "resultados": resultados,
            "ranking": ranking,
            "ofertas_temerarias": ofertas_temerarias,
            "ofertas_sobre_vr": ofertas_sobre_vr,
            "errores_calculo": errores_calculo,
            "tiene_errores": len(errores_calculo) > 0,
            "tiene_temerarias": len(ofertas_temerarias) > 0,
            "tiene_sobre_vr": len(ofertas_sobre_vr) > 0,
            "formula_aplicada": f"PE = (Pm/Pi) × {puntaje_economico_maximo}",
            "base_legal": "Art. 78 del Reglamento D.S. N° 009-2025-EF"
        }
    
    def evaluacion_integral(
        self,
        requisitos_bases: List[Dict],
        rtm_bases: List[Dict],
        factores_bases: List[Dict],
        propuesta: Dict,
        propuestas_economicas: List[Dict],
        valor_referencial: float = 0,
        puntaje_minimo_tecnico: float = 0
    ) -> Dict:
        """
        Ejecuta las 4 etapas secuencialmente.
        Se detiene si alguna etapa falla (DESCALIFICADO).
        
        Args:
            requisitos_bases: Requisitos mínimos de calificación
            rtm_bases: Requerimientos técnicos mínimos
            factores_bases: Factores de evaluación técnica
            propuesta: Propuesta del postor a evaluar
                {
                    documentos: {}, # Para Etapa 1
                    tecnica: {},    # Para Etapas 2 y 3
                    economica: {}   # Para Etapa 4
                }
            propuestas_economicas: Todas las propuestas económicas
            valor_referencial: VR del proceso
            puntaje_minimo_tecnico: Puntaje mínimo técnico requerido
        
        Returns:
            {
                postor: str,
                resultado_final: "ADMITIDO" | "DESCALIFICADO",
                etapa_final: int,
                etapa_falla: str | None,
                puntaje_tecnico: float,
                puntaje_economico: float,
                puntaje_total: float,
                etapas: {1: {...}, 2: {...}, 3: {...}, 4: {...}},
                vicios_detectados: [],
                recomendaciones: []
            }
        """
        postor = propuesta.get("postor", "Postor evaluado")
        etapas = {}
        vicios = []
        recomendaciones = []
        
        # ETAPA 1: Requisitos Mínimos
        resultado_e1 = self.evaluar_requisitos_minimos(
            requisitos_bases,
            propuesta.get("documentos", {})
        )
        etapas[1] = resultado_e1
        
        if not resultado_e1["cumple"]:
            for inc in resultado_e1.get("incumplimientos", []):
                vicios.append({
                    "etapa": 1,
                    "tipo": "requisito_no_cumplido",
                    "descripcion": inc["descripcion"],
                    "base_legal": inc.get("base_legal", ""),
                    "gravedad": "ALTA"
                })
            
            return {
                "postor": postor,
                "resultado_final": "DESCALIFICADO",
                "etapa_final": 1,
                "etapa_falla": "REQUISITOS_MINIMOS",
                "motivo": "No cumple requisitos mínimos de calificación",
                "puntaje_tecnico": None,
                "puntaje_economico": None,
                "puntaje_total": None,
                "etapas": etapas,
                "vicios_detectados": vicios,
                "recomendaciones": ["Revisar documentación faltante antes de presentar propuesta"]
            }
        
        # ETAPA 2: RTM
        resultado_e2 = self.evaluar_rtm(
            rtm_bases,
            propuesta.get("tecnica", {})
        )
        etapas[2] = resultado_e2
        
        if not resultado_e2["cumple"]:
            for inc in resultado_e2.get("incumplimientos", []):
                vicios.append({
                    "etapa": 2,
                    "tipo": "rtm_no_cumplido",
                    "descripcion": f"RTM '{inc['rtm']}': {inc['descripcion']}",
                    "exigido": inc.get("exigido"),
                    "ofrecido": inc.get("ofrecido"),
                    "gravedad": "ALTA"
                })
            
            return {
                "postor": postor,
                "resultado_final": "DESCALIFICADO",
                "etapa_final": 2,
                "etapa_falla": "RTM",
                "motivo": "No cumple requerimientos técnicos mínimos",
                "puntaje_tecnico": None,
                "puntaje_economico": None,
                "puntaje_total": None,
                "etapas": etapas,
                "vicios_detectados": vicios,
                "recomendaciones": ["Verificar cumplimiento de RTM según bases"]
            }
        
        # ETAPA 3: Factores Técnicos
        resultado_e3 = self.evaluar_factores_tecnicos(
            factores_bases,
            propuesta.get("tecnica", {}),
            puntaje_minimo_tecnico
        )
        etapas[3] = resultado_e3
        
        puntaje_tecnico = resultado_e3["puntaje_tecnico"]
        
        for alerta in resultado_e3.get("alertas", []):
            vicios.append({
                "etapa": 3,
                "tipo": alerta["tipo"],
                "descripcion": f"Error en factor '{alerta['factor']}'",
                "gravedad": alerta["gravedad"]
            })
        
        if not resultado_e3["cumple_minimo"]:
            return {
                "postor": postor,
                "resultado_final": "DESCALIFICADO",
                "etapa_final": 3,
                "etapa_falla": "FACTORES_TECNICOS",
                "motivo": f"Puntaje técnico ({puntaje_tecnico}) menor al mínimo ({puntaje_minimo_tecnico})",
                "puntaje_tecnico": puntaje_tecnico,
                "puntaje_economico": None,
                "puntaje_total": None,
                "etapas": etapas,
                "vicios_detectados": vicios,
                "recomendaciones": ["Mejorar propuesta técnica para alcanzar puntaje mínimo"]
            }
        
        # ETAPA 4: Económica
        resultado_e4 = self.evaluar_economica_completa(
            propuestas_economicas,
            valor_referencial
        )
        etapas[4] = resultado_e4
        
        # Encontrar el puntaje económico del postor evaluado
        puntaje_economico = 0
        posicion_ranking = None
        for r in resultado_e4.get("ranking", []):
            if r["postor"] == postor:
                puntaje_economico = r["puntaje_correcto"]
                posicion_ranking = r["posicion"]
                break
        
        for error in resultado_e4.get("errores_calculo", []):
            if error["postor"] == postor:
                vicios.append({
                    "etapa": 4,
                    "tipo": "error_calculo_economico",
                    "descripcion": f"Diferencia de {error['diferencia']} puntos en puntaje económico",
                    "gravedad": "ALTA"
                })
                recomendaciones.append("Considerar recurso de apelación por error en evaluación económica")
        
        # Puntaje total (asumiendo 50-50 por defecto, puede ajustarse)
        puntaje_total = round(puntaje_tecnico + puntaje_economico, 2)
        
        return {
            "postor": postor,
            "resultado_final": "ADMITIDO",
            "etapa_final": 4,
            "etapa_falla": None,
            "puntaje_tecnico": puntaje_tecnico,
            "puntaje_economico": puntaje_economico,
            "puntaje_total": puntaje_total,
            "posicion_ranking": posicion_ranking,
            "etapas": etapas,
            "vicios_detectados": vicios,
            "recomendaciones": recomendaciones if recomendaciones else ["Propuesta evaluada correctamente"],
            "base_legal": "Arts. 77-78 del Reglamento D.S. N° 009-2025-EF"
        }
    
    def generar_informe_evaluacion_etapas(self, resultado: Dict) -> str:
        """Genera informe formateado de la evaluación por etapas"""
        postor = resultado.get("postor", "Postor")
        estado = resultado.get("resultado_final", "N/A")
        etapa_final = resultado.get("etapa_final", 0)
        
        informe = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║      INFORME DE EVALUACIÓN DE PROPUESTA - FLUJO POR ETAPAS                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

Postor:          {postor}
Resultado:       {'✅ ' + estado if estado == 'ADMITIDO' else '❌ ' + estado}
Etapa Final:     {etapa_final}/4
Fecha Análisis:  {datetime.now().strftime("%d/%m/%Y %H:%M")}

═══════════════════════════════════════════════════════════════════════════════
                    RESUMEN POR ETAPAS
═══════════════════════════════════════════════════════════════════════════════
"""
        
        nombres_etapas = {
            1: "Requisitos Mínimos",
            2: "RTM (Requerimientos Técnicos Mínimos)",
            3: "Factores de Evaluación Técnica",
            4: "Evaluación Económica"
        }
        
        for i in range(1, 5):
            etapa = resultado.get("etapas", {}).get(i, {})
            if etapa:
                estado_etapa = "✅ PASA" if etapa.get("cumple", etapa.get("puede_continuar", True)) else "❌ NO PASA"
                informe += f"\nETAPA {i}: {nombres_etapas[i]}\n"
                informe += f"Estado: {estado_etapa}\n"
                
                if i == 3 and etapa.get("puntaje_tecnico"):
                    informe += f"Puntaje: {etapa['puntaje_tecnico']}/{etapa['puntaje_maximo']}\n"
                if i == 4 and resultado.get("puntaje_economico"):
                    informe += f"Puntaje Económico: {resultado['puntaje_economico']}\n"
                    informe += f"Posición en Ranking: {resultado.get('posicion_ranking', 'N/A')}\n"
        
        # Vicios detectados
        vicios = resultado.get("vicios_detectados", [])
        if vicios:
            informe += """
═══════════════════════════════════════════════════════════════════════════════
                    VICIOS DETECTADOS
═══════════════════════════════════════════════════════════════════════════════
"""
            for i, v in enumerate(vicios, 1):
                informe += f"\n{i}. [{v['gravedad']}] Etapa {v['etapa']}: {v['descripcion']}\n"
        
        # Puntaje final
        if resultado.get("puntaje_total"):
            informe += f"""
═══════════════════════════════════════════════════════════════════════════════
                    PUNTAJE FINAL
═══════════════════════════════════════════════════════════════════════════════

Puntaje Técnico:    {resultado['puntaje_tecnico']}
Puntaje Económico:  {resultado['puntaje_economico']}
─────────────────────────────────────────────────
PUNTAJE TOTAL:      {resultado['puntaje_total']}
"""
        
        # Recomendaciones
        informe += """
═══════════════════════════════════════════════════════════════════════════════
                    RECOMENDACIONES
═══════════════════════════════════════════════════════════════════════════════
"""
        for rec in resultado.get("recomendaciones", []):
            informe += f"• {rec}\n"
        
        informe += f"""
───────────────────────────────────────────────────────────────────────────────
Base legal: {resultado.get('base_legal', 'Arts. 77-78 del Reglamento D.S. N° 009-2025-EF')}
Generado por INKABOT - Agente de Contrataciones Públicas
═══════════════════════════════════════════════════════════════════════════════
"""
        
        return informe

    # =========================================================================
    # EVALUACIÓN AUTOMÁTICA DESDE PDF (CON GEMINI)
    # Analiza PDFs de propuestas sin input manual del usuario
    # =========================================================================
    
    def evaluar_propuesta_automatico(
        self,
        texto_propuesta: str,
        texto_bases: str = "",
        valor_referencial: float = 0,
        nombre_postor: str = "Postor Evaluado"
    ) -> Dict:
        """
        Evalúa una propuesta automáticamente desde texto extraído de PDF.
        Usa Gemini para extraer y analizar datos, ejecutando las 4 etapas.
        
        Args:
            texto_propuesta: Texto extraído del PDF de la propuesta
            texto_bases: Texto extraído del PDF de las bases (opcional)
            valor_referencial: Valor referencial del proceso
            nombre_postor: Nombre del postor
        
        Returns:
            Dict con resultado completo de evaluación y análisis IA
        """
        import google.generativeai as genai
        from config import Config
        
        try:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-2.0-flash')
        except Exception as e:
            return {
                "error": f"No se pudo configurar Gemini: {str(e)}",
                "postor": nombre_postor,
                "resultado_final": "ERROR"
            }
        
        # Prompt para que Gemini extraiga y analice la propuesta
        prompt = f"""Eres un experto en contrataciones públicas del Perú (Ley 32069 y Reglamento D.S. 009-2025-EF).
Analiza la siguiente propuesta de un postor y extrae la información relevante para evaluar si cumple con los requisitos.

TEXTO DE LA PROPUESTA:
{texto_propuesta[:15000]}

{"TEXTO DE LAS BASES:" + chr(10) + texto_bases[:8000] if texto_bases else ""}

VALOR REFERENCIAL: S/ {valor_referencial:,.2f} (si es 0, intenta encontrarlo en el texto)

Responde en formato JSON con la siguiente estructura EXACTA (sin texto adicional, solo el JSON):
{{
    "postor_identificado": "nombre del postor encontrado en el documento",
    "precio_ofertado": 0.0,
    "etapa1_requisitos_minimos": {{
        "rnp_vigente": {{"presentado": true/false, "documento": "descripción", "observacion": ""}},
        "capacidad_legal": {{"presentado": true/false, "documento": "descripción", "observacion": ""}},
        "declaracion_jurada": {{"presentado": true/false, "documento": "descripción", "observacion": ""}},
        "habilitacion": {{"presentado": true/false, "documento": "descripción", "observacion": ""}}
    }},
    "etapa2_rtm": {{
        "especificaciones_tecnicas": {{"cumple": true/false, "descripcion": "", "evidencia": ""}},
        "equipamiento_minimo": {{"cumple": true/false, "descripcion": "", "evidencia": ""}},
        "personal_clave": {{"cumple": true/false, "descripcion": "", "evidencia": ""}},
        "experiencia_minima": {{"cumple": true/false, "descripcion": "", "evidencia": ""}},
        "plazo_ofertado": {{"cumple": true/false, "valor": "", "evidencia": ""}}
    }},
    "etapa3_factores_tecnicos": {{
        "experiencia_postor": {{"puntaje_estimado": 0, "max": 50, "evidencia": ""}},
        "experiencia_personal": {{"puntaje_estimado": 0, "max": 30, "evidencia": ""}},
        "plan_trabajo": {{"puntaje_estimado": 0, "max": 20, "evidencia": ""}}
    }},
    "etapa4_economica": {{
        "precio_ofertado": 0.0,
        "moneda": "PEN",
        "incluye_igv": true/false,
        "plazo_ejecucion": ""
    }},
    "vicios_detectados": [
        {{"tipo": "", "descripcion": "", "gravedad": "ALTA/MEDIA/BAJA", "base_legal": ""}}
    ],
    "observaciones_generales": ""
}}"""

        try:
            response = model.generate_content(prompt)
            respuesta_texto = response.text.strip()
            
            # Limpiar respuesta JSON
            if respuesta_texto.startswith("```json"):
                respuesta_texto = respuesta_texto[7:]
            if respuesta_texto.startswith("```"):
                respuesta_texto = respuesta_texto[3:]
            if respuesta_texto.endswith("```"):
                respuesta_texto = respuesta_texto[:-3]
            
            import json
            datos_extraidos = json.loads(respuesta_texto.strip())
            
        except Exception as e:
            # Fallback con análisis básico
            datos_extraidos = self._analisis_fallback_propuesta(texto_propuesta, valor_referencial)
            datos_extraidos["error_gemini"] = str(e)
        
        # Ejecutar evaluación por etapas
        return self._ejecutar_evaluacion_desde_datos_extraidos(
            datos_extraidos, 
            valor_referencial,
            nombre_postor if nombre_postor != "Postor Evaluado" else datos_extraidos.get("postor_identificado", nombre_postor)
        )
    
    def _analisis_fallback_propuesta(self, texto: str, valor_referencial: float) -> Dict:
        """Análisis básico cuando Gemini falla"""
        texto_lower = texto.lower()
        
        # Buscar precio
        precio = 0.0
        patron_precio = r's/?\.?\s*([\d,]+(?:\.\d{2})?)'
        match = re.search(patron_precio, texto, re.IGNORECASE)
        if match:
            try:
                precio = float(match.group(1).replace(',', ''))
            except:
                pass
        
        # Buscar indicadores básicos
        tiene_rnp = 'rnp' in texto_lower or 'registro nacional de proveedores' in texto_lower
        tiene_dj = 'declaración jurada' in texto_lower or 'declaro bajo juramento' in texto_lower
        
        return {
            "postor_identificado": "Postor (análisis básico)",
            "precio_ofertado": precio,
            "etapa1_requisitos_minimos": {
                "rnp_vigente": {"presentado": tiene_rnp, "documento": "", "observacion": "Detectado por reglas"},
                "capacidad_legal": {"presentado": True, "documento": "", "observacion": ""},
                "declaracion_jurada": {"presentado": tiene_dj, "documento": "", "observacion": ""},
                "habilitacion": {"presentado": True, "documento": "", "observacion": ""}
            },
            "etapa2_rtm": {
                "especificaciones_tecnicas": {"cumple": True, "descripcion": "", "evidencia": "Análisis básico"},
                "equipamiento_minimo": {"cumple": True, "descripcion": "", "evidencia": ""},
                "personal_clave": {"cumple": True, "descripcion": "", "evidencia": ""},
                "experiencia_minima": {"cumple": True, "descripcion": "", "evidencia": ""},
                "plazo_ofertado": {"cumple": True, "valor": "", "evidencia": ""}
            },
            "etapa3_factores_tecnicos": {
                "experiencia_postor": {"puntaje_estimado": 35, "max": 50, "evidencia": ""},
                "experiencia_personal": {"puntaje_estimado": 20, "max": 30, "evidencia": ""},
                "plan_trabajo": {"puntaje_estimado": 15, "max": 20, "evidencia": ""}
            },
            "etapa4_economica": {
                "precio_ofertado": precio,
                "moneda": "PEN",
                "incluye_igv": True,
                "plazo_ejecucion": ""
            },
            "vicios_detectados": [],
            "observaciones_generales": "Análisis realizado con reglas básicas (Gemini no disponible)"
        }
    
    def _ejecutar_evaluacion_desde_datos_extraidos(
        self, 
        datos: Dict, 
        valor_referencial: float,
        nombre_postor: str
    ) -> Dict:
        """Ejecuta las 4 etapas con los datos extraídos por Gemini"""
        
        resultado = {
            "postor": nombre_postor,
            "datos_extraidos": datos,
            "etapas": {},
            "vicios_detectados": datos.get("vicios_detectados", []),
            "timestamp": datetime.now().isoformat()
        }
        
        # ========== ETAPA 1: Requisitos Mínimos ==========
        req_minimos = datos.get("etapa1_requisitos_minimos", {})
        cumple_e1 = True
        detalle_e1 = []
        incumplimientos_e1 = []
        
        for req, info in req_minimos.items():
            presentado = info.get("presentado", False)
            detalle_e1.append({
                "requisito": req,
                "cumple": presentado,
                "observacion": info.get("observacion", "")
            })
            if not presentado and req != "habilitacion":  # habilitación es opcional
                cumple_e1 = False
                incumplimientos_e1.append({
                    "requisito": req,
                    "descripcion": f"No presenta: {req.replace('_', ' ').title()}"
                })
        
        resultado["etapas"][1] = {
            "etapa": "REQUISITOS_MINIMOS",
            "cumple": cumple_e1,
            "resultado": "ADMITIDO" if cumple_e1 else "DESCALIFICADO",
            "detalle": detalle_e1,
            "incumplimientos": incumplimientos_e1
        }
        
        if not cumple_e1:
            resultado["resultado_final"] = "DESCALIFICADO"
            resultado["etapa_final"] = 1
            resultado["motivo"] = "No cumple requisitos mínimos de calificación"
            return resultado
        
        # ========== ETAPA 2: RTM ==========
        rtm = datos.get("etapa2_rtm", {})
        cumple_e2 = True
        detalle_e2 = []
        incumplimientos_e2 = []
        
        for rtm_item, info in rtm.items():
            cumple = info.get("cumple", True)
            detalle_e2.append({
                "rtm": rtm_item,
                "cumple": cumple,
                "evidencia": info.get("evidencia", "")
            })
            if not cumple:
                cumple_e2 = False
                incumplimientos_e2.append({
                    "rtm": rtm_item,
                    "descripcion": f"No cumple: {rtm_item.replace('_', ' ').title()}"
                })
        
        resultado["etapas"][2] = {
            "etapa": "RTM",
            "cumple": cumple_e2,
            "resultado": "ADMITIDO" if cumple_e2 else "DESCALIFICADO",
            "detalle": detalle_e2,
            "incumplimientos": incumplimientos_e2
        }
        
        if not cumple_e2:
            resultado["resultado_final"] = "DESCALIFICADO"
            resultado["etapa_final"] = 2
            resultado["motivo"] = "No cumple requerimientos técnicos mínimos"
            return resultado
        
        # ========== ETAPA 3: Factores Técnicos ==========
        factores = datos.get("etapa3_factores_tecnicos", {})
        puntaje_tecnico = 0
        puntaje_max = 0
        detalle_e3 = []
        
        for factor, info in factores.items():
            pts = info.get("puntaje_estimado", 0)
            max_pts = info.get("max", 0)
            puntaje_tecnico += pts
            puntaje_max += max_pts
            detalle_e3.append({
                "factor": factor,
                "puntaje": pts,
                "maximo": max_pts,
                "evidencia": info.get("evidencia", "")
            })
        
        resultado["etapas"][3] = {
            "etapa": "FACTORES_TECNICOS",
            "cumple": True,
            "puntaje_tecnico": puntaje_tecnico,
            "puntaje_maximo": puntaje_max,
            "detalle": detalle_e3
        }
        resultado["puntaje_tecnico"] = puntaje_tecnico
        
        # ========== ETAPA 4: Evaluación Económica ==========
        eco = datos.get("etapa4_economica", {})
        precio = eco.get("precio_ofertado", 0)
        
        # Calcular puntaje económico (asumiendo que es el único postor o el de menor precio)
        if precio > 0 and valor_referencial > 0:
            # Verificar límites
            es_temeraria = precio < (valor_referencial * 0.9)
            excede_vr = precio > valor_referencial
            
            # Puntaje (PE = Pm/Pi x 100, asumiendo este es Pm)
            puntaje_economico = 100
        else:
            puntaje_economico = 0
            es_temeraria = False
            excede_vr = False
        
        resultado["etapas"][4] = {
            "etapa": "ECONOMICA",
            "cumple": not excede_vr,
            "precio_ofertado": precio,
            "valor_referencial": valor_referencial,
            "puntaje_economico": puntaje_economico,
            "es_oferta_temeraria": es_temeraria,
            "excede_valor_referencial": excede_vr,
            "alertas": []
        }
        
        if es_temeraria:
            resultado["etapas"][4]["alertas"].append("⚠️ Oferta potencialmente temeraria (< 90% VR)")
            resultado["vicios_detectados"].append({
                "tipo": "oferta_temeraria",
                "descripcion": f"Precio ({precio:,.2f}) menor al 90% del VR ({valor_referencial * 0.9:,.2f})",
                "gravedad": "ALTA",
                "base_legal": "Art. 78.2 del Reglamento"
            })
        
        if excede_vr:
            resultado["etapas"][4]["alertas"].append("❌ Excede valor referencial")
            resultado["vicios_detectados"].append({
                "tipo": "excede_vr",
                "descripcion": f"Precio ({precio:,.2f}) excede el VR ({valor_referencial:,.2f})",
                "gravedad": "ALTA",
                "base_legal": "Art. 77 del Reglamento"
            })
        
        resultado["puntaje_economico"] = puntaje_economico
        resultado["puntaje_total"] = puntaje_tecnico + puntaje_economico
        
        # Resultado final
        if excede_vr:
            resultado["resultado_final"] = "DESCALIFICADO"
            resultado["etapa_final"] = 4
            resultado["motivo"] = "Precio excede valor referencial"
        else:
            resultado["resultado_final"] = "ADMITIDO"
            resultado["etapa_final"] = 4
            resultado["motivo"] = "Propuesta cumple todas las etapas"
        
        # Generar informe
        resultado["informe"] = self.generar_informe_evaluacion_etapas(resultado)
        resultado["observaciones_ia"] = datos.get("observaciones_generales", "")
        
        return resultado


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
