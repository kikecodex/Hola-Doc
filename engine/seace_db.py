"""
Módulo de Base de Datos SQLite para Procesos SEACE
Implementa caché persistente para búsquedas rápidas (< 100ms)
"""
import sqlite3
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from contextlib import contextmanager
import threading

# Ruta de la base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'seace_cache.db')

# Lock para thread-safety
_db_lock = threading.Lock()


class SeaceDB:
    """
    Base de datos SQLite para caché de procesos SEACE
    Proporciona búsquedas rápidas y persistencia entre reinicios
    """
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
        self._init_db()
    
    @contextmanager
    def _get_connection(self):
        """Context manager para conexiones thread-safe"""
        with _db_lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
    
    def _init_db(self):
        """Inicializa la base de datos con el esquema requerido"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabla principal de procesos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS procesos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nomenclatura TEXT UNIQUE NOT NULL,
                    entidad TEXT,
                    descripcion TEXT,
                    tipo_objeto TEXT,
                    tipo_procedimiento TEXT,
                    departamento TEXT,
                    valor_referencial REAL DEFAULT 0,
                    moneda TEXT DEFAULT 'PEN',
                    estado TEXT,
                    fecha_publicacion TEXT,
                    fecha_registro_participantes TEXT,
                    fecha_consultas TEXT,
                    fecha_observaciones TEXT,
                    fecha_integracion_bases TEXT,
                    fecha_presentacion_propuestas TEXT,
                    fecha_buena_pro TEXT,
                    url_ficha TEXT,
                    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fuente TEXT DEFAULT 'selenium'
                )
            ''')
            
            # Índices para búsquedas rápidas
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_departamento ON procesos(departamento)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tipo_objeto ON procesos(tipo_objeto)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_estado ON procesos(estado)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_fecha_pub ON procesos(fecha_publicacion)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_actualizado ON procesos(actualizado_en)')
            
            # Tabla de metadatos de sincronización
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sync_metadata (
                    id INTEGER PRIMARY KEY,
                    ultima_sincronizacion TIMESTAMP,
                    total_procesos INTEGER DEFAULT 0,
                    duracion_segundos REAL DEFAULT 0,
                    estado TEXT DEFAULT 'idle',
                    mensaje TEXT
                )
            ''')
            
            # Insertar registro inicial de metadatos si no existe
            cursor.execute('SELECT COUNT(*) FROM sync_metadata')
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO sync_metadata (id, estado, mensaje)
                    VALUES (1, 'pendiente', 'Nunca sincronizado')
                ''')
    
    def guardar_proceso(self, proceso: Dict[str, Any]) -> bool:
        """
        Guarda o actualiza un proceso en la base de datos
        
        Args:
            proceso: Diccionario con datos del proceso
            
        Returns:
            True si se guardó correctamente
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO procesos (
                        nomenclatura, entidad, descripcion, tipo_objeto,
                        tipo_procedimiento, departamento, valor_referencial,
                        moneda, estado, fecha_publicacion, fecha_registro_participantes,
                        fecha_consultas, fecha_observaciones, fecha_integracion_bases,
                        fecha_presentacion_propuestas, fecha_buena_pro, url_ficha,
                        actualizado_en, fuente
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    proceso.get('nomenclatura'),
                    proceso.get('entidad'),
                    proceso.get('descripcion'),
                    proceso.get('tipo_objeto'),
                    proceso.get('tipo_procedimiento'),
                    proceso.get('departamento'),
                    proceso.get('valor_referencial', 0),
                    proceso.get('moneda', 'PEN'),
                    proceso.get('estado'),
                    proceso.get('fecha_publicacion'),
                    proceso.get('fecha_registro_participantes'),
                    proceso.get('fecha_consultas'),
                    proceso.get('fecha_observaciones'),
                    proceso.get('fecha_integracion_bases'),
                    proceso.get('fecha_presentacion_propuestas'),
                    proceso.get('fecha_buena_pro'),
                    proceso.get('url_ficha'),
                    datetime.now().isoformat(),
                    proceso.get('fuente', 'selenium')
                ))
                return True
            except Exception as e:
                print(f"Error guardando proceso: {e}")
                return False
    
    def guardar_procesos_batch(self, procesos: List[Dict[str, Any]]) -> int:
        """
        Guarda múltiples procesos en una sola transacción
        
        Args:
            procesos: Lista de diccionarios de procesos
            
        Returns:
            Número de procesos guardados
        """
        guardados = 0
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            for proceso in procesos:
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO procesos (
                            nomenclatura, entidad, descripcion, tipo_objeto,
                            tipo_procedimiento, departamento, valor_referencial,
                            moneda, estado, fecha_publicacion, fecha_registro_participantes,
                            fecha_consultas, fecha_observaciones, fecha_integracion_bases,
                            fecha_presentacion_propuestas, fecha_buena_pro, url_ficha,
                            actualizado_en, fuente
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        proceso.get('nomenclatura'),
                        proceso.get('entidad'),
                        proceso.get('descripcion'),
                        proceso.get('tipo_objeto'),
                        proceso.get('tipo_procedimiento'),
                        proceso.get('departamento'),
                        proceso.get('valor_referencial', 0),
                        proceso.get('moneda', 'PEN'),
                        proceso.get('estado'),
                        proceso.get('fecha_publicacion'),
                        proceso.get('fecha_registro_participantes'),
                        proceso.get('fecha_consultas'),
                        proceso.get('fecha_observaciones'),
                        proceso.get('fecha_integracion_bases'),
                        proceso.get('fecha_presentacion_propuestas'),
                        proceso.get('fecha_buena_pro'),
                        proceso.get('url_ficha'),
                        datetime.now().isoformat(),
                        proceso.get('fuente', 'selenium')
                    ))
                    guardados += 1
                except Exception as e:
                    print(f"Error guardando proceso {proceso.get('nomenclatura')}: {e}")
                    
        return guardados
    
    def buscar(
        self,
        departamento: str = None,
        tipo_objeto: str = None,
        estado: str = None,
        texto: str = None,
        limite: int = 50,
        solo_frescos: bool = True,
        horas_frescura: int = 12
    ) -> List[Dict[str, Any]]:
        """
        Busca procesos en la base de datos local
        
        Args:
            departamento: Filtrar por departamento (ANCASH, LIMA, etc.)
            tipo_objeto: Filtrar por tipo (obras, servicios, consultoria_obras)
            estado: Filtrar por estado (Convocado, Adjudicado, etc.)
            texto: Búsqueda de texto libre en nomenclatura, entidad o descripción
            limite: Máximo de resultados a retornar
            solo_frescos: Si True, solo retorna datos actualizados recientemente
            horas_frescura: Horas de antigüedad máxima para datos frescos
            
        Returns:
            Lista de procesos como diccionarios
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM procesos WHERE 1=1"
            params = []
            
            if departamento:
                query += " AND UPPER(departamento) = UPPER(?)"
                params.append(departamento)
            
            if tipo_objeto:
                # Mapear tipos cortos a nombres completos
                tipo_map = {
                    'obras': 'Obra',
                    'servicios': 'Servicio',
                    'consultoria_obras': 'Consultoría de Obra'
                }
                tipo_nombre = tipo_map.get(tipo_objeto.lower(), tipo_objeto)
                query += " AND (tipo_objeto LIKE ? OR tipo_objeto LIKE ?)"
                params.extend([f"%{tipo_objeto}%", f"%{tipo_nombre}%"])
            
            if estado:
                query += " AND UPPER(estado) LIKE UPPER(?)"
                params.append(f"%{estado}%")
            
            if texto:
                query += """ AND (
                    nomenclatura LIKE ? OR
                    entidad LIKE ? OR
                    descripcion LIKE ?
                )"""
                texto_like = f"%{texto}%"
                params.extend([texto_like, texto_like, texto_like])
            
            if solo_frescos:
                fecha_limite = (datetime.now() - timedelta(hours=horas_frescura)).isoformat()
                query += " AND actualizado_en >= ?"
                params.append(fecha_limite)
            
            query += " ORDER BY fecha_publicacion DESC, actualizado_en DESC LIMIT ?"
            params.append(limite)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def contar_procesos(self, departamento: str = None, tipo_objeto: str = None) -> int:
        """Cuenta procesos en la base de datos"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT COUNT(*) FROM procesos WHERE 1=1"
            params = []
            
            if departamento:
                query += " AND UPPER(departamento) = UPPER(?)"
                params.append(departamento)
            
            if tipo_objeto:
                query += " AND tipo_objeto LIKE ?"
                params.append(f"%{tipo_objeto}%")
            
            cursor.execute(query, params)
            return cursor.fetchone()[0]
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales de la base de datos"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Total de procesos
            cursor.execute("SELECT COUNT(*) FROM procesos")
            total = cursor.fetchone()[0]
            
            # Por departamento
            cursor.execute("""
                SELECT departamento, COUNT(*) as cantidad 
                FROM procesos 
                GROUP BY departamento
            """)
            por_departamento = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Por tipo
            cursor.execute("""
                SELECT tipo_objeto, COUNT(*) as cantidad 
                FROM procesos 
                GROUP BY tipo_objeto
            """)
            por_tipo = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Última sincronización
            cursor.execute("SELECT * FROM sync_metadata WHERE id = 1")
            sync_row = cursor.fetchone()
            
            return {
                'total_procesos': total,
                'por_departamento': por_departamento,
                'por_tipo': por_tipo,
                'ultima_sincronizacion': sync_row['ultima_sincronizacion'] if sync_row else None,
                'estado_sync': sync_row['estado'] if sync_row else 'desconocido'
            }
    
    def actualizar_sync_metadata(
        self,
        estado: str,
        mensaje: str = None,
        duracion: float = None
    ):
        """Actualiza los metadatos de sincronización"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            updates = ["estado = ?", "ultima_sincronizacion = ?"]
            params = [estado, datetime.now().isoformat()]
            
            if mensaje:
                updates.append("mensaje = ?")
                params.append(mensaje)
            
            if duracion is not None:
                updates.append("duracion_segundos = ?")
                params.append(duracion)
            
            # Contar total actual
            cursor.execute("SELECT COUNT(*) FROM procesos")
            total = cursor.fetchone()[0]
            updates.append("total_procesos = ?")
            params.append(total)
            
            query = f"UPDATE sync_metadata SET {', '.join(updates)} WHERE id = 1"
            cursor.execute(query, params)
    
    def datos_frescos_disponibles(self, horas: int = 12) -> bool:
        """Verifica si hay datos frescos (actualizados recientemente)"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            fecha_limite = (datetime.now() - timedelta(hours=horas)).isoformat()
            cursor.execute(
                "SELECT COUNT(*) FROM procesos WHERE actualizado_en >= ?",
                (fecha_limite,)
            )
            return cursor.fetchone()[0] > 0
    
    def limpiar_datos_antiguos(self, dias: int = 30):
        """Elimina procesos más antiguos que N días"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            fecha_limite = (datetime.now() - timedelta(days=dias)).isoformat()
            cursor.execute(
                "DELETE FROM procesos WHERE actualizado_en < ?",
                (fecha_limite,)
            )
            eliminados = cursor.rowcount
            print(f"🗑️ Eliminados {eliminados} procesos antiguos")
            return eliminados


# Instancia global singleton
_db_instance: Optional[SeaceDB] = None


def get_seace_db() -> SeaceDB:
    """Obtiene la instancia global de la base de datos"""
    global _db_instance
    if _db_instance is None:
        _db_instance = SeaceDB()
    return _db_instance


if __name__ == "__main__":
    # Test básico
    db = SeaceDB()
    
    # Insertar proceso de prueba
    proceso_test = {
        'nomenclatura': 'TEST-001-2026',
        'entidad': 'ENTIDAD DE PRUEBA',
        'descripcion': 'Descripción de prueba para verificar funcionamiento',
        'tipo_objeto': 'Obra',
        'departamento': 'ANCASH',
        'valor_referencial': 1000000.00,
        'estado': 'Convocado'
    }
    
    db.guardar_proceso(proceso_test)
    print("✅ Proceso guardado")
    
    # Buscar
    resultados = db.buscar(departamento='ANCASH', solo_frescos=False)
    print(f"✅ Encontrados: {len(resultados)} procesos")
    
    # Estadísticas
    stats = db.obtener_estadisticas()
    print(f"📊 Estadísticas: {stats}")
