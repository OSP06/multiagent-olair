# utils/retriever.py
import pickle
import os
import numpy as np
from typing import List, Dict, Any, Optional
from sklearn.metrics.pairwise import cosine_similarity

class LeaseVectorStore:
    """
    Enhanced vector store with persistent save/load functionality.
    """
    
    def __init__(self):
        """Initialize empty vector store."""
        self.embeddings = []
        self.texts = []
        self.metadata = {}
        
    def add_embeddings(self, embeddings: List[List[float]], texts: List[str], metadata: List[Dict] = None):
        """
        Add embeddings and corresponding texts to the store.
        
        Args:
            embeddings: List of embedding vectors
            texts: List of text strings
            metadata: Optional metadata for each text
        """
        if len(embeddings) != len(texts):
            raise ValueError("Number of embeddings must match number of texts")
        
        self.embeddings.extend(embeddings)
        self.texts.extend(texts)
        
        if metadata:
            if len(metadata) != len(texts):
                raise ValueError("Number of metadata entries must match number of texts")
            for i, meta in enumerate(metadata):
                self.metadata[len(self.texts) - len(texts) + i] = meta
    
    def search(self, query_embedding: List[float], k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for most similar texts to the query embedding.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            
        Returns:
            List of dictionaries with 'text', 'score', and optional 'metadata'
        """
        if not self.embeddings:
            return []
        
        # Calculate cosine similarities
        query_array = np.array(query_embedding).reshape(1, -1)
        embeddings_array = np.array(self.embeddings)
        
        similarities = cosine_similarity(query_array, embeddings_array)[0]
        
        # Get top k indices
        top_indices = np.argsort(similarities)[::-1][:k]
        
        results = []
        for idx in top_indices:
            result = {
                "text": self.texts[idx],
                "score": float(similarities[idx])
            }
            
            # Add metadata if available
            if idx in self.metadata:
                result["metadata"] = self.metadata[idx]
            
            results.append(result)
        
        return results
    
    def save(self, path: str = "data/lease_vector_store.pkl"):
        """
        Save the vector store to disk using pickle.
        
        Args:
            path: Path to save the vector store
        """
        # Ensure directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        store_data = {
            "embeddings": self.embeddings,
            "texts": self.texts,
            "metadata": self.metadata,
            "version": "1.0"
        }
        
        try:
            with open(path, "wb") as f:
                pickle.dump(store_data, f)
            print(f"✅ Vector store saved to: {path}")
        except Exception as e:
            raise Exception(f"Failed to save vector store: {e}")
    
    def load(self, path: str = "data/lease_vector_store.pkl"):
        """
        Load the vector store from disk.
        
        Args:
            path: Path to load the vector store from
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            Exception: For other loading errors
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Vector store file not found: {path}")
        
        try:
            with open(path, "rb") as f:
                store_data = pickle.load(f)
            
            self.embeddings = store_data.get("embeddings", [])
            self.texts = store_data.get("texts", [])
            self.metadata = store_data.get("metadata", {})
            
            print(f"✅ Vector store loaded from: {path}")
            print(f"📊 Loaded {len(self.texts)} texts with {len(self.embeddings)} embeddings")
            
        except Exception as e:
            raise Exception(f"Failed to load vector store: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary with store statistics
        """
        if not self.embeddings:
            return {"total_texts": 0, "embedding_dimension": 0, "has_metadata": False}
        
        return {
            "total_texts": len(self.texts),
            "embedding_dimension": len(self.embeddings[0]) if self.embeddings else 0,
            "has_metadata": len(self.metadata) > 0,
            "metadata_coverage": len(self.metadata) / len(self.texts) if self.texts else 0
        }
    
    def clear(self):
        """Clear all data from the vector store."""
        self.embeddings = []
        self.texts = []
        self.metadata = {}
    
    def remove_by_index(self, indices: List[int]):
        """
        Remove texts and embeddings by their indices.
        
        Args:
            indices: List of indices to remove
        """
        # Sort indices in descending order to avoid index shifting issues
        indices = sorted(set(indices), reverse=True)
        
        for idx in indices:
            if 0 <= idx < len(self.texts):
                del self.texts[idx]
                del self.embeddings[idx]
                
                # Remove metadata if it exists
                if idx in self.metadata:
                    del self.metadata[idx]
                
                # Update metadata indices
                new_metadata = {}
                for meta_idx, meta_data in self.metadata.items():
                    if meta_idx > idx:
                        new_metadata[meta_idx - 1] = meta_data
                    elif meta_idx < idx:
                        new_metadata[meta_idx] = meta_data
                
                self.metadata = new_metadata
    
    def search_with_filter(self, query_embedding: List[float], k: int = 5, 
                          filter_func: callable = None) -> List[Dict[str, Any]]:
        """
        Search with optional filtering function.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            filter_func: Optional function to filter results (takes text and metadata)
            
        Returns:
            List of filtered search results
        """
        if not self.embeddings:
            return []
        
        # Get all results first
        all_results = self.search(query_embedding, k=len(self.texts))
        
        # Apply filter if provided
        if filter_func:
            filtered_results = []
            for result in all_results:
                metadata = result.get("metadata", {})
                if filter_func(result["text"], metadata):
                    filtered_results.append(result)
                    if len(filtered_results) >= k:
                        break
            return filtered_results
        
        return all_results[:k]
    
    def add_single_text(self, embedding: List[float], text: str, metadata: Dict = None):
        """
        Add a single text and embedding to the store.
        
        Args:
            embedding: Embedding vector
            text: Text string
            metadata: Optional metadata
        """
        self.embeddings.append(embedding)
        self.texts.append(text)
        
        if metadata:
            self.metadata[len(self.texts) - 1] = metadata
    
    def update_text(self, index: int, new_text: str, new_embedding: List[float] = None, 
                    new_metadata: Dict = None):
        """
        Update a text at a specific index.
        
        Args:
            index: Index of the text to update
            new_text: New text content
            new_embedding: New embedding (optional)
            new_metadata: New metadata (optional)
        """
        if 0 <= index < len(self.texts):
            self.texts[index] = new_text
            
            if new_embedding:
                self.embeddings[index] = new_embedding
            
            if new_metadata:
                self.metadata[index] = new_metadata
        else:
            raise IndexError(f"Index {index} out of range")
    
    def find_duplicates(self, similarity_threshold: float = 0.95) -> List[List[int]]:
        """
        Find duplicate or very similar texts based on embedding similarity.
        
        Args:
            similarity_threshold: Minimum similarity to consider as duplicate
            
        Returns:
            List of lists, where each inner list contains indices of similar texts
        """
        if len(self.embeddings) < 2:
            return []
        
        embeddings_array = np.array(self.embeddings)
        similarity_matrix = cosine_similarity(embeddings_array)
        
        duplicates = []
        processed = set()
        
        for i in range(len(self.embeddings)):
            if i in processed:
                continue
                
            similar_indices = []
            for j in range(i + 1, len(self.embeddings)):
                if j not in processed and similarity_matrix[i][j] >= similarity_threshold:
                    if not similar_indices:
                        similar_indices.append(i)
                    similar_indices.append(j)
                    processed.add(j)
            
            if similar_indices:
                duplicates.append(similar_indices)
                processed.update(similar_indices)
        
        return duplicates