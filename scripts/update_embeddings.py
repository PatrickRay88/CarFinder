#!/usr/bin/env python3
"""Update embeddings and FAISS index for CarFinder."""

import sys
from pathlib import Path

# Add the app directory to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.utils.config import load_config
from app.rag.retriever import VehicleRetriever

def main():
    """Update the vehicle embeddings and search index."""
    print("🚗 CarFinder Embedding Update")
    print("=" * 30)
    
    # Load configuration
    config = load_config()
    
    try:
        print("🔍 Initializing retriever...")
        retriever = VehicleRetriever(config)
        
        print("🔄 Updating embeddings and search index...")
        retriever.update_index()
        
        print("✅ Embeddings updated successfully!")
        print("\n💡 You can now run the Streamlit app with better search capabilities.")
        
    except Exception as e:
        print(f"❌ Error updating embeddings: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()