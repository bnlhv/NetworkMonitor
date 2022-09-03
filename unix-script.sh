#!/usr/bin/env sh
echo "Starting Network Monitor app."
docker compose up -d
echo "Started containers in detach mode."
echo "Installing servers python dependencies."
pip install -r server/requirements.txt
echo "Starting server."
python server/main.py
echo "Started server."
