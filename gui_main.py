import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
import ttkbootstrap as ttk
import csv
from ttkbootstrap.constants import *
import database
import app_config as config
from models import Vehicle, Customer, ServiceRecord, Attachment, TestDrive, Part, Document
from datetime import datetime
import os
import shutil
import webbrowser
import calendar
import zipfile
import email_utils
import requests
from pdf_generator import PDFGenerator

CURRENT_VERSION = "1.0.1"

import sys
import ctypes

try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("carmanager.pro.app.1.0")
except Exception:
    pass

class LoginDialog:
    def __init__(self, parent):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Login - CAR Manager Pro")
        self.dialog.geometry("300x180")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        
        # Center
        self.dialog.update_idletasks()
        width = 300
        height = 180
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        ttk.Label(self.dialog, text="🔒 Geschützter Bereich", font=("Helvetica", 12, "bold")).pack(pady=15)
        ttk.Label(self.dialog, text="Bitte Passwort eingeben:", font=("Helvetica", 10)).pack(pady=5)
        
        self.password_var = tk.StringVar()
        self.entry = ttk.Entry(self.dialog, show="*", textvariable=self.password_var)
        self.entry.pack(pady=5, padx=40, fill="x")
        self.entry.focus_set()
        
        ttk.Button(self.dialog, text="Anmelden", command=self.check_login, style="primary.TButton").pack(pady=15)
        
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_close)
        self.entry.bind("<Return>", lambda e: self.check_login())
        
        self.success = False
        self.parent.wait_window(self.dialog)

    def check_login(self):
        pwd = self.password_var.get()
        stored_pwd = database.get_setting('admin_password', 'admin')
        
        if pwd == stored_pwd:
            self.success = True
            self.dialog.destroy()
        else:
            messagebox.showerror("Zugriff verweigert", "Falsches Passwort!")
            self.entry.delete(0, 'end')

    def on_close(self):
        self.dialog.destroy()

