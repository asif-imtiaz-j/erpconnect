from flask import Blueprint, render_template, redirect, url_for, flash, request, Response
from flask_login import login_required, current_user
from app.models import Vendor, Invoice, User, InvoiceAnnotation, InvoiceMessage, InvoiceTag, VendorScore
from app.forms import VendorForm, InvoiceForm, InvoiceMessageForm, InvoiceAnnotationForm, ReportBuilderForm
from werkzeug.utils import secure_filename
from app import db
import os
import datetime
import csv, io
from sqlalchemy import extract
from app.utils import parse_tags, auto_categorize_invoice, calculate_vendor_score, filter_invoices_by_form, forecast_invoice_totals_by_month

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def home():
    total_vendors = Vendor.query.count()
    total_invoices = Invoice.query.count()
    unpaid_total = db.session.query(db.func.sum(Invoice.amount)).filter(Invoice.status == 'unpaid').scalar() or 0
    unpaid_count = Invoice.query.filter_by(status='unpaid').count()
    paid_count = Invoice.query.filter_by(status='paid').count()

    today = datetime.date.today()
    month_labels, monthly_totals = [], []
    for i in range(5, -1, -1):
        target = today.replace(day=1) - datetime.timedelta(days=i*30)
        label = target.strftime("%b %Y")
        total = db.session.query(db.func.sum(Invoice.amount)).filter(
            extract('month', Invoice.created_at) == target.month,
            extract('year', Invoice.created_at) == target.year
        ).scalar() or 0
        month_labels.append(label)
        monthly_totals.append(round(total, 2))

    forecast = forecast_invoice_totals_by_month(monthly_totals)

    return render_template(
        'dashboard.html',
        total_vendors=total_vendors,
        total_invoices=total_invoices,
        unpaid_total=unpaid_total,
        paid_count=paid_count,
        unpaid_count=unpaid_count,
        month_labels=month_labels,
        monthly_totals=monthly_totals,
        forecast_totals=forecast
    )

@main.route('/vendors')
@login_required
def vendors():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    return render_template('vendors.html', vendors=Vendor.query.all())

@main.route('/vendors/add', methods=['GET', 'POST'])
@login_required
def add_vendor():
    if current_user.role != 'admin':
        return redirect(url_for('main.home'))
    form = VendorForm()
    if form.validate_on_submit():
        vendor = Vendor(name=form.name.data, contact_info=form.contact_info.data, address=form.address.data, status=form.status.data)
        db.session.add(vendor)
        db.session.commit()
        return redirect(url_for('main.vendors'))
    return render_template('vendor_form.html', form=form, title="Add Vendor")

@main.route('/invoices')
@login_required
def invoices():
    if current_user.role != 'admin':
        flash("Access denied.", 'danger')
        return redirect(url_for('main.home'))
    return render_template('invoices.html', invoices=Invoice.query.all(), vendors=Vendor.query.all())

