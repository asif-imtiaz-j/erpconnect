from app.models import Invoice, Vendor, VendorScore
from datetime import date, timedelta
from sqlalchemy import func
from collections import defaultdict

# ========== REMINDERS ==========

def get_due_soon_invoices(days=7):
    today = date.today()
    upcoming = today + timedelta(days=days)
    return Invoice.query.filter(
        Invoice.status != 'paid',
        Invoice.due_date <= upcoming
    ).all()

def print_reminder_emails():
    invoices = get_due_soon_invoices()
    for i in invoices:
        print(f"📬 Reminder: Invoice #{i.invoice_number} from Vendor ID {i.vendor_id} is due on {i.due_date}. Amount: ${i.amount}")

# ========== TAGGING ==========

def parse_tags(tag_string):
    return [tag.strip().lower() for tag in tag_string.split(',') if tag.strip()]

# ========== SCORING ==========

def calculate_vendor_score(vendor_id):
    invoices = Invoice.query.filter_by(vendor_id=vendor_id).all()
    if not invoices:
        return

    total_amount = sum(i.amount for i in invoices)
    avg_invoice = total_amount / len(invoices)

    paid_on_time = sum(1 for i in invoices if i.status == 'paid' and i.due_date and i.created_at and i.created_at.date() <= i.due_date)
    on_time_rate = paid_on_time / len(invoices)

    reliability = round((on_time_rate + (1 if avg_invoice > 0 else 0)) / 2, 2)

    return VendorScore(
        vendor_id=vendor_id,
        avg_invoice_amount=round(avg_invoice, 2),
        on_time_rate=round(on_time_rate, 2),
        reliability_score=reliability
    )

# ========== CATEGORIZATION ==========

def auto_categorize_invoice(invoice):
    if 'amazon' in invoice.invoice_number.lower():
        invoice.category = 'Office Supplies'
    elif 'uber' in invoice.invoice_number.lower():
        invoice.category = 'Travel'
    elif invoice.amount > 5000:
        invoice.category = 'Capital Expense'
    else:
        invoice.category = 'General'

# ========== FORECASTING (Rolling Avg) ==========

def forecast_invoice_totals_by_month(history):
    if not history:
        return []

    avg = sum(history) / len(history)
    forecast = [round(avg, 2)] * 3  # forecast next 3 months
    return forecast

# ========== EXPORT FILTERS ==========

def filter_invoices_by_form(query, form):
    if form.status_filter.data:
        query = query.filter(Invoice.status == form.status_filter.data)
    if form.category_filter.data:
        query = query.filter(Invoice.category.ilike(f"%{form.category_filter.data.strip()}%"))
    return query
