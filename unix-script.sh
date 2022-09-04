#!/usr/bin/env sh
echo "Starting Network Monitor app."
docker compose up --build -d
echo "Started containers in detach mode."
echo "Installing client python dependencies."
pip install -r client/requirements.txt
echo "Installing servers python dependencies."
pip install -r server/requirements.txt
echo "Starting server."
python server/main.py
echo "Started server."