@main.route('/invoices/add', methods=['GET', 'POST'])
@login_required
def add_invoice():
    if current_user.role != 'admin':
        return redirect(url_for('main.home'))
    form = InvoiceForm()
    if form.validate_on_submit():
        file = request.files['file']
        filename = secure_filename(file.filename)
        upload_folder = os.path.join('app', 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        path = os.path.join(upload_folder, filename)
        file.save(path)

        invoice = Invoice(
            invoice_number=form.invoice_number.data,
            vendor_id=request.form['vendor_id'],
            amount=form.amount.data,
            status=form.status.data,
            category=form.category.data or None,
            due_date=form.due_date.data,
            approved=form.approved.data,
            upload_path=path
        )

        if not invoice.category:
            auto_categorize_invoice(invoice)

        tags = parse_tags(form.tags.data)
        for tag in tags:
            invoice.tags.append(InvoiceTag(tag=tag))

        db.session.add(invoice)
        db.session.commit()
        return redirect(url_for('main.invoices'))
    return render_template('invoice_form.html', form=form, vendors=Vendor.query.all(), title="Add Invoice")

@main.route('/invoice/<int:invoice_id>')
@login_required
def view_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    annotation_form = InvoiceAnnotationForm()
    message_form = InvoiceMessageForm()
    return render_template('invoice_detail.html', invoice=invoice, annotation_form=annotation_form, message_form=message_form)

@main.route('/invoice/<int:invoice_id>/add_note', methods=['POST'])
@login_required
def add_annotation(invoice_id):
    form = InvoiceAnnotationForm()
    if form.validate_on_submit():
        db.session.add(InvoiceAnnotation(invoice_id=invoice_id, content=form.content.data))
        db.session.commit()
    return redirect(url_for('main.view_invoice', invoice_id=invoice_id))

@main.route('/invoice/<int:invoice_id>/add_message', methods=['POST'])
@login_required
def add_invoice_message(invoice_id):
    form = InvoiceMessageForm()
    if form.validate_on_submit():
        db.session.add(InvoiceMessage(invoice_id=invoice_id, sender=current_user.username, message=form.message.data))
        db.session.commit()
    return redirect(url_for('main.view_invoice', invoice_id=invoice_id))

@main.route('/dashboard/charts')
@login_required
def dashboard_charts():
    months = int(request.args.get('months', 6))
    today = datetime.date.today()
    month_labels, monthly_totals = [], []
    for i in range(months-1, -1, -1):
        target = today.replace(day=1) - datetime.timedelta(days=i*30)
        label = target.strftime("%b %Y")
        total = db.session.query(db.func.sum(Invoice.amount)).filter(
            extract('month', Invoice.created_at) == target.month,
            extract('year', Invoice.created_at) == target.year
        ).scalar() or 0
        month_labels.append(label)
        monthly_totals.append(round(total, 2))

    vendor_data = db.session.query(Vendor.name, db.func.sum(Invoice.amount)).join(Invoice).group_by(Vendor.id).all()
    vendor_labels = [v[0] for v in vendor_data]
    vendor_totals = [float(v[1]) for v in vendor_data]

    return render_template(
        'dashboard_charts.html',
        month_labels=month_labels,
        monthly_totals=monthly_totals,
        vendor_labels=vendor_labels,
        vendor_totals=vendor_totals,
        selected_months=months
    )

@main.route('/vendor-scorecard')
@login_required
def vendor_scorecard():
    scores = VendorScore.query.all()
    return render_template('vendor_scorecard.html', scores=scores)

@main.route('/report-builder', methods=['GET', 'POST'])
@login_required
def report_builder():
    form = ReportBuilderForm()
    export_results = []

    if request.method == 'POST':
        # Apply filters no matter what
        query = Invoice.query
        query = filter_invoices_by_form(query, form)
        results = query.all()

        export_type = request.form.get('export_type')

        if export_type == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Invoice #', 'Vendor', 'Amount', 'Status', 'Category', 'Tags', 'Notes', 'Messages'])

            for i in results:
                writer.writerow([
                    i.invoice_number,
                    i.vendor.name,
                    i.amount,
                    i.status,
                    i.category or '',
                    ', '.join([t.tag for t in i.tags]) if 'include_tags' in request.form else '',
                    '; '.join([a.content for a in i.annotations]) if 'include_notes' in request.form else '',
                    '; '.join([m.message for m in i.messages]) if 'include_messages' in request.form else ''
                ])

            output.seek(0)
            return Response(output, mimetype='text/csv',
                            headers={"Content-Disposition": "attachment;filename=invoice_report.csv"})

        elif export_type == 'pdf':
            return "🔴 PDF export coming soon."

        elif export_type == 'excel':
            return "🟠 Excel export coming soon."

        else:  # No export: just render
            for i in results:
                export_results.append({
                    'invoice_number': i.invoice_number,
                    'vendor': i.vendor.name,
                    'amount': i.amount,
                    'status': i.status,
                    'category': i.category,
                    'tags': ', '.join([t.tag for t in i.tags]) if 'include_tags' in request.form else '',
                    'notes': '; '.join([a.content for a in i.annotations]) if 'include_notes' in request.form else '',
                    'messages': '; '.join([m.message for m in i.messages]) if 'include_messages' in request.form else ''
                })

    return render_template('report_builder.html', form=form, export_results=export_results)

@main.route('/report-download', methods=['POST'])
@login_required
def report_download():
    form = ReportBuilderForm()
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(['Invoice #', 'Vendor', 'Amount', 'Status', 'Category', 'Tags', 'Notes', 'Messages'])

    query = Invoice.query
    query = filter_invoices_by_form(query, form)
    results = query.all()

    for i in results:
        writer.writerow([
            i.invoice_number,
            i.vendor.name,
            i.amount,
            i.status,
            i.category or '',
            ', '.join([t.tag for t in i.tags]) if form.include_tags.data else '',
            '; '.join([a.content for a in i.annotations]) if form.include_notes.data else '',
            '; '.join([m.message for m in i.messages]) if form.include_messages.data else ''
        ])

    output.seek(0)
    return Response(output, mimetype='text/csv',
                    headers={"Content-Disposition": "attachment;filename=invoice_report.csv"})
