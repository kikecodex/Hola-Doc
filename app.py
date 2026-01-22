"""
Agente de Contrataciones Públicas del Perú
API REST con Flask - Versión 4.0 con procesamiento de PDFs
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
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

def allowed_file(filename):
    """Verifica si el archivo tiene extensión permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_engines():
    """Inicializa los motores del agente"""
    global conversation_engine
    try:
        Config.validate()
        conversation_engine = ConversationEngine()
        print("✅ Motores inicializados correctamente")
    except Exception as e:
        print(f"⚠️ Error inicializando motores: {e}")
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
            'jprd', 'arbitraje'
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
    """Genera documento formal de observación"""
    try:
        data = request.get_json()
        observacion = data.get('observacion', {})
        datos_proceso = data.get('datos_proceso', {})
        datos_observante = data.get('datos_observante', {})
        
        documento = observaciones_gen.generar_documento_observacion(
            observacion, datos_proceso, datos_observante
        )
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
# INICIAR SERVIDOR
# ============================================

if __name__ == '__main__':
    init_engines()
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║     🏛️  AGENTE DE CONTRATACIONES PÚBLICAS - PERÚ  🏛️        ║
║                                                              ║
║  Ley N° 32069 - Ley General de Contrataciones Públicas      ║
║  Reglamento D.S. N° 009-2025-EF (modificado D.S. 001-2026)  ║
║                                                              ║
║  Servidor: http://localhost:{Config.PORT}                         ║
╚══════════════════════════════════════════════════════════════╝
    """)
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
