import io
import re

class PDFProcessor:
    def __init__(self):
        self.available_extractors = []
        
        try:
            import fitz  # PyMuPDF
            self.available_extractors.append('pymupdf')
        except ImportError:
            pass
        
        try:
            from PyPDF2 import PdfReader
            self.available_extractors.append('pypdf2')
        except ImportError:
            pass
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text to remove problematic characters"""
        if not text:
            return ""
        
        # Remove null characters and other problematic Unicode characters
        # that can't be stored in PostgreSQL
        text = text.replace('\u0000', '')  # Remove null characters
        text = text.replace('\x00', '')    # Remove null bytes
        
        # Remove other problematic control characters except newlines and tabs
        text = re.sub(r'[\x01-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def extract_text_from_bytes(self, pdf_bytes: bytes) -> str:
        for extractor in self.available_extractors:
            try:
                if extractor == 'pymupdf':
                    raw_text = self._extract_with_pymupdf(pdf_bytes)
                elif extractor == 'pypdf2':
                    raw_text = self._extract_with_pypdf2(pdf_bytes)
                else:
                    continue
                
                # Clean the extracted text
                cleaned_text = self._clean_text(raw_text)
                
                if cleaned_text:  # Return first successful extraction
                    return cleaned_text
                    
            except Exception as e:
                print(f"❌ Text extraction failed with {extractor}: {e}")
                continue
        
        return "Text extraction failed - no readable content found"
    
    def _extract_with_pymupdf(self, pdf_bytes: bytes) -> str:
        import fitz
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ''.join([page.get_text() for page in doc])
        doc.close()
        return text.strip()
    
    def _extract_with_pypdf2(self, pdf_bytes: bytes) -> str:
        from PyPDF2 import PdfReader
        pdf_file = io.BytesIO(pdf_bytes)
        reader = PdfReader(pdf_file)
        text = ''.join([page.extract_text() or '' for page in reader.pages])
        return text.strip()