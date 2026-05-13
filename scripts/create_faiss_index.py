#!/usr/bin/env python3
"""
Script to create a FAISS index from the sample metadata.
Run this to generate the actual index.faiss file.
"""

import json
import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

def create_sample_index():
    """Create a sample FAISS index with sample data."""
    
    # Paths
    indices_dir = "/home/maxbogus/Repositories/cogniforge/data/indices"
    metadata_path = os.path.join(indices_dir, "metadata.json")
    
    # Load metadata
    with open(metadata_path, "r") as f:
        metadata = json.load(f)
    
    chunks = metadata["chunks"]
    embedding_dim = metadata.get("embedding_dim", 384)
    
    # Load embedding model
    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Generate embeddings
    print(f"Generating embeddings for {len(chunks)} chunks...")
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)
    embeddings = embeddings.astype(np.float32)
    
    # Normalize embeddings for cosine similarity
    faiss.normalize_L2(embeddings)
    
    # Create FAISS index (Inner Product for normalized vectors = cosine similarity)
    print("Creating FAISS index...")
    index = faiss.IndexFlatIP(embedding_dim)
    index.add(embeddings)
    
    # Save index
    index_path = os.path.join(indices_dir, "index.faiss")
    faiss.write_index(index, index_path)
    print(f"Index saved to: {index_path}")
    
    # Update metadata with embeddings
    for i, chunk in enumerate(chunks):
        chunk["embedding"] = embeddings[i].tolist()
    
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Updated metadata with embeddings at: {metadata_path}")
    print(f"Index contains {index.ntotal} vectors of dimension {embedding_dim}")

if __name__ == "__main__":
    create_sample_index()
