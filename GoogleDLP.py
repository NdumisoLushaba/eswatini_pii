import os
import csv
import fitz  # PyMuPDF
from datetime import datetime
from google.cloud import dlp_v2, vision
from google.cloud.dlp_v2 import types
import smtplib
from email.message import EmailMessage
import mimetypes
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import spacy
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import logging

# Configure logging for service and presentation
logging.basicConfig(
    filename="pii_scanner.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

nltk.download('vader_lexicon', quiet=True)
sia = SentimentIntensityAnalyzer()
nlp = spacy.load("en_core_web_sm")

# Add EntityRuler for siSwati-specific NER (from previous response)
def add_siswati_ner(nlp_model):
    ruler = nlp_model.add_pipe("entity_ruler", before="ner")
    patterns = [
        {"label": "PERSON", "pattern": [{"LOWER": {"IN": ["sipho", "thembumenzi", "nomsa", "thuli", "bongani"]}}]},
        {"label": "GPE", "pattern": [{"LOWER": {"IN": ["eswatini", "mbabane", "manzini", "lobamba"]}}]},
        {"label": "PERSON", "pattern": [{"TEXT": {"REGEX": r"^[A-Z][a-z]+(ani|ile|eni)$"}}]}
    ]
    ruler.add_patterns(patterns)
    return nlp_model

nlp = add_siswati_ner(nlp)

# ---------------- OCR SCAN ----------------
def extract_text_from_image(image_content):
    try:
        client = vision.ImageAnnotatorClient()
        image = vision.Image(content=image_content)
        response = client.text_detection(image=image)
        return response.full_text_annotation.text if response.full_text_annotation.text else ""
    except Exception as e:
        logging.error(f"Image OCR error: {e}")
        return ""

def extract_text_from_pdf(pdf_path):
    try:
        text = ""
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
        return text.strip()
    except Exception as e:
        logging.error(f"PDF extraction error for {pdf_path}: {e}")
        return ""

def get_text_from_file(file_path):
    ext = os.path.splitext(file_path)[-1].lower()
    try:
        if ext in [".png", ".jpg", ".jpeg"]:
            with open(file_path, "rb") as img_file:
                content = img_file.read()
                return extract_text_from_image(content)
        elif ext == ".pdf":
            return extract_text_from_pdf(file_path)
        elif ext == ".txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        else:
            logging.warning(f"Unsupported file: {file_path}")
            return ""
    except Exception as e:
        logging.error(f"Error processing file {file_path}: {e}")
        return ""

# ---------------- DLP SCAN ----------------
def dlp_custom_scan(text, project_id):
    try:
        dlp = dlp_v2.DlpServiceClient()
        parent = f"projects/{project_id}"
        custom_regex = types.CustomInfoType(
            info_type=types.InfoType(name="ESWATINI_ID"),
            regex=types.CustomInfoType.Regex(pattern=r"\b\d{2}-\d{6}-[A-Z]-\d{2}\b"),
            likelihood=types.Likelihood.LIKELY
        )
        name_list = ["Sipho", "Thembumenzi", "Nomsa", "Thuli", "Bongani", "Sibusiso", "Lindiwe", "Ndumiso"]
        custom_dict = types.CustomInfoType(
            info_type=types.InfoType(name="SISWATI_NAME"),
            dictionary=types.CustomInfoType.Dictionary(
                word_list=types.CustomInfoType.Dictionary.WordList(words=name_list)
            ),
            likelihood=types.Likelihood.LIKELY
        )
        inspect_config = types.InspectConfig(
            custom_info_types=[custom_regex, custom_dict],
            include_quote=True
        )
        item = {"value": text}
        response = dlp.inspect_content(
            request={"parent": parent, "inspect_config": inspect_config, "item": item}
        )
        findings = [
            {"info_type": finding.info_type.name, "match": finding.quote, "likelihood": finding.likelihood.name}
            for finding in response.result.findings
        ]
        return findings
    except Exception as e:
        logging.error(f"DLP scan error: {e}")
        return []

# ---------------- ANALYSIS ----------------
def analyze_sentiment(text):
    try:
        score = sia.polarity_scores(text)
        if score['compound'] >= 0.05:
            return "Positive"
        elif score['compound'] <= -0.05:
            return "Negative"
        else:
            return "Neutral"
    except Exception as e:
        logging.error(f"Sentiment analysis error: {e}")
        return "Unknown"

def extract_named_entities(text):
    try:
        doc = nlp(text)
        entities = set(f"{ent.text} ({ent.label_})" for ent in doc.ents if ent.label_ in ["PERSON", "ORG", "GPE", "LOC", "DATE"])
        return ", ".join(entities) if entities else "None"
    except Exception as e:
        logging.error(f"NER error: {e}")
        return "None"

# ---------------- CSV REPORT ----------------
def save_to_csv(file_name, pii_results, sentiment, named_entities, output_csv="scan_results.csv"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(output_csv, mode="a", newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            if os.path.getsize(output_csv) == 0:
                writer.writerow(["File", "InfoType", "Match", "Likelihood", "Sentiment", "NamedEntities", "Timestamp"])
            for pii in pii_results:
                writer.writerow([file_name, pii["info_type"], pii["match"], pii["likelihood"], sentiment, named_entities, timestamp])
        logging.info(f"Results written to {output_csv} for {file_name}")
    except Exception as e:
        logging.error(f"Error writing to CSV {output_csv}: {e}")

def save_named_entities_to_csv(file_name, named_entities, output_csv="named_entities.csv"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(output_csv, mode="a", newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            if os.path.getsize(output_csv) == 0:
                writer.writerow(["File", "NamedEntities", "Timestamp"])
            writer.writerow([file_name, named_entities, timestamp])
        logging.info(f"Named entities written to {output_csv} for {file_name}")
    except Exception as e:
        logging.error(f"Error writing to named entities CSV {output_csv}: {e}")

# ---------------- EMAIL FUNCTION ----------------
def send_email_with_attachment(sender_email, sender_password, recipient_email, subject, body, attachment_paths):
    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.set_content(body)
    for attachment_path in attachment_paths:
        try:
            with open(attachment_path, "rb") as f:
                file_data = f.read()
                maintype, subtype = mimetypes.guess_type(attachment_path)[0].split('/')
                msg.add_attachment(file_data, maintype=maintype, subtype=subtype, filename=os.path.basename(attachment_path))
        except Exception as e:
            logging.error(f"Error attaching file {attachment_path}: {e}")
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        logging.info(f"Email sent to {recipient_email} with attachments: {attachment_paths}")
    except Exception as e:
        logging.error(f"Email sending error: {e}")

# ---------------- FILE SYSTEM WATCHER ----------------
class FileWatcher(FileSystemEventHandler):
    def __init__(self, folders, project_id, sender_email, sender_password, recipient_email):
        self.folders = folders
        self.project_id = project_id
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipient_email = recipient_email
        self.output_csv = "scan_results.csv"
        self.entities_csv = "named_entities.csv"

    def on_created(self, event):
        if event.is_directory:
            return
        self.process_file(event.src_path)

    def on_modified(self, event):
        if event.is_directory:
            return
        self.process_file(event.src_path)

    def process_file(self, file_path):
        logging.info(f"Processing file: {file_path}")
        file_name = os.path.basename(file_path)
        text = get_text_from_file(file_path)
        if not text:
            logging.warning(f"No text extracted from {file_name}")
            return
        sentiment = analyze_sentiment(text)
        named_entities = extract_named_entities(text)
        pii_results = dlp_custom_scan(text, self.project_id)
        save_to_csv(file_name, pii_results, sentiment, named_entities, self.output_csv)
        save_named_entities_to_csv(file_name, named_entities, self.entities_csv)
        if pii_results:  # Send email only if PII is detected
            send_email_with_attachment(
                self.sender_email,
                self.sender_password,
                self.recipient_email,
                subject=f"PII Detected in {file_name}",
                body=f"Hi,\n\nPII was detected in {file_name}. See attached reports.\n\nRegards,\nDLP Scanner",
                attachment_paths=[self.output_csv, self.entities_csv]
            )

# ---------------- WINDOWS SERVICE ----------------
import win32serviceutil
import win32service
import win32event
import servicemanager

class PIIScannerService(win32serviceutil.ServiceFramework):
    _svc_name_ = "PIIScannerService"
    _svc_display_name_ = "PII Scanner Service"
    _svc_description_ = "Monitors folders for PII in files and generates reports."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.observer = None
        self.running = False

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.running = False
        if self.observer:
            self.observer.stop()
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def main(self):
        self.running = True
        folders_to_monitor = ["C:/Users/THlophe/Downloads/Test doc"]  # Add your folders here
        project_id = "eswatinidlp-pii"  # Replace with your GCP project ID
        sender_email = "your_email@gmail.com"  # Replace with your email
        sender_password = "your_app_password"  # Replace with Gmail App Password
        recipient_email = "recipient@example.com"  # Replace with recipient

        event_handler = FileWatcher(folders_to_monitor, project_id, sender_email, sender_password, recipient_email)
        self.observer = Observer()
        for folder in folders_to_monitor:
            if os.path.isdir(folder):
                self.observer.schedule(event_handler, folder, recursive=False)
                logging.info(f"Monitoring folder: {folder}")
            else:
                logging.error(f"Folder not found: {folder}")

        self.observer.start()
        try:
            while self.running:
                time.sleep(1)
        except Exception as e:
            logging.error(f"Service error: {e}")
        self.observer.stop()
        self.observer.join()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(PIIScannerService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(PIIScannerService)