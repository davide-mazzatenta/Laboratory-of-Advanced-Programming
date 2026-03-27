from chunker import Chunker
import os

def main():
    chunker = Chunker.get_instance()
    
    # Cambia con il percorso del tuo file di test
    file_path = "transaction.pdf"   
    
    if not os.path.exists(file_path):
        print(f"⚠️ File '{file_path}' non trovato.")
        return
    
    chunks = chunker.chunk_text(file_path)
    
    print(f"\n📄 File: {file_path}")
    print(f"🔹 Numero chunk generati: {len(chunks)}\n")
    
    for i, chunk in enumerate(chunks, 1):
        print(f"--- Chunk {i} ---")
        print(chunk["text"])
        #print(f"Entities: {chunk['entities']}")
        print(f"Embedding size: {len(chunk['embedding'])}")
        print()

if __name__ == "__main__":
    main()
