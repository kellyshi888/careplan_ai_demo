import numpy as np
import faiss
from typing import List, Dict, Any, Optional, Tuple
import json
import os

from ..models.guideline import Guideline


class VectorStore:
    """FAISS-based vector store for clinical guidelines retrieval"""
    
    def __init__(self, dimension: int = 1536, index_type: str = "flat"):
        self.dimension = dimension
        self.index_type = index_type
        self.index = None
        self.guidelines: List[Guideline] = []
        self.id_to_idx: Dict[str, int] = {}
        
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize FAISS index"""
        if self.index_type == "flat":
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
        elif self.index_type == "ivf":
            quantizer = faiss.IndexFlatIP(self.dimension)
            self.index = faiss.IndexIVFFlat(quantizer, self.dimension, 100)
        else:
            raise ValueError(f"Unsupported index type: {self.index_type}")
    
    async def add_guidelines(self, guidelines: List[Guideline]):
        """Add guidelines to the vector store"""
        if not guidelines:
            return
        
        vectors = []
        for guideline in guidelines:
            if guideline.embedding_vector is None:
                raise ValueError(f"Guideline {guideline.id} missing embedding vector")
            
            vectors.append(np.array(guideline.embedding_vector, dtype=np.float32))
            self.id_to_idx[guideline.id] = len(self.guidelines)
            self.guidelines.append(guideline)
        
        # Convert to numpy array and normalize for cosine similarity
        vectors_array = np.vstack(vectors)
        faiss.normalize_L2(vectors_array)
        
        # Train index if needed (for IVF)
        if self.index_type == "ivf" and not self.index.is_trained:
            self.index.train(vectors_array)
        
        # Add vectors to index
        self.index.add(vectors_array)
    
    async def search(
        self, 
        query_vector: List[float], 
        k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[Guideline, float]]:
        """Search for similar guidelines"""
        if self.index.ntotal == 0:
            return []
        
        # Normalize query vector
        query_array = np.array([query_vector], dtype=np.float32)
        faiss.normalize_L2(query_array)
        
        # Search
        scores, indices = self.index.search(query_array, min(k, self.index.ntotal))
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0:  # Valid index
                guideline = self.guidelines[idx]
                
                # Apply filters if provided
                if filters and not self._matches_filters(guideline, filters):
                    continue
                    
                results.append((guideline, float(score)))
        
        return results
    
    async def search_by_condition(
        self, 
        query_vector: List[float], 
        condition_codes: List[str],
        k: int = 10
    ) -> List[Tuple[Guideline, float]]:
        """Search guidelines filtered by condition codes"""
        filters = {"condition_codes": condition_codes}
        return await self.search(query_vector, k, filters)
    
    async def search_by_specialty(
        self, 
        query_vector: List[float], 
        specialty: str,
        k: int = 10
    ) -> List[Tuple[Guideline, float]]:
        """Search guidelines filtered by medical specialty"""
        filters = {"specialty": specialty}
        return await self.search(query_vector, k, filters)
    
    def _matches_filters(self, guideline: Guideline, filters: Dict[str, Any]) -> bool:
        """Check if guideline matches the given filters"""
        metadata = guideline.metadata
        
        # Check condition codes
        if "condition_codes" in filters:
            filter_codes = set(filters["condition_codes"])
            guideline_codes = set(metadata.get("condition_codes", []))
            if not filter_codes.intersection(guideline_codes):
                return False
        
        # Check specialty
        if "specialty" in filters:
            if metadata.get("specialty") != filters["specialty"]:
                return False
        
        # Check patient population
        if "patient_population" in filters:
            if metadata.get("patient_population") != filters["patient_population"]:
                return False
        
        return True
    
    async def save_index(self, filepath: str):
        """Save the FAISS index to disk"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        faiss.write_index(self.index, f"{filepath}.faiss")
        
        # Save guidelines metadata
        guidelines_data = [
            {
                "id": g.id,
                "content": g.content,
                "metadata": g.metadata
            }
            for g in self.guidelines
        ]
        
        with open(f"{filepath}.json", 'w') as f:
            json.dump({
                "guidelines": guidelines_data,
                "id_to_idx": self.id_to_idx,
                "dimension": self.dimension,
                "index_type": self.index_type
            }, f, indent=2)
    
    async def load_index(self, filepath: str):
        """Load the FAISS index from disk"""
        # Load FAISS index
        self.index = faiss.read_index(f"{filepath}.faiss")
        
        # Load guidelines metadata
        with open(f"{filepath}.json", 'r') as f:
            data = json.load(f)
        
        self.guidelines = [
            Guideline(
                id=g["id"],
                content=g["content"],
                metadata=g["metadata"]
            )
            for g in data["guidelines"]
        ]
        
        self.id_to_idx = data["id_to_idx"]
        self.dimension = data["dimension"]
        self.index_type = data["index_type"]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        return {
            "total_guidelines": len(self.guidelines),
            "index_size": self.index.ntotal if self.index else 0,
            "dimension": self.dimension,
            "index_type": self.index_type
        }