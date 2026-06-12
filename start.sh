#!/bin/bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 &
python -m streamlit run ui/app.py \
  --server.port 8501 \
  --server.address 0.0.0.0 \
  --server.headless true \
  --server.enableCORS false \
  --server.enableXsrfProtection false \
  nginx -g "daemon off;"
