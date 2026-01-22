/**
 * Chat Widget - Agente de Contrataciones Públicas
 * Lógica del chat y comunicación con el backend
 */

// Estado global
const API_URL = window.location.origin;
let isLoading = false;
let sessionId = generateSessionId();

/**
 * Genera un ID de sesión único
 */
function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

/**
 * Toggle del chat (minimizar/expandir)
 */
function toggleChat() {
    const widget = document.getElementById('chatWidget');
    const toggleIcon = document.querySelector('.toggle-icon');

    widget.classList.toggle('minimized');
    toggleIcon.textContent = widget.classList.contains('minimized') ? '+' : '−';
}

/**
 * Envía un mensaje al chat
 */
async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();

    if (!message || isLoading) return;

    // Agregar mensaje del usuario
    addMessage(message, 'user');
    input.value = '';

    // Mostrar indicador de carga
    showTypingIndicator();
    isLoading = true;

    try {
        const response = await fetch(`${API_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId
            })
        });

        const data = await response.json();

        // Remover indicador de carga
        hideTypingIndicator();

        if (data.error) {
            addMessage('❌ Error: ' + data.error, 'bot');
        } else {
            addMessage(data.response, 'bot');
        }

    } catch (error) {
        hideTypingIndicator();
        addMessage('❌ Error de conexión. Verifica que el servidor esté activo.', 'bot');
        console.error('Error:', error);
    } finally {
        isLoading = false;
    }
}

/**
 * Agrega un mensaje al chat
 */
function addMessage(content, type) {
    const container = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;

    const avatar = type === 'bot' ? '🏛️' : '👤';

    // Formatear contenido (markdown básico)
    const formattedContent = formatMessage(content);

    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">${formattedContent}</div>
    `;

    container.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Formatea el mensaje con markdown básico
 */
function formatMessage(text) {
    return text
        // Headers
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        // Line breaks
        .replace(/\n/g, '<br>')
        // Lists
        .replace(/^• (.+)$/gm, '<li>$1</li>')
        .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
        // Paragraphs
        .split('<br><br>').map(p => `<p>${p}</p>`).join('');
}

/**
 * Muestra indicador de escritura
 */
function showTypingIndicator() {
    const container = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message';
    typingDiv.id = 'typingIndicator';

    typingDiv.innerHTML = `
        <div class="message-avatar">🏛️</div>
        <div class="message-content">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;

    container.appendChild(typingDiv);
    scrollToBottom();
}

/**
 * Oculta indicador de escritura
 */
function hideTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

/**
 * Scroll al final del chat
 */
function scrollToBottom() {
    const container = document.getElementById('chatMessages');
    container.scrollTop = container.scrollHeight;
}

/**
 * Maneja el evento de tecla Enter
 */
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

/**
 * Hace una pregunta predefinida
 */
function askQuestion(question) {
    const input = document.getElementById('chatInput');
    input.value = question;

    // Asegurar que el chat esté visible
    const widget = document.getElementById('chatWidget');
    if (widget.classList.contains('minimized')) {
        toggleChat();
    }

    sendMessage();
}

/**
 * Abre el modal de calculadora
 */
function openCalculator() {
    const modal = document.getElementById('calculatorModal');
    modal.classList.add('active');
}

/**
 * Cierra el modal de calculadora
 */
function closeCalculator() {
    const modal = document.getElementById('calculatorModal');
    modal.classList.remove('active');

    // Limpiar resultado
    const result = document.getElementById('calcResult');
    result.classList.remove('active');
    result.innerHTML = '';
}

/**
 * Calcula el procedimiento según monto y tipo
 */
async function calculateProcedure() {
    const monto = parseFloat(document.getElementById('montoInput').value);
    const tipo = document.getElementById('tipoSelect').value;
    const result = document.getElementById('calcResult');

    if (!monto || monto <= 0) {
        result.innerHTML = '<p style="color: #ef4444;">⚠️ Ingresa un monto válido</p>';
        result.classList.add('active');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/calculate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ monto, tipo })
        });

        const data = await response.json();

        if (data.error) {
            result.innerHTML = `<p style="color: #ef4444;">❌ ${data.error}</p>`;
        } else {
            result.innerHTML = `
                <h3>${data.procedimiento}</h3>
                <p><strong>Monto:</strong> S/ ${monto.toLocaleString('es-PE', { minimumFractionDigits: 2 })}</p>
                <p><strong>Tipo:</strong> ${data.tipo}</p>
                <p>${data.descripcion}</p>
                <p><strong>Base Legal:</strong> ${data.base_legal}</p>
                ${data.rango ? `<p><strong>Rango:</strong> ${data.rango}</p>` : ''}
                ${data.nota ? `<p style="color: #fbbf24;">⚠️ ${data.nota}</p>` : ''}
            `;
        }

        result.classList.add('active');

    } catch (error) {
        result.innerHTML = '<p style="color: #ef4444;">❌ Error de conexión</p>';
        result.classList.add('active');
        console.error('Error:', error);
    }
}

// Cerrar modal al hacer clic fuera
document.getElementById('calculatorModal').addEventListener('click', function (e) {
    if (e.target === this) {
        closeCalculator();
    }
});

// Inicialización
document.addEventListener('DOMContentLoaded', function () {
    console.log('🏛️ Agente de Contrataciones Públicas - Iniciado');

    // Focus en el input
    document.getElementById('chatInput').focus();

    // Setup del upload zone
    const uploadZone = document.getElementById('uploadZone');
    if (uploadZone) {
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('dragging');
        });
        uploadZone.addEventListener('dragleave', () => {
            uploadZone.classList.remove('dragging');
        });
        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragging');
            if (e.dataTransfer.files.length) {
                handleFileSelect({ target: { files: e.dataTransfer.files } });
            }
        });
    }
});

// =====================================================
// FUNCIONES PARA UPLOAD DE PDF
// =====================================================

let selectedFile = null;

/**
 * Abre el modal de upload de PDF
 */
function openPdfUpload() {
    const modal = document.getElementById('pdfUploadModal');
    modal.classList.add('active');
}

/**
 * Cierra el modal de upload de PDF
 */
function closePdfUpload() {
    const modal = document.getElementById('pdfUploadModal');
    modal.classList.remove('active');

    // Limpiar estado
    selectedFile = null;
    document.getElementById('uploadStatus').innerHTML = '';
    document.getElementById('uploadStatus').className = 'upload-status';
    document.getElementById('analysisResult').innerHTML = '';
    document.getElementById('analysisResult').classList.remove('active');
    document.getElementById('analyzeBtn').disabled = true;
    document.getElementById('pdfInput').value = '';
}

/**
 * Maneja la selección de archivo
 */
function handleFileSelect(event) {
    const file = event.target.files[0];
    const statusDiv = document.getElementById('uploadStatus');
    const analyzeBtn = document.getElementById('analyzeBtn');

    if (!file) return;

    if (file.type !== 'application/pdf') {
        statusDiv.innerHTML = '❌ Solo se permiten archivos PDF';
        statusDiv.className = 'upload-status error';
        analyzeBtn.disabled = true;
        return;
    }

    if (file.size > 16 * 1024 * 1024) {
        statusDiv.innerHTML = '❌ El archivo es muy grande (máximo 16MB)';
        statusDiv.className = 'upload-status error';
        analyzeBtn.disabled = true;
        return;
    }

    selectedFile = file;
    statusDiv.innerHTML = `✅ Archivo seleccionado: <strong>${file.name}</strong> (${(file.size / 1024).toFixed(1)} KB)`;
    statusDiv.className = 'upload-status success';
    analyzeBtn.disabled = false;
}

/**
 * Sube y analiza el PDF
 */
async function uploadAndAnalyze() {
    if (!selectedFile) return;

    const analysisType = document.querySelector('input[name="analysisType"]:checked').value;
    const resultDiv = document.getElementById('analysisResult');
    const analyzeBtn = document.getElementById('analyzeBtn');

    analyzeBtn.disabled = true;
    analyzeBtn.textContent = '⏳ Analizando...';

    const formData = new FormData();
    formData.append('file', selectedFile);

    let endpoint = '/api/pdf/upload';
    if (analysisType === 'evaluacion') {
        endpoint = '/api/pdf/verificar-evaluacion';
    } else if (analysisType === 'chat') {
        formData.append('pregunta', '¿Qué vicios tiene este documento? Dame un resumen.');
        endpoint = '/api/pdf/chat';
    }

    try {
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.error) {
            resultDiv.innerHTML = `<p style="color: #ef4444;">❌ ${data.error}</p>`;
        } else {
            let html = '';

            if (data.respuesta_chat) {
                html = `<div>${formatMessage(data.respuesta_chat)}</div>`;
            } else if (data.respuesta) {
                html = `<div>${formatMessage(data.respuesta)}</div>`;
            } else if (data.vicios_detectados) {
                html = `<h3>⚠️ Vicios Detectados</h3>`;
                data.vicios_detectados.forEach(v => {
                    html += `<p><strong>${v.tipo}</strong>: ${v.descripcion}</p>`;
                });
            } else if (data.resultado && data.resultado.analisis_ia) {
                const analisis = data.resultado.analisis_ia;
                html = `<h3>📋 Análisis del Documento</h3>`;
                if (analisis.numero_proceso) {
                    html += `<p><strong>Proceso:</strong> ${analisis.numero_proceso}</p>`;
                }
                if (analisis.valor_referencial) {
                    html += `<p><strong>Valor Referencial:</strong> S/ ${analisis.valor_referencial.toLocaleString()}</p>`;
                }
                if (analisis.posibles_vicios && analisis.posibles_vicios.length > 0) {
                    html += `<h4>⚠️ Posibles Vicios:</h4>`;
                    analisis.posibles_vicios.forEach(v => {
                        html += `<p>• <strong>[${v.severidad}]</strong> ${v.descripcion}</p>`;
                    });
                }
            } else {
                html = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
            }

            resultDiv.innerHTML = html;
        }

        resultDiv.classList.add('active');

    } catch (error) {
        resultDiv.innerHTML = `<p style="color: #ef4444;">❌ Error de conexión: ${error.message}</p>`;
        resultDiv.classList.add('active');
        console.error('Error:', error);
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = '🔍 Analizar';
    }
}

// Cerrar modal de PDF al hacer clic fuera
document.getElementById('pdfUploadModal')?.addEventListener('click', function (e) {
    if (e.target === this) {
        closePdfUpload();
    }
});
