import os
from pdf_generator import PDFGenerator
from models import Vehicle

def create_sample():
    v = Vehicle(
        make="Volkswagen",
        model="Golf VII GTI",
        year=2020,
        price=24500.00,
        status="Verfügbar",
        condition="Gebraucht",
        mileage=45000,
        color="Weiß",
        fuel_type="Benzin",
        vin="WVWZZZAUZLW123456",
        tuv_due="05/2025",
        service_due="05/2024",
        purchase_price=20000.00
    )
    
    gen = PDFGenerator()
    path = gen.generate_expose(v, [])
    print(f"Sample Expose generated: {path}")

if __name__ == "__main__":
    create_sample()
