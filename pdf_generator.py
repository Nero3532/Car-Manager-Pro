
from fpdf import FPDF
import datetime
import os

class PDFGenerator:
    def __init__(self, output_dir="documents"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_sales_contract(self, vehicle, customer, price, date=None):
        if date is None:
            date = datetime.datetime.now().strftime("%d.%m.%Y")

        pdf = FPDF()
        pdf.add_page()
        
        # --- KOPFZEILE ---
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "KAUFVERTRAG", 0, 1, "C")
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 10, "über ein gebrauchtes Kraftfahrzeug", 0, 1, "C")
        pdf.ln(10)

        # --- VERKÄUFER ---
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "1. Verkäufer (Händler)", 0, 1)
        pdf.set_font("Arial", "", 11)
        # Hier könnten Händlerdaten aus einer Config kommen
        pdf.cell(0, 6, "Firma: Mein Autohandel", 0, 1) 
        pdf.cell(0, 6, "Adresse: Musterstraße 1, 12345 Musterstadt", 0, 1)
        pdf.ln(5)

        # --- KÄUFER ---
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "2. Käufer", 0, 1)
        pdf.set_font("Arial", "", 11)
        if customer:
            pdf.cell(0, 6, f"Name: {customer.name}", 0, 1)
            pdf.cell(0, 6, f"Adresse: {customer.address}", 0, 1)
            pdf.cell(0, 6, f"Telefon: {customer.phone}", 0, 1)
        else:
            pdf.cell(0, 6, "Name: __________________________", 0, 1)
            pdf.cell(0, 6, "Adresse: ________________________", 0, 1)
        pdf.ln(5)

        # --- FAHRZEUG ---
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "3. Fahrzeugdaten", 0, 1)
        pdf.set_font("Arial", "", 11)
        
        col_w = 45
        val_w = 100
        
        pdf.cell(col_w, 7, "Marke / Modell:", 0, 0)
        pdf.cell(val_w, 7, f"{vehicle.make} {vehicle.model}", 0, 1)
        
        pdf.cell(col_w, 7, "Fahrgestellnr. (VIN):", 0, 0)
        pdf.cell(val_w, 7, str(vehicle.vin), 0, 1)
        
        pdf.cell(col_w, 7, "Erstzulassung/Bj:", 0, 0)
        pdf.cell(val_w, 7, str(vehicle.year), 0, 1)
        
        pdf.cell(col_w, 7, "Kilometerstand:", 0, 0)
        pdf.cell(val_w, 7, f"{vehicle.mileage} km", 0, 1)
        
        pdf.ln(5)

        # --- KAUFPREIS ---
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "4. Kaufpreis", 0, 1)
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 8, f"Der Kaufpreis beträgt: {price:,.2f} EUR", 0, 1)
        pdf.set_font("Arial", "I", 10)
        pdf.cell(0, 6, "(In Worten: ...)", 0, 1)
        pdf.ln(5)

        # --- GEWÄHRLEISTUNG ---
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "5. Gewährleistung / Zustand", 0, 1)
        pdf.set_font("Arial", "", 10)
        text = ("Das Fahrzeug wird wie besichtigt und unter Ausschluss jeglicher Gewährleistung verkauft, "
                "soweit nicht nachfolgend ausdrücklich etwas anderes vereinbart wird. "
                "Der Ausschluss gilt nicht für Schadensersatzansprüche aus grob fahrlässiger "
                "oder vorsätzlicher Verletzung von Pflichten des Verkäufers sowie für jede Verletzung "
                "von Leben, Körper und Gesundheit.")
        pdf.multi_cell(0, 5, text)
        pdf.ln(5)

        # --- UNTERSCHRIFTEN ---
        pdf.ln(20)
        pdf.cell(0, 6, f"Ort, Datum: ________________, {date}", 0, 1)
        pdf.ln(15)
        
        y = pdf.get_y()
        pdf.line(10, y, 90, y)
        pdf.line(110, y, 190, y)
        
        pdf.cell(90, 5, "Unterschrift Verkäufer", 0, 0, "C")
        pdf.cell(10, 5, "", 0, 0)
        pdf.cell(90, 5, "Unterschrift Käufer", 0, 1, "C")

        filename = f"Kaufvertrag_{vehicle.make}_{vehicle.model}_{date}.pdf".replace(" ", "_").replace("/", "-")
        filepath = os.path.join(self.output_dir, filename)
        
        pdf.output(filepath, 'F')
        return filepath

    def generate_expose(self, vehicle, attachments=None):
        date = datetime.datetime.now().strftime("%d.%m.%Y")
        pdf = FPDF()
        pdf.add_page()
        
        # --- HEADER ---
        pdf.set_font("Arial", "B", 20)
        pdf.cell(0, 15, f"{vehicle.make} {vehicle.model}", 0, 1, "C")
        
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"Preis: {vehicle.price:,.2f} EUR", 0, 1, "C")
        pdf.ln(5)
        
        # --- HAUPTBILD (Erstes Bild aus Attachments) ---
        main_image = None
        other_images = []
        
        if attachments:
            for att in attachments:
                # Check extension roughly or use file_type if reliable
                if att.file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                    if main_image is None:
                        main_image = att.file_path
                    else:
                        other_images.append(att.file_path)
        
        if main_image and os.path.exists(main_image):
            try:
                # Zentriert, Breite 150
                pdf.image(main_image, x=30, w=150)
                pdf.ln(5)
            except Exception as e:
                print(f"Error loading image {main_image}: {e}")
                pdf.cell(0, 10, "(Bild konnte nicht geladen werden)", 0, 1, "C")
        
        pdf.ln(10)
        
        # --- DATEN ---
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Fahrzeugdaten", 0, 1)
        pdf.set_font("Arial", "", 11)
        
        # Grid layout for details
        details = [
            ("Erstzulassung", str(vehicle.year)),
            ("Kilometerstand", f"{vehicle.mileage} km"),
            ("Leistung/Motor", str(vehicle.fuel_type)), # Mapping fuel_type/power if available
            ("Farbe", vehicle.color),
            ("Zustand", vehicle.status),
            ("VIN", vehicle.vin),
            ("TÜV bis", vehicle.tuv_due)
        ]
        
        for label, value in details:
            pdf.cell(50, 8, label + ":", 0, 0)
            pdf.cell(0, 8, str(value), 0, 1)
            
        pdf.ln(5)
        
        # --- BESCHREIBUNG ---
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Beschreibung / Ausstattung", 0, 1)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 6, f"Zustand: {vehicle.condition}\n\nEin sehr gepflegtes Fahrzeug...") 
        # Here we could add more text if vehicle has a description field
        
        pdf.ln(10)
        
        # --- WEITERE BILDER (Gallery) ---
        if other_images:
            pdf.add_page()
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Bildergalerie", 0, 1)
            
            # Simple grid: 2 per row
            x_start = 10
            y_start = 30
            w = 90
            h = 60 # approx aspect ratio
            
            x = x_start
            y = y_start
            
            count = 0
            for img_path in other_images[:4]: # Limit to 4 for now
                if os.path.exists(img_path):
                    try:
                        pdf.image(img_path, x=x, y=y, w=w, h=h)
                        count += 1
                        if count % 2 == 0:
                            x = x_start
                            y += h + 10
                        else:
                            x += w + 10
                    except:
                        pass
                        
        # --- FUSSZEILE ---
        pdf.set_y(-30)
        pdf.set_font("Arial", "I", 8)
        pdf.cell(0, 10, "Alle Angaben ohne Gewähr. Zwischenverkauf vorbehalten.", 0, 1, "C")
        pdf.cell(0, 5, "Erstellt mit CAR Manager Pro", 0, 1, "C")

        filename = f"Expose_{vehicle.make}_{vehicle.model}_{date}.pdf".replace(" ", "_").replace("/", "-")
        filepath = os.path.join(self.output_dir, filename)
        
        pdf.output(filepath, 'F')
        return filepath
