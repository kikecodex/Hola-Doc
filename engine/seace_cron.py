"""
SEACE Cron Job - Sincronización Diaria Automatizada
Reemplaza el workflow de n8n con ejecución nativa en Render.

Ejecuta a las 8:15 AM (Lima) vía Render Cron Jobs.
"""
import os
import sys
import requests
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.seace_ocds import OCDSScraper
from engine.seace_db import SeaceDB
from engine.seace_exports import (
    filtrar_por_monto, filtrar_urgentes, deduplicar_procesos,
    generar_mensaje_whatsapp, generar_resumen_diario,
    MONTO_MINIMO_8_UIT
)


def enviar_whatsapp_evolution(mensaje: str) -> dict:
    """
    Envía mensaje via Evolution API.
    Configura las variables de entorno en Render:
    - EVOLUTION_API_URL
    - EVOLUTION_INSTANCE
    - EVOLUTION_API_KEY
    - EVOLUTION_DESTINO
    """
    api_url = os.getenv('EVOLUTION_API_URL', 'http://localhost:8080')
    instance = os.getenv('EVOLUTION_INSTANCE', 'holadoc')
    api_key = os.getenv('EVOLUTION_API_KEY', '')
    destino = os.getenv('EVOLUTION_DESTINO', '')
    
    if not api_key or not destino:
        print("[WARN] Evolution API no configurada. Mensaje no enviado.")
        return {'enviado': False, 'razon': 'Credenciales no configuradas'}
    
    try:
        url = f"{api_url}/message/sendText/{instance}"
        headers = {
            'apikey': api_key,
            'Content-Type': 'application/json'
        }
        payload = {
            'number': destino,
            'text': mensaje
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"[OK] WhatsApp enviado a {destino}")
        return {'enviado': True, 'destino': destino}
        
    except Exception as e:
        print(f"[ERROR] WhatsApp: {e}")
        return {'enviado': False, 'error': str(e)}


def ejecutar_sincronizacion_diaria() -> dict:
    """
    Pipeline completo de sincronización SEACE:
    1. Sincroniza OCDS (Ancash, Lima)
    2. Filtra > 8 UIT (S/ 42,800)
    3. Detecta urgentes (≤3 días)
    4. Envía WhatsApp si hay urgentes
    5. Retorna resumen
    """
    resultado = {
        'fecha': datetime.now().isoformat(),
        'etapas': [],
        'exito': True
    }
    
    try:
        # === ETAPA 1: Sincronizar OCDS ===
        print("[1/4] Sincronizando OCDS...")
        scraper = OCDSScraper()
        sync_result = scraper.sincronizar_sqlite(
            departamentos=['ANCASH', 'LIMA'],
            tipos_objeto=['obras', 'consultoria_obras', 'servicios'],
            limite=500
        )
        resultado['etapas'].append({
            'etapa': 'sync_ocds',
            'resultado': sync_result
        })
        print(f"      -> {sync_result.get('nuevos', 0)} nuevos procesos")
        
        # === ETAPA 2: Filtrar procesos ===
        print("[2/4] Filtrando procesos...")
        db = SeaceDB()
        procesos = db.buscar(limite=500, solo_frescos=False)
        
        procesos = deduplicar_procesos(procesos)
        procesos_filtrados = filtrar_por_monto(procesos, MONTO_MINIMO_8_UIT)
        urgentes = filtrar_urgentes(procesos_filtrados, dias_limite=3)
        
        resultado['total_original'] = len(procesos)
        resultado['total_filtrado'] = len(procesos_filtrados)
        resultado['urgentes_count'] = len(urgentes)
        
        print(f"      -> {len(procesos_filtrados)} procesos > 8 UIT")
        print(f"      -> {len(urgentes)} urgentes (≤3 días)")
        
        # === ETAPA 3: Generar resumen ===
        print("[3/4] Generando resumen...")
        resumen = generar_resumen_diario(procesos_filtrados)
        resultado['resumen'] = resumen
        
        # === ETAPA 4: Enviar WhatsApp si hay urgentes ===
        if urgentes:
            print("[4/4] Enviando WhatsApp...")
            mensaje = generar_mensaje_whatsapp(urgentes)
            whatsapp_result = enviar_whatsapp_evolution(mensaje)
            resultado['whatsapp'] = whatsapp_result
            resultado['mensaje_whatsapp'] = mensaje
        else:
            print("[4/4] Sin urgentes, no se envía WhatsApp")
            resultado['whatsapp'] = {'enviado': False, 'razon': 'Sin procesos urgentes'}
        
        print("\n✅ Sincronización completada exitosamente")
        
    except Exception as e:
        import traceback
        resultado['exito'] = False
        resultado['error'] = str(e)
        resultado['traceback'] = traceback.format_exc()
        print(f"\n❌ Error: {e}")
    
    return resultado


if __name__ == '__main__':
    """
    Ejecutar directamente para pruebas:
    python engine/seace_cron.py
    """
    print("=" * 60)
    print("🔄 SEACE CRON JOB - Sincronización Diaria")
    print("=" * 60)
    print(f"Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    resultado = ejecutar_sincronizacion_diaria()
    
    print()
    print("=" * 60)
    print("📊 RESUMEN:")
    print(f"   Procesos totales: {resultado.get('total_original', 0)}")
    print(f"   Filtrados (>8 UIT): {resultado.get('total_filtrado', 0)}")
    print(f"   Urgentes (≤3 días): {resultado.get('urgentes_count', 0)}")
    print(f"   WhatsApp: {'Enviado ✓' if resultado.get('whatsapp', {}).get('enviado') else 'No enviado'}")
    print("=" * 60)
