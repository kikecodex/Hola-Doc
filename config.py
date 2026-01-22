"""
Configuración del Agente de Contrataciones Públicas
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración principal de la aplicación"""
    
    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
    
    # Alternativa Gemini (para migración futura)
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
    USE_GEMINI = os.getenv('USE_GEMINI', 'false').lower() == 'true'
    
    # Servidor
    DEBUG = os.getenv('DEBUG', 'true').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))
    HOST = os.getenv('HOST', '0.0.0.0')
    
    # Rutas
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    KNOWLEDGE_DIR = os.path.join(BASE_DIR, 'knowledge')
    CHROMA_DIR = os.path.join(BASE_DIR, 'chroma_db')
    
    # RAG Settings
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    TOP_K_RESULTS = 15
    
    @classmethod
    def validate(cls):
        """Valida que las configuraciones necesarias estén presentes"""
        if not cls.USE_GEMINI and not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY es requerida. Configúrala en el archivo .env")
        if cls.USE_GEMINI and not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY es requerida cuando USE_GEMINI=true")
        return True