class CarManagerApp:
    def __init__(self, root):
        self.root = root
        
        # Login Check
        self.root.withdraw()
        login = LoginDialog(self.root)
        if not login.success:
            self.root.destroy()
            sys.exit()
        self.root.deiconify()
        
        self.root.title("CAR Manager Pro")
        self.root.geometry("1200x800")
        
        # Set Window Icon
        try:
            if getattr(sys, 'frozen', False):
                # Running as compiled exe
                application_path = sys._MEIPASS
            else:
                # Running as script
                application_path = os.path.dirname(os.path.abspath(__file__))
            
            icon_path = os.path.join(application_path, 'app_icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Icon load warning: {e}")
        
        self.pdf_gen = PDFGenerator()
        
        # Style (handled by ttkbootstrap Window)
        
        self.tab_control = ttk.Notebook(root)
        
        self.tab_dashboard = ttk.Frame(self.tab_control)
        self.tab_inventory = ttk.Frame(self.tab_control)
        self.tab_customers = ttk.Frame(self.tab_control)
        self.tab_workshop = ttk.Frame(self.tab_control)
        self.tab_test_drives = ttk.Frame(self.tab_control)
        self.tab_parts = ttk.Frame(self.tab_control)
        self.tab_documents = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.tab_dashboard, text='📊 Dashboard')
        self.tab_control.add(self.tab_inventory, text='🚗 Fahrzeugbestand')
        self.tab_control.add(self.tab_customers, text='👥 Kunden')
        self.tab_control.add(self.tab_workshop, text='🛠️ Werkstatt')
        self.tab_control.add(self.tab_test_drives, text='🏁 Probefahrten')
        self.tab_control.add(self.tab_parts, text='🔧 Ersatzteile')
        self.tab_control.add(self.tab_documents, text='📄 Dokumente')
        
        self.tab_calendar = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_calendar, text='📅 Kalender')

        self.tab_settings = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_settings, text='⚙️ Einstellungen')
        
        self.tab_control.pack(expand=1, fill="both")
        
        self.create_menu()
        
        # Init Tabs
        self.setup_dashboard()
        self.setup_inventory()
        self.setup_customers()
        self.setup_workshop()
        self.setup_test_drives()
        self.setup_parts()
        self.setup_documents()
        self.setup_calendar()
        self.setup_settings()
        
        # Initial Data Load
        self.refresh_all()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        # Auto-backup on exit
        try:
            backup_path = database.backup_database()
            if backup_path:
                print(f"Backup successful: {backup_path}")
        except Exception as e:
            print(f"Backup error: {e}")
        
        self.root.destroy()

    def run_tutorial(self):
        # Step 1: Welcome
        if not messagebox.askyesno("Tutorial", "Möchten Sie das Tutorial starten?"):
            return
            
        # Step 2: Dashboard
        self.tab_control.select(self.tab_dashboard)
        self.root.update()
        messagebox.showinfo("Tutorial: Dashboard", 
            "Das ist das Dashboard.\n\n"
            "Hier sehen Sie:\n"
            "- Wichtige Statistiken (Fahrzeuge, Umsatz, Gewinn)\n"
            "- Eine To-Do Liste für heute\n"
            "- Schnellzugriff-Buttons für neue Einträge\n"
            "- Umsatzverlauf des aktuellen Jahres")
            
        # Step 3: Inventory
        self.tab_control.select(self.tab_inventory)
        self.root.update()
        messagebox.showinfo("Tutorial: Fahrzeugbestand", 
            "Hier verwalten Sie Ihren Fahrzeugbestand.\n\n"
            "- Klicken Sie auf 'Neues Fahrzeug', um ein Auto hinzuzufügen.\n"
            "- Mit Rechtsklick auf ein Fahrzeug öffnen Sie das Kontextmenü (Bearbeiten, Exposé).\n"
            "- Doppelklick öffnet die Details.")

        # Step 4: Customers
        self.tab_control.select(self.tab_customers)
        self.root.update()
        messagebox.showinfo("Tutorial: Kunden", 
            "Verwalten Sie hier Ihre Kundendaten.\n\n"
            "Sie können Kunden anlegen, bearbeiten und direkt Emails senden.")
            
        # Step 6: Workshop
        self.tab_control.select(self.tab_workshop)
        self.root.update()
        messagebox.showinfo("Tutorial: Werkstatt", 
            "Planen Sie Werkstatt-Aufenthalte.\n\n"
            "- Service-Einträge erstellen\n"
            "- Reparaturkosten erfassen\n"
            "- Historie pro Fahrzeug einsehen")
            
        # Step 7: Settings
        self.tab_control.select(self.tab_settings)
        self.root.update()
        messagebox.showinfo("Tutorial: Einstellungen", 
            "Hier konfigurieren Sie das Programm:\n\n"
            "- Firmendaten für Verträge\n"
            "- Lizenzschlüssel eingeben\n"
            "- Email-Server (SMTP) einrichten\n"
            "- Datenbank-Backup erstellen")
            
        # End
        self.tab_control.select(self.tab_dashboard)
        messagebox.showinfo("Tutorial Beendet", "Das war der Überblick! Viel Erfolg mit CAR Manager Pro.")

    def refresh_all(self):
        self.update_dashboard()
        self.load_inventory()
        self.load_customers()
        self.load_workshop()
        self.load_test_drives()
        self.load_parts()
        self.load_documents()

    def _on_right_click(self, event, tree, menu):
        item = tree.identify_row(event.y)
        if item:
            tree.selection_set(item)
            menu.tk_popup(event.x_root, event.y_root)

    # --- DASHBOARD ---
    def setup_dashboard(self):
        self.dash_frame = ttk.Frame(self.tab_dashboard, padding=20)
        self.dash_frame.pack(fill="both", expand=True)
        
        ttk.Label(self.dash_frame, text="Willkommen im CAR Manager", font=("Helvetica", 24)).pack(pady=10)
        
        self.stats_frame = ttk.Frame(self.dash_frame)
        self.stats_frame.pack(fill="x", pady=10)
        
        self.lbl_total_cars = ttk.Label(self.stats_frame, text="Fahrzeuge: 0", font=("Helvetica", 14))
        self.lbl_total_cars.pack(side="left", padx=20)
        
        self.lbl_total_value = ttk.Label(self.stats_frame, text="Gesamtwert: 0.00 €", font=("Helvetica", 14))
        self.lbl_total_value.pack(side="left", padx=20)
        
        # Quick Actions
        qa_frame = ttk.Labelframe(self.dash_frame, text="Schnellzugriff", padding=10)
        qa_frame.pack(fill="x", pady=10, padx=20)

        btn_style = "info.TButton" 
        
        ttk.Button(qa_frame, text="➕ Neues Fahrzeug", style=btn_style, width=20, 
                   command=lambda: self.open_vehicle_dialog(None)).pack(side="left", padx=10)
        
        ttk.Button(qa_frame, text="👤 Neuer Kunde", style=btn_style, width=20,
                   command=lambda: self.open_customer_dialog(None)).pack(side="left", padx=10)
                   
        ttk.Button(qa_frame, text="🏁 Neue Probefahrt", style=btn_style, width=20,
                   command=self.open_test_drive_dialog).pack(side="left", padx=10)
                   
        ttk.Button(qa_frame, text="📧 Email senden", style=btn_style, width=20,
                   command=lambda: self.open_email_dialog()).pack(side="left", padx=10)

        # Content Frame (Todos & Chart)
        content_frame = ttk.Frame(self.dash_frame)
        content_frame.pack(fill="both", expand=True, padx=20, pady=5)
        
        # Left: To-Do
        todo_frame = ttk.Labelframe(content_frame, text="📅 To-Do Liste (Heute)", padding=10)
        todo_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.todo_list = tk.Listbox(todo_frame, font=("Segoe UI", 10), height=8, activestyle='none')
        self.todo_list.pack(fill="both", expand=True)

    def update_dashboard(self):
        stats = database.get_stats()
        
        self.lbl_total_cars.config(text=f"Fahrzeuge: {stats['total_count']}")
        self.lbl_total_value.config(text=f"Gesamtwert: {stats['total_value']:,.2f} €")
        
        # Update To-Do
        self.todo_list.delete(0, "end")
        today = datetime.now().strftime("%Y-%m-%d")
        todos = database.get_todos_for_date(today)
        
        # Check Parts Low Stock
        try:
            parts = database.get_parts()
            low_stock = [p for p in parts if p.quantity <= p.min_quantity]
            for p in low_stock:
                 todos.insert(0, {"type": "Bestand", "text": f"Nachbestellen: {p.name} ({p.quantity} Stk)", "id": p.id})
        except:
            pass

        if not todos:
            self.todo_list.insert("end", "Keine Aufgaben für heute.")
            self.todo_list.config(fg="gray")
        else:
            self.todo_list.config(fg="black")
            for t in todos:
                self.todo_list.insert("end", f"[{t['type']}] {t['text']}")
                if t['type'] == 'TÜV': self.todo_list.itemconfig("end", {'bg': '#ffeebb', 'fg': 'black'})
                if t['type'] == 'Service': self.todo_list.itemconfig("end", {'bg': '#eebbff', 'fg': 'black'})
                if t['type'] == 'Probefahrt': self.todo_list.itemconfig("end", {'bg': '#bbeeaa', 'fg': 'black'})
                if t['type'] == 'Bestand': self.todo_list.itemconfig("end", {'bg': '#ffcccc', 'fg': 'black'})

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Datei", menu=file_menu)
        file_menu.add_command(label="Backup erstellen", command=self.backup_data)
        file_menu.add_separator()
        file_menu.add_command(label="Einstellungen", command=self.open_settings_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Beenden", command=self.on_closing)

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Hilfe", menu=help_menu)
        help_menu.add_command(label="Tutorial starten", command=self.run_tutorial)

    def backup_data(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backup_{timestamp}.zip"
            save_path = filedialog.asksaveasfilename(defaultextension=".zip", initialfile=filename, filetypes=[("ZIP files", "*.zip")])
            
            if not save_path:
                return

            import zipfile
            with zipfile.ZipFile(save_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add Database
                if os.path.exists(database.DB_NAME):
                    zipf.write(database.DB_NAME, arcname=os.path.basename(database.DB_NAME))
                
                # Add Uploads
                uploads_dir = config.get_uploads_path()
                if os.path.exists(uploads_dir):
                    for root, dirs, files in os.walk(uploads_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.join("uploads", os.path.relpath(file_path, uploads_dir))
                            zipf.write(file_path, arcname=arcname)
            
            messagebox.showinfo("Erfolg", f"Backup erfolgreich erstellt:\n{save_path}")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Backup fehlgeschlagen: {e}")

    def open_settings_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Einstellungen")
        dialog.geometry("500x400")
        
        ttk.Label(dialog, text="SMTP Email Einstellungen", font=("Helvetica", 12, "bold")).pack(pady=10)
        
        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill="both", expand=True)
        
        fields = [("SMTP Server", "smtp_server"), ("SMTP Port", "smtp_port"), 
                  ("Benutzer (Email)", "smtp_user"), ("Passwort", "smtp_password")]
        entries = {}
        
        for i, (label, key) in enumerate(fields):
            ttk.Label(frame, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="e")
            entry = ttk.Entry(frame, show="*" if "password" in key else "")
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            
            # Load existing value
            val = database.get_setting(key, "")
            entry.insert(0, val)
            entries[key] = entry
            
        # Help Button in the frame
        ttk.Button(frame, text="❓ Hilfe / Provider Info", command=self.open_smtp_help_dialog).grid(row=len(fields), column=1, sticky="w", pady=10)

        def save_settings():
            for key, entry in entries.items():
                database.set_setting(key, entry.get())
            messagebox.showinfo("Erfolg", "Einstellungen gespeichert.")
            dialog.destroy()
            
        def test_settings():
            settings = {
                'server': entries['smtp_server'].get(),
                'port': entries['smtp_port'].get(),
                'user': entries['smtp_user'].get(),
                'password': entries['smtp_password'].get()
            }
            success, msg = email_utils.test_smtp_connection(settings)
            if success:
                messagebox.showinfo("Erfolg", msg)
            else:
                messagebox.showerror("Fehler", f"Verbindung fehlgeschlagen: {msg}")

        btn_frame = ttk.Frame(dialog, padding=10)
        btn_frame.pack(fill="x")
        
        ttk.Button(btn_frame, text="Verbindung testen", command=test_settings).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Speichern", command=save_settings).pack(side="right", padx=5)

    def open_smtp_help_dialog(self):
        help_win = tk.Toplevel(self.root)
        help_win.title("SMTP Hilfe & Provider Einstellungen")
        help_win.geometry("600x600")
        
        text_area = tk.Text(help_win, wrap="word", padx=15, pady=15, font=("Segoe UI", 10))
        scrollbar = ttk.Scrollbar(help_win, orient="vertical", command=text_area.yview)
        text_area.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        text_area.pack(fill="both", expand=True)
        
        # Tags for formatting
        text_area.tag_configure("h1", font=("Segoe UI", 14, "bold"), spacing3=10)
        text_area.tag_configure("h2", font=("Segoe UI", 11, "bold"), spacing3=5)
        text_area.tag_configure("bold", font=("Segoe UI", 10, "bold"))
        
        content = [
            ("Allgemeine Hilfe", "h1"),
            ("Damit Sie Emails direkt aus dem CAR Manager senden können, müssen Sie die SMTP-Zugangsdaten Ihres Email-Anbieters hinterlegen.\n\n", None),
            ("WICHTIG für Google Mail (Gmail):", "h2"),
            ("Da Google die Anmeldung mit dem normalen Passwort für Drittanbieter-Apps oft blockiert, müssen Sie ein sog. 'App-Passwort' erstellen:\n"
             "1. Loggen Sie sich bei Google ein und gehen Sie zu 'Google Konto verwalten'.\n"
             "2. Gehen Sie zu 'Sicherheit' -> 'Bestätigung in zwei Schritten' (muss aktiviert sein).\n"
             "3. Suchen Sie nach 'App-Passwörter'.\n"
             "4. Erstellen Sie ein neues App-Passwort (Name z.B. 'CarManager').\n"
             "5. Nutzen Sie dieses generierte Passwort hier in den Einstellungen (NICHT Ihr normales Login-Passwort!).\n\n", None),
             
            ("Gängige Anbieter & Einstellungen:", "h1"),
            
            ("Google Mail (Gmail)", "h2"),
            ("Server: smtp.gmail.com\n"
             "Port: 587\n"
             "Benutzer: Ihre Email-Adresse\n"
             "Passwort: Ihr App-Passwort (siehe oben)\n\n", None),
             
            ("Outlook / Hotmail / Office365", "h2"),
            ("Server: smtp.office365.com\n"
             "Port: 587\n"
             "Benutzer: Ihre Email-Adresse\n"
             "Passwort: Ihr Email-Passwort\n\n", None),
             
            ("GMX", "h2"),
            ("Server: mail.gmx.net\n"
             "Port: 587\n"
             "Benutzer: Ihre Kundennummer oder Email-Adresse\n"
             "Passwort: Ihr Email-Passwort\n"
             "(Hinweis: 'SMTP-Versand' muss in den GMX-Einstellungen im Webbrowser ggf. erst aktiviert werden!)\n\n", None),
             
            ("WEB.DE", "h2"),
            ("Server: smtp.web.de\n"
             "Port: 587\n"
             "Benutzer: Ihre Email-Adresse\n"
             "Passwort: Ihr Email-Passwort\n"
             "(Hinweis: Auch hier muss der SMTP-Versand oft erst in den Einstellungen aktiviert werden.)\n\n", None),
             
            ("Yahoo Mail", "h2"),
            ("Server: smtp.mail.yahoo.com\n"
             "Port: 465 (oder 587)\n"
             "Benutzer: Ihre Email-Adresse\n"
             "Passwort: Oft ist auch hier ein 'App-Passwort' nötig (ähnlich wie bei Google).\n\n", None),
             
            ("1&1 / Ionos", "h2"),
            ("Server: smtp.ionos.de\n"
             "Port: 587\n"
             "Benutzer: Ihre Email-Adresse\n"
             "Passwort: Ihr Email-Passwort\n\n", None),
             
            ("T-Online (Telekom)", "h2"),
            ("Server: securesmtp.t-online.de\n"
             "Port: 587\n"
             "Benutzer: Ihre Email-Adresse\n"
             "Passwort: Ein spezielles 'E-Mail-Passwort' (nicht das Login-Passwort für das Kundencenter).\n\n", None),

            ("iCloud (Apple)", "h2"),
            ("Server: smtp.mail.me.com\n"
             "Port: 587\n"
             "Benutzer: Ihre iCloud Email-Adresse\n"
             "Passwort: Ein anwendungsspezifisches Passwort (erforderlich!).\n\n", None),

            ("Freenet", "h2"),
            ("Server: mx.freenet.de\n"
             "Port: 587\n"
             "Benutzer: Ihre Email-Adresse\n"
             "Passwort: Ihr Email-Passwort\n"
             "(Hinweis: SMTP-Versand muss in den Einstellungen aktiviert sein.)\n\n", None),

            ("Strato", "h2"),
            ("Server: smtp.strato.de\n"
             "Port: 465 (oder 587)\n"
             "Benutzer: Ihre Email-Adresse\n"
             "Passwort: Ihr Email-Passwort\n\n", None),

            ("AOL", "h2"),
            ("Server: smtp.aol.com\n"
             "Port: 587\n"
             "Benutzer: Ihre Email-Adresse\n"
             "Passwort: Ein App-Passwort (erforderlich).\n\n", None),

            ("Vodafone / Arcor", "h2"),
            ("Server: mail.arcor.de (oder smtp.vodafonemail.de)\n"
             "Port: 587\n"
             "Benutzer: Ihre Email-Adresse\n"
             "Passwort: Ihr Email-Passwort\n\n", None),

            ("HostEurope", "h2"),
            ("Server: mail.your-server.de (allgemein)\n"
             "Port: 587\n"
             "Benutzer: Ihre Email-Adresse\n"
             "Passwort: Ihr Email-Passwort\n\n", None),

            ("All-Inkl", "h2"),
            ("Server: <Ihre-Domain>.de (oder kasserver.com)\n"
             "Port: 587\n"
             "Benutzer: Ihre Email-Adresse\n"
             "Passwort: Ihr Email-Passwort\n\n", None),

            ("Posteo", "h2"),
            ("Server: posteo.de\n"
             "Port: 587\n"
             "Benutzer: Ihre Email-Adresse\n"
             "Passwort: Ihr Email-Passwort\n\n", None),

            ("Mailbox.org", "h2"),
            ("Server: smtp.mailbox.org\n"
             "Port: 465 (oder 587)\n"
             "Benutzer: Ihre Email-Adresse\n"
             "Passwort: Ihr Email-Passwort\n\n", None),

            ("Zoho Mail", "h2"),
            ("Server: smtp.zoho.eu (oder .com)\n"
             "Port: 465\n"
             "Benutzer: Ihre Email-Adresse\n"
             "Passwort: Ihr Email-Passwort (oder App-Passwort bei 2FA)\n\n", None),

            ("Mail.com", "h2"),
            ("Server: smtp.mail.com\n"
             "Port: 587\n"
             "Benutzer: Ihre Email-Adresse\n"
             "Passwort: Ihr Email-Passwort\n\n", None),

            ("DomainFactory", "h2"),
            ("Server: smtps.df.eu\n"
             "Port: 465 (oder 587)\n"
             "Benutzer: Ihre Email-Adresse\n"
             "Passwort: Ihr Email-Passwort\n\n", None),

            ("O2 / Alice", "h2"),
            ("Server: mail.o2online.de\n"
             "Port: 587\n"
             "Benutzer: Ihre Email-Adresse\n"
             "Passwort: Ihr Email-Passwort\n\n", None)
        ]
        
        for text, tag in content:
            if tag:
                text_area.insert("end", text + "\n", tag)
            else:
                text_area.insert("end", text)
                
        text_area.configure(state="disabled")

    def open_email_dialog(self, to_email="", subject="", body="", attachment_path=None):
        dialog = tk.Toplevel(self.root)
        dialog.title("Email senden")
        dialog.geometry("500x500")
        
        ttk.Label(dialog, text="Empfänger:").pack(anchor="w", padx=10, pady=(10,0))
        
        frame_to = ttk.Frame(dialog)
        frame_to.pack(fill="x", padx=10, pady=5)
        entry_to = ttk.Entry(frame_to)
        entry_to.insert(0, to_email)
        entry_to.pack(side="left", fill="x", expand=True)
        self.create_copy_button(frame_to, entry_to).pack(side="left", padx=5)
        
        ttk.Label(dialog, text="Betreff:").pack(anchor="w", padx=10)
        
        frame_sub = ttk.Frame(dialog)
        frame_sub.pack(fill="x", padx=10, pady=5)
        entry_subject = ttk.Entry(frame_sub)
        entry_subject.insert(0, subject)
        entry_subject.pack(side="left", fill="x", expand=True)
        self.create_copy_button(frame_sub, entry_subject).pack(side="left", padx=5)
        
        ttk.Label(dialog, text="Nachricht:").pack(anchor="w", padx=10)
        text_body = tk.Text(dialog, height=15)
        text_body.insert("1.0", body)
        text_body.pack(fill="both", expand=True, padx=10, pady=5)
        
        att_label = ttk.Label(dialog, text=f"Anhang: {os.path.basename(attachment_path)}" if attachment_path else "")
        att_label.pack(anchor="w", padx=10, pady=5)
        
        def send():
            # Get settings
            settings = {
                'server': database.get_setting('smtp_server'),
                'port': database.get_setting('smtp_port'),
                'user': database.get_setting('smtp_user'),
                'password': database.get_setting('smtp_password')
            }
            
            if not all(settings.values()):
                messagebox.showerror("Fehler", "Bitte erst SMTP Einstellungen konfigurieren (Datei -> Einstellungen).")
                return
                
            btn_send.config(state="disabled", text="Sende...")
            self.root.update()
            
            success, msg = email_utils.send_email(
                settings, 
                entry_to.get(), 
                entry_subject.get(), 
                text_body.get("1.0", "end"),
                [attachment_path] if attachment_path else None
            )
            
            btn_send.config(state="normal", text="Senden")
            
            if success:
                messagebox.showinfo("Erfolg", msg)
                dialog.destroy()
            else:
                messagebox.showerror("Fehler", f"Senden fehlgeschlagen: {msg}")
        
        btn_send = ttk.Button(dialog, text="Senden", command=send)
        btn_send.pack(pady=10)

    # --- INVENTORY ---
    def setup_inventory(self):
        top_frame = ttk.Frame(self.tab_inventory, padding=10)
        top_frame.pack(fill="x")
        
        ttk.Button(top_frame, text="Neues Fahrzeug", command=lambda: self.open_vehicle_dialog(None)).pack(side="left")
        ttk.Button(top_frame, text="Bearbeiten", command=self.edit_selected_vehicle).pack(side="left", padx=5)
        ttk.Button(top_frame, text="Löschen", command=self.delete_selected_vehicle).pack(side="left", padx=5)
        ttk.Button(top_frame, text="Aktualisieren", command=self.load_inventory).pack(side="left", padx=5)
        ttk.Button(top_frame, text="📉 CSV Export", command=self.export_inventory_csv, style="info.TButton").pack(side="left", padx=5)
        ttk.Button(top_frame, text="🌐 Mobile.de Export", command=self.export_mobile_csv, style="warning.TButton").pack(side="left", padx=5)
        
        # Search
        ttk.Label(top_frame, text="Suche:").pack(side="left", padx=(20, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_inventory)
        ttk.Entry(top_frame, textvariable=self.search_var).pack(side="left", fill="x", expand=True)
        
        cols = ("ID", "Marke", "Modell", "Jahr", "Preis", "KM", "Farbe", "Status", "Besitzer")
        self.tree = ttk.Treeview(self.tab_inventory, columns=cols, show="headings")
        
        for col in cols:
            self.tree.heading(col, text=col)
            width = 50 if col == "ID" else 100
            self.tree.column(col, width=width)
        
        # Tags for coloring
        self.tree.tag_configure("overdue", foreground="red")
        
        scrollbar = ttk.Scrollbar(self.tab_inventory, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tree.bind("<Double-1>", lambda e: self.edit_selected_vehicle())
        
        # Context Menu
        self.inv_menu = tk.Menu(self.root, tearoff=0)
        self.inv_menu.add_command(label="✏ Bearbeiten", command=self.edit_selected_vehicle)
        self.inv_menu.add_command(label="🗑 Löschen", command=self.delete_selected_vehicle)
        self.inv_menu.add_separator()
        self.inv_menu.add_command(label="📋 Service Historie", command=self._context_show_history)
        self.inv_menu.add_command(label="✉ Exposé senden", command=self._context_email_expose)
        self.inv_menu.add_command(label="📄 Exposé als PDF", command=self._context_save_expose_pdf)
        self.inv_menu.add_separator()
        self.inv_menu.add_command(label="📄 Angebot erstellen", command=lambda: self.create_document_dialog("Angebot", self._get_selected_vehicle()))
        self.inv_menu.add_command(label="🤝 Kaufvertrag erstellen", command=lambda: self.create_document_dialog("Kaufvertrag", self._get_selected_vehicle()))
        self.inv_menu.add_command(label="🤝 Kaufvertrag als PDF", command=self._context_save_contract_pdf)
        
        self.tree.bind("<Button-3>", lambda e: self._on_right_click(e, self.tree, self.inv_menu))

    def _get_selected_vehicle(self):
        selected = self.tree.selection()
        if not selected: return None
        v_id = self.tree.item(selected[0])['values'][0]
        vehicles = database.get_all_vehicles()
        return next((v for v in vehicles if v.id == v_id), None)

    def _context_show_history(self):
        v = self._get_selected_vehicle()
        if v: self.show_service_history(v.id)

    def _context_email_expose(self):
        v = self._get_selected_vehicle()
        if v: self.email_expose(v)

    def _context_save_expose_pdf(self):
        v = self._get_selected_vehicle()
        if not v: return
        
        try:
            # Attachments holen
            attachments = database.get_attachments(v.id)
            filepath = self.pdf_gen.generate_expose(v, attachments)
            
            # Ask user where to save or just show success
            # Let's ask user for destination to be "user friendly"
            dest = filedialog.asksaveasfilename(
                defaultextension=".pdf", 
                filetypes=[("PDF Documents", "*.pdf")],
                initialfile=os.path.basename(filepath)
            )
            
            if dest:
                shutil.copy(filepath, dest)
                if messagebox.askyesno("Erfolg", f"Exposé gespeichert unter:\n{dest}\n\nÖffnen?"):
                    os.startfile(dest)
            else:
                # If canceled, maybe just open the temp one?
                pass
                
        except Exception as e:
            messagebox.showerror("Fehler", f"PDF Erstellung fehlgeschlagen: {e}")

    def _context_save_contract_pdf(self):
        v = self._get_selected_vehicle()
        if not v: return
        
        # We need customer data. If owner_id is set, fetch customer.
        customer = None
        if v.owner_id:
            customer = database.get_customer(v.owner_id)
            
        # If no owner assigned, maybe ask user to select one? 
        # For now, generate with blank customer if None
        
        try:
            filepath = self.pdf_gen.generate_sales_contract(v, customer, v.price)
             
            dest = filedialog.asksaveasfilename(
                defaultextension=".pdf", 
                filetypes=[("PDF Documents", "*.pdf")],
                initialfile=os.path.basename(filepath)
            )
            
            if dest:
                shutil.copy(filepath, dest)
                if messagebox.askyesno("Erfolg", f"Kaufvertrag gespeichert unter:\n{dest}\n\nÖffnen?"):
                    os.startfile(dest)
        except Exception as e:
             messagebox.showerror("Fehler", f"PDF Erstellung fehlgeschlagen: {e}")

    def load_inventory(self):
        self.all_vehicles = database.get_all_vehicles()
        self.filter_inventory()

    def filter_inventory(self, *args):
        search_term = self.search_var.get().lower()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        today = datetime.now().strftime("%Y-%m-%d")
        
        for v in self.all_vehicles:
            # Search Filter
            v_str = f"{v.make} {v.model} {v.year} {v.color} {v.vin} {v.status}".lower()
            if search_term and search_term not in v_str:
                continue
                
            tags = ()
            # Check overdue
            if (v.tuv_due and v.tuv_due <= today) or (v.service_due and v.service_due <= today):
                tags = ("overdue",)
            
            owner = "Händler"
            if v.owner_id:
                owner = f"Kunde {v.owner_id}" # Simplify for now, could fetch name
            
            self.tree.insert("", "end", values=(v.id, v.make, v.model, v.year, f"{v.price:,.2f}", v.mileage, v.color, v.status, owner), tags=tags)

    def export_inventory_csv(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not filename:
            return
            
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['ID', 'Marke', 'Modell', 'Jahr', 'Preis', 'Einkaufspreis', 'KM', 'Farbe', 'Status', 'Besitzer', 'VIN']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for v in self.all_vehicles:
                    writer.writerow({
                        'ID': v.id,
                        'Marke': v.make,
                        'Modell': v.model,
                        'Jahr': v.year,
                        'Preis': v.price,
                        'Einkaufspreis': v.purchase_price,
                        'KM': v.mileage,
                        'Farbe': v.color,
                        'Status': v.status,
                        'Besitzer': v.owner_id if v.owner_id else "Händler",
                        'VIN': v.vin
                    })
            messagebox.showinfo("Erfolg", "Fahrzeugbestand erfolgreich exportiert!")
        except Exception as e:
            messagebox.showerror("Fehler", f"Export fehlgeschlagen: {e}")

    def export_mobile_csv(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], title="Export für Mobile.de")
        if not filename: return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                # Approximate Mobile.de fields
                fieldnames = ['manufacturer', 'model_description', 'price', 'mileage', 'first_registration', 'fuel_type', 'color', 'vin']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';') # Mobile.de often uses semicolon
                writer.writeheader()
                for v in self.all_vehicles:
                    writer.writerow({
                        'manufacturer': v.make,
                        'model_description': v.model,
                        'price': int(v.price) if v.price else 0,
                        'mileage': v.mileage,
                        'first_registration': f"01/{v.year}", # Approx
                        'fuel_type': v.fuel_type,
                        'color': v.color,
                        'vin': v.vin
                    })
            messagebox.showinfo("Erfolg", "Mobile.de Export erfolgreich!")
        except Exception as e:
            messagebox.showerror("Fehler", f"Export fehlgeschlagen: {e}")

    def edit_selected_vehicle(self):
        selected = self.tree.selection()
        if not selected: return
        v_id = self.tree.item(selected[0])['values'][0]
        # Find vehicle object
        vehicles = database.get_all_vehicles()
        vehicle = next((v for v in vehicles if v.id == v_id), None)
        if vehicle:
            self.open_vehicle_dialog(vehicle)

    def delete_selected_vehicle(self):
        selected = self.tree.selection()
        if not selected: return
        v_id = self.tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Löschen", "Fahrzeug wirklich löschen?"):
            database.delete_vehicle(v_id)
            self.load_inventory()
            self.update_dashboard()

    def create_copy_button(self, dialog, entry):
        def copy_content():
            dialog.clipboard_clear()
            dialog.clipboard_append(entry.get())
        return ttk.Button(dialog, text="📋", width=3, command=copy_content)

    def open_vehicle_dialog(self, vehicle):
        dialog = tk.Toplevel(self.root)
        dialog.title("Fahrzeug Details" if vehicle else "Neues Fahrzeug")
        dialog.geometry("600x700")
        
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        tab_details = ttk.Frame(notebook)
        notebook.add(tab_details, text="Details")
        
        tab_photos = ttk.Frame(notebook)
        notebook.add(tab_photos, text="Bilder")
        
        # --- DETAILS TAB ---
        fields = [
            ("Marke", "make"), ("Modell", "model"), ("Jahr", "year"), ("Preis (€)", "price"),
            ("Einkaufspreis (€)", "purchase_price"),
            ("Kilometerstand", "mileage"), ("Farbe", "color"), ("Kraftstoff", "fuel_type"), ("VIN", "vin"),
            ("TÜV fällig", "tuv_due"), ("Service fällig", "service_due")
        ]
        
        entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(tab_details, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = ttk.Entry(tab_details)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            copy_btn = self.create_copy_button(tab_details, entry)
            copy_btn.grid(row=i, column=2, padx=5)
            entries[key] = entry
            
        ttk.Label(tab_details, text="Status").grid(row=len(fields), column=0, padx=10, pady=5, sticky="e")
        status_cb = ttk.Combobox(tab_details, values=["Verfügbar", "Reserviert", "In Werkstatt"])
        status_cb.grid(row=len(fields), column=1, padx=10, pady=5, sticky="ew")
        
        ttk.Label(tab_details, text="Zustand").grid(row=len(fields)+1, column=0, padx=10, pady=5, sticky="e")
        condition_cb = ttk.Combobox(tab_details, values=["Neu", "Gebraucht", "Beschädigt"])
        condition_cb.grid(row=len(fields)+1, column=1, padx=10, pady=5, sticky="ew")
        
        owner_id = None
        if vehicle:
            entries['make'].insert(0, vehicle.make)
            entries['model'].insert(0, vehicle.model)
            entries['year'].insert(0, vehicle.year)
            entries['price'].insert(0, vehicle.price)
            entries['purchase_price'].insert(0, vehicle.purchase_price)
            entries['mileage'].insert(0, vehicle.mileage)
            entries['color'].insert(0, vehicle.color)
            entries['fuel_type'].insert(0, vehicle.fuel_type)
            entries['vin'].insert(0, vehicle.vin)
            entries['tuv_due'].insert(0, vehicle.tuv_due)
            entries['service_due'].insert(0, vehicle.service_due)
            status_cb.set(vehicle.status)
            condition_cb.set(vehicle.condition)
            owner_id = vehicle.owner_id
        else:
            status_cb.set("Verfügbar")
            condition_cb.set("Gebraucht")
            entries['purchase_price'].insert(0, "0.0")

        # --- PHOTOS TAB ---
        photo_frame = ttk.Frame(tab_photos, padding=10)
        photo_frame.pack(fill="both", expand=True)
        
        photo_cols = ("Dateiname", "Datum")
        photo_tree = ttk.Treeview(photo_frame, columns=photo_cols, show="headings")
        photo_tree.heading("Dateiname", text="Dateiname")
        photo_tree.heading("Datum", text="Datum")
        photo_tree.pack(fill="both", expand=True, pady=10)
        
        def load_photos():
            for item in photo_tree.get_children():
                photo_tree.delete(item)
            if vehicle:
                atts = database.get_attachments(vehicle.id)
                # Show only photos (no service_id)
                photos = [a for a in atts if a.service_id is None]
                for p in photos:
                    fname = os.path.basename(p.file_path)
                    photo_tree.insert("", "end", values=(fname, p.upload_date), tags=(p.file_path,))

        def add_photo():
            if not vehicle:
                messagebox.showinfo("Info", "Bitte erst Fahrzeug speichern.")
                return
            path = filedialog.askopenfilename(filetypes=[("Bilder", "*.jpg *.jpeg *.png *.gif")])
            if path:
                fname = os.path.basename(path)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                clean_fname = "".join(c for c in fname if c.isalnum() or c in (' ', '.', '_', '-')).strip()
                new_name = f"{vehicle.id}_{timestamp}_{clean_fname}"
                dest = os.path.join(config.get_uploads_path(), new_name)
                try:
                    shutil.copy(path, dest)
                    att = Attachment(vehicle.id, dest, "photo", datetime.now().strftime("%Y-%m-%d %H:%M"))
                    database.add_attachment(att)
                    load_photos()
                except Exception as e:
                    messagebox.showerror("Fehler", f"Fehler beim Upload: {e}")

        def open_photo():
            selected = photo_tree.selection()
            if not selected: return
            item = photo_tree.item(selected[0])
            path = item['tags'][0]
            try:
                os.startfile(path)
            except Exception as e:
                messagebox.showerror("Fehler", f"Kann Datei nicht öffnen: {e}")

        def save_photo():
            selected = photo_tree.selection()
            if not selected: return
            item = photo_tree.item(selected[0])
            path = item['tags'][0]
            fname = os.path.basename(path)
            
            dest = filedialog.asksaveasfilename(initialfile=fname)
            if dest:
                try:
                    shutil.copy(path, dest)
                    messagebox.showinfo("Erfolg", "Foto gespeichert.")
                except Exception as e:
                    messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")

        btn_frame = ttk.Frame(photo_frame)
        btn_frame.pack(fill="x")
        ttk.Button(btn_frame, text="Foto hinzufügen", command=add_photo).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Anzeigen", command=open_photo).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Speichern unter...", command=save_photo).pack(side="left", padx=5)
        
        if vehicle:
            load_photos()

        def save():
            try:
                data = {key: entry.get() for key, entry in entries.items()}
                
                # Validation
                try:
                    year_val = int(data['year']) if data['year'] else 0
                    price_val = float(data['price']) if data['price'] else 0.0
                    purchase_price_val = float(data['purchase_price']) if data['purchase_price'] else 0.0
                    mileage_val = int(data['mileage']) if data['mileage'] else 0
                except ValueError:
                    messagebox.showerror("Eingabefehler", "Bitte überprüfen Sie die Zahlenfelder (Jahr, Preis, KM).\nVerwenden Sie Punkt statt Komma für Preise.")
                    return

                v = Vehicle(
                    make=data['make'], model=data['model'], year=year_val, price=price_val,
                    purchase_price=purchase_price_val,
                    status=status_cb.get(), condition=condition_cb.get(),
                    mileage=mileage_val, color=data['color'], 
                    fuel_type=data['fuel_type'], vin=data['vin'],
                    owner_id=owner_id,
                    tuv_due=data['tuv_due'], service_due=data['service_due'],
                    id=vehicle.id if vehicle else None
                )
                
                if vehicle:
                    database.update_vehicle(v)
                else:
                    database.add_vehicle(v)
                
                dialog.destroy()
                self.refresh_all()
            except Exception as e:
                messagebox.showerror("Fehler", f"Speichern fehlgeschlagen:\n{str(e)}")
                print(f"Save error: {e}")

        # Button Frame (Bottom)
        btn_frame_main = ttk.Frame(dialog, padding=10)
        btn_frame_main.pack(fill="x", side="bottom")

        ttk.Button(btn_frame_main, text="Speichern", command=save, bootstyle="success").pack(side="right", padx=5)
        
        if vehicle:
            ttk.Button(btn_frame_main, text="Exposé drucken", command=lambda: self.print_expose(vehicle)).pack(side="left", padx=5)
            ttk.Button(btn_frame_main, text="✉ Exposé per Email", command=lambda: self.email_expose(vehicle)).pack(side="left", padx=5)

    # --- CUSTOMERS ---
    def setup_customers(self):
        top_frame = ttk.Frame(self.tab_customers, padding=10)
        top_frame.pack(fill="x")
        
        ttk.Button(top_frame, text="Neuer Kunde", command=lambda: self.open_customer_dialog(None)).pack(side="left")
        ttk.Button(top_frame, text="Bearbeiten", command=self.edit_selected_customer).pack(side="left", padx=5)
        ttk.Button(top_frame, text="Aktualisieren", command=self.load_customers).pack(side="left", padx=5)
        
        cols = ("ID", "Name", "Telefon", "Email", "Status", "Adresse")
        self.cust_tree = ttk.Treeview(self.tab_customers, columns=cols, show="headings")
        for col in cols:
            self.cust_tree.heading(col, text=col)
            self.cust_tree.column(col, width=120)
        self.cust_tree.column("ID", width=40)
        self.cust_tree.column("Status", width=100)
        self.cust_tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.cust_tree.bind("<Double-1>", lambda e: self.edit_selected_customer())

        # Context Menu
        self.cust_menu = tk.Menu(self.root, tearoff=0)
        self.cust_menu.add_command(label="✏ Bearbeiten", command=self.edit_selected_customer)
        self.cust_menu.add_command(label="✉ Email senden", command=self._context_email_customer)
        
        self.cust_tree.bind("<Button-3>", lambda e: self._on_right_click(e, self.cust_tree, self.cust_menu))

    def _context_email_customer(self):
        selected = self.cust_tree.selection()
        if not selected: return
        c_id = self.cust_tree.item(selected[0])['values'][0]
        customers = database.get_all_customers()
        c = next((x for x in customers if x.id == c_id), None)
        if c and c.email:
            self.open_email_dialog(to_email=c.email)
        else:
            messagebox.showinfo("Info", "Keine Email-Adresse vorhanden.")

    def load_customers(self):
        for item in self.cust_tree.get_children():
            self.cust_tree.delete(item)
        for c in database.get_all_customers():
            self.cust_tree.insert("", "end", values=(c.id, c.name, c.phone, c.email, c.status, c.address))

    def edit_selected_customer(self):
        selected = self.cust_tree.selection()
        if not selected: return
        c_id = self.cust_tree.item(selected[0])['values'][0]
        customers = database.get_all_customers()
        customer = next((c for c in customers if c.id == c_id), None)
        if customer:
            self.open_customer_dialog(customer)

    def open_customer_dialog(self, customer):
        dialog = tk.Toplevel(self.root)
        dialog.title("Kunde" if customer else "Neuer Kunde")
        dialog.geometry("500x450")
        
        fields = [("Name", "name"), ("Telefon", "phone"), ("Email", "email"), ("Adresse", "address")]
        entries = {}
        
        for i, (label, key) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = ttk.Entry(dialog)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            copy_btn = self.create_copy_button(dialog, entry)
            copy_btn.grid(row=i, column=2, padx=5)
            entries[key] = entry
        
        # Status Field
        ttk.Label(dialog, text="Status").grid(row=len(fields), column=0, padx=10, pady=5, sticky="e")
        status_cb = ttk.Combobox(dialog, values=["Interessent", "Kunde", "Inaktiv", "VIP"], state="readonly")
        status_cb.grid(row=len(fields), column=1, padx=10, pady=5, sticky="ew")
        status_cb.set("Interessent")
        entries['status'] = status_cb
        
        # Notes Field
        ttk.Label(dialog, text="Notizen").grid(row=len(fields)+1, column=0, padx=10, pady=5, sticky="ne")
        notes_entry = tk.Text(dialog, height=4, width=30)
        notes_entry.grid(row=len(fields)+1, column=1, padx=10, pady=5, sticky="ew")
        entries['notes'] = notes_entry
            
        if customer:
            entries['name'].insert(0, customer.name)
            entries['phone'].insert(0, customer.phone)
            entries['email'].insert(0, customer.email)
            entries['address'].insert(0, customer.address)
            entries['status'].set(customer.status)
            entries['notes'].insert("1.0", customer.notes)
            
        def save():
            data = {key: entry.get() if key != 'notes' else entry.get("1.0", "end-1c") for key, entry in entries.items()}
            c = Customer(data['name'], data['phone'], data['email'], data['address'], status=data['status'], notes=data['notes'], id=customer.id if customer else None)
            if customer:
                database.update_customer(c)
            else:
                database.add_customer(c)
            dialog.destroy()
            self.load_customers()
            
        ttk.Button(dialog, text="Speichern", command=save).grid(row=len(fields)+2, column=0, columnspan=2, pady=20)
        
        if customer and customer.email:
            def send_mail():
                self.open_email_dialog(to_email=customer.email)
            ttk.Button(dialog, text="✉ Email senden", command=send_mail).grid(row=len(fields)+3, column=0, columnspan=2, pady=5)

    # --- WORKSHOP ---
    def setup_workshop(self):
        top_frame = ttk.Frame(self.tab_workshop, padding=10)
        top_frame.pack(fill="x")
        
        ttk.Button(top_frame, text="Service-Eintrag hinzufügen", command=self.open_service_dialog).pack(side="left")
        ttk.Button(top_frame, text="Historie anzeigen", command=self.show_service_history).pack(side="left", padx=5)
        ttk.Button(top_frame, text="Reparatur abgeschlossen (-> Verfügbar)", command=self.workshop_finish).pack(side="left", padx=5)

        cols = ("ID", "Marke", "Modell", "Status")
        self.ws_tree = ttk.Treeview(self.tab_workshop, columns=cols, show="headings")
        for col in cols: self.ws_tree.heading(col, text=col)
        self.ws_tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Context Menu
        self.ws_menu = tk.Menu(self.root, tearoff=0)
        self.ws_menu.add_command(label="➕ Neuer Service", command=self.open_service_dialog)
        self.ws_menu.add_command(label="📋 Historie", command=self.show_service_history)
        self.ws_menu.add_separator()
        self.ws_menu.add_command(label="✅ Fertig melden", command=self.workshop_finish)
        
        self.ws_tree.bind("<Double-1>", lambda e: self.show_service_history())
        self.ws_tree.bind("<Button-3>", lambda e: self._on_right_click(e, self.ws_tree, self.ws_menu))

    def load_workshop(self):
        for item in self.ws_tree.get_children(): self.ws_tree.delete(item)
        for v in database.get_all_vehicles():
            self.ws_tree.insert("", "end", values=(v.id, v.make, v.model, v.status))

    def open_service_dialog(self):
        selected = self.ws_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Bitte Fahrzeug wählen.")
            return
        v_id = self.ws_tree.item(selected[0])['values'][0]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Service Eintrag")
        dialog.geometry("500x650")
        
        ttk.Label(dialog, text="Beschreibung / Arbeitsschritte:").pack(pady=5)
        desc_entry = tk.Text(dialog, height=4)
        desc_entry.pack(fill="x", padx=20)
        
        # Costs
        cost_frame = ttk.Labelframe(dialog, text="Kostenaufstellung")
        cost_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(cost_frame, text="Lohnkosten (€):").grid(row=0, column=0, padx=5, pady=5)
        labor_entry = ttk.Entry(cost_frame)
        labor_entry.grid(row=0, column=1, padx=5, pady=5)
        labor_entry.insert(0, "0.00")
        
        ttk.Label(cost_frame, text="Teilekosten (€):").grid(row=1, column=0, padx=5, pady=5)
        parts_entry = ttk.Entry(cost_frame)
        parts_entry.grid(row=1, column=1, padx=5, pady=5)
        parts_entry.insert(0, "0.00")
        
        # Material List
        ttk.Label(dialog, text="Verwendetes Material / Teile:").pack(pady=5)
        mat_entry = tk.Text(dialog, height=4)
        mat_entry.pack(fill="x", padx=20)
        
        ttk.Label(dialog, text="Datum:").pack(pady=5)
        date_entry = ttk.Entry(dialog)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        date_entry.pack(fill="x", padx=20)
        
        # Invoice Upload
        file_path_var = tk.StringVar()
        def select_file():
            path = filedialog.askopenfilename()
            if path:
                file_path_var.set(path)
        
        ttk.Button(dialog, text="Rechnung/Dokument anhängen", command=select_file).pack(pady=10)
        ttk.Label(dialog, textvariable=file_path_var, font=("Segoe UI", 8)).pack()
        
        def save():
            try:
                labor = float(labor_entry.get())
                parts = float(parts_entry.get())
                total = labor + parts
                desc = desc_entry.get("1.0", "end-1c")
                mat = mat_entry.get("1.0", "end-1c")
                date = date_entry.get()
                
                record = ServiceRecord(v_id, date, desc, total, labor_cost=labor, parts_cost=parts, materials=mat)
                rec_id = database.add_service_record(record)
                
                # Handle attachment
                if file_path_var.get():
                    path = file_path_var.get()
                    fname = os.path.basename(path)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    clean_fname = "".join(c for c in fname if c.isalnum() or c in (' ', '.', '_', '-')).strip()
                    new_name = f"SVC_{rec_id}_{timestamp}_{clean_fname}"
                    dest = os.path.join(config.get_uploads_path(), new_name)
                    
                    try:
                        shutil.copy(path, dest)
                        att = Attachment(v_id, dest, "Rechnung (Service)", datetime.now().strftime("%Y-%m-%d %H:%M"), service_id=rec_id)
                        database.add_attachment(att)
                    except Exception as e:
                        messagebox.showerror("Fehler", f"Fehler beim Upload: {e}")
                
                if messagebox.askyesno("Status", "Status auf 'In Werkstatt' setzen?"):
                    database.update_status(v_id, "In Werkstatt")
                
                dialog.destroy()
                self.refresh_all()
            except ValueError:
                messagebox.showerror("Fehler", "Ungültige Kosten.")
                
        ttk.Button(dialog, text="Speichern", command=save).pack(pady=20)

    def show_service_history(self, v_id=None):
        if v_id is None:
            selected = self.ws_tree.selection()
            if not selected: return
            v_id = self.ws_tree.item(selected[0])['values'][0]
        
        records = database.get_service_history(v_id)
        
        h_win = tk.Toplevel(self.root)
        h_win.title(f"Service Historie (Fahrzeug {v_id})")
        h_win.geometry("900x500")
        
        cols = ("ID", "Datum", "Beschreibung", "Material", "Lohn", "Teile", "Gesamt")
        tree = ttk.Treeview(h_win, columns=cols, show="headings")
        for col in cols: tree.heading(col, text=col)
        tree.column("ID", width=40)
        tree.column("Beschreibung", width=200)
        tree.column("Material", width=200)
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        total = 0
        for r in records:
            tree.insert("", "end", values=(r.id, r.date, r.description, r.materials, 
                                           f"{r.labor_cost:.2f} €", f"{r.parts_cost:.2f} €", f"{r.cost:.2f} €"))
            total += r.cost
            
        ttk.Label(h_win, text=f"Gesamtkosten: {total:.2f} €", font=('bold', 12)).pack(pady=5)
        
        def open_invoice():
            sel = tree.selection()
            if not sel: return
            s_id = tree.item(sel[0])['values'][0]
            
            atts = database.get_attachments(v_id)
            svc_atts = [a for a in atts if a.service_id == s_id]
            
            if not svc_atts:
                messagebox.showinfo("Info", "Keine Anhänge vorhanden.")
                return
            
            if len(svc_atts) == 1:
                try:
                    os.startfile(svc_atts[0].file_path)
                except Exception as e:
                    messagebox.showerror("Fehler", f"Fehler: {e}")
            else:
                sel_win = tk.Toplevel(h_win)
                sel_win.title("Anhänge")
                for a in svc_atts:
                    fname = os.path.basename(a.file_path)
                    def open_a(path=a.file_path):
                        os.startfile(path)
                    ttk.Button(sel_win, text=fname, command=open_a).pack(fill="x", padx=10, pady=2)

        ttk.Button(h_win, text="Rechnung/Anhang öffnen", command=open_invoice).pack(pady=10)

    def workshop_finish(self):
        selected = self.ws_tree.selection()
        if not selected: return
        v_id = self.ws_tree.item(selected[0])['values'][0]
        
        if messagebox.askyesno("Fertig", "Fahrzeugstatus auf 'Verfügbar' setzen?"):
            database.update_status(v_id, "Verfügbar")
            self.refresh_all()

    # --- TEST DRIVES ---
    def setup_test_drives(self):
        top_frame = ttk.Frame(self.tab_test_drives, padding=10)
        top_frame.pack(fill="x")
        
        ttk.Button(top_frame, text="Neue Probefahrt", command=self.open_test_drive_dialog).pack(side="left")
        ttk.Button(top_frame, text="Aktualisieren", command=self.load_test_drives).pack(side="left", padx=5)
        
        cols = ("ID", "Datum", "Fahrzeug", "Kunde", "Führerschein?", "Notizen")
        self.td_tree = ttk.Treeview(self.tab_test_drives, columns=cols, show="headings")
        
        for col in cols:
            self.td_tree.heading(col, text=col)
            width = 40 if col == "ID" else 100
            self.td_tree.column(col, width=width)
        
        self.td_tree.column("Fahrzeug", width=200)
        self.td_tree.column("Kunde", width=150)
        self.td_tree.column("Notizen", width=300)
            
        self.td_tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Context Menu
        self.td_menu = tk.Menu(self.root, tearoff=0)
        self.td_menu.add_command(label="🗑 Löschen", command=self.delete_selected_test_drive)
        
        self.td_tree.bind("<Button-3>", lambda e: self._on_right_click(e, self.td_tree, self.td_menu))

    def load_test_drives(self):
        for item in self.td_tree.get_children():
            self.td_tree.delete(item)
            
        tds = database.get_test_drives()
        for td in tds:
            lic = "Ja" if td.license_check else "Nein"
            self.td_tree.insert("", "end", values=(td.id, td.date_time, td.vehicle_name, td.customer_name, lic, td.notes))
        
        self.update_calendar()

    def delete_selected_test_drive(self):
        selected = self.td_tree.selection()
        if not selected: return
        td_id = self.td_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Löschen", "Probefahrt wirklich löschen?"):
            database.delete_test_drive(td_id)
            self.load_test_drives()

    # --- CALENDAR (Redesigned) ---
    # --- PARTS ---
    def setup_parts(self):
        top_frame = ttk.Frame(self.tab_parts, padding=10)
        top_frame.pack(fill="x")
        
        ttk.Button(top_frame, text="Neues Ersatzteil", command=lambda: self.open_part_dialog(None)).pack(side="left")
        ttk.Button(top_frame, text="Bearbeiten", command=self.edit_selected_part).pack(side="left", padx=5)
        ttk.Button(top_frame, text="Löschen", command=self.delete_selected_part).pack(side="left", padx=5)
        ttk.Button(top_frame, text="Aktualisieren", command=self.load_parts).pack(side="left", padx=5)
        
        # Search
        ttk.Label(top_frame, text="Suche:").pack(side="left", padx=(20, 5))
        self.parts_search_var = tk.StringVar()
        self.parts_search_var.trace("w", self.filter_parts)
        ttk.Entry(top_frame, textvariable=self.parts_search_var).pack(side="left", fill="x", expand=True)
        
        cols = ("ID", "Name", "Nummer", "Menge", "Min. Menge", "Preis", "Lieferant", "Lagerort")
        self.parts_tree = ttk.Treeview(self.tab_parts, columns=cols, show="headings")
        
        for col in cols:
            self.parts_tree.heading(col, text=col)
            width = 50 if col == "ID" else 100
            self.parts_tree.column(col, width=width)
            
        # Tags for low stock
        self.parts_tree.tag_configure("low_stock", foreground="red")
        
        scrollbar = ttk.Scrollbar(self.tab_parts, orient="vertical", command=self.parts_tree.yview)
        self.parts_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.parts_tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.parts_tree.bind("<Double-1>", lambda e: self.edit_selected_part())
        
        # Context Menu
        self.parts_menu = tk.Menu(self.root, tearoff=0)
        self.parts_menu.add_command(label="✏ Bearbeiten", command=self.edit_selected_part)
        self.parts_menu.add_command(label="🗑 Löschen", command=self.delete_selected_part)
        
        self.parts_tree.bind("<Button-3>", lambda e: self._on_right_click(e, self.parts_tree, self.parts_menu))

    def load_parts(self):
        self.all_parts = database.get_parts()
        self.filter_parts()

    def filter_parts(self, *args):
        search_term = self.parts_search_var.get().lower()
        
        for item in self.parts_tree.get_children():
            self.parts_tree.delete(item)
            
        for p in self.all_parts:
            # Search Filter
            p_str = f"{p.name} {p.part_number} {p.supplier} {p.storage_location}".lower()
            if search_term and search_term not in p_str:
                continue
                
            tags = ()
            # Check low stock
            if p.quantity <= p.min_quantity:
                tags = ("low_stock",)
            
            self.parts_tree.insert("", "end", values=(p.id, p.name, p.part_number, p.quantity, p.min_quantity, f"{p.price:,.2f}", p.supplier, p.storage_location), tags=tags)

    def edit_selected_part(self):
        selected = self.parts_tree.selection()
        if not selected: return
        p_id = self.parts_tree.item(selected[0])['values'][0]
        # Find part object
        parts = database.get_parts()
        part = next((p for p in parts if p.id == p_id), None)
        if part:
            self.open_part_dialog(part)

    def delete_selected_part(self):
        selected = self.parts_tree.selection()
        if not selected: return
        p_id = self.parts_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Löschen", "Ersatzteil wirklich löschen?"):
            database.delete_part(p_id)
            self.load_parts()

    def open_part_dialog(self, part):
        dialog = tk.Toplevel(self.root)
        dialog.title("Ersatzteil Details" if part else "Neues Ersatzteil")
        dialog.geometry("500x500")
        
        fields = [
            ("Name", "name"), ("Teilenummer", "part_number"), 
            ("Menge", "quantity"), ("Min. Menge", "min_quantity"),
            ("Preis (€)", "price"), ("Lieferant", "supplier"),
            ("Lagerort", "storage_location")
        ]
        
        entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = ttk.Entry(dialog)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            copy_btn = self.create_copy_button(dialog, entry)
            copy_btn.grid(row=i, column=2, padx=5)
            entries[key] = entry
            
        if part:
            entries['name'].insert(0, part.name)
            entries['part_number'].insert(0, part.part_number)
            entries['quantity'].insert(0, part.quantity)
            entries['min_quantity'].insert(0, part.min_quantity)
            entries['price'].insert(0, part.price)
            entries['supplier'].insert(0, part.supplier)
            entries['storage_location'].insert(0, part.storage_location)
        else:
            entries['quantity'].insert(0, "0")
            entries['min_quantity'].insert(0, "0")
            entries['price'].insert(0, "0.0")

        def save():
            try:
                data = {key: entry.get() for key, entry in entries.items()}
                
                # Validation
                try:
                    qty = int(data['quantity']) if data['quantity'] else 0
                    min_qty = int(data['min_quantity']) if data['min_quantity'] else 0
                    price = float(data['price']) if data['price'] else 0.0
                except ValueError:
                    messagebox.showerror("Eingabefehler", "Bitte überprüfen Sie die Zahlenfelder (Menge, Preis).")
                    return

                p = Part(
                    name=data['name'], part_number=data['part_number'],
                    quantity=qty, min_quantity=min_qty, price=price,
                    supplier=data['supplier'], storage_location=data['storage_location'],
                    id=part.id if part else None
                )
                
                if part:
                    database.update_part(p)
                else:
                    database.add_part(p)
                
                dialog.destroy()
                self.load_parts()
            except Exception as e:
                messagebox.showerror("Fehler", f"Speichern fehlgeschlagen:\n{str(e)}")

        ttk.Button(dialog, text="Speichern", command=save, bootstyle="success").grid(row=len(fields), column=1, pady=20, sticky="e")

    # --- DOCUMENTS ---
    def setup_documents(self):
        top_frame = ttk.Frame(self.tab_documents, padding=10)
        top_frame.pack(fill="x")
        
        ttk.Button(top_frame, text="Aktualisieren", command=self.load_documents).pack(side="left", padx=5)
        ttk.Button(top_frame, text="➕ Hochladen", command=self.upload_document).pack(side="left", padx=5)
        ttk.Button(top_frame, text="Bearbeiten", command=self.edit_selected_document).pack(side="left", padx=5)
        ttk.Button(top_frame, text="Öffnen", command=self.open_selected_document).pack(side="left", padx=5)
        ttk.Button(top_frame, text="💾 Speichern unter...", command=self.save_selected_document).pack(side="left", padx=5)
        ttk.Button(top_frame, text="Löschen", command=self.delete_selected_document).pack(side="left", padx=5)
        
        cols = ("ID", "Typ", "Titel", "Datum", "Fahrzeug", "Kunde")
        self.doc_tree = ttk.Treeview(self.tab_documents, columns=cols, show="headings")
        
        for col in cols:
            self.doc_tree.heading(col, text=col)
            width = 50 if col == "ID" else 150
            self.doc_tree.column(col, width=width)
            
        scrollbar = ttk.Scrollbar(self.tab_documents, orient="vertical", command=self.doc_tree.yview)
        self.doc_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.doc_tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Context Menu
        self.doc_menu = tk.Menu(self.root, tearoff=0)
        self.doc_menu.add_command(label="✏ Bearbeiten", command=self.edit_selected_document)
        self.doc_menu.add_command(label="📂 Öffnen", command=self.open_selected_document)
        self.doc_menu.add_command(label="💾 Speichern unter...", command=self.save_selected_document)
        self.doc_menu.add_command(label="🗑 Löschen", command=self.delete_selected_document)
        
        self.doc_tree.bind("<Button-3>", lambda e: self._on_right_click(e, self.doc_tree, self.doc_menu))
        self.doc_tree.bind("<Double-1>", lambda e: self.open_selected_document())

    def load_documents(self):
        for item in self.doc_tree.get_children():
            self.doc_tree.delete(item)
            
        docs = database.get_documents()
        for d in docs:
            self.doc_tree.insert("", "end", values=(d.id, d.doc_type, d.title, d.date_created, d.vehicle_id if d.vehicle_id else "-", d.customer_id if d.customer_id else "-"), tags=(d.file_path,))

    def open_selected_document(self):
        selected = self.doc_tree.selection()
        if not selected: return
        item = self.doc_tree.item(selected[0])
        path = item['tags'][0]
        if os.path.exists(path):
            try:
                os.startfile(path)
            except Exception as e:
                messagebox.showerror("Fehler", f"Kann Datei nicht öffnen: {e}")
        else:
            messagebox.showerror("Fehler", "Datei nicht gefunden.")

    def save_selected_document(self):
        selected = self.doc_tree.selection()
        if not selected: return
        item = self.doc_tree.item(selected[0])
        path = item['tags'][0]
        
        if not os.path.exists(path):
             messagebox.showerror("Fehler", "Datei nicht gefunden.")
             return
             
        fname = os.path.basename(path)
        dest = filedialog.asksaveasfilename(initialfile=fname)
        
        if dest:
            try:
                shutil.copy(path, dest)
                messagebox.showinfo("Erfolg", "Dokument gespeichert.")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")

    def delete_selected_document(self):
        selected = self.doc_tree.selection()
        if not selected: return
        d_id = self.doc_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Löschen", "Dokument wirklich löschen?"):
            database.delete_document(d_id)
            self.load_documents()

    def edit_selected_document(self):
        selected = self.doc_tree.selection()
        if not selected:
             messagebox.showwarning("Auswahl", "Bitte wählen Sie ein Dokument aus.")
             return
        d_id = self.doc_tree.item(selected[0])['values'][0]
        
        docs = database.get_documents()
        doc = next((d for d in docs if d.id == d_id), None)
        
        if doc:
            self.open_doc_edit_dialog(doc)
            
    def open_doc_edit_dialog(self, doc):
        dialog = tk.Toplevel(self.root)
        dialog.title("Dokument bearbeiten")
        dialog.geometry("400x250")
        
        ttk.Label(dialog, text="Titel / Beschreibung:").pack(pady=5)
        title_entry = ttk.Entry(dialog)
        title_entry.pack(fill="x", padx=20)
        title_entry.insert(0, doc.title)
        
        ttk.Label(dialog, text="Typ:").pack(pady=5)
        type_cb = ttk.Combobox(dialog, values=["Allgemein", "Rechnung", "Vertrag", "Notiz"], state="readonly")
        type_cb.pack(fill="x", padx=20)
        type_cb.set(doc.doc_type)
        
        def save():
            new_title = title_entry.get()
            new_type = type_cb.get()
            
            if not new_title:
                messagebox.showerror("Fehler", "Bitte Titel eingeben.")
                return
            
            doc.title = new_title
            doc.doc_type = new_type
            
            try:
                database.update_document(doc)
                dialog.destroy()
                self.load_documents()
                messagebox.showinfo("Erfolg", "Dokument aktualisiert.")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")
            
        ttk.Button(dialog, text="Speichern", command=save).pack(pady=20)

    def upload_document(self):
        file_path = filedialog.askopenfilename(title="Dokument auswählen")
        if not file_path: return
        
        # Ask for details
        dialog = tk.Toplevel(self.root)
        dialog.title("Dokument hochladen")
        dialog.geometry("400x250")
        
        ttk.Label(dialog, text="Titel / Beschreibung:").pack(pady=5)
        title_entry = ttk.Entry(dialog)
        title_entry.pack(fill="x", padx=20)
        title_entry.insert(0, os.path.basename(file_path))
        
        ttk.Label(dialog, text="Typ:").pack(pady=5)
        type_cb = ttk.Combobox(dialog, values=["Allgemein", "Rechnung", "Vertrag", "Notiz"], state="readonly")
        type_cb.pack(fill="x", padx=20)
        type_cb.set("Allgemein")
        
        def save():
            title = title_entry.get()
            doc_type = type_cb.get()
            
            if not title:
                messagebox.showerror("Fehler", "Bitte Titel eingeben.")
                return
                
            # Copy file
            try:
                fname = os.path.basename(file_path)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_name = f"DOC_{timestamp}_{fname}"
                dest = os.path.join(config.get_uploads_path(), new_name)
                shutil.copy(file_path, dest)
                
                doc = Document(doc_type, title, datetime.now().strftime("%Y-%m-%d %H:%M"), file_path=dest)
                database.add_document(doc)
                
                dialog.destroy()
                self.load_documents()
                messagebox.showinfo("Erfolg", "Dokument hochgeladen.")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Hochladen: {e}")
                
        ttk.Button(dialog, text="Hochladen", command=save).pack(pady=20)

    def create_document_dialog(self, doc_type, vehicle=None):
        if not vehicle:
             messagebox.showinfo("Info", "Bitte wählen Sie ein Fahrzeug aus.")
             return

        # Select Customer
        customers = database.get_all_customers()
        cust_map = {f"{c.name} (ID: {c.id})": c for c in customers}
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"{doc_type} erstellen")
        dialog.geometry("400x200")
        
        ttk.Label(dialog, text="Kunde wählen:").pack(pady=10)
        cb_cust = ttk.Combobox(dialog, values=list(cust_map.keys()))
        cb_cust.pack(fill="x", padx=20)
        
        def generate():
            cust_name = cb_cust.get()
            customer = cust_map.get(cust_name)
            
            if not customer:
                if not messagebox.askyesno("Info", "Kein Kunde ausgewählt. Fortfahren?"):
                    # allow proceeding without customer
                    pass
            
            try:
                self.generate_document(doc_type, vehicle, customer)
                dialog.destroy()
                self.load_documents()
                # messagebox.showinfo("Erfolg", "Dokument erstellt!") # generate_document opens it, so maybe no need for popup
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler: {e}")
                
        ttk.Button(dialog, text="Erstellen", command=generate).pack(pady=20)

    def generate_document(self, doc_type, vehicle, customer):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{doc_type}_{vehicle.id if vehicle else 'gen'}_{timestamp}.html"
        filepath = os.path.join(config.get_uploads_path(), filename)
        
        date_str = datetime.now().strftime("%d.%m.%Y")
        
        html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; padding: 40px; }}
                h1 {{ color: #333; }}
                .header {{ margin-bottom: 40px; }}
                .details {{ margin-bottom: 20px; }}
                table {{ width: 100%; border-collapse: collapse; }}
                td, th {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{doc_type}</h1>
                <p>Datum: {date_str}</p>
            </div>
        """
        
        if customer:
            html += f"""
            <div class="details">
                <h3>Kunde</h3>
                <p><strong>{customer.name}</strong><br>{customer.address}<br>Tel: {customer.phone}<br>Email: {customer.email}</p>
            </div>
            """
            
        if vehicle:
            html += f"""
            <div class="details">
                <h3>Fahrzeug</h3>
                <table>
                    <tr><th>Marke</th><td>{vehicle.make}</td></tr>
                    <tr><th>Modell</th><td>{vehicle.model}</td></tr>
                    <tr><th>Jahr</th><td>{vehicle.year}</td></tr>
                    <tr><th>VIN</th><td>{vehicle.vin}</td></tr>
                    <tr><th>KM</th><td>{vehicle.mileage}</td></tr>
                    <tr><th>Preis</th><td>{vehicle.price:,.2f} €</td></tr>
                </table>
            </div>
            """
            
        if doc_type == "Kaufvertrag":
             html += """
             <div class="details">
                <h3>Vertragsbedingungen</h3>
                <p>Das Fahrzeug wird unter Ausschluss der Sachmängelhaftung verkauft, soweit nicht anders vereinbart.
                Das Fahrzeug bleibt bis zur vollständigen Bezahlung Eigentum des Verkäufers.</p>
             </div>
             """
            
        html += """
            <div class="footer">
                <br><br><br>
                <table style="border: none;">
                    <tr>
                        <td style="border: none;">_________________________<br>Unterschrift Verkäufer</td>
                        <td style="border: none;">_________________________<br>Unterschrift Käufer</td>
                    </tr>
                </table>
            </div>
        </body>
        </html>
        """
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
            
        doc = Document(
            doc_type=doc_type,
            title=f"{doc_type} - {vehicle.make if vehicle else ''} {vehicle.model if vehicle else ''}",
            date_created=date_str,
            vehicle_id=vehicle.id if vehicle else None,
            customer_id=customer.id if customer else None,
            file_path=filepath
        )
        database.add_document(doc)
        
        # Open it
        os.startfile(filepath)

    def setup_calendar(self):
        # Header Controls (Month/Year)
        header_frame = ttk.Frame(self.tab_calendar, padding=10)
        header_frame.pack(fill="x")
        
        self.cal_month = datetime.now().month
        self.cal_year = datetime.now().year
        
        ttk.Button(header_frame, text="< Vorheriger", command=lambda: self.change_month(-1)).pack(side="left")
        self.lbl_month = ttk.Label(header_frame, text="", font=("Segoe UI", 16, "bold"), width=25, anchor="center")
        self.lbl_month.pack(side="left", padx=20)
        ttk.Button(header_frame, text="Nächster >", command=lambda: self.change_month(1)).pack(side="left")
        
        ttk.Button(header_frame, text="Heute", command=self.go_to_today).pack(side="right", padx=10)
        
        # Weekday Headers
        days_header = ttk.Frame(self.tab_calendar)
        days_header.pack(fill="x", padx=10, pady=(10, 0))
        
        days = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
        for i, day in enumerate(days):
            lbl = ttk.Label(days_header, text=day, font=("Segoe UI", 10, "bold"), anchor="center")
            lbl.grid(row=0, column=i, sticky="ew")
            days_header.columnconfigure(i, weight=1)
            
        # Main Grid
        self.cal_frame = ttk.Frame(self.tab_calendar, padding=10)
        self.cal_frame.pack(fill="both", expand=True)
        
        self.update_calendar()

    def go_to_today(self):
        self.cal_month = datetime.now().month
        self.cal_year = datetime.now().year
        self.update_calendar()

    def change_month(self, delta):
        self.cal_month += delta
        if self.cal_month > 12:
            self.cal_month = 1
            self.cal_year += 1
        elif self.cal_month < 1:
            self.cal_month = 12
            self.cal_year -= 1
        self.update_calendar()

    def update_calendar(self):
        for widget in self.cal_frame.winfo_children():
            widget.destroy()
            
        month_name = calendar.month_name[self.cal_month]
        self.lbl_month.config(text=f"{month_name} {self.cal_year}")
        
        cal_data = calendar.monthcalendar(self.cal_year, self.cal_month)
        events_map = self.get_events_details(self.cal_year, self.cal_month)
        
        today_date = datetime.now().strftime("%Y-%m-%d")
        
        # Configure grid weights
        for i in range(7):
            self.cal_frame.columnconfigure(i, weight=1, uniform="day_col")
        for i in range(len(cal_data)):
            self.cal_frame.rowconfigure(i, weight=1, uniform="day_row")
            
        for r, week in enumerate(cal_data):
            for c, day in enumerate(week):
                if day == 0:
                    # Empty cell for days from prev/next month
                    bg = "#e0e0e0" # darker gray
                    f = tk.Frame(self.cal_frame, bg=bg, relief="flat")
                    f.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
                    continue
                
                day_str = f"{self.cal_year}-{self.cal_month:02d}-{day:02d}"
                day_events = events_map.get(day_str, [])
                
                # Cell Styling
                bg_color = "#ffffff" # White default
                fg_color = "#000000"
                
                # Check if today
                border_color = "#cccccc"
                border_width = 1
                
                if day_str == today_date:
                    border_color = "#007bff" # Blue border for today
                    border_width = 2
                    bg_color = "#f0f8ff" # AliceBlue
                
                # Frame for the day
                day_frame = tk.Frame(self.cal_frame, bg=bg_color, highlightbackground=border_color, highlightthickness=border_width)
                day_frame.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
                
                # Day Number
                tk.Label(day_frame, text=str(day), font=("Segoe UI", 12, "bold"), bg=bg_color, fg=fg_color).pack(anchor="ne", padx=5, pady=2)
                
                # Events Container
                event_container = tk.Frame(day_frame, bg=bg_color)
                event_container.pack(fill="both", expand=True, padx=2)
                
                # List events (max 3-4 to fit)
                for i, evt in enumerate(day_events):
                    if i >= 3:
                        tk.Label(event_container, text=f"+ {len(day_events)-i} weitere...", font=("Segoe UI", 8), bg=bg_color, fg="gray").pack(anchor="w")
                        break
                    
                    # Event Pill
                    pill_color = evt['color']
                    pill_text = evt['title']
                    
                    # Create a label that looks like a pill
                    e_lbl = tk.Label(event_container, text=pill_text, bg=pill_color, fg="black", font=("Segoe UI", 8), anchor="w", padx=2)
                    e_lbl.pack(fill="x", pady=1)
                    
                    # Click to show details
                    e_lbl.bind("<Button-1>", lambda e, d=day_str: self.show_day_details_popup(d))
                
                # Click on empty space in day frame also shows details
                day_frame.bind("<Button-1>", lambda e, d=day_str: self.show_day_details_popup(d))

    def get_events_details(self, year, month):
        events = {} # "YYYY-MM-DD": [{title, color, ...}]
        
        # Test Drives
        for td in database.get_test_drives():
            if len(td.date_time) >= 10:
                try:
                    dt_str = td.date_time[:10]
                    dt = datetime.strptime(dt_str, "%Y-%m-%d")
                    if dt.year == year and dt.month == month:
                        if dt_str not in events: events[dt_str] = []
                        time_part = td.date_time[11:] if len(td.date_time) > 11 else ""
                        sort_time = time_part if time_part else "00:00"
                        title = f"⏰ {time_part} {td.vehicle_name}"
                        events[dt_str].append({"title": title, "color": "#ADD8E6", "type": "test_drive", "sort_time": sort_time})
                except: pass
        
        # Vehicles
        for v in database.get_all_vehicles():
            # TUV
            if v.tuv_due:
                try:
                    dt = datetime.strptime(v.tuv_due, "%Y-%m-%d")
                    if dt.year == year and dt.month == month:
                        if v.tuv_due not in events: events[v.tuv_due] = []
                        events[v.tuv_due].append({"title": f"⚠️ TÜV: {v.make}", "color": "#FFB6C1", "type": "tuv", "sort_time": "00:00"})
                except: pass
            # Service
            if v.service_due:
                try:
                    dt = datetime.strptime(v.service_due, "%Y-%m-%d")
                    if dt.year == year and dt.month == month:
                        if v.service_due not in events: events[v.service_due] = []
                        events[v.service_due].append({"title": f"🔧 Svc: {v.make}", "color": "#FFB6C1", "type": "service", "sort_time": "00:00"})
                except: pass
        
        # Sort events by time
        for day_events in events.values():
            day_events.sort(key=lambda x: x['sort_time'])
                        
        return events

    def show_day_details_popup(self, date_str):
        events = self.get_events_details(int(date_str[:4]), int(date_str[5:7])).get(date_str, [])
        if not events: return
        
        p = tk.Toplevel(self.root)
        p.title(f"Termine am {date_str}")
        p.geometry("400x300")
        
        ttk.Label(p, text=f"Termine am {date_str}", font=("bold", 14)).pack(pady=10)
        
        for evt in events:
            f = tk.Frame(p, bg=evt['color'], pady=5, padx=5)
            f.pack(fill="x", padx=10, pady=2)
            tk.Label(f, text=evt['title'], bg=evt['color'], font=("Segoe UI", 10)).pack(anchor="w")

    def open_test_drive_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Neue Probefahrt")
        dialog.geometry("500x400")
        
        # Vehicle Selection
        ttk.Label(dialog, text="Fahrzeug:").pack(pady=5)
        vehicles = database.get_all_vehicles()
        avail_vehicles = [v for v in vehicles if v.status == "Verfügbar"]
        v_map = {f"{v.make} {v.model} ({v.vin})": v.id for v in avail_vehicles}
        v_cb = ttk.Combobox(dialog, values=list(v_map.keys()))
        v_cb.pack(fill="x", padx=20)
        
        # Customer Selection
        ttk.Label(dialog, text="Kunde:").pack(pady=5)
        customers = database.get_customers()
        c_map = {f"{c.name} ({c.id})": c.id for c in customers}
        c_cb = ttk.Combobox(dialog, values=list(c_map.keys()))
        c_cb.pack(fill="x", padx=20)
        
        # Date
        ttk.Label(dialog, text="Datum/Zeit (YYYY-MM-DD HH:MM):").pack(pady=5)
        date_entry = ttk.Entry(dialog)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))
        date_entry.pack(fill="x", padx=20)
        
        # License Check
        lic_var = tk.BooleanVar()
        ttk.Checkbutton(dialog, text="Führerschein geprüft?", variable=lic_var).pack(pady=10)
        
        # Notes
        ttk.Label(dialog, text="Notizen:").pack(pady=5)
        note_entry = tk.Text(dialog, height=3)
        note_entry.pack(fill="x", padx=20)
        
        def save():
            if not v_cb.get() or not c_cb.get():
                messagebox.showerror("Fehler", "Bitte Fahrzeug und Kunde wählen.")
                return
            
            v_id = v_map[v_cb.get()]
            c_id = c_map[c_cb.get()]
            dt = date_entry.get()
            lic = lic_var.get()
            notes = note_entry.get("1.0", "end-1c")
            
            td = TestDrive(v_id, c_id, dt, lic, notes)
            database.add_test_drive(td)
            
            dialog.destroy()
            self.load_test_drives()
            
        ttk.Button(dialog, text="Speichern", command=save).pack(pady=20)

    def setup_settings(self):
        container = ttk.Frame(self.tab_settings, padding=20)
        container.pack(fill="both", expand=True)

        # --- COMPANY DATA ---
        lf_company = ttk.Labelframe(container, text="Firmendaten (für Verträge)", padding=15)
        lf_company.pack(fill="x", pady=10)

        grid_opts = {'padx': 5, 'pady': 5, 'sticky': 'ew'}

        ttk.Label(lf_company, text="Firmenname:").grid(row=0, column=0, **grid_opts)
        self.ent_company_name = ttk.Entry(lf_company)
        self.ent_company_name.grid(row=0, column=1, **grid_opts)
        self.create_copy_button(lf_company, self.ent_company_name).grid(row=0, column=2, padx=5)
        self.ent_company_name.insert(0, database.get_setting("company_name", "CAR Manager Händler"))

        ttk.Label(lf_company, text="Adresse:").grid(row=1, column=0, **grid_opts)
        self.ent_company_address = ttk.Entry(lf_company)
        self.ent_company_address.grid(row=1, column=1, **grid_opts)
        self.create_copy_button(lf_company, self.ent_company_address).grid(row=1, column=2, padx=5)
        self.ent_company_address.insert(0, database.get_setting("company_address", "Musterstraße 1, 12345 Musterstadt"))

        ttk.Label(lf_company, text="Fußzeile (Vertrag):").grid(row=2, column=0, **grid_opts)
        self.ent_company_footer = ttk.Entry(lf_company)
        self.ent_company_footer.grid(row=2, column=1, **grid_opts)
        self.create_copy_button(lf_company, self.ent_company_footer).grid(row=2, column=2, padx=5)
        self.ent_company_footer.insert(0, database.get_setting("company_footer", "Geschäftsführer: Max Mustermann | HRB 12345"))

        ttk.Label(lf_company, text="Logo Pfad:").grid(row=3, column=0, **grid_opts)
        self.ent_company_logo = ttk.Entry(lf_company)
        self.ent_company_logo.grid(row=3, column=1, **grid_opts)
        self.create_copy_button(lf_company, self.ent_company_logo).grid(row=3, column=3, padx=5)
        self.ent_company_logo.insert(0, database.get_setting("company_logo", ""))
        
        def choose_logo():
            path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
            if path:
                self.ent_company_logo.delete(0, "end")
                self.ent_company_logo.insert(0, path)
        
        ttk.Button(lf_company, text="...", width=3, command=choose_logo).grid(row=3, column=2, padx=5)

        lf_company.columnconfigure(1, weight=1)

        # --- SECURITY ---
        lf_security = ttk.Labelframe(container, text="Sicherheit", padding=15)
        lf_security.pack(fill="x", pady=10)
        
        ttk.Label(lf_security, text="Admin Passwort:").grid(row=0, column=0, **grid_opts)
        self.ent_admin_pwd = ttk.Entry(lf_security, show="*")
        self.ent_admin_pwd.grid(row=0, column=1, **grid_opts)
        self.create_copy_button(lf_security, self.ent_admin_pwd).grid(row=0, column=2, padx=5)
        self.ent_admin_pwd.insert(0, database.get_setting("admin_password", "admin"))
        
        lf_security.columnconfigure(1, weight=1)

        # --- EMAIL SETTINGS ---
        lf_email = ttk.Labelframe(container, text="Email Server (SMTP)", padding=15)
        lf_email.pack(fill="x", pady=10)

        ttk.Label(lf_email, text="SMTP Server:").grid(row=0, column=0, **grid_opts)
        self.ent_smtp_server = ttk.Entry(lf_email)
        self.ent_smtp_server.grid(row=0, column=1, **grid_opts)
        self.create_copy_button(lf_email, self.ent_smtp_server).grid(row=0, column=2, padx=5)
        self.ent_smtp_server.insert(0, database.get_setting("smtp_server", ""))

        ttk.Label(lf_email, text="Port:").grid(row=1, column=0, **grid_opts)
        self.ent_smtp_port = ttk.Entry(lf_email)
        self.ent_smtp_port.grid(row=1, column=1, **grid_opts)
        self.create_copy_button(lf_email, self.ent_smtp_port).grid(row=1, column=2, padx=5)
        self.ent_smtp_port.insert(0, database.get_setting("smtp_port", "587"))

        ttk.Label(lf_email, text="Benutzer (Email):").grid(row=2, column=0, **grid_opts)
        self.ent_smtp_user = ttk.Entry(lf_email)
        self.ent_smtp_user.grid(row=2, column=1, **grid_opts)
        self.create_copy_button(lf_email, self.ent_smtp_user).grid(row=2, column=2, padx=5)
        self.ent_smtp_user.insert(0, database.get_setting("smtp_user", ""))

        ttk.Label(lf_email, text="Passwort:").grid(row=3, column=0, **grid_opts)
        self.ent_smtp_pass = ttk.Entry(lf_email, show="*")
        self.ent_smtp_pass.grid(row=3, column=1, **grid_opts)
        self.create_copy_button(lf_email, self.ent_smtp_pass).grid(row=3, column=2, padx=5)
        self.ent_smtp_pass.insert(0, database.get_setting("smtp_password", ""))

        lf_email.columnconfigure(1, weight=1)

        # --- UPDATE SETTINGS ---
        lf_update = ttk.Labelframe(container, text="Software Update (GitHub)", padding=15)
        lf_update.pack(fill="x", pady=10)

        ttk.Label(lf_update, text="GitHub User/Org:").grid(row=0, column=0, **grid_opts)
        self.ent_github_owner = ttk.Entry(lf_update)
        self.ent_github_owner.grid(row=0, column=1, **grid_opts)
        self.create_copy_button(lf_update, self.ent_github_owner).grid(row=0, column=2, padx=5)
        
        # Default fallback
        gh_owner = database.get_setting("github_owner", "Nero3532")
        if not gh_owner: gh_owner = "Nero3532"
        self.ent_github_owner.insert(0, gh_owner)

        ttk.Label(lf_update, text="Repository:").grid(row=1, column=0, **grid_opts)
        self.ent_github_repo = ttk.Entry(lf_update)
        self.ent_github_repo.grid(row=1, column=1, **grid_opts)
        self.create_copy_button(lf_update, self.ent_github_repo).grid(row=1, column=2, padx=5)
        
        # Default fallback
        gh_repo = database.get_setting("github_repo", "Car-Manager-Pro")
        if not gh_repo: gh_repo = "Car-Manager-Pro"
        self.ent_github_repo.insert(0, gh_repo)
        
        def test_connection():
            owner = self.ent_github_owner.get()
            repo = self.ent_github_repo.get()
            if not owner or not repo:
                 messagebox.showwarning("Fehler", "Bitte User und Repo angeben.")
                 return
            
            url = f"https://api.github.com/repos/{owner}/{repo}"
            try:
                r = requests.get(url, timeout=5)
                if r.status_code == 200:
                    messagebox.showinfo("Erfolg", "Verbindung erfolgreich! Repository gefunden.")
                else:
                    messagebox.showerror("Fehler", f"Repository nicht gefunden (Status: {r.status_code})")
            except Exception as e:
                messagebox.showerror("Fehler", f"Verbindungsfehler: {e}")

        ttk.Button(lf_update, text="Nach Updates suchen", command=self.check_for_updates).grid(row=2, column=1, pady=10, sticky="w")
        ttk.Button(lf_update, text="Verbindung testen", command=test_connection, style="info.Outline.TButton").grid(row=2, column=1, pady=10, sticky="e")
        
        lf_update.columnconfigure(1, weight=1)

        def save_settings():
            database.set_setting("admin_password", self.ent_admin_pwd.get())
            database.set_setting("company_name", self.ent_company_name.get())
            database.set_setting("company_address", self.ent_company_address.get())
            database.set_setting("company_footer", self.ent_company_footer.get())
            database.set_setting("company_logo", self.ent_company_logo.get())
            
            database.set_setting("smtp_server", self.ent_smtp_server.get())
            database.set_setting("smtp_port", self.ent_smtp_port.get())
            database.set_setting("smtp_user", self.ent_smtp_user.get())
            database.set_setting("smtp_password", self.ent_smtp_pass.get())

            database.set_setting("github_owner", self.ent_github_owner.get())
            database.set_setting("github_repo", self.ent_github_repo.get())
            
            messagebox.showinfo("Erfolg", "Einstellungen gespeichert!")

        ttk.Button(container, text="💾 Einstellungen speichern", command=save_settings, style="success.TButton").pack(pady=20, anchor="e")

    # --- EXPOSE ---
    def _create_expose_html(self, vehicle):
        filename = f"expose_{vehicle.id}_{datetime.now().strftime('%Y%m%d')}.html"
        filepath = os.path.abspath(filename)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Fahrzeug Exposé: {vehicle.make} {vehicle.model}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                h1 {{ color: #333; border-bottom: 2px solid #333; padding-bottom: 10px; }}
                .info-box {{ background: #f9f9f9; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                .price {{ font-size: 24px; color: #d00; font-weight: bold; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                td, th {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>{vehicle.make} {vehicle.model}</h1>
            <div class="info-box">
                <p class="price">{vehicle.price:,.2f} €</p>
                <p><strong>Jahr:</strong> {vehicle.year} | <strong>Kilometer:</strong> {vehicle.mileage:,} km</p>
            </div>
            
            <h2>Details</h2>
            <table>
                <tr><th>Marke</th><td>{vehicle.make}</td></tr>
                <tr><th>Modell</th><td>{vehicle.model}</td></tr>
                <tr><th>Jahr</th><td>{vehicle.year}</td></tr>
                <tr><th>Kilometerstand</th><td>{vehicle.mileage} km</td></tr>
                <tr><th>Kraftstoff</th><td>{vehicle.fuel_type}</td></tr>
                <tr><th>Farbe</th><td>{vehicle.color}</td></tr>
                <tr><th>Zustand</th><td>{vehicle.condition}</td></tr>
                <tr><th>VIN</th><td>{vehicle.vin}</td></tr>
                <tr><th>TÜV fällig</th><td>{vehicle.tuv_due}</td></tr>
                <tr><th>Service fällig</th><td>{vehicle.service_due}</td></tr>
            </table>
            
            <p style="margin-top: 30px; font-size: 12px; color: #666;">
                Generiert am {datetime.now().strftime("%Y-%m-%d %H:%M")} mit CAR Manager.
            </p>
            
            <script>window.print();</script>
        </body>
        </html>
        """
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        return filepath

    def print_expose(self, vehicle):
        try:
            filepath = self._create_expose_html(vehicle)
            webbrowser.open(f"file://{filepath}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Erstellen des Exposés: {e}")

    def email_expose(self, vehicle):
        try:
            filepath = self._create_expose_html(vehicle)
            self.open_email_dialog(
                subject=f"Exposé: {vehicle.make} {vehicle.model}",
                body=f"Guten Tag,\n\nanbei erhalten Sie das Exposé für den {vehicle.make} {vehicle.model}.\n\nMit freundlichen Grüßen\nIhr Autohaus",
                attachment_path=filepath
            )
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Vorbereiten der Email: {e}")

    def check_for_updates(self):
        owner = self.ent_github_owner.get()
        repo = self.ent_github_repo.get()
        
        if not owner or not repo:
            messagebox.showwarning("Fehler", "Bitte GitHub User und Repository in den Einstellungen angeben.")
            return

        api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
        
        try:
            response = requests.get(api_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                latest_tag = data.get("tag_name", "").lstrip("v")
                html_url = data.get("html_url", "")
                
                if latest_tag != CURRENT_VERSION:
                     if messagebox.askyesno("Update verfügbar", f"Neue Version {latest_tag} verfügbar!\nAktuell: {CURRENT_VERSION}\n\nJetzt zur Download-Seite wechseln?"):
                         webbrowser.open(html_url)
                else:
                    messagebox.showinfo("Aktuell", f"Sie haben die neueste Version ({CURRENT_VERSION}).")
            elif response.status_code == 404:
                messagebox.showerror("Fehler", "Repository oder Release nicht gefunden.\nBitte Einstellungen prüfen.")
            else:
                messagebox.showerror("Fehler", f"Konnte Updates nicht prüfen.\nStatus: {response.status_code}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Update-Prüfung fehlgeschlagen: {e}")

if __name__ == "__main__":
    # Create upload dir if not exists
    config.get_uploads_path()
        
    # Init DB
    database.init_db()
    
    # Use ttkbootstrap Window
    root = ttk.Window(themename="superhero")
    
    # Resize for main app
    root.geometry("1200x800")
    root.title("CAR Manager Pro")
    
    # Start App
    app = CarManagerApp(root)
    
    root.mainloop()
