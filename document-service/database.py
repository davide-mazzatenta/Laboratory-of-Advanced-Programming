import base64
from typing import List, Optional, Dict, Any
import numpy as np
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False


def cosine_similarity(v1, v2):
            """Calcola la similarità del coseno tra due vettori."""
            dot_product = np.dot(v1, v2)
            norm_v1 = np.linalg.norm(v1)
            norm_v2 = np.linalg.norm(v2)
            if norm_v1 == 0 or norm_v2 == 0:
                return 0
            return dot_product / (norm_v1 * norm_v2)


class DatabaseManager:
    def __init__(self):
        self.supabase: Optional[Client] = None
        self.available = False
        self._initialize_client()

    def _initialize_client(self):
        if not SUPABASE_AVAILABLE:
            print("❌ Supabase library not available")
            return

        supabase_url = "https://sjfdkgzmjaasjtavuhfu.supabase.co"
        supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNqZmRrZ3ptamFhc2p0YXZ1aGZ1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDE5NDUwNTIsImV4cCI6MjA1NzUyMTA1Mn0.dWBqYF31Ot73oXqf8v2KaMj37Tkzb3dd7Szq1WviDPA"

        print(f"🔗 Connecting to Supabase: {supabase_url[:30]}...")

        try:
            self.supabase = create_client(supabase_url, supabase_key)
            self.available = True
            print("✅ Supabase connected successfully")
        except Exception as e:
            print(f"❌ Supabase error: {e}")
            self.available = False

    def list_user_projects(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all projects for a user (derived from documents)"""
        if not self.available:
            return []

        try:
            # Get distinct project_ids for the user with document counts
            result = self.supabase.table('project_documents').select(
                'project_id'
            ).eq('user_id', user_id).execute()

            if not result.data:
                return []

            # Count documents per project
            project_counts = {}
            for doc in result.data:
                project_id = doc['project_id']
                project_counts[project_id] = project_counts.get(
                    project_id, 0) + 1

            # Return list of project info
            projects = [
                {'project_id': project_id, 'document_count': count}
                for project_id, count in project_counts.items()
            ]

            return projects
        except Exception as e:
            print(f"List projects error: {e}")
            return []

    def store_document(self, document_id: str, user_id: str, project_id: str,
                       doc_id: str, title: str, file_data: bytes, text_content: str) -> bool:
        if not self.available:
            return False

        try:
            # Clean text content to remove problematic characters
            if text_content:
                # Remove null characters and other problematic Unicode characters
                text_content = text_content.replace('\u0000', '').replace('\x00', '')
                # Remove other problematic control characters except newlines and tabs
                import re
                text_content = re.sub(r'[\x01-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text_content)
                text_content = text_content.strip()
            
            # Convert bytes to base64 for JSON storage
            file_data_b64 = base64.b64encode(file_data).decode('utf-8')

            # Store binary PDF data
            self.supabase.table('pdf_storage').insert({
                'id': document_id,
                'user_id': user_id,
                'project_id': project_id,
                'doc_id': doc_id,
                'file_data': file_data_b64,
                'file_size': len(file_data),
                'content_type': 'application/pdf'
            }).execute()

            # Store document metadata and text content
            self.supabase.table('project_documents').insert({
                'id': document_id,
                'user_id': user_id,
                'project_id': project_id,
                'doc_id': doc_id,
                'title': title,
                'content': text_content
            }).execute()

            print(f"✅ Document {document_id} stored successfully")
            return True
        except Exception as e:
            print(f"❌ Store error: {e}")
            return False

    def get_document(self, document_id: str) -> Optional[bytes]:
        if not self.available:
            return None

        try:
            result = self.supabase.table('pdf_storage').select(
                'file_data').eq('id', document_id).execute()
            if result.data:
                # Decode base64 back to bytes
                file_data_b64 = result.data[0]['file_data']
                return base64.b64decode(file_data_b64)
            return None
        except Exception as e:
            print(f"❌ Get document error: {e}")
            return None

    def get_document_text(self, document_id: str) -> Optional[str]:
        if not self.available:
            return None

        try:
            result = self.supabase.table('project_documents').select(
                'content').eq('id', document_id).execute()
            if result.data:
                return result.data[0]['content']
            return None
        except Exception as e:
            print(f"Get text error: {e}")
            return None

    def get_all_chunks(self, user_id: str, project_id: str, doc_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all chunks for a document (useful for full document generation)"""
        if not self.available:
            return []
            
        try:
            query = self.supabase.table('document_chunks').select(
                'chunk_index, chunk_text'
            ).eq('user_id', user_id).eq('project_id', project_id).eq('doc_id', doc_id).order('chunk_index', desc=False)
            
            if limit:
                query = query.limit(limit)
                
            result = query.execute()
            
            chunks = []
            for chunk in result.data:
                chunks.append({
                    "chunk_index": chunk['chunk_index'],
                    "text": chunk['chunk_text']
                })
            
            return chunks
            
        except Exception as e:
            print(f"Get all chunks error: {e}")
            return []

    def list_project_documents(self, user_id: str, project_id: str) -> List[Dict[str, Any]]:
        if not self.available:
            return []

        try:
            result = self.supabase.table('project_documents').select(
                'doc_id, title, content'
            ).eq('user_id', user_id).eq('project_id', project_id).execute()

            return [
                {
                    'doc_id': doc['doc_id'],
                    'title': doc['title'],
                    'content': doc['content']
                } for doc in result.data
            ]
        except Exception as e:
            print(f"List documents error: {e}")
            return []

    # New methods for chunk management
    def check_if_chunked(self, document_id: str) -> bool:
        """Checks if a document has been chunked and stored in the database."""
        if not self.available:
            return False
        try:
            result = self.supabase.table('document_chunks').select(
                'id'
            ).eq('id', document_id).limit(1).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Check chunked status error: {e}")
            return False

    def store_chunks(self, chunks_data: List[Dict[str, Any]]) -> bool:
        """Stores a list of document chunks in the database."""
        if not self.available:
            return False
        try:
            # We need to explicitly convert embeddings to list of floats for Supabase
            chunks_to_insert = []
            for chunk in chunks_data:
                # Clean chunk text to remove problematic characters
                chunk_text = chunk['chunk_text']
                if chunk_text:
                    # Remove null characters and other problematic Unicode characters
                    chunk_text = chunk_text.replace('\u0000', '').replace('\x00', '')
                    # Remove other problematic control characters except newlines and tabs
                    import re
                    chunk_text = re.sub(r'[\x01-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', chunk_text)
                    chunk_text = chunk_text.strip()
                
                chunks_to_insert.append({
                    'id': chunk['id'],
                    'user_id': chunk['user_id'],
                    'project_id': chunk['project_id'],
                    'doc_id': chunk['doc_id'],
                    'chunk_index': chunk['chunk_index'],
                    'chunk_text': chunk_text,
                    'embedding': chunk['embedding'],
                    'embedding_size': len(chunk['embedding'])
                })

            self.supabase.table('document_chunks').insert(
                chunks_to_insert).execute()
            print(f"✅ Stored {len(chunks_to_insert)} chunks successfully.")
            return True
        except Exception as e:
            print(f"❌ Store chunks error: {e}")
            return False
    

    def get_best_chunks(self, user_id: str, project_id: str, doc_id: str, query_embedding: List[float], limit: int) -> List[Dict[str, Any]]:
        """Retrieves the best chunks by calculating cosine similarity locally."""
        if not self.available:
            return []
        try:
            # 1. Recupera TUTTI i chunk per il documento
            result = self.supabase.from_('document_chunks').select('*').eq('user_id', user_id).eq('project_id', project_id).eq('doc_id', doc_id).execute()
            
            # 2. Prepara una lista per i chunk con i loro punteggi
            chunks_with_scores = []
            
            # 3. Itera su ogni chunk per calcolare la similarità
            for chunk in result.data:
                chunk_embedding = np.array(chunk['embedding'])  # Converte la lista JSON in un array NumPy
                score = cosine_similarity(np.array(query_embedding), chunk_embedding)
                chunk['score'] = score  # Aggiungi il punteggio al dizionario del chunk
                chunks_with_scores.append(chunk)

            # 4. Ordina i chunk in base al punteggio di similarità in ordine decrescente
            chunks_with_scores.sort(key=lambda x: x['score'], reverse=True)

            # 5. Rimuovi il campo 'embedding' da ogni chunk prima di restituirli
            for chunk in chunks_with_scores:
                if 'embedding' in chunk:
                    del chunk['embedding']

            # 6. Restituisci i chunk migliori in base al limite
            return chunks_with_scores[:limit]
        
        except Exception as e:
            print(f"Get best chunks error: {e}")
            return []
        



        