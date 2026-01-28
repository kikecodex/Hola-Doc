"""
Módulo de Scraping SEACE
Búsqueda automatizada de procesos de selección en el Sistema Electrónico
de Contrataciones del Estado (SEACE) - Perú

Filtros configurados:
- Regiones: Ancash, Lima
- Tipos: Obras, Servicios, Consultoría de Obras
"""
import os
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Optional, List
import requests
from dataclasses import dataclass, asdict

# Importar módulo de caché SQLite
try:
    from .seace_db import get_seace_db, SeaceDB
except ImportError:
    from seace_db import get_seace_db, SeaceDB

# ============================================
# CONFIGURACIÓN
# ============================================

SEACE_BASE_URL = "https://prod2.seace.gob.pe"
SEACE_SEARCH_URL = f"{SEACE_BASE_URL}/seacebus-uiwd-pub/buscadorPublico/buscadorPublico.xhtml"

# IDs de departamentos en SEACE
DEPARTAMENTOS = {
    "ANCASH": "02",
    "LIMA": "15"
}

# Tipos de objeto de contratación
TIPOS_OBJETO = {
    "obras": "O",           # Obra
    "servicios": "S",       # Servicio
    "consultoria_obras": "C"  # Consultoría de Obra
}

# Tipos de procedimiento de interés
TIPOS_PROCEDIMIENTO = {
    "LP": "Licitación Pública",
    "CP": "Concurso Público",
    "LA": "Licitación Abreviada",
    "CA": "Concurso Abreviado"
}


@dataclass
class ProcesoSEACE:
    """Representa un proceso de selección en SEACE"""
    nomenclatura: str
    entidad: str
    descripcion: str
    tipo_objeto: str
    tipo_procedimiento: str
    departamento: str
    valor_referencial: float
    moneda: str
    estado: str
    fecha_publicacion: str
    fecha_registro_participantes: Optional[str]
    fecha_consultas: Optional[str]
    fecha_observaciones: Optional[str]
    fecha_integracion_bases: Optional[str]
    fecha_presentacion_propuestas: Optional[str]
    fecha_buena_pro: Optional[str]
    url_ficha: Optional[str]
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    def resumen_fechas(self) -> str:
        """Genera un resumen de las fechas importantes"""
        lineas = [
            f"📋 **{self.nomenclatura}**",
            f"🏛️ {self.entidad}",
            f"📝 {self.descripcion[:100]}..." if len(self.descripcion) > 100 else f"📝 {self.descripcion}",
            f"💰 {self.moneda} {self.valor_referencial:,.2f}",
            f"📍 {self.departamento}",
            "",
            "**📅 CRONOGRAMA:**"
        ]
        
        if self.fecha_consultas:
            lineas.append(f"• Consultas hasta: **{self.fecha_consultas}**")
        if self.fecha_observaciones:
            lineas.append(f"• Observaciones hasta: **{self.fecha_observaciones}**")
        if self.fecha_integracion_bases:
            lineas.append(f"• Integración de Bases: {self.fecha_integracion_bases}")
        if self.fecha_presentacion_propuestas:
            lineas.append(f"• 📬 Presentación de Propuestas: **{self.fecha_presentacion_propuestas}**")
        if self.fecha_buena_pro:
            lineas.append(f"• Buena Pro: {self.fecha_buena_pro}")
            
        return "\n".join(lineas)


