"""
Módulo de Datos Abiertos OCDS para SEACE
Obtiene datos oficiales de contrataciones desde la API de OSCE
Sin scraping, sin CAPTCHA, 100% confiable

API: http://contratacionesabiertas.osce.gob.pe
Actualización: Diaria a las 08:15 AM (Lima)
Formato: OCDS (Open Contracting Data Standard)
"""
import os
import gzip
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from io import BytesIO

# Importar dependencias locales
try:
    from .seace_scraper import ProcesoSEACE
    from .seace_db import get_seace_db
except ImportError:
    from seace_scraper import ProcesoSEACE
    from seace_db import get_seace_db


# ============================================
# CONFIGURACIÓN API OCDS
# ============================================

# NOTA: El dominio cambió de osce.gob.pe a oece.gob.pe (nuevo organismo)
OCDS_BASE_URL = "https://contratacionesabiertas.oece.gob.pe"
OCDS_DESCARGAS_URL = f"{OCDS_BASE_URL}/descargas"
OCDS_API_URL = f"{OCDS_BASE_URL}/api"

# Mapeo de tipos OCDS a tipos internos
TIPOS_OCDS_MAP = {
    "goods": "Bien",
    "works": "Obra", 
    "services": "Servicio",
    "consultingServices": "Consultoría de Obra"
}

# Mapeo inverso para filtros
TIPOS_INTERNOS_MAP = {
    "obras": ["works"],
    "servicios": ["services"],
    "consultoria_obras": ["consultingServices"],
    "bienes": ["goods"]
}

# Departamentos para filtrar
DEPARTAMENTOS_PERU = [
    "AMAZONAS", "ANCASH", "APURIMAC", "AREQUIPA", "AYACUCHO",
    "CAJAMARCA", "CALLAO", "CUSCO", "HUANCAVELICA", "HUANUCO",
    "ICA", "JUNIN", "LA LIBERTAD", "LAMBAYEQUE", "LIMA",
    "LORETO", "MADRE DE DIOS", "MOQUEGUA", "PASCO", "PIURA",
    "PUNO", "SAN MARTIN", "TACNA", "TUMBES", "UCAYALI"
]


