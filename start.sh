#!/bin/bash

apt-get update
apt-get install -y tesseract-ocr
apt-get install -y tesseract-ocr-khm

python khmer_ocr_bot.py
