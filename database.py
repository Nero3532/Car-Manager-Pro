import sqlite3
import shutil
import os
from datetime import datetime
from models import Vehicle, Customer, ServiceRecord, Attachment, VehicleComment, TestDrive, Part, Document
import app_config as config

DB_NAME = config.get_db_path()

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Vehicles Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            make TEXT NOT NULL,
            model TEXT NOT NULL,
            year INTEGER NOT NULL,
            price REAL NOT NULL,
            status TEXT NOT NULL,
            condition TEXT NOT NULL,
            mileage INTEGER DEFAULT 0,
            color TEXT DEFAULT '',
            fuel_type TEXT DEFAULT '',
            vin TEXT DEFAULT '',
            owner_id INTEGER,
            tuv_due TEXT DEFAULT '',
            service_due TEXT DEFAULT ''
        )
    """)

    # Check for columns and migrate if needed
    cursor.execute("PRAGMA table_info(vehicles)")
    columns = [info[1] for info in cursor.fetchall()]
    
    new_cols = {
        "mileage": "INTEGER DEFAULT 0",
        "color": "TEXT DEFAULT ''",
        "fuel_type": "TEXT DEFAULT ''",
        "vin": "TEXT DEFAULT ''",
        "owner_id": "INTEGER",
        "tuv_due": "TEXT DEFAULT ''",
        "service_due": "TEXT DEFAULT ''",
        "purchase_price": "REAL DEFAULT 0.0"
    }
    
    for col, definition in new_cols.items():
        if col not in columns:
            try:
                print(f"Migrating DB: Adding column {col}...")
                cursor.execute(f"ALTER TABLE vehicles ADD COLUMN {col} {definition}")
            except Exception as e:
                print(f"Migration error for {col}: {e}")

    # Customers Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT
        )
    """)
    
    # Service History Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS service_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER,
            date TEXT,
            description TEXT,
            cost REAL,
            labor_cost REAL DEFAULT 0,
            parts_cost REAL DEFAULT 0,
            materials TEXT DEFAULT '',
            FOREIGN KEY(vehicle_id) REFERENCES vehicles(id)
        )
    """)

    # Migrate service_history
    cursor.execute("PRAGMA table_info(service_history)")
    sh_cols = [info[1] for info in cursor.fetchall()]
    new_sh_cols = {
        "labor_cost": "REAL DEFAULT 0",
        "parts_cost": "REAL DEFAULT 0",
        "materials": "TEXT DEFAULT ''"
    }
    for col, definition in new_sh_cols.items():
        if col not in sh_cols:
            try:
                print(f"Migrating DB: Adding column {col} to service_history...")
                cursor.execute(f"ALTER TABLE service_history ADD COLUMN {col} {definition}")
            except Exception as e:
                print(f"Migration error for service_history {col}: {e}")

    # Migrate customers
    cursor.execute("PRAGMA table_info(customers)")
    cust_cols = [info[1] for info in cursor.fetchall()]
    new_cust_cols = {
        "status": "TEXT DEFAULT 'Interessent'",
        "notes": "TEXT DEFAULT ''"
    }
    for col, definition in new_cust_cols.items():
        if col not in cust_cols:
            try:
                print(f"Migrating DB: Adding column {col} to customers...")
                cursor.execute(f"ALTER TABLE customers ADD COLUMN {col} {definition}")
            except Exception as e:
                print(f"Migration error for customers {col}: {e}")
    
    # Attachments Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER,
            service_id INTEGER,
            file_path TEXT,
            file_type TEXT,
            upload_date TEXT,
            FOREIGN KEY(vehicle_id) REFERENCES vehicles(id)
        )
    """)

    # Comments Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicle_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER,
            content TEXT,
            timestamp TEXT,
            FOREIGN KEY(vehicle_id) REFERENCES vehicles(id)
        )
    """)

    # Test Drives Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_drives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER,
            customer_id INTEGER,
            date_time TEXT,
            license_check INTEGER,
            notes TEXT,
            FOREIGN KEY(vehicle_id) REFERENCES vehicles(id),
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        )
    """)

    # Migrate attachments
    cursor.execute("PRAGMA table_info(attachments)")
    att_cols = [info[1] for info in cursor.fetchall()]
    if "service_id" not in att_cols:
        try:
            print("Migrating DB: Adding column service_id to attachments...")
            cursor.execute("ALTER TABLE attachments ADD COLUMN service_id INTEGER")
        except Exception as e:
            print(f"Migration error for attachments service_id: {e}")

    # Documents Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_type TEXT,
            title TEXT,
            date_created TEXT,
            vehicle_id INTEGER,
            customer_id INTEGER,
            file_path TEXT,
            FOREIGN KEY(vehicle_id) REFERENCES vehicles(id),
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        )
    """)

    # Parts Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            part_number TEXT,
            quantity INTEGER DEFAULT 0,
            min_quantity INTEGER DEFAULT 0,
            price REAL DEFAULT 0.0,
            supplier TEXT,
            storage_location TEXT
        )
    """)

    # Settings Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    
    conn.commit()
    conn.close()

