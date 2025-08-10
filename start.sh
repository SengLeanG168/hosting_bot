#!/bin/bash

# Install tesseract OCR
apt-get update
apt-get install -y tesseract-ocr
apt-get install -y tesseract-ocr-khm

# Run the bot
python khmer_ocr_bot.py
