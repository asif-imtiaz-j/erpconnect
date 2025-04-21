from app import create_app, db
from app.models import User, Vendor, Invoice
from werkzeug.security import generate_password_hash
from faker import Faker
import random

app = create_app()
faker = Faker()

with app.app_context():
    db.drop_all()
    db.create_all()

    # Create admin user
    admin = User(username="admin", password=generate_password_hash("admin123"), role="admin")
    db.session.add(admin)

    # Create fake vendors
    vendors = []
    for _ in range(10):
        vendor = Vendor(
            name=faker.company(),
            contact_info=faker.email(),
            address=faker.address(),
            status=random.choice(["active", "inactive"])
        )
        db.session.add(vendor)
        vendors.append(vendor)

    db.session.flush()

    # Create fake invoices
    for _ in range(30):
        invoice = Invoice(
            invoice_number=faker.unique.bothify(text="INV####"),
            vendor_id=random.choice(vendors).id,
            amount=round(random.uniform(100.0, 5000.0), 2),
            status=random.choice(["paid", "unpaid"]),
            upload_path=""
        )
        db.session.add(invoice)

    db.session.commit()
    print("✅ Realistic sample data seeded.")
