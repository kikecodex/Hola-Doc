"""
Módulo de exportación SEACE
Funciones para exportar procesos a CSV, Excel y generar alertas
"""
import csv
import io
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# UIT 2026 = S/ 5,350
UIT_2026 = 5350
MONTO_MINIMO_8_UIT = 8 * UIT_2026  # S/ 42,800


def calcular_dias_restantes(fecha_str: str) -> Optional[int]:
    """Calcula días restantes hasta una fecha DD/MM/YYYY"""
    if not fecha_str:
        return None
    try:
        # Formato: DD/MM/YYYY HH:MM o DD/MM/YYYY
        fecha_parte = fecha_str.split(' ')[0]
        dia, mes, anio = fecha_parte.split('/')
        fecha = datetime(int(anio), int(mes), int(dia))
        hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return (fecha - hoy).days
    except:
        return None


def filtrar_por_monto(procesos: List[Dict], monto_minimo: float = MONTO_MINIMO_8_UIT) -> List[Dict]:
    """
    Filtra procesos por monto mínimo.
    Por defecto: > 8 UIT (S/ 42,800)
    """
    return [
        p for p in procesos 
        if float(p.get('valor_referencial', 0) or 0) >= monto_minimo
    ]


def filtrar_urgentes(procesos: List[Dict], dias_limite: int = 3) -> List[Dict]:
    """
    Filtra procesos urgentes (próximos a vencer).
    Por defecto: <= 3 días para presentar propuestas
    """
    urgentes = []
    for p in procesos:
        dias = calcular_dias_restantes(p.get('fecha_presentacion_propuestas'))
        if dias is not None and 0 <= dias <= dias_limite:
            p['dias_restantes'] = dias
            urgentes.append(p)
    return urgentes


def deduplicar_procesos(procesos: List[Dict]) -> List[Dict]:
    """Elimina procesos duplicados por nomenclatura"""
    vistos = set()
    unicos = []
    for p in procesos:
        nom = p.get('nomenclatura', '')
        if nom and nom not in vistos:
            vistos.add(nom)
            unicos.append(p)
    return unicos


def exportar_csv(procesos: List[Dict]) -> str:
    """
    Genera contenido CSV desde lista de procesos.
    Retorna string con contenido CSV.
    """
    if not procesos:
        return ""
    
    output = io.StringIO()
    
    # Definir columnas
    columnas = [
        'nomenclatura', 'entidad', 'tipo_objeto', 'departamento',
        'valor_referencial', 'estado', 'fecha_publicacion',
        'fecha_observaciones', 'fecha_presentacion_propuestas',
        'descripcion'
    ]
    
    writer = csv.DictWriter(output, fieldnames=columnas, extrasaction='ignore')
    writer.writeheader()
    
    for proceso in procesos:
        # Limpiar datos
        row = {col: proceso.get(col, '') for col in columnas}
        writer.writerow(row)
    
    return output.getvalue()


def generar_mensaje_whatsapp(procesos_urgentes: List[Dict]) -> str:
    """
    Genera mensaje para WhatsApp con procesos urgentes.
    Formato optimizado para lectura en móvil.
    """
    if not procesos_urgentes:
        return ""
    
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    
    mensaje = f"🚨 *ALERTA SEACE - {fecha_hoy}*\n\n"
    mensaje += f"⚠️ *{len(procesos_urgentes)} proceso(s) urgente(s)*\n"
    mensaje += "─" * 20 + "\n\n"
    
    for i, p in enumerate(procesos_urgentes[:5], 1):  # Máximo 5 para no saturar
        dias = p.get('dias_restantes', '?')
        emoji_dias = "🔴" if dias <= 1 else "🟡"
        
        mensaje += f"{emoji_dias} *{i}. {p.get('tipo_objeto', 'N/D')}*\n"
        mensaje += f"📋 {p.get('nomenclatura', 'N/D')}\n"
        mensaje += f"🏛️ {p.get('entidad', 'N/D')[:50]}...\n"
        mensaje += f"📍 {p.get('departamento', 'N/D')}\n"
        mensaje += f"💰 S/ {float(p.get('valor_referencial', 0)):,.0f}\n"
        mensaje += f"⏰ *{dias} día(s) restante(s)*\n"
        mensaje += f"📬 Propuestas: {p.get('fecha_presentacion_propuestas', 'N/D')}\n\n"
    
    if len(procesos_urgentes) > 5:
        mensaje += f"_...y {len(procesos_urgentes) - 5} más_\n\n"
    
    mensaje += "🔗 Ver más en: holadoc.com/seace"
    
    return mensaje


def generar_resumen_diario(procesos: List[Dict]) -> Dict[str, Any]:
    """
    Genera resumen estadístico diario de procesos.
    """
    total = len(procesos)
    
    # Contar por tipo
    tipos = {}
    for p in procesos:
        tipo = p.get('tipo_objeto', 'Otro')
        tipos[tipo] = tipos.get(tipo, 0) + 1
    
    # Contar por departamento
    departamentos = {}
    for p in procesos:
        dep = p.get('departamento', 'Otro')
        departamentos[dep] = departamentos.get(dep, 0) + 1
    
    # Sumar monto total
    monto_total = sum(float(p.get('valor_referencial', 0) or 0) for p in procesos)
    
    # Contar urgentes
    urgentes = len(filtrar_urgentes(procesos, dias_limite=3))
    proximos = len(filtrar_urgentes(procesos, dias_limite=7)) - urgentes
    
    return {
        'fecha': datetime.now().isoformat(),
        'total_procesos': total,
        'monto_total': monto_total,
        'monto_total_formatted': f"S/ {monto_total:,.0f}",
        'urgentes': urgentes,
        'proximos_7_dias': proximos,
        'por_tipo': tipos,
        'por_departamento': departamentos
    }


# Información del módulo
def get_exports_info() -> Dict[str, Any]:
    return {
        'modulo': 'SEACE Exports',
        'version': '1.0.0',
        'funciones': [
            'exportar_csv - Genera archivo CSV',
            'filtrar_por_monto - Filtra por monto mínimo (8 UIT)',
            'filtrar_urgentes - Filtra por días restantes',
            'generar_mensaje_whatsapp - Mensaje para alertas',
            'deduplicar_procesos - Elimina duplicados'
        ],
        'uit_2026': UIT_2026,
        'monto_minimo_default': MONTO_MINIMO_8_UIT
    }
