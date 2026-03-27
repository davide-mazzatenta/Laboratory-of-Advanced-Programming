# Usa un'immagine base di Python
FROM python:3.11-slim

# Imposta le variabili d'ambiente per migliorare le performance di Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Imposta la directory di lavoro nel container
WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    # Rimuove la cache di apt per ridurre le dimensioni dell'immagine
    && rm -rf /var/lib/apt/lists/*

# Installa tutte le dipendenze Python necessarie direttamente con pip
RUN pip install --upgrade pip \
    && pip install \
        fastapi \
        uvicorn \
        requests \
        pydantic \
        pypdf \
        pymupdf \
        python-multipart\
        supabase\
        numpy

# Copia il codice sorgente dell'applicazione nella directory di lavoro
COPY . .

# Crea un utente non-root per questioni di sicurezza
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Espone la porta che l'applicazione utilizzerà
EXPOSE 8000

# Health check per verificare che l’API sia attiva
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/docs || exit 1

# Comando per avviare il servizio utilizzando uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]