class OCDSScraper:
    """
    Cliente para la API de Contrataciones Abiertas de OSCE.
    
    Ventajas sobre scraping:
    - Sin CAPTCHA
    - Sin bloqueos de IP
    - Datos oficiales actualizados diariamente
    - Formato estándar internacional (OCDS)
    """
    
    def __init__(self, timeout: int = 60):
        """
        Args:
            timeout: Timeout en segundos para requests HTTP
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'HolaDoc-Bot/1.0 (Consultor Contrataciones Peru)',
            'Accept': 'application/json'
        })
        self._cache_releases = {}
    
    def obtener_archivo_descargas(self, anio: int = None, mes: int = None) -> Optional[str]:
        """
        Obtiene la URL del archivo de descargas masivas más reciente.
        
        Args:
            anio: Año específico (default: actual)
            mes: Mes específico (default: actual)
            
        Returns:
            URL del archivo JSON.gz o None si falla
        """
        if anio is None:
            anio = datetime.now().year
        if mes is None:
            mes = datetime.now().month
            
        # Formato: YYYY-MM (ej: 2026-01)
        fecha_str = f"{anio}-{mes:02d}"
        
        # Intentar obtener archivo del mes actual o anterior
        urls_intentar = [
            f"{OCDS_DESCARGAS_URL}/releases_{fecha_str}.jsonl.gz",
            f"{OCDS_DESCARGAS_URL}/releases_{anio}-{mes-1:02d}.jsonl.gz" if mes > 1 else None,
            f"{OCDS_DESCARGAS_URL}/records_{fecha_str}.jsonl.gz"
        ]
        
        for url in urls_intentar:
            if url:
                try:
                    resp = self.session.head(url, timeout=10)
                    if resp.status_code == 200:
                        return url
                except:
                    continue
        
        return None
    
    def descargar_releases(
        self,
        url: str = None,
        limite: int = 1000,
        departamentos: List[str] = None,
        tipos_objeto: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Descarga y parsea releases OCDS desde la API REST.
        
        Args:
            url: URL del archivo (ignorado, usamos API directa)
            limite: Máximo de registros a procesar
            departamentos: Filtrar por departamentos
            tipos_objeto: Filtrar por tipos (obras, servicios, consultoria_obras)
            
        Returns:
            Lista de releases OCDS como diccionarios
        """
        if departamentos is None:
            departamentos = ["ANCASH", "LIMA"]
        if tipos_objeto is None:
            tipos_objeto = ["obras", "consultoria_obras"]
            
        # Convertir tipos internos a OCDS
        tipos_ocds = []
        for tipo in tipos_objeto:
            tipos_ocds.extend(TIPOS_INTERNOS_MAP.get(tipo.lower(), []))
        
        # Usar directamente la API REST (más confiable que archivos .gz)
        return self._obtener_desde_api(departamentos, tipos_ocds, limite)
    
    def _obtener_desde_api(
        self,
        departamentos: List[str],
        tipos_ocds: List[str],
        limite: int
    ) -> List[Dict[str, Any]]:
        """Fallback: obtener releases desde API REST v1"""
        releases = []
        
        try:
            # Endpoint correcto: /api/v1/releases con paginación
            url = f"{OCDS_BASE_URL}/api/v1/releases"
            page = 1
            page_size = min(limite, 100)
            total_obtenidos = 0
            
            print(f"🔄 Obteniendo datos desde API OCDS: {url}")
            
            while total_obtenidos < limite:
                params = {
                    "page": page,
                    "pageSize": page_size
                }
                
                resp = self.session.get(url, params=params, timeout=self.timeout)
                
                if resp.status_code == 200:
                    data = resp.json()
                    
                    # Extraer releases de la respuesta
                    releases_page = data.get("releases", [])
                    if not releases_page:
                        break
                    
                    # Filtrar por departamento y tipo
                    for release in releases_page:
                        ubicacion = self._extraer_ubicacion(release)
                        tipo = self._extraer_tipo(release)
                        
                        # Aplicar filtros si están definidos
                        # Si departamentos es None, vacío o contiene "TODOS", no filtrar
                        if departamentos and "TODOS" not in [d.upper() for d in departamentos]:
                            if not any(d.upper() in ubicacion.upper() for d in departamentos):
                                continue
                        if tipos_ocds and tipo not in tipos_ocds:
                            continue
                        
                        releases.append(release)
                        total_obtenidos += 1
                        
                        if total_obtenidos >= limite:
                            break
                    
                    # Verificar si hay más páginas
                    links = data.get("links", {})
                    if not links.get("next"):
                        break
                    
                    page += 1
                    
                else:
                    print(f"   ⚠️ API respondió {resp.status_code}")
                    break
            
            print(f"   ✅ {len(releases)} releases desde API")
                
        except Exception as e:
            print(f"   ❌ Error en API: {e}")
        
        return releases
    
    def _extraer_ubicacion(self, release: Dict) -> str:
        """Extrae ubicación/departamento de un release OCDS"""
        try:
            # Buscar en tender.deliveryAddresses
            tender = release.get("tender", {})
            addresses = tender.get("deliveryAddresses", [])
            if addresses:
                return addresses[0].get("region", "")
            
            # Buscar en parties (buyer)
            parties = release.get("parties", [])
            for party in parties:
                if "buyer" in party.get("roles", []):
                    addr = party.get("address", {})
                    return addr.get("region", addr.get("locality", ""))
            
            # Buscar en buyer directamente
            buyer = release.get("buyer", {})
            return buyer.get("address", {}).get("region", "LIMA")
            
        except:
            return "LIMA"
    
    def _extraer_tipo(self, release: Dict) -> str:
        """Extrae tipo de contratación de un release OCDS"""
        try:
            tender = release.get("tender", {})
            
            # mainProcurementCategory es el campo estándar OCDS
            categoria = tender.get("mainProcurementCategory", "")
            if categoria:
                return categoria
            
            # Fallback: procurementMethodDetails
            details = tender.get("procurementMethodDetails", "").lower()
            if "obra" in details:
                return "works"
            elif "consultor" in details:
                return "consultingServices"
            elif "servicio" in details:
                return "services"
            
            return "works"  # Default
            
        except:
            return "works"
    
    def convertir_a_proceso(self, release: Dict) -> Optional[ProcesoSEACE]:
        """
        Convierte un release OCDS a ProcesoSEACE.
        
        Args:
            release: Diccionario con datos OCDS
            
        Returns:
            ProcesoSEACE o None si falla
        """
        try:
            tender = release.get("tender", {})
            buyer = release.get("buyer", {})
            
            # Extraer nomenclatura/ID
            ocid = release.get("ocid", "")
            tender_id = tender.get("id", ocid)
            
            # Extraer valor
            value = tender.get("value", {})
            valor_ref = float(value.get("amount", 0) or 0)
            moneda = value.get("currency", "PEN")
            
            # Extraer fechas
            periodo = tender.get("tenderPeriod", {})
            fecha_pub = periodo.get("startDate", "")
            if fecha_pub:
                # Convertir ISO a formato DD/MM/YYYY
                try:
                    dt = datetime.fromisoformat(fecha_pub.replace("Z", "+00:00"))
                    fecha_pub = dt.strftime("%d/%m/%Y")
                except:
                    pass
            
            # Extraer fechas adicionales del cronograma
            milestones = tender.get("milestones", [])
            fechas = {}
            for m in milestones:
                code = m.get("code", "").lower()
                due = m.get("dueDate", "")
                if "consulta" in code:
                    fechas["consultas"] = due
                elif "observacion" in code:
                    fechas["observaciones"] = due
                elif "propuesta" in code or "oferta" in code:
                    fechas["propuestas"] = due
            
            # Tipo de objeto
            tipo_ocds = self._extraer_tipo(release)
            tipo_interno = TIPOS_OCDS_MAP.get(tipo_ocds, "Obra")
            
            # Estado
            status_map = {
                "active": "Convocado",
                "complete": "Adjudicado",
                "cancelled": "Cancelado",
                "unsuccessful": "Desierto"
            }
            estado = status_map.get(tender.get("status", "active"), "Convocado")
            
            return ProcesoSEACE(
                nomenclatura=tender_id,
                entidad=buyer.get("name", "Sin entidad"),
                descripcion=tender.get("title", tender.get("description", "")),
                tipo_objeto=tipo_interno,
                tipo_procedimiento=tender.get("procurementMethod", ""),
                departamento=self._extraer_ubicacion(release),
                valor_referencial=valor_ref,
                moneda=moneda,
                estado=estado,
                fecha_publicacion=fecha_pub,
                fecha_registro_participantes=None,
                fecha_consultas=fechas.get("consultas"),
                fecha_observaciones=fechas.get("observaciones"),
                fecha_integracion_bases=None,
                fecha_presentacion_propuestas=fechas.get("propuestas"),
                fecha_buena_pro=None,
                url_ficha=f"{OCDS_BASE_URL}/process/{ocid}"
            )
            
        except Exception as e:
            print(f"⚠️ Error convirtiendo release: {e}")
            return None
    
    def buscar_procesos(
        self,
        departamentos: List[str] = None,
        tipos_objeto: List[str] = None,
        limite: int = 100
    ) -> List[ProcesoSEACE]:
        """
        Busca procesos de contratación usando datos OCDS.
        
        Args:
            departamentos: Lista de departamentos (ANCASH, LIMA, etc.)
            tipos_objeto: Lista de tipos (obras, servicios, consultoria_obras)
            limite: Máximo de resultados
            
        Returns:
            Lista de ProcesoSEACE
        """
        if departamentos is None:
            departamentos = ["ANCASH", "LIMA"]
        if tipos_objeto is None:
            tipos_objeto = ["obras", "consultoria_obras"]
        
        print(f"\n🔍 Buscando procesos OCDS...")
        print(f"   📍 Departamentos: {', '.join(departamentos)}")
        print(f"   📦 Tipos: {', '.join(tipos_objeto)}")
        
        # Descargar releases
        releases = self.descargar_releases(
            departamentos=departamentos,
            tipos_objeto=tipos_objeto,
            limite=limite * 2  # Descargar más para compensar filtros
        )
        
        # Convertir a ProcesoSEACE
        procesos = []
        for release in releases:
            proceso = self.convertir_a_proceso(release)
            if proceso:
                procesos.append(proceso)
                if len(procesos) >= limite:
                    break
        
        print(f"   ✅ {len(procesos)} procesos encontrados\n")
        return procesos
    
    def sincronizar_sqlite(
        self,
        departamentos: List[str] = None,
        tipos_objeto: List[str] = None,
        limite: int = 500
    ) -> Dict[str, Any]:
        """
        Sincroniza datos OCDS con la base de datos SQLite local.
        
        Args:
            departamentos: Departamentos a sincronizar
            tipos_objeto: Tipos de contratación
            limite: Máximo de registros
            
        Returns:
            Diccionario con estadísticas de sincronización
        """
        inicio = datetime.now()
        resultado = {
            "exito": False,
            "procesados": 0,
            "guardados": 0,
            "errores": 0,
            "duracion_segundos": 0,
            "mensaje": ""
        }
        
        try:
            print("\n" + "="*50)
            print("🔄 SINCRONIZACIÓN OCDS → SQLite")
            print("="*50)
            
            # Obtener procesos de OCDS
            procesos = self.buscar_procesos(
                departamentos=departamentos,
                tipos_objeto=tipos_objeto,
                limite=limite
            )
            
            resultado["procesados"] = len(procesos)
            
            if not procesos:
                resultado["mensaje"] = "No se encontraron procesos en OCDS"
                return resultado
            
            # Guardar en SQLite
            db = get_seace_db()
            
            datos_guardar = []
            for p in procesos:
                d = p.to_dict()
                d["fuente"] = "ocds"  # Marcar origen
                datos_guardar.append(d)
            
            guardados = db.guardar_procesos_batch(datos_guardar)
            resultado["guardados"] = guardados
            
            # Actualizar metadatos
            db.actualizar_sync_metadata(
                estado="completado",
                mensaje=f"Sincronizados {guardados} procesos desde OCDS",
                duracion=(datetime.now() - inicio).total_seconds()
            )
            
            resultado["exito"] = True
            resultado["mensaje"] = f"Sincronizados {guardados} procesos exitosamente"
            
        except Exception as e:
            resultado["errores"] = 1
            resultado["mensaje"] = f"Error: {str(e)}"
            print(f"❌ Error en sincronización: {e}")
            
        finally:
            resultado["duracion_segundos"] = (datetime.now() - inicio).total_seconds()
            
        print(f"\n📊 Resultado: {resultado}")
        return resultado


