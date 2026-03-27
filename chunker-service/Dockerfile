# Usa un'immagine base di Python
FROM python:3.11-slim

# Imposta la directory di lavoro nel container
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install \
    torch==2.3.0+cpu \
    torchvision==0.18.0+cpu \
    torchaudio==2.3.0+cpu \
    -f https://download.pytorch.org/whl/torch_stable.html

RUN pip install \
    spacy \
    pymupdf \
    fastapi \
    uvicorn[standard] \
    requests \
    transformers \
    python-multipart 

# Scarica e installa il modello linguistico di spaCy
RUN python -m spacy download it_core_news_sm

# Copia il codice sorgente
COPY . .

# Espone la porta che l'applicazione utilizzerà
EXPOSE 8000

# Comando per avviare il servizio
CMD ["uvicorn", "chunker:app", "--host", "0.0.0.0", "--port", "8000"]