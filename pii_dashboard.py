import tkinter as tk
from tkinter import ttk, filedialog
from threading import Thread
import queue
import time

class PIIDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("🔒 PII Scanner Dashboard")
        self.root.geometry("800x500")
        self.root.configure(bg="#f4f4f4")

        self.scan_running = False
        self.file_count = 0
        self.queue = queue.Queue()

        # ----- Header Frame -----
        header = tk.Frame(root, bg="#2c3e50", height=50)
        header.pack(fill="x")

        title = tk.Label(header,
                         text="PII Scanner Dashboard",
                         bg="#2c3e50",
                         fg="white",
                         font=("Segoe UI", 16, "bold"))
        title.pack(pady=10)

        # ----- Folder selection Frame -----
        folder_frame = tk.Frame(root, bg="#f4f4f4")
        folder_frame.pack(fill="x", padx=20, pady=(5, 10))

        tk.Label(folder_frame,
                 text="Folder to scan:",
                 font=("Segoe UI", 11),
                 bg="#f4f4f4").pack(side="left")

        self.folder_path = tk.StringVar(value="No folder selected")
        tk.Label(folder_frame,
                 textvariable=self.folder_path,
                 font=("Segoe UI", 10),
                 bg="#f4f4f4",
                 fg="blue").pack(side="left", padx=(5, 10))

        select_folder_btn = tk.Button(folder_frame,
                                      text="Select Folder",
                                      command=self.select_folder,
                                      font=("Segoe UI", 10))
        select_folder_btn.pack(side="left")

        # ----- Info Frame -----
        info_frame = tk.Frame(root, bg="#f4f4f4")
        info_frame.pack(fill="x", padx=20, pady=(10, 0))

        self.status_label = tk.Label(info_frame,
                                     text="Status: Idle",
                                     font=("Segoe UI", 11),
                                     bg="#f4f4f4")
        self.status_label.pack(side="left", padx=(0, 20))

        self.file_label = tk.Label(info_frame,
                                   text="Files Scanned: 0",
                                   font=("Segoe UI", 11),
                                   bg="#f4f4f4")
        self.file_label.pack(side="left")

        # ----- Treeview Frame -----
        tree_frame = tk.Frame(root)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("type", "file", "line")
        self.tree = ttk.Treeview(tree_frame,
                                 columns=columns,
                                 show="headings",
                                 height=12)
        for col, text, width in (
            ("type", "PII Type", 120),
            ("file", "File Name", 500),
            ("line", "Line #", 80),
        ):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width,
                             anchor="center" if col == "line" else "w")
        self.tree.pack(side="left", fill="both", expand=True)

        # ——— Proper Scrollbar Hookup ———
        scrollbar = ttk.Scrollbar(tree_frame,
                                  orient="vertical",
                                  command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # ----- Control Button -----
        self.toggle_btn = tk.Button(root,
                                    text="Start Scan",
                                    command=self.toggle_scan,
                                    width=20,
                                    bg="#27ae60",
                                    fg="white",
                                    font=("Segoe UI", 11, "bold"),
                                    relief="flat",
                                    height=2)
        self.toggle_btn.pack(pady=10)

        self.root.after(1000, self.update_from_queue)

    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)
            self.file_count = 0
            self.file_label.config(text="Files Scanned: 0")
            # clear any previous results
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
        from detect_eswatini_id_Email_DashboardLandingPage import scan_folder
        while self.scan_running:
            folder_to_scan = self.folder_path.get()
            if folder_to_scan and folder_to_scan != "No folder selected":
                scan_folder(queue=self.queue, folder_path=folder_to_scan)
            time.sleep(10)

    def update_from_queue(self):
        try:
            while True:
                item = self.queue.get_nowait()
                if item["type"] == "file_scanned":
                    self.file_count += 1
                    self.file_label.config(text=f"Files Scanned: {self.file_count}")
                elif item["type"] == "pii_detected":
                    self.tree.insert("", "end",
                                     values=(item["pii_type"],
                                             item["file_name"],
                                             item["line"]))
        except queue.Empty:
            pass
        finally:
            self.root.after(1000, self.update_from_queue)


if __name__ == "__main__":
    root = tk.Tk()
    app = PIIDashboard(root)
    root.mainloop()
