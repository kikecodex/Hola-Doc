"""
Agente de Contrataciones Públicas del Perú
API REST con Flask - Versión 4.0 con procesamiento de PDFs
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import tempfile

from config import Config
from engine.conversation import ConversationEngine
from engine.calculator import ProcurementCalculator
from engine.opiniones import OpinionesOECE, get_opiniones_info
from engine.tribunal import TribunalContrataciones, get_tribunal_info
from engine.penalties import PenaltiesCalculator, get_penalties_info
from engine.adicionales import AdicionalesCalculator, get_adicionales_info
from engine.plazos import PlazosCalculator, get_plazos_info
from engine.impedimentos import ImpedimentosVerifier, get_impedimentos_info
from engine.nulidad import NulidadAnalyzer, get_nulidad_info
from engine.ampliaciones import AmpliacionesResolucion, get_ampliaciones_info, get_resolucion_info
from engine.jprd_arbitraje import JPRDArbitraje, get_jprd_info, get_arbitraje_info
# Módulos avanzados
from engine.observaciones import ObservacionesGenerator, get_observaciones_info
from engine.apelaciones import ApelacionesGenerator, get_apelaciones_info
from engine.evaluador_propuestas import EvaluadorPropuestas, get_evaluador_info
# Procesador de PDFs
from engine.pdf_processor import PDFProcessor, DocumentAnalyzer, get_pdf_processor_info
# Buscador SEACE
from engine.seace_scraper import (
    SEACEScraper, SEACEAutoSearcher, get_seace_auto_searcher,
    iniciar_busqueda_automatica, get_seace_info, buscar_procesos_rapido,
    SeleniumSEACEScraper, get_selenium_scraper, buscar_seace_real
)
# SEACE con autenticación - REMOVIDO (no utilizado en producción)

# SEACE con API OCDS (datos abiertos oficiales)
try:
    from engine.seace_ocds import OCDSScraper, buscar_con_ocds
    SEACE_OCDS_AVAILABLE = True
except ImportError:
    SEACE_OCDS_AVAILABLE = False
    print("[WARN] OCDSScraper no disponible")

# Inicializar Flask
app = Flask(__name__, static_folder='static')
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
ALLOWED_EXTENSIONS = {'pdf'}

# Inicializar motores
conversation_engine = None
calculator = ProcurementCalculator()
opiniones = OpinionesOECE()
tribunal = TribunalContrataciones()
penalties_calc = PenaltiesCalculator()
adicionales_calc = AdicionalesCalculator()
plazos_calc = PlazosCalculator()
impedimentos_verifier = ImpedimentosVerifier()
nulidad_analyzer = NulidadAnalyzer()
ampliaciones_module = AmpliacionesResolucion()
jprd_module = JPRDArbitraje()
# Instancias de módulos avanzados
observaciones_gen = ObservacionesGenerator()
apelaciones_gen = ApelacionesGenerator()
evaluador = EvaluadorPropuestas()
# Instancia del procesador de PDFs
document_analyzer = DocumentAnalyzer()
# Instancia del buscador SEACE
seace_scraper = SEACEScraper()

def allowed_file(filename):
    """Verifica si el archivo tiene extensión permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_engines():
    """Inicializa los motores del agente"""
    global conversation_engine
    try:
        Config.validate()
        conversation_engine = ConversationEngine()
        print("[OK] Motores inicializados correctamente")
    except Exception as e:
        print(f"[WARN] Error inicializando motores: {e}")
        print("El agente funcionará en modo limitado (solo calculadora)")

# ============================================
# RUTAS API - PRINCIPAL
# ============================================

