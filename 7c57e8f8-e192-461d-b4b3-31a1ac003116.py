{
    "chunks": [
        {
            "type": "txt",
            "chunk_number": 1,
            "lines": [
                {
                    "line_number": 1,
                    "text": "import os"
                },
                {
                    "line_number": 2,
                    "text": "import re"
                },
                {
                    "line_number": 3,
                    "text": "import pandas as pd"
                },
                {
                    "line_number": 4,
                    "text": "import smtplib"
                },
                {
                    "line_number": 5,
                    "text": "from datetime import datetime"
                },
                {
                    "line_number": 6,
                    "text": "import hashlib"
                },
                {
                    "line_number": 7,
                    "text": "from email.mime.text import MIMEText"
                },
                {
                    "line_number": 8,
                    "text": "from email.mime.multipart import MIMEMultipart"
                },
                {
                    "line_number": 9,
                    "text": "from email.mime.application import MIMEApplication"
                },
                {
                    "line_number": 10,
                    "text": "import pytesseract"
                },
                {
                    "line_number": 11,
                    "text": "from pdf2image import convert_from_path"
                },
                {
                    "line_number": 12,
                    "text": "import pdfplumber"
                },
                {
                    "line_number": 13,
                    "text": "import openpyxl"
                },
                {
                    "line_number": 14,
                    "text": "from PIL import Image"
                },
                {
                    "line_number": 15,
                    "text": "import logging"
                },
                {
                    "line_number": 16,
                    "text": "import warnings"
                },
                {
                    "line_number": 17,
                    "text": "import tkinter as tk"
                },
                {
                    "line_number": 18,
                    "text": "from tkinter import messagebox"
                },
                {
                    "line_number": 19,
                    "text": "import threading"
                },
                {
                    "line_number": 20,
                    "text": "import time"
                },
                {
                    "line_number": 21,
                    "text": "from watchdog.observers import Observer"
                },
                {
                    "line_number": 22,
                    "text": "from watchdog.events import FileSystemEventHandler"
                },
                {
                    "line_number": 23,
                    "text": "from transformers import pipeline"
                },
                {
                    "line_number": 24,
                    "text": "import langid"
                },
                {
                    "line_number": 25,
                    "text": "import fasttext"
                },
                {
                    "line_number": 26,
                    "text": "import requests"
                },
                {
                    "line_number": 27,
                    "text": "from langdetect import detect, DetectorFactory"
                },
                {
                    "line_number": 28,
                    "text": ""
                },
                {
                    "line_number": 29,
                    "text": "# Initialize deterministic language detection"
                },
                {
                    "line_number": 30,
                    "text": "DetectorFactory.seed = 0"
                },
                {
                    "line_number": 31,
                    "text": ""
                },
                {
                    "line_number": 32,
                    "text": "# Suppress non-critical warnings"
                },
                {
                    "line_number": 33,
                    "text": "logging.getLogger(\"pdfminer\").setLevel(logging.ERROR)"
                },
                {
                    "line_number": 34,
                    "text": "warnings.filterwarnings(\"ignore\")"
                },
                {
                    "line_number": 35,
                    "text": ""
                },
                {
                    "line_number": 36,
                    "text": "# Tesseract path"
                },
                {
                    "line_number": 37,
                    "text": "pytesseract.pytesseract.tesseract_cmd = r\"C:\\Program Files\\Tesseract-OCR\\tesseract.exe\""
                },
                {
                    "line_number": 38,
                    "text": ""
                },
                {
                    "line_number": 39,
                    "text": "# Folders"
                },
                {
                    "line_number": 40,
                    "text": "FOLDER_PATH       = r\"C:\\Users\\nlushaba\\PII_Project\\scans\"         # Manual / batch scans"
                },
                {
                    "line_number": 41,
                    "text": "LOG_FOLDER        = r\"C:\\Users\\nlushaba\\PII_Project\\logs\"          # Where Excel logs go"
                },
                {
                    "line_number": 42,
                    "text": "USB_MONITOR_PATH  = r\"C:\\Users\\nlushaba\\PII_Project\\USB_DRIVE\"     # Folder to monitor for moved files"
                },
                {
                    "line_number": 43,
                    "text": ""
                },
                {
                    "line_number": 44,
                    "text": "os.makedirs(LOG_FOLDER, exist_ok=True)"
                },
                {
                    "line_number": 45,
                    "text": ""
                },
                {
                    "line_number": 46,
                    "text": "# Email settings"
                },
                {
                    "line_number": 47,
                    "text": "SENDER_EMAIL   = \"ndumisolushaba0@gmail.com\""
                },
                {
                    "line_number": 48,
                    "text": "PASSWORD       = \"bugmmsqggpijxmtd\""
                },
                {
                    "line_number": 49,
                    "text": "RECIPIENT_EMAIL= \"ndumisolushaba0@gmail.com\""
                },
                {
                    "line_number": 50,
                    "text": "CC_EMAILS      = []"
                },
                {
                    "line_number": 51,
                    "text": ""
                },
                {
                    "line_number": 52,
                    "text": "# Load FastText language detection model"
                },
                {
                    "line_number": 53,
                    "text": "LANG_MODEL_PATH = \"lid.176.bin\""
                },
                {
                    "line_number": 54,
                    "text": "if not os.path.exists(LANG_MODEL_PATH):"
                },
                {
                    "line_number": 55,
                    "text": "url = \"https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin\""
                },
                {
                    "line_number": 56,
                    "text": "r = requests.get(url, allow_redirects=True)"
                },
                {
                    "line_number": 57,
                    "text": "with open(LANG_MODEL_PATH, 'wb') as f:"
                },
                {
                    "line_number": 58,
                    "text": "f.write(r.content)"
                },
                {
                    "line_number": 59,
                    "text": "lang_model = fasttext.load_model(LANG_MODEL_PATH)"
                },
                {
                    "line_number": 60,
                    "text": ""
                },
                {
                    "line_number": 61,
                    "text": "# Initialize NER pipeline"
                },
                {
                    "line_number": 62,
                    "text": "ner_pipeline = pipeline("
                },
                {
                    "line_number": 63,
                    "text": "\"ner\","
                },
                {
                    "line_number": 64,
                    "text": "model=\"Davlan/bert-base-multilingual-cased-ner-hrl\",  # Multilingual model"
                },
                {
                    "line_number": 65,
                    "text": "aggregation_strategy=\"max\","
                },
                {
                    "line_number": 66,
                    "text": "device=-1  # Use CPU (-1) or GPU (0)"
                },
                {
                    "line_number": 67,
                    "text": ")"
                },
                {
                    "line_number": 68,
                    "text": ""
                },
                {
                    "line_number": 69,
                    "text": "# Base PII Patterns (language-independent)"
                },
                {
                    "line_number": 70,
                    "text": "BASE_PATTERNS = {"
                },
                {
                    "line_number": 71,
                    "text": "\"National ID\": r\"\\b\\d{6}(?:6100|1100|2100|7100)\\d{3}\\b\","
                },
                {
                    "line_number": 72,
                    "text": "\"Phone Number\": r\"\\b(?:\\+268)?(?:7[89]\\d{6}|[56]\\d{7}|2\\d{7})\\b\","
                },
                {
                    "line_number": 73,
                    "text": "\"Passport Number\": r\"\\b[A-Z]{1,2}\\d{6,8}\\b\","
                },
                {
                    "line_number": 74,
                    "text": "\"TIN\": r\"\\b\\d{9}\\b\","
                },
                {
                    "line_number": 75,
                    "text": "\"Driver\u2019s License\": r\"\\bD\\d{7,9}\\b\","
                },
                {
                    "line_number": 76,
                    "text": "\"Bank Account\": r\"\\b(?:62|02|91|77|10|99|63)\\d{8,10}\\b\","
                },
                {
                    "line_number": 77,
                    "text": "\"Credit Card\": r\"\\b(?:\\d{4}[ -]?){3}\\d{4}\\b\","
                },
                {
                    "line_number": 78,
                    "text": "\"Health Record\": r\"\\b(?:MED|PAT)\\d{6,8}\\b\","
                },
                {
                    "line_number": 79,
                    "text": "\"Student ID\": r\"\\b\\d{8,10}\\b\""
                },
                {
                    "line_number": 80,
                    "text": "}"
                },
                {
                    "line_number": 81,
                    "text": ""
                },
                {
                    "line_number": 82,
                    "text": "# Language-specific regex enhancements"
                },
                {
                    "line_number": 83,
                    "text": "LANGUAGE_REGEX_MAP = {"
                },
                {
                    "line_number": 84,
                    "text": "\"en\": {"
                },
                {
                    "line_number": 85,
                    "text": "\"Email\": r\"\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}\\b\","
                },
                {
                    "line_number": 86,
                    "text": "\"Name Prefix\": r\"\\b(?:Mr|Mrs|Ms|Dr|Prof)\\.?\\b\""
                },
                {
                    "line_number": 87,
                    "text": "},"
                },
                {
                    "line_number": 88,
                    "text": "\"fr\": {"
                },
                {
                    "line_number": 89,
                    "text": "\"Email\": r\"\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}\\b\","
                },
                {
                    "line_number": 90,
                    "text": "\"Name Prefix\": r\"\\b(?:M|Mme|Mlle|Dr|Prof)\\.?\\b\""
                },
                {
                    "line_number": 91,
                    "text": "},"
                },
                {
                    "line_number": 92,
                    "text": "\"es\": {"
                },
                {
                    "line_number": 93,
                    "text": "\"Email\": r\"\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}\\b\","
                },
                {
                    "line_number": 94,
                    "text": "\"Name Prefix\": r\"\\b(?:Sr|Sra|Srta|Dr|Prof)\\.?\\b\""
                },
                {
                    "line_number": 95,
                    "text": "},"
                },
                {
                    "line_number": 96,
                    "text": "\"pt\": {"
                },
                {
                    "line_number": 97,
                    "text": "\"Email\": r\"\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}\\b\","
                },
                {
                    "line_number": 98,
                    "text": "\"Name Prefix\": r\"\\b(?:Sr|Sra|Srta|Dr|Prof)\\.?\\b\""
                },
                {
                    "line_number": 99,
                    "text": "},"
                },
                {
                    "line_number": 100,
                    "text": "\"zu\": {"
                },
                {
                    "line_number": 101,
                    "text": "\"Phone Number\": r\"\\b(?:\\+27|0)[1-8]\\d{8}\\b\""
                },
                {
                    "line_number": 102,
                    "text": "}"
                },
                {
                    "line_number": 103,
                    "text": "}"
                },
                {
                    "line_number": 104,
                    "text": ""
                },
                {
                    "line_number": 105,
                    "text": "def get_log_path():"
                },
                {
                    "line_number": 106,
                    "text": "ts = datetime.now().strftime(\"%Y-%m-%d_%H-%M-%S\")"
                },
                {
                    "line_number": 107,
                    "text": "return os.path.join(LOG_FOLDER, f\"detected_pii_{ts}.xlsx\")"
                },
                {
                    "line_number": 108,
                    "text": ""
                },
                {
                    "line_number": 109,
                    "text": "def detect_language(text):"
                },
                {
                    "line_number": 110,
                    "text": "\"\"\"Detect language using multiple methods for reliability\"\"\""
                },
                {
                    "line_number": 111,
                    "text": "if len(text) < 50:"
                },
                {
                    "line_number": 112,
                    "text": "return \"unknown\""
                },
                {
                    "line_number": 113,
                    "text": ""
                },
                {
                    "line_number": 114,
                    "text": "try:"
                },
                {
                    "line_number": 115,
                    "text": "# Method 1: FastText (most reliable for short texts)"
                },
                {
                    "line_number": 116,
                    "text": "lang_pred = lang_model.predict(text.replace(\"\\n\", \" \"))[0][0].split(\"__\")[-1]"
                },
                {
                    "line_number": 117,
                    "text": "if lang_pred in LANGUAGE_REGEX_MAP:"
                },
                {
                    "line_number": 118,
                    "text": "return lang_pred"
                },
                {
                    "line_number": 119,
                    "text": "except:"
                },
                {
                    "line_number": 120,
                    "text": "pass"
                },
                {
                    "line_number": 121,
                    "text": ""
                },
                {
                    "line_number": 122,
                    "text": "try:"
                },
                {
                    "line_number": 123,
                    "text": "# Method 2: langdetect"
                },
                {
                    "line_number": 124,
                    "text": "return detect(text)"
                },
                {
                    "line_number": 125,
                    "text": "except:"
                },
                {
                    "line_number": 126,
                    "text": "pass"
                },
                {
                    "line_number": 127,
                    "text": ""
                },
                {
                    "line_number": 128,
                    "text": "try:"
                },
                {
                    "line_number": 129,
                    "text": "# Method 3: langid"
                },
                {
                    "line_number": 130,
                    "text": "return langid.classify(text)[0]"
                },
                {
                    "line_number": 131,
                    "text": "except:"
                },
                {
                    "line_number": 132,
                    "text": "return \"unknown\""
                },
                {
                    "line_number": 133,
                    "text": ""
                },
                {
                    "line_number": 134,
                    "text": "def get_patterns_for_text(text):"
                },
                {
                    "line_number": 135,
                    "text": "\"\"\"Get combined patterns based on detected language\"\"\""
                },
                {
                    "line_number": 136,
                    "text": "lang = detect_language(text)"
                },
                {
                    "line_number": 137,
                    "text": "patterns = BASE_PATTERNS.copy()"
                },
                {
                    "line_number": 138,
                    "text": ""
                },
                {
                    "line_number": 139,
                    "text": "# Add language-specific patterns if available"
                },
                {
                    "line_number": 140,
                    "text": "if lang in LANGUAGE_REGEX_MAP:"
                },
                {
                    "line_number": 141,
                    "text": "for key, pattern in LANGUAGE_REGEX_MAP[lang].items():"
                },
                {
                    "line_number": 142,
                    "text": "patterns[key] = pattern"
                },
                {
                    "line_number": 143,
                    "text": ""
                },
                {
                    "line_number": 144,
                    "text": "return patterns"
                },
                {
                    "line_number": 145,
                    "text": ""
                },
                {
                    "line_number": 146,
                    "text": "# Extraction functions with OCR support ------------------------------"
                },
                {
                    "line_number": 147,
                    "text": "def extract_text_from_txt(path):"
                },
                {
                    "line_number": 148,
                    "text": "try:"
                },
                {
                    "line_number": 149,
                    "text": "with open(path, 'r', encoding='utf-8', errors='ignore') as f:"
                },
                {
                    "line_number": 150,
                    "text": "return f.read()"
                },
                {
                    "line_number": 151,
                    "text": "except:"
                },
                {
                    "line_number": 152,
                    "text": "return \"\""
                },
                {
                    "line_number": 153,
                    "text": ""
                },
                {
                    "line_number": 154,
                    "text": "def extract_text_from_pdf(path):"
                },
                {
                    "line_number": 155,
                    "text": "text = \"\""
                },
                {
                    "line_number": 156,
                    "text": "try:"
                },
                {
                    "line_number": 157,
                    "text": "with pdfplumber.open(path) as pdf:"
                },
                {
                    "line_number": 158,
                    "text": "for p in pdf.pages:"
                },
                {
                    "line_number": 159,
                    "text": "text += (p.extract_text() or \"\") + \"\\n\""
                },
                {
                    "line_number": 160,
                    "text": "except:"
                },
                {
                    "line_number": 161,
                    "text": "pass"
                },
                {
                    "line_number": 162,
                    "text": ""
                },
                {
                    "line_number": 163,
                    "text": "# Fallback to OCR if text extraction fails"
                },
                {
                    "line_number": 164,
                    "text": "if len(text) < 50:"
                },
                {
                    "line_number": 165,
                    "text": "try:"
                },
                {
                    "line_number": 166,
                    "text": "images = convert_from_path(path, dpi=300)"
                },
                {
                    "line_number": 167,
                    "text": "for img in images:"
                },
                {
                    "line_number": 168,
                    "text": "text += pytesseract.image_to_string(img, lang='eng+fra+spa+por') + \"\\n\""
                },
                {
                    "line_number": 169,
                    "text": "except Exception as e:"
                },
                {
                    "line_number": 170,
                    "text": "print(f\"PDF OCR failed: {e}\")"
                },
                {
                    "line_number": 171,
                    "text": "return text"
                },
                {
                    "line_number": 172,
                    "text": ""
                },
                {
                    "line_number": 173,
                    "text": "def extract_text_from_doc(path):"
                },
                {
                    "line_number": 174,
                    "text": "try:"
                },
                {
                    "line_number": 175,
                    "text": "import docx2txt"
                },
                {
                    "line_number": 176,
                    "text": "return docx2txt.process(path) or \"\""
                },
                {
                    "line_number": 177,
                    "text": "except:"
                },
                {
                    "line_number": 178,
                    "text": "return \"\""
                },
                {
                    "line_number": 179,
                    "text": ""
                },
                {
                    "line_number": 180,
                    "text": "def extract_text_from_xlsx(path):"
                },
                {
                    "line_number": 181,
                    "text": "content = \"\""
                },
                {
                    "line_number": 182,
                    "text": "try:"
                },
                {
                    "line_number": 183,
                    "text": "wb = openpyxl.load_workbook(path, data_only=True)"
                },
                {
                    "line_number": 184,
                    "text": "for sheet in wb.sheetnames:"
                },
                {
                    "line_number": 185,
                    "text": "for row in wb[sheet].iter_rows(values_only=True):"
                },
                {
                    "line_number": 186,
                    "text": "for cell in row:"
                },
                {
                    "line_number": 187,
                    "text": "if cell:"
                },
                {
                    "line_number": 188,
                    "text": "content += f\"{cell} \""
                },
                {
                    "line_number": 189,
                    "text": "except:"
                },
                {
                    "line_number": 190,
                    "text": "pass"
                },
                {
                    "line_number": 191,
                    "text": "return content"
                },
                {
                    "line_number": 192,
                    "text": ""
                },
                {
                    "line_number": 193,
                    "text": "def extract_text_from_image(path):"
                },
                {
                    "line_number": 194,
                    "text": "try:"
                },
                {
                    "line_number": 195,
                    "text": "img = Image.open(path)"
                },
                {
                    "line_number": 196,
                    "text": "# Detect language for OCR optimization"
                },
                {
                    "line_number": 197,
                    "text": "temp_text = pytesseract.image_to_string(img, lang='eng')"
                },
                {
                    "line_number": 198,
                    "text": "lang = detect_language(temp_text)"
                },
                {
                    "line_number": 199,
                    "text": ""
                },
                {
                    "line_number": 200,
                    "text": "# Use appropriate language packs"
                },
                {
                    "line_number": 201,
                    "text": "langs = 'eng'"
                },
                {
                    "line_number": 202,
                    "text": "if lang == 'fr': langs = 'fra'"
                },
                {
                    "line_number": 203,
                    "text": "elif lang == 'es': langs = 'spa'"
                },
                {
                    "line_number": 204,
                    "text": "elif lang == 'pt': langs = 'por'"
                },
                {
                    "line_number": 205,
                    "text": ""
                },
                {
                    "line_number": 206,
                    "text": "return pytesseract.image_to_string(img, lang=langs)"
                },
                {
                    "line_number": 207,
                    "text": "except Exception as e:"
                },
                {
                    "line_number": 208,
                    "text": "print(f\"Image OCR failed: {e}\")"
                },
                {
                    "line_number": 209,
                    "text": "return \"\""
                },
                {
                    "line_number": 210,
                    "text": ""
                },
                {
                    "line_number": 211,
                    "text": "def extract_text_from_any_file(path):"
                },
                {
                    "line_number": 212,
                    "text": "\"\"\""
                },
                {
                    "line_number": 213,
                    "text": "Attempts PDF \u2192 DOC \u2192 XLSX \u2192 image \u2192 TXT extraction in order."
                },
                {
                    "line_number": 214,
                    "text": "Returns the first non-empty result."
                },
                {
                    "line_number": 215,
                    "text": "\"\"\""
                },
                {
                    "line_number": 216,
                    "text": "ext = path.lower().split('.')[-1]"
                },
                {
                    "line_number": 217,
                    "text": ""
                },
                {
                    "line_number": 218,
                    "text": "handlers = {"
                },
                {
                    "line_number": 219,
                    "text": "'pdf': extract_text_from_pdf,"
                },
                {
                    "line_number": 220,
                    "text": "'docx': extract_text_from_doc,"
                },
                {
                    "line_number": 221,
                    "text": "'xlsx': extract_text_from_xlsx,"
                },
                {
                    "line_number": 222,
                    "text": "'txt': extract_text_from_txt,"
                },
                {
                    "line_number": 223,
                    "text": "'png': extract_text_from_image,"
                },
                {
                    "line_number": 224,
                    "text": "'jpg': extract_text_from_image,"
                },
                {
                    "line_number": 225,
                    "text": "'jpeg': extract_text_from_image,"
                },
                {
                    "line_number": 226,
                    "text": "'bmp': extract_text_from_image,"
                },
                {
                    "line_number": 227,
                    "text": "'tiff': extract_text_from_image"
                },
                {
                    "line_number": 228,
                    "text": "}"
                },
                {
                    "line_number": 229,
                    "text": ""
                },
                {
                    "line_number": 230,
                    "text": "for extension, handler in handlers.items():"
                },
                {
                    "line_number": 231,
                    "text": "if ext == extension:"
                },
                {
                    "line_number": 232,
                    "text": "return handler(path)"
                },
                {
                    "line_number": 233,
                    "text": ""
                },
                {
                    "line_number": 234,
                    "text": "# Fallback for unknown extensions"
                },
                {
                    "line_number": 235,
                    "text": "for handler in ("
                },
                {
                    "line_number": 236,
                    "text": "extract_text_from_pdf,"
                },
                {
                    "line_number": 237,
                    "text": "extract_text_from_doc,"
                },
                {
                    "line_number": 238,
                    "text": "extract_text_from_xlsx,"
                },
                {
                    "line_number": 239,
                    "text": "extract_text_from_txt,"
                },
                {
                    "line_number": 240,
                    "text": "extract_text_from_image"
                },
                {
                    "line_number": 241,
                    "text": "):"
                },
                {
                    "line_number": 242,
                    "text": "try:"
                },
                {
                    "line_number": 243,
                    "text": "text = handler(path)"
                },
                {
                    "line_number": 244,
                    "text": "if text and text.strip():"
                },
                {
                    "line_number": 245,
                    "text": "return text"
                },
                {
                    "line_number": 246,
                    "text": "except Exception as e:"
                },
                {
                    "line_number": 247,
                    "text": "print(f\"Extraction failed for {path}: {e}\")"
                },
                {
                    "line_number": 248,
                    "text": ""
                },
                {
                    "line_number": 249,
                    "text": "return \"\""
                },
                {
                    "line_number": 250,
                    "text": ""
                },
                {
                    "line_number": 251,
                    "text": "# Logging & Email -----------------------------------------------"
                },
                {
                    "line_number": 252,
                    "text": "def log_detected_pii(df, pii_type, value, filename, line_no, confidence=1.0):"
                },
                {
                    "line_number": 253,
                    "text": "masked = value[:2] + '*'*(len(value)-4) + value[-2:] if len(value)>4 else '*'*len(value)"
                },
                {
                    "line_number": 254,
                    "text": "entry = {"
                },
                {
                    "line_number": 255,
                    "text": "\"Timestamp\": pd.Timestamp.now(),"
                },
                {
                    "line_number": 256,
                    "text": "\"PII Type\": pii_type,"
                },
                {
                    "line_number": 257,
                    "text": "\"Masked PII\": masked,"
                },
                {
                    "line_number": 258,
                    "text": "\"SHA256 Hash\": hashlib.sha256(value.encode()).hexdigest(),"
                },
                {
                    "line_number": 259,
                    "text": "\"File Name\": filename,"
                },
                {
                    "line_number": 260,
                    "text": "\"Line Number\": line_no,"
                },
                {
                    "line_number": 261,
                    "text": "\"Confidence\": confidence"
                },
                {
                    "line_number": 262,
                    "text": "}"
                },
                {
                    "line_number": 263,
                    "text": "return pd.concat([df, pd.DataFrame([entry])], ignore_index=True)"
                },
                {
                    "line_number": 264,
                    "text": ""
                },
                {
                    "line_number": 265,
                    "text": "def send_email_alert(subject, body, log_df):"
                },
                {
                    "line_number": 266,
                    "text": "path = get_log_path()"
                },
                {
                    "line_number": 267,
                    "text": "log_df.to_excel(path, index=False)"
                },
                {
                    "line_number": 268,
                    "text": "msg = MIMEMultipart()"
                },
                {
                    "line_number": 269,
                    "text": "msg['From'] = SENDER_EMAIL"
                },
                {
                    "line_number": 270,
                    "text": "msg['To']   = RECIPIENT_EMAIL"
                },
                {
                    "line_number": 271,
                    "text": "msg['Subject'] = subject"
                },
                {
                    "line_number": 272,
                    "text": "if CC_EMAILS:"
                },
                {
                    "line_number": 273,
                    "text": "msg['Cc'] = ','.join(CC_EMAILS)"
                },
                {
                    "line_number": 274,
                    "text": "msg.attach(MIMEText(body, 'plain'))"
                },
                {
                    "line_number": 275,
                    "text": "with open(path, 'rb') as f:"
                },
                {
                    "line_number": 276,
                    "text": "part = MIMEApplication(f.read(), Name=os.path.basename(path))"
                },
                {
                    "line_number": 277,
                    "text": "part['Content-Disposition'] = f'attachment; filename=\"{os.path.basename(path)}\"'"
                },
                {
                    "line_number": 278,
                    "text": "msg.attach(part)"
                },
                {
                    "line_number": 279,
                    "text": ""
                },
                {
                    "line_number": 280,
                    "text": "try:"
                },
                {
                    "line_number": 281,
                    "text": "with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:"
                },
                {
                    "line_number": 282,
                    "text": "server.login(SENDER_EMAIL, PASSWORD)"
                },
                {
                    "line_number": 283,
                    "text": "server.sendmail(SENDER_EMAIL, [RECIPIENT_EMAIL]+CC_EMAILS, msg.as_string())"
                },
                {
                    "line_number": 284,
                    "text": "print(\"\u2705 Email sent:\", path)"
                },
                {
                    "line_number": 285,
                    "text": "except Exception as e:"
                },
                {
                    "line_number": 286,
                    "text": "print(\"\ud83d\udce8 Email failed:\", e)"
                },
                {
                    "line_number": 287,
                    "text": ""
                },
                {
                    "line_number": 288,
                    "text": "def show_popup(title, message):"
                },
                {
                    "line_number": 289,
                    "text": "root = tk.Tk()"
                },
                {
                    "line_number": 290,
                    "text": "root.withdraw()"
                },
                {
                    "line_number": 291,
                    "text": "messagebox.showinfo(title, message)"
                },
                {
                    "line_number": 292,
                    "text": "root.destroy()"
                },
                {
                    "line_number": 293,
                    "text": ""
                },
                {
                    "line_number": 294,
                    "text": "# Folder-scan function (updated) -------------------------------"
                },
                {
                    "line_number": 295,
                    "text": "def scan_folder(queue, folder_path):"
                },
                {
                    "line_number": 296,
                    "text": "df = pd.DataFrame(columns=["
                },
                {
                    "line_number": 297,
                    "text": "\"Timestamp\",\"PII Type\",\"Masked PII\",\"SHA256 Hash\",\"File Name\",\"Line Number\",\"Confidence\""
                },
                {
                    "line_number": 298,
                    "text": "])"
                },
                {
                    "line_number": 299,
                    "text": ""
                },
                {
                    "line_number": 300,
                    "text": "for fname in os.listdir(folder_path):"
                },
                {
                    "line_number": 301,
                    "text": "full = os.path.join(folder_path, fname)"
                },
                {
                    "line_number": 302,
                    "text": "if not os.path.isfile(full):"
                },
                {
                    "line_number": 303,
                    "text": "continue"
                },
                {
                    "line_number": 304,
                    "text": ""
                },
                {
                    "line_number": 305,
                    "text": "text = extract_text_from_any_file(full)"
                },
                {
                    "line_number": 306,
                    "text": "if queue:"
                },
                {
                    "line_number": 307,
                    "text": "queue.put({\"type\":\"file_scanned\",\"file_name\":fname})"
                },
                {
                    "line_number": 308,
                    "text": ""
                },
                {
                    "line_number": 309,
                    "text": "if not text.strip():"
                },
                {
                    "line_number": 310,
                    "text": "print(f\"Skipping (no text): {fname}\")"
                },
                {
                    "line_number": 311,
                    "text": "continue"
                },
                {
                    "line_number": 312,
                    "text": ""
                },
                {
                    "line_number": 313,
                    "text": "print(f\"\\n--- Scanning {fname} ---\")"
                },
                {
                    "line_number": 314,
                    "text": "detected = False"
                },
                {
                    "line_number": 315,
                    "text": ""
                },
                {
                    "line_number": 316,
                    "text": "# Get language-specific patterns"
                },
                {
                    "line_number": 317,
                    "text": "patterns = get_patterns_for_text(text)"
                },
                {
                    "line_number": 318,
                    "text": "print(f\"Detected language: {detect_language(text)}\")"
                },
                {
                    "line_number": 319,
                    "text": ""
                },
                {
                    "line_number": 320,
                    "text": "# Regex-based detection"
                },
                {
                    "line_number": 321,
                    "text": "for pii, pat in patterns.items():"
                },
                {
                    "line_number": 322,
                    "text": "for idx, m in enumerate(re.findall(pat, text, flags=re.IGNORECASE), start=1):"
                },
                {
                    "line_number": 323,
                    "text": "detected = True"
                },
                {
                    "line_number": 324,
                    "text": "print(f\"  \u2705 [Regex] {pii}: {m}\")"
                },
                {
                    "line_number": 325,
                    "text": "df = log_detected_pii(df, pii, m, fname, idx)"
                },
                {
                    "line_number": 326,
                    "text": "if queue:"
                },
                {
                    "line_number": 327,
                    "text": "queue.put({"
                },
                {
                    "line_number": 328,
                    "text": "\"type\":\"pii_detected\","
                },
                {
                    "line_number": 329,
                    "text": "\"pii_type\":pii,"
                },
                {
                    "line_number": 330,
                    "text": "\"file_name\":fname,"
                },
                {
                    "line_number": 331,
                    "text": "\"line\":idx"
                },
                {
                    "line_number": 332,
                    "text": "})"
                },
                {
                    "line_number": 333,
                    "text": ""
                },
                {
                    "line_number": 334,
                    "text": "# NER-based name detection"
                },
                {
                    "line_number": 335,
                    "text": "try:"
                },
                {
                    "line_number": 336,
                    "text": "# Process in chunks for large documents"
                },
                {
                    "line_number": 337,
                    "text": "chunk_size = 1000"
                },
                {
                    "line_number": 338,
                    "text": "chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]"
                },
                {
                    "line_number": 339,
                    "text": ""
                },
                {
                    "line_number": 340,
                    "text": "for chunk_idx, chunk in enumerate(chunks):"
                },
                {
                    "line_number": 341,
                    "text": "entities = ner_pipeline(chunk)"
                },
                {
                    "line_number": 342,
                    "text": ""
                },
                {
                    "line_number": 343,
                    "text": "for entity in entities:"
                },
                {
                    "line_number": 344,
                    "text": "if entity['entity_group'] == 'PER' and entity['score'] >= 0.85:"
                },
                {
                    "line_number": 345,
                    "text": "detected = True"
                },
                {
                    "line_number": 346,
                    "text": "line_no = chunk_idx * chunk_size + entity['start']  # Approximate line number"
                },
                {
                    "line_number": 347,
                    "text": "print(f\"  \u2705 [NER] Personal Name: {entity['word']} (confidence: {entity['score']:.2f})\")"
                },
                {
                    "line_number": 348,
                    "text": "df = log_detected_pii("
                },
                {
                    "line_number": 349,
                    "text": "df,"
                },
                {
                    "line_number": 350,
                    "text": "\"Personal Name\","
                },
                {
                    "line_number": 351,
                    "text": "entity['word'],"
                },
                {
                    "line_number": 352,
                    "text": "fname,"
                },
                {
                    "line_number": 353,
                    "text": "line_no,"
                },
                {
                    "line_number": 354,
                    "text": "entity['score']"
                },
                {
                    "line_number": 355,
                    "text": ")"
                },
                {
                    "line_number": 356,
                    "text": "if queue:"
                },
                {
                    "line_number": 357,
                    "text": "queue.put({"
                },
                {
                    "line_number": 358,
                    "text": "\"type\":\"pii_detected\","
                },
                {
                    "line_number": 359,
                    "text": "\"pii_type\":\"Personal Name\","
                },
                {
                    "line_number": 360,
                    "text": "\"file_name\":fname,"
                },
                {
                    "line_number": 361,
                    "text": "\"line\":line_no"
                },
                {
                    "line_number": 362,
                    "text": "})"
                },
                {
                    "line_number": 363,
                    "text": "except Exception as e:"
                },
                {
                    "line_number": 364,
                    "text": "print(f\"NER processing failed: {e}\")"
                },
                {
                    "line_number": 365,
                    "text": ""
                },
                {
                    "line_number": 366,
                    "text": "if not detected:"
                },
                {
                    "line_number": 367,
                    "text": "print(f\"  \u274c No PII in {fname}\")"
                },
                {
                    "line_number": 368,
                    "text": ""
                },
                {
                    "line_number": 369,
                    "text": "if not df.empty:"
                },
                {
                    "line_number": 370,
                    "text": "summary = df.to_string(index=False)"
                },
                {
                    "line_number": 371,
                    "text": "show_popup(\"Scan Complete\", \"PII found\u2014sending email alert now\u2026\")"
                },
                {
                    "line_number": 372,
                    "text": "send_email_alert(\"\u2705 PII Detection Alert\", f\"Dear Team,\\n\\n{summary}\\n\\nRegards\", df)"
                },
                {
                    "line_number": 373,
                    "text": "else:"
                },
                {
                    "line_number": 374,
                    "text": "print(\"\u2705 No PII found.\")"
                },
                {
                    "line_number": 375,
                    "text": ""
                },
                {
                    "line_number": 376,
                    "text": "# USB/folder monitor (updated) ----------------------------------"
                },
                {
                    "line_number": 377,
                    "text": "def try_extract_text_with_retries(path, retries=5, delay=1):"
                },
                {
                    "line_number": 378,
                    "text": "for i in range(retries):"
                },
                {
                    "line_number": 379,
                    "text": "text = extract_text_from_any_file(path)"
                },
                {
                    "line_number": 380,
                    "text": "if text.strip():"
                },
                {
                    "line_number": 381,
                    "text": "return text"
                },
                {
                    "line_number": 382,
                    "text": "time.sleep(delay)"
                },
                {
                    "line_number": 383,
                    "text": "return \"\""
                },
                {
                    "line_number": 384,
                    "text": ""
                },
                {
                    "line_number": 385,
                    "text": "class PIIFileHandler(FileSystemEventHandler):"
                },
                {
                    "line_number": 386,
                    "text": "def __init__(self, base_patterns, lang_model):"
                },
                {
                    "line_number": 387,
                    "text": "super().__init__()"
                },
                {
                    "line_number": 388,
                    "text": "self.base_patterns = base_patterns"
                },
                {
                    "line_number": 389,
                    "text": "self.lang_model = lang_model"
                },
                {
                    "line_number": 390,
                    "text": ""
                },
                {
                    "line_number": 391,
                    "text": "def get_patterns_for_text(self, text):"
                },
                {
                    "line_number": 392,
                    "text": "lang = detect_language(text)"
                },
                {
                    "line_number": 393,
                    "text": "patterns = self.base_patterns.copy()"
                },
                {
                    "line_number": 394,
                    "text": ""
                },
                {
                    "line_number": 395,
                    "text": "if lang in LANGUAGE_REGEX_MAP:"
                },
                {
                    "line_number": 396,
                    "text": "for key, pattern in LANGUAGE_REGEX_MAP[lang].items():"
                },
                {
                    "line_number": 397,
                    "text": "patterns[key] = pattern"
                },
                {
                    "line_number": 398,
                    "text": ""
                },
                {
                    "line_number": 399,
                    "text": "return patterns"
                },
                {
                    "line_number": 400,
                    "text": ""
                },
                {
                    "line_number": 401,
                    "text": "def detect_pii(self, text, filename):"
                },
                {
                    "line_number": 402,
                    "text": "# Check regex patterns"
                },
                {
                    "line_number": 403,
                    "text": "patterns = self.get_patterns_for_text(text)"
                },
                {
                    "line_number": 404,
                    "text": "for pat in patterns.values():"
                },
                {
                    "line_number": 405,
                    "text": "if re.search(pat, text, flags=re.IGNORECASE):"
                },
                {
                    "line_number": 406,
                    "text": "return True"
                },
                {
                    "line_number": 407,
                    "text": ""
                },
                {
                    "line_number": 408,
                    "text": "# Check NER for names"
                },
                {
                    "line_number": 409,
                    "text": "try:"
                },
                {
                    "line_number": 410,
                    "text": "entities = ner_pipeline(text[:2000])  # Only check first 2000 chars for performance"
                },
                {
                    "line_number": 411,
                    "text": "for entity in entities:"
                },
                {
                    "line_number": 412,
                    "text": "if entity['entity_group'] == 'PER' and entity['score'] >= 0.85:"
                },
                {
                    "line_number": 413,
                    "text": "return True"
                },
                {
                    "line_number": 414,
                    "text": "except:"
                },
                {
                    "line_number": 415,
                    "text": "pass"
                },
                {
                    "line_number": 416,
                    "text": ""
                },
                {
                    "line_number": 417,
                    "text": "return False"
                },
                {
                    "line_number": 418,
                    "text": ""
                },
                {
                    "line_number": 419,
                    "text": "def on_created(self, event):"
                },
                {
                    "line_number": 420,
                    "text": "if event.is_directory:"
                },
                {
                    "line_number": 421,
                    "text": "return"
                },
                {
                    "line_number": 422,
                    "text": "path = event.src_path"
                },
                {
                    "line_number": 423,
                    "text": "print(\"Detected new file:\", path)"
                },
                {
                    "line_number": 424,
                    "text": "text = try_extract_text_with_retries(path)"
                },
                {
                    "line_number": 425,
                    "text": "if not text.strip():"
                },
                {
                    "line_number": 426,
                    "text": "print(\"  \u2192 No text extracted.\")"
                },
                {
                    "line_number": 427,
                    "text": "return"
                },
                {
                    "line_number": 428,
                    "text": ""
                },
                {
                    "line_number": 429,
                    "text": "if self.detect_pii(text, os.path.basename(path)):"
                },
                {
                    "line_number": 430,
                    "text": "show_popup(\"PII Detected\","
                },
                {
                    "line_number": 431,
                    "text": "f\"'{os.path.basename(path)}' contains PII and cannot stay here!\")"
                },
                {
                    "line_number": 432,
                    "text": "try:"
                },
                {
                    "line_number": 433,
                    "text": "os.remove(path)"
                },
                {
                    "line_number": 434,
                    "text": "print(\"  \u2192 Deleted:\", path)"
                },
                {
                    "line_number": 435,
                    "text": "except Exception as e:"
                },
                {
                    "line_number": 436,
                    "text": "print(\"  \u2192 Delete failed:\", e)"
                },
                {
                    "line_number": 437,
                    "text": ""
                },
                {
                    "line_number": 438,
                    "text": "def start_monitor(folder, base_patterns, lang_model):"
                },
                {
                    "line_number": 439,
                    "text": "handler  = PIIFileHandler(base_patterns, lang_model)"
                },
                {
                    "line_number": 440,
                    "text": "observer = Observer()"
                },
                {
                    "line_number": 441,
                    "text": "observer.schedule(handler, folder, recursive=False)"
                },
                {
                    "line_number": 442,
                    "text": "observer.start()"
                },
                {
                    "line_number": 443,
                    "text": "print(\"Monitoring folder:\", folder)"
                },
                {
                    "line_number": 444,
                    "text": "try:"
                },
                {
                    "line_number": 445,
                    "text": "while True:"
                },
                {
                    "line_number": 446,
                    "text": "time.sleep(1)"
                },
                {
                    "line_number": 447,
                    "text": "except KeyboardInterrupt:"
                },
                {
                    "line_number": 448,
                    "text": "observer.stop()"
                },
                {
                    "line_number": 449,
                    "text": "observer.join()"
                },
                {
                    "line_number": 450,
                    "text": ""
                },
                {
                    "line_number": 451,
                    "text": "# Launch monitor thread and run initial scan --------------------"
                },
                {
                    "line_number": 452,
                    "text": "monitor_thread = threading.Thread("
                },
                {
                    "line_number": 453,
                    "text": "target=start_monitor,"
                },
                {
                    "line_number": 454,
                    "text": "args=(USB_MONITOR_PATH, BASE_PATTERNS, lang_model),"
                },
                {
                    "line_number": 455,
                    "text": "daemon=True"
                },
                {
                    "line_number": 456,
                    "text": ")"
                },
                {
                    "line_number": 457,
                    "text": "monitor_thread.start()"
                },
                {
                    "line_number": 458,
                    "text": ""
                },
                {
                    "line_number": 459,
                    "text": "if __name__ == \"__main__\":"
                },
                {
                    "line_number": 460,
                    "text": "# initial batch scan"
                },
                {
                    "line_number": 461,
                    "text": "scan_folder(None, FOLDER_PATH)"
                },
                {
                    "line_number": 462,
                    "text": ""
                },
                {
                    "line_number": 463,
                    "text": "print(\"Monitoring in background. Ctrl+C to exit.\")"
                },
                {
                    "line_number": 464,
                    "text": "try:"
                },
                {
                    "line_number": 465,
                    "text": "while True:"
                },
                {
                    "line_number": 466,
                    "text": "time.sleep(10)"
                },
                {
                    "line_number": 467,
                    "text": "except KeyboardInterrupt:"
                },
                {
                    "line_number": 468,
                    "text": "print(\"Exiting.\")"
                }
            ],
            "token_count": 3121
        }
    ]
}