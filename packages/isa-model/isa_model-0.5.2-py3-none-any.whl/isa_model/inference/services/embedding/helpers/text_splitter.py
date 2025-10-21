from typing import Dict, List, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from uuid import uuid4

class TextChunkHelper:
    """Text splitting and chunking helper"""
    
    def __init__(self, 
                 chunk_size: int = 512,
                 chunk_overlap: int = 50,
                 min_chunk_size: int = 50):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", ", ", " "]
        )
        self.min_chunk_size = min_chunk_size

    def create_chunks(self, text: str, metadata: Optional[Dict] = None) -> List[Dict]:
        """Create text chunks with metadata"""
        if not text or not isinstance(text, str):
            raise ValueError("Text must be a non-empty string")
            
        chunks = self.text_splitter.split_text(text)
        valid_chunks = [
            chunk for chunk in chunks 
            if len(chunk) >= self.min_chunk_size
        ]
        
        results = []
        for i, chunk in enumerate(valid_chunks):
            chunk_data = {
                "chunk_id": f"chunk_{uuid4().hex[:8]}",
                "content": chunk,
                "token_count": len(chunk),
                "metadata": {
                    **(metadata or {}),
                    "position": i,
                    "start_idx": text.find(chunk),
                    "end_idx": text.find(chunk) + len(chunk)
                }
            }
            results.append(chunk_data)
            
        return results 