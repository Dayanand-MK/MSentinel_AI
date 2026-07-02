FROM python:3.10-slim

# Install system dependencies for OCR and PDF rendering
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Download spaCy model during build
RUN python -m spacy download en_core_web_sm

# Copy project files
COPY . .

# Create necessary runtime directories
RUN mkdir -p uploads outputs logs chroma_db

# Streamlit Cloud Run config: use PORT env variable (Cloud Run injects this)
ENV PORT=8080

EXPOSE 8080

# Entrypoint: bind to $PORT for Cloud Run compatibility
CMD streamlit run app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false