# --- PARTS ---
def add_part(part):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO parts (name, part_number, quantity, min_quantity, price, supplier, storage_location)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (part.name, part.part_number, part.quantity, part.min_quantity, part.price, part.supplier, part.storage_location))
    part_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return part_id

def get_parts():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM parts ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return [Part(row[1], row[2], row[3], row[4], row[5], row[6], row[7], id=row[0]) for row in rows]

def update_part(part):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE parts SET name=?, part_number=?, quantity=?, min_quantity=?, price=?, supplier=?, storage_location=?
        WHERE id=?
    """, (part.name, part.part_number, part.quantity, part.min_quantity, part.price, part.supplier, part.storage_location, part.id))
    conn.commit()
    conn.close()

def delete_part(part_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM parts WHERE id=?", (part_id,))
    conn.commit()
    conn.close()

# --- DOCUMENTS ---
def add_document(doc):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO documents (doc_type, title, date_created, vehicle_id, customer_id, file_path)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (doc.doc_type, doc.title, doc.date_created, doc.vehicle_id, doc.customer_id, doc.file_path))
    doc_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return doc_id

def get_documents():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents ORDER BY date_created DESC")
    rows = cursor.fetchall()
    conn.close()
    return [Document(row[1], row[2], row[3], row[4], row[5], row[6], id=row[0]) for row in rows]

def get_documents_by_vehicle(vehicle_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE vehicle_id=? ORDER BY date_created DESC", (vehicle_id,))
    rows = cursor.fetchall()
    conn.close()
    return [Document(row[1], row[2], row[3], row[4], row[5], row[6], id=row[0]) for row in rows]

def delete_document(doc_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM documents WHERE id=?", (doc_id,))
    conn.commit()
    conn.close()

def update_document(doc):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE documents SET doc_type=?, title=? WHERE id=?", 
                   (doc.doc_type, doc.title, doc.id))
    conn.commit()
    conn.close()

def backup_database():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = config.get_backups_path()
    backup_file = os.path.join(backup_dir, f"backup_{timestamp}.db")
    shutil.copy(DB_NAME, backup_file)
    return backup_file

# --- SETTINGS ---
def get_setting(key, default=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else default

def set_setting(key, value):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()



def get_todos_for_date(date_str):
    todos = []
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. TUV Due
    cursor.execute("SELECT id, make, model FROM vehicles WHERE tuv_due = ?", (date_str,))
    for row in cursor.fetchall():
        todos.append({"type": "TÜV", "text": f"TÜV fällig: {row[1]} {row[2]}", "id": row[0]})
        
    # 2. Service Due
    cursor.execute("SELECT id, make, model FROM vehicles WHERE service_due = ?", (date_str,))
    for row in cursor.fetchall():
        todos.append({"type": "Service", "text": f"Service fällig: {row[1]} {row[2]}", "id": row[0]})
        
    # 3. Test Drives
    try:
        cursor.execute("""
            SELECT t.id, v.make, v.model, c.name, t.date_time 
            FROM test_drives t
            JOIN vehicles v ON t.vehicle_id = v.id
            JOIN customers c ON t.customer_id = c.id
            WHERE substr(t.date_time, 1, 10) = ?
        """, (date_str,))
        for row in cursor.fetchall():
            time_part = row[4][11:] if len(row[4]) > 10 else ""
            todos.append({"type": "Probefahrt", "text": f"Probefahrt {time_part}: {row[3]} ({row[1]})", "id": row[0]})
    except:
        pass
        
    conn.close()
    return todos

# --- VEHICLES ---
def add_vehicle(vehicle):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO vehicles (make, model, year, price, status, condition, mileage, color, fuel_type, vin, owner_id, tuv_due, service_due, purchase_price)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (vehicle.make, vehicle.model, vehicle.year, vehicle.price, vehicle.status, vehicle.condition, 
          vehicle.mileage, vehicle.color, vehicle.fuel_type, vehicle.vin, vehicle.owner_id, vehicle.tuv_due, vehicle.service_due, vehicle.purchase_price))
    conn.commit()
    conn.close()

def get_all_vehicles():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vehicles")
    rows = cursor.fetchall()
    conn.close()
    
    vehicles = []
    for row in rows:
        # Check if row has enough columns (in case of very old weird state, but migration should fix)
        # Expected: id(0), make(1), model(2), year(3), price(4), status(5), condition(6), 
        #           mileage(7), color(8), fuel_type(9), vin(10), owner_id(11), tuv_due(12), service_due(13), purchase_price(14)
        
        # Handle cases where migration might have failed or order is diff (basic mapping)
        v = Vehicle(
            id=row[0],
            make=row[1], model=row[2], year=row[3], price=row[4], status=row[5], condition=row[6],
            mileage=row[7] if len(row) > 7 else 0,
            color=row[8] if len(row) > 8 else "",
            fuel_type=row[9] if len(row) > 9 else "",
            vin=row[10] if len(row) > 10 else "",
            owner_id=row[11] if len(row) > 11 else None,
            tuv_due=row[12] if len(row) > 12 else "",
            service_due=row[13] if len(row) > 13 else "",
            purchase_price=row[14] if len(row) > 14 else 0.0
        )
        vehicles.append(v)
    return vehicles

def update_vehicle(vehicle):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE vehicles 
        SET make=?, model=?, year=?, price=?, status=?, condition=?, 
        mileage=?, color=?, fuel_type=?, vin=?, owner_id=?, tuv_due=?, service_due=?, purchase_price=?
        WHERE id=?
    """, (vehicle.make, vehicle.model, vehicle.year, vehicle.price, vehicle.status, vehicle.condition,
          vehicle.mileage, vehicle.color, vehicle.fuel_type, vehicle.vin, vehicle.owner_id, vehicle.tuv_due, vehicle.service_due, vehicle.purchase_price, vehicle.id))
    conn.commit()
    conn.close()

