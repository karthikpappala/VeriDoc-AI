#!/bin/bash
uvicorn api.main:app --host 0.0.0.0 --port 8080 &
python -m streamlit run ui/app.py --server.port 7860 --server.address 0.0.0.0 --server.headless true