@app.route('/')
def index():
    """Página principal"""
    return send_from_directory('static', 'index.html')

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'agent': 'Agente de Contrataciones Públicas - Experto',
        'version': '2.0.0',
        'ai_ready': conversation_engine is not None,
        'modules': [
            'calculator', 'opiniones', 'tribunal', 'chat',
            'penalties', 'adicionales', 'plazos', 
            'impedimentos', 'nulidad', 'ampliaciones',
            'jprd', 'arbitraje', 'seace'
        ]
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint principal del chat"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')
        
        if not message:
            return jsonify({'error': 'Mensaje vacío'}), 400
        
        message_lower = message.lower()
        
        # Detectar consultas específicas sobre opiniones
        if any(word in message_lower for word in ['opinión', 'opinion', 'opiniones', 'dtn']) and not ('?' in message and len(message.split()) > 4):
            resultados = opiniones.buscar_opinion(message)
            if resultados:
                response = opiniones.formatear_lista_opiniones(resultados)
                return jsonify({
                    'response': response,
                    'type': 'opiniones',
                    'session_id': session_id
                })
        
        # Detectar consultas sobre tribunal
        if any(word in message_lower for word in ['tribunal', 'sanción', 'sancion', 'inhabilitación', 'inhabilitacion', 'resolución tce', 'resolucion tce']):
            resultados = tribunal.buscar_resoluciones(message)
            if resultados:
                response = tribunal.formatear_lista_resoluciones(resultados)
                return jsonify({
                    'response': response,
                    'type': 'tribunal',
                    'session_id': session_id
                })
        
        # Detectar consultas sobre SEACE / procesos de selección
        seace_keywords = ['seace', 'licitación', 'licitacion', 'proceso de selección', 
                         'proceso de seleccion', 'convocatoria', 'obras públicas', 
                         'obras publicas', 'buscar proceso', 'buscar licitación',
                         'buscar licitacion', 'consultoría de obra', 'consultoria de obra']
        if any(word in message_lower for word in seace_keywords):
            resumen = buscar_procesos_rapido(message)
            return jsonify({
                'response': resumen,
                'type': 'seace',
                'session_id': session_id
            })
        
        # Verificar si es una consulta de cálculo
        calc_result = calculator.detect_and_calculate(message)
        if calc_result:
            return jsonify({
                'response': calc_result,
                'type': 'calculation',
                'session_id': session_id
            })
        
        # Usar motor conversacional si está disponible
        if conversation_engine:
            response = conversation_engine.process(message, session_id)
            return jsonify({
                'response': response,
                'type': 'conversation',
                'session_id': session_id
            })
        else:
            return jsonify({
                'response': '⚠️ El motor de IA no está configurado. Por favor configura tu OPENAI_API_KEY en el archivo .env',
                'type': 'error',
                'session_id': session_id
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rag/ingest', methods=['POST'])
def rag_ingest():
    """Forzar ingestión de documentos para RAG"""
    if not conversation_engine or not conversation_engine.rag_engine:
        return jsonify({'error': 'Motor RAG no inicializado'}), 503
        
    try:
        result = conversation_engine.rag_engine.ingest_documents()
        return jsonify({
            'status': 'success',
            'message': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# RUTAS API - CALCULADORA
# ============================================

@app.route('/api/calculate', methods=['POST'])
def calculate():
    """Calcula el procedimiento de selección según monto y tipo"""
    try:
        data = request.get_json()
        monto = float(data.get('monto', 0))
        tipo = data.get('tipo', 'bienes').lower()
        
        result = calculator.get_procedure(monto, tipo)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/procedures', methods=['GET'])
def get_procedures():
    """Obtiene la lista de procedimientos y montos vigentes"""
    return jsonify(calculator.get_all_procedures())

@app.route('/api/principles', methods=['GET'])
def get_principles():
    """Obtiene los principios de la Ley 32069"""
    from engine.responses import get_principles
    return jsonify(get_principles())

# ============================================
# RUTAS API - OPINIONES OECE
# ============================================

@app.route('/api/opiniones', methods=['GET'])
def get_opiniones():
    """Obtiene información sobre opiniones OECE"""
    return jsonify({
        'info': get_opiniones_info(),
        'recientes': opiniones.listar_opiniones_recientes(5)
    })

@app.route('/api/opiniones/buscar', methods=['POST'])
def buscar_opiniones():
    """Busca opiniones por tema"""
    try:
        data = request.get_json()
        consulta = data.get('consulta', '')
        
        resultados = opiniones.buscar_opinion(consulta)
        return jsonify({
            'resultados': resultados,
            'total': len(resultados)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/opiniones/<numero>', methods=['GET'])
def get_opinion(numero):
    """Obtiene una opinión específica por número"""
    opinion = opiniones.obtener_opinion_por_numero(numero)
    if opinion:
        return jsonify(opinion)
    return jsonify({'error': 'Opinión no encontrada'}), 404

# ============================================
# RUTAS API - TRIBUNAL DE CONTRATACIONES
# ============================================

@app.route('/api/tribunal', methods=['GET'])
def get_tribunal():
    """Obtiene información sobre el Tribunal de Contrataciones"""
    return jsonify({
        'info': get_tribunal_info(),
        'tipos_sanciones': tribunal.obtener_tipos_sanciones(),
        'infracciones': tribunal.obtener_infracciones()
    })

@app.route('/api/tribunal/resoluciones', methods=['GET'])
def get_resoluciones():
    """Obtiene resoluciones recientes del Tribunal"""
    return jsonify({
        'resoluciones': tribunal.RESOLUCIONES_RELEVANTES
    })

@app.route('/api/tribunal/buscar', methods=['POST'])
def buscar_resoluciones():
    """Busca resoluciones por materia"""
    try:
        data = request.get_json()
        consulta = data.get('consulta', '')
        
        resultados = tribunal.buscar_resoluciones(consulta)
        return jsonify({
            'resultados': resultados,
            'total': len(resultados)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tribunal/sanciones', methods=['GET'])
def get_sanciones():
    """Obtiene los tipos de sanciones"""
    return jsonify(tribunal.obtener_tipos_sanciones())

@app.route('/api/tribunal/infracciones', methods=['GET'])
def get_infracciones():
    """Obtiene la lista de infracciones"""
    return jsonify(tribunal.obtener_infracciones())

# ============================================
# RUTAS API - PENALIDADES
# ============================================

@app.route('/api/penalidades', methods=['GET'])
def get_penalidades_info_route():
    """Información sobre penalidades"""
    return jsonify({'info': get_penalties_info()})

@app.route('/api/penalidades/calcular', methods=['POST'])
def calcular_penalidad():
    """Calcula penalidad por mora"""
    try:
        data = request.get_json()
        monto = float(data.get('monto', 0))
        plazo = int(data.get('plazo', 0))
        dias_atraso = int(data.get('dias_atraso', 0))
        tipo = data.get('tipo', 'bienes')
        
        resultado = penalties_calc.calcular_penalidad_total(monto, plazo, dias_atraso, tipo)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# RUTAS API - ADICIONALES
# ============================================

@app.route('/api/adicionales', methods=['GET'])
def get_adicionales_info_route():
    """Información sobre adicionales"""
    return jsonify({'info': get_adicionales_info()})

@app.route('/api/adicionales/calcular', methods=['POST'])
def calcular_adicional():
    """Calcula adicional de obra o bienes/servicios"""
    try:
        data = request.get_json()
        monto_contrato = float(data.get('monto_contrato', 0))
        monto_adicional = float(data.get('monto_adicional', 0))
        tipo = data.get('tipo', 'obra')
        
        if tipo == 'obra':
            resultado = adicionales_calc.calcular_adicional_obra(monto_contrato, monto_adicional)
        else:
            resultado = adicionales_calc.calcular_adicional_bienes_servicios(monto_contrato, monto_adicional)
        
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# RUTAS API - PLAZOS
# ============================================

@app.route('/api/plazos', methods=['GET'])
def get_plazos_info_route():
    """Información sobre plazos"""
    return jsonify({'info': get_plazos_info()})

@app.route('/api/plazos/calcular', methods=['POST'])
def calcular_plazo():
    """Calcula un plazo en días hábiles"""
    try:
        data = request.get_json()
        fecha_inicio = data.get('fecha_inicio', '')
        tipo_plazo = data.get('tipo_plazo', '')
        
        if tipo_plazo:
            resultado = plazos_calc.calcular_plazo(fecha_inicio, tipo_plazo)
        else:
            dias = int(data.get('dias', 8))
            tipo_dias = data.get('tipo_dias', 'habiles')
            resultado = plazos_calc.calcular_plazo_generico(fecha_inicio, dias, tipo_dias)
        
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# RUTAS API - IMPEDIMENTOS
# ============================================

@app.route('/api/impedimentos', methods=['GET'])
def get_impedimentos_info_route():
    """Información sobre impedimentos"""
    return jsonify({
        'info': get_impedimentos_info(),
        'lista_impedidos': impedimentos_verifier.obtener_lista_impedidos()
    })

@app.route('/api/impedimentos/verificar', methods=['POST'])
def verificar_impedimento():
    """Verifica si existe impedimento"""
    try:
        data = request.get_json()
        cargo = data.get('cargo', '')
        meses_cese = int(data.get('meses_desde_cese', 0))
        parentesco = data.get('parentesco', '')
        
        if parentesco:
            resultado = impedimentos_verifier.verificar_impedimento_parentesco(parentesco, cargo)
        else:
            resultado = impedimentos_verifier.verificar_impedimento_cargo(cargo, meses_cese)
        
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# RUTAS API - NULIDAD
# ============================================

@app.route('/api/nulidad', methods=['GET'])
def get_nulidad_info_route():
    """Información sobre causales de nulidad"""
    return jsonify({
        'info': get_nulidad_info(),
        'causales': nulidad_analyzer.obtener_causales()
    })

@app.route('/api/nulidad/analizar', methods=['POST'])
def analizar_nulidad():
    """Analiza un caso para identificar causales de nulidad"""
    try:
        data = request.get_json()
        descripcion = data.get('descripcion', '')
        resultado = nulidad_analyzer.analizar_causal(descripcion)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# RUTAS API - AMPLIACIONES Y RESOLUCIÓN
# ============================================

@app.route('/api/ampliaciones', methods=['GET'])
def get_ampliaciones_info_route():
    """Información sobre ampliaciones de plazo"""
    return jsonify({'info': get_ampliaciones_info()})

@app.route('/api/resolucion', methods=['GET'])
def get_resolucion_info_route():
    """Información sobre resolución de contratos"""
    return jsonify({'info': get_resolucion_info()})

@app.route('/api/ampliaciones/evaluar', methods=['POST'])
def evaluar_ampliacion():
    """Evalúa una solicitud de ampliación"""
    try:
        data = request.get_json()
        causal = data.get('causal', '')
        dias_solicitados = int(data.get('dias_solicitados', 0))
        dias_conocimiento = int(data.get('dias_desde_conocimiento', 0))
        
        resultado = ampliaciones_module.evaluar_ampliacion(causal, dias_solicitados, dias_conocimiento)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# RUTAS API - JPRD Y ARBITRAJE
# ============================================

@app.route('/api/jprd', methods=['GET'])
def get_jprd_info_route():
    """Información sobre JPRD"""
    return jsonify({'info': get_jprd_info()})

@app.route('/api/arbitraje', methods=['GET'])
def get_arbitraje_info_route():
    """Información sobre arbitraje"""
    return jsonify({
        'info': get_arbitraje_info(),
        'clausula_tipo': jprd_module.obtener_clausula_tipo()
    })

@app.route('/api/jprd/verificar', methods=['POST'])
def verificar_jprd():
    """Verifica si JPRD es obligatoria"""
    try:
        data = request.get_json()
        monto_obra = float(data.get('monto_obra', 0))
        resultado = jprd_module.es_obligatoria_jprd(monto_obra)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/apelacion/calcular', methods=['POST'])
def calcular_tasa_apelacion():
    """Calcula la tasa de apelación"""
    try:
        data = request.get_json()
        valor_referencial = float(data.get('valor_referencial', 0))
        resultado = calculator.calcular_tasa_apelacion(valor_referencial)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# RUTAS API - OBSERVACIONES A BASES
# ============================================

@app.route('/api/observaciones', methods=['GET'])
def get_observaciones_info_route():
    """Información sobre observaciones a las bases"""
    return jsonify({'info': get_observaciones_info()})

@app.route('/api/observaciones/analizar-experiencia', methods=['POST'])
def analizar_experiencia():
    """Analiza si requisito de experiencia es excesivo"""
    try:
        data = request.get_json()
        experiencia_requerida = float(data.get('experiencia_requerida', 0))
        valor_referencial = float(data.get('valor_referencial', 0))
        tipo = data.get('tipo', 'postor')
        
        resultado = observaciones_gen.analizar_requisito_experiencia(
            experiencia_requerida, valor_referencial, tipo
        )
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/observaciones/analizar-plazo', methods=['POST'])
def analizar_plazo_proceso():
    """Analiza si plazo de ejecución es razonable"""
    try:
        data = request.get_json()
        plazo_dias = int(data.get('plazo_dias', 0))
        tipo_contratacion = data.get('tipo_contratacion', 'servicios')
        complejidad = data.get('complejidad', 'media')
        
        resultado = observaciones_gen.analizar_plazo_ejecucion(
            plazo_dias, tipo_contratacion, complejidad
        )
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/observaciones/analizar-penalidad', methods=['POST'])
def analizar_penalidad_bases():
    """Analiza si penalidad cumple con Art. 163"""
    try:
        data = request.get_json()
        penalidad_diaria = float(data.get('penalidad_diaria', 0))
        plazo_dias = int(data.get('plazo_dias', 0))
        monto_contrato = float(data.get('monto_contrato', 0))
        
        resultado = observaciones_gen.analizar_penalidad(
            penalidad_diaria, plazo_dias, monto_contrato
        )
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/observaciones/generar', methods=['POST'])
def generar_observacion():
    """
    Genera documento formal de observación con fundamento legal profesional.
    Aplica la Ley 32069, Reglamento D.S. 009-2025-EF y jurisprudencia del TCE.
    """
    try:
        data = request.get_json()
        vicios = data.get('vicios', [])
        datos_proceso = data.get('datos_proceso', {})
        datos_observante = data.get('datos_observante', {})
        
        if not vicios:
            return jsonify({'error': 'No se proporcionaron vicios para observar'}), 400
        
        # Base de datos de fundamentos legales para cada tipo de vicio
        FUNDAMENTOS_LEGALES = {
            "experiencia": {
                "articulos": [
                    "Art. 2, numeral 8 de la Ley 32069 (Principio de Libertad de Concurrencia)",
                    "Art. 29 del Reglamento D.S. 009-2025-EF (Proporcionalidad de requisitos de calificación)",
                    "Art. 45 del Reglamento (Experiencia del postor)"
                ],
                "fundamento": """El requisito de experiencia establecido en las bases resulta MANIFIESTAMENTE EXCESIVO 
y DESPROPORCIONADO respecto al objeto de la contratación, contraviniendo el PRINCIPIO DE LIBERTAD DE 
CONCURRENCIA consagrado en el Art. 2, numeral 8 de la Ley 32069, que establece que las Entidades deben 
promover el libre acceso y participación de proveedores sin exigencias que limiten injustificadamente 
la competencia.

Asimismo, el Art. 29 del Reglamento prescribe que los requisitos de calificación deben ser RAZONABLES 
y PROPORCIONALES al objeto del contrato, debiendo guardar relación directa con la capacidad necesaria 
para ejecutar el contrato. El Art. 45 del Reglamento establece que la experiencia del postor debe 
acreditarse con un monto facturado acumulado que NO EXCEDA el valor estimado del procedimiento.

La exigencia de experiencia que supera el valor referencial constituye una BARRERA DE ACCESO que 
restringe indebidamente la participación de postores técnicamente calificados, afectando la pluralidad 
de participantes y la obtención de las condiciones más ventajosas para el Estado.""",
                "jurisprudencia": [
                    "Res. 1850-2025-TCE-S1: Los requisitos de experiencia excesivos constituyen barreras de acceso",
                    "Res. 2150-2025-TCE-S2: La experiencia requerida debe ser proporcional al VR del proceso"
                ],
                "petitorio": """En virtud de lo expuesto, al amparo del Art. 51 del Reglamento, solicito:
PRIMERO: Se ACOJA la presente observación por encontrarse debidamente fundamentada.
SEGUNDO: Se MODIFIQUE el requisito de experiencia del postor, reduciéndolo a un monto que no exceda 
el valor referencial del proceso, conforme al Art. 45 del Reglamento.
TERCERO: Se publique la absolución de la observación en el SEACE con la debida modificación."""
            },
            "garantia": {
                "articulos": [
                    "Art. 33 de la Ley 32069 (Garantías)",
                    "Art. 162 del Reglamento D.S. 009-2025-EF (Garantía de fiel cumplimiento)"
                ],
                "fundamento": """El plazo o monto de garantía exigido en las bases contraviene los límites establecidos 
en el Art. 33 de la Ley 32069 y Art. 162 del Reglamento, que establecen que la garantía de fiel 
cumplimiento debe ser equivalente al DIEZ POR CIENTO (10%) del monto del contrato original, 
con un plazo máximo de vigencia determinado.

Exigir garantías que excedan estos parámetros constituye una carga financiera desproporcional que 
afecta la competencia efectiva y vulnera el principio de EFICIENCIA en la contratación pública.""",
                "jurisprudencia": [
                    "Res. 1650-2025-TCE-S1: Garantías que exceden límites legales son nulas"
                ],
                "petitorio": """SOLICITO se modifique el requisito de garantía adecuándolo a los límites del Art. 33 
de la Ley 32069 y Art. 162 del Reglamento."""
            },
            "marca": {
                "articulos": [
                    "Art. 16 de la Ley 32069 (Especificaciones técnicas)",
                    "Art. 2, numeral 10 de la Ley 32069 (Principio de Competencia)",
                    "Art. 37 del Reglamento D.S. 009-2025-EF (Requerimientos)"
                ],
                "fundamento": """Las especificaciones técnicas hacen referencia DIRECTA O INDIRECTA a una marca, 
fabricante o proveedor específico, sin incluir la expresión 'O EQUIVALENTE', contraviniendo 
EXPRESAMENTE el Art. 16 de la Ley 32069 que PROHÍBE la referencia a marcas, patentes o tipos 
que orienten la contratación hacia un determinado proveedor.

Esta práctica constituye un DIRECCIONAMIENTO de la contratación que vulnera el PRINCIPIO DE 
COMPETENCIA (Art. 2, numeral 10) al impedir que proveedores de productos equivalentes participen 
en igualdad de condiciones, restringiendo artificialmente el universo de postores potenciales.""",
                "jurisprudencia": [
                    "Res. 2000-2025-TCE-S2: La mención de marca sin 'o equivalente' direcciona la contratación",
                    "Res. 1800-2025-TCE-S1: Especificaciones direccionadas vulneran la libre competencia"
                ],
                "petitorio": """SOLICITO se elimine la referencia a marca específica o, en su defecto, se incluya 
la expresión 'O EQUIVALENTE' conforme al Art. 16 de la Ley 32069, permitiendo la participación 
de productos de similares características técnicas."""
            },
            "claridad": {
                "articulos": [
                    "Art. 2, numeral 4 de la Ley 32069 (Principio de Transparencia)",
                    "Art. 28 del Reglamento D.S. 009-2025-EF (Factores de evaluación)",
                    "Art. 73 del Reglamento (Criterios de evaluación técnica)"
                ],
                "fundamento": """Los criterios de evaluación técnica carecen de la OBJETIVIDAD y CLARIDAD requeridas 
por el Art. 28 del Reglamento, que exige que los factores de evaluación sean OBJETIVOS, RAZONABLES, 
CONGRUENTES y PROPORCIONALES con el objeto de la contratación.

La falta de parámetros claros y cuantificables para la evaluación vulnera el PRINCIPIO DE 
TRANSPARENCIA (Art. 2, numeral 4 de la Ley 32069), generando INSEGURIDAD JURÍDICA en los 
postores sobre cómo serán evaluadas sus propuestas y abriendo espacios de DISCRECIONALIDAD 
indebida en la calificación.""",
                "jurisprudencia": [
                    "Res. 2100-2025-TCE-SP: Factores subjetivos vulneran igualdad de trato",
                    "Res. 1950-2025-TCE-S2: Criterios deben ser objetivos y medibles"
                ],
                "petitorio": """SOLICITO se reformulen los criterios de evaluación estableciendo parámetros OBJETIVOS 
y CUANTIFICABLES que permitan a los postores conocer con certeza cómo serán evaluados."""
            },
            "plazo": {
                "articulos": [
                    "Art. 16 de la Ley 32069 (Especificaciones objetivas)",
                    "Art. 2, numeral 7 de la Ley 32069 (Principio de Sostenibilidad)",
                    "Art. 37 del Reglamento D.S. 009-2025-EF (Contenido del requerimiento)"
                ],
                "fundamento": """El plazo de ejecución establecido resulta TÉCNICAMENTE INVIABLE para cumplir 
adecuadamente con el objeto contractual, evidenciando deficiencias en el estudio de mercado 
o posible direccionamiento hacia proveedores que cuenten con stock o capacidad excepcional.

Un plazo irreal vulnera el PRINCIPIO DE SOSTENIBILIDAD (Art. 2, numeral 7 de la Ley 32069) 
pues compromete la calidad del producto/servicio y la correcta ejecución contractual.""",
                "jurisprudencia": [
                    "Res. 1900-2025-TCE-S1: Plazos irreales afectan la competencia efectiva"
                ],
                "petitorio": """SOLICITO se amplíe el plazo de ejecución a uno técnicamente viable que permita 
el cumplimiento adecuado de las prestaciones contratadas."""
            },
            "penalidad": {
                "articulos": [
                    "Art. 163 del Reglamento D.S. 009-2025-EF (Penalidad por mora)",
                    "Art. 164 del Reglamento (Otras penalidades)"
                ],
                "fundamento": """La penalidad establecida en las bases EXCEDE los límites del Art. 163 del 
Reglamento que prescribe la fórmula: Penalidad diaria = (0.10 x monto) / (F x plazo).

El factor F aplicable es: 0.40 para plazos ≤60 días, 0.25 para plazos entre 61-120 días, 
y 0.15 para plazos >120 días. Penalidades que excedan estos límites son ILEGALES y 
generan un desincentivo desproporcionado a la participación de postores.""",
                "jurisprudencia": [
                    "Res. 1750-2025-TCE-S1: Penalidades excesivas son inaplicables por ilegales"
                ],
                "petitorio": """SOLICITO se ajuste la penalidad por mora a los límites del Art. 163 del Reglamento, 
aplicando el factor F que corresponda según el plazo del contrato."""
            }
        }
        
        # Función para encontrar el fundamento legal más apropiado
        def obtener_fundamento(tipo_vicio, descripcion):
            tipo_lower = tipo_vicio.lower() if tipo_vicio else ""
            desc_lower = descripcion.lower() if descripcion else ""
            
            # Mapeo de palabras clave a tipos de fundamento
            for key in FUNDAMENTOS_LEGALES.keys():
                if key in tipo_lower or key in desc_lower:
                    return FUNDAMENTOS_LEGALES[key]
            
            # Detección por palabras específicas
            if any(w in desc_lower or w in tipo_lower for w in ['experiencia', 'postor', 'excesi', 'art. 45', 'art. 29']):
                return FUNDAMENTOS_LEGALES['experiencia']
            if any(w in desc_lower or w in tipo_lower for w in ['marca', 'direcc', 'equivalente', 'fabricante']):
                return FUNDAMENTOS_LEGALES['marca']
            if any(w in desc_lower or w in tipo_lower for w in ['claridad', 'evalua', 'criterio', 'objetivo', 'subjetivo']):
                return FUNDAMENTOS_LEGALES['claridad']
            if any(w in desc_lower or w in tipo_lower for w in ['garant', 'art. 33', 'art. 162']):
                return FUNDAMENTOS_LEGALES['garantia']
            if any(w in desc_lower or w in tipo_lower for w in ['plazo', 'día', 'tiempo', 'ejecución']):
                return FUNDAMENTOS_LEGALES['plazo']
            if any(w in desc_lower or w in tipo_lower for w in ['penalidad', 'mora', 'art. 163']):
                return FUNDAMENTOS_LEGALES['penalidad']
            
            # Fundamento genérico si no hay match
            return {
                "articulos": [
                    "Art. 2 de la Ley 32069 (Principios que rigen la contratación pública)",
                    "Art. 51 del Reglamento D.S. 009-2025-EF (Formulación de observaciones)"
                ],
                "fundamento": """El aspecto observado contraviene los principios rectores de la contratación 
pública establecidos en la Ley 32069, específicamente los principios de Libertad de Concurrencia, 
Competencia, Igualdad de Trato y Transparencia.""",
                "jurisprudencia": ["Revisar jurisprudencia aplicable del TCE"],
                "petitorio": "SOLICITO se modifique el aspecto observado conforme a la normativa vigente."
            }
        
        # Generar documento profesional
        fecha_actual = datetime.now().strftime("%d de %B de %Y").replace(
            'January', 'enero').replace('February', 'febrero').replace('March', 'marzo'
            ).replace('April', 'abril').replace('May', 'mayo').replace('June', 'junio'
            ).replace('July', 'julio').replace('August', 'agosto').replace('September', 'septiembre'
            ).replace('October', 'octubre').replace('November', 'noviembre').replace('December', 'diciembre')
        
        # Encabezado del documento
        documento = f"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                              FORMULACIÓN DE OBSERVACIONES A LAS BASES                                ║
║                                    Ley N° 32069 - Art. 51 del Reglamento                             ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝

SUMILLA: OBSERVACIONES A LAS BASES DEL PROCEDIMIENTO DE SELECCIÓN

▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

SEÑORES:
{datos_proceso.get('entidad', '[ENTIDAD CONTRATANTE]')}
Comité de Selección
Presente.-

REFERENCIA: {datos_proceso.get('numero_proceso', 'Procedimiento de Selección N° XXX-2026')}
            {datos_proceso.get('objeto', 'Contratación de bienes/servicios/obras')}

OBSERVANTE: {datos_observante.get('nombre', '[NOMBRE O RAZÓN SOCIAL DEL PARTICIPANTE]')}
RUC:         {datos_observante.get('ruc', '[N° RUC]')}
DOMICILIO:   {datos_observante.get('domicilio', '[DOMICILIO LEGAL]')}

▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

De nuestra consideración:

Por medio del presente, en uso del derecho que nos asiste conforme al ARTÍCULO 51 del 
Reglamento de la Ley de Contrataciones del Estado (D.S. N° 009-2025-EF), procedemos a 
formular OBSERVACIONES a las Bases del procedimiento de selección de la referencia, 
las mismas que se sustentan en los siguientes términos:

"""
        
        # Agregar cada observación
        for i, vicio in enumerate(vicios, 1):
            tipo_vicio = vicio.get('tipo', vicio.get('categoria', 'Vicio detectado'))
            descripcion = vicio.get('descripcion', vicio.get('detalle', str(vicio)))
            base_legal = vicio.get('base_legal', vicio.get('fundamento_legal', ''))
            
            # Obtener fundamento legal apropiado
            fundamento = obtener_fundamento(tipo_vicio, descripcion)
            
            documento += f"""
═══════════════════════════════════════════════════════════════════════════════════════════════════════
                                         OBSERVACIÓN N° {i}
═══════════════════════════════════════════════════════════════════════════════════════════════════════

I. ASPECTO OBSERVADO
───────────────────────────────────────────────────────────────────────────────────────────────────────
   📌 TIPO: {tipo_vicio.upper()}
   📋 DESCRIPCIÓN: {descripcion}
"""
            # Construir ubicación detallada con página y capítulo
            ubicacion_partes = []
            if vicio.get('pagina'):
                ubicacion_partes.append(f"Página {vicio['pagina']}")
            if vicio.get('capitulo'):
                ubicacion_partes.append(f"Capítulo: {vicio['capitulo']}")
            if vicio.get('ubicacion') and 'Página' not in vicio.get('ubicacion', ''):
                ubicacion_partes.append(vicio['ubicacion'])
            
            ubicacion_final = " - ".join(ubicacion_partes) if ubicacion_partes else "Numeral correspondiente de las Bases"
            documento += f"   📍 UBICACIÓN: {ubicacion_final}\n"
            
            # Agregar cita textual si está disponible
            if vicio.get('cita_textual'):
                documento += f"   📖 EXTRACTO: \"{vicio['cita_textual']}\"\n"
            
            documento += f"""
II. BASE LEGAL (Artículos que se contravienen)
───────────────────────────────────────────────────────────────────────────────────────────────────────
"""
            for art in fundamento['articulos']:
                documento += f"   ⚖️  {art}\n"
            
            if base_legal:
                documento += f"   ⚖️  {base_legal}\n"
            
            documento += f"""
III. FUNDAMENTACIÓN JURÍDICA
───────────────────────────────────────────────────────────────────────────────────────────────────────
{fundamento['fundamento']}

IV. JURISPRUDENCIA APLICABLE DEL TRIBUNAL DE CONTRATACIONES
───────────────────────────────────────────────────────────────────────────────────────────────────────
"""
            for juris in fundamento['jurisprudencia']:
                documento += f"   📚 {juris}\n"
            
            documento += f"""
V. PETITORIO / SOLICITUD CONCRETA
───────────────────────────────────────────────────────────────────────────────────────────────────────
{fundamento['petitorio']}

"""
        
        # Cierre del documento
        documento += f"""
═══════════════════════════════════════════════════════════════════════════════════════════════════════
                                         SOLICITUD FINAL
═══════════════════════════════════════════════════════════════════════════════════════════════════════

Por lo expuesto, SOLICITO:

1️⃣  Se ACOJAN las observaciones formuladas por encontrarse debidamente fundamentadas en 
    la Ley N° 32069 y su Reglamento D.S. N° 009-2025-EF.

2️⃣  Se MODIFIQUEN las Bases del procedimiento conforme a las observaciones sustentadas.

3️⃣  Se PUBLIQUE la absolución de observaciones en el SEACE, de acuerdo al Art. 52 del 
    Reglamento.

4️⃣  De no ser acogidas las observaciones, se ELEVE las mismas al OSCE para su 
    pronunciamiento, conforme al Art. 53 del Reglamento.

▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

Lima, {fecha_actual}

Atentamente,



_______________________________________
{datos_observante.get('nombre', '[FIRMA DEL OBSERVANTE]')}
{datos_observante.get('cargo', 'Representante Legal')}
RUC: {datos_observante.get('ruc', 'N° RUC')}

═══════════════════════════════════════════════════════════════════════════════════════════════════════
   Documento generado por INKABOT - Agente de Contrataciones Públicas del Perú
   Basado en Ley N° 32069 y Reglamento D.S. N° 009-2025-EF (Mod. D.S. N° 001-2026-EF)
═══════════════════════════════════════════════════════════════════════════════════════════════════════
"""
        
        return jsonify({'documento': documento})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/observaciones/analizar-hibrido', methods=['POST'])
def analizar_hibrido():
    """
    Análisis híbrido IA + Reglas de bases de procedimiento
    Combina detección de Gemini con validación de reglas legales para máxima precisión
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No se envió archivo PDF'}), 400
        
        file = request.files['file']
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Solo se permiten archivos PDF'}), 400
        
        filename = secure_filename(file.filename)
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, filename)
        file.save(temp_path)
        
        try:
            # 1. Extraer texto del PDF
            extraccion = document_analyzer.pdf_processor.extraer_texto_pdf(temp_path)
            
            if 'error' in extraccion:
                return jsonify({'error': extraccion['error']}), 500
            
            texto = extraccion['texto_completo']
            
            # 2. Análisis con Gemini (IA)
            analisis_ia = document_analyzer.pdf_processor.analizar_documento_gemini_sync(texto, "bases")
            
            # 3. Extraer valor referencial si está disponible
            datos_basicos = document_analyzer.pdf_processor.extraer_datos_bases(texto)
            valor_referencial = datos_basicos.get('valor_referencial')
            
            # 4. Análisis híbrido (IA + Reglas)
            resultado_hibrido = observaciones_gen.analizar_vicios_hibrido(
                texto, analisis_ia, valor_referencial
            )
            
            # 5. Formatear respuesta para chat
            respuesta_chat = observaciones_gen.formatear_resultado_hibrido(resultado_hibrido)
            
            return jsonify({
                'archivo': extraccion['archivo'],
                'paginas': extraccion['paginas'],
                'valor_referencial': valor_referencial,
                'analisis_hibrido': resultado_hibrido,
                'respuesta_chat': respuesta_chat,
                'motor': 'Híbrido: Gemini AI + Reglas Ley 32069 + Jurisprudencia TCE'
            })
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# RUTAS API - APELACIONES
# ============================================

@app.route('/api/apelaciones', methods=['GET'])
def get_apelaciones_info_route():
    """Información sobre recursos de apelación"""
    return jsonify({
        'info': get_apelaciones_info(),
        'tipos': apelaciones_gen.obtener_tipos_apelacion()
    })

@app.route('/api/apelaciones/calcular-tasa', methods=['POST'])
def calcular_tasa_competencia():
    """Calcula tasa y determina instancia competente"""
    try:
        data = request.get_json()
        valor_referencial = float(data.get('valor_referencial', 0))
        
        resultado = apelaciones_gen.calcular_tasa_y_competencia(valor_referencial)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/apelaciones/calcular-plazo', methods=['POST'])
def calcular_plazo_apelacion():
    """Calcula fecha límite para apelar"""
    try:
        data = request.get_json()
        fecha_notificacion = data.get('fecha_notificacion', '')
        
        resultado = apelaciones_gen.calcular_plazo_limite(fecha_notificacion)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/apelaciones/generar', methods=['POST'])
def generar_apelacion():
    """Genera recurso de apelación completo"""
    try:
        data = request.get_json()
        tipo_apelacion = data.get('tipo_apelacion', 'descalificacion_indebida')
        datos_proceso = data.get('datos_proceso', {})
        datos_apelante = data.get('datos_apelante', {})
        datos_impugnacion = data.get('datos_impugnacion', {})
        
        documento = apelaciones_gen.generar_recurso_apelacion(
            tipo_apelacion, datos_proceso, datos_apelante, datos_impugnacion
        )
        return jsonify({'documento': documento})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# RUTAS API - EVALUADOR DE PROPUESTAS
# ============================================

@app.route('/api/evaluador', methods=['GET'])
def get_evaluador_info_route():
    """Información sobre evaluación de propuestas"""
    return jsonify({'info': get_evaluador_info()})

@app.route('/api/evaluador/verificar-tecnica', methods=['POST'])
def verificar_evaluacion_tecnica():
    """Verifica evaluación técnica"""
    try:
        data = request.get_json()
        puntajes_bases = data.get('puntajes_bases', {})
        puntajes_otorgados = data.get('puntajes_otorgados', {})
        
        resultado = evaluador.verificar_evaluacion_tecnica(
            puntajes_bases, puntajes_otorgados
        )
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/evaluador/verificar-economica', methods=['POST'])
def verificar_evaluacion_economica():
    """Verifica evaluación económica"""
    try:
        data = request.get_json()
        propuestas = data.get('propuestas', [])
        puntaje_maximo = float(data.get('puntaje_economico_maximo', 100))
        
        resultado = evaluador.verificar_evaluacion_economica(propuestas, puntaje_maximo)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/evaluador/calcular-economico', methods=['POST'])
def calcular_puntaje_economico():
    """Calcula puntaje económico según Art. 78"""
    try:
        data = request.get_json()
        precio_propuesta = float(data.get('precio_propuesta', 0))
        precio_menor = float(data.get('precio_menor', 0))
        puntaje_maximo = float(data.get('puntaje_maximo', 100))
        
        resultado = evaluador.calcular_puntaje_economico(
            precio_propuesta, precio_menor, puntaje_maximo
        )
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/evaluador/verificar-prelacion', methods=['POST'])
def verificar_orden_prelacion():
    """Verifica orden de prelación"""
    try:
        data = request.get_json()
        puntajes_totales = data.get('puntajes_totales', [])
        orden_buena_pro = data.get('orden_buena_pro', [])
        
        resultado = evaluador.verificar_orden_prelacion(puntajes_totales, orden_buena_pro)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/evaluador/informe', methods=['POST'])
def generar_informe_evaluacion():
    """Genera informe completo de verificación"""
    try:
        data = request.get_json()
        
        # Verificar evaluación técnica
        resultado_tecnica = evaluador.verificar_evaluacion_tecnica(
            data.get('puntajes_bases', {}),
            data.get('puntajes_otorgados', {})
        )
        
        # Verificar evaluación económica
        resultado_economica = evaluador.verificar_evaluacion_economica(
            data.get('propuestas', [])
        )
        
        # Verificar prelación (opcional)
        resultado_prelacion = None
        if data.get('orden_buena_pro'):
            resultado_prelacion = evaluador.verificar_orden_prelacion(
                data.get('puntajes_totales', []),
                data.get('orden_buena_pro', [])
            )
        
        # Generar informe
        informe = evaluador.generar_informe_inconsistencias(
            resultado_tecnica, resultado_economica, resultado_prelacion
        )
        
        return jsonify({
            'informe': informe,
            'resumen': {
                'tecnica_correcta': resultado_tecnica.get('evaluacion_correcta'),
                'economica_correcta': resultado_economica.get('evaluacion_correcta'),
                'total_errores': resultado_tecnica.get('cantidad_errores', 0) + 
                                len(resultado_economica.get('inconsistencias', []))
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# RUTAS API - EVALUACIÓN POR ETAPAS (NUEVO)
# ============================================

@app.route('/api/evaluador/etapa1-requisitos', methods=['POST'])
def evaluar_requisitos_minimos_route():
    """
    ETAPA 1: Evalúa requisitos mínimos de calificación.
    Si no cumple → DESCALIFICADO
    """
    try:
        data = request.get_json()
        requisitos_bases = data.get('requisitos_bases', [])
        documentos_postor = data.get('documentos_postor', {})
        
        resultado = evaluador.evaluar_requisitos_minimos(requisitos_bases, documentos_postor)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/evaluador/etapa2-rtm', methods=['POST'])
def evaluar_rtm_route():
    """
    ETAPA 2: Evalúa Requerimientos Técnicos Mínimos.
    Si no cumple → DESCALIFICADO
    """
    try:
        data = request.get_json()
        rtm_bases = data.get('rtm_bases', [])
        propuesta_tecnica = data.get('propuesta_tecnica', {})
        
        resultado = evaluador.evaluar_rtm(rtm_bases, propuesta_tecnica)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/evaluador/etapa3-factores', methods=['POST'])
def evaluar_factores_route():
    """
    ETAPA 3: Evalúa factores de evaluación técnica.
    Calcula puntaje técnico.
    """
    try:
        data = request.get_json()
        factores_bases = data.get('factores_bases', [])
        propuesta_tecnica = data.get('propuesta_tecnica', {})
        puntaje_minimo = float(data.get('puntaje_minimo', 0))
        
        resultado = evaluador.evaluar_factores_tecnicos(
            factores_bases, propuesta_tecnica, puntaje_minimo
        )
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/evaluador/etapa4-economica', methods=['POST'])
def evaluar_economica_route():
    """
    ETAPA 4: Evaluación económica completa.
    Detecta ofertas temerarias, calcula puntajes según Art. 78.
    """
    try:
        data = request.get_json()
        propuestas = data.get('propuestas', [])
        valor_referencial = float(data.get('valor_referencial', 0))
        tipo_contratacion = data.get('tipo_contratacion', 'bienes_servicios')
        puntaje_maximo = float(data.get('puntaje_maximo', 100))
        
        resultado = evaluador.evaluar_economica_completa(
            propuestas, valor_referencial, tipo_contratacion, puntaje_maximo
        )
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/evaluador/evaluacion-completa', methods=['POST'])
def evaluacion_completa_route():
    """
    Evaluación integral: Ejecuta las 4 etapas secuencialmente.
    Se detiene si alguna etapa falla.
    """
    try:
        data = request.get_json()
        
        resultado = evaluador.evaluacion_integral(
            requisitos_bases=data.get('requisitos_bases', []),
            rtm_bases=data.get('rtm_bases', []),
            factores_bases=data.get('factores_bases', []),
            propuesta=data.get('propuesta', {}),
            propuestas_economicas=data.get('propuestas_economicas', []),
            valor_referencial=float(data.get('valor_referencial', 0)),
            puntaje_minimo_tecnico=float(data.get('puntaje_minimo_tecnico', 0))
        )
        
        # Generar informe formateado
        informe = evaluador.generar_informe_evaluacion_etapas(resultado)
        resultado['informe_texto'] = informe
        
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/evaluador/analizar-propuesta', methods=['POST'])
def analizar_propuesta_automatico():
    """
    EVALUACIÓN AUTOMÁTICA DE PROPUESTA DESDE PDF.
    Extrae texto del PDF y ejecuta las 4 etapas automáticamente con IA.
    Similar a analizar_bases pero para propuestas.
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No se envió archivo de propuesta'}), 400
        
        file = request.files['file']
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Solo se permiten archivos PDF'}), 400
        
        # Valor referencial opcional
        valor_referencial = float(request.form.get('valor_referencial', 0))
        nombre_postor = request.form.get('nombre_postor', 'Postor Evaluado')
        
        # Archivo de bases opcional
        texto_bases = ""
        if 'bases' in request.files:
            bases_file = request.files['bases']
            if bases_file and allowed_file(bases_file.filename):
                bases_temp = tempfile.mktemp(suffix='.pdf')
                bases_file.save(bases_temp)
                try:
                    extraccion_bases = pdf_processor.extraer_texto_pdf(bases_temp)
                    if "error" not in extraccion_bases:
                        texto_bases = extraccion_bases.get("texto_completo", "")
                finally:
                    if os.path.exists(bases_temp):
                        os.remove(bases_temp)
        
        # Guardar y procesar propuesta
        filename = secure_filename(file.filename)
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, filename)
        file.save(temp_path)
        
        try:
            # Extraer texto de la propuesta
            extraccion = pdf_processor.extraer_texto_pdf(temp_path)
            
            if "error" in extraccion:
                return jsonify({'error': f"Error al procesar PDF: {extraccion['error']}"}), 400
            
            texto_propuesta = extraccion.get("texto_completo", "")
            
            if len(texto_propuesta) < 100:
                return jsonify({
                    'error': 'El PDF no contiene suficiente texto para analizar',
                    'caracteres_extraidos': len(texto_propuesta)
                }), 400
            
            # Ejecutar evaluación automática con IA
            resultado = evaluador.evaluar_propuesta_automatico(
                texto_propuesta=texto_propuesta,
                texto_bases=texto_bases,
                valor_referencial=valor_referencial,
                nombre_postor=nombre_postor
            )
            
            # Agregar metadata del archivo
            resultado['archivo_analizado'] = {
                'nombre': filename,
                'paginas': extraccion.get('paginas', 0),
                'caracteres': len(texto_propuesta)
            }
            
            return jsonify(resultado)
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
                
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

# ============================================
# RUTAS API - PROCESAMIENTO DE PDFs

# ============================================

@app.route('/api/pdf', methods=['GET'])
def get_pdf_info_route():
    """Información sobre procesamiento de PDFs"""
    return jsonify({'info': get_pdf_processor_info()})

@app.route('/api/pdf/upload', methods=['POST'])
def upload_and_analyze_pdf():
    """Sube y analiza un PDF automáticamente"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No se envió archivo'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'Nombre de archivo vacío'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Solo se permiten archivos PDF'}), 400
        
        # Guardar temporalmente
        filename = secure_filename(file.filename)
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, filename)
        file.save(temp_path)
        
        try:
            # Analizar documento
            resultado = document_analyzer.analizar_bases_completo(temp_path)
            
            # Formatear respuesta
            respuesta_formateada = document_analyzer.formatear_resultado_analisis(resultado)
            
            return jsonify({
                'resultado': resultado,
                'respuesta_chat': respuesta_formateada
            })
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pdf/analizar-bases', methods=['POST'])
def analizar_bases_pdf():
    """Analiza bases de un procedimiento para detectar vicios"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No se envió archivo'}), 400
        
        file = request.files['file']
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Solo se permiten archivos PDF'}), 400
        
        filename = secure_filename(file.filename)
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, filename)
        file.save(temp_path)
        
        try:
            resultado = document_analyzer.detectar_vicios_bases(temp_path)
            return jsonify(resultado)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pdf/verificar-evaluacion', methods=['POST'])
def verificar_evaluacion_pdf():
    """Verifica un cuadro de evaluación desde PDF"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No se envió archivo'}), 400
        
        file = request.files['file']
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Solo se permiten archivos PDF'}), 400
        
        filename = secure_filename(file.filename)
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, filename)
        file.save(temp_path)
        
        try:
            # Extraer datos de evaluación
            resultado_extraccion = document_analyzer.analizar_evaluacion(temp_path)
            
            # Si se extrajeron propuestas, verificar los cálculos
            if resultado_extraccion.get('propuestas'):
                propuestas = [
                    {"postor": p["postor"], "precio": p["precio"], "puntaje_otorgado": 0}
                    for p in resultado_extraccion['propuestas']
                ]
                
                # Usar el evaluador para verificar
                verificacion = evaluador.verificar_evaluacion_economica(propuestas)
                
                resultado_extraccion['verificacion'] = verificacion
            
            return jsonify(resultado_extraccion)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pdf/chat', methods=['POST'])
def chat_con_documento():
    """Chat inteligente sobre un documento subido"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No se envió archivo'}), 400
        
        file = request.files['file']
        pregunta = request.form.get('pregunta', 'Analiza este documento')
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Solo se permiten archivos PDF'}), 400
        
        filename = secure_filename(file.filename)
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, filename)
        file.save(temp_path)
        
        try:
            # Extraer texto
            extraccion = document_analyzer.pdf_processor.extraer_texto_pdf(temp_path)
            
            if 'error' in extraccion:
                return jsonify({'error': extraccion['error']}), 500
            
            texto = extraccion['texto_completo']
            
            # Usar Gemini para responder la pregunta
            prompt = f"""Eres INKABOT, experto en contrataciones públicas de Perú (Ley 32069).
            
El usuario ha subido un documento y pregunta: {pregunta}

DOCUMENTO:
{texto[:15000]}

Responde de manera clara y profesional, citando los artículos relevantes de la Ley 32069 o su Reglamento."""
            
            import google.generativeai as genai
            genai.configure(api_key=Config.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(prompt)
            
            return jsonify({
                'archivo': extraccion['archivo'],
                'paginas': extraccion['paginas'],
                'respuesta': response.text
            })
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# RUTAS API - BÚSQUEDA SEACE
# ============================================

@app.route('/api/seace', methods=['GET'])
def get_seace_info_route():
    """Información sobre la búsqueda en SEACE"""
    return jsonify({'info': get_seace_info()})

@app.route('/api/seace/buscar', methods=['POST'])
def buscar_seace():
    """
    Busca procesos en SEACE según los criterios especificados.
    Regiones configuradas: Ancash, Lima
    Tipos: Obras, Servicios, Consultoría de Obras
    """
    try:
        data = request.get_json() or {}
        
        # Obtener parámetros de búsqueda
        tipos = data.get('tipos', None)  # ['obras', 'servicios', 'consultoria_obras']
        departamentos = data.get('departamentos', None)  # ['ANCASH', 'LIMA']
        consulta = data.get('consulta', '')
        
        # Si hay consulta de texto, usar búsqueda rápida
        if consulta:
            resumen = buscar_procesos_rapido(consulta)
            return jsonify({
                'resumen': resumen,
                'tipo': 'busqueda_texto'
            })
        
        # Búsqueda por filtros
        procesos = seace_scraper.buscar_procesos(
            tipos_objeto=tipos,
            departamentos=departamentos
        )
        
        # Generar resumen
        resumen = seace_scraper.generar_resumen_fechas(procesos)
        
        return jsonify({
            'procesos': [p.to_dict() for p in procesos],
            'total': len(procesos),
            'resumen': resumen
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/seace/resumen', methods=['GET'])
def get_seace_resumen():
    """
    Obtiene un resumen rápido de los procesos activos.
    Ideal para visualización en dashboard.
    """
    try:
        auto_searcher = get_seace_auto_searcher()
        procesos = auto_searcher.obtener_ultimo_resultado()
        
        if not procesos:
            # Primera búsqueda si no hay resultados previos
            procesos = seace_scraper.buscar_procesos()
        
        resumen = seace_scraper.generar_resumen_fechas(procesos)
        nuevos = auto_searcher.obtener_nuevos_procesos()
        
        return jsonify({
            'resumen': resumen,
            'total_procesos': len(procesos),
            'nuevos_procesos': len(nuevos),
            'procesos_nuevos': [p.to_dict() for p in nuevos] if nuevos else []
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/seace/obras', methods=['GET'])
def buscar_obras_seace():
    """Busca específicamente procesos de OBRAS en Ancash y Lima"""
    try:
        procesos = seace_scraper.buscar_procesos(tipos_objeto=['obras'])
        resumen = seace_scraper.generar_resumen_fechas(procesos)
        return jsonify({
            'procesos': [p.to_dict() for p in procesos],
            'total': len(procesos),
            'resumen': resumen
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/seace/consultoria', methods=['GET'])
def buscar_consultoria_seace():
    """Busca específicamente procesos de CONSULTORÍA DE OBRAS en Ancash y Lima"""
    try:
        procesos = seace_scraper.buscar_procesos(tipos_objeto=['consultoria_obras'])
        resumen = seace_scraper.generar_resumen_fechas(procesos)
        return jsonify({
            'procesos': [p.to_dict() for p in procesos],
            'total': len(procesos),
            'resumen': resumen
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/seace/servicios', methods=['GET'])
def buscar_servicios_seace():
    """Busca específicamente procesos de SERVICIOS en Ancash y Lima"""
    try:
        procesos = seace_scraper.buscar_procesos(tipos_objeto=['servicios'])
        resumen = seace_scraper.generar_resumen_fechas(procesos)
        return jsonify({
            'procesos': [p.to_dict() for p in procesos],
            'total': len(procesos),
            'resumen': resumen
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/seace/forzar-busqueda', methods=['POST'])
def forzar_busqueda_seace():
    """Fuerza una búsqueda inmediata en SEACE"""
    try:
        auto_searcher = get_seace_auto_searcher()
        procesos = auto_searcher.buscar_ahora()
        resumen = seace_scraper.generar_resumen_fechas(procesos)
        
        return jsonify({
            'mensaje': 'Búsqueda ejecutada correctamente',
            'total_procesos': len(procesos),
            'resumen': resumen
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/seace/buscar-real', methods=['POST'])
def buscar_seace_selenium():
    """
    Busca procesos en SEACE usando Selenium (navegador real).
    
    IMPORTANTE: Abrirá un navegador Chrome visible.
    Si hay CAPTCHA, el usuario debe resolverlo manualmente.
    
    Body (opcional):
    {
        "tipos": ["obras", "servicios", "consultoria_obras"],
        "departamentos": ["ANCASH", "LIMA"]
    }
    """
    try:
        data = request.get_json() or {}
        tipos = data.get('tipos', None)
        departamentos = data.get('departamentos', None)
        
        # Usar el scraper Selenium
        selenium_scraper = get_selenium_scraper()
        
        if not selenium_scraper._selenium_available:
            return jsonify({
                'error': 'Selenium no está instalado. Ejecuta: pip install selenium webdriver-manager',
                'instrucciones': 'Instala las dependencias y reinicia el servidor.'
            }), 400
        
        procesos = selenium_scraper.buscar_procesos_real(
            tipos_objeto=tipos,
            departamentos=departamentos,
            esperar_captcha=True,
            timeout_captcha=120
        )
        
        resumen = seace_scraper.generar_resumen_fechas(procesos)
        
        return jsonify({
            'mensaje': 'Búsqueda real con Selenium completada',
            'procesos': [p.to_dict() for p in procesos],
            'total': len(procesos),
            'resumen': resumen,
            'tipo_busqueda': 'selenium_real'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/seace/buscar-autenticado', methods=['POST'])
def buscar_seace_autenticado():
    """
    Busca procesos en SEACE con autenticación (de Buo).
    
    Usa credenciales configuradas en .env (SEACE_USER, SEACE_PASSWORD)
    Incluye filtrado por IA para procesos de geotecnia/mecánica de suelos.
    
    Body (opcional):
    {
        "palabras_clave": ["geotecnia", "cimentaciones"]
    }
    """
    if not SEACE_AUTH_AVAILABLE:
        return jsonify({
            'error': 'SEACEAuthScraper no disponible',
            'instrucciones': 'Verifica que engine/seace_auth_scraper.py existe'
        }), 400
    
    try:
        import os
        username = os.getenv("SEACE_USER")
        password = os.getenv("SEACE_PASSWORD")
        
        if not username or not password:
            return jsonify({
                'error': 'Credenciales SEACE no configuradas',
                'instrucciones': 'Configura SEACE_USER y SEACE_PASSWORD en .env'
            }), 400
        
        # Iniciar scraper autenticado
        scraper = SEACEAuthScraper(username, password)
        
        # Ejecutar búsqueda
        df = scraper.buscar_procesos_del_dia()
        
        if df.empty:
            return jsonify({
                'mensaje': 'Búsqueda autenticada completada',
                'procesos': [],
                'total': 0,
                'tipo_busqueda': 'autenticado_buo'
            })
        
        # Convertir DataFrame a lista de diccionarios
        procesos = df.to_dict('records')
        
        return jsonify({
            'mensaje': 'Búsqueda autenticada completada (Buo)',
            'procesos': procesos,
            'total': len(procesos),
            'tipo_busqueda': 'autenticado_buo',
            'usuario': username
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ============================================
# RUTAS API - SEACE OCDS (DATOS ABIERTOS)
# ============================================

@app.route('/api/seace/sync-ocds', methods=['POST'])
def sync_seace_ocds():
    """
    Sincroniza datos de SEACE desde la API oficial OCDS.
    Sin scraping, sin CAPTCHA - datos abiertos oficiales.
    
    Ideal para automatización con n8n o cron jobs.
    """
    if not SEACE_OCDS_AVAILABLE:
        return jsonify({'error': 'Módulo OCDS no disponible'}), 503
    
    try:
        data = request.get_json() or {}
        departamentos = data.get('departamentos', ['ANCASH', 'LIMA'])
        tipos = data.get('tipos_objeto', ['obras', 'consultoria_obras'])
        limite = int(data.get('limite', 500))
        
        scraper = OCDSScraper()
        resultado = scraper.sincronizar_sqlite(
            departamentos=departamentos,
            tipos_objeto=tipos,
            limite=limite
        )
        
        return jsonify(resultado)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/seace/buscar-ocds', methods=['POST'])
def buscar_seace_ocds():
    """
    Busca procesos directamente desde la API OCDS.
    """
    if not SEACE_OCDS_AVAILABLE:
        return jsonify({'error': 'Módulo OCDS no disponible'}), 503
    
    try:
        data = request.get_json() or {}
        departamentos = data.get('departamentos', ['ANCASH', 'LIMA'])
        tipos = data.get('tipos_objeto', ['obras', 'consultoria_obras'])
        limite = int(data.get('limite', 50))
        
        procesos = buscar_con_ocds(departamentos, tipos, limite)
        
        return jsonify({
            'procesos': [p.to_dict() for p in procesos],
            'total': len(procesos),
            'fuente': 'ocds'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# RUTAS API - SEACE EXPORTS & NOTIFICACIONES
# ============================================

# Importar módulo de exportaciones
try:
    from engine.seace_exports import (
        exportar_csv, filtrar_por_monto, filtrar_urgentes,
        generar_mensaje_whatsapp, deduplicar_procesos, generar_resumen_diario,
        MONTO_MINIMO_8_UIT, get_exports_info
    )
    SEACE_EXPORTS_AVAILABLE = True
except ImportError:
    SEACE_EXPORTS_AVAILABLE = False
    print("[WARN] Módulo seace_exports no disponible")

@app.route('/api/seace/export-csv', methods=['POST'])
def export_seace_csv():
    """
    Exporta procesos a CSV con filtros opcionales.
    
    Body:
    {
        "monto_minimo": 42800,  // Por defecto 8 UIT
        "solo_urgentes": false,
        "departamentos": ["ANCASH", "LIMA"]
    }
    """
    if not SEACE_EXPORTS_AVAILABLE:
        return jsonify({'error': 'Módulo de exportación no disponible'}), 503
    
    try:
        from engine.seace_db import SeaceDB
        
        data = request.get_json() or {}
        monto_minimo = float(data.get('monto_minimo', MONTO_MINIMO_8_UIT))
        solo_urgentes = data.get('solo_urgentes', False)
        departamento = data.get('departamento')
        
        # Buscar en base de datos local
        db = SeaceDB()
        procesos = db.buscar(departamento=departamento, limite=500, solo_frescos=False)
        
        # Aplicar filtros
        procesos = deduplicar_procesos(procesos)
        procesos = filtrar_por_monto(procesos, monto_minimo)
        
        if solo_urgentes:
            procesos = filtrar_urgentes(procesos, dias_limite=3)
        
        # Generar CSV
        csv_content = exportar_csv(procesos)
        
        # Retornar como archivo descargable
        from flask import Response
        fecha = datetime.now().strftime('%Y%m%d')
        filename = f"seace_procesos_{fecha}.csv"
        
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/seace/notify', methods=['POST'])
def notify_seace_urgentes():
    """
    Genera mensaje de WhatsApp con procesos urgentes.
    
    Body:
    {
        "monto_minimo": 42800,
        "dias_limite": 3
    }
    
    Retorna mensaje formateado para WhatsApp.
    En producción, integrar con Twilio o WhatsApp Business API.
    """
    if not SEACE_EXPORTS_AVAILABLE:
        return jsonify({'error': 'Módulo de exportación no disponible'}), 503
    
    try:
        from engine.seace_db import SeaceDB
        
        data = request.get_json() or {}
        monto_minimo = float(data.get('monto_minimo', MONTO_MINIMO_8_UIT))
        dias_limite = int(data.get('dias_limite', 3))
        
        # Buscar procesos
        db = SeaceDB()
        procesos = db.buscar(limite=500, solo_frescos=False)
        
        # Filtrar
        procesos = deduplicar_procesos(procesos)
        procesos = filtrar_por_monto(procesos, monto_minimo)
        urgentes = filtrar_urgentes(procesos, dias_limite)
        
        # Generar mensaje WhatsApp
        mensaje = generar_mensaje_whatsapp(urgentes)
        
        # Generar resumen
        resumen = generar_resumen_diario(procesos)
        
        return jsonify({
            'mensaje_whatsapp': mensaje,
            'urgentes_count': len(urgentes),
            'total_filtrados': len(procesos),
            'resumen': resumen,
            'enviar_a': 'Configurar Twilio/WhatsApp Business API en producción'
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/seace/resumen-n8n', methods=['POST'])
def seace_resumen_n8n():
    """
    Endpoint optimizado para n8n.
    Retorna datos estructurados para el workflow automatizado.
    """
    if not SEACE_EXPORTS_AVAILABLE:
        return jsonify({'error': 'Módulo de exportación no disponible'}), 503
    
    try:
        from engine.seace_db import SeaceDB
        
        data = request.get_json() or {}
        monto_minimo = float(data.get('monto_minimo', MONTO_MINIMO_8_UIT))
        
        db = SeaceDB()
        procesos = db.buscar(limite=500, solo_frescos=False)
        
        # Aplicar pipeline completo
        procesos = deduplicar_procesos(procesos)
        procesos_filtrados = filtrar_por_monto(procesos, monto_minimo)
        urgentes = filtrar_urgentes(procesos_filtrados, dias_limite=3)
        
        return jsonify({
            'fecha': datetime.now().isoformat(),
            'monto_minimo_aplicado': monto_minimo,
            'total_original': len(procesos),
            'total_filtrado': len(procesos_filtrados),
            'urgentes_count': len(urgentes),
            'procesos': procesos_filtrados,
            'urgentes': urgentes,
            'mensaje_whatsapp': generar_mensaje_whatsapp(urgentes) if urgentes else None,
            'resumen': generar_resumen_diario(procesos_filtrados)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# RUTAS API - CRON JOBS (REEMPLAZA N8N)
# ============================================

# Importar módulo de cron
try:
    from engine.seace_cron import ejecutar_sincronizacion_diaria
    SEACE_CRON_AVAILABLE = True
except ImportError:
    SEACE_CRON_AVAILABLE = False
    print("[WARN] Módulo seace_cron no disponible")

@app.route('/api/cron/seace-diario', methods=['POST'])
def cron_seace_diario():
    """
    Endpoint para Render Cron Jobs.
    Ejecuta el pipeline completo de sincronización SEACE:
    1. Sincroniza OCDS (Ancash, Lima)
    2. Filtra > 8 UIT (S/ 42,800)
    3. Detecta urgentes (≤3 días)
    4. Envía WhatsApp si hay urgentes
    
    Configurar en Render:
    - Cron expression: 15 13 * * * (8:15 AM Lima)
    - Command: curl -X POST https://tu-app.onrender.com/api/cron/seace-diario
    """
    if not SEACE_CRON_AVAILABLE:
        return jsonify({'error': 'Módulo de cron no disponible'}), 503
    
    try:
        resultado = ejecutar_sincronizacion_diaria()
        return jsonify(resultado)
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

# ============================================
# INICIAR SERVIDOR
# ============================================

if __name__ == '__main__':
    init_engines()
    
    # Iniciar búsqueda automática de SEACE (cada 6 horas)
    iniciar_busqueda_automatica(intervalo_horas=6)
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║     🏛️  AGENTE DE CONTRATACIONES PÚBLICAS - PERÚ  🏛️        ║
║                                                              ║
║  Ley N° 32069 - Ley General de Contrataciones Públicas      ║
║  Reglamento D.S. N° 009-2025-EF (modificado D.S. 001-2026)  ║
║                                                              ║
║  🔍 SEACE Auto-Search: Activo (Ancash, Lima)                ║
║  Servidor: http://localhost:{Config.PORT}                         ║
╚══════════════════════════════════════════════════════════════╝
    """)
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)