# Función de conveniencia
def buscar_con_ocds(
    departamentos: List[str] = None,
    tipos_objeto: List[str] = None,
    limite: int = 50
) -> List[ProcesoSEACE]:
    """
    Función de conveniencia para buscar procesos con OCDS.
    
    Args:
        departamentos: Lista de departamentos
        tipos_objeto: Lista de tipos
        limite: Máximo de resultados
        
    Returns:
        Lista de ProcesoSEACE
    """
    scraper = OCDSScraper()
    return scraper.buscar_procesos(departamentos, tipos_objeto, limite)


# Test rápido
if __name__ == "__main__":
    print("🧪 Probando OCDSScraper...")
    
    scraper = OCDSScraper()
    
    # Probar búsqueda
    procesos = scraper.buscar_procesos(
        departamentos=["ANCASH", "LIMA"],
        tipos_objeto=["obras", "consultoria_obras"],
        limite=10
    )
    
    print(f"\n📋 Resultados: {len(procesos)} procesos")
    for p in procesos[:3]:
        print(f"   • {p.nomenclatura}: {p.entidad[:50]}...")
    
    # Probar sincronización
    print("\n🔄 Probando sincronización...")
    resultado = scraper.sincronizar_sqlite(limite=20)
    print(f"   Resultado: {resultado}")