def update_status(vehicle_id, new_status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE vehicles SET status = ? WHERE id = ?", (new_status, vehicle_id))
    conn.commit()
    conn.close()

def delete_vehicle(vehicle_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vehicles WHERE id = ?", (vehicle_id,))
    conn.commit()
    conn.close()

# --- CUSTOMERS ---
def add_customer(customer):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO customers (name, phone, email, address, status, notes) VALUES (?, ?, ?, ?, ?, ?)",
                   (customer.name, customer.phone, customer.email, customer.address, customer.status, customer.notes))
    conn.commit()
    conn.close()

def get_customers():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers")
    rows = cursor.fetchall()
    conn.close()
    customers = []
    for row in rows:
        # Check if row has new columns (migrated vs new)
        # Standard: id, name, phone, email, address (5 cols)
        # New: status, notes (7 cols)
        status = row[5] if len(row) > 5 else "Interessent"
        notes = row[6] if len(row) > 6 else ""
        customers.append(Customer(row[1], row[2], row[3], row[4], status=status, notes=notes, id=row[0]))
    return customers

def get_all_customers():
    return get_customers()

def update_customer(customer):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE customers SET name=?, phone=?, email=?, address=?, status=?, notes=? WHERE id=?",
                   (customer.name, customer.phone, customer.email, customer.address, customer.status, customer.notes, customer.id))
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*), SUM(price) FROM vehicles")
    v_stats = cursor.fetchone()
    total_count = v_stats[0] if v_stats[0] else 0
    total_value = v_stats[1] if v_stats[1] else 0.0
    
    cursor.execute("SELECT status, COUNT(*) FROM vehicles GROUP BY status")
    status_counts = dict(cursor.fetchall())
    
    conn.close()
    
    return {
        "total_count": total_count,
        "total_value": total_value,
        "status_counts": status_counts,
        "total_sales_count": 0,
        "total_revenue": 0.0
    }

