#!/bin/bash

# Install tesseract OCR and Khmer language pack
sudo apt-get update
sudo apt-get install -y tesseract-ocr
sudo apt-get install -y tesseract-ocr-khm

# Run the bot
python khmer_ocr_bot.py