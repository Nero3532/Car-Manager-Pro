class Vehicle:
    def __init__(self, make, model, year, price, status, condition, mileage=0, color="", fuel_type="", vin="", owner_id=None, tuv_due="", service_due="", purchase_price=0.0, id=None):
        self.id = id
        self.make = make
        self.model = model
        self.year = year
        self.price = price
        self.status = status
        self.condition = condition
        self.mileage = mileage
        self.color = color
        self.fuel_type = fuel_type
        self.vin = vin
        self.owner_id = owner_id  # None = Dealer Stock, Integer = Customer ID
        self.tuv_due = tuv_due
        self.service_due = service_due
        self.purchase_price = purchase_price

    def __str__(self):
        return f"[{self.id}] {self.make} {self.model} ({self.year}) - {self.price}€"

class TestDrive:
    def __init__(self, vehicle_id, customer_id, date_time, license_check, notes, id=None):
        self.id = id
        self.vehicle_id = vehicle_id
        self.customer_id = customer_id
        self.date_time = date_time
        self.license_check = license_check
        self.notes = notes

class Customer:
    def __init__(self, name, phone, email, address, status="Interessent", notes="", id=None):
        self.id = id
        self.name = name
        self.phone = phone
        self.email = email
        self.address = address
        self.status = status # 'Interessent', 'Kunde', 'Inaktiv'
        self.notes = notes

class ServiceRecord:
    def __init__(self, vehicle_id, date, description, cost, labor_cost=0.0, parts_cost=0.0, materials="", id=None):
        self.id = id
        self.vehicle_id = vehicle_id
        self.date = date
        self.description = description
        self.cost = cost
        self.labor_cost = labor_cost
        self.parts_cost = parts_cost
        self.materials = materials

class Attachment:
    def __init__(self, vehicle_id, file_path, file_type, upload_date, service_id=None, id=None):
        self.id = id
        self.vehicle_id = vehicle_id
        self.service_id = service_id
        self.file_path = file_path
        self.file_type = file_type  # 'registration', 'photo', 'invoice', etc.
        self.upload_date = upload_date

class VehicleComment:
    def __init__(self, vehicle_id, content, timestamp, id=None):
        self.id = id
        self.vehicle_id = vehicle_id
        self.content = content
        self.timestamp = timestamp

class Part:
    def __init__(self, name, part_number, quantity, min_quantity, price, supplier="", storage_location="", id=None):
        self.id = id
        self.name = name
        self.part_number = part_number
        self.quantity = quantity
        self.min_quantity = min_quantity
        self.price = price
        self.supplier = supplier
        self.storage_location = storage_location

class Document:
    def __init__(self, doc_type, title, date_created, vehicle_id=None, customer_id=None, file_path="", id=None):
        self.id = id
        self.doc_type = doc_type # 'offer', 'contract', 'invoice', 'general'
        self.title = title
        self.date_created = date_created
        self.vehicle_id = vehicle_id
        self.customer_id = customer_id
        self.file_path = file_path
