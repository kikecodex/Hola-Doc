import os
import re
from typing import List
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
except ImportError:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from config import Config

class RagEngine:
    """Motor RAG para búsqueda semántica en documentos"""
    
    def __init__(self):
        # Asegurar que existe el directorio de vectores
        os.makedirs(Config.CHROMA_DIR, exist_ok=True)
        
        # Configurar Embeddings de Google (Gemini)
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=Config.GEMINI_API_KEY
        )
        
        # Inicializar ChromaDB (Persistente)
        self.vector_store = Chroma(
            persist_directory=Config.CHROMA_DIR,
            embedding_function=self.embeddings,
            collection_name="contrataciones_publicas"
        )
        
    def ingest_documents(self):
        """Carga, procesa e indexa documentos desde el directorio knowledge"""
        if not os.path.exists(Config.KNOWLEDGE_DIR):
            os.makedirs(Config.KNOWLEDGE_DIR)
            print(f"📁 Directorio creado: {Config.KNOWLEDGE_DIR}")
            return "Directorio de conocimiento estaba vacío"

        print(f"📥 Cargando documentos desde {Config.KNOWLEDGE_DIR}...")
        
        # Cargar PDFs
        loader = DirectoryLoader(
            Config.KNOWLEDGE_DIR,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader
        )
        documents = loader.load()
        
        if not documents:
            print("⚠️ No se encontraron documentos PDF")
            return "No se encontraron documentos"
            
        print(f"📄 Se cargaron {len(documents)} páginas")
        
        # Dividir en chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = text_splitter.split_documents(documents)
        print(f"🧩 Documentos divididos en {len(chunks)} fragmentos")
        
        # Guardar en ChromaDB
        self.vector_store.add_documents(chunks)
        self.vector_store.persist()
        print("💾 Base de datos vectorial actualizada y guardada")
        
        return f"Ingestión completada: {len(chunks)} fragmentos indexados"

    def search(self, query: str, k: int = 3) -> List[str]:
        """Busca fragmentos relevantes para la consulta"""
        try:
            # 🚀 STRATEGY: ARTIFICIAL BOOSTING FOR SPECIFIC ARTICLES
            # Detected intent: "Artículo X" -> Boost search to find header
            article_match = re.search(r'(?:art\.?|art[ií]culo)\s*(\d+)', query.lower())
            
            # If detecting specific article, widen search to ensuring finding it
            search_k = k
            target_article = None
            
            if article_match:
                target_article = article_match.group(1)
                search_k = 500  # Massive retrieval to guarantee finding the specific article chunk
                print(f"🚀 Detected search for Article {target_article}. Boosting candidates to {search_k}...")
            
            # Perform raw vector search
            results = self.vector_store.similarity_search(query, k=search_k)
            
            if not target_article:
                # Normal behavior
                return [doc.page_content for doc in results]
            
            # 🔍 RE-RANKING LOGIC
            # Prioritize chunks that act as the HEADER of the article (e.g., "Artículo 100")
            
            priority_chunks = []
            secondary_chunks = []
            other_chunks = []
            
            for doc in results:
                content = doc.page_content
                # Check for "Artículo 100." or "Art. 100" appearing as a header pattern
                # We look for the number followed by dot or space, to avoid "100" matching "1000"
                if re.search(rf'(?:art\.?|art[ií]culo)\s*{target_article}(?:[\.\s]|$)', content.lower()):
                    priority_chunks.append(content)
                elif target_article in content:
                    secondary_chunks.append(content)
                else:
                    other_chunks.append(content)
            
            # Reassemble prioritized list
            final_results = priority_chunks + secondary_chunks + other_chunks
            
            # Limit back to original K (or slightly more to ensure context)
            final_k = max(k, 5) 
            print(f"✅ Re-ranked: {len(priority_chunks)} priority matches found.")
            
            return final_results[:final_k]
            
        except Exception as e:
            print(f"❌ Error en búsqueda RAG: {e}")
            return []
