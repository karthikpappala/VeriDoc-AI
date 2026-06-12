#!/bin/bash
uvicorn api.main:app --host 127.0.0.1 --port 8000 &
python -m streamlit run ui/app.py \
  --server.port 8501 \
  --server.address 127.0.0.1 \
  --server.headless true \
  --server.enableCORS false \
  --server.enableXsrfProtection false &
sleep 10
nginx -g "daemon off;"
