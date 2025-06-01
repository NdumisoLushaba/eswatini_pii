import os
import sys
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
import tkinter as tk
from tkinter import ttk, filedialog
from threading import Thread
import queue
import win32serviceutil
import win32service
import win32event
import servicemanager
from transformers import pipeline, AutoTokenizer

# Configure logging
logging.basicConfig(
    filename="pii_scanner.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize NLTK and spaCy
nltk.download('vader_lexicon', quiet=True)
sia = SentimentIntensityAnalyzer()
nlp = spacy.load("en_core_web_sm")

# Add Siswati-specific NER
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

# Load Siswati tokenizer (optional, if available)
try:
    siswati_tokenizer = AutoTokenizer.from_pretrained("your-username/siswati_tokenizer")
except Exception as e:
    logging.warning(f"Could not load Siswati tokenizer: {e}. Falling back to spaCy NER.")

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
def dlp_custom_scan(text, project_id="eswatinidlp-pii"):
    try:
        dlp = dlp_v2.DlpServiceClient()
        parent = f"projects/{project_id}"
        
        # Custom info types
        custom_info_types = [
            types.CustomInfoType(
                info_type=types.InfoType(name="ESWATINI_ID"),
                regex=types.CustomInfoType.Regex(pattern=r"\b\d{2}-\d{6}-[A-Z]-\d{2}\b"),
                likelihood=types.Likelihood.LIKELY
            ),
            types.CustomInfoType(
                info_type=types.InfoType(name="DRIVERS_LICENSE"),
                regex=types.CustomInfoType.Regex(pattern=r"\bDL-\d{8,10}\b"),
                likelihood=types.Likelihood.LIKELY
            ),
            types.CustomInfoType(
                info_type=types.InfoType(name="PASSPORT_NUMBER"),
                regex=types.CustomInfoType.Regex(pattern=r"\bP\d{7,10}\b"),
                likelihood=types.Likelihood.LIKELY
            ),
            types.CustomInfoType(
                info_type=types.InfoType(name="BANK_ACCOUNT_NUMBER"),
                regex=types.CustomInfoType.Regex(pattern=r"\b\d{10,20}\b"),
                likelihood=types.Likelihood.LIKELY
            ),
            types.CustomInfoType(
                info_type=types.InfoType(name="CREDIT_CARD_NUMBER"),
                regex=types.CustomInfoType.Regex(pattern=r"\b\d{13,16}\b"),
                likelihood=types.Likelihood.LIKELY
            ),
            types.CustomInfoType(
                info_type=types.InfoType(name="SISWATI_NAME"),
                dictionary=types.CustomInfoType.Dictionary(
                    word_list=types.CustomInfoType.Dictionary.WordList(words=["Sipho", "Thembumenzi", "Nomsa", "Thuli", "Bongani"])
                ),
                likelihood=types.Likelihood.LIKELY
            ),
        ]
        
        inspect_config = types.InspectConfig(
            custom_info_types=custom_info_types,
            include_quote=True
        )
        item = {"value": text}
        response = dlp.inspect_content(
            request={"parent": parent, "inspect_config": inspect_config, "item": item}
        )
        findings = [
            {"info_type": finding.info_type.name, "match": finding.quote, "likelihood": finding.likelihood.name, "line": finding.location.content_locations[0].byte_range.start if finding.location.content_locations else "N/A"}
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
    def __init__(self, folders, project_id, sender_email, sender_password, recipient_email, queue=None):
        self.folders = folders
        self.project_id = project_id
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipient_email = recipient_email
        self.output_csv = "scan_results.csv"
        self.entities_csv = "named_entities.csv"
        self.queue = queue

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
        if self.queue:
            self.queue.put({"type": "file_scanned"})
            for pii in pii_results:
                self.queue.put({
                    "type": "pii_detected",
                    "pii_type": pii["info_type"],
                    "file_name": file_name,
                    "line": pii["line"]
                })
        if pii_results:
            send_email_with_attachment(
                self.sender_email,
                self.sender_password,
                self.recipient_email,
                subject=f"PII Detected in {file_name}",
                body=f"Hi,\n\nPII was detected in {file_name}. See attached reports.\n\nRegards,\nDLP Scanner",
                attachment_paths=[self.output_csv, self.entities_csv]
            )

# ---------------- SCAN FOLDER FUNCTION ----------------
def scan_folder(queue, folder_path, project_id="eswatinidlp-pii", sender_email="your_email@gmail.com", sender_password="your_app_password", recipient_email="recipient@example.com"):
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            logging.info(f"Scanning file: {file_path}")
            file_name = os.path.basename(file_path)
            text = get_text_from_file(file_path)
            if not text:
                logging.warning(f"No text extracted from {file_name}")
                continue
            sentiment = analyze_sentiment(text)
            named_entities = extract_named_entities(text)
            pii_results = dlp_custom_scan(text, project_id)
            save_to_csv(file_name, pii_results, sentiment, named_entities)
            save_named_entities_to_csv(file_name, named_entities)
            queue.put({"type": "file_scanned"})
            for pii in pii_results:
                queue.put({
                    "type": "pii_detected",
                    "pii_type": pii["info_type"],
                    "file_name": file_name,
                    "line": pii["line"]
                })
            if pii_results:
                send_email_with_attachment(
                    sender_email,
                    sender_password,
                    recipient_email,
                    subject=f"PII Detected in {file_name}",
                    body=f"Hi,\n\nPII was detected in {file_name}. See attached reports.\n\nRegards,\nDLP Scanner",
                    attachment_paths=["scan_results.csv", "named_entities.csv"]
                )

# ---------------- WINDOWS SERVICE ----------------
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
        folders_to_monitor = ["C:/Users/THlophe/Downloads/Test doc"]  # Update as needed
        project_id = "eswatinidlp-pii"
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

# ---------------- DASHBOARD ----------------
class PIIDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("🔒 PII Scanner Dashboard")
        self.root.geometry("800x500")
        self.root.configure(bg="#f4f4f4")
        self.scan_running = False
        self.file_count = 0
        self.queue = queue.Queue()

        # Header Frame
        header = tk.Frame(root, bg="#2c3e50", height=50)
        header.pack(fill="x")
        title = tk.Label(header, text="PII Scanner Dashboard", bg="#2c3e50", fg="white", font=("Segoe UI", 16, "bold"))
        title.pack(pady=10)

        # Folder selection Frame
        folder_frame = tk.Frame(root, bg="#f4f4f4")
        folder_frame.pack(fill="x", padx=20, pady=(5, 10))
        tk.Label(folder_frame, text="Folder to scan:", font=("Segoe UI", 11), bg="#f4f4f4").pack(side="left")
        self.folder_path = tk.StringVar(value="No folder selected")
        tk.Label(folder_frame, textvariable=self.folder_path, font=("Segoe UI", 10), bg="#f4f4f4", fg="blue").pack(side="left", padx=(5, 10))
        select_folder_btn = tk.Button(folder_frame, text="Select Folder", command=self.select_folder, font=("Segoe UI", 10))
        select_folder_btn.pack(side="left")

        # Info Frame
        info_frame = tk.Frame(root, bg="#f4f4f4")
        info_frame.pack(fill="x", padx=20, pady=(10, 0))
        self.status_label = tk.Label(info_frame, text="Status: Idle", font=("Segoe UI", 11), bg="#f4f4f4")
        self.status_label.pack(side="left", padx=(0, 20))
        self.file_label = tk.Label(info_frame, text="Files Scanned: 0", font=("Segoe UI", 11), bg="#f4f4f4")
        self.file_label.pack(side="left")

        # Treeview Frame
        tree_frame = tk.Frame(root)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        columns = ("type", "file", "line")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)
        for col, text, width in (
            ("type", "PII Type", 120),
            ("file", "File Name", 500),
            ("line", "Line #", 80),
        ):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="center" if col == "line" else "w")
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Control Button
        self.toggle_btn = tk.Button(root, text="Start Scan", command=self.toggle_scan, width=20, bg="#27ae60", fg="white", font=("Segoe UI", 11, "bold"), relief="flat", height=2)
        self.toggle_btn.pack(pady=10)

        self.root.after(1000, self.update_from_queue)

    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)
            self.file_count = 0
            self.file_label.config(text="Files Scanned: 0")
            for row in self.tree.get_children():
                self.tree.delete(row)

    def toggle_scan(self):
        self.scan_running = not self.scan_running
        if self.scan_running:
            self.toggle_btn.config(text="Pause Scan", bg="#e74c3c")
            self.status_label.config(text="Status: Scanning...")
            self.scan_thread = Thread(target=self.scan_loop, daemon=True)
            self.scan_thread.start()
        else:
            self.toggle_btn.config(text="Start Scan", bg="#27ae60")
            self.status_label.config(text="Status: Paused")

    def scan_loop(self):
        while self.scan_running:
            folder_to_scan = self.folder_path.get()
            if folder_to_scan and folder_to_scan != "No folder selected":
                scan_folder(self.queue, folder_to_scan)
            time.sleep(10)

    def update_from_queue(self):
        try:
            while True:
                item = self.queue.get_nowait()
                if item["type"] == "file_scanned":
                    self.file_count += 1
                    self.file_label.config(text=f"Files Scanned: {self.file_count}")
                elif item["type"] == "pii_detected":
                    self.tree.insert("", "end", values=(item["pii_type"], item["file_name"], item["line"]))
        except queue.Empty:
            pass
        finally:
            self.root.after(1000, self.update_from_queue)

# ---------------- MAIN ----------------
if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run as Windows service
        win32serviceutil.HandleCommandLine(PIIScannerService)
    else:
        # Run dashboard
        root = tk.Tk()
        app = PIIDashboard(root)
        root.mainloop()