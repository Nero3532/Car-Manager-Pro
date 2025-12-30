import sys
from models import Vehicle
import database

def print_menu():
    print("\n--- Autohändler & Werkstatt Management ---")
    print("1. Fahrzeug hinzufügen")
    print("2. Alle Fahrzeuge anzeigen")
    print("3. Fahrzeugstatus ändern (z.B. In Werkstatt)")
    print("4. Fahrzeug löschen")
    print("5. Beenden")

def add_vehicle_ui():
    print("\n--- Neues Fahrzeug hinzufügen ---")
    make = input("Marke: ")
    model = input("Modell: ")
    try:
        year = int(input("Baujahr: "))
        price = float(input("Preis (€): "))
    except ValueError:
        print("Fehler: Bitte gültige Zahlen für Jahr und Preis eingeben.")
        return

    print("Zustand wählen:")
    print("1. Neu")
    print("2. Gebraucht")
    c_choice = input("Auswahl (1/2): ")
    condition = "Neu" if c_choice == "1" else "Gebraucht"

    status = "Verfügbar"

    vehicle = Vehicle(make, model, year, price, status, condition)
    database.add_vehicle(vehicle)
    print("Fahrzeug erfolgreich hinzugefügt!")

def list_vehicles_ui():
    print("\n--- Fahrzeugliste ---")
    vehicles = database.get_all_vehicles()
    if not vehicles:
        print("Keine Fahrzeuge vorhanden.")
    else:
        for v in vehicles:
            print(v)

def update_status_ui():
    list_vehicles_ui()
    try:
        v_id = int(input("\nID des Fahrzeugs zum Ändern: "))
    except ValueError:
        print("Ungültige ID.")
        return

    print("Neuer Status:")
    print("1. Verfügbar")
    print("2. Verkauft")
    print("3. In Werkstatt")
    s_choice = input("Auswahl (1-3): ")
    
    status_map = {
        "1": "Verfügbar",
        "2": "Verkauft",
        "3": "In Werkstatt"
    }
    
    new_status = status_map.get(s_choice)
    if new_status:
        database.update_status(v_id, new_status)
        print("Status aktualisiert!")
    else:
        print("Ungültige Auswahl.")

def delete_vehicle_ui():
    list_vehicles_ui()
    try:
        v_id = int(input("\nID des zu löschenden Fahrzeugs: "))
        confirm = input(f"Fahrzeug {v_id} wirklich löschen? (j/n): ")
        if confirm.lower() == 'j':
            database.delete_vehicle(v_id)
            print("Fahrzeug gelöscht.")
    except ValueError:
        print("Ungültige ID.")

def main():
    database.init_db()
    while True:
        print_menu()
        choice = input("Auswahl: ")
        
        if choice == "1":
            add_vehicle_ui()
        elif choice == "2":
            list_vehicles_ui()
        elif choice == "3":
            update_status_ui()
        elif choice == "4":
            delete_vehicle_ui()
        elif choice == "5":
            print("Programm beendet.")
            sys.exit()
        else:
            print("Ungültige Eingabe.")

if __name__ == "__main__":
    main()