# --- SERVICE HISTORY ---
def add_service_record(record):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO service_history (vehicle_id, date, description, cost, labor_cost, parts_cost, materials)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (record.vehicle_id, record.date, record.description, record.cost, 
          record.labor_cost, record.parts_cost, record.materials))
    record.id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record.id

def get_service_history(vehicle_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM service_history WHERE vehicle_id = ?", (vehicle_id,))
    rows = cursor.fetchall()
    conn.close()
    
    records = []
    for row in rows:
        # 0:id, 1:vehicle_id, 2:date, 3:description, 4:cost
        # Optional: 5:labor_cost, 6:parts_cost, 7:materials
        labor = row[5] if len(row) > 5 else 0
        parts = row[6] if len(row) > 6 else 0
        materials = row[7] if len(row) > 7 else ""
        
        r = ServiceRecord(row[1], row[2], row[3], row[4], labor_cost=labor, parts_cost=parts, materials=materials, id=row[0])
        records.append(r)
    return records

# --- ATTACHMENTS ---
def add_attachment(attachment):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO attachments (vehicle_id, file_path, file_type, upload_date, service_id) 
        VALUES (?, ?, ?, ?, ?)
    """, (attachment.vehicle_id, attachment.file_path, attachment.file_type, attachment.upload_date, attachment.service_id))
    conn.commit()
    conn.close()

def get_attachments(vehicle_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attachments WHERE vehicle_id = ?", (vehicle_id,))
    rows = cursor.fetchall()
    conn.close()
    
    atts = []
    for row in rows:
        # 0:id, 1:vehicle_id, 2:service_id, 3:file_path, 4:file_type, 5:upload_date
        # Check column order based on schema evolution or just robust reading
        # Based on CREATE TABLE: id, vehicle_id, service_id, file_path, file_type, upload_date
        # But if old schema, service_id might be missing or added later.
        # Let's rely on standard order if migration works.
        
        # NOTE: If service_id was added later via ALTER, it's the last column? 
        # Actually in init_db we add it if missing.
        # Let's check typical fetchall result.
        pass
    
    # Simpler approach:
    # Just query standard columns
    return get_attachments_robust(vehicle_id)

def get_attachments_robust(vehicle_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attachments WHERE vehicle_id = ?", (vehicle_id,))
    rows = cursor.fetchall()
    conn.close()
    
    atts = []
    for row in rows:
        # row is a dict-like object
        sid = row['service_id'] if 'service_id' in row.keys() else None
        a = Attachment(row['vehicle_id'], row['file_path'], row['file_type'], row['upload_date'], service_id=sid, id=row['id'])
        atts.append(a)
    return atts

# --- COMMENTS ---
def add_comment(comment):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO vehicle_comments (vehicle_id, content, timestamp) VALUES (?, ?, ?)",
                   (comment.vehicle_id, comment.content, comment.timestamp))
    conn.commit()
    conn.close()

def get_comments(vehicle_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vehicle_comments WHERE vehicle_id = ? ORDER BY id DESC", (vehicle_id,))
    rows = cursor.fetchall()
    conn.close()
    return [VehicleComment(row[1], row[2], row[3], id=row[0]) for row in rows]

# --- TEST DRIVES ---
def add_test_drive(td):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO test_drives (vehicle_id, customer_id, date_time, license_check, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (td.vehicle_id, td.customer_id, td.date_time, 1 if td.license_check else 0, td.notes))
    td.id = cursor.lastrowid
    conn.commit()
    conn.close()
    return td.id

def get_test_drives():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT td.id, td.vehicle_id, td.customer_id, td.date_time, td.license_check, td.notes,
               v.make, v.model, c.name
        FROM test_drives td
        LEFT JOIN vehicles v ON td.vehicle_id = v.id
        LEFT JOIN customers c ON td.customer_id = c.id
        ORDER BY td.date_time DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        td = TestDrive(row[1], row[2], row[3], bool(row[4]), row[5], id=row[0])
        td.vehicle_name = f"{row[6]} {row[7]}" if row[6] else "Unbekannt"
        td.customer_name = row[8] if row[8] else "Unbekannt"
        results.append(td)
    return results

def delete_test_drive(td_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM test_drives WHERE id = ?", (td_id,))
    conn.commit()
    conn.close()