class SEACEScraper:
    """
    Scraper para el buscador público de SEACE
    Extrae información de procesos de selección con fechas clave
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/html',
            'Accept-Language': 'es-PE,es;q=0.9'
        })
        self._cache = {}
        self._cache_ttl = 3600  # 1 hora
        self._ultimo_scrape = {}
        
    def buscar_procesos(
        self,
        tipos_objeto: list[str] = None,
        departamentos: list[str] = None,
        estado: str = "convocado",
        dias_atras: int = 30,
        forzar_actualizacion: bool = False
    ) -> list[ProcesoSEACE]:
        """
        Busca procesos en SEACE desde la base de datos local.
        
        ARQUITECTURA SIMPLIFICADA:
        - n8n sincroniza datos OCDS → SQLite cada mañana
        - Esta función solo consulta SQLite (< 100ms)
        - Sin scraping, sin esperas, sin CAPTCHA
        
        Args:
            tipos_objeto: Lista de tipos (obras, servicios, consultoria_obras)
            departamentos: Lista de departamentos (ANCASH, LIMA)
            estado: Estado del proceso (convocado, adjudicado, etc.)
            dias_atras: Buscar procesos publicados en los últimos N días
            forzar_actualizacion: Ignorado (usar endpoint /api/seace/sync-ocds)
            
        Returns:
            Lista de procesos encontrados en SQLite
        """
        if tipos_objeto is None:
            tipos_objeto = ["obras", "servicios", "consultoria_obras"]
        if departamentos is None:
            departamentos = ["ANCASH", "LIMA"]
        
        resultados = []
        
        try:
            db = get_seace_db()
            
            for tipo in tipos_objeto:
                for depto in departamentos:
                    datos = db.buscar(
                        departamento=depto,
                        tipo_objeto=tipo,
                        estado=estado,
                        solo_frescos=False,  # Mostrar todos los datos disponibles
                        horas_frescura=24 * 7  # Última semana
                    )
                    for d in datos:
                        proceso = self._dict_a_proceso(d)
                        if proceso:
                            resultados.append(proceso)
            
            if resultados:
                print(f"⚡ SQLite: {len(resultados)} procesos encontrados")
            else:
                print("📭 Base de datos vacía. Ejecuta sincronización OCDS.")
                    
        except Exception as e:
            print(f"⚠️ Error accediendo SQLite: {e}")
        
        return resultados
    
    def _dict_a_proceso(self, d: dict) -> Optional[ProcesoSEACE]:
        """Convierte un diccionario de SQLite a ProcesoSEACE"""
        try:
            return ProcesoSEACE(
                nomenclatura=d.get('nomenclatura', ''),
                entidad=d.get('entidad', ''),
                descripcion=d.get('descripcion', ''),
                tipo_objeto=d.get('tipo_objeto', ''),
                tipo_procedimiento=d.get('tipo_procedimiento', ''),
                departamento=d.get('departamento', ''),
                valor_referencial=float(d.get('valor_referencial', 0) or 0),
                moneda=d.get('moneda', 'PEN'),
                estado=d.get('estado', ''),
                fecha_publicacion=d.get('fecha_publicacion', ''),
                fecha_registro_participantes=d.get('fecha_registro_participantes'),
                fecha_consultas=d.get('fecha_consultas'),
                fecha_observaciones=d.get('fecha_observaciones'),
                fecha_integracion_bases=d.get('fecha_integracion_bases'),
                fecha_presentacion_propuestas=d.get('fecha_presentacion_propuestas'),
                fecha_buena_pro=d.get('fecha_buena_pro'),
                url_ficha=d.get('url_ficha')
            )
        except Exception as e:
            print(f"Error convirtiendo proceso: {e}")
            return None
    
    def _guardar_en_sqlite(self, procesos: list[ProcesoSEACE]):
        """Guarda procesos en caché SQLite"""
        try:
            db = get_seace_db()
            datos = [p.to_dict() for p in procesos]
            guardados = db.guardar_procesos_batch(datos)
            if guardados > 0:
                print(f"💾 Guardados {guardados} procesos en caché SQLite")
        except Exception as e:
            print(f"⚠️ Error guardando en SQLite: {e}")
    
    def _obtener_datos_demo(
        self, 
        tipos_objeto: list[str], 
        departamentos: list[str]
    ) -> list[ProcesoSEACE]:
        """
        Retorna datos de demostración para desarrollo
        Estos serán reemplazados con datos reales del scraping
        """
        procesos_demo = []
        
        # Datos de ejemplo para Ancash - Obras
        if "ANCASH" in departamentos and "obras" in tipos_objeto:
            procesos_demo.append(ProcesoSEACE(
                nomenclatura="LP-001-2026-GRA/CS",
                entidad="GOBIERNO REGIONAL DE ANCASH",
                descripcion="MEJORAMIENTO DEL SERVICIO DE TRANSITABILIDAD VEHICULAR Y PEATONAL EN LA AV. LUZURIAGA, DISTRITO DE HUARAZ",
                tipo_objeto="Obra",
                tipo_procedimiento="Licitación Pública",
                departamento="ANCASH",
                valor_referencial=4850000.00,
                moneda="PEN",
                estado="Convocado",
                fecha_publicacion="20/01/2026",
                fecha_registro_participantes="21/01/2026 al 05/02/2026",
                fecha_consultas="21/01/2026 al 28/01/2026",
                fecha_observaciones="21/01/2026 al 30/01/2026",
                fecha_integracion_bases="03/02/2026",
                fecha_presentacion_propuestas="10/02/2026 10:00 hrs",
                fecha_buena_pro="12/02/2026",
                url_ficha=f"{SEACE_BASE_URL}/seacebus-uiwd-pub/fichaSeleccion/fichaSeleccion.xhtml?idFicha=example1"
            ))
            
            procesos_demo.append(ProcesoSEACE(
                nomenclatura="LP-002-2026-GRA/CS",
                entidad="GOBIERNO REGIONAL DE ANCASH",
                descripcion="CONSTRUCCIÓN DE PUENTE CARROZABLE SOBRE EL RÍO SANTA, PROVINCIA DE HUAYLAS",
                tipo_objeto="Obra",
                tipo_procedimiento="Licitación Pública",
                departamento="ANCASH",
                valor_referencial=8200000.00,
                moneda="PEN",
                estado="Convocado",
                fecha_publicacion="22/01/2026",
                fecha_registro_participantes="23/01/2026 al 07/02/2026",
                fecha_consultas="23/01/2026 al 29/01/2026",
                fecha_observaciones="23/01/2026 al 31/01/2026",
                fecha_integracion_bases="04/02/2026",
                fecha_presentacion_propuestas="11/02/2026 10:00 hrs",
                fecha_buena_pro="14/02/2026",
                url_ficha=f"{SEACE_BASE_URL}/seacebus-uiwd-pub/fichaSeleccion/fichaSeleccion.xhtml?idFicha=example2"
            ))
        
        # Datos de ejemplo para Lima - Consultoría de Obras
        if "LIMA" in departamentos and "consultoria_obras" in tipos_objeto:
            procesos_demo.append(ProcesoSEACE(
                nomenclatura="CP-003-2026-MML/CS",
                entidad="MUNICIPALIDAD METROPOLITANA DE LIMA",
                descripcion="ELABORACIÓN DEL EXPEDIENTE TÉCNICO PARA LA REHABILITACIÓN DE LA COSTA VERDE - TRAMO MIRAFLORES",
                tipo_objeto="Consultoría de Obra",
                tipo_procedimiento="Concurso Público",
                departamento="LIMA",
                valor_referencial=1250000.00,
                moneda="PEN",
                estado="Convocado",
                fecha_publicacion="19/01/2026",
                fecha_registro_participantes="20/01/2026 al 03/02/2026",
                fecha_consultas="20/01/2026 al 27/01/2026",
                fecha_observaciones="20/01/2026 al 29/01/2026",
                fecha_integracion_bases="01/02/2026",
                fecha_presentacion_propuestas="07/02/2026 09:00 hrs",
                fecha_buena_pro="10/02/2026",
                url_ficha=f"{SEACE_BASE_URL}/seacebus-uiwd-pub/fichaSeleccion/fichaSeleccion.xhtml?idFicha=example3"
            ))
            
        # Datos de ejemplo para Lima - Servicios
        if "LIMA" in departamentos and "servicios" in tipos_objeto:
            procesos_demo.append(ProcesoSEACE(
                nomenclatura="LA-005-2026-MINSA/CS",
                entidad="MINISTERIO DE SALUD",
                descripcion="SERVICIO DE MANTENIMIENTO PREVENTIVO Y CORRECTIVO DE EQUIPOS BIOMÉDICOS HOSPITALARIOS",
                tipo_objeto="Servicio",
                tipo_procedimiento="Licitación Abreviada",
                departamento="LIMA",
                valor_referencial=890000.00,
                moneda="PEN",
                estado="Convocado",
                fecha_publicacion="24/01/2026",
                fecha_registro_participantes="25/01/2026 al 01/02/2026",
                fecha_consultas="25/01/2026 al 28/01/2026",
                fecha_observaciones="25/01/2026 al 29/01/2026",
                fecha_integracion_bases="31/01/2026",
                fecha_presentacion_propuestas="04/02/2026 11:00 hrs",
                fecha_buena_pro="06/02/2026",
                url_ficha=f"{SEACE_BASE_URL}/seacebus-uiwd-pub/fichaSeleccion/fichaSeleccion.xhtml?idFicha=example4"
            ))
            
        return procesos_demo
    
    def generar_resumen_fechas(self, procesos: list[ProcesoSEACE]) -> str:
        """
        Genera un resumen formateado de las fechas clave de los procesos
        
        Args:
            procesos: Lista de procesos a resumir
            
        Returns:
            Texto formateado con el resumen
        """
        if not procesos:
            return "❌ No se encontraron procesos con los criterios especificados."
        
        # Ordenar por fecha de presentación de propuestas
        procesos_ordenados = sorted(
            procesos, 
            key=lambda p: p.fecha_presentacion_propuestas or "99/99/9999"
        )
        
        lineas = [
            "# 📊 RESUMEN DE PROCESOS SEACE",
            f"**Fecha de consulta:** {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            f"**Total de procesos encontrados:** {len(procesos)}",
            "",
            "---",
            ""
        ]
        
        # Agrupar por departamento
        por_departamento = {}
        for p in procesos_ordenados:
            if p.departamento not in por_departamento:
                por_departamento[p.departamento] = []
            por_departamento[p.departamento].append(p)
        
        for depto, procs in por_departamento.items():
            lineas.append(f"## 📍 {depto}")
            lineas.append("")
            
            for p in procs:
                lineas.append(p.resumen_fechas())
                lineas.append("")
                lineas.append("---")
                lineas.append("")
        
        # Resumen de fechas próximas
        hoy = datetime.now()
        proximos_7_dias = []
        
        for p in procesos:
            if p.fecha_presentacion_propuestas:
                try:
                    # Extraer solo la fecha (sin hora)
                    fecha_str = p.fecha_presentacion_propuestas.split()[0]
                    fecha = datetime.strptime(fecha_str, "%d/%m/%Y")
                    dias_restantes = (fecha - hoy).days
                    if 0 <= dias_restantes <= 7:
                        proximos_7_dias.append((p, dias_restantes))
                except:
                    pass
        
        if proximos_7_dias:
            lineas.append("## ⚠️ FECHAS PRÓXIMAS (próximos 7 días)")
            lineas.append("")
            for p, dias in sorted(proximos_7_dias, key=lambda x: x[1]):
                emoji = "🔴" if dias <= 2 else "🟡" if dias <= 5 else "🟢"
                lineas.append(f"{emoji} **{p.nomenclatura}** - Propuestas en **{dias} días** ({p.fecha_presentacion_propuestas})")
            lineas.append("")
        
        return "\n".join(lineas)


class SeleniumSEACEScraper:
    """
    Scraper con Selenium para SEACE
    Usa navegador real para manejar JavaScript y CAPTCHAs
    
    IMPORTANTE: SEACE puede requerir resolver CAPTCHAs manualmente.
    El navegador se abrirá en modo visible para permitir intervención.
    """
    
    def __init__(self, headless: bool = False, timeout: int = 30):
        """
        Args:
            headless: Si True, navegador invisible (no funciona con CAPTCHA)
            timeout: Tiempo máximo de espera en segundos
        """
        self.headless = headless
        self.timeout = timeout
        self.driver = None
        self._selenium_available = self._check_selenium()
        
    def _check_selenium(self) -> bool:
        """Verifica si Selenium está instalado"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            return True
        except ImportError:
            print("⚠️ Selenium no instalado. Ejecuta: pip install selenium webdriver-manager")
            return False
    
    def _init_driver(self):
        """Inicializa el navegador Chrome"""
        if not self._selenium_available:
            raise RuntimeError("Selenium no está disponible")
            
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        
        options = Options()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # User agent realista
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.implicitly_wait(10)
        
        # Evitar detección de bot
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def _close_driver(self):
        """Cierra el navegador"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def buscar_procesos_real(
        self,
        tipos_objeto: list[str] = None,
        departamentos: list[str] = None,
        esperar_captcha: bool = True,
        timeout_captcha: int = 120
    ) -> list[ProcesoSEACE]:
        """
        Busca procesos en SEACE usando Selenium con lógica robusta de AgenteBuoAvanzado.
        
        Args:
            tipos_objeto: Lista de tipos (obras, servicios, consultoria_obras)
            departamentos: Lista de departamentos (ANCASH, LIMA)
            esperar_captcha: Si True, espera a que el usuario resuelva el CAPTCHA
            timeout_captcha: Segundos máximos para esperar CAPTCHA
            
        Returns:
            Lista de procesos encontrados
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException, NoSuchElementException
        
        # Mapeo de tipos a nombres de SEACE
        TIPOS_SEACE = {
            "obras": "Obra",
            "servicios": "Servicio", 
            "consultoria_obras": "Consultoría de Obra"
        }
        
        if tipos_objeto is None:
            tipos_objeto = ["obras", "consultoria_obras"]
        if departamentos is None:
            departamentos = ["ANCASH", "LIMA"]
            
        resultados = []
        
        try:
            self._init_driver()
            print("🌐 Abriendo SEACE...")
            
            # Navegar al buscador
            self.driver.get(SEACE_SEARCH_URL)
            time.sleep(3)
            
            # Verificar si hay CAPTCHA
            if esperar_captcha:
                self._esperar_captcha(timeout_captcha)
            
            # === LÓGICA DE AGENTE BUO AVANZADO ===
            
            # 1. Buscar y hacer clic en la pestaña "Procedimiento de Selección"
            print("📑 Buscando pestaña de Procedimientos...")
            try:
                tab_selectors = [
                    "//a[contains(text(), 'Procedimiento') and contains(text(), 'Selección')]",
                    "//li[@role='tab']//a[contains(text(), 'Procedimiento')]",
                ]
                tab = None
                for xpath in tab_selectors:
                    try:
                        tab = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, xpath))
                        )
                        break
                    except:
                        continue
                        
                if tab:
                    tab.click()
                    time.sleep(2)
                    print("   ✅ Pestaña seleccionada")
            except Exception as e:
                print(f"   ⚠️ No se encontró pestaña específica: {e}")
            
            # 2. Buscar por cada tipo de contratación
            for tipo in tipos_objeto:
                tipo_nombre = TIPOS_SEACE.get(tipo, tipo)
                print(f"\n📦 Buscando tipo: {tipo_nombre}...")
                
                # Seleccionar tipo de contratación usando JavaScript (más confiable)
                script_seleccionar = f"""
                var dropdown = document.querySelector('div[id*="tipoContratacion"]');
                if(dropdown) dropdown.click();
                """
                self.driver.execute_script(script_seleccionar)
                time.sleep(1)
                
                # Buscar en lista desplegada
                script_item = f"""
                var items = document.querySelectorAll('li.ui-selectonemenu-item');
                for(var i=0; i<items.length; i++) {{
                    if(items[i].textContent.trim() === '{tipo_nombre}') {{
                        items[i].click();
                        return true;
                    }}
                }}
                return false;
                """
                resultado = self.driver.execute_script(script_item)
                time.sleep(1)
                
                if not resultado:
                    print(f"   ⚠️ No se pudo seleccionar {tipo_nombre}")
                    continue
                
                # 3. Clic en Buscar
                print("   🔎 Ejecutando búsqueda...")
                try:
                    boton = self.driver.find_element(By.ID, "tbBuscador:idFormBuscarProceso:btnBuscarSel")
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", boton)
                    time.sleep(0.5)
                    boton.click()
                except:
                    # Fallback JS
                    self.driver.execute_script("""
                        var btn = document.querySelector('button[id*="btnBuscar"]');
                        if(btn) btn.click();
                    """)
                
                time.sleep(5)  # SEACE es lento
                
                # 4. Extraer datos con JavaScript (método robusto de Buo)
                print("   📊 Extrayendo datos...")
                script_extraer = """
                var filas = document.querySelectorAll('table tbody tr');
                var datos = [];
                
                for(var i=0; i<filas.length; i++) {
                    var celdas = filas[i].querySelectorAll('td');
                    if(celdas.length < 3) continue;
                    
                    var textos = [];
                    for(var j=0; j<Math.min(celdas.length, 15); j++) {
                        textos.push(celdas[j].textContent.trim());
                    }
                    
                    var todo = textos.join(' ').toLowerCase();
                    // Filtrar basura (headers repetidos, etc)
                    if(todo.length > 50 && !todo.includes('nombre o sigla')) {
                        datos.push(textos);
                    }
                }
                return datos;
                """
                datos = self.driver.execute_script(script_extraer)
                
                # 5. Convertir a ProcesoSEACE
                for fila in datos:
                    if len(fila) >= 6:
                        # Extraer valores (estructura típica de SEACE)
                        try:
                            nomenclatura = fila[1] if len(fila) > 1 else ""
                            entidad = fila[2] if len(fila) > 2 else ""
                            descripcion = fila[3] if len(fila) > 3 else ""
                            
                            # Detectar departamento basado en texto
                            texto_completo = " ".join(fila).upper()
                            depto = "LIMA"  # Default
                            for dep in departamentos:
                                if dep in texto_completo:
                                    depto = dep
                                    break
                            
                            # Solo incluir si coincide con departamentos solicitados
                            if depto not in departamentos:
                                continue
                            
                            # Extraer valor referencial
                            valor_ref = 0.0
                            for col in fila:
                                if "S/" in col or col.replace(",", "").replace(".", "").isdigit():
                                    try:
                                        valor_str = col.replace("S/", "").replace(",", "").strip()
                                        valor_ref = float(valor_str) if valor_str else 0.0
                                        break
                                    except:
                                        pass
                            
                            proceso = ProcesoSEACE(
                                nomenclatura=nomenclatura,
                                entidad=entidad,
                                descripcion=descripcion,
                                tipo_objeto=tipo_nombre,
                                tipo_procedimiento="",
                                departamento=depto,
                                valor_referencial=valor_ref,
                                moneda="PEN",
                                estado="Convocado",
                                fecha_publicacion="",
                                fecha_registro_participantes=None,
                                fecha_consultas=None,
                                fecha_observaciones=None,
                                fecha_integracion_bases=None,
                                fecha_presentacion_propuestas=None,
                                fecha_buena_pro=None,
                                url_ficha=None
                            )
                            resultados.append(proceso)
                            
                        except Exception as e:
                            continue
                
                print(f"   ✅ Encontrados: {len(datos)} registros")
                                
        except Exception as e:
            print(f"❌ Error en scraping: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            self._close_driver()
            
        print(f"\n✅ Total procesos encontrados: {len(resultados)}")
        return resultados
    
    def _esperar_captcha(self, timeout: int = 120):
        """
        Espera a que el usuario resuelva el CAPTCHA si aparece
        
        Args:
            timeout: Segundos máximos de espera
        """
        from selenium.webdriver.common.by import By
        
        print("\n" + "="*60)
        print("🔒 VERIFICACIÓN DE CAPTCHA")
        print("="*60)
        print("Si aparece un CAPTCHA en el navegador, resuélvelo manualmente.")
        print(f"Esperando hasta {timeout} segundos...")
        print("="*60 + "\n")
        
        inicio = time.time()
        captcha_detectado = False
        
        while time.time() - inicio < timeout:
            try:
                # Buscar indicadores de CAPTCHA
                page_source = self.driver.page_source.lower()
                
                if "captcha" in page_source or "recaptcha" in page_source:
                    if not captcha_detectado:
                        print("⚠️ CAPTCHA detectado. Por favor resuélvalo en el navegador...")
                        captcha_detectado = True
                    time.sleep(2)
                else:
                    # Verificar si ya cargó el buscador
                    try:
                        self.driver.find_element(By.ID, "tbBuscador:cbEstado")
                        if captcha_detectado:
                            print("✅ CAPTCHA resuelto correctamente")
                        return
                    except:
                        time.sleep(1)
                        
            except Exception:
                time.sleep(1)
                
        if captcha_detectado:
            print("⏰ Timeout esperando resolución de CAPTCHA")
        
    def _extraer_resultados_tabla(self, departamento: str, tipo: str) -> list[ProcesoSEACE]:
        """
        Extrae los datos de la tabla de resultados
        
        Returns:
            Lista de ProcesoSEACE
        """
        from selenium.webdriver.common.by import By
        from selenium.common.exceptions import NoSuchElementException
        
        procesos = []
        
        try:
            # Buscar la tabla de resultados
            tabla = self.driver.find_element(By.ID, "tbBuscador:dtProcedimientos_data")
            filas = tabla.find_elements(By.TAG_NAME, "tr")
            
            for fila in filas:
                try:
                    celdas = fila.find_elements(By.TAG_NAME, "td")
                    if len(celdas) >= 8:
                        # Extraer datos de cada celda
                        nomenclatura = celdas[1].text.strip()
                        entidad = celdas[2].text.strip()
                        descripcion = celdas[3].text.strip()
                        tipo_proc = celdas[4].text.strip()
                        
                        # Intentar extraer valor referencial
                        try:
                            vr_text = celdas[5].text.strip().replace(",", "").replace("S/", "").strip()
                            valor_ref = float(vr_text) if vr_text else 0.0
                        except:
                            valor_ref = 0.0
                        
                        estado = celdas[6].text.strip()
                        
                        # Obtener fechas desde la ficha del proceso
                        fechas = self._obtener_fechas_proceso(nomenclatura)
                        
                        proceso = ProcesoSEACE(
                            nomenclatura=nomenclatura,
                            entidad=entidad,
                            descripcion=descripcion,
                            tipo_objeto=tipo.replace("_", " ").title(),
                            tipo_procedimiento=tipo_proc,
                            departamento=departamento,
                            valor_referencial=valor_ref,
                            moneda="PEN",
                            estado=estado,
                            fecha_publicacion=fechas.get("publicacion", ""),
                            fecha_registro_participantes=fechas.get("registro", ""),
                            fecha_consultas=fechas.get("consultas", ""),
                            fecha_observaciones=fechas.get("observaciones", ""),
                            fecha_integracion_bases=fechas.get("integracion", ""),
                            fecha_presentacion_propuestas=fechas.get("propuestas", ""),
                            fecha_buena_pro=fechas.get("buena_pro", ""),
                            url_ficha=None
                        )
                        procesos.append(proceso)
                        
                except Exception as e:
                    continue
                    
        except NoSuchElementException:
            print("   ⚠️ No se encontró tabla de resultados")
        except Exception as e:
            print(f"   ❌ Error extrayendo tabla: {e}")
            
        return procesos
    
    def _obtener_fechas_proceso(self, nomenclatura: str) -> dict:
        """
        Por ahora retorna fechas vacías.
        Para obtener fechas reales, se debe acceder a la ficha de cada proceso.
        """
        # TODO: Implementar navegación a ficha individual si se requiere
        return {
            "publicacion": "",
            "registro": "",
            "consultas": "",
            "observaciones": "",
            "integracion": "",
            "propuestas": "",
            "buena_pro": ""
        }


# Variable global para instancia de Selenium scraper
_selenium_scraper: Optional[SeleniumSEACEScraper] = None


def get_selenium_scraper() -> SeleniumSEACEScraper:
    """Obtiene instancia global del scraper Selenium"""
    global _selenium_scraper
    if _selenium_scraper is None:
        _selenium_scraper = SeleniumSEACEScraper(headless=False)
    return _selenium_scraper


def buscar_seace_real(
    tipos: list[str] = None,
    departamentos: list[str] = None
) -> list[ProcesoSEACE]:
    """
    Función de conveniencia para búsqueda real con Selenium
    
    IMPORTANTE: Abrirá un navegador Chrome visible.
    Si hay CAPTCHA, deberás resolverlo manualmente.
    """
    scraper = get_selenium_scraper()
    return scraper.buscar_procesos_real(tipos, departamentos)


class SEACEAutoSearcher:
    """
    Buscador automático de SEACE con sincronización periódica.
    Se ejecuta cada 12 horas y guarda resultados en caché SQLite.
    """
    
    def __init__(self, scraper: SEACEScraper = None):
        self.scraper = scraper or SEACEScraper()
        self._running = False
        self._thread = None
        self._intervalo_horas = 12  # Sincronizar cada 12 horas
        self._ultimo_resultado = []
        self._nuevos_procesos = []
        self._callbacks = []
        self._sincronizando = False
        
    def iniciar(self, intervalo_horas: int = 12):
        """Inicia las búsquedas automáticas"""
        self._intervalo_horas = intervalo_horas
        self._running = True
        self._thread = threading.Thread(target=self._loop_busqueda, daemon=True)
        self._thread.start()
        print(f"🔄 Sincronización SEACE iniciada (cada {intervalo_horas} horas)")
        
    def detener(self):
        """Detiene las búsquedas automáticas"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        print("⏹️ Sincronización SEACE detenida")
        
    def registrar_callback(self, callback):
        """Registra una función a llamar cuando se encuentren nuevos procesos"""
        self._callbacks.append(callback)
    
    def esta_sincronizando(self) -> bool:
        """Indica si hay una sincronización en progreso"""
        return self._sincronizando
        
    def _loop_busqueda(self):
        """Loop principal de búsqueda automática"""
        # Primera búsqueda inmediata
        self._ejecutar_busqueda()
        
        while self._running:
            # Esperar el intervalo
            for _ in range(self._intervalo_horas * 3600):
                if not self._running:
                    break
                time.sleep(1)
            
            if self._running:
                self._ejecutar_busqueda()
    
    def _ejecutar_busqueda(self, usar_selenium: bool = True):
        """
        Ejecuta una búsqueda y guarda en SQLite.
        
        Args:
            usar_selenium: Si True, intenta usar Selenium para datos reales.
                          Si falla, usa datos demo como fallback.
        """
        if self._sincronizando:
            print("⚠️ Ya hay una sincronización en progreso")
            return
            
        self._sincronizando = True
        inicio = time.time()
        resultados = []
        fuente = "demo"
        
        try:
            print(f"🔍 Sincronizando con SEACE... ({datetime.now().strftime('%H:%M')})")
            
            # Actualizar metadatos
            try:
                db = get_seace_db()
                db.actualizar_sync_metadata('sincronizando', 'Búsqueda en progreso...')
            except:
                pass
            
            # ========================================
            # DATOS DESDE SQLite (sincronizado por n8n OCDS)
            # ========================================
            # La sincronización automática con SEACE OCDS se realiza 
            # cada día a las 8:15 AM mediante n8n workflow externo.
            # Este método solo consulta el caché SQLite local.
            print("📋 Obteniendo datos desde caché SQLite...")
            resultados = self.scraper.buscar_procesos(forzar_actualizacion=True)
            fuente = "sqlite_cache"
            
            # ========================================
            # CAPA 2: DATOS DEMO (fallback)
            # ========================================
            if not resultados:
                print("📋 Usando datos de demostración...")
                resultados = self.scraper.buscar_procesos(forzar_actualizacion=True)
                fuente = "demo"
            
            # ========================================
            # GUARDAR EN SQLITE
            # ========================================
            try:
                db = get_seace_db()
                datos = []
                for p in resultados:
                    d = p.to_dict()
                    d['fuente'] = fuente  # Marcar la fuente de los datos
                    datos.append(d)
                
                guardados = db.guardar_procesos_batch(datos)
                
                duracion = time.time() - inicio
                db.actualizar_sync_metadata(
                    'completado',
                    f'Sincronizados {guardados} procesos ({fuente})',
                    duracion
                )
                print(f"💾 Guardados {guardados} procesos en caché SQLite (fuente: {fuente})")
            except Exception as e:
                print(f"⚠️ Error guardando en SQLite: {e}")
            
            # Detectar nuevos procesos
            nomenclaturas_anteriores = {p.nomenclatura for p in self._ultimo_resultado}
            self._nuevos_procesos = [
                p for p in resultados 
                if p.nomenclatura not in nomenclaturas_anteriores
            ]
            
            # Notificar callbacks
            if self._nuevos_procesos:
                print(f"✨ Se encontraron {len(self._nuevos_procesos)} nuevos procesos")
                for callback in self._callbacks:
                    try:
                        callback(self._nuevos_procesos)
                    except Exception as e:
                        print(f"Error en callback: {e}")
            
            self._ultimo_resultado = resultados
            print(f"✅ Sincronización completada: {len(resultados)} procesos activos")
            
        except Exception as e:
            print(f"❌ Error en sincronización automática: {e}")
            try:
                db = get_seace_db()
                db.actualizar_sync_metadata('error', str(e))
            except:
                pass
        finally:
            self._sincronizando = False
    
    def obtener_ultimo_resultado(self) -> list[ProcesoSEACE]:
        """Retorna el último resultado de búsqueda"""
        return self._ultimo_resultado
    
    def obtener_nuevos_procesos(self) -> list[ProcesoSEACE]:
        """Retorna los procesos nuevos desde la última búsqueda"""
        return self._nuevos_procesos
    
    def buscar_ahora(self) -> list[ProcesoSEACE]:
        """Fuerza una sincronización inmediata"""
        self._ejecutar_busqueda()
        return self._ultimo_resultado
    
    def obtener_estadisticas(self) -> dict:
        """Obtiene estadísticas del caché"""
        try:
            db = get_seace_db()
            return db.obtener_estadisticas()
        except:
            return {'error': 'No se pudo acceder a la base de datos'}


# ============================================
# FUNCIONES DE UTILIDAD
# ============================================

# Instancia global del buscador automático
_auto_searcher: Optional[SEACEAutoSearcher] = None


def get_seace_auto_searcher() -> SEACEAutoSearcher:
    """Obtiene la instancia global del buscador automático"""
    global _auto_searcher
    if _auto_searcher is None:
        _auto_searcher = SEACEAutoSearcher()
    return _auto_searcher


def iniciar_busqueda_automatica(intervalo_horas: int = 12):
    """Inicia la sincronización automática con el intervalo especificado (default: 12 horas)"""
    searcher = get_seace_auto_searcher()
    searcher.iniciar(intervalo_horas)


def get_seace_info() -> str:
    """Retorna información sobre la funcionalidad de búsqueda SEACE"""
    return """🔍 **BÚSQUEDA DE PROCESOS SEACE**

**¿Qué es SEACE?**
El Sistema Electrónico de Contrataciones del Estado es la plataforma oficial donde las entidades públicas peruanas publican sus procesos de contratación.

**Tipos de proceso que buscamos:**
• 🏗️ **Obras**: Construcción, rehabilitación, mejoramiento
• 📋 **Servicios**: Mantenimiento, consultoría, asesoría
• 📐 **Consultoría de Obras**: Expedientes técnicos, supervisión

**Regiones configuradas:**
• 📍 ANCASH
• 📍 LIMA

**Búsqueda automática:**
Se ejecuta cada 6 horas y notifica nuevos procesos.

**Comandos disponibles:**
• "Buscar procesos de obras en Ancash"
• "¿Qué licitaciones hay disponibles?"
• "Mostrar resumen de fechas de procesos"
• "Buscar consultorías en Lima"
"""


def buscar_procesos_rapido(
    consulta: str = None,
    tipo: str = None
) -> str:
    """
    Búsqueda rápida de procesos para respuesta del chat
    
    Args:
        consulta: Texto de consulta del usuario
        tipo: Tipo específico (obras, servicios, consultoria_obras)
        
    Returns:
        Resumen formateado de procesos encontrados
    """
    scraper = SEACEScraper()
    
    # Determinar filtros basados en la consulta
    tipos = None
    departamentos = None
    
    if consulta:
        consulta_lower = consulta.lower()
        
        # Detectar tipo
        if "obra" in consulta_lower and "consultor" not in consulta_lower:
            tipos = ["obras"]
        elif "consultor" in consulta_lower:
            tipos = ["consultoria_obras"]
        elif "servicio" in consulta_lower:
            tipos = ["servicios"]
            
        # Detectar departamento
        if "ancash" in consulta_lower:
            departamentos = ["ANCASH"]
        elif "lima" in consulta_lower:
            departamentos = ["LIMA"]
    
    if tipo:
        tipos = [tipo]
    
    # Ejecutar búsqueda
    procesos = scraper.buscar_procesos(
        tipos_objeto=tipos,
        departamentos=departamentos
    )
    
    # Generar resumen
    return scraper.generar_resumen_fechas(procesos)
