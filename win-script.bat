@echo off
docker compose up -d
pip install -r server\requirements.txt
python server\main.py